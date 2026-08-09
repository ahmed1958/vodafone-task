# Assumptions and limitations

1. The parser targets the exact Cisco, Huawei, and Juniper structures represented by the supplied sample files; it is not a full vendor configuration grammar.
2. The task asks for OSPF/BGP areas to be consistent "where declared". The supplied BGP configurations do not contain a BGP area concept, so the application does not invent one.
3. Juniper `lo0` is normalized as Loopback0.
4. Validation is intentionally rule-based and deterministic.
5. The dashboard uses Chart.js from a CDN for charts; an offline deployment should vendor the JS asset locally.
6. Logs must use the Task 1 timestamp/device/severity/message structure.
7. Uploaded files are stored locally under the configured upload directory. Production deployments should add authentication, file scanning, quotas, and stronger upload isolation.