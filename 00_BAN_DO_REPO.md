# 00 · BẢN ĐỒ REPO `agentnet-corner`

Repo này là **tầng chung** của đội quân Muse: Hub giao việc, cầu nối giao tiếp, xưởng dựng video, tài nguyên âm thanh/font. Mỗi kênh nội dung làm trên **nhánh riêng** và chỉ thêm thư mục `channels/<tên-kênh>/`.

## Cây nhánh

```text
main                    ← Torque (VPS) tự lưu STATUS.md mỗi 30 phút
└─ feat/core-shared     ← TÀI NGUYÊN DÙNG CHUNG (nhánh này)
   ├─ feat/phim-ma-dan-gian   → channels/phim-ma-dan-gian/
   └─ feat/tap-lam-content    → channels/tap-lam-content-k08/   (KENH_008 · Tập Làm Content)
```

Quy tắc: sửa công cụ dùng chung ở `feat/core-shared` → các nhánh kênh `git merge feat/core-shared` để nhận bản mới. Không sửa thư mục của kênh khác trên nhánh mình.

## Thư mục dùng chung

| Thư mục | Vai trò | Ghi chú |
| :--- | :--- | :--- |
| `core/vps_live/` | **Bản đang chạy thật trên VPS** `/opt/agentnet-corner` (v1.3-fleet): `corner.py`, `research_queue.py`, `hub_portal.py`, `ggmap_scout.py`, `join.py`, prompt, test | Chụp nguyên trạng ngày 25/11/2026, khớp SHA-256 với VPS. Deploy lấy từ đây. |
| Gốc repo (`corner.py`, `research_queue.py`, `test_*.py`) | Bản **V2.0 Auto-99%** (DAG pipeline, GPU→CPU fallback) | **Chưa deploy** lên VPS. |
| `bridges/` | Cầu nối giao tiếp Muse: bơm lệnh vào chat `muse.ai`, phòng họp Telegram, gửi file tạm, QC máy | Bản sao từ `D:\AI_AGENT\AI_SYSTEM\RAG`, đã bỏ secret. Xem `docs/KENH_GIAO_TIEP_MUSE.md`. |
| `auto99/` | Xưởng dựng: giọng đọc + Whisper tự sửa, ghép video, QC 100 điểm, worker PC, cổng duyệt Telegram | Giữ đường dẫn cũ vì code import `auto99.*`. |
| `stickman-shorts/` | Rig người que + **kho BGM/SFX `.ogg`** + font Be Vietnam Pro | Cần cài `manim` trên PC để render. |
| `video-pipeline/` | Tải và phân tích video mẫu | |
| `video_production/` | Kho 14 video thử `v001…v014` + 2 lượt so sánh giọng | Lịch sử, chỉ đọc. |
| `studio/` | **Danh mục công cụ local trên PC** (chọn giọng, ghép giọng, ghép video) | `studio/CONG_CU_LOCAL.md`, `studio/local_tools.json` |
| `assets/` | Danh mục tài nguyên dùng chung (font, nhạc, SFX, giọng mẫu, từ điển phát âm) | Chỉ manifest; media nặng ở Google Drive. |
| `docs/` | Nghiên cứu chung + tài liệu giao tiếp | |
| `channels/` | Chỗ các nhánh kênh đặt thư mục riêng | Trên nhánh này chỉ có README. |

## Luật bắt buộc

- **Không commit media** (`.mp4/.wav/.png/.jpg`), token, cookie, session Telegram, mã mời. Media → Google Drive.
- Muse **không được push GitHub**; chỉ nộp kết quả qua Hub. Chief/PC gộp code.
- Cách ly Tầng 1 Facebook (`L060`): không ghi vào `D:\0.1_FACE_BOOK`, chỉ đọc (vd. giọng mẫu OmniVoice).
- Chạy test trước khi push: xem `studio/CONG_CU_LOCAL.md` mục *Kiểm tra*.
