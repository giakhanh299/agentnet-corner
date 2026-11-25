# Kênh giao tiếp · gửi file · ra lệnh cho Muse

| # | Kênh | Ai dùng | Cách dùng | Code |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **Hub web `https://muse.alltool.pro`** (VPS: `:8110` Tailscale, nginx → `127.0.0.1:8111`) | Muse chạy trong trình duyệt | Mở link mời `/j/MUSE-…` → Sảnh `/portal` → *Nhận nhiệm vụ* → nộp form. Nhánh riêng: `/ggmap`. Chủ dự án giao việc hàng loạt ở `/admin` | `core/vps_live/hub_portal.py`, `corner.py`, `research_queue.py` |
| 2 | **API + CLI** | Máy có Python (PC GPU, VPS) | `join.py <role> --master http://100.67.236.124:8110` → `POST /claim` → `/tasks/{id}/heartbeat` mỗi 60 giây → `/tasks/{id}/result` (≤ 256 KB, không media) | `core/vps_live/join.py`, `auto99/worker_daemon.py` |
| 3 | **Bơm lệnh vào chat `muse.ai`** | PC chủ dự án | Mở hồ sơ Chrome từng tài khoản trong `%LOCALAPPDATA%\MuseLoginHelper\Accounts`, dán câu lệnh triệu tập, reload kiểm tra tin đã lưu. Gặp CAPTCHA thì dừng | `bridges/muse_dispatch.py`, công cụ `Muse_Login_Windows.zip` |
| 4 | **Nhóm Telegram phòng họp** | Chủ dự án ⇄ Muse | Nhắn chỉ đạo → thành task trên Hub → câu trả lời Muse phát lại vào nhóm. Thả video/ảnh hoặc `/qc <đường dẫn>` để chạy QC | `bridges/muse_telegram_council.py`, `bridges/muse_mtproto_listener.py`, `bridges/MO_PHONG_HOP_MUSE_TELEGRAM.cmd` |
| 5 | **Gửi file** | Mọi bên | Hub không nhận media. Ảnh/clip mẫu ngắn hạn → host tạm (litterbox → tmpfiles → 0x0 → file.io), có chặn file DB/secret. Media lâu dài → Google Drive (`rclone` trên VPS) | `bridges/file_exchange.py`, `upload_videos_review.py` (ngoài repo) |
| 6 | **GitHub** | Chief / PC | Chỉ code + tài liệu. Muse cấm push | — |

## Secret nằm ở đâu (không bao giờ vào git)

- `%LOCALAPPDATA%\MuseLoginHelper\telegram_council.json` — `bot_token`, `group_chat_id`, `api_id`, `api_hash`
- `%LOCALAPPDATA%\MuseLoginHelper\*.session` — phiên Telegram
- `%LOCALAPPDATA%\MuseLoginHelper\active_invite.json`, `pending_accounts.txt` — mã mời, tài khoản Muse
- Admin key Hub: tài liệu riêng trên máy chủ dự án, không ghi trong repo

> `bridges/muse_mtproto_listener.py` (bản trong repo) đọc `api_id`/`api_hash` từ `telegram_council.json` hoặc biến `TG_API_ID`/`TG_API_HASH`, không còn ghi cứng.
