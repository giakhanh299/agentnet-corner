# Stickman Shorts — Manim rig

Repo animation người que tái sử dụng cho kênh Shorts faceless
(1080x1920, 30fps, tiếng Việt, không cần máy quay). Một nhân vật duy nhất,
định nghĩa một lần trong `src/rig/character.py`, mọi video import lại.

Stack: **Manim Community Edition 0.22.1 (Python)** + FFmpeg.
Chọn Manim vì render bằng CPU, chạy được cả trên VPS yếu lẫn PC Windows
(RTX 5060 Ti không giúp Manim nhanh hơn bao nhiêu — Manim dùng CPU).

## Cài đặt

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Font Be Vietnam Pro nằm trong `src/assets/fonts/` kèm [giấy phép SIL OFL 1.1](src/assets/fonts/OFL.txt).
`TextCard` nạp trực tiếp hai tệp font này khi render.

## Chạy thử (5 giây)

```bash
tools/render.sh stickman_demo.py StickmanScene
# Windows: tools\render.bat stickman_demo.py StickmanScene
```

Output: `media/videos/stickman_demo/1920p30/StickmanScene.mp4`.
Kiểm tra: 1080x1920, 30fps, ~5s, người que đi vào từ trái, vẫy tay,
card "TÂM SỰ NGƯỜI QUE" hiện rõ dấu tiếng Việt.

Khi ghép `--srt`, `tools/assemble.py` cần FFmpeg có bộ lọc `subtitles`
(libass) và dùng font Be Vietnam Pro có sẵn trong repo. Bản xuất giữ thời
lượng video và chuẩn hóa âm lượng của bản phối sau khi ghép nhạc.

```bash
python tools/assemble.py --video raw.mp4 --voice voice.wav --srt captions.srt --out final.mp4
```

## Cấu trúc

```
stickman-shorts/
├── config.py                  # SPEC đóng băng: mọi số liệu của nhân vật
├── requirements.txt           # manim==0.22.1
├── stickman_demo.py           # demo 5s: đi vào -> vẫy tay -> text card
├── src/
│   ├── rig/
│   │   ├── character.py       # Stickman(VGroup): FK, set_pose/walk/wave
│   │   ├── poses.py           # PoseAngles + pose đặt tên + lerp_pose
│   │   ├── walk.py            # walk cycle (sin)
│   │   ├── gestures.py        # wave / nod / point / shrug / think
│   │   ├── expressions.py     # mặt: neutral/happy/sad/surprised/...
│   │   └── props.py           # đạo cụ cùng nét vẽ (đất, túi tiền, laptop...)
│   ├── scenes/
│   │   ├── base_scene.py      # StickmanScene: config 9:16 + ground + helper
│   │   └── text_card.py       # TextCard (Be Vietnam Pro Bold, tự co chữ)
│   ├── utils/
│   │   ├── text.py            # NFC normalize + chia dòng tiếng Việt
│   │   ├── timing.py          # words <-> seconds <-> frames (150-165 wpm)
│   │   └── export.py          # apply_video_config + ffprobe
│   └── assets/fonts/          # BeVietnamPro Regular + Bold (.ttf)
├── videos/<ngày>_<slug>/      # mỗi video: script.yaml + scene.py + voice
├── tools/
│   ├── render.sh / render.bat # render 1 scene
│   ├── render_all.sh          # render hàng loạt (qua đêm trên VPS)
│   └── assemble.py            # ffmpeg: voice + caption -> final.mp4 (-16 LUFS)
├── docs/
│   ├── STYLE_GUIDE.md         # quy chuẩn hình ảnh / chữ / âm thanh
│   └── WORKFLOW.md            # quy trình 1 video 45s
└── tests/test_rig.py          # smoke test hình học (không cần render)
```

## Quy tắc vàng

1. **Một nguồn sự thật duy nhất**: mọi số liệu nhân vật chỉ ở `config.py`
   (SPEC đóng băng). Scene chỉ điều khiển bằng góc khớp (PoseAngles).
2. **Tiếng Việt**: chỉ dùng Manim `Text` (Pango) + font Be Vietnam Pro.
   KHÔNG dùng `Tex`/LaTeX. Mọi chuỗi chữ qua `normalize_text()` (NFC).
3. **Âm thanh**: giọng 150-165 từ/phút, chuẩn hóa -16 LUFS,
   true peak ≤ -1 dBTP, giọng bắt đầu ~0.1s.
4. **Video mới**: tạo thư mục `videos/<ngày>_<slug>/`, viết `script.yaml`
   + `scene.py` import rig, không copy code rig.

## Windows (PC RTX 5060 Ti)

- Cài Python 3.12, rồi `python -m venv .venv` + `pip install -r requirements.txt`.
- Render: `tools\render.bat stickman_demo.py StickmanScene`.
- Manim render bằng CPU nên RTX không tăng tốc; PC mạnh hơn VPS ở CPU/RAM
  nên render nhanh hơn 2-3 lần. Không cần cài LaTeX (không dùng Tex).
