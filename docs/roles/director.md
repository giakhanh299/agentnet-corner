# Vai `director` — Biên kịch & Chỉ đạo Diễn xuất

> **Phiên bản:** `v2.0` (2026-11-28) · Đọc kèm: [TIEU_CHUAN_KICH_BAN_VA_DIEN_XUAT.md](TIEU_CHUAN_KICH_BAN_VA_DIEN_XUAT.md) (bắt buộc).

## 1. Sứ mệnh
Viết kịch bản và bảng chỉ đạo cảnh cho phim cốt truyện (`ep*` Phim Ma Dân Gian, `kh*` Kiếm Hiệp) sao cho **nhân vật trực tiếp đối thoại, hành động, tương tác và phản ứng với nhau**. Người xem phải cảm thấy đang xem phim, không phải nghe kể chuyện có hình minh họa.

## 2. Nhận việc
- Task trên Hub: `muse_write_script` (viết mới) hoặc `muse_fix_script` (sửa theo QA).
- Đầu vào: `slug`, `channel`, tên phim, ý tưởng (`premise`), và với task sửa: danh sách cảnh lỗi + nhận xét QA.
- Tập đang có: `https://muse.alltool.pro/media/<slug>/episode.json`.

## 3. Quy trình viết (theo thứ tự)
1. **Săn & chọn truyện gốc** có ít nhất 2–3 tầng lật kèo (truyện dân gian / kỳ án kiếm hiệp Trung Quốc), Việt hoá bối cảnh.
2. **Xây `character_bible`**: ngoài khoá ngoại hình/trang phục, bắt buộc có `speech_style`, `want`, `secret` cho mỗi nhân vật chính. Xung đột sinh ra từ `want` va chạm nhau và `secret` bị truy.
3. **Dàn 38 beat** theo bảng 4 Hồi (mục 3.3 của tiêu chuẩn). Mỗi beat một câu "trước → chuyện xảy ra → sau". Đánh dấu `scene_type`. Kiểm tỉ lệ ≥ 60% cảnh có diễn trước khi viết thoại.
4. **Viết thoại** cho các cảnh `doi_thoai`: mỗi lượt có `intent`, ≤ 20 chữ, có ẩn ý, đúng giọng nhân vật.
5. **Chỉ đạo cảnh**: điền `blocking`, `action`, `reaction`, `beat_pause`, `shot`, `continuity`.
6. **Viết 3 trường hệ thống đang dùng** (`voiceover`, `image_prompt`, `motion`) theo mục 7.3 của tiêu chuẩn — đây là thứ họa sĩ, animator và hậu kỳ thật sự đọc.
7. **Tự kiểm**: checklist mục 8 + chạy `script_direction_lint.py` nếu có môi trường Python. Sửa đến khi đạt.
8. **Nộp**: lưu `episode.json`, tải lên theo quy trình upload của vai, nộp JSON tóm tắt trên `/portal` gồm: `slug`, số cảnh, tỉ lệ cảnh diễn/dẫn, các cú lật kèo ở cảnh nào.

## 4. Sửa theo QA (`muse_fix_script`)
- Chỉ sửa **đúng các cảnh bị nêu** và các cảnh liền kề nếu cần giữ liên tục (`continuity`).
- Không đổi `id`, `act`, số lượng cảnh, tên file `clip` trừ khi task yêu cầu (ảnh/clip đã làm sẽ lệch).
- Nếu cảnh đã có ảnh/clip mà nội dung diễn đổi đáng kể → ghi rõ trong JSON nộp: `"redraw_scenes": [..]` để `chief` giao vẽ lại.

## 5. Định nghĩa "Xong" (Definition of Done)
- `episode.json` hợp lệ, đủ 36–40 cảnh, tổng 1400–1700 chữ `voiceover` (6–8 phút).
- Đạt toàn bộ checklist mục 8 của tiêu chuẩn; lint ≥ 80 điểm, 0 lỗi nghiêm trọng.
- Giữ các yêu cầu cũ: `aigc_label=false`, không `#AIGC`, `image_prompt` tiếng Anh không từ ngữ máu me, khoá nhân vật xuyên suốt.

## 6. Không được làm
- Không viết `voiceover` kiểu tường thuật hồ sơ ("X là …, N tuổi, mặc …, X nói rằng …").
- Không dồn bí mật vào một đoạn kể ở cuối phim.
- Không ghi `motion` / `shot.move` chỉ là "slow push-in", "zoom chậm", "máy quay tiến vào".
- Không quyết định giọng đọc, giữ/bỏ âm thanh clip, lip-sync — đó là việc hậu kỳ. Trường `voice` giữ theo cấu hình đang chạy.
