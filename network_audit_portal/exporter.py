import csv
from pathlib import Path
from database import Database

def export_csv(db_path, output):
    db=Database(db_path); db.initialize()
    with db.connect() as c:
        rows=c.execute("""SELECT device,rule_name,status,details FROM validation_results ORDER BY device,rule_name""").fetchall()
    output=Path(output); output.parent.mkdir(parents=True,exist_ok=True)
    with output.open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["Device","Validation_Rule","Status","Details"])
        w.writerows(rows)
    return output