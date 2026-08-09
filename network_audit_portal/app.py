import os
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from parsers.config_parser import ConfigParser
from parsers.log_parser import parse_logs, detect_risks
from validation.validator import validate_devices
from database import Database
from exporter import export_csv

load_dotenv()
BASE=Path(__file__).resolve().parent
UPLOAD=Path(os.getenv("UPLOAD_DIR", BASE/"uploads"))
DB_PATH=Path(os.getenv("DATABASE_PATH", BASE/"instance/network_audit.db"))
EXPORT_DIR=Path(os.getenv("EXPORT_DIR", BASE/"exports"))
for p in [UPLOAD,DB_PATH.parent,EXPORT_DIR]: p.mkdir(parents=True,exist_ok=True)

app=Flask(__name__)
app.secret_key=os.getenv("FLASK_SECRET_KEY","development-only-change-me")
app.config["MAX_CONTENT_LENGTH"]=int(os.getenv("MAX_UPLOAD_MB","10"))*1024*1024

def ingest():
    cp=ConfigParser()
    configs=[p for p in UPLOAD.iterdir() if p.is_file() and p.suffix.lower() in {".txt",".cfg",".conf"}]
    logs=[p for p in UPLOAD.iterdir() if p.is_file() and p.suffix.lower()==".log"]
    devices=[cp.parse_file(p) for p in configs]
    events=detect_risks(parse_logs(UPLOAD))
    validations=validate_devices(devices)
    Database(DB_PATH).replace_all(devices,events,validations)
    return devices,events,validations

@app.route("/")
def index(): return redirect(url_for("dashboard"))

@app.route("/upload",methods=["GET","POST"])
def upload():
    if request.method=="POST":
        files=request.files.getlist("files")
        saved=0
        for f in files:
            if not f or not f.filename: continue
            name=secure_filename(f.filename)
            if Path(name).suffix.lower() not in {".txt",".cfg",".conf",".log"}:
                continue
            f.save(UPLOAD/name); saved+=1
        if saved:
            ingest(); flash(f"Uploaded and parsed {saved} file(s).","success")
            return redirect(url_for("dashboard"))
        flash("No supported files were uploaded.","error")
    return render_template("upload.html")

@app.route("/dashboard")
def dashboard():
    db=Database(DB_PATH); db.initialize()
    devices,validations,events,interfaces,protocols=db.dashboard_data()
    hostname=request.args.get("hostname","").lower()
    protocol=request.args.get("protocol","").lower()
    status=request.args.get("status","").upper()
    risk=request.args.get("risk","").capitalize()
    if hostname: devices=[d for d in devices if hostname in d["hostname"].lower()]
    if status: validations=[v for v in validations if v["status"]==status]
    if protocol:
        protocols=[p for p in protocols if p["protocol"].lower()==protocol]
    if risk: events=[e for e in events if e["risk_level"]==risk]
    summary={}
    for v in validations:
        summary[v["status"]]=summary.get(v["status"],0)+1
    return render_template("dashboard.html",devices=devices,validations=validations,events=events,interfaces=interfaces,protocols=protocols,summary=summary,hostname=hostname,protocol=protocol,status=status,risk=risk)

@app.route("/device/<hostname>")
def device(hostname):
    data=Database(DB_PATH).device(hostname)
    if not data: return "Device not found",404
    return render_template("device.html",data=data)

@app.route("/export")
def export():
    path=export_csv(DB_PATH,EXPORT_DIR/"validation_report.csv")
    return send_file(path,as_attachment=True,download_name="validation_report.csv")

@app.route("/ingest")
def reingest():
    ingest()
    return redirect(url_for("dashboard"))

if __name__=="__main__":
    app.run(host=os.getenv("FLASK_HOST","127.0.0.1"),port=int(os.getenv("FLASK_PORT","5000")),debug=os.getenv("FLASK_DEBUG","0")=="1")