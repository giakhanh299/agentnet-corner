# So sánh giọng đọc tiếng Việt — voice-compare-20261115

Ngày: 2026-11-15. Lý do: người dùng nghe v002 và nói giọng đọc chưa ok — cụ thể là
chỗ ngưng nghỉ (pause) sai. MMS-TTS đơn điệu, ngắt nghỉ máy móc (nói nhanh + khoảng
lặng cố định). Mục tiêu: thử các giọng khác trên PC của người dùng, để người dùng
tự nghe và chọn.

## Câu test (giống nhau cho mọi giọng)

1. Hook: "Mỗi lần đăng nhập, bạn đang dùng mẹo của thủy thủ năm trăm năm trước?"
2. Beat: "Thủy thủ viết tất cả vào sổ nhật ký của tàu, gọi là sổ log."
3. Payoff: "Đăng nhập là ký tên vào sổ log của tàu."

40 từ. Câu 1 không có chữ số (500 viết thành chữ) — giữ nguyên cho mọi giọng.
Khoảng lặng nối câu: 0,6s sau câu 1, 0,8s trước câu payoff (ngắt nghỉ KHÁC NHAU
theo loại câu, không dùng một khoảng cố định — đó chính là lỗi người dùng phàn nàn;
v002 dùng cố định 1,2s).

## Kiểm tra bằng máy (Whisper)

Mỗi file được kiểm tra bằng faster-whisper large-v3 trên PC (CUDA) và đối chiếu
từng từ với 3 câu test. Lưu ý: Whisper chuẩn hoá số thành chữ số ("năm trăm" →
"500") nên 2 từ đó luôn tính là "nghe sai" dù TTS đọc đúng. Tỉ lệ thật = tỉ lệ
báo cáo + 2 từ đó. **Whisper chỉ đo "đọc đúng chữ không". Độ tự nhiên, ngữ điệu,
cảm xúc KHÔNG đo được bằng máy — phải nghe bằng tai người dùng.**

## Kết quả

### D. MMS-TTS với ngắt nghỉ khác nhau (CONTROL) — DÙNG ĐƯỢC ✅

| Hạng mục | Nội dung |
|---|---|
| File | `mms_varied.wav` — 497.452 bytes, 15,54s, PCM 16-bit mono 16 kHz (ffprobe đã kiểm chứng) |
| Engine | MMS-TTS `facebook/mms-tts-vie`, chạy local trên PC, miễn phí (checkpoint MMS là CC-BY-NC — phi thương mại, cần kiểm tra lại trước khi bật kiếm tiền) |
| Giọng | 1 giọng tiếng Việt duy nhất của MMS (nữ, trung tính) |
| Cách chạy | PC, venv ai-stack (transformers 5.23.0, CUDA), tổng hợp từng câu rồi nối |
| Tốc độ | Tổng thể **154 wpm** (40 từ / 15,54s); chỉ tính phần nói 170 wpm; từng câu 183 / 194 / 131 wpm |
| Ngắt nghỉ | 0,6s sau hook, 0,8s trước payoff |
| Whisper | **36/40 = 90,0%** (thật ~95%: 'năm', 'trăm' là lỗi chuẩn hoá số của Whisper; 'log' ×2 nghe thành "đô"/"lon" — lỗi đã biết của MMS, đọc "log" thành "lô") |
| Tổng hợp | 0,9s cho 3 câu |
| Cài đặt | Đã có sẵn trong ai-stack venv, không cần cài thêm |

**Nhận xét thật:** ngắt nghỉ khác nhau giúp cấu trúc rõ ràng hơn v002, nhưng bản
chất giọng MMS vẫn đơn điệu (monotone). Ngắt nghỉ chỉ sửa được "chỗ dừng", không
sửa được "giọng đều đều". Người dùng cần nghe thử và quyết xem chỉ sửa pause
đã đủ chưa.

### B. F5-TTS (local, GPU) — CHẠY ĐƯỢC NHƯNG NÓI SAI TIẾNG VIỆT ❌

| Hạng mục | Nội dung |
|---|---|
| File | `f5tts.wav` — 366.042 bytes, 11,44s; `f5tts_slow.wav` — 473.902 bytes, 14,81s (cả hai PCM 16-bit mono 16 kHz, ffprobe đã kiểm chứng) |
| Engine | F5-TTS v1, model `F5TTS_v1_Base` (SWivid/F5-TTS), chạy local trên PC, miễn phí, CC-BY-NC (phi thương mại) |
| Giọng | Zero-shot clone giọng MMS câu 1 (ref audio = 4,91s đầu của mms_varied.wav + đúng text câu 1). File này chỉ test được **nhịp điệu của F5**, không phải một giọng mới |
| Cách chạy | PC, venv riêng `.venv-f5` (torch 2.11.0+cu128), CLI `f5-tts_infer-cli`, CUDA, ~13s/câu |
| Tốc độ | speed 1.0: tổng thể **210 wpm** (217/248/265 từng câu — quá nhanh so với vùng an toàn 150–165 wpm). speed 0.75: tổng thể **162 wpm** (163/186/198) |
| Ngắt nghỉ | 0,6s / 0,8s như các giọng khác |
| Whisper | speed 1.0: **0/40 = 0,0%**. speed 0.75: **1/40 = 2,5%**. Từng câu (speed 1.0): câu 1 → "Hãy subscribe cho kênh La La School Để không bỏ lỡ những video hấp dẫn"; câu 2 → "Cái gì? Tại vì TTC phí đồ trên FKK A2, ghi bí lệ s log."; câu 3 → "Xin chào và hẹn gặp lại các bạn trong những video tiếp theo." |
| Cài đặt | ~4,5 phút; venv `.venv-f5` 5,5 GB (chủ yếu là torch); model đã có sẵn trong HF cache dùng chung của người dùng (không tải mới); phải tải thêm FFmpeg 8.1 shared DLLs 223 MB để sửa lỗi torchcodec (xem dưới) |

**Nhận xét thật:** F5-TTS base **không nói được tiếng Việt**. Nó không đọc câu
được giao mà nhại lại các câu outro YouTube tiếng Việt đã thuộc lòng ("subscribe
La La School", "hẹn gặp lại trong những video tiếp theo") — kể cả câu 1, dù được
đưa đúng audio + text gốc làm mẫu. Con số wpm vô nghĩa khi từ đọc ra đã sai.
**Không dùng cho sản xuất.** Hai file wav giữ lại làm bằng chứng, không phải mẫu
nghe thử. (Muốn dùng F5 cho tiếng Việt thì cần bản fine-tune tiếng Việt — đó là
một dự án khác, không làm trong lần này.)

Lỗi gặp khi cài F5 (đã sửa, ghi lại để lần sau khỏi mất công):
1. CLI báo `ambiguous option: --output` — phải dùng `--output_dir` + `--output_file`.
2. `UnicodeEncodeError: 'charmap' codec can't encode character '\u1ed7'` — CLI in
   text Việt ra console cp1252; sửa bằng `[Console]::OutputEncoding = UTF8` +
   `$env:PYTHONIOENCODING = "utf-8"` trong file .ps1.
3. `OSError: Could not load this library: ...\torchcodec\libtorchcodec_core4.dll` —
   wheel torchcodec 0.17.0+cpu trên Windows **không kèm DLL FFmpeg** (avcodec…),
   mà torchaudio 2.11 bắt buộc phải có torchcodec (không có fallback soundfile).
   Sửa bằng cách tải FFmpeg 8.1 shared build (BtbN, 85,5 MB) về
   `ai-stack\ffmpeg-shared\` và thêm thư mục `bin` vào PATH trước khi chạy
   (xem `voice_ffmpeg_shared.ps1`). Gỡ torchcodec rồi cài lại không sửa được.

### A. Edge TTS (Microsoft neural, miễn phí) — THẤT BẠI (bị chặn) ❌

| Hạng mục | Nội dung |
|---|---|
| File | Không có file mẫu |
| Engine | Edge TTS (edge-tts 7.3.1), miễn phí, không cần key. Giọng `vi-VN-HoaiMyNeural` (nữ) và `vi-VN-NamMinhNeural` (nam) — đã kiểm chứng là tồn tại |
| Cách chạy | PC, venv ai-stack (mạng nhà, không qua proxy VPS) |
| Lỗi chính xác | `edge_tts.exceptions.NoAudioReceived: No audio was received.` Server gửi `turn.start` + `response` (nhận request) rồi đóng kết nối lặng lẽ — 0 byte audio, không có `turn.end`, không báo lỗi. Lúc đầu chạy được 2 lần, sau đó bắt đầu bị chặn → nghi là throttle theo IP/thời gian. Thử lại sau ~1 giờ vẫn lỗi y hệt. |
| Lưu ý thêm | edge-tts 7.3.1 KHÔNG ăn SSML: nó escape SSML rồi bọc thêm thẻ `<speak>` của nó, nên giọng đọc luôn cả thẻ XML (Whisper kiểm chứng trên file mp3 "thành công": "...Speak version... HTTP 2.2... www.vw3.org..."). Text thường + có dấu cũng lỗi `NoAudioReceived`. |
| Cài đặt | edge-tts 7.3.1, nhỏ, vài phút |

**Nhận xét thật:** Edge vẫn là giọng miễn phí tự nhiên nhất nếu chạy được (giọng
neural thật + điều khiển pause bằng SSML), nhưng hiện tại endpoint Microsoft
đang chặn IP này. Đáng thử lại vào một ngày khác (throttle có thể tự hết sau
một khoảng thời gian không rõ). Trên VPS thì Edge đã bị chặn từ trước (proxy
giết WebSocket) nên chỉ thử được trên PC.

### C. Kokoro-82M (local, nhỏ) — THẤT BẠI (không có tiếng Việt) ❌

| Hạng mục | Nội dung |
|---|---|
| File | Không có file mẫu |
| Engine | Kokoro-82M 0.9.4, chạy local trên PC, miễn phí, Apache 2.0 |
| Lỗi chính xác | Không có giọng tiếng Việt. Danh sách voice chính thức của Kokoro-82M (37 voice) chỉ có: tiếng Anh Mỹ, Anh Anh, Tây Ban Nha, Pháp, Hindi, Ý, Nhật, Bồ Đào Nha, Trung — **không có voice 'v' (Vietnamese)**. Đã kiểm chứng bằng cách liệt kê file voice trên Hugging Face (`hexgrad/Kokoro-82M`, thư mục `voices/`). Vì không có voice nên không thử tổng hợp. |
| Cài đặt | venv riêng `.venv-kokoro` (torch 2.11.0+cu128), ~3,5 phút; venv 4,8 GB |

## Không test

- **FPT.AI / Vbee** — cần người dùng đăng ký tài khoản (không tự đăng ký).
- **ElevenLabs** — trả phí (không chi tiền khi chưa được duyệt).
- **Qwen3-TTS** — ghi chú trong codexreply.md là TTS an toàn thương mại, chưa test.
  Có thể là ứng viên cho lần sau.

## Kết luận & đề xuất

1. **Mẫu duy nhất dùng được: `mms_varied.wav`.** Ngắt nghỉ 0,6s/0,8s đã sửa được
   cấu trúc dừng (lỗi chính người dùng phàn nàn), nhưng giọng MMS vẫn đơn điệu.
   Người dùng hãy nghe thử file này trước.
2. Nếu nghe xong vẫn thấy giọng chưa đủ hay, các hướng tiếp theo theo thứ tự:
   (a) thử lại Edge TTS vào ngày khác (throttle có thể hết — đây vẫn là giọng
   miễn phí tự nhiên nhất); (b) FPT.AI/Vbee — cần người dùng đăng ký;
   (c) ElevenLabs — trả phí, cần người dùng duyệt.
3. **F5-TTS base và Kokoro là ngõ cụt cho tiếng Việt** với setup hiện tại — đừng
   đốt thêm thời gian vào hai hướng này (F5 cần bản fine-tune tiếng Việt;
   Kokoro không có voice tiếng Việt).

## File trong thư mục này (VPS)

- `mms_varied.wav`, `f5tts.wav`, `f5tts_slow.wav` — 3 file mẫu (ffprobe đã kiểm chứng, xem bảng trên)
- `voice_compare.md` — file này
- Script chạy trên PC (đều ở đây, đã scp lên PC khi dùng):
  `voice_edge_install.ps1`, `voice_edge_synth.py/.ps1`, `voice_edge_diag*.py/.ps1`,
  `voice_edge_raw*.py/.ps1`, `voice_mms_varied.py/.ps1`, `voice_f5_install.ps1`,
  `voice_f5_synth.py/.ps1`, `voice_f5_slow_and_check.ps1`, `voice_whisper_check.py`,
  `voice_torchcodec_fix*.ps1`, `voice_ffmpeg_shared.ps1`, `voice_kokoro_install.ps1`,
  `voice_kokoro_probe.py/.ps1`, `voice_f5_diag.ps1`
- Trên PC, file nằm ở `C:\Users\w\agentnet-corner\ai-stack\voice_compare\`
  (giữ lại cả file câu đơn `f5_s1/s2/s3.wav`, `f5tts_slow_s1/s2/s3.wav`,
  `f5_ref_s1.wav` và log `C:\Users\w\voice_*.log` làm bằng chứng).
- Dung lượng mới trên PC: `.venv-f5` 5,5 GB + `.venv-kokoro` 4,8 GB +
  `ffmpeg-shared` 223 MB (+ file zip 85,5 MB). `.venv-kokoro` có thể xoá để
  lấy lại ~4,8 GB vì Kokoro đã xác định không dùng được.
