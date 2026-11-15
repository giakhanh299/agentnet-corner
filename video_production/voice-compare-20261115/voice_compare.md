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

---

# Vòng 2 — chỉnh tốc độ + ngưng nghỉ MMS (2026-11-15, sau phán quyết của người dùng)

**Phán quyết của người dùng (~18:28, sau khi nghe `mms_varied.wav`): giọng MMS
hiện tại HAY — giữ nguyên giọng, KHÔNG đổi giọng nữa. Chỉ có ngưng nghỉ và tốc
độ là chưa ok.** Vòng 2 sửa đúng hai thứ đó: chậm tốc độ NÓI TRONG câu + ngưng
nghỉ ngắn, đặt đúng chỗ. Cùng 3 câu test như vòng 1 (40 từ).

## Phát hiện kỹ thuật: không có `length_scale`, có `speaking_rate`

- transformers 5.23.0, `VitsModel.forward` KHÔNG có tham số `length_scale`
  (kiểm chứng bằng `inspect.signature`: các tham số là `input_ids,
  attention_mask, speaker_id, output_attentions, output_hidden_states,
  return_dict, labels, speaking_rate, kwargs`; `VitsConfig.length_scale`
  cũng không tồn tại).
- Thay vào đó có **`speaking_rate`** (mặc định 1.0) — **nhỏ hơn = nói chậm
  hơn**, đã kiểm chứng bằng probe (câu 1, 15 từ): rate 1.0 → 5,49s / 164
  từ/phút; rate 0.75 → 6,66s / 135 từ/phút; rate 1.25 → 4,59s / 196
  từ/phút. Quy đổi tương đương length_scale: 1.2 ≈ speaking_rate 0.83;
  1.35 ≈ 0.74. **Không cần fallback atempo** (ffmpeg) — `speaking_rate`
  chạy được, và atempo có thể làm giọng nghe hơi "xử lý" nên không dùng.
- Không tạo venv mới, không đăng ký, không trả phí. Chạy trong venv
  ai-stack có sẵn.

## Ngưng nghỉ dùng cho vòng 2 (giống nhau cho mọi biến thể)

Ba con số trong nhiệm vụ được map vào ba điểm dừng thực sự có: **0,3s sau
hook** (câu 1 → câu 2), **0,4s micro-pause tại dấu phẩy trong câu 2** (câu 2
tách thành 2 mệnh đề để tổng hợp riêng: "Thủy thủ viết tất cả vào sổ nhật
ký của tàu," + "gọi là sổ log."), **0,6s trước câu payoff** (câu 2 → câu 3).
Tổng ngưng nghỉ 1,3s (vòng 1 là 1,4s với 0,6s/0,8s; v002 là 2,4s với 1,2s
cố định). Biến thể D dùng micro-pause 0,25s tại dấu phẩy thay vì 0,4s.

## Kết quả vòng 2 (đối chiếu vòng 1: `mms_varied.wav` — từng câu 183/194/131
từ/phút, tổng thể 154, chỉ tính phần nói 170, Whisper 36/40 = 90,0%)

| Biến thể | speaking_rate | Từng câu (từ/phút) | Tổng thể | Chỉ phần nói | Whisper |
|---|---|---|---|---|---|
| A `mms_slow12.wav` (17,76s, 568.492 byte) | 0.83 (= length_scale 1.2) | 161 / 132 / 149 | 135 | 146 | **35/40 = 87,5%** |
| B `mms_slow135.wav` (19,52s, 624.812 byte) | 0.74 (= length_scale 1.35) | 143 / 124 / 129 | 123 | 132 | 34/40 = 85,0% |
| C `mms_slow09.wav` (16,34s, 522.924 byte) | 0.92 (thêm vào để bracket) | 172 / 148 / 161 | 147 | **160** | 33/40 = 82,5% |
| D `mms_clause.wav` (15,41s, 493.036 byte) | 1.0 + micro-pause 0,25s (đối chứng) | 180 / 166 / 157 | 156 | 168 | 33/40 = 82,5% |

Tất cả 4 file PCM 16-bit mono 16 kHz, ffprobe đã kiểm chứng trên VPS.
Whisper: faster-whisper large-v3 trên PC, như vòng 1.

**Đọc số thật:**
- **Độ đều (chênh lệch tốc độ giữa các câu):** vòng 1 chênh 63 từ/phút
  (131–194). Vòng 2: B đều nhất (19; 124–143), rồi D (23), C (24), A (29).
  Tất cả đều đều hơn hẳn vòng 1 — chậm trong câu đã sửa được nhịp "nói nhanh
  rồi nghỉ dài".
- **Vùng an toàn 150–165 từ/phút (tính theo phần nói):** chỉ **C (160)** nằm
  trong vùng. A (146) hơi dưới, B (132) rõ ràng dưới, D (168) hơi trên.
- **Whisper (chỉ đo đúng chữ):** A tốt nhất vòng 2 (87,5%; thật ~92,5% vì
  'năm'/'trăm' là lỗi chuẩn hoá số của Whisper, còn lại chỉ sai 'gọi' +
  'log'×2). B 85,0% (thật ~90%). C và D 82,5% (thật ~87,5%). Chênh lệch nhỏ,
  không đủ để chọn giọng theo Whisper — **người dùng nghe mới là chuẩn**.
- **"log" vẫn sai ở mọi biến thể** (nghe thành "lon"/"lo") — lỗi MMS đã biết,
  chậm tốc độ không sửa được. Chữ trên màn hình vẫn phải gánh cách viết đúng.
- **"gọi" bị nghe thành "vậy" ở cả 4 biến thể vòng 2** ("Vậy là sổ lon"),
  trong khi vòng 1 nghe đúng "gọi". Nghi ngờ: tách câu 2 tại dấu phẩy khiến
  mệnh đề "gọi là sổ log." tổng hợp riêng, mất ngữ cảnh, nên MMS đọc "gọi"
  khác đi — hoặc chỉ là dao động ngẫu nhiên của model (VITS lấy mẫu
  duration, mỗi lần chạy tốc độ chênh ~10%: câu 1 ở rate 1.0 đo được 164
  từ/phút ở probe nhưng 180 ở biến thể D). Ghi lại để lần sau kiểm tra, không
  kết luận vội.
- **Câu hook luôn nhanh nhất ở mọi biến thể** (161/143/172/180) — model đọc
  câu hỏi nhanh hơn câu kể; chỉnh rate không san bằng hoàn toàn được.

## Đề xuất vòng 2

1. **Nghe `mms_slow09.wav` (C) TRƯỚC** — duy nhất nằm trong vùng an toàn
   (160 từ/phút phần nói), nhịp đều hơn vòng 1 nhiều (148–172 thay vì
   131–194). Đây là ứng viên chính cho pipeline sản xuất.
2. **Nghe `mms_slow12.wav` (A) thứ hai** — chậm hơn, thư thả hơn (146
   từ/phút phần nói), Whisper tốt nhất vòng 2 (87,5%). Nếu người dùng thấy C
   vẫn hơi nhanh thì A là lựa chọn.
3. **B (0.74) có lẽ quá chậm** (123 từ/phút tổng thể) — đều nhất nhưng dễ
   nghe ì. D chứng minh chỉ tách mệnh đề mà không chậm tốc độ thì không sửa
   được vấn đề (168 từ/phút phần nói, vẫn nhanh).
4. Nếu cả C và A đều chưa vừa tai, hướng tiếp theo: rate ~0.87–0.88 (giữa A
   và C) hoặc rate riêng theo câu (hook chậm hơn, beat giữ nguyên) — model
   cho phép chỉnh từng câu, không cần đổi giọng.

## File vòng 2 trong thư mục này (VPS)

- `mms_slow12.wav`, `mms_slow135.wav`, `mms_slow09.wav`, `mms_clause.wav`
  — 4 file mẫu (ffprobe đã kiểm chứng, xem bảng trên)
- `voice_r2_probe.py/.ps1` — probe `length_scale` (kết quả: không hỗ trợ)
- `voice_r2_probe2.py/.ps1` — probe chiều của `speaking_rate` (nhỏ = chậm)
- `voice_r2_synth.py/.ps1` — tổng hợp 4 biến thể + kiểm Whisper
- Trên PC, file nằm ở `C:\Users\w\agentnet-corner\ai-stack\voice_compare\`
  và log `C:\Users\w\voice_r2_*.log`. Không thêm dung lượng đáng kể trên PC
  (chỉ 4 file wav, reuse venv ai-stack).

---

# Vòng 3 — mở rộng menu giọng (2026-11-15)

**Yêu cầu của người dùng (~18:33): muốn THÊM lựa chọn giọng, ưu tiên theo
thứ tự: (1) TỰ ĐỘNG HOÁ ĐƯỢC — chạy bằng script từ VPS/PC, không bấm tay
trên trình duyệt cho mỗi video; (2) BỀN LÂU — không phải free tier bị bóp
là chết, không phải mẹo một lần; (3) DÙNG ĐƯỢC PC (RTX 5060 Ti, 16 GB
VRAM).** MMS-TTS vẫn là baseline (người dùng thích giọng; chỉnh
`speaking_rate` vòng 2 là hướng sửa chính). Cùng 3 câu test như vòng 1-2
(40 từ). **Không đăng ký, không trả tiền, không tạo tài khoản/key nào** —
phần API chỉ nghiên cứu và ghi rõ người dùng phải làm gì.

## A. Qwen3-TTS (local, GPU) — NGÕ CỤT (bản open chính thức) ❌

- **Kiểm chứng từ README chính thức (QwenLM/Qwen3-TTS, đọc 2026-11-15):**
  bản open hỗ trợ đúng **10 ngôn ngữ** — Chinese, English, Japanese,
  Korean, German, French, Russian, Portuguese, Spanish, Italian.
  **KHÔNG có tiếng Việt.** Không cài gì cả.
- Lưu ý để khỏi nhầm: API **Qwen-Audio 3.0/3.1 host trên Alibaba Cloud**
  có liệt kê tiếng Việt, nhưng đó là sản phẩm cloud trả phí khác, không
  phải bản open weights.
- **Fine-tune cộng đồng `ShiniChien/Qwen3-TTS-12Hz-1.7B-Vietnamese`:**
  0 lượt tải, 0 like, license Apache 2.0 (an toàn thương mại), fine-tune
  2 giai đoạn trên H200 (phonology + style), 30 giọng built-in, dùng qua
  package `qwen_tts` vendored. File `model.safetensors` = **3,83 GB** —
  **VƯỢT ngưỡng 3 GB → KHÔNG tải, chờ phụ huynh duyệt.** Chưa kiểm chứng
  chất lượng (0 lượt tải). Xếp sau F5-ViVoice.

## B. Model TTS tiếng Việt khác trên Hugging Face

| Model | Lượt tải / like | License | Dung lượng | Trạng thái |
|---|---|---|---|---|
| `hynt/F5-TTS-Vietnamese-ViVoice` | **9.569 / 60** | CC-BY-NC-SA-4.0 (phi thương mại) | `model_last.pt` **5,39 GB** | **CHƯA TEST — vượt 3 GB, chờ duyệt** |
| `multilingual-tts/F5-TTS-OpenBible-Vietnamese` | 279 / 0 | CC-BY-SA-4.0 | `model_last.pt` 5,37 GB | Chưa test — vượt 3 GB; dữ liệu Kinh Thánh |
| `thangquang09/parler-tts-vietnamese-v1-stage2` | 312 / 0 | chưa ghi | `model.safetensors` 3,54 GB | Chưa test — vượt 3 GB |
| `dinhthuan/index-tts-2-vietnamese` | 146 / 21 | chưa ghi | chưa đo | Chưa test |
| `multilingual-tts/VITS-OpenBible-Vietnamese` | 42 / 1 | CC-BY-SA-4.0 | `model_last.pth` **998 MB** | **TEST — BỊ CHẶN (xem dưới)** |

**`hynt/F5-TTS-Vietnamese-ViVoice` — ứng viên nâng cấp local số 1 (chờ
duyệt tải):** fine-tune F5-TTS trên **1.000 giờ** tiếng Việt (ViVoice +
VLSP 2021/2022/2023), train 1,5 tháng trên RTX 3090, base F5-TTS_Base.
Dùng lại được `.venv-f5` (F5-TTS đã cài sẵn vòng 1). **License
CC-BY-NC-SA-4.0 = phi thương mại — phải kiểm tra lại trước khi bật kiếm
tiền** (giống vấn đề đã ghi của MMS). Nếu được duyệt tải 5,39 GB, test
ngay bằng CLI F5-TTS có sẵn.

**`multilingual-tts/VITS-OpenBible-Vietnamese` — TEST NHƯNG BỊ CHẶN:**
- Model: Coqui VITS, **grapheme** (`use_phonemes: False` — không cần
  espeak), 2 speaker, 22.050 Hz, train 585 epoch trên dữ liệu OpenBible
  (sách nói Kinh Thánh). File model **998 MB** (< 3 GB) đã tải về PC
  (`ai-stack\voice_compare\vits_openbible\`).
- **Lỗi chặn chính xác:** Coqui TTS **không có wheel cho Windows**
  (kiểm chứng qua PyPI JSON: mọi phiên bản 0.8.0–0.22.0 chỉ có wheel
  `manylinux1_x86_64`). `pip install TTS` trên PC phải build từ source
  và đòi **Microsoft Visual C++ 14.0+** để biên dịch extension
  `monotonic_align` — PC không có MSVC Build Tools (dự án đã quyết
  định không cài Build Tools cho trường hợp `av` trước đây).
- Đã tạo `.venv-vits` (Python 3.10 + torch 2.11.0+cu128, CUDA ok) cho
  lần thử này. File model nằm sẵn trên PC — thử lại được sau này nếu
  cài Build Tools, hoặc chạy trên Linux.
- **Nhận xét thật:** ưu tiên thấp — 42 lượt tải, dữ liệu Kinh Thánh
  (giọng đọc sách trang trọng, chưa chắc hợp Shorts), và Coqui TTS đã
  ngừng phát triển (công ty đóng cửa 2024).

## C. Edge TTS — thử lại: VẪN BỊ CHẶN ❌

- Thử lại **một lần** (~1 giờ sau vòng 1), **text thường** (không SSML —
  edge-tts 7.3.1 đọc luôn thẻ XML): cả HoaiMy và NamMinh đều
  `NoAudioReceived` ngay câu 1, 0 byte. Dừng sau một lần thử, không
  spam Microsoft (theo nhiệm vụ). Script: `voice_r3_edge_retry.py`.
- Kết luận: vẫn bị bóp theo IP/thời gian. Thử lại vào ngày khác.

## D. API — CHỈ NGHIÊN CỨU (không key, không đăng ký)

### D1. Gemini TTS (Google AI Studio API) — ỨNG VIÊN API SỐ 1 ⭐

| Hạng mục | Nội dung (nguồn: docs AI Studio + pricing Google, đọc 2026-11-15) |
|---|---|
| Model | `gemini-3.8-flash-tts` và `gemini-3.8-flash-lite-tts` (GA 2026-09-23) |
| Free tier tiếng Việt | **Có, "Free of charge"** — không cần thẻ. Hạn mức free KHÔNG công bố (chỉ hiện trong AI Studio theo từng project) |
| Giá sau free | Flash **$9/1M audio token (~$0,81/giờ)**, Flash-Lite **$6/1M (~$0,54/giờ)** đến 31/12/2026, **tăng gấp đôi từ 01/01/2027**. Input text $0,50/1M token. 25 token/giây audio |
| Tự động hoá | **Có** — REST `generateContent` tại `generativelanguage.googleapis.com` với API key, hoặc qua Vertex AI. Chạy bằng curl/Python, không cần trình duyệt |
| Điều khiển pause/style | **Không SSML** — style bằng ngôn ngữ tự nhiên trong `speech_metadata.style` (vd "speaking slowly and calmly", tối đa 500 ký tự) + tag inline `<short pause>`, `<sigh>`, `<laugh>`, `<breath>`. Không có nút tốc độ riêng (style chậm → audio dài hơn) |
| Giọng | 30 giọng built-in, giọng nào cũng nói được mọi ngôn ngữ; voice design + nhân bản giọng có sẵn (chặn ở EU/UK/một số bang Mỹ; Việt Nam OK) |
| Tiếng Việt | 101–130 ngôn ngữ; bảng Voice Arena của Google: **tiếng Việt đứng đầu** (Flash-Lite 1156) — lưu ý đây là số của Google, không độc lập |
| Lưu ý | Free tier: Google có thể dùng dữ liệu để cải thiện sản phẩm, **người thật có thể đọc** input/output. Kịch bản video không phải dữ liệu riêng tư nên chấp nhận được |
| Người dùng phải làm | Vào **aistudio.google.com → Get API key** (tài khoản Google giakhanhgcm@gmail.com đã có) → tạo key miễn phí → đưa key cho Torque lưu vào `.env` (không gửi key qua chat) |
| Phán quyết | **API tốt nhất để thử tiếp theo**: miễn phí, không cần thẻ, tự động hoá hoàn toàn, chất lượng tiếng Việt được Google xếp hạng cao nhất |

### D2. FPT.AI TTS v5 — API tiếng Việt tốt nhất (dự phòng số 1)

| Hạng mục | Nội dung (nguồn: docs.fpt.ai pricing + guide, đọc 2026-11-15) |
|---|---|
| Free tier | **100.000 ký tự/tháng miễn phí** (giọng tự nhiên v5; tốc độ chuyển đổi thấp, request xếp hàng, giới hạn request/ngày, không hỗ trợ kỹ thuật). ~100k ký tự ≈ 20.000 từ ≈ **~160 video 45s/tháng** (mỗi video ~600 ký tự) |
| Giá sau free | Gói 500.000 VND → +1,5 triệu ký tự; 1.000.000 VND → +4 triệu; 2.000.000 VND → +10 triệu; 5.000.000 VND → +27 triệu |
| Tự động hoá | **Có** — REST `POST https://api.fpt.ai/hmi/tts/v5` với API key |
| Điều khiển | 9 giọng, 3 vùng (Bắc/Trung/Nam), nam/nữ, **7 mức tốc độ**, từ điển phát âm riêng. SSML: **không xác nhận được** trong tài liệu đã đọc |
| Người dùng phải làm | Đăng ký tại **console.fpt.ai** → tạo Project → tạo API key (không cần thẻ cho free tier) |
| Phán quyết | **Dự phòng API tốt nhất nếu Gemini free tier quá hẹp**: công ty Việt, giọng Việt bản địa, free tier đủ ~160 video/tháng |

### D3. Google Cloud Text-to-Speech — free nhiều nhất, nhưng cần thẻ

| Hạng mục | Nội dung (nguồn: pricing Google Cloud, đọc 2026-11-15) |
|---|---|
| Free tier | **4 triệu ký tự/tháng** Standard + WaveNet, **1 triệu/tháng** Neural2 / Studio / Chirp 3: HD — ≈ 6.600 video 45s/tháng |
| Điều kiện | **BẮT BUỘC bật billing (thẻ tín dụng)** ngay cả khi chỉ dùng free; vượt hạn mức sẽ **tự động tính tiền** |
| Giá sau free | Standard/WaveNet $4/1M ký tự; Neural2 $16/1M; Chirp 3: HD $30/1M; Studio $160/1M |
| Giọng vi-VN | Neural2-A (nữ), Neural2-D (nam), Wavenet-A–D, Chirp3-HD-Achernar (nữ) |
| Tự động hoá | **Có** — REST API với API key/service account. **SSML đầy đủ** (`<break>`, `<prosody>`…) |
| Người dùng phải làm | Tạo Google Cloud project → bật Text-to-Speech API → **bật billing (nhập thẻ)** → tạo API key/service account |
| Phán quyết | Free nhiều nhất, nhưng **rủi ro tự động trừ tiền** — chỉ dùng nếu người dùng chấp nhận nhập thẻ |

### D4. Vbee — giọng Việt tốt, nhưng trả phí từ đầu

| Hạng mục | Nội dung (nguồn: GetApp/Capterra, đọc 2026-11-15) |
|---|---|
| Giọng | 700+ giọng, 50+ ngôn ngữ, **giọng Việt Gen 2** (1.212 giọng Việt theo DubVoice), SSML, chỉnh tốc độ/cao độ/nhấn |
| Tự động hoá | **Có** — REST API (App ID + Token, tạo trong mục API) |
| Giá | Từ **$5,99/tháng** (125k ký tự/tháng, Standard); Special $7,99; VIP $11,99. Có free trial; **hạn mức free plan không công bố** |
| Người dùng phải làm | Đăng ký tại vbee.ai → mục API → tạo application → copy App ID + Token |
| Phán quyết | Lựa chọn Việt tốt, nhưng **trả phí ngay từ đầu và free tier mập mờ** — xếp sau Gemini và FPT.AI |

### D5. ElevenLabs — chưa nghiên cứu sâu

Trả phí, chưa test (ghi chú vòng 1). Có giọng Việt trong thư viện cộng
đồng. Chỉ xem xét nếu cả 4 API trên đều không dùng được.

## Bảng menu tổng (vòng 1–3 + API)

| Giọng | Tự động hoá? | Bền lâu? | Chạy trên PC? | Chi phí | Whisper | Phán quyết |
|---|---|---|---|---|---|---|
| **MMS-TTS (vòng 2 tuning)** | ✅ script Python | ✅ local, không throttle | ✅ | Miễn phí | 87,5% (A) / 82,5% (C) | **BASELINE — sản xuất ngay** |
| Edge TTS | ✅ script, không key | ❌ đang bị bóp IP | ✅ | Miễn phí | — (không có audio) | Thử lại ngày khác |
| F5-TTS base | ✅ local | ❌ không nói được tiếng Việt | ✅ | Miễn phí | 0–2,5% | Ngõ cụt |
| Kokoro-82M | ✅ local | ❌ không có giọng Việt | ✅ | Miễn phí | — | Ngõ cụt |
| Qwen3-TTS (open) | ✅ local | ❌ không có tiếng Việt | ✅ | Miễn phí | — | Ngõ cụt |
| F5-TTS-Vietnamese-ViVoice (hynt) | ✅ local (CLI F5) | ⚠️ chờ test; license CC-BY-NC-SA | ✅ | Miễn phí | chưa test | **Ứng viên nâng cấp local #1 — chờ duyệt tải 5,39 GB** |
| Qwen3-TTS-Vietnamese (ShiniChien) | ✅ local | ⚠️ 0 lượt tải, chưa kiểm chứng | ✅ | Miễn phí | chưa test | Chờ duyệt tải 3,83 GB; Apache 2.0 |
| VITS-OpenBible-Vietnamese | ✅ local (Coqui) | ❌ chặn Windows (cần MSVC) | ⚠️ chặn build | Miễn phí | chưa test | Ưu tiên thấp |
| Parler-TTS Vietnamese | ✅ local | ⚠️ chưa test | ✅ | Miễn phí | chưa test | Chờ duyệt tải 3,54 GB |
| **Gemini TTS (API)** | ✅ REST + key | ⚠️ hạn mức free không công bố | cloud | **Free** → $0,54–0,81/giờ | chưa test | **API #1 — thử ngay khi có key** |
| **FPT.AI TTS v5 (API)** | ✅ REST + key | ✅ | cloud | Free 100k ký tự/tháng | chưa test | **API #2 — dự phòng Việt** |
| Google Cloud TTS (API) | ✅ REST + key | ✅ | cloud | Free 4M ký tự/tháng | chưa test | Chỉ nếu chấp nhận nhập thẻ |
| Vbee (API) | ✅ REST + token | ✅ | cloud | Từ $5,99/tháng | chưa test | Sau Gemini + FPT.AI |
| ElevenLabs (API) | ✅ | ✅ | cloud | Trả phí | chưa test | Chưa nghiên cứu sâu |

## Đề xuất xếp hạng (vòng 3)

1. **MMS-TTS (vòng 2) — sản xuất ngay.** Local, miễn phí, tự động hoá,
   không phụ thuộc mạng/key/throttle; người dùng đã thích giọng.
2. **Gemini TTS free tier — nâng cấp API đầu tiên.** Miễn phí, không cần
   thẻ, tự động hoá bằng REST; người dùng chỉ cần tạo key miễn phí trong
   AI Studio (2 phút, tài khoản Google đã có). Khi có key: test ngay 3
   câu test + đo Whisper, rồi so với MMS.
3. **FPT.AI — dự phòng API tiếng Việt.** Free 100k ký tự/tháng (~160
   video), không cần thẻ; đăng ký console.fpt.ai nếu Gemini free tier
   quá hẹp.
4. **(Chờ duyệt) F5-TTS-Vietnamese-ViVoice — nâng cấp local.** Tải 5,39 GB
   (vượt ngưỡng 3 GB nên chưa tải), test bằng CLI F5-TTS có sẵn trong
   `.venv-f5`. Nhớ kiểm tra license CC-BY-NC-SA trước khi bật kiếm tiền.
5. **Edge TTS — thử lại thỉnh thoảng.** Nếu hết bị bóp thì đây là giọng
   neural miễn phí hay nhất.
6. **Google Cloud TTS — chỉ khi người dùng chấp nhận nhập thẻ.**
7. **Vbee / ElevenLabs — phương án cuối.**

## Ghi chú trung thực

- **Whisper chỉ đo "đọc đúng chữ không". Độ tự nhiên, ngữ điệu, cảm xúc
  KHÔNG đo được bằng máy — người dùng nghe mới là chuẩn.** Mọi phán quyết
  về "giọng hay" đều chờ tai người dùng.
- Các model >3 GB (F5-ViVoice 5,39 GB, Qwen3-Vietnamese 3,83 GB,
  Parler 3,54 GB, F5-OpenBible 5,37 GB) **chưa tải** — cần phụ huynh
  duyệt dung lượng trước khi tải.
- Giá API lấy từ tài liệu công khai ngày 2026-11-15; Google tăng giá TTS
  từ 01/01/2027 (gấp đôi) — kiểm tra lại trước khi cam kết dài hạn.

## File vòng 3 trong thư mục này (VPS)

- `voice_r3_edge_retry.py/.ps1` — thử lại Edge (plain text, 2 giọng)
- `voice_r3_vits_install.ps1` — tạo `.venv-vits` (Python 3.10 + torch
  cu128) + tải model VITS 998 MB về PC
- `voice_r3_vits_synth.py/.ps1` — tổng hợp VITS (chưa chạy được do thiếu
  Coqui TTS)
- `voice_r3_vits_dryrun.ps1` — kiểm tra `pip install TTS` (kết quả:
  không có wheel Windows)
- `voice_r3_disksize.ps1` — đo dung lượng PC
- **Không có file wav mới vòng 3** (Edge không ra audio; VITS bị chặn
  trước khi tổng hợp).
- Trên PC: model VITS ở
  `C:\Users\w\agentnet-corner\ai-stack\voice_compare\vits_openbible\`;
  log `C:\Users\w\voice_r3_*.log`.
- **Dung lượng mới trên PC (đo 2026-11-15):** `.venv-vits` 4,2 GB (mới),
  `.venv-f5` 5,3 GB, `.venv-kokoro` 4,7 GB (xoá vẫn chờ người dùng quyết),
  `.venv-ai` 4,6 GB, `ffmpeg-shared` 0,2 GB, `voice_compare` 0,9 GB
  (gồm model VITS 998 MB). **C: còn trống 45,5 GB.**
