# HANDOFF — AgentNet Video Studio (tiếp nối công việc)

> Tài liệu này để một Muse khác (hoặc chính Torque sau này) đọc là tiếp tục được
> công việc, không cần hỏi lại chủ. Cập nhật file này mỗi khi trạng thái đổi.
> Đối chiếu tiến độ ngày 15/11/2026 theo các báo cáo đã lưu trên GitHub.
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

## 3. Trạng thái ghi nhận ngày 15/11/2026

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
- `5246f45f` research chọn 30 video phân tích sâu — SUBMITTED, outcome `BLOCKED`
  (yt-dlp 403, lease 15 phút không đủ xem 30 video, 0 video được xem). Đừng duyệt.
- **Chọn 30 video (FINALIZED, 95/100):** engineer `f07e0ce6` SUBMITTED (ok) và
  verify `f364bd47` SUBMITTED (verified_with_findings, 6/6 điểm kiểm tra PASS) —
  nhưng cả hai đều **ĐÃ BỊ THAY THẾ**, không duyệt nữa (xem bên dưới).
- **FB-05 ĐƯỢC ĐƯA VÀO 30 (quyết định của chủ 15/11 ~09:34, "Duyệt + FB-05 thay
  #32"):** FB-05 (85 điểm, stickman mindset, hook đã xác minh từ frame thật) vào
  30 với mã C04, thay #32 (67 điểm, xuống dự bị R4). Điểm trung bình mới 69,67;
  5 video đạt 85+ (#77 90, #50 89, #81 87, #80 87, FB-05 85). Dự bị mới:
  R1 #42, R2 #65, R3 #79, R4 #32, R5 #76, R6 #71, R7 #85, R8 #29, R9 #57,
  R10 #60. File: `docs/selection-30-20261115.md` + `.csv` (commit 2060ecf).
  Brief kiểm chứng: `docs/verify-f364bd47-brief-20261115.md`.
- **Task chờ chủ duyệt theo báo cáo 12:19:** engineer `b4413e82` đã SUBMITTED
  (outcome `ok`, bản có FB-05). Verify `ce4f147d` đã SUBMITTED
  (`verified_with_findings`). [Biên bản Verify](docs/verify-ce4f147d-brief-20261115.md).
  Hai task `f07e0ce6` và `86debefd` đã được thay thế.
  **Không tự duyệt công việc do controller làm Engineer** — phải qua Verify trước.

### Tải video (VPS này, Engineer)
- Đã xong: **95/100 video đã tải + phân tích** (92 .mp4 + 3 .webm chuyển sang .mp4
  bằng ffmpeg: #37, #77, #82). Chỉ 5 video chưa bao giờ tải được: #6, #21, #38,
  #75 (TikTok @zakszalai, IP bị chặn; TikHub cũng trả về rỗng), #94.
  File trong `video_downloads/candidates/` (không đẩy lên git, đã lên Drive).
- Test đã chứng minh: YouTube client mặc định bị chặn bot, `--extractor-args
  "youtube:player_client=android"` vượt được (format 18); TikTok tải được bằng
  yt-dlp thường sau vài lần thử.

### Phân tích video (VPS này, Engineer)
- Đã xong: **95/100 video đã phân tích** vào `video_analysis/<tên>/` (summary.json
  + timeline.md + keyframes + 30s audio.wav; FB-05 có thư mục riêng, tổng 96 thư mục).
  Index: `video_analysis/index.jsonl`.
- **Whisper.cpp ĐÃ CÀI (15/11 ~09:02):** `whisper.cpp/build/bin/whisper-cli`,
  model ggml-base.bin (141 MiB) — chạy ~1x real-time, `-l auto` tự nhận ngôn ngữ
  (đã test #77: tiếng Urdu, khớp frame). Model Tiny tệ hơn, chỉ dùng dự phòng.
- **Transcribe xong 96/96 lúc 10:05:54** theo [bảng hook](docs/deep-analysis-hook-sheet-20261115.md).
  Transcript chỉ bao phủ 30 giây đầu. Hook nói của H05, H08, C03 và D02 vẫn
  chưa xác định do lỗi nhận dạng tiếng Hindi.
- **Đã lưu 30/30 bản phân tích sâu**, gồm [5 video ưu tiên](docs/deep-analysis-5x85-20261115.md)
  và [25 video còn lại](docs/deep-analysis-25-20261115.md). Tổng điểm chấm lại
  là 2.082, trung bình 69,40, có 4 video đạt 85+. Xem giới hạn bằng chứng và
  bộ 8 công thức, 3 format ưu tiên, 3 template trong
  [Production Framework](docs/production-framework-20261115.md).

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
- **ChatGPT** (Plus): đã trả lời 5 câu + câu hỏi tiếp (kế hoạch 2 tuần + web tải
  video). Đã lưu: `docs/chatgpt-answers-20261115.md` và
  `docs/chatgpt-followup-20261115.md`. Kế hoạch 2 tuần: tuần 1 (16–22/11) chuẩn hoá
  100 → chọn 30 + 10 dự bị → tải → phân tích sâu 6 lớp/video 19–21/11 → tổng hợp
  5–8 công thức 22/11; tuần 2 (23–29/11) viết 5 kịch bản 23/11 → làm thử 5 video
  25–26/11 → đăng thử 27–29/11 lúc 11:30/20:00. **Sora ĐÃ NGỪNG** (web/app
  26/4/2026, API 24/9/2026) — không dùng Sora; tạo video bằng Google Flow/Veo,
  Kling, hoặc Wan 2.2 local trên máy chủ (RTX 5060 Ti 16GB).
- **Facebook**: 4 link share → 3 bài duy nhất trên tài khoản gikhah.99 + 1 Reel
  1669933094108812 (FB-05, đã tải + phân tích, giờ là C04 trong 30).
  `facebook-cli` chưa nối; Apify bị chặn từ VPS (3 token đều timeout khi gọi có
  xác thực). 4 bài share vẫn chưa đọc được — chờ chủ nối Facebook hoặc gửi link
  video trực tiếp (reel/ hoặc watch/?v=). Đây là link công khai do chủ gửi để
  nghiên cứu, KHÔNG phải dữ liệu fanpage cũ.

### GitHub
- Bản chọn 30 có FB-05 ở `2060ecf`. Các mốc sau đó gồm báo cáo Verify
  (`4010e01`), phân tích 25 video còn lại (`503655a`), Production Framework
  (`3fb06dc`) và hai đề xuất stickman (`4017985`, `6898781`).
- Token PAT fine-grained ĐẦU TIÊN chỉ có quyền đọc (push 403, tạo blob 403) —
  đã thay bằng token mới có quyền ghi. `gh` đang đăng nhập.
- **Quy tắc mới (chủ dặn 01:52): đẩy git mỗi 30 phút; file nặng lên Google Drive,
  không đẩy lên git.** Cron `agentnet-git-autopush-30min` chạy script
  `~/workspace/agentnet-corner/auto_push.sh` (chỉ add các đường dẫn an toàn:
  video-pipeline/, docs/, HANDOFF.md, README — không bao giờ add file media,
  token, .env, credentials).
- **Rig stickman:** starter [Manim + FFmpeg](stickman-shorts/README.md) đã vào
  `main` ở `58b70a2`. [Báo cáo thử trên VPS](stickman-shorts/test-report.md)
  ghi nhận 11/11 kiểm tra rig đạt và demo 5 giây 1080×1920, 30 fps, có thẻ
  chữ tiếng Việt. Xem thêm [bản kiểm kê công cụ](docs/codexreply.md).

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
- Transcript (ASR): **Whisper.cpp đã cài** — model Base, chạy ~1x real-time:
  `cd whisper.cpp && ./build/bin/whisper-cli -m models/ggml-base.bin -f <audio.wav> -l auto --output-txt --output-file <out>`. Chạy hàng loạt: `transcribe_all.sh` (log `transcribe_all.log`). Ghi lại ngôn ngữ nói của từng video (transcript sẽ cho biết).
- Hook 3s đầu đánh giá từ frame ở 0/1/2s + transcript (lời nói) + audio.

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

1. **Chốt bản chọn:** chủ duyệt `b4413e82` trên queue sau khi xem [biên bản Verify](docs/verify-ce4f147d-brief-20261115.md).
   Engineer kiểm tra queue hiện tại trước khi nộp thêm task cho hai báo cáo
   phân tích sâu và Production Framework.
2. **Thử ghép giọng Việt thật vào demo stickman:** đo -16 LUFS và true peak
   ≤ -1 dBTP từ bản xuất, kiểm tra dấu và thời điểm hiện phụ đề tiếng Việt.
   [Lệnh ghép](stickman-shorts/README.md).
3. **Chuẩn bị trước buổi làm thử:** dùng danh mục Core_SFX trong Production
   Framework để sưu tầm âm có giấy phép thương mại và lưu nguồn; thử một đoạn
   giọng Việt ở 150–165 từ/phút trước khi viết kịch bản cần giọng kể.
4. **Tuần 2 (23–29/11):** viết 5 kịch bản gốc 23/11 → làm thử 5 video 25–26/11
   (Flow/Veo, Kling, hoặc Wan 2.2 local trên máy chủ) → đăng thử 27–29/11 lúc
   11:30/20:00. Kênh YouTube 2–3 kênh (Tò mò / Bất ngờ / Cảm xúc) CHỈ tạo khi chủ
   chốt tên + chủ đề.
5. **4 link Facebook share chưa đọc được** nằm ngoài danh sách 30. Bổ sung
   nghiên cứu khi có link video trực tiếp.
6. Duy trì: cron đẩy git mỗi 30 phút; file nặng lên Google Drive (thư mục
   "AgentNet Video Studio"); cập nhật file HANDOFF này mỗi khi trạng thái đổi.

## 8. Hướng mới (chủ dặn 15/11 ~01:55 — lưu lại lời chủ)

- **Lưu cả những gì chủ nói**, không chỉ kết quả.
- **Dùng ChatGPT + Gemini để TẠO video, rồi lấy video đó phân tích tiếp** bằng
  pipeline (analyze_video.py): tạo → phân tích hook/nhịp/audio → cải thiện.
  Gemini Pro tạo video bằng Veo; ChatGPT (Plus/Pro) tạo bằng Sora. Video AI tạo
  ra tải về rồi chạy qua pipeline như video ứng viên.
- **Dùng tài khoản Google đang đăng nhập (giakhanhgcm@gmail.com) để tạo 2–3 kênh
  YouTube** về một chủ đề. CHƯA tạo — cần chủ xác nhận tên kênh/chủ đề trước khi
  tạo (đây là thao tác trên tài khoản thật). Đề xuất từ nghiên cứu: (1) Tò mò —
  Visual Essay, dễ làm + viral nhất; (2) Bất ngờ — plot twist; (3) Cảm xúc —
  stickman/mindset (kiểu Reel "Tâm sự người que").
- Google Drive chưa nối (cần chủ bấm link kết nối) — file nặng đang chờ upload.

## 9. Khi Muse mới vào (chủ dặn 15/11 ~01:58)

- **Muse mới vào cần quyền gì thì cấp hết 1 lần** — đừng xin từng quyền lẻ tẻ
  làm gián đoạn công việc. Liệt kê toàn bộ quyền cần thiết (đọc/ghi file, chạy
  lệnh, trình duyệt, đăng nhập, kết nối dịch vụ, duyệt chi) và xin một lần duy nhất.
- **Lần sau cần đăng nhập gì thì cập nhật vào đây (HANDOFF.md)** — ghi rõ dịch vụ,
  tài khoản, trạng thái (đã nối/chưa nối), link kết nối. Chủ sẽ nối khi rảnh.
- **Key/API token của dự án thử nghiệm này được lưu trên Google Drive** (thư mục
  "AgentNet Video Studio", file FB_API_tokens_20261115.json) — KHÔNG đưa giá trị
  key vào git, log hay chat. Đọc key từ file trên Drive/VPS lúc chạy, không in ra.
- Chủ dặn: nếu không có việc thì tự kiếm việc mà làm; làm sớm hơn tiến độ cũng được.
