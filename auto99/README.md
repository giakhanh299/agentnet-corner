# AgentNet V2.0 — Auto 99% Autonomous Video Studio (`auto99/`)

Gói nâng cấp đưa hệ thống AgentNet từ điều phối phẳng (V1.2) lên quy trình khép kín **Auto 99%**, giữ nguyên cô lập an toàn khỏi hệ thống Facebook cũ (`8000`/`8101`) và giới hạn lưu trữ `< 1 GB` trên Master.

## Kiến trúc 5 Phase đã triển khai

1. **Control Plane DAG + GPU-First Fallback (`research_queue.py`, `corner.py`)**:
   - Hỗ trợ `POST /pipelines` (DAG đa bước `WAITING_DEPS -> QUEUED`).
   - Ưu tiên đẩy tác vụ nặng (`preferred_capabilities: ["gpu_cuda"]`) về **PC Windows RTX 5060 Ti** khi máy đang bật; tự động fallback `0 giây` về **CPU VPS1** khi PC tắt hoặc sau `fallback_after_seconds` khi PC quá tải.
   - Cho phép `verify` đọc trực tiếp `GET /tasks/<target_id>` (bỏ copy-paste 256KB).
   - Khép kín `auto_verify` + `auto_approve` (`PASS` & `score >= 85` tự động duyệt và đẩy sang `staging_reviews`; `RETRYABLE_FAIL` tự động sửa tối đa `max_retries=2` lần trước khi báo `ESCALATED`).

2. **Persistent Worker Daemon (`auto99/worker_daemon.py`, `auto99/pc_worker_start.ps1`)**:
   - Tự phát hiện phần cứng (`gpu_cuda`, `tts_mms`, `whisper_large_v3`, `ffmpeg`, `manim_stickman`, `cpu_fallback`).
   - Tự cấu hình `torch\lib` vào `PATH` + UTF-8 trên Windows.
   - Chạy luồng `heartbeat` nền mỗi `45s` (không bao giờ mất lease 15 phút) và giữ `outbox/` chống đứt mạng tạm thời.

3. **Self-Healing TTS + Từ điển phiên âm tự học (`auto99/tts_auto_heal.py`, `auto99/pronunciation_lexicon.json`)**:
   - Xóa bỏ hoàn toàn việc viết tay `v0xx_probe1..4.py`.
   - Tách riêng chữ hiển thị phụ đề (`Canada`, `60%`) và chữ đọc phát âm (`Ca-na-đa`, `sáu mươi phần trăm`).
   - Dùng `faster-whisper` nghe kiểm tra lại từng câu ngay sau khi `MMS-TTS` đọc: tự căn chỉnh `speaking_rate` về vùng `150–165 wpm` và tự thay cụm từ dễ lệch thanh điệu (`băng hà -> băng tuyết khổng lồ`).

4. **Trình biên dịch tập phim thống nhất (`auto99/episode_compiler.py`)**:
   - Biên dịch từ một file `episode.yaml` / `episode.json` duy nhất cho cả **Visual Essay** (`zoompan` + card `Be Vietnam Pro Bold` + endcard) và **Stickman** (tự sinh code Manim từ rig chuẩn `stickman-shorts`).
   - Chuẩn hóa âm thanh **EBU R128 2-pass tuyến tính (`-16.0 LUFS`, `-1.5 dBTP`)** + phụ đề `.ass` `1080x1920`.

5. **Auto-QC 100 điểm (`auto99/qc_verify.py`) + Cổng duyệt 1% Telegram Bot (`auto99/telegram_gate.py`)**:
   - Kiểm định cứng bằng `ffprobe` + `loudnorm` + kiểm tra tràn dòng `.ass` + trích xuất keyframe trước khi chấm thang 100 điểm.
   - Đẩy bản dựng đạt chuẩn thẳng về điện thoại chủ qua **Telegram Bot** kèm 4 nút bấm:
     - `✅ Duyệt 11:30` | `🌙 Duyệt 20:00` | `🔁 Render lại` | `❌ Loại (+Bài học)`
   - Khi bấm `Loại` hoặc `Render lại` kèm 1 dòng nhắn (ví dụ: `phát âm: Ottawa -> Ót-ta-oa`), hệ thống tự ghi vào `lessons` và tự dạy luôn từ điển `pronunciation_lexicon.json`.

## Lệnh chạy nhanh trên PC Windows (RTX 5060 Ti)

```powershell
# 1. Chạy thử trọn bộ Unit + Integration Tests
.\ai-stack\.venv-ai\Scripts\python.exe -m unittest test_corner.py test_research_queue.py test_research_http.py test_auto99.py -v

# 2. Biên dịch + Tự sửa TTS + Chuẩn hóa -16 LUFS + Auto-QC 1 tập phim bất kỳ bằng 1 lệnh
.\ai-stack\.venv-ai\Scripts\python.exe -m auto99.studio_cli run-local --spec stickman-shorts\videos\2026-11-15_ep001-cam-dau-lam-viec\script.yaml --out studio_runs\ep001_auto

# 3. Cài đặt token Telegram Bot (lưu an toàn ngoài Git tại ~\.agentnet-corner\telegram.json)
.\ai-stack\.venv-ai\Scripts\python.exe -m auto99.telegram_gate init-config --token "<BOT_TOKEN>" --chat-id <YOUR_CHAT_ID>

# 4. Khởi động GPU Worker Daemon kết nối mạng Tailscale
.\auto99\pc_worker_start.ps1 -Master "http://100.67.236.124:8110"
```
