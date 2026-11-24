# Phim Ma Dân Gian Việt Nam — Phòng họp đa Muse ⇄ Telegram

Nhánh `feat/phim-ma-dan-gian` (Tầng 3 · R&D, cách ly Tầng 1 theo `L060`).

## Thành phần
- `muse_telegram_council.py` — điều phối bàn tròn: tạo đề bài Vòng 1/2 cho Muse Chính + 4 Muse Phụ trên AgentNet Hub `:8110`, gom kết quả, định dạng tin Telegram, nối QC Tầng 1 (`qc_engine.py`) + `file_exchange.py`.
- `muse_mtproto_listener.py` — trực nhóm Telegram 2 chiều qua MTProto DC5 (`@MUSEall1_bot`): nhận câu hỏi, nhận video/ảnh hoặc `/qc <path>` để chạy QC 2 tầng, phát câu trả lời của Muse vào nhóm.
- `tests/test_muse_telegram_council.py` — test luồng bàn tròn + che secret.
- `docs/` — biên bản 7 lượt họp ngày 24/11/2026 và kịch bản Pilot #1 "Ma Da Kéo Giò".

## Phụ thuộc runtime (chưa nằm trong nhánh này)
Code đang chạy thật tại `D:\AI_AGENT\AI_SYSTEM\RAG` và import: `muse_dispatch.py`, `qc_engine.py`, `file_exchange.py`, cùng `vps_ssh_helper.py` ở `D:\0.1_FACE_BOOK\macro-tool`. Nhánh này là bản lưu phiên bản; chạy bằng `run_listener.cmd` (đặt `PYTHONPATH` trỏ về RAG).

## Secret — KHÔNG commit (`L065`)
- `%LOCALAPPDATA%\MuseLoginHelper\telegram_council.json` (bot token, group id)
- `%LOCALAPPDATA%\MuseLoginHelper\council_dc5.session` (phiên đăng nhập bot = mật khẩu)

## Việc còn mở
- Đang dùng `api_id` công khai của Telegram Desktop cho MTProto → cần đăng ký `api_id` riêng tại my.telegram.org.
- Đổi bot token qua `@BotFather /revoke` sau khi ổn định (token từng lộ trong chat).
- Pilot #1 chưa render; chờ chủ dự án duyệt kênh thử nghiệm cách ly.

## Test
```
set PYTHONPATH=D:\AI_AGENT\AI_SYSTEM\RAG
python -m unittest discover -s phim-ma-dan-gian\tests -v
```
