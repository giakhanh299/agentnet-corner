# Công cụ của dự án AgentNet Video Studio — kiểm kê + công cụ mới

> **Mục đích file này:** liệt kê những công cụ dự án ĐANG CÓ trên VPS và những công cụ MỚI nên có, để chủ đưa cho người khác (hoặc AI khác) đọc và trả lời câu hỏi về cách dựng/làm việc. Viết ngày 2026-11-15.
>
> **Bối cảnh dự án:** kênh YouTube Shorts faceless (video dọc 1080×1920, 38–65 giây, KHÔNG dùng máy quay — chỉ dùng AI/stock/animation/text). Giai đoạn hiện tại: tuần 1 nghiên cứu (100 video mẫu, đã phân tích 95/100, đã chốt 30 video phân tích sâu). Máy local của chủ: PC Windows, NVIDIA RTX 5060 Ti 16 GB VRAM.
>
> **Lưu ý bảo mật:** file này KHÔNG chứa bất kỳ token, API key, mật khẩu hay giá trị credential nào. Chỗ nào cần tài khoản/token thì chỉ ghi "cần tài khoản/token", không ghi giá trị.

---

# PHẦN 1 — CÔNG CỤ HIỆN CÓ (đã kiểm tra trên VPS ngày 2026-11-15)

## 1.1. Script trong `~/workspace/agentnet-corner/`

Thư mục làm việc chính của dự án trên VPS. (Thư mục `video-pipeline/` và `docs/` KHÔNG nằm ở đây mà nằm trong repo git `~/workspace/agentnet-corner-github/` — xem mục 1.4.)

| Script | Để làm gì | Chạy thế nào | Cần gì |
|---|---|---|---|
| `download_candidates.py` | Tải 100 video mẫu (73 YouTube Shorts, 27 TikTok) từ file `verify_research_payload_20261114.txt`. Ưu tiên 6 TikTok đã xác minh trước, rồi tới hài/bất ngờ/tò mò. Bỏ qua file đã tải, ghi log từng video vào `video_downloads/download_log.jsonl` | `venv/bin/python3 download_candidates.py` | yt-dlp trong venv; file danh sách ứng viên |
| `analyze_video.py` | Phân tích 1 video: ffprobe (độ dài, kích thước, độ phân giải, codec), keyframe đổi cảnh, ảnh keyframe, 30 giây audio mono 16kHz, xuất `timeline.md` + `summary.json` | `python3 analyze_video.py <video.mp4> <thư_mục_đích>` | ffmpeg/ffprobe hệ thống |
| `batch_analyze.py` | Chạy `analyze_video.py` cho mọi file `.mp4` trong `video_downloads/candidates/`, kết quả vào `video_analysis/<tên_file>/`, ghi 1 dòng/video vào `video_analysis/index.jsonl` | `python3 batch_analyze.py` | ffmpeg/ffprobe; thư mục video đã tải |
| `retry_failed.py` | Tải lại các video tải lỗi đợt đầu (19 video: 18 YouTube bị chặn bot + 1 TikTok), thử lần lượt các player client, có delay giữa các lần | `python3 retry_failed.py` | yt-dlp trong venv; `video_downloads/download_log.jsonl` |
| `queue_status.py` | Xem nhanh trạng thái hàng đợi AgentNet (bảng task + agent gọn) | `python3 queue_status.py` | File `~/.agentnet-corner/connection.json` (chứa application_token — script tự đọc, không in token); mạng Tailscale qua proxy cổng 3130 |
| `check_controller.py` | Kiểm tra API Controller, in toàn bộ JSON (rất dài — tránh dùng, dùng `queue_status.py` thay) | `python3 check_controller.py` | Như trên |
| `post_task.py` | Đăng task lên hàng đợi (định dạng CŨ) — **KHÔNG dùng để đăng task V1.2** | `python3 post_task.py <assigned_to> <kind> <dedup> <source_url> <instruction>` | application_token |
| `approve_task.py` | Duyệt 1 task đã SUBMITTED (chỉ duyệt được task có outcome `ok`/`PASS`) | `python3 approve_task.py <task_id đầy đủ>` | application_token |
| `submit_selection.py` | Đăng bản chọn 30 video (bản 92/100) lên hàng đợi: đăng task engineer → claim → nộp kết quả → đăng task verify. **Đã bị thay thế bởi `submit_final.py`** | `python3 submit_selection.py` | application_token; file `selection-30-20261115.md/.csv` |
| `submit_final.py` | Như trên nhưng cho bản chọn 30 **cuối cùng (95/100)**. Task engineer `f07e0ce6` đã SUBMITTED, task verify `f364bd47` đang chờ Verify | `python3 submit_final.py` | application_token; file `selection-30-20261115.md/.csv` |
| `upload_to_drive.sh` | Upload toàn bộ `.mp4` trong `video_downloads/candidates/` lên thư mục Google Drive "AgentNet Video Studio". Chạy lại được (bỏ qua file đã có dòng OK trong log) | `./upload_to_drive.sh` (chạy nền nếu nhiều file) | Google Drive đã kết nối; `hatch_gws_cli` |
| `auto_push.sh` | Commit + push lên GitHub CHỈ các đường dẫn an toàn (text): `video-pipeline/`, `docs/`, `HANDOFF.md`, `README.md`, `.gitignore`. Không bao giờ push media/token/credential. Chạy tự động mỗi 30 phút bằng cron | `./auto_push.sh` hoặc cron tự chạy | `gh` đã đăng nhập; repo `~/workspace/agentnet-corner-github/` |
| `apify_fb.py` | Dùng Apify (actor `apify/facebook-posts-scraper`) để đọc 4 link Facebook share + 1 Reel, lưu vào `video_downloads/fb_posts_apify.json` | `python3 apify_fb.py` | Token Apify (đọc từ file token của user, không in giá trị). **Hiện BỊ CHẶN: mọi lệnh Apify có auth đều timeout từ VPS này** |
| `apify_diag.py` | Chẩn đoán kết nối Apify: thử `GET /v2/users/me` với từng token, chỉ in mã HTTP, không in token | `python3 apify_diag.py` | Token Apify |
| `tikhub_fetch.py` | Lấy dữ liệu 1 video TikTok qua API TikHub (`GET /api/v1/tiktok/app/v3/fetch_one_video`) | `python3 tikhub_fetch.py <aweme_id>` | Token TikHub. **Đã xác nhận là ngõ cụt cho video bị chặn ở cấp tài khoản/IP TikTok** (API trả 200 nhưng không có `aweme_detail`) |
| `join.py` | Đăng ký node mới vào AgentNet (chỉ chạy 1 lần lúc dựng node). Từ chối lưu nếu không phải `project=research` + `mode=research-only` | `python3 join.py ...` | Tailscale + master API |
| `join-v11-backup.py` | Bản sao lưu của `join.py` thời V1.1 — **không dùng** | — | — |
| `push_via_api.py` | Push commit lên GitHub qua git database API (đường vòng khi `git push` bị 403). Hiện ít dùng vì PAT mới đã push được bình thường | `python3 push_via_api.py` | `gh` đã đăng nhập |

## 1.2. Phần mềm đã cài trên VPS (đã kiểm tra phiên bản)

VPS: 4 CPU, RAM 7,7 GB, ổ 150 GB (còn trống 148 GB). **Không có GPU.**

| Phần mềm | Phiên bản | Ghi chú |
|---|---|---|
| Python | 3.12.3 (hệ thống) | Dùng venv riêng cho yt-dlp vì pip hệ thống bị chặn (PEP 668) |
| Python venv | `~/workspace/agentnet-corner/venv/` | Chứa `yt-dlp` + `pip`. Lệnh: `venv/bin/python3`, `venv/bin/yt-dlp` |
| yt-dlp | 2026.10.26 (trong venv) | Công cụ tải video chính. Xem lưu ý ở mục 1.5 và 2.6 về cách dùng hiện tại |
| ffmpeg / ffprobe | 8.1.2 (hệ thống) | Dùng cho phân tích video, cắt frame, tách audio |
| gh (GitHub CLI) | 2.102.0 | Đã đăng nhập tài khoản `giakhanh299`, giao thức HTTPS |
| Tailscale | client tại `/opt/hatch/bin/tailscale` | Đã kết nối tailnet. Lưu lượng tới registry phải qua tunnel proxy cổng 3130 (lấy host từ biến `HTTPS_PROXY`, đổi cổng) |
| hatch_gws_cli | gws 0.22.5 (`/opt/hatch/bin/hatch_gws_cli`) | Lệnh cho Google Drive / Sheets / Docs |
| git | (theo hệ thống) | Push qua HTTPS only (SSH tới github.com bị chặn bởi egress proxy) |

**Chưa có trên VPS:** OpenCV, bất kỳ công cụ ASR/transcript nào (Whisper), không có GPU, không có công cụ tạo video.

## 1.3. Dịch vụ / tài khoản đã kết nối

| Dịch vụ | Dùng để làm gì | Cần gì để dùng |
|---|---|---|
| Google Drive (đã kết nối, tài khoản `giakhanhgcm@gmail.com`) | Lưu video mẫu + file key dự án. Thư mục "AgentNet Video Studio": 95 video MP4 + 1 file key | Tài khoản Google đã kết nối qua `hatch_gws_cli`. Upload đúng dạng: `hatch_gws_cli drive +upload <file> --parent <folder_id>` |
| GitHub — repo `https://github.com/giakhanh299/agentnet-corner` (public) | Lưu code + tài liệu để Muse khác tiếp quản. Commit mới nhất `df75479` (bản chọn 30 cuối, 2026-11-15 08:30 +07). Clone tại `~/workspace/agentnet-corner-github/` | `gh` đã đăng nhập (fine-grained PAT có quyền ghi, lưu trong cấu hình của `gh`) |
| AgentNet registry (master `http://100.67.236.124:8110`, project `research`) | Hàng đợi task Research / Verify / Engineer. Node controller `1a74385032d8652dc2e1b2ba`, trạng thái APPROVED | `~/.agentnet-corner/connection.json` (application_token, quyền 0600 — không in/không ghi giá trị ra ngoài) |
| Gemini (Google, gói Pro) | Hỏi đáp tư vấn (đã hỏi 5 câu + follow-up), tài khoản `giakhanhgcm@gmail.com` | Phiên đăng nhập trong trình duyệt (user tự đăng nhập). Có thể tạo video bằng Veo qua Google Flow |
| ChatGPT (gói Plus) | Hỏi đáp tư vấn (đã hỏi 5 câu + follow-up + phương pháp phân tích) | Phiên đăng nhập trong trình duyệt (user tự đăng nhập) |
| Google Sheets / Google Docs | **CHƯA kết nối** (trạng thái `not_connected`) — chưa đọc được nội dung các bảng tính trên Drive | User bấm link kết nối khi cần |
| Facebook | **CHƯA liên kết** (`facebook-cli me` trả về rỗng) — chưa đọc được 4 link share Facebook của user | User liên kết Facebook hoặc gửi URL video trực tiếp (dạng `reel/` hoặc `watch/?v=`) |
| Apify | Đọc post Facebook qua API — **BỊ CHẶN từ VPS** (mọi lệnh có auth đều timeout, chưa rõ nguyên nhân, không thử lại mù) | Token Apify (3 token trong file của user) |
| TikHub | Lấy dữ liệu video TikTok qua API — **ngõ cụt cho video bị chặn** (trả 200 nhưng không có dữ liệu video) | Token TikHub |

## 1.4. Dữ liệu và tài liệu (vị trí)

| Dữ liệu | Vị trí | Nội dung |
|---|---|---|
| Video mẫu đã tải | `~/workspace/agentnet-corner/video_downloads/candidates/` | **95 file MP4** (92 đợt đầu + 3 file khôi phục từ `.webm`: #37, #77, #82). Đã upload đủ 95/95 lên Drive |
| Kết quả phân tích video | `~/workspace/agentnet-corner/video_analysis/` | **96 thư mục** (95 video mẫu + 1 Reel Facebook FB-05), mỗi thư mục có `summary.json` + `timeline.md` + ảnh keyframe + file audio 30s. Lưu ý nhỏ: `video_analysis/index.jsonl` mới có 92 dòng (3 video khôi phục chưa được ghi thêm vào index) |
| Bản chọn 30 video (cuối cùng) | `~/workspace/agentnet-corner/selection-30-20261115.md` + `.csv` (đồng thời trong repo `docs/`) | 30 video + 10 dự bị, chấm theo công thức 100 điểm của ChatGPT + bộ lọc của Gemini. Điểm trung bình 69,07; 4 video đạt 85+; top 1 là #77 stickman "85 FLOORS / THE CABLE SNAPS!" (90 điểm) |
| Danh sách 100 ứng viên | `~/workspace/agentnet-corner/verify_research_payload_20261114.txt` | 100 URL (73 YouTube Shorts, 27 TikTok, 0 Facebook Reels) kèm niche + channel |
| Câu trả lời Gemini | `gemini-answers-20261115.md`, `gemini-followup-20261115.md` (cả trong repo `docs/`) | 5 câu hỏi + follow-up: format faceless theo niche, cách chọn 30, công cụ transcript/audio, lịch đăng/title/thumbnail/hook, kế hoạch 7 ngày |
| Câu trả lời ChatGPT | `chatgpt-answers-20261115.md`, `chatgpt-followup-20261115.md` (cả trong repo `docs/`) | 5 câu hỏi + follow-up: format, cách chấm 100 điểm, công cụ Whisper.cpp, kế hoạch 2 tuần, web tải video |
| Nguồn tham khảo thêm | `more-sources-20261115.md` (cả trong repo `docs/`) | ~132 nguồn: 56 kênh/creator, 20 công cụ trend, 56 tài nguyên sản xuất |
| Prompt + hướng dẫn bàn giao | Repo `~/workspace/agentnet-corner-github/HANDOFF.md`, `master-v1.0.md`, `MASTER_PROMPT_V1_2.md` | Prompt V1.0 (user chọn), V1.2 (research-only), hướng dẫn để Muse mới tiếp quản |
| Code pipeline trong repo | `~/workspace/agentnet-corner-github/video-pipeline/` | `README.md`, `analyze_video.py`, `download_candidates.py` |
| Video test pipeline | `~/workspace/agentnet-corner/video_pipeline_test/` | Video test Big Buck Bunny (CC-BY) + timeline mẫu |
| Báo cáo kiểm chứng | `~/workspace/agentnet-corner/verify-84434dcd-brief-20261115.md` | Kết quả Verify cho bản chọn 30 (bản 92/100): kiểm tra chính PASS, 2 lỗi chỉ là câu chữ về giới hạn |

## 1.5. Khoảng trống đã biết (chưa có / đang bị chặn)

- ⚠️ **REPO NGƯỜI QUE (STICKMAN) CHƯA CÓ — đây là khoảng trống lớn nhất.** Không có repo nào cho việc sản xuất video stickman: không có code animation stickman, không có template, không có rig/nhân vật. Tài liệu stickman hiện có CHỈ là: video tham khảo đã phân tích (Reel Facebook FB-05 "CÁCH LÀM GIÀU DỄ NHẤT VÀ NHANH NHẤT", #50 stickman "EVERY DAY, THE WORLD WALKED PAST HIM", #77 stickman "85 FLOORS / THE CABLE SNAPS!") + 1 kịch bản remake 50–55s do ChatGPT viết cho FB-05. Cần xây mới từ đầu — xem công cụ đề xuất ở mục 2.3.
- Không có công cụ transcript/ASR (hook bằng lời nói và audio của 95 video chưa được đánh giá).
- Không có công cụ tạo video (chưa tạo video nào; mới chỉ phân tích video mẫu).
- 5/100 video mẫu chưa tải được (#6, #21, #38, #75 TikTok bị chặn IP, #94).
- Apify bị chặn từ VPS → 4 link Facebook share của user vẫn chưa đọc được.
- Google Sheets/Docs chưa kết nối → chưa đọc được nội dung bảng tính trên Drive (Chamcong, UPVIDEO, nhân sự…).
- Lưu ý về yt-dlp: dự án hiện dùng `--extractor-args "youtube:player_client=android"` để qua chặn bot YouTube (đã kiểm chứng chạy được ngày 2026-11-15). Nghiên cứu mới (mục 2.6) cho thấy cách này đã lỗi thời — xem mục 2.6 trước khi dùng cho đợt tải sau.

---

# PHẦN 2 — CÔNG CỤ MỚI NÊN CÓ (nghiên cứu mới ngày 2026-11-15)

> Các công cụ dưới đây là nghiên cứu mới trên web (tháng 11/2026), chưa được cài/thử trong dự án. Giá là giá niêm yết USD trừ khi ghi khác. Chỗ nào chưa xác minh được sẽ ghi rõ "chưa xác minh".

## 2.1. Checklist cài đặt máy local (PC Windows, RTX 5060 Ti)

Thứ tự cài — làm theo từng bước, kiểm tra xong bước nào mới sang bước sau:

| Bước | Cài gì | Cách làm / ghi chú |
|---|---|---|
| 1. Hệ điều hành | Windows 11 22H2 trở lên (khuyên 24H2) | WSL2 GPU passthrough chạy sẵn trên 24H2. Windows 10 vẫn chạy được Ollama nhưng đã hết hỗ trợ chính |
| 2. Driver NVIDIA | Driver mới nhất (≥ 572.60; khuyên 580 trở lên) | Tải từ trang NVIDIA. Nếu máy từng có driver cũ, dùng DDU gỡ sạch rồi cài mới. Kiểm tra bằng `nvidia-smi` |
| 3. Python | 3.11 hoặc 3.12 | Dùng venv riêng cho từng project. **Không dùng lại venv cũ** tạo cho card đời trước Blackwell |
| 4. git + gh | `git`, GitHub CLI (`gh auth login`) | Như trên VPS |
| 5. ffmpeg | Bản full (gyan.dev / BtbN), cho vào PATH | Cần cho yt-dlp, Whisper, Subtitle Edit, loudnorm. Kiểm tra `ffmpeg -h filter=ass` nếu cần burn subtitle |
| 6. yt-dlp | Bản mới nhất **2026.10.26** | `yt-dlp -U` hoặc pip. Cần Python ≥ 3.11 |
| 7. JS runtime cho yt-dlp | **Deno ≥ 2.3.0** (mặc định bật) | Bắt buộc để giải thử thách JS của YouTube. Node ≥ 22 cũng được nhưng không bật mặc định |
| 8. PyTorch | `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128` (hoặc cu130 nếu lúc cài pytorch.org đã chuyển sang CUDA 13) | **TUYỆT ĐỐI KHÔNG cài cu124/cu126** — xem mục 2.2. Kiểm tra: `python -c "import torch; print(torch.__version__, torch.cuda.get_device_capability(), torch.cuda.get_arch_list())"` — phải có `sm_120` / `(12, 0)` |
| 9. Giao diện ảnh/video | **ComfyUI portable (Windows)** — bản portable hiện tại đã kèm PyTorch/CUDA mới, hỗ trợ sm_120; hoặc Forge Neo | Tránh các app đóng gói cũ ghim `torch==2.1.0` (vd: launcher Fooocus — đã báo lỗi sm_120 trên RTX 5060) |
| 10. LLM local | **Ollama** (cài native Windows / `winget install Ollama.Ollama`, API ở cổng 11434) hoặc **LM Studio** (giao diện, có sẵn trình duyệt model) | Cả hai đều dựa trên llama.cpp, dùng CUDA trên NVIDIA. **vLLM chỉ chạy dưới WSL2, không chạy native trên Windows** |
| 11. WSL2 (tùy chọn) | `wsl --install -d Ubuntu-24.04`, rồi chạy `nvidia-smi` trong WSL để xác nhận passthrough | Dùng cho tool Linux-first (vLLM, Unsloth, bitsandbytes). Chậm hơn native Windows ~2–15% khi inference; Windows giữ nhiều VRAM/RAM hơn Linux nên VRAM dùng được hơi ít hơn. Ubuntu bare-metal là tốt nhất cho máy chạy 24/7; WSL2 đủ dùng cho máy trạm |

## 2.2. Máy local của chủ: RTX 5060 Ti 16GB — chạy được gì, không chạy được gì

### Điểm quan trọng nhất: Blackwell (sm_120) cần phần mềm mới

- RTX 5060 Ti / toàn bộ RTX 50-series là kiến trúc **Blackwell, compute capability 12.0 (`sm_120`)**.
- **Driver tối thiểu: R570 (Linux) / 572 (Windows); CUDA tối thiểu 12.8** cho kernel sm_120. Thực tế: cài driver mới nhất (≥ 572.60 Windows, ≥ 570 Linux; 580+ an toàn hơn cho wheel CUDA 13).
- **PyTorch cũ SẼ LỖI.** `torch < 2.7` (wheel cu121/cu124/cu126) chỉ có kernel tới `sm_90`: import vẫn được, `torch.cuda.is_available()` vẫn trả True, nhưng chạy kernel đầu tiên sẽ lỗi `CUDA error: no kernel image is available for execution on the device` / `sm_120 is not compatible with the current PyTorch installation`.
- **Hỗ trợ Blackwell ổn định đầu tiên: PyTorch 2.7.0 + CUDA 12.8 (`cu128`)**, ra tháng 4/2025. Đã có báo cáo `torch==2.10.0+cu128` chạy tốt trên 5060 Ti (driver 570.211.01, Ubuntu 24.04, Python 3.12.3).
- **Chưa xác minh:** bản stable mới nhất ngày 15/11/2026 là gì (nguồn mâu thuẫn giữa cu128, 2.10/cu128 và 2.13/cu130). **Lúc cài dùng bộ chọn trên pytorch.org, lấy wheel CUDA 12.8+ mới nhất (cu128 hoặc cu130), rồi kiểm tra bằng lệnh ở bước 8 trên.**
- Wheel PyTorch **đã kèm sẵn CUDA runtime/cuDNN** — không cần cài riêng CUDA Toolkit khi dùng PyTorch/ComfyUI. Chỉ cài Toolkit (12.8.1) nếu cần biên dịch extension (flash-attn, bitsandbytes, bản CUDA của whisper.cpp).
- Lưu ý: các extension biên dịch sẵn (xformers, flash-attn, bitsandbytes, sageattention, custom node ComfyUI) có thể lỗi độc lập ngay cả khi torch đã hỗ trợ sm_120 — test 1 lần tạo ảnh/video cơ bản trước khi thêm node.

### Chạy ĐƯỢC trên 16 GB VRAM (số liệu gần đúng, 1024×1024 / 720p trừ khi ghi khác)

| Việc | Vừa không | VRAM / ghi chú |
|---|---|---|
| Whisper large-v3 | ✅ dễ | ~10 GB FP16, ~5 GB INT8 (faster-whisper); bản turbo ~6 GB FP16 / ~3 GB INT8 |
| Whisper large-v3-turbo | ✅ | ~6 GB; nhanh gấp ~8 lần large-v3, độ chính xác gần tương đương — lựa chọn hợp lý nhất |
| Stable Diffusion 1.5 | ✅ | ~4 GB @512×512 |
| SDXL base | ✅ | ~8 GB @1024×1024; ~12 GB nếu load refiner cùng lúc; ~14–16 GB với ControlNet. Vừa thoải mái trên 16 GB |
| SD 3.5 Medium | ✅ | ~9,9 GB (chưa tính text encoder) |
| FLUX.1 [dev/schnell] 12B | ✅ **chỉ bản lượng tử hóa** | FP16 cần **23,8 GB — KHÔNG vừa**. FP8: ~11,9 GB file, thực tế ~12–16 GB (tối thiểu 13,3 GB ở 1024×1024). GGUF Q4_K_S 6,8 GB / Q5 8,3 GB / Q8_0 12,7 GB đều vừa. Cần 32 GB RAM hệ thống để offload CPU. **Giấy phép: FLUX.1 [dev] cấm dùng thương mại; [schnell] là Apache 2.0** |
| Wan 2.1 T2V-1.3B | ✅ | Chính thức **8,19 GB** VRAM, clip 5 giây 480p ~4 phút trên RTX 4090; GGUF Q4 ~4–6 GB |
| Wan 2.2 TI2V-5B | ✅ có offload | File FP16 10 GB; mục tiêu chính thức **24 GB** (RTX 4090, 720p/24fps). Tài liệu ComfyUI: "vừa tốt trên 8 GB VRAM với native offloading"; GGUF Q8_0 5,4 GB. Trên 16 GB sẽ chậm ở 720p |
| Wan 2.2 T2V/I2V-A14B (MoE, 27B tổng / 14B active) | ⚠️ **chỉ bản lượng tử hóa + offload T5 lên CPU** | FP16: **~54–65 GB tổng** (transformer ~28 GB + T5-XXL ~9,4 GB) — KHÔNG vừa. FP8 transformer: ~22–26 GB trên GPU, ~14–16 GB khi offload CPU. **GGUF Q5_K_M: ~10,8 GB/expert, cộng đồng báo chạy được trên 16 GB ở 720p; Q4_K_M ~9,65 GB/expert, 12–16 GB với offload, chậm hơn.** Cần **≥ 32 GB RAM hệ thống** (T5-XXL offload lên CPU). Clip 720p mất 2–4 phút trên card 16 GB với cấu hình này. Apache 2.0 (dùng thương mại được) |
| LTX-2 / LTX-2.5 distilled | ✅ | **16 GB là mức sàn theo tài liệu** (lượng tử hóa FP8/NVFP8, 720p/24fps/clip 4 giây); bản dev 22B cần 24 GB. Khuyên 32 GB RAM hệ thống; LTX Desktop cần 160 GB ổ đĩa |
| LLM local (Ollama / LM Studio, Q4_K_M, context 8K) | ✅ 7B/8B, ⚠️ 13/14B, ⚠️ 30B ở Q3 | Llama 3.1 8B Q4 ~**5–5,5 GB**, ~30–42 token/giây; Mistral 7B Q4 ~5 GB; Qwen2.5 7B ~5,2 GB; 8B Q8 ~7–8,5 GB (chật, context nhỏ). **13B/14B Q4 ~8,5–9 GB — vừa 16 GB, ~25 token/giây. 30B Q3_K_S vừa, ~10 token/giây.** Context dài (128K) làm KV cache phình to (12 GB+ chỉ cho 8B) — giữ context 4–8K |
| Real-ESRGAN (upscale ảnh/video) | ✅ dễ | Tối thiểu **4 GB** (checkpoint 67 MB); thường 2–4 GB VRAM cho đầu ra 4K với tiling. Video: tối thiểu 8 GB cho pipeline Real-ESRGAN+RIFE. Upscaler diffusion (SUPIR, SeedVR2 3B) cần 12–16 GB; SeedVR2 7B cần 24 GB+ |
| TTS local — Piper / Kokoro | ✅ | Piper 0,5–1,5 GB (chạy CPU là chính); Kokoro-82M ~2–3 GB, chạy được trên CPU |
| TTS — XTTS-v2 / F5-TTS | ✅ | XTTS-v2 750M ~4,2 GB FP16 (khuyên 4–6 GB); F5-TTS 336M ~2,5–5 GB. Cả hai clone giọng từ clip mẫu 3–6 giây. **Giấy phép phi thương mại: XTTS-v2 CPML, F5-TTS CC-BY-NC — KHÔNG dùng cho giọng kênh kiếm tiền** (xem mục 2.5) |
| Blender Grease Pencil, Manim, Remotion, Pivot | ✅ dễ | Chủ yếu dùng CPU/2D, card này thừa sức |

### KHÔNG chạy được trên 16 GB VRAM — ghi rõ để khỏi mất thời gian thử

- **Wan 2.2 A14B ở FP16** (~54–65 GB tổng) và **Wan 2.2 TI2V-5B ở FP16 không offload** (chính thức 24 GB).
- **FLUX.1 [dev] FP16** (23,8 GB chỉ riêng transformer, ~33 GB kèm T5-XXL FP16) và **FLUX.2 [dev]** (tối thiểu fp8 ~36–48 GB).
- **LLM 70B:** Llama 3.1 70B Q4 ~**38 GB**, FP16 ~140 GB — không thể chạy trên 16 GB. (70B Q2 có nơi ghi ~24 GB — vẫn không vừa.)
- **SD 3.5 Large FP16** (> 18 GB; ~11 GB dạng FP8 qua TensorRT mới vừa).
- **Model video lớn full-precision nói chung** (HunyuanVideo gốc 13B: 45 GB @544×960, 60 GB @720p, khuyên 80 GB).
- **Fine-tune LoRA** cho LLM 7B cần ~10 GB+; fine-tune model video thì ngoài tầm card này.

### Giới hạn thực tế cho video AI local

- Wan 2.2 và LTX: mỗi lần tạo chỉ ~5 giây ở 720p. Một Short 50 giây = ~10 clip nối lại + edit. Tính trước thời gian render. Wan không có audio sẵn (phải ghép giọng/nhạc riêng bằng ffmpeg); LTX có audio đồng bộ trong 1 lần tạo.
- Nguồn: pytorch.org, discuss.pytorch.org (sm_120), github.com/anasalqadhi/rtx5060ti-cuda-ubuntu-setup, vramglass.com, localaimaster.com, runaihome.com, smeltcore.com (FLUX trên RTX 5060 Ti).

## 2.3. Sản xuất video stickman ("người que") — khoảng trống lớn nhất

> Hiện trạng: **chưa có repo/code/template stickman nào.** Phần này là các công cụ để xây nó từ đầu. Khuyến nghị tổng thể: **Manim hoặc Remotion** (code 1 rig stickman dùng lại cho mọi video — nhân vật nhất quán tuyệt đối, miễn phí, không watermark) + **Pivot Animator** cho người không biết code; AI video chỉ làm bổ sung (B-roll), **không** dựa vào AI để giữ nhân vật stickman nhất quán qua nhiều cảnh (xem giới hạn ở cuối mục).

### 2.3.1. Phần mềm desktop vẽ stickman

| Công cụ | Miễn phí? | Windows? | Xuất MP4 dọc? | Độ khó / ghi chú |
|---|---|---|---|---|
| **Pivot Animator 5.2.x** | **Miễn phí, kể cả dùng thương mại** | **Chỉ Windows** (Win 7 SP1+, DirectX 11, GPU) | **Có — MP4, WEBM, WMV, AVI, GIF/APNG trực tiếp** | **Dễ bắt đầu nhất.** Kéo khớp để tạo dáng, thêm frame, lặp lại; v5 tự nội suy (inbetweening); có camera ảo/pan-zoom. **Không có track audio** — ghép giọng/nhạc ở editor sau. Đặt canvas 1080×1920 |
| **Stick Nodes** | Bản free; **Pro $3,99 trả 1 lần** (app riêng) | **Chỉ mobile — Android/iOS**, không có bản Windows | Free chỉ GIF; **Pro mới có MP4, không watermark, có âm thanh/filter** | Tạo dáng stick figure, tự tween. Tốt để phác trên điện thoại, không phải pipeline desktop |
| **StykAnimate** (mới) | **Miễn phí, open-source (GPL-3.0)** | Windows, Linux, trình duyệt | MP4, WebM (nền trong suốt), GIF, APNG | **Mới — repo tạo ngày 9/11/2026.** Mở được project Pivot (.piv/.stk) và Stick Nodes. Còn non, chưa có review độc lập — triển vọng thay Pivot, chưa chứng minh được |
| **Wick Editor** | **Miễn phí, open-source** | Web (trình duyệt), có bản desktop | MP4, GIF, HTML, SVG, PNG | Chạy trên trình duyệt, không cần cài; tốt cho 2D đơn giản + code. Chậm với project lớn/phức tạp |
| **Pencil2D** | **Miễn phí, open-source** | Windows, macOS, Linux | MP4, WEBM, AVI, GIF, APNG, PNG sequence | **Vẽ tay từng frame dễ nhất.** Không có rigging/tweening — phải vẽ từng frame. Không chuyên stickman |
| **Synfig Studio** | **Miễn phí, open-source** | Windows, macOS, Linux | Video, GIF, image sequence | Tween vector: đặt pose chính, phần mềm tự điền frame giữa. Khó trung bình; tốt cho stickman vector mượt nếu tự build rig |
| **OpenToonz** | **Miễn phí, open-source** | Windows, macOS, Linux | Xuất video (qua ffmpeg) | Chuẩn chuyên nghiệp (dòng Studio Ghibli), có rigging nhân vật. **Khó học nhất trong nhóm; quá mức cần thiết cho stickman** |
| **Blender Grease Pencil** | **Miễn phí, open-source** | Windows, macOS, Linux | **Có — FFmpeg Video → MPEG-4/H.264 MP4, đặt 1080×1920, Eevee, 24/30 fps** | Công cụ 2D-trong-3D đầy đủ: layer, camera, edit video (VSE) trong 1 app. Khó hơn Pivot nhưng mạnh hơn nhiều (đạo cụ, nền, chuyển động camera). Có API Python để viết script. Chạy nhẹ trên RTX 5060 Ti |
| **Adobe Animate** | **Không — $22,99/tháng** (trả theo năm), trial 7 ngày | Windows, macOS | Xuất video/HTML5 Canvas/WebGL/SVG | Timeline vector, rig xương, tween. ⚠️ **Từ tháng 2/2026 chỉ còn bảo trì: vẫn bán, chỉ sửa lỗi/bảo mật, không tính năng mới.** Không khuyên dùng cho pipeline mới |
| FlipaClip | Miễn phí; Plus tùy chọn | Mobile (iOS/Android) | MP4 (bản free có watermark theo kiểm tra tháng 11/2026) | Vẽ tay từng frame trên điện thoại/tablet. Không phải công cụ stickman desktop |

Nguồn: taletok.io (hướng dẫn làm stickman), github.com/oxzoe/StykAnimate-App, itechfaqs.com, stickreel.com.

### 2.3.2. Animation bằng code — cách làm được nhiều video nhất

**Tốt nhất cho người biết code (hoặc AI viết code): Manim hoặc Remotion. Người không biết code: không dùng trực tiếp được — dùng Pivot, hoặc nhờ ChatGPT/Gemini viết code Manim/Remotion rồi chỉ việc chạy.**

- **Manim (Community Edition, Python, miễn phí/open-source)** — **Đã kiểm chứng workflow dọc:** đặt `config.pixel_width=1080, config.pixel_height=1920, frame_width=9, frame_height=16`; render `manim -qh --format mp4 script.py Scene` → MP4 H.264 1080×1920, 30/60 fps. Rất hợp video giải thích vật lý, sơ đồ, text + stickman vector đơn giản (đường thẳng/vòng tròn trong Manim là chuyện nhỏ). Render bằng CPU, không cần GPU. Mỗi beat của câu chuyện là 1 scene-class, nối bằng ffmpeg. Độ khó trung bình nếu biết Python; LLM viết được hầu hết scene. Đã có repo công khai làm đúng việc này (Shorts/TikTok dọc, 38–40 giây, Manim + TTS + ffmpeg mux).
- **Remotion (React, miễn phí cho cá nhân / team ≤ 3 người; licence Company $25/ghế/tháng nếu lớn hơn)** — video = component React, từng frame một; lệnh `npx remotion render … out/video.mp4`, rộng 1080 / cao 1920, 30 fps. Rất tốt cho kinetic type, caption, template theo dữ liệu, và dùng lại 1 component stickman (SVG) cho 100 video. Cần biết Node + React; LLM (Claude Code / ChatGPT Codex) viết tốt — đây đã là workflow chuẩn. Render local, không cần GPU.
- **GSAP / SVG / Canvas / p5.js** — miễn phí, thư viện animation chạy trên trình duyệt. Tốt cho chuyển động, morph, vẽ đường. **Không xuất MP4 trực tiếp** — phải quay màn hình hoặc capture headless (Playwright/Chromium + ffmpeg) từng frame để ra MP4. Dùng được, nhưng thêm 1 bước so với Manim/Remotion. Hợp làm lớp vẽ *bên trong* pipeline Remotion hoặc HTML-to-video.
- **Kết luận:** để làm stickman từ kịch bản với số lượng lớn, **Manim (video giải thích vật lý/tò mò) + Remotion (Shorts kể chuyện/text)** là tổ hợp mạnh nhất. Build 1 rig stickman dùng lại (các dáng đi, chỉ, ngã, suy nghĩ, ăn mừng thành hàm) thì mỗi kịch bản mới chỉ là dữ liệu, không phải làm animation mới. **Đây chính là cái "repo" còn thiếu — nên tự xây, không mua.**

### 2.3.3. Công cụ AI tạo stickman sẵn (gõ text → video stickman hoàn chỉnh)

- **StickReel** — https://stickreel.com/ — trial miễn phí, rồi **$19/tháng Starter (16 credit/tháng), $39/tháng Creator, $99/tháng Pro**. Dọc 9:16 + ngang 16:9, tối đa 10 phút. Video 30 giây = 1 credit (Moving Images) / 4 (Mixed Motion) / 6 (Full Animation); 60 giây gấp đôi. **Dùng thương mại được trên mọi gói.** Phù hợp nhất cho dự án trong các tool chuyên stickman.
- **Stickmotion** — 50 credit miễn phí khi đăng ký, **Starter $15/tháng**, project tối đa 10 phút, có thư viện dáng, 1 dàn nhân vật stickman (tốt cho nhất quán). Nguồn là bảng so sánh của đối thủ — kiểm tra giá trên trang chính trước khi trả tiền.
- **ClipFlux** — từ **$29/tháng**; làm Shorts stickman + video dài. ⚠️ Trang nguồn do chính ClipFlux viết (tự quảng cáo); đối chiếu so sánh đối thủ của họ một cách thận trọng.
- **Chưa xác minh:** các tool này có lồng tiếng Việt tốt không, và điều khoản watermark ở bản trial miễn phí — kiểm tra trước khi dùng.

### 2.3.4. Gói asset/template stickman có sẵn (mua 1 lần / thuê bao)

- **VideoHive (Envato Market, mua theo món):** các pack cũ (2015–2016) nhưng vẫn dùng được, 1080p MOV/PNG+alpha loop: Business Stickman Pack 2/4/5 — **$25 mỗi pack** (16–24 clip, loop 4–5 giây); Happy Stickman Pack 2 — **$25**; Stickman Cycling Super Pack — **$19** (60 clip); Stick Figure Normal Walk 2-pack — **$18**. **Stick Figure Rig cho After Effects — $186** (rig vector, dựa trên Limber, AE 2020+; rig thật duy nhất tìm được). ⚠️ Đây là *clip render sẵn dạng loop*, không phải rig — tốt làm B-roll/phản ứng, không kể được câu chuyện mới. Licence thường: dùng cho số lượng sản phẩm không giới hạn, miễn phí hoặc thương mại.
- **Envato Elements (thuê bao, tải không giới hạn):** **Core $16,50/tháng (trả theo năm, $198/năm) hoặc ~$33–39/tháng (trả tháng); Plus từ $39/tháng (năm); Ultimate $109/tháng (năm).** Licence thương mại trọn đời cho project được cấp phép trong thời gian thuê bao. Hữu ích nếu cần cả stock footage/nhạc/font — không chuyên stickman.
- **Motion Array:** gói template **báo cáo $15,99/tháng (trả theo năm)** — giá từ nguồn thứ ba tháng 8/2026, chưa xác minh trên trang vendor (trả về 403).
- **Khác:** Gumroad "Animated Stickman Pack" (Premiere Pro .MOGRT) ~299 INR (~$3,50); Codester "Stickman Animation Pack" (Unity/Spine, 100+ animation game) **$99** — hướng game, không phải video. **Không tìm được pack rig stickman chuyên dụng, mới, sẵn kể chuyện cho YouTube Shorts** — càng khẳng định khoảng trống này.

### 2.3.5. Giới hạn thật của AI video với nhân vật stickman

- **Không có model AI video tổng quát nào tạo được nhân vật stickman *nhất quán* một cách đáng tin.** Mỗi clip được diễn giải lại từ đầu; tỷ lệ cơ thể/quần áo/chi tiết trôi giữa các lần tạo, càng tệ với clip dài và đổi góc sáng/camera. Cách giảm (không sửa triệt để): ảnh tham chiếu (Runway Gen-4: tối đa 3 ảnh; Kling 3.0: tối đa 2, 7 ở Universal Reference, multi-shot tối đa 6 shot; Veo 3.1: ingredients-to-video với ảnh tham chiếu), giữ nguyên wording prompt, chuyển động/ánh sáng vừa phải, nối frame cuối clip trước làm frame đầu clip sau. Độ trôi tích lũy tới shot 10–15. Stickman *dễ hơn* người photoreal (ít chi tiết để trôi), nhưng số chi, độ dày nét và tỷ lệ vẫn lệch.
- Vì vậy: **AI video chỉ nên làm B-roll/cảnh mở đầu, còn stickman kể chuyện chính phải làm bằng Manim/Remotion/Pivot** (xác định, nhất quán 100%).

## 2.4. Tạo video bằng AI (chung cho video faceless)

Tất cả tool cloud dưới đây đều **chỉ chạy trên cloud** (không dùng GPU local). Chỉ Wan 2.2 / LTX chạy được trên RTX 5060 Ti. Mỗi lần tạo chỉ 5–15 giây; Short 38–65 giây cần nối nhiều clip lại.

| Công cụ | Để làm gì / vì sao hợp dự án | Giá / free tier (11/2026) | Watermark + dùng thương mại | Lấy ở đâu |
|---|---|---|---|---|
| **Google Flow / Veo 3.1** | Studio làm phim AI của Google; Veo 3.1 bám prompt tốt nhất + **audio đồng bộ sẵn**; Flow có Scenebuilder, ingredients-to-video (ảnh tham chiếu), edit. Điểm vào miễn phí chất lượng cao nhất | **Miễn phí: 50 credit Flow/ngày, không cần gói** (không cộng dồn). Veo 3.1 Lite 10 credit/clip (4/6/8 giây, 720p). **Plus $4,99/tháng** (200/tháng), **Pro $19,99/tháng hoặc $199,99/năm (1.000/tháng)** — gói trả phí hợp lý nhất, **Ultra 5x $99,99/tháng (10.000/tháng), Ultra 20x $199,99/tháng (25.000/tháng)**. Model tháng 11/2026: Omni Flash 1.2 (tối đa 10 giây free / 15 giây trả phí) + Veo 3.1 Lite (tối đa 8 giây). Veo 3.1 Fast/Quality + Omni 1.1 ngừng **5/12/2026** | **Watermark ẩn SynthID trên mọi output, mọi gói** (+ C2PA trên Omni). ⚠️ **Watermark HIỆN được tự gắn ở Việt Nam (cả Ấn Độ, Hàn Quốc) trừ khi dùng Ultra 20x** — liên quan trực tiếp tới user. Google không sở hữu output; dùng thương mại theo ToS Google + GenAI Prohibited Use Policy (không được giả làm người thật) | flow.google.com (xem thêm professionalstoolkit.com, theairankings.com) |
| **Kling (Kuaishou)** | Chuyển động thực nhất theo giá tiền; Kling 3.0, storyboard multi-shot (tối đa 6 shot), audio sẵn, clip tới 30 giây | **Miễn phí: 66 credit/ngày, không cộng dồn** — nhưng chỉ dùng **Kling 2.1 cũ, 5 giây, 720p**. **Standard ~$6,99–$10/tháng** (660 credit, giá tháng đầu khuyến mãi khác giá gia hạn ~$8,80 — **nguồn mâu thuẫn, kiểm tra lúc thanh toán**), Pro ~$25,99–$32,56/tháng (3.000), Premier ~$64,99–$80,96/tháng. Kling 3.0, 1080p/4K, từ 10 giây trở lên bắt đầu ở gói Standard | **Free: có watermark hiện, chỉ dùng cá nhân — cấm dùng thương mại nếu không có gói trả phí.** Trả phí: gỡ watermark, được dùng thương mại | klingai.com |
| **Runway Gen-4 / Gen-4.5** | Ưu tiên editor: tạo + timeline thật, Gen-4 Reference (tối đa 3 ảnh tham chiếu — hiện là cơ chế giữ nhất quán qua shot mạnh nhất), brand kit | **Miễn phí: 125 credit 1 lần duy nhất, không nạp lại** (~2 clip 5 giây Gen-4.5, 60 credit/5 giây). **Standard $15/tháng ($12/tháng nếu trả theo năm, 625 credit/tháng)**, Pro ~$28/tháng, Max ~$76/tháng | Bản free xuất **có watermark**; gói trả phí gỡ watermark. Dùng thương mại trên gói trả phí | runwayml.com |
| **Pika** | Nhanh, hiệu ứng sáng tạo/clip mạng xã hội; image-to-video từ ảnh tham chiếu | **Miễn phí: 80 credit/tháng ở 480p** (theo đa số nguồn). **Standard $10/tháng ($8/tháng nếu trả năm, 700 credit)**, Pro $28/tháng, Fancy $76/tháng | ⚠️ **Nguồn mâu thuẫn về watermark bản free**: 1 bảng so sánh tháng 9/2026 nói bản free tải về **không** watermark; nguồn khác nói bản free **có watermark, không dùng thương mại**. Dùng thương mại trên gói trả phí. **Chưa xác minh — kiểm tra trang giá của Pika** | pika.art |
| **Luma Dream Machine (Ray2)** | Chuyển động photoreal/điện ảnh nhất; nhanh. Nay gói trong lớp workflow "Luma Agents" | ⚠️ **Nguồn mâu thuẫn**: 1 nguồn nói free ~30 lần tạo/tháng; nguồn khác (tháng 10/2026, trang vendor) nói **không có gói free**. Trả phí: **Lite $9,99/tháng, Plus $29,99/tháng (10.000 credit), Pro $90/tháng, Ultra $300/tháng**. **Chưa xác minh — kiểm tra trang vendor** | Bản free (nếu có) có watermark, không có quyền thương mại. **Dùng thương mại + gỡ watermark từ gói Plus ($29,99/tháng)** | lumalabs.ai |
| **Hailuo / MiniMax (H3 / Hailuo 2.3)** | Vật lý tốt nhất theo giá tiền; chuyển động mạnh. App tại hailuoai.video | **Miễn phí: $0 nhưng 0 credit/tháng** — chỉ có gói chào mừng 1 lần, hết hạn **3 ngày** sau khi nhận; 6 giây, 768p. **Standard $14,99/tháng niêm yết (khuyến mãi ~$7,99–$10,50) cho 1.000 credit ≈ 40 clip 6 giây 768p**, Pro $54,99/tháng, Master $94,99–$119,99/tháng, Max $199,99/tháng. API: H3 ~$0,08/giây ở 768p | Free: **có watermark, không dùng thương mại**. Trả phí: không watermark, được dùng thương mại theo điều khoản | hailuoai.video |
| **Sora (OpenAI)** | — | ⛔ **ĐÃ NGỪNG — KHÔNG LẬP KẾ HOẠCH THEO NÓ.** Web/app ngừng **26/4/2026**, API ngừng **24/9/2026** (OpenAI Help Center, kiểm tra tháng 11/2026). Không có waitlist, không có gói trả phí nào khôi phục lại. Chỉ tải được output cũ qua sora.chatgpt.com/sunset. Hồi còn chạy: Plus $20/tháng (720p, có watermark), Pro $200/tháng (1080p, không watermark). Kết luận này giải quyết mâu thuẫn trước đó: câu "Sora vẫn còn trên Plus" đã lỗi thời | Hồi còn chạy: watermark động hiện + C2PA trên Plus; sạch hơn trên Pro. Nay không còn ý nghĩa | — |
| **Wan 2.2 (Alibaba, tự host)** | **Open-weights, model mở gần Kling/Veo nhất về chuyển động.** Text-to-video + image-to-video. **Chạy local trên RTX 5060 Ti 16 GB** | **Miễn phí — không thuê bao, không credit, render không giới hạn** (chỉ tốn điện + thời gian setup). Qua ComfyUI / diffusers; weight trên Hugging Face | **Không watermark. Apache 2.0 — dùng thương mại miễn phí, không royalty.** Không có audio sẵn (pipeline riêng) | huggingface.co (tìm Wan 2.2) |
| **LTX-2 / LTX-2.5 (Lightricks, tự host)** | Open-weights, **model mở nhanh nhất + có audio đồng bộ sẵn trong 1 lần tạo** (khác Wan). LTX-2.5 (22B, tháng 8/2026) multishot. **Chạy local trên 16 GB** | **Weight miễn phí** (app LTX Desktop miễn phí; API từ $0,09/giây ở 720p nếu dùng host) | **Không watermark khi tự host. Community Licence: dùng thương mại miễn phí nếu doanh thu năm dưới $10M**; trên mức đó cần thỏa thuận trả phí. Không phải licence open-source chuẩn (có giới hạn doanh thu) | lightricks.com / huggingface.co (tìm LTX-2) |

### Vừa VRAM trên RTX 5060 Ti 16 GB (video AI local)

- **Wan 2.2:** 1.3B ≈ 8,2 GB VRAM; **TI2V-5B ≈ 12–16 GB — điểm ngọt cho card này** (720p, clip 5 giây); 14B cần 24 GB FP8, hoặc ~16 GB qua lượng tử hóa GGUF nhưng tạo chậm hơn (~90 giây–4+ phút cho clip 5 giây) + offload. ~30 GB ổ đĩa cho mỗi biến thể.
- **LTX-2/2.5 distilled:** **16 GB là mức sàn theo tài liệu** (lượng tử hóa FP8/NVFP8, 720p/24fps/clip 4 giây); model dev 22B cần 24 GB. Khuyên 32 GB RAM hệ thống; LTX Desktop cần 160 GB ổ đĩa.
- **Giới hạn thực tế:** ~5 giây/clip ở 720p; Short 50 giây = ~10 clip nối lại + edit. Wan không có audio sẵn; LTX có.

## 2.5. Transcript + phân tích audio (cho VPS yếu và máy local)

**Chia việc hợp lý:** VPS (không GPU, 4 CPU / 8 GB RAM) → whisper.cpp `tiny/base/small` hoặc API Groq; máy local (5060 Ti) → faster-whisper `large-v3-turbo` / `large-v3`, UVR, TTS, upscale.

### Bảng model Whisper (thông số chính thức OpenAI; VRAM theo model card)

| Model | Tham số | File whisper.cpp / RAM | VRAM GPU (PyTorch FP16) | Tốc độ tương đối |
|---|---|---|---|---|
| tiny | 39M | 75 MB / ~273 MB | ~1 GB | ~10× |
| base | 74M | 142 MB / ~388 MB | ~1 GB | ~7× |
| small | 244M | 466 MB / ~852 MB | ~2 GB | ~4× |
| medium | 769M | 1,5 GB / ~2,1 GB | ~5 GB | ~2× |
| large-v3 | 1.550M | 2,9 GB / ~3,9 GB | ~10 GB | 1× |
| large-v3-turbo | 809M | 1,5 GB (547 MB dạng q5_0) / ~6 GB VRAM | ~6 GB | ~8× |

WER (tiếng Anh sạch, LibriSpeech): large-v3 ~2,7%, turbo ~7,8% trên benchmark rộng hơn — turbo là điểm ngọt thực tế. Bản `.en` chỉ tiếng Anh, nhanh hơn ~10–15% trên tiếng Anh; dùng model đa ngôn ngữ cho tiếng Việt.

| Công cụ | Để làm gì / vì sao hợp dự án | Giá | Cần phần cứng gì |
|---|---|---|---|
| **whisper.cpp** | Bản port C/C++, không cần Python, có CLI + chế độ server, lượng tử hóa GGML. Tốt nhất trên CPU / Apple Silicon (Metal) / Vulkan. **VPS: dùng `tiny/base/small`** (small ≈ nhanh gấp 7–8 lần thời gian thực trên i7 hiện đại; large-v3 trên CPU chậm gấp ~3 lần thời gian thực — không dùng được cho batch). **PC: build với `-DGGML_CUDA=1` để dùng GPU** | Miễn phí, MIT | CPU: CPU AVX bất kỳ + vài GB RAM. GPU: CUDA 12 + driver |
| **faster-whisper** | Python (CTranslate2), nhanh gấp ~4 lần Whisper gốc, tới 12,5 lần khi chạy batch; INT8 ~3 GB VRAM cho large-v3. Tốt nhất cho pipeline batch viết script trên PC. `pip install faster-whisper` (1.2.1 trên PyPI tính đến 2/11/2026). **PC: `large-v3-turbo` hoặc `large-v3`. VPS CPU: `small`/`base` INT8** | Miễn phí, MIT | Ưu tiên GPU; CPU vẫn chạy được, chậm hơn 5–10 lần |
| **Groq Whisper API** | Host `whisper-large-v3` + `whisper-large-v3-turbo`, endpoint tương thích OpenAI `api.groq.com/openai/v1/audio/transcriptions`, **nhanh gấp 189–299 lần thời gian thực** (audio 10 phút xong trong 2–3 giây). Tốt nhất cho tiếng Việt? **CHƯA xác minh cụ thể** — Whisper large-v3 hỗ trợ 99+ ngôn ngữ gồm tiếng Việt, Groq liệt kê 99+ ngôn ngữ, nhưng không tìm được WER riêng cho tiếng Việt trên model host của Groq. Coi là "lựa chọn cloud rẻ nhất, kiểm chứng trên mẫu tiếng Việt trước" | **$0,111/giờ audio (large-v3), $0,04/giờ audio (turbo)** — tức ~$4 cho 100 giờ với turbo. Free tier: 25 MB/file, 200K ASH / 300 RPM (v3) / 400K ASH (turbo) theo 1 bảng giá tổng hợp; dev tier 100 MB/file. Tính phí tối thiểu 10 giây | Không cần (cloud) |
| **OpenAI Whisper API** | Host `whisper-1`, 25 MB/file, SRT/VTT + timestamp + dịch. ⚠️ **ĐÃ NGỪNG 26/8/2026 — tắt hẳn 26/2/2027**, thay bằng `gpt-4o-transcribe` / `gpt-4o-mini-transcribe` / `gpt-4o-transcribe-diarize` và `/v1/audio/translations`. Thay thế: `gpt-transcribe` ($0,0045/phút) cho file, `gpt-live-transcribe` cho live. **Không xây pipeline mới trên `whisper-1`** | `whisper-1` $0,006/phút ($0,36/giờ); `gpt-transcribe` $0,0045/phút ($0,27/giờ); `gpt-4o-mini-transcribe` ~$0,003/phút | Không cần (cloud) |
| **Subtitle Edit** | Editor phụ đề miễn phí open-source, **300+ định dạng**, waveform/spectrogram căn thời gian, OCR, kiểm tra chính tả, Whisper STT local tích hợp, burn-in qua ffmpeg. **v5.3.0 ra 14/10/2026** (Windows 10 22H2+, macOS 12+, Linux Flatpak). Tốt nhất để sửa tay output Whisper và căn caption từng từ cho Shorts. Ưu tiên Windows; bản cross-platform v5 trên Mac vẫn beta | Miễn phí, GPL/LGPL (1 nguồn nói MIT — wording licence mâu thuẫn; coi là free/open-source, kiểm tra repo) | Cần tải model Whisper; GPU giúp nhanh hơn; ghi nhận tới 16 GB RAM cho model lớn |
| **UVR — Ultimate Vocal Remover v5.6** | App desktop miễn phí open-source (MIT) gồm Demucs v3/v4, MDX-Net, VR Architecture, MDX23C, RoFormer. Tách vocal khỏi nhạc nền — dùng để lấy giọng sạch, bỏ nhạc nền, hoặc tách nhạc nền sạch từ video tham khảo. **Bản ổn định mới nhất v5.6 (26/9/2023); bản beta RoFormer tháng 11/2024–1/2025.** Model khởi đầu: BS-Roformer-Viperx / MDX23C cho vocal, Demucs v4 cho trống/bass. Installer ~1,69 GB (file .exe Windows) | Miễn phí, không giới hạn, local, không cần tài khoản | **Khuyên dùng GPU** (mức sàn được nêu là GTX 1060 6 GB); CPU chạy được nhưng chậm. **Chạy trên PC, không chạy trên VPS.** Lựa chọn CLI: `audio-separator` (cùng model, Python ≥ 3.10 + ffmpeg) |
| **Audacity** | Editor miễn phí open-source: cắt/fade/xuất, edit waveform, kiểm tra loudness. **Bản mới nhất 4.0.1 (30/9/2026).** Tính năng cũ "Vocal Reduction and Isolation" (khử phase kênh giữa) **đã bỏ từ 3.5.0** — thô, chỉ dùng được với vocal đặt cứng ở giữa; dùng UVR thay. Hướng AI mới: plugin Intel OpenVINO Music Separation | Miễn phí, GPL | CPU bất kỳ |
| **ffmpeg — loudness / silence** | Filter có sẵn, không cần cài thêm: `loudnorm` (EBU R128, vd `I=-14:TP=-1.5:LRA=11` cho mục tiêu -14 LUFS của Shorts), `ebur128` (đo loudness), `silencedetect` (tìm khoảng lặng / nhịp hook), `afftdn` (khử nhiễu), `highpass`. Dùng trong pipeline phân tích ở **cả VPS và PC** để chấm video tham khảo một cách khách quan (loudness tích hợp, true peak, khoảng lặng trong 3 giây đầu) | Miễn phí | Chỉ CPU |

### Ghi chú TTS (giọng lồng tiếng cho video faceless)

- **Edge TTS là cloud** (Microsoft, free tier qua gói Python `edge-tts`, không cần GPU) — giọng Việt tốt, nhưng online + giới hạn ToS; giữ làm lựa chọn nhanh, không phải stack local chính.
- **Local, dùng thương mại được:** Piper (GPL-3.0 ở fork OHF-Voice hiện tại; weight MIT cũ vẫn dùng được), Kokoro-82M (Apache 2.0, ~2–3 GB), Qwen3-TTS 0.6B/1.7B (Apache 2.0, ~4 / ~6–8 GB, clone giọng zero-shot từ 3 giây, 10 ngôn ngữ — **lựa chọn clone giọng an toàn thương mại, tháng 11/2026**). Tất cả vừa dễ trên 16 GB.
- **Chỉ phi thương mại:** XTTS-v2 (CPML; Coqui đóng cửa tháng 1/2024, không còn ai bán licence thương mại) và F5-TTS (CC-BY-NC). Dùng test cá nhân được, **không dùng cho kênh kiếm tiền**.
- Chất lượng giọng Việt của Piper/Kokoro/Qwen3-TTS **chưa được kiểm chứng** trong nghiên cứu này — test bằng mẫu tiếng Việt trước khi chốt; Edge TTS / giọng Gemini / ChatGPT vẫn là phương án dự phòng cho lời dẫn tiếng Việt.

## 2.6. Công cụ tải video (thay thế / bổ sung cho yt-dlp)

### yt-dlp — tình trạng hiện tại (tháng 11/2026)

- **Bản ổn định mới nhất: 2026.10.26** (26/10/2026; kiểm tra 12/11/2026). Cần **Python ≥ 3.11** (đã bỏ hỗ trợ 3.10), binary Windows cần Windows 10+.
- **Chặn bot YouTube — lời khuyên cũ nay ĐÃ SAI:** **KHÔNG** ép `player_client=android` nữa. Android hiện cần PO token cho hầu hết format và không dùng được cookie, nên ép nó thường làm tệ hơn. yt-dlp hiện tại cần **JS runtime (Deno ≥ 2.3.0, bật mặc định)** để giải thử thách `n`-signature của YouTube; không có nó sẽ fallback sang ít client hơn và dễ bị challenge/403 hơn. Nếu `-v` cảnh báo format "require a GVS PO Token", cài plugin PO Token provider (vd `bgutil-ytdlp-pot-provider`).
- **Thứ tự làm việc hiện tại (hướng dẫn tháng 10/2026):** (1) cập nhật yt-dlp (`yt-dlp -U`, không dùng apt của distro — gói distro cũ hơn vài tuần); (2) cài Deno; (3) truyền cookie trình duyệt (`--cookies-from-browser chrome`) khi gặp "Sign in to confirm you're not a bot"; (4) chậm lại (`--sleep-requests 2 --sleep-interval 5 --max-sleep-interval 15 --limit-rate 2M`); (5) tránh IP datacentre bị gắn cờ (IP VPS bị gắn cờ nặng — đây là lý do VPS controller hay bị 403; IP dân cư / máy local chạy tốt hơn). **Không** ghim `player_client=` — vòng xoay mặc định của yt-dlp là thứ upstream duy trì; các client ghim (`tv`, `android_vr`) đã bị lấy đi / chỉ còn SABR hoặc cần PO token từ tháng 8/2026.
- **TikTok qua yt-dlp không ổn định:** 1 ghi chú nghiên cứu tháng 6/2026 báo TikTok chặn yt-dlp ngay cả từ IP dân cư (`--impersonate chrome` với curl_cffi cũng không qua). Dùng TikWM (dưới đây) cho TikTok.
- **Facebook Reels qua yt-dlp:** chỉ chạy với post công khai + cookie trong nhiều trường hợp; FDown/SnapSave là phương án web dự phòng.
- ⚠️ **Mâu thuẫn với cách làm hiện tại của dự án:** dự án đang dùng `--extractor-args "youtube:player_client=android"` (kiểm chứng chạy được trên VPS ngày 2026-11-15). Nghiên cứu mới nói cách này đã lỗi thời. **Khuyến nghị: đợt tải sau thử Deno + cookie trước, chỉ dùng android client làm phương án dự phòng.**

### Công cụ thay thế / bổ sung

| Công cụ | Nền tảng | Miễn phí / giới hạn | Watermark | Shorts / TikTok / Reels | Chặn đã biết |
|---|---|---|---|---|---|
| **Cobalt (cobalt.tools)** | YouTube (gồm Shorts & Music), TikTok, Instagram, X, Reddit, Vimeo, Bilibili, 20+ | Miễn phí, open-source, không cần tài khoản, về lý thuyết không quota; instance chính thức **bị rate-limit**; tự host để tải bulk | TikTok không watermark (stream gốc); không gắn thêm watermark | Shorts: về lý thuyết có. TikTok: mạnh. FB: **không nằm trong danh sách nền tảng chính** — dùng FDown/SnapSave | **YouTube không ổn định/bị chặn trên instance công khai** — 1 nguồn nói bị chặn từ 2025 và "vẫn bị chặn năm 2026"; nguồn khác nói lúc được lúc không. **Không dựa vào nó làm tool YouTube chính; tự host (~$2–5/tháng Railway) là cách sửa được nêu.** Không bulk (1 link/lần), tối đa ~1080p ở nhiều video, không playlist |
| **SnapTik (snaptik.app)** | Chỉ TikTok | Miễn phí, có quảng cáo; app có gói $4,99/tuần | MP4 + MP3 không watermark, HD | TikTok: có, tốt nhất trên mobile. Shorts/Reels: không | Trang web nhiều quảng cáo, pop-up/redirect; có domain nhái — dùng đúng domain. Video riêng tư/chỉ bạn bè không tải được |
| **SSSTik / SSSTikTok (ssstik.io)** | Chỉ TikTok | Miễn phí, có quảng cáo, "không giới hạn" | MP4 + MP3 không watermark, HD (theo quảng cáo) | TikTok: có, nhanh nhất trong 1 bảng so sánh (trung bình 8 giây) | Quảng cáo + redirect khi bấm trên một số mirror; "HD/không giới hạn" là marketing cho tới khi kiểm chứng trên file đã tải |
| **TikWM API (tikwm.com / api.tikwmapi.com)** | Chỉ TikTok | **Miễn phí, không cần auth** trên endpoint công khai `POST https://www.tikwm.com/api/`; **giới hạn 1 request/giây** (throttle 1,5 giây); response được cache theo URL. **Lưu ý:** `tikwmapi.com` là API **trả phí riêng** (cần API key, ví dụ 600 req/phút, có quota) — đừng nhầm hai cái | `data.play` / `hdplay` = MP4 không watermark; có cả `wmplay`, cover, title, author, duration | TikTok: có — **lựa chọn lập trình tốt nhất cho pipeline** (chạy được với link ngắn `vm.tiktok.com`; 1 báo cáo nói URL dài `tiktok.com/@user/video/ID` lỗi code=-1 — resolve link ngắn trước). Shorts/Reels: không | Bên thứ ba, độ tin cậy dài hạn không đảm bảo; một số video bị chặn ở cấp tài khoản/IP TikTok sẽ không trả `aweme_detail` (đã gặp với zakszalai). URL CDN hết hạn — tải ngay sau khi lấy |
| **FDown / FDown.net (trước là FBDown)** | Video Facebook + Reels | Miễn phí, không cần đăng ký, chạy trên trình duyệt | Không gắn watermark | **FB Reels: có** — hỗ trợ Reel riêng, đã sửa tháng 3 & 8/2026. Shorts/TikTok: không | Khả năng tương thích link thay đổi theo thời gian khi Facebook đổi; video riêng tư/cần đăng nhập sẽ lỗi. Không nhập mật khẩu/cookie Facebook vào đây |
| **SnapSave (.app / .io — hai đơn vị khác nhau)** | Video Facebook, Reels, Stories, MP3 | Miễn phí, có quảng cáo, không cần tài khoản; chọn chất lượng tới 1080p (một số bảng nói 2K/4K) | Reels không watermark là tính năng chính được quảng cáo | **FB Reels: có.** Shorts/TikTok: không | **Thận trọng:** 1 công cụ quét đánh giá độ tin cậy thấp; có báo cáo về lời mời premium / phí xác minh nhỏ biến thành phí định kỳ. Chỉ dùng luồng tải thường; coi là phương án phụ sau FDown. `.app` ≠ `.io` |
| **Nabfox (nabfox.com)** | YouTube, TikTok, Instagram, Facebook, X, Pinterest | Miễn phí, không cần đăng ký, không cài gì; 1 video/lần; file chuẩn bị xong bị xóa sau ~30 phút | Không gắn watermark | **Shorts: có** (link watch/Shorts/youtu.be, MP4/WebM + âm thanh, MP3, 1080p+ khi có). TikTok/FB: có trong danh sách nhưng chưa có test tỷ lệ thành công độc lập | Không playlist, live, riêng tư, cần đăng nhập, link ngắn `fb.watch`, hoặc Stories. YouTube có thể "từ chối request một lúc" — cùng vấn đề IP datacentre như Cobalt. **Hữu ích cho bulk research: thấp (1 video/lần); tốt làm phương án thủ công cho 1–vài video** |

## Kết luận nhanh cho dự án

1. **Máy local làm trước:** driver NVIDIA mới nhất → Python 3.11/3.12 → Deno → yt-dlp 2026.10.26 → PyTorch cu128/cu130 (kiểm chứng sm_120) → ComfyUI portable → Ollama (Qwen/Llama 8B Q4) → faster-whisper large-v3-turbo → UVR 5.6 → Subtitle Edit 5.3.0. Như vậy đủ: ảnh (SDXL, FLUX FP8), video (Wan 2.2 5B / 14B GGUF Q5 + offload T5, 32 GB RAM), giọng (Kokoro / Qwen3-TTS cho an toàn thương mại; Edge TTS dự phòng tiếng Việt).
2. **VPS giữ nhẹ:** yt-dlp + ffmpeg + whisper.cpp `small` (hoặc API Groq Turbo $0,04/giờ — ~$0,0007/phút, rẻ hơn nhiều so với OpenAI và nhanh gấp 189 lần thời gian thực) + filter ffmpeg `loudnorm/ebur128/silencedetect` để chấm điểm. Không làm việc GPU trên VPS.
3. **Tải video:** yt-dlp vẫn là chính cho YouTube (với Deno + cookie, không ghim `player_client=android`); **TikWM API là đường lập trình cho TikTok** (1 request/giây); **FDown là đường cho FB Reels**, SnapSave dự phòng; Cobalt/Nabfox/SnapTik/SSSTik chỉ là phương án thủ công 1 lần — không cái nào đáng tin cho bulk, và YouTube trên instance công khai của Cobalt bị chặn/không ổn định.
4. **Stickman:** bắt đầu bằng **Manim** (video giải thích) hoặc **Remotion** (video kể chuyện) + 1 rig stickman dùng lại; Pivot Animator cho người không code; StickReel ($19/tháng) nếu muốn tool chuyên dụng có sẵn. AI video (Veo/Kling) chỉ làm B-roll, không giữ nhân vật nhất quán được.

## Những gì chưa xác minh được (ghi rõ để khỏi hiểu lầm)

- Bản stable PyTorch mới nhất ngày 15/11/2026 (nguồn mâu thuẫn giữa 2.7/cu128, 2.10/cu128 và 2.13/cu130) — kiểm tra trên pytorch.org lúc cài.
- Độ chính xác của Groq Whisper **riêng cho tiếng Việt** (không tìm được WER tiếng Việt công bố); chỉ có bằng chứng Whisper large-v3 hỗ trợ 99 ngôn ngữ.
- Chất lượng giọng Việt của TTS local (Piper/Kokoro/Qwen3-TTS) — chưa test.
- Giá chính xác của Kling (Standard được báo $6,99 / $8,80 gia hạn / ~$10/tháng ở các nguồn khác nhau); trang giá cần đăng nhập.
- Watermark bản free của Pika (nguồn mâu thuẫn trực tiếp); free tier của Luma (1 nguồn nói có ~30 lần tạo/tháng, 1 nguồn nói trang vendor không liệt kê gói free); giá Standard của Hailuo (niêm yết $14,99 vs khuyến mãi $7,99–$10,50).
- Watermark của Google Flow ở Việt Nam (1 hướng dẫn giá tháng 11/2026 nói tự gắn trừ khi Ultra 20x; chưa đối chiếu trực tiếp với trang help của Google) — kiểm tra trực tiếp 1 lần trước khi trả tiền gói Pro.
- Giá Stickmotion (chỉ qua bảng so sánh của đối thủ); chất lượng lồng tiếng Việt và điều khoản watermark trial của StickReel; StykAnimate còn quá mới (9/11/2026), chưa có review độc lập.
- Giá Envato Elements / Motion Array (trang vendor chặn/JS, chỉ có nguồn thứ ba); tỷ lệ thành công của SnapTik/SSSTik/FDown/SnapSave/Nabfox (toàn là claim của dịch vụ hoặc bảng tổng hợp, chưa có test độc lập lặp lại); Cobalt YouTube trên instance công khai đúng ngày (nguồn mâu thuẫn: "bị chặn từ 2025" vs "lúc được lúc không").
- Không có test thực tế nào được làm trong nghiên cứu này — tất cả là từ trang vendor và review/bảng tổng hợp tháng 11/2026, không phải từ việc tự tạo video.
