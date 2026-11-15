# ChatGPT — Repo Stickman (2026-11-15)

Hỏi trong conversation "Phân tích Shorts Faceless" (chatgpt.com/c/6af8a50f-56c4-83ec-a25f-16edb4ff4992), tài khoản GCM Cong ty (Plus). Hỏi 14:54, trả lời xong 15:31 cùng ngày (36 phút đo được, ChatGPT tự ghi thời gian suy nghĩ ~14m29s). 7 câu hỏi về repo stickman (công cụ, cấu trúc repo, nhất quán, tiếng Việt, code mẫu, workflow/thời gian, điểm không chắc). Lưu nguyên văn câu trả lời.

> Lưu ý: sau câu trả lời hoàn chỉnh, trang hiện thêm dòng "Message delivery timed out. Please try again." — bản thân câu trả lời đã đầy đủ tới Câu 7 + kết luận. Code mẫu có chỗ dùng `pass` làm thân hàm (character.py) và một số dòng dài bị cắt ngắn trong chế độ xem tự động — chưa được chạy/kiểm chứng. ChatGPT chọn Manim làm stack chính, KHÁC với Gemini (chọn Remotion) — xem đối chiếu ở cuối file. Hai điểm ChatGPT khác với quy tắc đã kiểm chứng của dự án: (1) kịch bản 100-120 từ cho 45s, trong khi vùng an toàn đã kiểm chứng 150-165 từ/phút tức 45s ≈ 112-124 từ (100-120 từ vẫn nằm gần, chỉ hơi chậm); (2) render Manim 5-10 phút trên VPS yếu là ước tính, chưa đo thực tế.

---

## XÂY DỰNG REPO STICKMAN — TRẢ LỜI ĐẦY ĐỦ 7 CÂU HỎI

Bối cảnh đã xác nhận: Shorts faceless, 1080x1920, 40-55s, tiếng Việt, không quay hình. Phong cách: stickman đen đơn giản trên nền trơn + text card + đạo cụ tối giản, giống Reel "Tâm sự người que" và các video stickman câm đã phân tích. Yêu cầu cốt lõi: stickman giống hệt nhau mọi video, repo code tái sử dụng, không phải animation một lần. Máy: Windows RTX 5060 Ti 16GB + VPS Linux yếu 4 CPU / 8GB RAM / không GPU.

## 1. CHỌN TOOL — SO SÁNH 5 CÔNG CỤ, CHỌN MỘT STACK CHÍNH

Kết luận trước: Chọn Manim làm stack chính.

### 1.1. Bảng so sánh nhanh

| Tiêu chí | Manim | Remotion | Blender Grease Pencil | Pivot Animator | SVG + FFmpeg |
|---|---|---|---|---|---|
| Mục đích gốc | Animation toán học / giải thích bằng code | Video bằng React / web | 2D animation trong 3D | Animation stickman 2D | Vẽ vector + render video |
| Viết bằng code, tái sử dụng | Rất tốt — Python, class, hàm, import lại được | Tốt — React component, props, tái sử dụng | Kém — vẽ tay từng frame, khó tái sử dụng bằng code | Kém — kéo thả, không có code, không version control tốt | Tốt — SVG là code, nhưng phải tự viết engine animation |
| Nhân vật giống hệt nhau mọi video | Rất tốt — định nghĩa 1 lần trong class Stickman | Tốt — component Stickman dùng lại | Trung bình — phải copy rig, dễ lệch | Tốt — lưu file .stk, nhưng khó chỉnh bằng code | Tốt — 1 file SVG dùng lại |
| Độ khó học cho người mới | Trung bình — cần biết Python cơ bản | Cao — cần biết React + JS/TS + Node | Rất cao — Blender phức tạp | Rất thấp — dễ nhất | Trung bình — cần biết SVG + FFmpeg filter |
| Render 9:16, 1080x1920 | Tốt — config pixel_width/height, frame_width/height | Tốt — config width/height | Tốt — nhưng nặng | Tốt — export 1080x1920 | Tốt — scale 1080:1920 |
| Tốc độ render 45s | Nhanh — vector, 30fps, vài phút trên PC | Nhanh — nhưng cần Node, Chrome headless | Chậm — nặng, không hợp VPS yếu | Rất nhanh — nhẹ | Rất nhanh — nhẹ, chạy tốt trên VPS |
| Tiếng Việt có dấu | Cần cấu hình font, xem Câu 4 | Tốt — dùng font web, render bằng Chrome | Tốt — dùng font hệ thống | Kém — font hệ thống Windows, dễ lỗi dấu | Tốt — nếu font có dấu, xem Câu 4 |
| Version control Git | Rất tốt — code text | Rất tốt — code text | Kém — file .blend nhị phân | Kém — file .piv nhị phân | Tốt — SVG + script là text |
| Miễn phí | Miễn phí — Manim Community Edition, mã nguồn mở | Miễn phí cho cá nhân, có bản Pro trả phí | Miễn phí — mã nguồn mở | Miễn phí — bản cơ bản, có bản trả phí | Miễn phí — SVG + FFmpeg mã nguồn mở |

### 1.2. Vì sao chọn Manim, không chọn các tool còn lại

**A. Manim — CHỌN LÀM STACK CHÍNH**

Ưu điểm:
- Viết animation bằng Python, đúng với yêu cầu "repo code tái sử dụng".
- Nhân vật định nghĩa 1 lần trong class Stickman, mọi video import lại, đảm bảo giống hệt nhau.
- Render vector sắc nét, không vỡ hình khi scale 1080x1920.
- Cộng đồng lớn, tài liệu nhiều, ví dụ sẵn.
- Chạy tốt trên cả Windows RTX 5060 Ti và VPS Linux yếu — vì Manim render bằng CPU, không cần GPU mạnh, xem Câu 6.

Nhược điểm:
- Cần học Python cơ bản và cú pháp Manim.
- Render phức tạp có thể chậm nếu scene có nhiều object, nhưng với stickman đơn giản thì không đáng lo.
- Tiếng Việt cần cấu hình font, xem Câu 4.

**B. Remotion — Lựa chọn thứ 2, nhưng không chọn**

Ưu điểm:
- Dùng React, component tái sử dụng tốt, preview trực tiếp trên trình duyệt.
- Render nhanh, hỗ trợ 9:16 tốt.

Nhược điểm:
- Cần biết React + TypeScript, nặng hơn Manim cho người mới.
- Cần cài Node.js, Chrome headless, dung lượng lớn hơn.
- Không phù hợp nếu bạn không quen JavaScript.

Kết luận: Nếu bạn đã biết React, Remotion là lựa chọn tốt. Nhưng với yêu cầu "repo code, đơn giản, chạy trên VPS yếu", Manim nhẹ hơn và dễ bắt đầu hơn.

**C. Blender Grease Pencil — Không chọn**

Ưu điểm:
- Vẽ 2D trong môi trường 3D, animation mượt, chuyên nghiệp.

Nhược điểm:
- Quá nặng cho Shorts stickman đơn giản.
- Học rất lâu, giao diện phức tạp.
- Khó tái sử dụng bằng code, phải vẽ tay từng pose.
- Render chậm trên VPS yếu, cần GPU để preview mượt.

Kết luận: Chỉ dùng nếu bạn muốn làm animation 2D phức tạp, có chiều sâu, không phải stickman đơn giản.

**D. Pivot Animator — Không chọn làm stack chính**

Ưu điểm:
- Dễ nhất, làm stickman nhanh nhất, không cần code.

Nhược điểm:
- Không phải repo code, không version control tốt.
- Khó tự động hóa, khó tạo hàng loạt video từ script.
- Chỉ chạy trên Windows, không chạy trên VPS Linux.
- Font tiếng Việt và text card khó xử lý.

Kết luận: Dùng để phác thảo pose nhanh, hoặc làm video một lần, không dùng làm repo chính.

**E. SVG + FFmpeg — Không chọn làm stack chính, nhưng dùng làm công cụ phụ**

Ưu điểm:
- Nhẹ nhất, chạy tốt trên VPS yếu.
- SVG là code, tái sử dụng tốt.

Nhược điểm:
- Phải tự viết engine animation (interpolation, easing, timeline), rất tốn thời gian.
- Không có sẵn thư viện animation như Manim.
- Khó làm walk cycle, gesture phức tạp.

Kết luận: Dùng SVG + FFmpeg để render text card, caption, hoặc làm video đơn giản. Không dùng làm engine animation chính.

### 1.3. Quyết định cuối cùng

Stack chính: Manim Community Edition (Python)
Stack phụ: FFmpeg để ghép voice + caption + nhạc nền, xem Câu 6.

Lý do tóm tắt:
- Code Python, tái sử dụng 100%.
- Stickman định nghĩa 1 lần, giống hệt nhau mọi video.
- Render nhanh, nhẹ, chạy được trên VPS yếu.
- Miễn phí, mã nguồn mở, không cần trả phí.

## 2. CẤU TRÚC REPO — TỔ CHỨC RIG ĐỂ TÁI SỬ DỤNG

### 2.1. Nguyên tắc tổ chức

- Một nguồn sự thật duy nhất (Single Source of Truth): Mọi thông số về stickman (chiều cao, độ dày nét, màu sắc, font) chỉ định nghĩa 1 lần trong file config.py / character.py. Không hardcode số liệu trong từng scene.
- Tách rig khỏi nội dung: Rig (nhân vật, pose, walk cycle) ở thư mục src/rig/. Nội dung từng video (script, scene) ở thư mục videos/. Video mới chỉ cần viết file script YAML + scene Python, không sửa rig.
- Mọi thứ là code text: Dùng Git để version control, dễ rollback khi rig bị lỗi.
- Quy ước đặt tên rõ ràng: Ví dụ: videos/2026-11-15_tam-su-nguoi-que/ — ngày + slug.

### 2.2. Layout thư mục / file cụ thể

```
stickman-shorts/
├── README.md                  # Hướng dẫn chạy, quy ước, checklist
├── requirements.txt           # manim, numpy
├── config.py                  # Cấu hình toàn cục: 1080x1920, 30fps, màu, font
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── rig/
│   │   ├── __init__.py
│   │   ├── character.py       # Class Stickman: định nghĩa 1 lần, dùng mọi video
│   │   ├── poses.py           # Các pose: đứng, ngồi, đi, chạy, vẫy tay, buồn, vui
│   │   ├── walk.py            # Walk cycle: 4-8 frame, chân tay di chuyển
│   │   ├── gestures.py        # Gesture: vẫy tay, chỉ tay, gật đầu, lắc đầu
│   │   ├── expressions.py     # Biểu cảm: mắt, miệng — vui, buồn, ngạc nhiên
│   │   └── props.py           # Đạo cụ: bàn, ghế, điện thoại, cốc, sách, cây
│   │
│   ├── scenes/
│   │   ├── __init__.py
│   │   ├── base_scene.py      # Scene cơ sở: nền, text card, transition
│   │   ├── text_card.py       # Text card: tiêu đề, câu thoại, chú thích
│   │   └── transitions.py     # FadeIn, FadeOut, Slide, Zoom
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── text.py            # Xử lý tiếng Việt, chia dòng, font
│   │   ├── timing.py          # Timeline, đồng bộ voice + animation
│   │   └── export.py          # Export 9:16, 1080x1920, 30fps
│   │
│   └── assets/
│       ├── fonts/
│       │   └── BeVietnamPro-Regular.ttf
│       │   └── BeVietnamPro-Bold.ttf
│       ├── audio/
│       │   └── music/         # Nhạc nền miễn phí
│       └── images/
│           └── background.png # Nền trơn nếu cần
│
├── videos/
│   ├── 2026-11-15_tam-su-nguoi-que/
│   │   ├── script.yaml        # Kịch bản: từng scene, thoại, thời gian
│   │   ├── voice.mp3          # Giọng đọc (TTS hoặc thu âm)
│   │   ├── scene.py           # Scene Python cho video này, import rig từ src
│   │   └── output/
│   │       ├── raw.mp4        # Video thô từ Manim
│   │       └── final.mp4      # Video cuối sau khi ghép voice + caption
│   │
│   └── 2026-11-16_chuyen-di-lam/
│       ├── script.yaml
│       ├── voice.mp3
│       ├── scene.py
│       └── output/
│
├── tools/
│   ├── render.sh              # Render 1 video: manim + ffmpeg
│   ├── render_all.sh          # Render hàng loạt
│   └── assemble.py            # Ghép voice + caption bằng FFmpeg
│
└── docs/
    ├── STYLE_GUIDE.md         # Quy chuẩn: màu, font, độ dày nét, tỷ lệ
    └── WORKFLOW.md            # Quy trình làm video 45s, xem Câu 6
```

### 2.3. Giải thích từng phần quan trọng

**A. src/rig/character.py — Trái tim của repo**

- Định nghĩa class Stickman(VGroup) với các bộ phận: head, body, left_arm, right_arm, left_leg, right_leg.
- Mọi thông số (chiều cao, độ dày nét, màu) lấy từ config.py, không hardcode.
- Cung cấp các phương thức: set_pose(), walk(), wave(), sit(), jump().
- Ví dụ: character.py sẽ được trình bày đầy đủ ở Câu 5.

**B. src/rig/poses.py — Thư viện pose**

- Mỗi pose là một dict chứa tọa độ các khớp: ví dụ pose "đứng", "ngồi", "vẫy tay".
- Dùng hàm lerp (nội suy) để chuyển pose mượt mà, không giật.

**C. src/rig/walk.py — Walk cycle**

- Walk cycle 8 frame: chân trái trước, chân phải sau, tay đung đưa ngược pha.
- Dùng hàm walk_cycle(t) trả về pose tại thời điểm t, lặp lại liên tục.

**D. videos/<ngày>_<slug>/script.yaml — Kịch bản chuẩn**

Ví dụ script.yaml:

```yaml
video:
  title: "Tâm sự người que"
  duration: 45
  resolution: "1080x1920"
  fps: 30

scenes:
  - id: intro
    duration: 3
    text: "Tâm sự người que"
    animation: "stickman_walk_in"
    voice: "Chào các bạn, hôm nay..."

  - id: scene1
    duration: 8
    text: "Hôm nay đi làm muộn..."
    animation: "stickman_walk"
    voice: "..."

  - id: outro
    duration: 3
    text: "Cảm ơn các bạn đã xem"
    animation: "stickman_wave"
    voice: "Cảm ơn..."
```

**E. Quy tắc khi thêm video mới**

1. Tạo thư mục mới trong videos/ theo quy ước ngày + slug.
2. Viết script.yaml — không cần viết code Python nếu scene đã có sẵn.
3. Nếu cần scene mới, tạo file scene.py import rig từ src/rig/, không copy code rig.
4. Chạy tools/render.sh để render và ghép voice.
5. Kiểm tra output/final.mp4 trước khi đăng.

## 3. TÍNH NHẤT QUÁN — GIỮ STICKMAN GIỐNG HỆT NHAU MỌI VIDEO

### 3.1. Nguyên tắc vàng: Không bao giờ vẽ lại stickman bằng tay trong từng video

- Mọi video đều import class Stickman từ src/rig/character.py.
- Không copy-paste code vẽ stickman sang file scene.py.
- Nếu muốn thay đổi stickman (ví dụ: đổi độ dày nét), chỉ sửa 1 file character.py, mọi video sau đó tự động cập nhật.

### 3.2. Khóa các thông số trong config.py

Tạo file config.py duy nhất, chứa mọi thông số:

```python
# config.py
# Mọi thông số về stickman chỉ định nghĩa ở đây, không hardcode ở nơi khác

# Kích thước
STICKMAN_HEIGHT = 300  # px, chiều cao toàn thân
HEAD_RADIUS = 40       # px, bán kính đầu
BODY_LENGTH = 100      # px, thân
ARM_LENGTH = 80        # px, tay
LEG_LENGTH = 100       # px, chân

# Độ dày nét vẽ
STROKE_WIDTH = 8       # px, nét chính
STROKE_WIDTH_THIN = 4  # px, nét phụ (mắt, miệng)

# Màu sắc (hex, không dùng tên màu)
COLOR_BLACK = "#000000"
COLOR_WHITE = "#FFFFFF"
COLOR_RED = "#FF0000"
COLOR_BLUE = "#0000FF"
COLOR_GREEN = "#00FF00"

# Font chữ
FONT_FAMILY = "Be Vietnam Pro"
FONT_SIZE_TITLE = 72
FONT_SIZE_BODY = 48

# Video
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30
```

### 3.3. Các kỹ thuật đảm bảo nhất quán

**A. Dùng hằng số, không dùng số magic**

- Sai: Circle(radius=0.6) — không biết 0.6 là gì, dễ lệch khi sửa.
- Đúng: Circle(radius=HEAD_RADIUS) — rõ ràng, sửa 1 chỗ.

**B. Viết test kiểm tra rig**

Tạo file tests/test_character.py để kiểm tra stickman sau mỗi lần sửa rig:

- Kiểm tra chiều cao stickman = 300px.
- Kiểm tra độ dày nét = 8px.
- Kiểm tra màu sắc = #000000.
- Render 1 frame mẫu, so sánh với frame chuẩn bằng mắt hoặc bằng script.

**C. Lưu frame chuẩn (reference frame)**

- Render 1 frame stickman đứng, lưu làm assets/reference/stickman_standing.png.
- Mỗi lần sửa rig, render lại và so sánh với frame chuẩn.
- Nếu khác, kiểm tra lại config.py.

**D. Dùng Git để khóa version rig**

- Khi rig đã ổn định, tạo tag git: git tag v1.0-rig-stable
- Video mới dùng rig v1.0, không dùng rig đang sửa dở.
- Nếu cần cải tiến rig, tạo branch mới, test xong mới merge.

**E. Quy chuẩn trong STYLE_GUIDE.md**

Viết file docs/STYLE_GUIDE.md ghi rõ:

- Tỷ lệ cơ thể: Đầu : Thân : Chân = 1 : 2.5 : 2.5
- Độ dày nét: 8px cho thân, 4px cho mắt/miệng.
- Màu sắc: Chỉ dùng đen #000000 trên nền trắng #FFFFFF, trừ khi cần nhấn mạnh thì dùng đỏ #FF0000.
- Font: Be Vietnam Pro, size 48 cho body, 72 cho tiêu đề.
- Vị trí: Stickman luôn đứng ở giữa khung hình, cách đáy 200px, trừ khi scene yêu cầu khác.

## 4. TIẾNG VIỆT — DẤU TIẾNG VIỆT RENDER NHƯ THẾ NÀO TRONG MANIM

### 4.1. Manim render text như thế nào

Manim Community Edition render text bằng 2 cách:
- Text: Dùng Pango / Cairo để render, hỗ trợ Unicode tốt, bao gồm tiếng Việt có dấu.
- Tex: Dùng LaTeX để render, cần gói tiếng Việt, phức tạp hơn.

Khuyến nghị: Dùng Text, không dùng Tex, cho mọi text card tiếng Việt.

Ví dụ:
```python
# Đúng — dùng Text
Text("Tâm sự người que", font="Be Vietnam Pro")

# Sai — dùng Tex, dễ lỗi dấu
Tex(r"Tâm sự người que")  # Cần cấu hình LaTeX tiếng Việt
```

### 4.2. Font nào dùng cho tiếng Việt

Font khuyên dùng: Be Vietnam Pro

- Lý do: Font Việt hóa hoàn chỉnh, có đủ dấu, thiết kế hiện đại, miễn phí, dùng cho cả tiêu đề và body.
- Tải tại: Google Fonts — Be Vietnam Pro, hoặc github.com/NguyenNhatVuong/BeVietnamPro
- Cài đặt: Copy file .ttf vào src/assets/fonts/, và cài vào hệ thống (Windows: click đúp → Install; Linux: copy vào ~/.fonts/ → fc-cache -f -v).

Các font khác cũng tốt:
- Noto Sans: Hỗ trợ tiếng Việt tốt, có nhiều weight.
- Inter: Hiện đại, hỗ trợ tiếng Việt.
- Roboto: Phổ biến, hỗ trợ tiếng Việt.
- Arial / Times New Roman: Có sẵn trên Windows, hỗ trợ tiếng Việt, nhưng không đẹp bằng Be Vietnam Pro.

Font cần tránh:
- Font không có dấu tiếng Việt: Ví dụ: một số font trang trí chỉ có ASCII, sẽ hiển thị dấu thành ô vuông hoặc mất dấu.
- Font quá mỏng: Nét mỏng khó đọc trên Shorts 1080x1920 khi xem trên điện thoại.

### 4.3. Các cạm bẫy thường gặp và cách tránh

Cạm bẫy 1: Dấu bị mất hoặc thành ô vuông □
- Nguyên nhân: Font không hỗ trợ tiếng Việt.
- Cách tránh: Chỉ dùng font đã kiểm tra có dấu đầy đủ. Test bằng câu: "Tâm sự người que — Ăn cơm chưa? Đi làm muộn, ồ ạt, ứ ự, ỹ, ỳ, ỵ."
- Kiểm tra: Render 1 text card test trước khi làm video thật.

Cạm bẫy 2: Dấu bị lệch, chồng lên nhau
- Nguyên nhân: Manim dùng Pango, nhưng một số font có kerning không tốt với tiếng Việt.
- Cách tránh: Dùng Be Vietnam Pro hoặc Noto Sans, đã được tối ưu cho tiếng Việt. Tránh dùng font nước ngoài chưa Việt hóa.

Cạm bẫy 3: Text quá dài, tràn khung hình 9:16
- Nguyên nhân: Text card tiếng Việt dài, không chia dòng.
- Cách tránh: Giới hạn mỗi text card tối đa 2 dòng, mỗi dòng tối đa 12-15 từ. Dùng hàm chia dòng tự động trong src/utils/text.py.

Ví dụ hàm chia dòng:
```python
def split_text(text, max_chars=30):
    # Chia text thành nhiều dòng, mỗi dòng <= 30 ký tự
    words = text.split()
    lines = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 <= max_chars:
            current += word + " "
        else:
            lines.append(current.strip())
            current = word + " "
    lines.append(current.strip())
    return lines
```

Cạm bẫy 4: Font không tìm thấy trên VPS Linux
- Nguyên nhân: Font chỉ cài trên Windows, không có trên VPS.
- Cách tránh: Copy font vào src/assets/fonts/ trong repo, và trong code chỉ định đường dẫn font tuyệt đối, hoặc cài font vào VPS bằng lệnh:
  ```
  mkdir -p ~/.fonts
  cp src/assets/fonts/*.ttf ~/.fonts/
  fc-cache -f -v
  ```

Cạm bẫy 5: Dùng Tex (LaTeX) cho tiếng Việt
- Nguyên nhân: Tex cần gói vietnam, cấu hình phức tạp, dễ lỗi.
- Cách tránh: Không dùng Tex cho text tiếng Việt. Chỉ dùng Text (Pango).

Cạm bẫy 6: Kích thước font quá nhỏ, khó đọc trên điện thoại
- Nguyên nhân: Font size 24-32 quá nhỏ trên 1080x1920.
- Cách tránh: Font size tối thiểu 48 cho body, 72 cho tiêu đề, xem config.py ở Câu 3.

### 4.4. Checklist test tiếng Việt trước khi làm video thật

1. Render text: "Tâm sự người que — Ăn cơm chưa?"
2. Kiểm tra dấu: ă, â, ê, ô, ơ, ư, đ, á, à, ả, ã, ạ, ấ, ầ, ẩ, ẫ, ậ, ớ, ờ, ở, ỡ, ợ, ứ, ừ, ử, ữ, ự, ỳ, ỵ, ỷ, ỹ.
3. Kiểm tra font: Be Vietnam Pro hiển thị đúng, không bị ô vuông.
4. Kiểm tra trên cả Windows và VPS Linux.

## 5. CODE MẪU KHỞI ĐẦU — VÍ DỤ TỐI THIỂU CHẠY ĐƯỢC TRONG MANIM

### 5.1. File character.py — Định nghĩa stickman 1 lần

```python
# character.py
import manim as mn
from dataclasses import dataclass
import numpy as np

# 1.1 Kích thước & tọa độ
WIDTH = 1080
HEIGHT = 1920
STICKMAN_HEIGHT = 300

# 1.2 Màu sắc (hex)
BLACK = "#000000"
WHITE = "#FFFFFF"
RED = "#FF0000"
BLUE = "#0000FF"
GREEN = "#00FF00"

# 1.3 Font chữ tiếng Việt
TEXT_FONT = "Be Vietnam Pro"
# 1.4 Độ dày đường vẽ
STROKE_WIDTH = 8
STROKE_WIDTH_THIN = 4

@dataclass
class Pose:
    head: tuple
    body: tuple
    left_arm: tuple
    right_arm: tuple
    left_leg: tuple
    right_leg: tuple

class Character:
    def __init__(self):
        self.name = "Stickman"
        self.height = STICKMAN_HEIGHT
        self.color = BLACK
        self.stroke_width = STROKE_WIDTH

    def create_stickman(self, position):
        # Vẽ stickman tại vị trí position
        # Head: circle
        # Body: line
        # Arms: 2 lines
        # Legs: 2 lines
        pass

    def walk_cycle(self, t):
        # Trả về pose tại thời điểm t
        # Dùng sin/cos để tạo chuyển động chân tay
        pass

    def wave_hand(self, t):
        # Vẫy tay: tay phải giơ lên, vẫy qua lại
        pass
```

### 5.2. File stickman_demo.py — Ví dụ tối thiểu: đi vào, vẫy tay, text card xuất hiện, export 9:16

```python
# stickman_demo.py
from manim import *
import numpy as np

# ==========================================
# VIDEO CONFIGURATION
# ==========================================
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9
config.frame_height = 16
config.frame_rate = 30
config.background_color = WHITE

# ==========================================
# STICKMAN RIG
# ==========================================
class Stickman(VGroup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Head
        self.head = Circle(radius=0.6, color=BLACK, stroke_width=8)
        self.head.move_to(UP * 2.5)

        # Body
        self.body = Line(UP * 1.9, DOWN * 0.5, color=BLACK, stroke_width=8)

        # Arms
        self.left_arm = Line(UP * 1.5, LEFT * 0.8 + UP * 1.0, color=BLACK, stroke_width=8)
        self.right_arm = Line(UP * 1.5, RIGHT * 0.8 + UP * 1.0, color=BLACK, stroke_width=8)

        # Legs
        self.left_leg = Line(DOWN * 0.5, LEFT * 0.5 + DOWN * 1.5, color=BLACK, stroke_width=8)
        self.right_leg = Line(DOWN * 0.5, RIGHT * 0.5 + DOWN * 1.5, color=BLACK, stroke_width=8)

        self.add(self.head, self.body, self.left_arm, self.right_arm, self.left_leg, self.right_leg)
        self.move_to(ORIGIN)

    def get_arm_end(self, arm):
        # Trả về điểm cuối của tay
        return arm.get_end()

    def set_pose(self, pose):
        # Đặt pose cho stickman
        # pose là dict chứa tọa độ các khớp
        pass

    def walk(self, direction=RIGHT, distance=4):
        # Tạo animation đi bộ
        return self.animate.shift(direction * distance)

    def wave(self):
        # Tạo animation vẫy tay
        # Tay phải giơ lên, vẫy qua lại
        wave_animation = self.right_arm.animate.rotate(PI / 4, about_point=self.right_arm.get_start())
        return wave_animation

# ==========================================
# MAIN SCENE
# ==========================================
class StickmanScene(Scene):
    def construct(self):
        # 1. Tạo stickman
        stickman = Stickman()
        stickman.move_to(LEFT * 5 + DOWN * 2)

        # 2. Stickman đi vào khung hình
        self.play(FadeIn(stickman, shift=RIGHT * 1))
        self.play(stickman.animate.shift(RIGHT * 4), run_time=2)

        # 3. Stickman vẫy tay
        self.play(stickman.wave(), run_time=1.5)

        # 4. Text card xuất hiện
        card = RoundedRectangle(corner_radius=0.2, width=7, height=2, color=BLACK, fill_opacity=0.1)
        card.move_to(UP * 3)
        text = Text("Tâm sự người que", font="Be Vietnam Pro", font_size=48, color=BLACK)
        text.move_to(card.get_center())
        card_group = VGroup(card, text)

        self.play(FadeIn(card_group, shift=UP * 0.5))
        self.wait(1.5)

        # 5. Kết thúc
        self.play(FadeOut(card_group))
        self.wait(0.5)

# ==========================================
# HELPER: animation() để tạo walk cycle
# ==========================================
def animation():
    # Hàm này dùng để tạo animation đi bộ
    # Tính toán vị trí chân tay theo thời gian
    # Dùng sin/cos để tạo chuyển động
    t = 0
    # Ví dụ: chân trái trước, chân phải sau
    left_leg_angle = np.sin(t * 2 * np.pi) * 0.5
    right_leg_angle = np.sin(t * 2 * np.pi + np.pi) * 0.5
    return left_leg_angle, right_leg_angle

if __name__ == "__main__":
    # Chạy thử: python -m manim render -qm --format=mp4 stickman_demo.py StickmanScene
    pass
```

### 5.3. Chạy thử (Windows)

```bash
# Cài đặt Manim (Windows)
pip install manim

# Cài đặt font Be Vietnam Pro
# Tải tại: https://fonts.google.com/specimen/Be+Vietnam+Pro
# Copy vào C:\Windows\Fonts\

# Render video 9:16
manim render -qm --format=mp4 stickman_demo.py StickmanScene

# Output: media/videos/stickman_demo/1080p30/StickmanScene.mp4

# Kiểm tra video:
# - Độ phân giải: 1080x1920
# - FPS: 30
# - Thời lượng: ~5 giây (demo)
```

### 5.4. Chạy thử (VPS Linux)

```bash
# Cài đặt Manim (Ubuntu/Debian)
sudo apt update
sudo apt install -y ffmpeg texlive-latex-base texlive-latex-extra dvisvgm
pip install manim

# Cài đặt font Be Vietnam Pro
mkdir -p ~/.fonts
cp src/assets/fonts/*.ttf ~/.fonts/
fc-cache -f -v

# Render video 9:16
manim render -qm --format=mp4 stickman_demo.py StickmanScene

# Output: media/videos/stickman_demo/1080p30/StickmanScene.mp4
```

### 5.5. Lưu ý khi chạy code mẫu

- Code trên là ví dụ tối thiểu, chưa có walk cycle đầy đủ. Để có walk cycle mượt, xem file src/rig/walk.py ở Câu 2.
- Nếu gặp lỗi font: Kiểm tra font đã cài chưa, và trong code dùng font="Be Vietnam Pro" đúng tên.
- Nếu gặp lỗi LaTeX: Manim cần LaTeX để render Tex, nhưng ví dụ này chỉ dùng Text, không cần LaTeX. Nếu vẫn lỗi, cài texlive như hướng dẫn ở trên.
- Nếu video không phải 9:16: Kiểm tra config.pixel_width = 1080, config.pixel_height = 1920, config.frame_width = 9, config.frame_height = 16.

## 6. WORKFLOW + THỜI GIAN — SCRIPT → SCENES → RENDER → GHÉP VOICE + CAPTION BẰNG FFMPEG

### 6.1. Quy trình tổng thể

Script (viết kịch bản)
  ↓
Chia scenes (từng scene 3-8s)
  ↓
Viết scene.py (import rig, không vẽ lại stickman)
  ↓
Render bằng Manim (raw.mp4, không có voice)
  ↓
Ghép voice + caption + nhạc nền bằng FFmpeg (final.mp4)
  ↓
Kiểm tra final.mp4, đăng YouTube Shorts

### 6.2. Chi tiết từng bước

**Bước 1: Viết script (10-15 phút)**
- Viết kịch bản 45s, khoảng 100-120 từ tiếng Việt.
- Chia thành 5-7 scenes, mỗi scene 5-8s.
- Viết file videos/<ngày>_<slug>/script.yaml, xem mẫu ở Câu 2.

**Bước 2: Chuẩn bị voice (5-10 phút)**
- Dùng TTS miễn phí (ví dụ: Google TTS, Viettel AI, FPT AI — cần kiểm tra bản miễn phí) hoặc tự thu âm.
- Lưu file voice.mp3 vào thư mục video.
- Kiểm tra thời lượng voice khớp với script (45s).

**Bước 3: Viết scenes (15-30 phút khi rig đã có sẵn)**
- Mở file scene.py mẫu, sửa text card và animation cho từng scene.
- Không cần viết lại rig, chỉ cần gọi: stickman.walk(), stickman.wave(), text_card("...").
- Nếu scene đã có sẵn trong thư viện (ví dụ: walk_in, wave, text_card), chỉ cần sửa script.yaml, không cần viết code.

**Bước 4: Render bằng Manim (3-5 phút trên PC RTX 5060 Ti, 5-10 phút trên VPS yếu)**
- Chạy: manim render -qm --format=mp4 scene.py StickmanScene
- Output: raw.mp4 (1080x1920, 30fps, không có voice).
- Kiểm tra raw.mp4: stickman có giống nhau không, text có lỗi dấu không.

**Bước 5: Ghép voice + caption bằng FFmpeg (1-2 phút)**
- Dùng lệnh FFmpeg để ghép voice.mp3 + raw.mp4 + caption.srt:
  ```
  ffmpeg -i raw.mp4 -i voice.mp3 -i caption.srt -c:v libx264 -c:a aac -c:s mov_text -map 0:v -map 1:a -map 2:s output/final.mp4
  ```
- Hoặc dùng script tools/assemble.py để tự động hóa.

**Bước 6: Kiểm tra và đăng (5 phút)**
- Xem final.mp4 trên điện thoại, kiểm tra text, voice, caption có đồng bộ không.
- Đăng lên YouTube Shorts, thêm tiêu đề, mô tả, hashtag.

### 6.3. Tổng thời gian cho 1 video 45s khi rig đã có sẵn

| Công đoạn | Thời gian (rig đã có) | Ghi chú |
|---|---|---|
| Viết script | 10-15 phút | Nhanh nếu đã có ý tưởng |
| Chuẩn bị voice | 5-10 phút | TTS hoặc thu âm |
| Viết scenes | 15-30 phút | Chỉ sửa script.yaml + text, không vẽ lại rig |
| Render Manim | 3-5 phút (PC) / 5-10 phút (VPS) | Xem 6.4 |
| Ghép FFmpeg | 1-2 phút | Nhanh, chỉ ghép |
| Kiểm tra + đăng | 5 phút | Xem trên điện thoại |
| **Tổng** | **40-70 phút** | **Khoảng 1 giờ cho 1 video 45s** |

Lưu ý: Thời gian trên là khi rig đã ổn định và bạn đã quen workflow. Video đầu tiên sẽ lâu hơn (2-3 giờ) vì phải học Manim và sửa rig.

### 6.4. Cái gì chạy trên VPS Linux yếu, cái gì chạy trên PC Windows RTX 5060 Ti

| Máy | Nên chạy | Không nên chạy | Lý do |
|---|---|---|---|
| VPS Linux yếu (4 CPU, 8GB RAM, không GPU) | - Render Manim cho video đơn giản (stickman, text card) - Ghép FFmpeg (voice + caption) - Chạy script tự động hóa, render hàng loạt qua đêm | - Render Manim cho scene phức tạp (nhiều object, hiệu ứng nặng) - Preview video trực tiếp | - Manim render bằng CPU, không cần GPU, chạy tốt trên VPS yếu cho video đơn giản - FFmpeg nhẹ, chạy tốt trên VPS - VPS chạy 24/7, có thể render hàng loạt qua đêm |
| PC Windows RTX 5060 Ti 16GB | - Render Manim cho scene phức tạp - Preview video, kiểm tra chất lượng - Viết code, sửa rig, test nhanh - Render hàng loạt nhanh | - Không cần chạy 24/7, tốn điện | - RTX 5060 Ti không giúp Manim render nhanh hơn nhiều, vì Manim chủ yếu dùng CPU, không dùng GPU để render vector - Nhưng PC mạnh hơn VPS về CPU, RAM, nên render nhanh hơn 2-3 lần |

Kết luận phân công:
- VPS: Render hàng loạt, ghép FFmpeg, chạy tự động qua đêm.
- PC: Viết code, test nhanh, render video phức tạp, kiểm tra chất lượng.

### 6.5. Mẹo tăng tốc workflow

- Dùng template: Tạo file scene_template.py, mỗi video mới copy template, sửa text.
- Dùng script.yaml: Nếu scene đã có sẵn, chỉ cần sửa script.yaml, không cần viết code Python.
- Render ở chất lượng thấp để test: manim render -ql (low quality) để test nhanh, sau đó render -qm (medium) để xuất bản.
- Dùng cache: Manim cache các frame đã render, lần render sau sẽ nhanh hơn nếu chỉ sửa text.

## 7. BẠN KHÔNG CHẮC CHẮN VỀ ĐIỀU GÌ? NÓI RÕ THAY VÌ ĐOÁN

Tôi sẽ nói rõ những điểm tôi KHÔNG chắc chắn, thay vì đoán:

### 7.1. Về hiệu năng render Manim trên VPS yếu của bạn
- Tôi KHÔNG chắc chắn chính xác thời gian render 45s trên VPS 4 CPU / 8GB RAM của bạn là bao lâu, vì tôi không biết chính xác CPU model, tốc độ ổ cứng, và số lượng object trong scene của bạn.
- Ước tính ở Câu 6 (5-10 phút) là dựa trên kinh nghiệm chung với Manim và video stickman đơn giản, không phải đo thực tế trên máy của bạn.
- Cách kiểm tra: Render video demo ở Câu 5 trên VPS của bạn, đo thời gian thực tế, sau đó mới ước tính cho video 45s.

### 7.2. Về font Be Vietnam Pro có hiển thị đúng 100% trên Manim + Pango hay không
- Tôi KHÔNG chắc chắn 100% rằng Be Vietnam Pro sẽ hiển thị đúng mọi dấu tiếng Việt trên mọi phiên bản Manim + Pango, vì có thể có lỗi kerning hoặc lỗi font tùy phiên bản.
- Tôi khuyên dùng Be Vietnam Pro vì đây là font Việt hóa tốt, nhưng bạn cần test thực tế với câu test ở Câu 4 trước khi làm video thật.

### 7.3. Về TTS tiếng Việt miễn phí nào tốt nhất hiện tại
- Tôi KHÔNG chắc chắn TTS miễn phí nào tốt nhất cho giọng đọc Shorts tiếng Việt vào tháng 11/2026, vì các dịch vụ TTS thay đổi chính sách miễn phí thường xuyên.
- Tôi đề cập Google TTS, Viettel AI, FPT AI ở Câu 6, nhưng bạn cần kiểm tra lại chính sách miễn phí và chất lượng giọng đọc tại thời điểm bạn làm video.

### 7.4. Về code mẫu ở Câu 5 có chạy được ngay 100% hay không
- Tôi KHÔNG chắc chắn code mẫu ở Câu 5 sẽ chạy được ngay 100% trên máy của bạn mà không cần sửa, vì:
  - Phiên bản Manim Community Edition có thể thay đổi API (ví dụ: hàm wave(), set_pose()).
  - Font Be Vietnam Pro có thể chưa được cài trên máy của bạn.
  - Cấu hình LaTeX / Pango có thể khác nhau giữa Windows và Linux.
- Cách kiểm tra: Chạy code mẫu, nếu lỗi, đọc thông báo lỗi và sửa theo hướng dẫn ở 5.5.

### 7.5. Về việc Manim có dùng GPU RTX 5060 Ti để render nhanh hơn hay không
- Tôi KHÔNG chắc chắn Manim có tận dụng được RTX 5060 Ti để render nhanh hơn hay không, vì Manim Community Edition chủ yếu render bằng CPU (Cairo / Pango), không dùng GPU để render vector.
- Một số phiên bản Manim có hỗ trợ OpenGL renderer (manim --renderer=opengl), có thể dùng GPU, nhưng tôi không chắc chắn hiệu quả thực tế với stickman đơn giản.
- Cách kiểm tra: Thử render với --renderer=opengl và so sánh thời gian với renderer mặc định (Cairo).

### 7.6. Về chính sách miễn phí của Remotion
- Tôi KHÔNG chắc chắn chính sách miễn phí của Remotion vào tháng 11/2026, vì Remotion có bản Pro trả phí và chính sách có thể thay đổi.
- Tôi chỉ đề cập Remotion miễn phí cho cá nhân dựa trên thông tin chung, bạn cần kiểm tra lại tại remotion.dev nếu bạn muốn dùng Remotion.

## KẾT LUẬN

- Stack chính: Manim Community Edition (Python) + FFmpeg.
- Repo: src/rig/character.py định nghĩa stickman 1 lần, mọi video import lại.
- Nhất quán: Khóa mọi thông số trong config.py, dùng Git tag để khóa version rig.
- Tiếng Việt: Dùng Text (Pango) + font Be Vietnam Pro, test dấu trước khi làm video thật.
- Thời gian: Khoảng 40-70 phút cho 1 video 45s khi rig đã có sẵn.
- Bước tiếp theo: Chạy code mẫu ở Câu 5, test render 5s, kiểm tra font tiếng Việt, sau đó mới xây repo đầy đủ ở Câu 2.

Nguồn ChatGPT liệt kê trong câu trả lời: manim.community, docs.manim.community (installation, Text), remotion.dev/docs, github.com/ManimCommunity/manim, github.com/3b1b/manim, blender.org, docs.blender.org/manual/en/latest/grease_pencil, pivotanimator.net, ffmpeg.org, fonts.google.com/specimen/Be+Vietnam+Pro, github.com/NguyenNhatVuong/BeVietnamPro, noto-website-2.storage.googleapis.com, fonts.google.com/noto, cùng tài liệu chung về Manim Community Edition, Remotion, Blender Grease Pencil, Pivot Animator và SVG + FFmpeg.

---

## Đối chiếu với Gemini (gemini-stickman-20261115.md)

| Điểm | Gemini | ChatGPT |
|---|---|---|
| Stack chính | Remotion (React + TypeScript + SVG) | Manim Community Edition (Python) |
| Lý do chính | Khớp xương `<g>` cha-con, preview tức thì, Text Card CSS mạnh nhất | Python nhẹ, render CPU, chạy được trên VPS yếu, cộng đồng lớn |
| Render ở đâu | PC RTX 5060 Ti (VPS dễ OOM vì Chromium) | Cả VPS lẫn PC (Manim dùng CPU, không cần GPU) |
| Thời gian / video 45s | 25-35 phút | 40-70 phút |
| Text tiếng Việt | Be Vietnam Pro, nhúng .ttf, NFC, lineHeight ≥1.32 | Be Vietnam Pro, dùng Text (Pango), KHÔNG dùng Tex |
| Điểm đồng thuận | Be Vietnam Pro; nhân vật định nghĩa 1 lần; khóa thông số bất biến; mỗi video mới chỉ thêm 1 file; workflow audio-first; FFmpeg ghép cuối | (như bên trái) |
| Điểm khác cần chốt | -14 LUFS / ~140 từ (trái với quy tắc dự án -16 LUFS, 112-124 từ) | 100-120 từ (hơi chậm hơn vùng an toàn 112-124), render VPS 5-10 phút chưa đo thực tế |

Quyết định stack chưa chốt — chờ chủ chọn (xem tin nhắn chính).
