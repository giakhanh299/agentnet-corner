# AgentNet Corner — phần bổ sung dưới 1 GB

Phân công tạm thời: Controller kiêm Engineer; Research và Verify là hai worker riêng. Refresh join.py controller để nhận additional_roles.engineer trong connection.json private. Dùng credential Engineer để claim/heartbeat/result, credential Chief để điều phối. Không in additional_roles/token ra log. CLI riêng: `corner.py delegate-engineering on` hoặc `off`. Khi tắt, token đã cấp vẫn cần được rotate để thu hồi quyền cũ hoàn toàn; việc đó phải có kế hoạch tránh ảnh hưởng hệ thống cũ.

Chỉ thêm /opt/agentnet-corner. Python standard library, không venv/Docker/model; không sửa hoặc restart bridge 8000/controller 8101. Registry bổ sung bind Tailscale cổng 8110.

## Có thể dùng

- Prompt Chief và Worker tại /prompts/chief và /prompts/worker.
- Đăng ký máy gắn với Node.ID lấy từ tailscale whois; yêu cầu vai trò luôn chờ chủ duyệt.
- Địa chỉ Controller lấy từ registry, không hardcode trong worker.
- Chỉ node đã duyệt nhận token ứng dụng riêng của role; không có API cho worker xem toàn bộ registry.
- Request tối đa 16KB, tối đa 256 bản đăng ký, SQLite giới hạn khoảng 256 MiB; guard trước khi ghi ở 900 triệu byte.

Guard không phải filesystem quota; root/chương trình bên ngoài vẫn có thể chép file vào thư mục. Không lưu media, model, backup lớn hoặc repo dự án khác ở đây.

## Đăng ký

Trên máy mới đọc join.py rồi chạy `python3 join.py ROLE --master http://MASTER_IP_TAILSCALE:8110`, ROLE là controller/research/verify/engineer.

Trên MASTER: `python3 /opt/agentnet-corner/corner.py status`, đối chiếu Node.ID với máy do chủ tạo, sau đó `python3 /opt/agentnet-corner/corner.py approve REQUEST_ID`.

Máy mới chạy lại join.py để nhận connection.json riêng. Client phải refresh trước mỗi vòng nhận việc. Auth key Tailscale không thay thế bước duyệt và token ứng dụng.

## Tương thích cũ

Route ban đầu trỏ controller cũ, không di chuyển database. Mapping: research=MUSE-03, verify=MUSE-02, engineer=MUSE-04, chief=MUSE-01. credentials.json là cấu hình private của registry, không đưa vào Git hoặc endpoint tài liệu.

## Thay máy

Revoke registry chỉ chặn resolve, không tự thu hồi token đã cấp ở controller cũ. Phải rotate/thu hồi token ứng dụng cũ trước khi approve máy thay; công cụ chặn approve khi còn predecessor APPROVED. Không tự sửa controller cũ khi chưa có kế hoạch tránh gián đoạn.

Chỉ đổi route sau khi Controller mới phục hồi state và kiểm thử. Route CLI hiện chỉ hỗ trợ adapter legacy.

## Vận hành

```bash
systemctl status agentnet-corner.service --no-pager
systemctl stop agentnet-corner.service
systemctl start agentnet-corner.service
python3 /opt/agentnet-corner/corner.py status
du -sh /opt/agentnet-corner
```

Unit nằm trong thư mục; systemd có thêm liên kết đăng ký service riêng, không ghi đè unit cũ. Không ghi request body/token vào log.

## Chưa triển khai/kiểm chứng

Chưa có bốn VPS riêng đăng ký, chưa có runtime AI/model, repo công khai đã tạo tại https://github.com/giakhanh299/agentnet-corner. Chưa có public key age của chủ nên chưa bật backup 03:00 hoặc thử restore. Chưa kiểm thử đổi Controller thật hoặc áp dụng Grants. Registry/prompt không tự tạo AI.

MASTER hiện vẫn có .env/token Drive và dịch vụ cũ, được giữ nguyên theo yêu cầu không thay đổi hệ thống cũ. Vì vậy chưa đạt thiết kế MASTER chỉ giữ kiến trúc và không có secret AI/Drive; việc migration cần nhiệm vụ riêng có máy đích.

## Source công khai

https://github.com/giakhanh299/agentnet-corner — chỉ source/prompt/scripts; không có credentials.json, state hoặc dữ liệu thực tế.
