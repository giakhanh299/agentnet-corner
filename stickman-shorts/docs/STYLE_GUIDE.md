# docs/STYLE_GUIDE.md

Quy chuẩn hình ảnh cho mọi video stickman của kênh. Sửa rig thì sửa ở
`config.py` / `src/rig/` — không bao giờ hardcode số liệu trong scene.

## Nhân vật (khóa trong config.py — SPEC)

- Tỷ lệ (đơn vị Manim, đều suy ra từ HEAD_R = 0.6):
  đầu 2×0.6 · cổ 0.25 · thân 2.5 · tay trên 0.95 · tay dưới 0.85 ·
  đùi 1.05 · cẳng chân 1.05. Tổng cao 6.05 đơn vị.
- Nét vẽ: STROKE = 8 cho thân + đạo cụ, STROKE_THIN = 4 cho mắt/miệng.
  Chỉ một độ dày nét cho toàn bộ cơ thể và đạo cụ.
- Màu: mực #141414 (không dùng đen tuyệt đối #000000), nền #F6F5F0
  (trắng ngà), nhấn #D9381E (đỏ cam) cho từ khóa / đạo cụ quan trọng.
- Vị trí: stickman đứng giữa khung, chân chạm đường đất y = -3.6,
  trừ khi scene yêu cầu khác.

## Nhất quán

- Mọi video import `Stickman` từ `src/rig/character.py`. Không vẽ lại
  nhân vật trong scene, không copy-paste code vẽ.
- Scene chỉ điều khiển bằng góc khớp (PoseAngles): `set_pose()`,
  `walk()`, `wave()`, hoặc các pose có sẵn trong `poses.py` / `gestures.py`.
- Khi rig ổn định: `git tag v1.0-rig-stable`. Video mới dùng rig đã tag;
  cải tiến rig thì tạo branch, test xong mới merge.
- Frame chuẩn: `media/videos/stickman_demo/1080p30/StickmanScene.mp4`
  (frame 2s) là ảnh đối chiếu mỗi khi sửa rig.

## Chữ tiếng Việt

- Font duy nhất: Be Vietnam Pro (đã nhúng trong `src/assets/fonts/`).
  Tiêu đề Bold 72, body Regular 48 — không nhỏ hơn 48 trên màn 1080x1920.
- Luôn dùng Manim `Text` (Pango). KHÔNG dùng `Tex`/LaTeX cho tiếng Việt.
- Mọi chuỗi chữ phải qua `normalize_text()` (NFC) trước khi render.
- Text card tối đa 2 dòng, mỗi dòng 12-15 từ; card tự co chữ cho vừa
  khung 7.4 đơn vị. Test dấu trước video thật:
  "Tâm sự người que — Ăn cơm chưa? Đi làm muộn, ồ ạt, ứ ự, ỹ, ỳ, ỵ."

## Âm thanh (chuẩn đã đo từ video thật)

- Giọng 150-165 từ/phút → video 45s khoảng 112-124 từ.
- Chuẩn hóa -16 LUFS, true peak ≤ -1 dBTP, giọng bắt đầu từ ~0.1s,
  không khoảng lặng đầu video.
