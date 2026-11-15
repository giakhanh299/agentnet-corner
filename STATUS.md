# STATUS — AgentNet Video Studio (per-feature result log)

> Log kết quả từng tính năng: xong (đúng hay sai) đều ghi vào đây, KHÔNG báo
> riêng cho chủ nữa (chủ dặn 15/11 ~15:50: "ko cần báo tôi — báo lên git hay
> gg driver"). Chủ không can thiệp; cứ bám theo kế hoạch mà làm.
> Mới nhất ở trên cùng. Mỗi mục: tên, thời gian (+07), trạng thái
> (DONE / FAILED / IN PROGRESS / BLOCKED), file/commit chứng minh, kết quả
> thật — thành công hay lỗi (kèm lỗi) đều ghi. Không ghi số không có bằng chứng.
> Bản trên git là bản chính; bản trên Drive là bản sao dự phòng.
> Cập nhật lần cuối: 2026-11-15 ~15:55 +07.

## IN PROGRESS

### Video #1 — Visual Essay 45s (F2) — IN PROGRESS
- **Bắt đầu:** 2026-11-15 14:53 +07 (chủ duyệt "Làm video đầu tiên ngay").
  Vẫn đang chạy lúc 15:50 (subagent hoạt động, không kẹt).
- **Thư mục:** `video_production/v001-visual-essay-45s/` — đã có `v001.mp4`,
  `voice.wav`, `captions.srt` trên đĩa (thấy lúc 15:50), nhưng báo cáo cuối
  của subagent + kiểm tra QC (ffprobe, loudness, xem frame) CHƯA có — KHÔNG
  được coi là DONE.
- **Ghi chú:** TTS đang thử nhiều hướng (gtts lỗi, đã tải model từ Hugging Face).
  Chưa đăng/upload đâu cả.

### Ep001 — tập stickman thật đầu tiên (F7, 50s) — IN PROGRESS
- **Bắt đầu:** 2026-11-15 ~15:46 +07. Thư mục
  `stickman-shorts/videos/2026-11-15_ep001-cam-dau-lam-viec/` đã tạo.
- **Nội dung:** kịch bản gốc (không copy FB-05) theo bài học FB-05
  "cắm đầu làm việc không giúp bạn giàu lên", ~125–138 từ, giọng Edge TTS
  hoặc TTS đang dùng ở v001, render Manim + assemble có `--srt` (đường này
  chưa từng thử), QC đầy đủ trước khi báo.

### PC Windows — test render stickman qua SSH — IN PROGRESS
- **Bắt đầu:** 2026-11-15 ~15:46 +07.
- **SSH đã kiểm chứng 15:33:** `w@100.101.158.71` (desktop-01o3hnf),
  Windows 11 Pro, 32.269 MB RAM — đăng nhập được, chạy lệnh được.
- **Còn làm:** clone repo về `C:\Users\w\agentnet-corner`, cài Python 3.12 +
  ffmpeg + git (winget nếu thiếu), venv + Manim, cài font Be Vietnam Pro,
  render demo 5s, đo thời gian, copy frame về xem.

## DONE

### Stickman repo (Manim) — DONE 2026-11-15 15:45 +07
- **Commit:** `58b70a2` (30 file) — `stickman-shorts/`.
  Manim 0.22.1, venv riêng; config.py SPEC đóng băng (HEAD_R=0.6);
  `src/rig/character.py` là class Stickman thật (set_pose/walk/wave/place),
  không còn `pass` placeholder (grep đã kiểm chứng); poses/walk/gestures/
  expressions (6 mặt)/props; scenes text_card; utils text NFC+wrap;
  tools render.sh/render.bat/render_all.sh/assemble.py (loudnorm -16 LUFS);
  docs STYLE_GUIDE + WORKFLOW; tests/test_rig.py.
- **Đã kiểm chứng thật:** demo render 17,2s lạnh / 8,6s ấm (thấp hơn nhiều
  so với ChatGPT ước 5–10 phút); ffprobe: h264 1080x1920 30fps đúng 5.000s,
  186.679 bytes (`media/videos/stickman_demo/1920p30/StickmanScene.mp4`);
  rig smoke test 11/11 PASS; frame 1s đi bộ đúng dáng, frame 4s bảng
  "TÂM SỰ NGƯỜI QUE" dấu đầy đủ, người que cười vẫy tay.
- **Lỗi đã tìm + sửa:** tư thế vẫy đầu tiên để khuỷu tay nằm trong vòng đầu
  nên cánh tay bị che — đã sửa góc vai, render lại, xem lại frame.
- **Báo cáo:** `stickman-shorts/test-report.md`.
- **Còn thiếu:** chưa có tập thật nào (`videos/` trống ngoài Ep001 đang làm);
  assemble `--srt` chưa thử; đường Windows chưa thử; `render_all.sh` chưa
  thử; chưa có thư viện nhạc/SFX.

### Gateway auto-start — DONE 2026-11-15 12:45 +07
- **Giao:** systemd unit `/etc/systemd/system/media-gateway.service`
  (Type=forking, PIDFile `data/gateway.pid`, Restart=on-failure, enabled)
  + watchdog `media_gateway/scripts/watchdog.sh` + cron
  `media-gateway-watchdog-10min` (mỗi 10 phút, kiểm tra `/health`, restart
  qua `deploy.sh` chỉ khi down; im lặng khi khỏe).
- **Đã kiểm chứng thật:** VPS reboot ~12:50 và ~14:50 — watchdog tự
  tái tạo unit file bị `/etc` xóa + restart gateway (pid 1833, rồi 9018),
  `/health` ok. Lần kiểm tra cuối của parent: 14:54 (không kiểm tra lại
  trong lần ghi này — xem HANDOFF §10 để biết cách kiểm tra lại).
- **Ghi chú:** file unit trong `/etc` mất mỗi lần VM bị thay — watchdog
  (nằm trong home) là lớp bền vững, tự tạo lại unit.

### SRT cho 30 video — DONE 2026-11-15 15:01 +07
- 30/30 file `transcript.srt` cạnh `transcript.txt` trong
  `video_analysis/<thư mục>/` (map `srt_map.json`, log `srt_run.log`).
  25 dùng được (lời nói thật, timestamp bắt đầu 00:00:00,000, 0 đoạn
  không đơn điệu); 4 rác do Whisper Base lỗi tiếng Hindi (H05, H08, C03,
  D02) — cần model khác/người kiểm trước khi dùng làm phụ đề; 1 rỗng D03
  (video chỉ có nhạc). `transcript.txt` không bị ghi đè.

### Production Framework — DONE 2026-11-15 14:41 +07
- `production-framework-20261115.md` (615 dòng) + bản copy trong `docs/`,
  commit `3fb06dc`. 8 công thức (F1 hook kép, F2 Visual Essay, F3 countdown,
  F4 một hình phi lý, F5 X vs Y, F6 quá trình biến đổi, F7 truyện stickman,
  F8 nhãn "POV:"), 3 format ưu tiên, 3 template trống, 18 SFX, checklist
  hook/title/thumbnail/audio. Cổng tuần 2: ChatGPT 5/5 đạt; Gemini 2/3
  (tốc độ lời 140–160 từ/48s của Gemini nhanh hơn vùng an toàn 150–165 wpm
  đã kiểm chứng → chuẩn dùng 120–132 từ/48s).

### Phân tích sâu 30/30 video — DONE 2026-11-15 12:30 +07
- `deep-analysis-5x85-20261115.md` (481 dòng) + `deep-analysis-25-20261115.md`
  (1.983 dòng), commit `99ca657` / `503655a`. 23 giữ nguyên, 2 sửa:
  H06 #23 59→54, B06 #24 49→54 — tổng không đổi (2082, trung bình 69,4;
  4 video đạt 85+: #77 90, #81 87, #50 85, FB-05 85). #50 có watermark
  "© 2026 Christopher Thomas. All Rights Reserved." — bản làm lại phải
  vẽ hoàn toàn mới. 15/25 video dùng lại clip/audio/ảnh của người khác —
  bản làm lại phải dùng tài sản của mình.

### Transcription toàn bộ — DONE 2026-11-15 10:05:54 +07
- 96/96 transcript, 0 FAIL (`transcribe_all.sh`, Whisper.cpp Base).
  Ngôn ngữ: en 60, hi 15, es 5, ta 2, ml 2, id 2, bn 2, zh 1, vi 1 (FB-05),
  ur 1 (#77), th 1, te 1, sv 1, ko 1, fr 1. Giới hạn: audio chỉ 30s đầu;
  Whisper Base lỗi tiếng Hindi (4/5 transcript Hindi rác).

### Media Gateway (nền tảng) — DONE 2026-11-15 10:42 +07
- `media_gateway/` — FastAPI + SQLite, đủ 17 endpoint `/api/v1`,
  license engine (§10), 11 provider adapter, cache dedup SHA-256,
  timeline engine, module render FFmpeg, dashboard, SDK Python,
  HANDOVER.md. Test §21: 23 PASS / 0 FAIL / 2 SKIPPED (case 13 Worker
  Tailscale, case 25 redeploy VPS 0 — không có quyền truy cập từ đây).
  Chạy keyless (Openverse, Wikimedia, Mixkit, Imgflip) — chưa có key
  provider nào. Drive `AI_MEDIA_GATEWAY/` + 21 thư mục con đã tạo.

### FB-05 đưa vào 30 video — DONE 2026-11-15 09:34 +07
- Quyết định của chủ ("Duyệt + FB-05 thay #32"): FB-05 (85) vào 30 với mã
  C04, #32 (67) xuống dự bị R4. Trung bình mới 69,67; 5 video đạt 85+.
  Commit `2060ecf`. Task engineer `b4413e82` + verify `ce4f147d`
  (xem mục BLOCKED bên dưới — đang chờ chủ duyệt).

### Chọn 30 video FINALIZED (95/100) — DONE 2026-11-15 08:30 +07
- #77 (26,22s) 90 điểm — #1 mới; #82 (175,54s) 78 điểm — vào T05;
  #37 (7,97s) 40 điểm — LOẠI (quay người thật, vi phạm lọc không-máy-quay).
  Commit `df75479`. File `selection-30-20261115.md` + `.csv`.

## FAILED

### Đăng ký API key provider cho gateway — FAILED (task chết) ~2026-11-15 12:18 +07
- **Nhiệm vụ:** đăng ký key miễn phí Pexels, Pixabay, GIPHY, Tenor,
  Freesound, Unsplash bằng tài khoản Google của chủ (giakhanhgcm@gmail.com).
- **Lỗi:** browser task `a6f34055` chết (errored) sau ~2 giờ chờ thẻ đăng nhập
  Google của Pixabay mà chủ không hoàn thành; cửa sổ đóng. **KHÔNG có key
  nào được giao — không xác nhận được key nào đã lấy.** `.env` vẫn trống
  cả 6 key provider (kiểm tra 11:33).
- **Còn lại:** đăng nhập Google cho Pexels đã xong 10:17; cookie trình duyệt
  còn pexels.com + pixabay.com nên khởi động lại sẽ nhanh hơn. Khởi động lại
  cần chủ bấm (widget đã đưa 12:19, chủ chưa bấm) và chủ phải hoàn thành thẻ
  đăng nhập Pixabay khi hiện. Không khởi động lại khi chưa có chủ.
- **Gateway vẫn chạy keyless** bằng nguồn miễn phí trong lúc chờ.

## BLOCKED

### Duyệt task engineer b4413e82 — BLOCKED (chờ chủ) — từ 2026-11-15 09:35 +07
- `b4413e82` SUBMITTED, outcome `ok` (bản chọn 30 có FB-05). Verify
  `ce4f147d` SUBMITTED, outcome `verified_with_findings` — kiểm tra lần cuối
  12:19: 30+10 đúng, phân bổ 8/7/6/5/4, tổng 2090, trung bình 69,67,
  đúng 5 video đạt 85+, file GitHub khớp. **Chờ chủ duyệt — không tự duyệt
  việc Engineer làm.** KHÔNG duyệt `f07e0ce6` / `86debefd` (đã bị thay thế).
- Lưu ý: điểm đã sửa trong phân tích sâu (trung bình 69,4; 4 video 85+) nằm
  trong báo cáo phân tích sâu, chờ lần kiểm chứng sau — không chặn duyệt này.

### Apify scrape 4 bài Facebook — BLOCKED — từ 2026-11-15 ~02:26 +07
- **Lỗi:** cả 3 token Apify đều timeout khi gọi có xác thực từ VPS này
  (30s và 120s, urllib thường và qua egress proxy), trong khi curl KHÔNG
  xác thực tới được api.apify.com (401 trong 0,7s). Nguyên nhân chưa rõ —
  không thử lại mù. 4 bài share FB vẫn chưa đọc được.
- **Đường còn lại:** chủ nối Facebook
  (https://agent.meta.ai/foa_ac_link/facebook) hoặc gửi link video trực
  tiếp (reel/ hoặc watch/?v=).

### 4 bài Facebook share — BLOCKED (chờ chủ) — từ 2026-11-15 00:21 +07
- 4 link share → 3 bài duy nhất trên tài khoản gikhah.99 (2 link trùng 1 bài).
  `browser.open` không đọc được bài Facebook; `facebook-cli` chưa nối
  (`facebook-cli me` trả `{}`). Cần chủ nối Facebook hoặc gửi URL video
  trực tiếp. Đây là link công khai do chủ gửi để nghiên cứu, KHÔNG phải
  dữ liệu fanpage cũ.

---

## Bản sao trên Google Drive

- Thư mục: "AgentNet Video Studio"
  (https://drive.google.com/drive/folders/1q0gL8euNge458b_ktbGSg_RMfiz3FcC8)
- `STATUS.md` (bản này) — Drive file id: `1gpLAunMiYnQhwknN-QNgmFlBYfrOUXCj`
  (upload 2026-11-15 ~15:55 +07)
- `HANDOFF.md` — Drive file id: `16lcqICKbi8ZvurA-T4O4_eXhe6ZoKaZ7`
  (upload 2026-11-15 ~15:55 +07)
- Lưu ý: bản Drive của STATUS.md được upload trước khi thêm dòng ghi id này;
  bản trên git là bản chính, mới nhất.
