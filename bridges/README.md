# bridges/ · Cầu nối giao tiếp Muse

Bản sao có phiên bản của các công cụ đang chạy thật tại `D:\AI_AGENT\AI_SYSTEM\RAG` (ngày 25/11/2026).

| File | Việc |
| :--- | :--- |
| `muse_dispatch.py` | Mở hồ sơ Chrome Muse, đăng nhập (OTP tempmail), dán lệnh triệu tập vào chat `muse.ai` |
| `muse_telegram_council.py` | Phòng họp bàn tròn: tạo đề bài lên Hub, gom kết quả, định dạng tin Telegram |
| `muse_mtproto_listener.py` | Trực nhóm Telegram 2 chiều qua MTProto |
| `file_exchange.py` | Gửi file qua host tạm, chặn secret/DB |
| `qc_engine.py` | QC máy 0-token: ffprobe, loudness, OCR, dHash, contact sheet 3×2 |
| `MO_PHONG_HOP_MUSE_TELEGRAM.cmd` | Bật phòng họp |

Chạy: đặt thư mục này vào `PYTHONPATH` (các file import lẫn nhau). Cần thêm `vps_ssh_helper.py` (`D:\0.1_FACE_BOOK\macro-tool`) cho thao tác VPS.

Test: `python -m unittest discover -s bridges/tests -v` (đặt `PYTHONPATH=bridges`).

�?ng b? t? RAG (1 chi?u, t? b? secret): `python bridges/sync_from_rag.py --check` d? xem kh�c bi?t, b? `--check` d? ghi.
