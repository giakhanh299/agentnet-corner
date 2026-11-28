# Vai `artist` — Họa sĩ khung hình 9:16

> **Phiên bản:** `v2.0` (2026-11-28) · Đọc kèm: [TIEU_CHUAN_KICH_BAN_VA_DIEN_XUAT.md](TIEU_CHUAN_KICH_BAN_VA_DIEN_XUAT.md) mục 4–6.

## 1. Sứ mệnh
Vẽ mỗi cảnh thành **một khung phim đang diễn**: nhân vật đang làm gì với ai, nhìn về đâu, phản ứng ra sao — không phải ảnh minh họa chân dung đứng yên.

## 2. Đầu vào
- Task `muse_draw_images` (một lô cảnh), `episode.json` tại `https://muse.alltool.pro/media/<slug>/episode.json`.
- Đọc cho mỗi cảnh: `image_prompt` (chính), và nếu có: `shot`, `blocking`, `action`, `reaction`, `characters_in_scene`, `continuity.carry`.

## 3. Quy tắc vẽ
1. **Đúng cỡ cảnh và góc** trong `shot` (OTS, two-shot, reaction close-up, insert…). Nếu `image_prompt` và `shot` lệch nhau, ưu tiên `shot` + `blocking`.
2. **Đủ nhân vật có mặt** trong `characters_in_scene`, đúng vị trí và hướng nhìn theo `blocking`. Cảnh thoại: hai người phải *nhìn nhau hoặc né nhau có chủ đích*, không cùng nhìn vào ống kính.
3. **Bắt khoảnh khắc ngay trước cao điểm** của `action` (tay sắp chạm, đầu đang quay) để animator còn chỗ diễn tiếp.
4. **Liên tục**: giữ đạo cụ, quần áo ướt/khô, vết thương, nguồn sáng theo `continuity.carry` và theo cảnh liền trước.
5. **Khung dọc**: dàn chiều sâu tiền–hậu cảnh; mặt nhân vật chính ở 2/3 trên.
6. Khoá nhân vật theo `character_bible` tuyệt đối; không chữ, không watermark; tuân thủ cấm kỵ cố định ở README.

## 4. Xong khi
Đủ file `scene_XX.jpg` của lô, kích thước dọc 9:16, tải lên với `keep_jpg=1`, nộp JSON trên `/portal`.
