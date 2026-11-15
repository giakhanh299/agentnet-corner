# STATUS — AgentNet Video Studio (per-feature result log)

> Log kết quả từng tính năng: xong (đúng hay sai) đều ghi vào đây, KHÔNG báo
> riêng cho chủ nữa (chủ dặn 15/11 ~15:50: "ko cần báo tôi — báo lên git hay
> gg driver"). Chủ không can thiệp; cứ bám theo kế hoạch mà làm.
> Mới nhất ở trên cùng. Mỗi mục: tên, thời gian (+07), trạng thái
> (DONE / FAILED / IN PROGRESS / BLOCKED), file/commit chứng minh, kết quả
> thật — thành công hay lỗi (kèm lỗi) đều ghi. Không ghi số không có bằng chứng.
> Bản trên git là bản chính; bản trên Drive là bản sao dự phòng.
> Cập nhật lần cuối: 2026-11-15 ~16:05 +07.

## IN PROGRESS

### PC Windows — test render stickman qua SSH — IN PROGRESS
- **Bắt đầu:** 2026-11-15 ~15:46 +07.
- **SSH đã kiểm chứng 15:33:** `w@100.101.158.71` (desktop-01o3hnf),
  Windows 11 Pro, 32.269 MB RAM — đăng nhập được, chạy lệnh được.
- **Còn làm:** clone repo về `C:\Users\w\agentnet-corner`, cài Python 3.12 +
  ffmpeg + git (winget nếu thiếu), venv + Manim, cài font Be Vietnam Pro,
  render demo 5s, đo thời gian, copy frame về xem.

## DONE

### Ep001 — tập stickman thật đầu tiên (F7, 50s) — DONE 2026-11-15 16:02 +07
- **File:** `stickman-shorts/videos/2026-11-15_ep001-cam-dau-lam-viec/output/final.mp4`
  — 48,8s, 1080x1920 30fps, H.264 + AAC 192k, 3,2 MB, sha256 `3f40bf21a0616d30baaa…`
  (Torque kiểm chứng: ffprobe + sha khớp; xem frame 1s và 36s: hook
  "CÙNG LÀM 10 TIẾNG" rõ, dấu đúng; 2 nhân vật An/Bình + túi tiền rõ, không
  đè chân; phụ đề rõ, đúng vị trí).
- **Chủ đề:** "Cùng làm 10 tiếng, sao người giàu, người nghèo?" — kịch bản
  gốc 137 từ (F7), hook kép 0–3s → An đổi giờ lấy tiền → Bình xây cây cầu
  → một năm sau → payoff "Giàu không phải làm nhiều hơn. Giàu là làm khác
  đi." Bài học cảm hứng từ FB-05, không sao chép câu chữ/cảnh nào.
- **Đã đo:** -17,40 LUFS (thấp hơn mục tiêu 1,4 — chưa sửa), true peak
  -2,91 dBTP, giọng bắt đầu 0,105s, 174 từ/phút (trên vùng an toàn 150–165).
  Phụ đề 16 events, khớp kịch bản 137/137 từ; 7 frame đã xem (`qc.md`).
- **Giọng MMS-TTS** (đúng pipeline v001): từng beat riêng, ngắt 0,3/0,4/0,4/0,7s.
  Piper tự kiểm: 275 từ/phút — loại; Edge TTS file 0 byte — khớp v001.
  Caption sửa theo kịch bản gốc (timestamp Whisper giữ nguyên).
- **Đường `--srt` của assemble.py ĐÃ TEST + SỬA XONG:** `tools/assemble.py`
  tự convert .srt → .ass (PlayRes 1080x1920, Be Vietnam Pro 56) + filter
  `ass` + `alimiter=limit=0.7:level=false`; 2 bài học ghi vào docstring.
- **Lỗi hình đã sửa:** POSE_SURPRISED 2 tay chồng thành 1 tay + chân/thân
  thành 1 cột → sửa pose-only (SPEC không đụng), rig test chạy lại ALL
  PASSED; túi tiền đè chân Bình → dời x 2,2 → 3,2.
- **Giới hạn thật:** không nhạc nền (thư viện nhạc/SFX vẫn trống — điểm yếu
  lớn nhất); chưa ai nghe giọng bằng tai; tốc độ 174 từ/phút hơi nhanh;
  beat 2 có ~4s tư thế suy nghĩ tĩnh hơi dài; ảnh tĩnh giữa nhịp đi bộ
  đôi khi gượng.
- **Chưa đăng/upload đâu cả.** Thời gian: ~75 phút.

### Video #1 — Visual Essay 45s (F2) — DONE 2026-11-15 15:57 +07
- **File:** `video_production/v001-visual-essay-45s/v001.mp4` — 47,1s,
  1080x1920 30fps, H.264 + AAC 192k, 12,6 MB, sha256 `e65285dd625caccc…`
  (Torque kiểm chứng: ffprobe + sha khớp báo cáo; xem frame 1s và 24s:
  hook "Bạn có biết cửa sổ máy bay tròn không phải để đẹp?" rõ, dấu đúng;
  phụ đề rõ, đúng vị trí).
- **Chủ đề:** "Vì sao cửa sổ máy bay lại tròn?" — 126 từ, tiếng Việt,
  hook kép (chữ + lời hỏi cùng 1 câu trong 3s đầu) → lịch sử Comet →
  toán ứng suất Inglis/Kirsch → payoff + CTA. Nguồn đã kiểm chứng
  (FAA Comet, Kirsch 1898 ×3, Inglis 1913 tới ×21, số chu kỳ bay
  G-ALYP 1.290 / G-ALYY 900 / G-ALYU 3.060).
- **Đã đo:** -16,74 LUFS, true peak -3,05 dBTP, giọng bắt đầu ~0,05s,
  160 từ/phút — đều trong chuẩn. 9 frame QC đã xem (`qc.md`).
- **Giọng đọc MMS-TTS** (`facebook/mms-tts-vie`, local, miễn phí) — đọc
  từng câu + ngắt 0,9s; Whisper kiểm 70% khớp từ, từ khóa nghe rõ.
  Edge TTS bị proxy chặn (WebSocket), gTTS 429, Piper phá dấu tiếng Việt
  ("góc nhọn"→"khóc ngọt") — không dùng được. **MMS-TTS là pipeline
  chuẩn cho các video sau** (mẫu `gen_voice.py` / `synth_sentences.py`).
- **Lỗi đã sửa:** phụ đề SRT bị phóng 6,67× (PlayRes 384x288) → chuyển
  sang ASS (PlayRes 1080x1920); true peak +0,24 dBTP sau AAC → sửa bằng
  `alimiter=limit=0.7:level=false` (level=true là auto-gain, KHÔNG phải
  true-peak — đã tăng nhầm loudness lên -13,16 LUFS ở 1 build).
- **Giới hạn thật:** chưa ai nghe giọng bằng tai (chỉ Whisper kiểm —
  Whisper yếu tiếng Việt, ~30% nghe nhầm âm gần giống); chưa có nhạc nền
  (chưa có thư viện nhạc có bản quyền); ảnh img3 hơi mềm (nguồn 960px
  upscale ~2×). Chủ nên nghe 1 lần trước khi đăng.
- **Chưa đăng/upload đâu cả.** Thời gian: ~65 phút (3 lần build).

### Hệ thống liên tục / thay thế VPS (STATUS + HANDOFF) — DONE 2026-11-15 15:54 +07
- **Commit:** `4fe66f4` (3 file) — `STATUS.md` (file này), `HANDOFF.md` §10
  "Takeover" (10 bước cho VPS/Muse mới tiếp quản) + §11 "Infrastructure —
  tất cả các VPS" (VPS 0/1/2/3/4, node Research `baa7de1f`, Verify
  `355c4b87`, tailnet peers, thư mục Drive), `scripts/auto_push.sh`
  (bản sao của auto_push.sh để VPS mới khôi phục cron).
- **Đã kiểm chứng thật:** `STATUS.md` + `HANDOFF.md` đã lên Drive
  (id ở cuối file, kiểm tra bằng `drive files list`); `auto_push.sh` đã
  thêm `STATUS.md` vào danh sách git-add (grep đã kiểm chứng ở cả 2 bản).
- **Quy tắc mới (chủ dặn ~15:50):** kết quả từng tính năng ghi vào
  STATUS.md này (git là bản chính, Drive là bản sao) — KHÔNG báo riêng
  cho chủ nữa. Chủ không can thiệp; cứ bám kế hoạch mà làm.
- **Còn thiếu (xem mục "Rủi ro takeover" cuối file):** `identity.json` /
  `connection.json`, `.env` gateway và khóa SSH `~/.ssh/pc_torque` chưa
  có bản sao lưu nào — cần quyết định của chủ trước khi sao lưu bí mật
  lên Drive; cron chỉ sống trong runtime, chưa có script tái tạo tự động.

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

## Rủi ro takeover (VPS mới chưa tiếp quản trọn vẹn được)

- `identity.json` / `connection.json` (khóa node AgentNet) KHÔNG có bản
  sao lưu nào (cố ý — bí mật, không lên git). Nếu VM bị thay và
  `~/.agentnet-corner/` mất, VPS mới không đăng ký lại được cùng node
  nếu không có chủ. Sao lưu lên Drive được (chủ đã lưu key thử nghiệm lên
  Drive) nhưng CẦN chủ quyết trước — chưa tự làm.
- `.env` của gateway cũng chưa có bản sao lưu (lý do như trên;
  `.env.example` đã có trên git, key thật thì không).
- Khóa riêng SSH `~/.ssh/pc_torque` chưa sao lưu — VPS mới phải tạo cặp
  khóa mới và chủ phải thêm public key mới vào
  `administrators_authorized_keys` trên PC.
- Cron sống trong runtime, không có trên git — HANDOFF §10 có hướng dẫn
  tạo lại cả 3 cron bằng tay, chưa có script tự tạo.
- VPS 0/2/3/4 vẫn không tới được, IP chưa biết — đã ghi là chưa biết kèm
  cách phát hiện (`tailscale status`, registry `/nodes`), không bịa.
- HANDOFF.md §3 còn vài dòng cũ bên dưới ghi chú sửa (vd "Commit hiện tại
  2060ecf") — ghi chú ở đầu §3 đã đính chính, nhưng viết lại toàn §3 vẫn
  đang chờ.

---

## Bản sao trên Google Drive

- Thư mục: "AgentNet Video Studio"
  (https://drive.google.com/drive/folders/1q0gL8euNge458b_ktbGSg_RMfiz3FcC8)
- `STATUS.md` (bản này) — Drive file id: `1lAPg14W9pW43zq6aQCyWEIahxgbI6MKc`
  (upload 2026-11-15 ~16:06 +07 — bản mới nhất, có Ep001 DONE; bản cũ
  `1gpLAunMiYnQhwknN-QNgmFlBYfrOUXCj` (15:55) đã lỗi thời, giữ lại làm
  bản sao cũ, không xóa theo quy tắc không xóa dữ liệu Drive)
- `HANDOFF.md` — Drive file id: `16lcqICKbi8ZvurA-T4O4_eXhe6ZoKaZ7`
  (upload 2026-11-15 ~15:55 +07)
- Video thành phẩm (bản sao dự phòng, không lên git):
  - `v001.mp4` (Video #1) — Drive file id: `1oVxOPRVSl5HmjdzI47RQiVGKHotAdCxn`
  - `ep001-cam-dau-lam-viec.mp4` (Ep001) — Drive file id: `152--2bfxwsQIjKi_5bCmKbO3V8jsdu9f`
- Lưu ý: bản trên git là bản chính, mới nhất.
