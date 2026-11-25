# Phim Ma Dân Gian Việt Nam — `channels/phim-ma-dan-gian/`

Nhánh `feat/phim-ma-dan-gian` (Tầng 3 · R&D, cách ly Tầng 1 theo `L060`). Công cụ dùng chung lấy từ nhánh `feat/core-shared` (xem `00_BAN_DO_REPO.md` ở gốc repo).

## Thành phần riêng của kênh
- `docs/` — biên bản 7 lượt họp bàn tròn ngày 24/11/2026 và kịch bản Pilot #1 *Ma Da Kéo Giò*.
- `pilot01_ma_da/scenes.json` — 5 cảnh, Visual DNA làng quê Việt cổ, negative prompt chống Hán hóa, lời dẫn + giọng ma, SFX, lệnh mix audio.
- `studio_app/main.py` — bản nháp giao diện quản lý hàng đợi tạo video (FastAPI). **Đang giả lập** (`_simulate_run`), chưa nối máy dựng thật, còn thiếu `static/index.html`.
- `run_listener.cmd` — bật cầu nối Telegram phòng họp.

## Dùng chung (không chép lại vào đây)
- Phòng họp Muse ⇄ Telegram, gửi lệnh Muse, gửi file, QC máy: `bridges/`
- Giọng đọc + Whisper, ghép video, QC 100 điểm: `auto99/`
- Danh mục giọng / FFmpeg / GPU trên PC: `studio/CONG_CU_LOCAL.md`
- Nhạc, SFX, font: `assets/README.md`

## Quy tắc lưu trữ
- Git: chỉ code, kịch bản, tài liệu. Media (ảnh cảnh, clip, giọng, nhạc, bản ghép) → Google Drive `phim-ma-dan-gian/`.

## Secret — KHÔNG commit (`L065`)
- `%LOCALAPPDATA%\MuseLoginHelper\telegram_council.json`, `*.session`

## Việc còn mở
- Đăng ký `api_id` Telegram riêng tại my.telegram.org rồi ghi vào `telegram_council.json` (bản `bridges/` không còn ghi cứng).
- Đổi bot token qua `@BotFather /revoke` (token từng lộ trong chat).
- Pilot #1 chưa render.
