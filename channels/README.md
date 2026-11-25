# channels/ · Thư mục riêng của từng kênh

Mỗi kênh sống trên **nhánh riêng** tách từ `feat/core-shared`:

| Nhánh | Thư mục | Kênh |
| :--- | :--- | :--- |
| `feat/phim-ma-dan-gian` | `channels/phim-ma-dan-gian/` | Phim ma dân gian Việt Nam (phòng họp Muse, Pilot #1 *Ma Da Kéo Giò*) |
| `feat/tap-lam-content` | `channels/tap-lam-content-k08/` | KENH_008 · Tập Làm Content (video ngắn kiến thức, đồng bộ sang hàng chờ duyệt FB) |

Trong mỗi thư mục kênh: kịch bản, `scenes.json`, preset giọng/nhạc, prompt riêng, script đồng bộ. Công cụ dùng chung lấy từ `auto99/`, `bridges/`, `studio/`, `assets/` — không chép lại.

Nhận công cụ mới: `git merge feat/core-shared` trên nhánh kênh.
