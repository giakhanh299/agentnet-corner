# docs/WORKFLOW.md

Quy trình làm 1 video stickman 45s khi rig đã có sẵn
(tổng ~40-70 phút, video đầu tiên sẽ lâu hơn vì phải học rig).

## 1. Kịch bản (10-15 phút)

- Viết kịch bản tiếng Việt 112-124 từ cho 45s (150-165 từ/phút).
- Chia 5-7 scene, mỗi scene 5-8s. Hook (câu hỏi/câu khẳng định bất ngờ)
  nằm trong 3s đầu, cả chữ trên màn hình và giọng đọc hỏi CÙNG một câu.
- Tạo thư mục `videos/<ngày>_<slug>/`, viết `script.yaml` theo mẫu
  trong `videos/` (xem `src/rig/poses.py` để biết pose có sẵn).

## 2. Giọng đọc (5-10 phút)

- Tạo `voice.wav` bằng TTS miễn phí (Edge TTS thử trước) hoặc thu âm.
- Kiểm tra thời lượng voice khớp kịch bản (40-55s). Cắt khoảng lặng thừa
  ở đầu để giọng bắt đầu từ ~0.1s.

## 3. Scene (15-30 phút)

- Viết `scene.py` trong thư mục video, import rig từ `src/rig/`,
  không vẽ lại nhân vật. Chỉ dùng pose có sẵn; scene mới thì ghép
  từ template `stickman_demo.py`.
- Text card: dùng `TextCard` trong `src/scenes/text_card.py`.

## 4. Render bằng Manim (3-5 phút trên PC, 5-10 phút trên VPS yếu)

```
tools/render.sh videos/2026-11-15_tam-su-nguoi-que/scene.py StickmanScene
```
- Output: `media/videos/.../1080p30/StickmanScene.mp4` (raw, chưa có tiếng).
- Render ở chất lượng thấp (`-ql`) để test nhanh, `-qm` để xuất bản.
- VPS render bằng CPU (Manim không dùng GPU); render hàng loạt qua đêm
  bằng `tools/render_all.sh`. PC dùng để viết code, test nhanh, render
  scene phức tạp, kiểm tra chất lượng.

## 5. Ghép voice + caption bằng FFmpeg (1-2 phút)

```
python tools/assemble.py --video <raw.mp4> --voice voice.wav \
    --srt captions.srt --out videos/<ngày>_<slug>/output/final.mp4
```
- Chuẩn hóa -16 LUFS tự động. Caption `.srt` lấy từ Whisper
  (xem whisper.cpp ở thư mục gốc của dự án).

## 6. Kiểm tra và đăng (5 phút)

- Xem `final.mp4` trên điện thoại: chữ có lỗi dấu không, stickman có
  giống rig chuẩn không, voice + hình có đồng bộ không.
- Đăng YouTube Shorts, thêm tiêu đề + mô tả + hashtag.
