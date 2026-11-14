# AgentNet Corner — dự án nghiên cứu độc lập

Code, registry và queue mới chỉ nằm trong /opt/agentnet-corner, dưới 1 GB. Python standard library; không model/media. API và prompt bind Tailscale cổng 8110.

## Sửa lỗi nối nhầm dự án

Trước đây assistant nối ba agent với broker 8101 tự sinh việc đánh giá FB. Thiết kế đó sai phạm vi nghiên cứu riêng. Broker phụ 8101 được dừng/disable, database giữ nguyên; các dịch vụ Facebook gốc và bridge 8000 không bị sửa/restart.

Queue nghiên cứu mới không nhập task/kết quả/token FB. Registry không đọc credentials.json của broker cũ. Node dùng credential đăng ký riêng đã được chủ duyệt, xác thực thêm Tailscale Node.ID. Revoke registry chặn cả API nghiên cứu, không chỉ resolve.

## Thành phần

- state/registry.sqlite3: giữ đăng ký Controller, Research, Verify.
- state/research.sqlite3: hàng đợi project=research, ban đầu rỗng.
- Controller tạm kiêm Engineer; không cần node thứ tư.
- Prompt: /prompts/master-v1.2, /prompts/chief, /prompts/worker.
- Không timer sinh việc FB, không HTTP client tích hợp FB.

## Kết nối lại

Cập nhật join.py từ source đã duyệt, giữ identity.json. Chạy đúng controller/research/verify với --master http://MASTER_IP:8110. Chỉ dùng connection.json có project=research, mode=research-only. Không dùng cache/token broker cũ. Khóa Tailscale không phải credential ứng dụng.

## API

GET /health trả project=research. GET /tasks, GET /agents, POST /tasks và POST /tasks/{id}/approve chỉ Chief. Worker: POST /claim, POST /tasks/{id}/heartbeat, POST /tasks/{id}/result. API private yêu cầu Bearer credential node và nguồn Tailscale khớp đăng ký.

POST /tasks gồm project=research, assigned_to là research/verify/engineer, kind, dedup, payload.objective. Chief kiêm Engineer thêm as_role=engineer trong claim/heartbeat/result; server kiểm tra delegation hiện tại, không dùng token Engineer FB.

Trạng thái QUEUED → RUNNING → SUBMITTED → APPROVED. Lease 15 phút, heartbeat 60 giây, chống trùng task/result. BLOCKED không được approve. Chặn URL nguồn trỏ endpoint đánh giá FB cũ. Không tự duyệt/đăng bài/thực thi code trên MASTER.

## Dung lượng và vận hành

Guard 900 triệu byte; mỗi SQLite giới hạn khoảng 256 MiB. Đây không phải hard quota với root. Media/model/repo lớn ở worker hoặc Drive; queue chỉ giữ metadata/kết quả nhỏ có nguồn.

systemctl status agentnet-corner.service --no-pager
python3 /opt/agentnet-corner/corner.py status
python3 /opt/agentnet-corner/corner.py delegate-engineering on
du -sh /opt/agentnet-corner

Không bật broker 8101 cho dự án này. Source công khai không chứa state/credential/backup. Daily backup Drive mã hóa, restore và AI runtime chạy nền chưa được triển khai; không báo đã có chỉ vì queue hoạt động.
