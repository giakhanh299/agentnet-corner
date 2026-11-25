# KENH_008 · Tập Làm Content — `channels/tap-lam-content-k08/`

Nhánh `feat/tap-lam-content`. Kênh Facebook KENH_008 (thư mục cũ `KENH_008_ChiDepDiCau`, đã đổi tên kênh thành **Tập Làm Content**). Lab thử format video ngắn kiến thức 9:16, mục tiêu 2–3 video/ngày.

## Luồng sản xuất

```text
Muse (Hub) viết kịch bản  →  PC dựng: auto99 (giọng + Whisper + ghép + QC)
   →  sync_agentnet_to_kenh008.py chép MP4 + caption vào
      D:\0.1_FACE_BOOK\videos_upload\KENH_008_ChiDepDiCau\02_MOI_RENDER_CHO_XAC_NHAN\
   →  chủ dự án duyệt 1 chạm qua Telegram  →  tool FB đăng theo lịch (11:20 / 17:25 / 20:25)
```

> Bước chép vào thư mục FB là **ghi vào Tầng 1**: chỉ chạy khi video đã QC và chủ dự án đồng ý. Không tự đăng (`L012/L056`).

## File trong thư mục này

| File | Việc |
| :--- | :--- |
| `sync_agentnet_to_kenh008.py` | Kiểm tra MP4 1080×1920 có tiếng, đặt tên theo tiêu đề, viết `.caption.txt` (hook + câu hỏi + hashtag `#TapLamConTent`), chống chép trùng bằng SHA-256 |
| `agentnet_kenh008_sync_manifest.json` | Bản chụp sổ đã đồng bộ: `v006, v007, v009, v010, v011, v012` |

Bản chạy thật vẫn ở `D:\AI_AGENT\sync_agentnet_to_kenh008.py` và ghi sổ vào `D:\AI_AGENT\agentnet_kenh008_sync_manifest.json`; thư mục này là bản có phiên bản.

## Dùng chung (không chép lại)

- Kịch bản/phụ đề các tập đã làm: `video_production/v001…v014`
- Giọng, ghép video, QC: `auto99/`, `studio/CONG_CU_LOCAL.md`
- Nhạc/SFX/font: `assets/README.md`
- Giao việc cho Muse: `docs/KENH_GIAO_TIEP_MUSE.md`
