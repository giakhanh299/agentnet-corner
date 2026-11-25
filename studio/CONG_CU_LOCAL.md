# studio/ · Công cụ local trên PC (chọn giọng · ghép giọng · ghép video)

Kiểm tra thật ngày 25/11/2026 trên PC Windows của chủ dự án. Bản máy đọc được: `local_tools.json`.

## Phần cứng

- GPU **NVIDIA RTX 5060 Ti 16 GB**, `torch 2.10.0+cu128` — CUDA chạy được.
- Python 3.10.11, Node 24, FFmpeg **8.1.2 full build** (gyan.dev).

## 1. Chọn / tạo giọng

| Công cụ | Giọng có sẵn | Ghi chú |
| :--- | :--- | :--- |
| **OmniVoice** (clone giọng từ mẫu) | 8 mẫu trong `D:\0.1_FACE_BOOK\Lay video tiktok\OmniVoice\voices\`: `giongnamtnghiemtuc.wav`, `giongnamdanchuongtrinh.mp3`, `giongnamreviewdao.mp3`, `giongdocconhan_short.mp3`, `giongchigg.wav`, `giongnucute.wav`, `ref_better_version.mp3` | Thư mục Tầng 1 → **chỉ đọc**, chép mẫu ra ngoài nếu cần sửa |
| **edge-tts 7.3.1** | `vi-VN-NamMinhNeural` (nam), `vi-VN-HoaiMyNeural` (nữ) | Cần mạng, nhanh, dùng để nháp |
| **MMS-TTS** (`facebook/mms-tts-vie`, qua `transformers`) | 1 giọng | Đã dùng cho 9 video `v00x`; giấy phép **CC-BY-NC** (không thương mại). Model tải lần đầu |
| **VieNeu-TTS** | — | Thắng điểm Whisper 80% trong lượt so sánh 16/11, giấy phép Apache 2.0 (thương mại được); **chưa cài trên PC** |
| gwen-tts 0.6B | — | Model đã có trong cache Hugging Face, chưa tích hợp |

So sánh giọng chi tiết: `video_production/voice-compare-20261116/voice_compare_20261116.md`.

## 2. Kiểm tra & ghép giọng

- `faster-whisper` (GPU) nghe lại, chấm đúng chữ, đo tốc độ đọc — dùng trong `auto99/tts_auto_heal.py` (tự sửa phát âm theo `auto99/pronunciation_lexicon.json`).
- FFmpeg filter có sẵn: `rubberband` (đổi cao độ, vd. giọng ma −3 semitone), `sidechaincompress` (nhạc tự nhỏ khi có lời), `loudnorm` (chuẩn −15/−16 LUFS), `amix`, `whisper` (phụ đề tự động trong FFmpeg).

## 3. Ghép video

- FFmpeg encoder GPU: `h264_nvenc`, `hevc_nvenc`, `av1_nvenc`.
- Filter: `zoompan` (Ken Burns), `xfade` (chuyển cảnh), `ass` (đốt phụ đề `.ass`), `overlay`.
- Code dựng sẵn: `auto99/episode_compiler.py` (template `visual_essay` + `stickman`), `stickman-shorts/tools/assemble.py`.
- Tạo ảnh: `diffusers` đã cài, **chưa có model ảnh**.
- Người que: cần cài `manim` (chưa có).

## 4. QC

- `bridges/qc_engine.py`: ffprobe, loudness, khung đen/đứng hình, OCR (RapidOCR), dHash chống trùng, contact sheet 3×2.
- `auto99/qc_verify.py`: thang 100 điểm, `PASS` / `RETRYABLE_FAIL`.

## Kiểm tra trước khi push

```powershell
cd core\vps_live; python -m unittest discover -p "test_*.py"; cd ..\..
python -m unittest test_corner test_research_queue test_research_http test_auto99
$env:PYTHONPATH="$PWD\bridges"; python -m unittest discover -s bridges\tests
```
