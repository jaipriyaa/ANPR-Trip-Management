# REST API Quick Reference Matrix

This reference table lists all FastAPI endpoints exposed by the backend application.

---

| Method | Endpoint Route | Purpose / Action | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Application status health check | No |
| `GET` | `/api/system/health` | Active inference backend & CUDA status | No |
| `GET` | `/api/system/performance` | Real-time CPU, RAM, GPU, and disk telemetry | No |
| `GET` | `/api/system/benchmark` | Latest system benchmark results | No |
| `POST` | `/api/system/benchmark/run` | Execute on-demand benchmark run | No |
| `GET` | `/api/system/benchmark/history` | Historical benchmark run logs | No |
| `GET` | `/api/v1/transporters` | List registered transporters | Optional |
| `POST` | `/api/v1/transporters` | Register new transporter | Yes |
| `GET` | `/api/v1/transporters/{id}` | Get transporter by ID | Optional |
| `PUT` | `/api/v1/transporters/{id}` | Update transporter record | Yes |
| `DELETE` | `/api/v1/transporters/{id}` | Deactivate transporter | Yes |
| `GET` | `/api/v1/vehicles` | List registered vehicles | Optional |
| `POST` | `/api/v1/vehicles` | Register new vehicle | Yes |
| `GET` | `/api/v1/vehicle-plates` | List vehicle plate records | Optional |
| `POST` | `/api/v1/vehicle-plates` | Register vehicle plate details | Yes |
| `GET` | `/api/v1/drivers` | List driver master records | Optional |
| `POST` | `/api/v1/drivers` | Create driver profile | Yes |
| `POST` | `/api/v1/vehicle-recognition/process-image` | Process image through full AI ANPR pipeline | No |
| `POST` | `/api/v1/vehicle-recognition/process-video` | Process video file through tracking pipeline | No |
| `GET` | `/api/v1/gates` | List plant entry/exit gates | Optional |
| `POST` | `/api/v1/gates` | Create gate record | Yes |
| `GET` | `/api/v1/gate-cameras` | List camera RTSP assignments | Optional |
| `POST` | `/api/v1/gate-rules` | Configure gate passage rules | Yes |
| `GET` | `/api/v1/movements` | Query vehicle passage movement logs | Optional |
| `POST` | `/api/v1/movements` | Log vehicle entry/exit movement event | No |
| `GET` | `/api/v1/live-monitor/status` | Real-time live control room telemetry | No |
| `GET` | `/api/v1/trips` | Query plant trip lifecycle tickets | Optional |
| `POST` | `/api/v1/trips` | Schedule new trip ticket | Yes |
| `PUT` | `/api/v1/trips/{id}/status` | Transition trip lifecycle status | Yes |
| `POST` | `/api/v1/authorization/verify` | Evaluate access authorization decision | No |
| `GET` | `/api/v1/whitelist` | List authorized whitelist entries | Optional |
| `POST` | `/api/v1/whitelist` | Add plate to whitelist | Yes |
| `GET` | `/api/v1/watchlist` | List security watchlist entries | Optional |
| `POST` | `/api/v1/watchlist` | Add plate to watchlist | Yes |
| `GET` | `/api/v1/manual-review` | List low-confidence OCR review queue | Optional |
| `POST` | `/api/v1/manual-review/{id}/correct` | Submit manual OCR correction | Yes |
| `GET` | `/api/v1/admin/analytics` | Operational analytics dataset | Optional |
| `GET` | `/api/v1/admin/audit-logs` | Security audit trail logs | Yes |
