# HANDOFF — AgentNet Video Studio (tiếp nối công việc)

> Tài liệu này để một Muse khác (hoặc chính Torque sau này) đọc là tiếp tục được
> công việc, không cần hỏi lại chủ. Cập nhật file này mỗi khi trạng thái đổi.
> Cập nhật lần cuối: 15/11/2026 ~01:55 +07 (Asia/Bangkok).
> KHÔNG BAO GIỜ ghi token, mật khẩu, PAT hay khóa bí mật vào file này (repo công khai).

## 1. Nhiệm vụ

Chủ đang xây **Autonomous AI Video Studio** (kênh video ngắn faceless, không máy quay).
Tuần 1 chỉ làm RESEARCH (không viết kịch bản, không sản xuất). Tuần 2 mới viết
kịch bản và thử sản xuất khi có đủ công cụ/ngân sách.

- Video phải làm được **không cần máy quay**: faceless, AI tạo hình/giọng, stock
  footage, animation, text-based. Nội dung big-production (vd MrBeast) chỉ dùng làm
  tham chiếu hook/retention, KHÔNG làm mẫu sản xuất.
- Khung chuẩn: video dọc, **38–65 giây**, hook mạnh 3 giây đầu.
- Khung giờ đăng đã biết: **11:30 và 20:00** (từ video-audit cũ).
- Chủ đề tuần 1 phải FRESH, không liên quan kênh cũ.
- Chủ bận, đã ủy quyền cho Torque tự quyết trong phạm vi nhiệm vụ, nhưng KHÔNG
  bao gồm tự duyệt việc mình làm (xem mục 6).

## 2. Vai trò và hạ tầng

- Master/registry: `http://100.67.236.124:8110`, project=`research`, API V1.2.
  Source: `https://github.com/giakhanh299/agentnet-corner` (repo CÔNG KHAI).
- VPS này là **controller** (node `1a74385032d8652dc2e1b2ba`, registration APPROVED).
  Tailscale đã nối (IP VPS 100.89.246.91, master 100.67.236.124).
- **Registry chỉ đi qua tunnel proxy port 3130** (lấy host từ biến HTTPS_PROXY, đổi
  port 3128 → 3130). Egress proxy công khai KHÔNG tới được tailnet. SSH ra ngoài bị chặn.
- Worker nodes: Research `baa7de1f...` (chỉ web_search/browser/image_search/research/
  summarize — KHÔNG tải video, KHÔNG chạy code), Verify `355c4b87...` (chỉ verify).
  Engineer là controller này qua `as_role=engineer` (python/shell/ffmpeg/ffprobe/http/file).
- Broker cũ 8101 đã TẮT, không dùng. Không động vào dữ liệu Facebook cũ.
- `identity.json` (0600) giữ nguyên, không đăng ký lại node mới.
- `connection.json` (0600) có `application_token` và `additional_roles.engineer` —
  KHÔNG in/log giá trị token. Engineer đi qua `as_role=engineer`, không dùng token
  additional_roles trực tiếp.
- Repo git local: `~/workspace/agentnet-corner-github` (origin main). Thư mục làm
  việc: `~/workspace/agentnet-corner`. `gh` đã đăng nhập tài khoản giakhanh299
  (dùng `gh auth login --with-token`, token qua stdin, KHÔNG ghi vào file/URL/log).
  Push HTTPS qua `gh` làm credential helper.

## 3. Trạng thái hiện tại (15/11/2026 ~01:55)

### Hàng đợi nghiên cứu (API 8110)
- `ac56d158` research 100 ứng viên — SUBMITTED (outcome `completed`, KHÔNG duyệt
  được: server chỉ duyệt outcome `ok`/`PASS`, và không sửa được result đã nộp).
  Dữ liệu đã VERIFIED (task `a1d31407`, verified_with_findings) và đang dùng làm cơ sở.
  100 URL: 73 YouTube Shorts, 27 TikTok, 0 FB Reels. Ngách: humor 24, curiosity 17,
  surprise 15, entertainment 10, emotional storytelling 10, relatable 9,
  heartwarming 5, emotional 4, everyday life 4, emotional everyday-life 1,
  illogical creative 1. Chỉ 22 video biết độ dài; 58 biết kênh.
- `aa5f7d18` engineer pipeline phân tích video — APPROVED (outcome `ok`).
- `a1d31407` + `ef4e0b2c` verify — SUBMITTED, verified_with_findings.
- `5246f45f` research chọn 30 video phân tích sâu — **QUEUED, Research chưa nhận lại**
  (đã nhận 1 lần ~00:31 rồi hết lease 15 phút không nộp; Research online,
  last_seen 01:24, nhưng không claim lại). Đây là điểm tắc cần xử lý (mục 7).

### Tải video (VPS này, Engineer)
- Đợt 1 xong: **81/100 OK, 19 lỗi**. 81 file trong `video_downloads/candidates/`
  (439 MB). 19 lỗi: 18 YouTube "Sign in to confirm you're not a bot" + 1 TikTok
  "Your IP address is blocked". Log: `video_downloads/download_log.jsonl`.
- Đang chạy lại 19 lỗi: `retry_failed.py` (pid 5845, log `video_downloads/retry_run.log`)
  — thử lại theo thứ tự android → ios → tv_embedded, nghỉ giữa các lần.
  TikTok lỗi IP vẫn fail; sẽ xử lý bằng TikHub (mục 5).
- Test đã chứng minh: YouTube client mặc định bị chặn bot, `--extractor-args
  "youtube:player_client=android"` vượt được (format 18); TikTok tải được bằng
  yt-dlp thường sau vài lần thử.

### Phân tích video (VPS này, Engineer)
- Đang chạy: `batch_analyze.py` (pid 5934, log `video_analysis/batch_run.log`) —
  chạy `analyze_video.py` cho từng .mp4: ffprobe, keyframes theo scene, tách 30s
  audio mono 16kHz, ghi `timeline.md` + `summary.json` vào `video_analysis/<tên>/`,
  gom index vào `video_analysis/index.jsonl`.
- Chưa có ASR/OCR/OpenCV. Transcript: dùng Groq Whisper Large-v3-turbo miễn phí
  (tiếng Việt tốt nhất) hoặc Subtitle Edit/Whisper.cpp offline (xem docs Gemini).

### AI bên ngoài (Gemini + ChatGPT, qua browser)
- **Gemini** (GCM Cong ty, giakhanhgcm@gmail.com, Pro, mode Argon): đã trả lời 5 câu
  + 2 câu hỏi tiếp (kế hoạch 7 ngày + web tải video). Đã lưu đầy đủ:
  `docs/gemini-answers-20261115.md` và `docs/gemini-followup-20261115.md`
  (bản gốc trong `~/workspace/agentnet-corner/`).
  Điểm chính: Tò mò dễ làm + viral nhất (Visual Essay 42–50s); chọn 30 theo 4 lọc
  có trọng số (không-máy-quay 40%, độ dài 25%, hook 3s 20%, view vượt trội 15%),
  chia 23 Shorts/7 TikTok, 3 đợt; kế hoạch 7 ngày lọc → tải → transcript → đào
  sâu 3 wave → tổng hợp Production Framework, sang tuần 2 sáng ngày 8.
  Web tải: Cobalt (sạch nhất), SnapTik/TikWM (TikTok), FDown/SnapSave (Facebook),
  Publer. yt-dlp làm 90% (hàng loạt + metadata), web làm 10% (video lẻ, link bị chặn).
  Link Facebook /share/p/ là "opaque share link" — không web nào tự giải được;
  phải mở bằng trình duyệt đã đăng nhập FB, lấy link canonical (watch/?v=… hoặc
  reel/…) rồi mới tải được.
- **ChatGPT**: đã đăng nhập, đang trả lời 5 câu (task browser đang chạy, chủ cầm
  cửa sổ). Khi có kết quả: lưu câu trả lời + phương pháp vào VPS như đã làm với
  Gemini. Câu hỏi tiếp (làm gì tiếp + web tải video) CHƯA gửi được cho ChatGPT vì
  chủ đang cầm cửa sổ — gửi lại khi chủ trả quyền.
- **Facebook**: 4 link share → 3 bài duy nhất trên tài khoản gikhah.99 + 1 Reel
  1669933094108812. fsave.net lỗi cả 4 link share, chỉ tải được Reel (12,1 MB,
  720x1280, "Tâm sự người que", 2:21, stickman mindset). `facebook-cli` chưa nối.
  Task browser xem FB vẫn chờ đăng nhập Facebook. Đây là link công khai do chủ
  gửi để nghiên cứu, KHÔNG phải dữ liệu fanpage cũ.

### GitHub
- Commit `55f5a8a` "Add video pipeline..." đã push thành công lên main
  (video-pipeline/: README.md, analyze_video.py, download_candidates.py).
- Token PAT fine-grained ĐẦU TIÊN chỉ có quyền đọc (push 403, tạo blob 403) —
  đã thay bằng token mới có quyền ghi. `gh` đang đăng nhập.
- **Quy tắc mới (chủ dặn 01:52): đẩy git mỗi 30 phút; file nặng lên Google Drive,
  không đẩy lên git.** Cron `agentnet-git-autopush-30min` chạy script
  `~/workspace/agentnet-corner/auto_push.sh` (chỉ add các đường dẫn an toàn:
  video-pipeline/, docs/, HANDOFF.md, README — không bao giờ add file media,
  token, .env, credentials).

## 4. Cách làm (phương pháp đã kiểm chứng)

### Tải video
```bash
cd ~/workspace/agentnet-corner
./venv/bin/python3 download_candidates.py   # tải 100 ứng viên theo thứ tự ưu tiên
./venv/bin/python3 retry_failed.py          # thử lại các link lỗi (android→ios→tv)
# Lẻ: ./venv/bin/yt-dlp --extractor-args "youtube:player_client=android" -f 18 <url>
```
- yt-dlp 2026.10.26 nằm trong venv `~/workspace/agentnet-corner/venv` (system pip
  bị PEP 668 chặn). ffmpeg/ffprobe 8.1.2 hệ thống.
- Log JSONL ghi từng video (i, url, platform, niche, channel, ok, bytes).

### Phân tích video
```bash
python3 analyze_video.py <video.mp4> <out_dir>   # timeline.md + summary.json + frames + audio.wav
python3 batch_analyze.py                          # chạy hàng loạt cho candidates/
```
- Keyframes: ffprobe lavfi `select=gt(scene,0.4)`. Audio: 30s mono 16kHz.
- Hook 3s đầu đánh giá từ frame ở 0/1/2s (chưa có ASR nên không có transcript).

### Quy trình hàng đợi (V1.2)
- Chỉ Chief (controller) tạo task: POST /tasks với project=research,
  assigned_to research/verify/engineer, kind, dedup duy nhất, payload gồm
  objective/sources/acceptance_criteria/instruction (+ dữ liệu đính kèm).
- **Verify KHÔNG đọc được task khác** (GET /tasks chỉ Chief; GET /tasks/{id} 404
  với role verify) → task verification phải đính kèm toàn bộ tài liệu cần kiểm
  trong instruction.
- Approve chỉ chấp nhận outcome `ok` hoặc `PASS` → dặn worker nộp outcome `ok`.
- Lease 15 phút, heartbeat 60s. Result tối đa 256KB, không media/base64.
- Hết lease không nộp → task về QUEUED, worker khác nhận lại.
- Kiểm tra nhanh: `python3 queue_status.py` (bảng task + agent gọn).

### Chọn 30 video (đang làm)
- Lọc: không-máy-quay 40%, độ dài 38–65s 25%, hook 3s rõ 20%, view vượt trội 15%.
- Cơ cấu: Tò mò 8, Bất ngờ 7, Kể chuyện cảm xúc 5, Ấm áp+Cảm xúc 3, Hài 4,
  Đời thường+Đời sống 2, Giải trí 1 (23 Shorts / 7 TikTok).
- 3 đợt: Wave 1 giữ chân (15: 8 Tò mò + 7 Bất ngờ) → Wave 2 cảm xúc (8) →
  Wave 3 hài/đời thường (7). Mỗi video: xem thật, ghi hook 3s, cảnh/hành động,
  thoại, audio, nhịp, độ dài, format, bài học chuyển giao được.
- Sau khi Research nộp: đăng task verification kèm toàn bộ result trong instruction.

## 5. API tải video (chủ gửi 01:50)

File: `~/workspace/user/files/FB_API_tokens_20261115_014934.json`
(chỉ đường dẫn — KHÔNG ghi giá trị token vào đây hay bất kỳ đâu).
- `tiktok_download` (TikHub): `GET https://api.tikhub.io/api/v1/tiktok/app/v3/fetch_one_video?aweme_id=...`,
  header `Authorization: Bearer <token>`. Trả về play/download URL. Khoảng
  $0.001/call thành công. Dùng cho video TikTok bị yt-dlp chặn IP.
  Script: `tikhub_fetch.py` (đọc token từ file lúc chạy, không in token).
  Lỗi đang gặp: lần chạy đầu traceback ở urlopen — cần xem lỗi đầy đủ (có thể do
  proxy; API công khai đi qua egress proxy, KHÔNG qua tunnel 3130).
- `post_scraping` (Apify, 3 token): API `https://api.apify.com/v2`, kiểm tra bằng
  `GET /v2/users/me`. Actor Facebook posts: `apify/facebook-posts-scraper`
  (POST /v2/acts/<actor>/runs, input startUrls + resultsLimit; poll tới
  SUCCEEDED rồi lấy dataset items). Dùng cho 3 bài FB + Reel bị chặn. Chạy nhỏ
  (4–5 URL) để tiết kiệm quota; quota chưa kiểm chứng.

## 6. Quy tắc bắt buộc

- Không ghi Tailscale auth key, application_token, additional_roles hay PAT vào
  source, prompt, log, file git. Token chỉ đi qua stdin/header lúc chạy.
- Không tự duyệt việc controller tự làm với vai trò Engineer — phải qua Verify trước.
- Không tự nhận role Chief/vai trò trống, không tự nâng quyền, không bỏ qua bước duyệt.
- Không sửa hệ thống Facebook cũ, không tự đăng, không deploy production.
- Tuần 1 chỉ research, không viết kịch bản/sản xuất.
- Không khẳng định kết nối/kiểm tra/đăng ký thành công khi chưa kiểm chứng thật.
- Mọi con số báo cáo phải lấy từ tool output/file/log thật, không đoán.
- File nặng (video, audio, frames) KHÔNG đẩy lên git — lên Google Drive.
  Git chỉ chứa code + tài liệu text.

## 7. Việc tiếp theo (theo thứ tự)

1. Chờ `retry_failed.py` + `batch_analyze.py` chạy xong; kiểm tra log, đếm OK/FAIL.
2. Sửa lỗi TikHub (xem traceback đầy đủ) → tải video TikTok còn thiếu bằng TikHub.
3. Dùng Apify lấy 3 bài FB + Reel → tải video về `video_downloads/facebook/`,
   phân tích bằng `analyze_video.py` như video khác.
4. Xử lý task `5246f45f` đang QUEUED: nếu Research vẫn không nhận, làm phân tích
   30 video bằng Engineer (video đã tải + keyframes/audio/transcript) rồi đăng
   task engineer mới để nộp kết quả chọn 30, sau đó đăng task verification
   (kèm result trong instruction). Task research cũ cứ để QUEUED — nếu Research
   nộp sau thì có thêm góc nhìn đối chứng.
5. Khi có kết quả ChatGPT: lưu câu trả lời + phương pháp vào VPS (file
   `chatgpt-answers-20261115.md`), hỏi tiếp 2 câu (làm gì tiếp + web tải video).
6. Transcript cho 30 video đã chọn: Groq Whisper Large-v3-turbo (ưu tiên, miễn phí,
   tiếng Việt tốt nhất) hoặc Subtitle Edit offline.
7. Tổng hợp ngày 7: ngân hàng 30 công thức hook, khung kịch bản theo mốc 5 giây,
   3 template trống (Tò mò/Bất ngờ/Cảm xúc), thư mục Core_SFX. Sáng ngày 8 mới
   sang tuần 2 viết 7 kịch bản đầu.
8. Duy trì: cron đẩy git mỗi 30 phút; file nặng lên Google Drive (thư mục
   "AgentNet Video Studio"); cập nhật file HANDOFF này mỗi khi trạng thái đổi.
