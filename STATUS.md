# STATUS — AgentNet Video Studio (per-feature result log)

> Log kết quả từng tính năng: xong (đúng hay sai) đều ghi vào đây, KHÔNG báo
> riêng cho chủ nữa (chủ dặn 15/11 ~15:50: "ko cần báo tôi — báo lên git hay
> gg driver"). Chủ không can thiệp; cứ bám theo kế hoạch mà làm.
> Mới nhất ở trên cùng. Mỗi mục: tên, thời gian (+07), trạng thái
> (DONE / FAILED / IN PROGRESS / BLOCKED), file/commit chứng minh, kết quả
> thật — thành công hay lỗi (kèm lỗi) đều ghi. Không ghi số không có bằng chứng.
> Bản trên git là bản chính; bản trên Drive là bản sao dự phòng.
> Cập nhật lần cuối: 2026-11-15 ~17:15 +07.

## DONE

### Video #5 (v005) — "Top 5 câu nói huyền thoại của mẹ" Countdown 45s (F3, H02 #69) — DONE + QC-passed 2026-11-15 21:03 +07
- **File:** `video_production/v005-countdown-45s/v005.mp4` — **49,97s,
  1080x1920, 30fps, H.264 + AAC 192k, 14.072.099 byte, sha256
  `0c967c677b23…`** — **-16,42 LUFS** (mục tiêu ~-16), true peak
  **-2,55 dBTP**, LRA 3,70, giọng vào **0,00s**, **155 từ/phút** (chỉ
  phần nói, trong vùng 150–165; tổng thể 143 do pause đếm ngược có
  chủ đích — gốc H02 cũng ~114 tổng thể). **Torque kiểm chứng:**
  ffprobe + sha khớp; xem frame 1s (tiêu đề lớn rõ, dấu đúng, #3 mở
  sẵn, các hàng ẩn "• • •", caption rõ) và 49,5s (end card "SỐ 1 CỦA
  BẠN LÀ CÂU NÀO?" + "Bình luận nhé!" + quote #1 đầy đủ, không cắt).
- **Giọng:** MMS-TTS trên PC (speaking_rate 0.92), Whisper large-v3
  **102/119 = 85,7%**. Run 1 (47,92s, 163 wpm, 89,1%) bị loại vì câu
  #1 cảm xúc chạy 190 wpm; **run 2 dùng** (n1a chậm lại rate 0.80 →
  170 wpm, 49,95s, 155 wpm). File run 1 đã bị ghi đè trên PC, không
  khôi phục được; run 2 là bản chính.
- **Probe từ:** "phăng phắc" nghe thành "phan phát" — GIỮ (phương án
  thay thế tệ hơn: "im re"→"Inge", "nín thinh"→"nứng thiên"); chính
  tả đúng nhờ thẻ danh sách + caption (tiền lệ "log" ở v002). "Tao"
  đúng 100% — giữ. "trĩu" nghe thành "triếu" — ĐỔI thành "nặng nề"
  theo kịch bản (caption dùng "nặng nề"). "Top" nghe thành "Tốc"
  (giới hạn từ mượn của MMS; tiêu đề + caption gánh chính tả).
- **Hình:** 5 ảnh dùng, toàn CC0/CC BY (nguồn đầy đủ trong
  `images/sources.txt`): #5 bàn ăn (Kazz.0, CC BY), #4 người một mình
  trong phòng tối (goblinbox_, CC BY), #3 mẹ + bé nấu ăn (Direct
  Media, CC0), #2 bé trai bên cửa sổ (inclusivesecurity, CC BY), #1
  ảnh gia đình (Family Moments, CC0). 9 ảnh khác bị loại có lý do.
  Toàn 1024px, trừ n2a 679px dọc — crop + upscale ~1,6x, hơi mờ.
- **Nhạc + SFX:** bgm_comedy vol 0.12 (đo được: pause-window -41,6
  dB so với giọng -57,1 dB) + whoosh/pop 0,1s, pop mỗi lần reveal
  (3,48/11,32/19,64/28,50/37,68s), riser 34,60–37,68s vào #1 (đo
  được: -29,2 dB so với giọng -94,6 dB ở cửa sổ không giọng),
  **victory NHẸ ở #1** (cắt 1,5s, vol 0,35 — #1 là cảm xúc, không
  phải trò đùa), laugh sau punchline #4, ding ở CTA. **Laugh ở #2
  BỎ** — sẽ đụng riser + reveal #1; bảo vệ cú lật cảm xúc quan
  trọng hơn. Mix `amix duration=longest`; loudnorm 2-pass +
  `alimiter=limit=0.7:level=false`. Lưu ý: `aresample=48000:ocl=
  stereo` không hỗ trợ trên ffmpeg build này — đã bỏ; amix tự xử
  input mono/stereo lẫn nhau.
- **QC frame (đã xem: 1/5/13/21/30/39/46,5/49,5s):** reveal đúng
  thứ tự, ảnh + caption khớp; 39s: #1 huy hiệu vàng + highlight hổ
  phách, quote đầy đủ 1 dòng. Nhỏ: caption (MarginV 300) sát hàng
  #5 (vd 39s) — vẫn đọc được, không che chữ; lần sau nâng MarginV
  lên ~360. Caption "luận nhé!" trùng chữ end card ở 2s cuối (lỗi
  nhỏ đã có ở v002).
- **Giới hạn trung thực:** chưa ai nghe thật (chỉ Whisper 85,7%) —
  chủ nên nghe 1 lần trước khi đăng, nhất là "phăng phắc" ("phan
  phát"), "Top" ("Tốc"), và câu #1 cảm xúc. SFX không đo riêng từng
  cái được (trùng giọng theo thiết kế); chỉ BGM + riser đo bằng cửa
  sổ năng lượng, còn lại kiểm bằng cấu trúc filter. Ảnh 1024px hơi
  mờ khi crop 9:16 (n2a tệ nhất); ảnh n4 tối. **CHƯA đăng.** Đã gửi
  cho chủ xem trong chat. Video đầu tiên trong lô 3 hoàn thành —
  v003 + v004 vẫn đang làm.

### Vòng 3 — mở rộng menu giọng (tự động hóa + lâu dài + dùng PC) — DONE 2026-11-15 18:48 +07
- **Lý do:** chủ dặn (18:33) chọn thêm lựa chọn, ưu tiên tự động hóa
  được + render dài lâu được, có thể dùng máy của chủ (RTX 5060 Ti,
  16 GB VRAM).
- **Vị trí:** `video_production/voice-compare-20261115/voice_compare.md`
  (435 dòng, 33 KB — Torque kiểm chứng: đủ mục "Vòng 3", bảng menu,
  mục Gemini/FPT.AI) + 5 script vòng 3. Không có mẫu wav mới vòng
  này (Edge không ra tiếng; VITS bị chặn trước khi tổng hợp).
- **Kết quả:**
  - **Qwen3-TTS — NGÕ CỤT (không cần cài):** README chính thức liệt
    kê đúng 10 ngôn ngữ (Trung, Anh, Nhật, Hàn, Đức, Pháp, Nga, Bồ,
    Tây, Ý) — **không có tiếng Việt**. Bản fine-tune cộng đồng
    `ShiniChien/Qwen3-TTS-12Hz-1.7B-Vietnamese` có (Apache 2.0, 30
    giọng, fine-tune trên H200) nhưng 0 lượt tải, checkpoint **3,83
    GB — vượt ngưỡng 3 GB, CHƯA tải**, chờ duyệt.
  - **Model Việt trên HF — ứng viên số 1: `hynt/F5-TTS-Vietnamese-
    ViVoice`** (9.569 lượt tải, 60 like, fine-tune 1.000 giờ ViVoice
    + VLSP 2021–2023, 1,5 tháng trên RTX 3090, tái dùng `.venv-f5`).
    Checkpoint **5,39 GB — CHƯA tải** (vượt ngưỡng), license
    **CC-BY-NC-SA-4.0 (phi thương mại) — phải kiểm lại trước khi
    kiếm tiền**. Các model khác cũng vượt ngưỡng, chưa tải:
    `multilingual-tts/F5-TTS-OpenBible-Vietnamese` (5,37 GB),
    `thangquang09/parler-tts-vietnamese-v1-stage2` (3,54 GB). Model
    duy nhất dưới ngưỡng đã thử: `multilingual-tts/VITS-OpenBible-
    Vietnamese` (998 MB, CC-BY-SA-4.0, 2 giọng) — **BỊ CHẶN:** Coqui
    TTS không có wheel Windows (kiểm chứng qua PyPI JSON — mọi
    phiên bản 0.8.0–0.22.0 chỉ có manylinux); `pip install TTS` đòi
    biên dịch từ source và cần MSVC 14.0+ (PC không có MSVC Build
    Tools). Đã tạo `.venv-vits` (Python 3.10 + torch 2.11 cu128) và
    tải sẵn model về PC để thử sau nếu có Build Tools hoặc chạy
    Linux. Ưu tiên thấp (42 lượt tải, dữ liệu audiobook Kinh Thánh).
  - **Edge TTS thử lại — VẪN BỊ BÓP:** 1 lần thử nhanh, plain text
    (không SSML), cả HoaiMy + NamMinh → `NoAudioReceived`, 0 byte.
    Dừng sau 1 lần, không cố thêm.
  - **API (chỉ nghiên cứu, không key/không đăng ký):**
    - **Gemini TTS (Flash/Lite) — API SỐ 1:** free tier "Free of
      charge", không cần thẻ; trả phí $0,81/giờ Flash / $0,54/giờ
      Flash-Lite tới 31/12/2026, tăng gấp đôi từ 01/01/2027. REST
      `generateContent` + API key, hoàn toàn tự động hóa được.
      Style bằng `speech_metadata` + thẻ `<short pause>` (không
      SSML). 30 giọng, giọng nào cũng nói được mọi ngôn ngữ; tiếng
      Việt được đánh giá cao trên Voice Arena. **Chủ cần: tạo key
      miễn phí tại aistudio.google.com (2 phút, dùng tài khoản
      Google sẵn có).**
    - **FPT.AI TTS v5 — dự phòng Việt số 1:** free 100k ký tự/tháng
      (~160 video/tháng), sau đó gói từ 500k VND. 9 giọng, 3 vùng
      miền, 7 tốc độ, từ điển phát âm. REST + API key. **Chủ cần:
      đăng ký tại console.fpt.ai → tạo project → API key (không
      cần thẻ).**
    - **Google Cloud TTS:** free 4M ký tự/tháng Standard/WaveNet +
      1M Neural2/Chirp 3 HD, SSML đầy đủ, giọng vi-VN — **nhưng bắt
      buộc billing + thẻ tín dụng ngay cả khi dùng free, vượt hạn
      mức tự tính tiền.** Chỉ dùng nếu chủ chấp nhận thẻ.
    - **Vbee:** 700+ giọng, Gen 2 tiếng Việt, SSML, REST API; từ
      $5,99/tháng, có free-trial nhưng hạn mức free không công bố
      — trả phí ngay từ đầu.
- **Xếp hạng đề xuất:** 1) **MMS-TTS (vòng 2) — làm ngay** (local,
  miễn phí, tự động hóa hoàn toàn, chủ đã ưng giọng). 2) **Gemini
  TTS free tier** — nâng cấp API đầu tiên (thử 3 câu ngay khi chủ
  tạo key). 3) **FPT.AI** — dự phòng Việt. 4) **F5-TTS-Vietnamese-
  ViVoice, 5,39 GB — chờ chủ duyệt tải.** 5) Edge — thử lại thỉnh
  thoảng. 6) Cloud TTS — chỉ khi chủ chấp nhận thẻ. 7) Vbee /
  ElevenLabs — cuối cùng.
- **Cần chủ quyết (chưa tự quyết):** duyệt/không duyệt tải 5,39 GB
  `hynt/F5-TTS-Vietnamese-ViVoice` (và tùy chọn 3,83 GB Qwen3-Việt
  sau đó). Không xóa gì trên PC. Đĩa mới: `.venv-vits` 4,2 GB + model
  VITS 998 MB; ổ C: còn 45,5 GB trống. `.venv-kokoro` 4,7 GB vẫn chờ
  chủ quyết xóa.
- **Thời gian:** ~15 phút (18:33–18:48). Menu đã đưa cho chủ chọn
  trong chat (3 lựa chọn).

### Vòng 2 — chỉnh tốc độ + ngưng nghỉ MMS-TTS (giữ nguyên giọng) — DONE 2026-11-15 18:33 +07
- **Lý do:** chủ phán giọng MMS hay, chỉ ngưng nghỉ + tốc độ chưa ok
  (18:28). Không đổi giọng; sửa cách đọc.
- **Phát hiện kỹ thuật:** `length_scale` KHÔNG hỗ trợ trong
  transformers 5.23.0 (kiểm chứng bằng `inspect.signature(VitsModel.
  forward)` — tham số có `speaking_rate`, không có `length_scale`).
  Tương đương là **`speaking_rate`** (mặc định 1.0, thấp hơn = chậm
  hơn): đo thực tế câu 1 — rate 1.0 → 164 từ/phút, 0.75 → 135,
  1.25 → 196. Không cần atempo (sẽ nghe máy móc hơn). Tái dùng venv
  ai-stack trên PC; không venv mới, không đăng ký, không trả tiền.
- **Ngưng nghỉ mới:** 0,3s sau hook, 0,4s micro-pause ở dấu phẩy
  trong câu 2 (tách thành 2 mệnh đề), 0,6s trước payoff — tổng 1,3s
  (vòng 1: 1,4s; v002: 2,4s cố định).
- **4 mẫu (cùng 3 câu vòng 1, 40 từ; đã copy về VPS, ffprobe kiểm
  chứng — Torque kiểm lại: slow09 16,34s/522.924 byte, slow12
  17,76s/568.492 byte, đủ 4 file + mục "Vòng 2" trong
  `voice_compare.md`):**
  - **C — `mms_slow09.wav` (rate 0.92): NGHE TRƯỚC — duy nhất nằm
    trong vùng an toàn 150–165 từ/phút (160, tính riêng phần nói),
    đều nhất sau B. Whisper 33/40 = 82,5%.**
  - **A — `mms_slow12.wav` (rate 0.83): NGHE THỨ HAI — chậm/nhẹ
    nhàng hơn (146 từ/phút phần nói), Whisper tốt nhất vòng 2
    (35/40 = 87,5%). Nếu C vẫn thấy nhanh thì A là lựa chọn.**
  - B — `mms_slow135.wav` (rate 0.74): có lẽ quá chậm (123 từ/phút
    tổng thể). D — `mms_clause.wav` (rate 1.0 + micro-pause 0,25s):
    chứng minh chỉ đổi vị trí ngưng nghỉ không sửa được tốc độ.
- **Độ đều đã sửa:** vòng 1 chênh lệch giữa các câu 63 từ/phút
  (131–194). Vòng 2: B 19, D 23, C 24, A 29 — nhịp nhanh-chậm giật
  cục đã hết. Chênh lệch Whisper giữa các mẫu nhỏ, không phải căn
  cứ chọn (thật ~90–92,5% sau khi trừ lỗi chuẩn hóa số "500" của
  Whisper). "log" vẫn nghe sai thành "lon"/"lo" ở MỌI mẫu — tốc độ
  không sửa được lỗi MMS "log"→"lô" đã biết; chữ trên hình phải
  gánh chính tả.
- **2 lưu ý trung thực:** (1) "gọi" nghe đúng ở vòng 1 nhưng thành
  "vậy" ở cả 4 mẫu vòng 2 — có thể do tách mệnh đề ở dấu phẩy, hoặc
  do model ngẫu nhiên (tốc độ từng lần chạy dao động ~10%: câu 1 ở
  rate 1.0 đo 164 từ/phút lúc probe nhưng 180 ở mẫu D). (2) Câu hook
  nhanh nhất ở mọi mẫu — model đọc câu hỏi nhanh hơn; chỉnh rate
  không san phẳng hoàn toàn.
- **Nếu C và A đều chưa vừa ý:** bước tiếp là rate ở giữa (~0,87–
  0,88) hoặc rate riêng từng câu (hook chậm hơn, beat bình thường)
  — model hỗ trợ chỉnh từng câu, không cần đổi giọng.
- **Thời gian:** ~5 phút (18:28–18:33). 2 mẫu C + A đã gửi cho chủ
  nghe trong chat.

### So sánh giọng đọc thay thế MMS-TTS — DONE (báo cáo) 2026-11-15 18:21 +07
- **Lý do:** chủ nghe v002 và nói giọng đọc chưa ok, ngưng nghỉ chưa
  ok (17:48). Thử 3 giọng khác trên PC với cùng 3 câu (hook + beat +
  payoff v002) để chủ nghe và chọn.
- **Vị trí:** `video_production/voice-compare-20261115/` —
  `voice_compare.md` (báo cáo đầy đủ) + 3 file wav + 27 script (.py/
  .ps1). PC gốc + log: `C:\Users\w\agentnet-corner\ai-stack\
  voice_compare\` và `C:\Users\w\voice_*.log`.
- **Kết quả — chỉ 1/4 giọng cho ra mẫu dùng được:**
  - **MMS-TTS với ngưng nghỉ THAY ĐỔI (mẫu đối chứng) — DÙNG ĐƯỢC:**
    `mms_varied.wav` 15,54s, 497.452 byte (Torque kiểm chứng bằng
    ffprobe: PCM 16-bit mono 16 kHz). Ngưng nghỉ 0,6s sau hook, 0,8s
    trước payoff (không cố định 1,2s như v002). Whisper large-v3 trên
    PC nghe đúng 36/40 từ = 90,0% (thật ~95% — "năm/trăm" là lỗi
    chuẩn hóa số "500" của Whisper; "log"×2 nghe thành "đô"/"lon" —
    lỗi MMS "log"→"lô" đã biết). Tốc độ 154 từ/phút tổng thể
    (183/194/131 từng câu). **Giọng vẫn đơn điệu** — ngưng nghỉ đổi
    chỉ sửa cấu trúc của lời phàn nàn, không sửa được độ đơn điệu.
    Chủ là người duy nhất phán được (Whisper chỉ đo đúng từ, không
    đo độ tự nhiên).
  - **Edge TTS (HoaiMy/NamMinh) — THẤT BẠI (bị chặn/bóp băng
    thông):** `edge_tts.exceptions.NoAudioReceived` — server nhận
    stream (turn.start + response) rồi đóng lặng, 0 byte âm thanh.
    Lúc đầu chạy được 2 lần, sau đó bị bóp. Thử lại ~1 giờ sau vẫn
    lỗi. Ngoài ra edge-tts 7.3.1 KHÔNG làm được SSML (nó escape
    SSML và giọng đọc luôn cả thẻ XML — Whisper xác nhận). Không có
    mẫu nào.
  - **F5-TTS — THẤT BẠI (không nói được tiếng Việt):** cài + chạy
    được (sửa 3 lỗi: `--output` mơ hồ → `--output_dir`/`--output_file`;
    cp1252 crash khi in tiếng Việt → UTF-8; torchcodec 0.17.0 thiếu
    DLL FFmpeg → tải FFmpeg 8.1 shared build 85,5 MB, thêm bin vào
    PATH). Nhưng model gốc KHÔNG nói được tiếng Việt: đưa đúng câu
    1 kèm audio+text tham chiếu, nó đọc "Hãy subscribe cho kênh La
    La School…" — nhại lại câu outro YouTube đã nhớ. Cả 6 file từng
    câu đều 0–5% (tốc độ 1.0: 0/40 = 0,0%, 210 từ/phút quá nhanh;
    tốc độ 0.75: 1/40 = 2,5%, 162 từ/phút). Model đã có sẵn trong
    HF cache của chủ (không tải mới). `f5tts.wav` + `f5tts_slow.wav`
    giữ lại làm bằng chứng, KHÔNG phải mẫu nghe.
  - **Kokoro-82M — THẤT BẠI (không có giọng Việt):** danh sách
    giọng chính thức (37 giọng) không có tiếng Việt (chỉ en-US/GB,
    es, fr, hi, it, ja, pt, zh) — kiểm chứng bằng cách liệt kê
    `hexgrad/Kokoro-82M` voices/ trên HF.
- **Chưa thử:** FPT.AI/Vbee (cần chủ đăng ký tài khoản), ElevenLabs
  (trả phí, cần chủ duyệt), Qwen3-TTS. Không đăng ký, không trả tiền,
  không tạo tài khoản nào. Không đăng/upload gì.
- **Đề xuất:** (1) chủ nghe `mms_varied.wav` và phán xem ngưng nghỉ
  thay đổi có đủ không; (2) nếu không đủ, theo thứ tự: thử lại Edge
  TTS hôm khác (bóp băng thông có thể hết), FPT.AI/Vbee (cần chủ đăng
  ký), ElevenLabs (trả phí). Không tốn thêm thời gian cho F5-TTS gốc
  hay Kokoro với tiếng Việt.
- **Dọn dẹp PC:** `.venv-f5` 5,5 GB + `.venv-kokoro` 4,8 GB +
  `ffmpeg-shared` 223 MB (+ zip 85,5 MB) mới sinh trên PC. `.venv-
  kokoro` xóa được để lấy lại ~4,8 GB (Kokoro đã là ngõ cụt) — đang
  chờ quyết định, chưa xóa. Bản sửa torchcodec (DLL FFmpeg 8.1
  shared trên PATH) tái dùng được cho mọi việc torchaudio sau này
  trên PC — ghi trong `voice_ffmpeg_shared.ps1` + `voice_compare.md`.
- **Thời gian:** ~33 phút (17:48–18:21). Mẫu `mms_varied.wav` đã gửi
  cho chủ nghe trong chat.

### Lô 3 kịch bản (v003 + v004 + v005) — DONE 2026-11-15 17:47 +07
- **Vị trí:** `video_production/scripts-batch-20261115/` — 3 kịch bản +
  `scripts_batch.md` (tóm tắt lô, thứ tự sản xuất, danh sách probe).
  Chỉ kịch bản — chưa sản xuất video, chưa tổng hợp giọng, chưa
  đăng/upload gì. (Torque kiểm chứng: 4 file có đủ; đọc tóm tắt lô +
  phần đầu v003: nguồn có URL đầy đủ.)
- **v003 — #77 (90) thang máy đứt ở tầng 85, F2 Visual Essay, 45s,
  123 từ, ~164 từ/phút:** "Cáp thang máy đứt ở tầng 85 — nhảy lên thì
  sống không?" Nguồn đã kiểm chứng: ScienceABC (rơi từ tầng 20 đã
  ~108 km/h; nhảy Olympic chỉ trừ ~4 m/s; canh thời điểm phải chính
  xác tới mili-giây — coi như không thể; nằm ngửa là tư thế được gợi ý
  nhiều nhất), Otis + AboutElevators (≥4 lớp an toàn độc lập; bộ điều
  tốc tác động ~115% tốc độ định mức; phanh Otis 1852, trình diễn 1854),
  ZestyHabit (nằm ngửa chỉ mang tính lý thuyết, không đảm bảo sống).
  **Con số "72 km/h" của video gốc #77 KHÔNG kiểm chứng được — không
  dùng trong kịch bản**, thay bằng 108 km/h đã kiểm chứng. Năm "1854"
  và tên "Otis" chỉ hiện trên hình, không đọc (bài học MMS v001).
- **v004 — #50 (85) truyện stickman cảm xúc, F7, 50s, 130 từ, ~156
  từ/phút, CÓ giọng kể (không làm bản câm như gốc):** "Ông Tư sửa
  giày — chỉ cần một người dừng lại". Truyện hư cấu hoàn toàn mới
  (ông Tư + bé gái, sạp sửa giày góc phố lúc chạng vạng, đôi giày nhỏ
  không ai nhận + bức vẽ của bé, câu chốt "Chỉ cần một người dừng
  lại.") — khác hẳn nhân vật/bối cảnh/câu chuyện/câu chốt của #50;
  chỉ giữ cơ chế. Không dùng mưa (tránh lặp lại ghế đá mưa của gốc).
  Cảnh báo © của #50 đã tính.
- **v005 — H02 #69 (78) hài, F3 Countdown, 45s, 119 từ, ~159
  từ/phút:** "Top 5 câu nói huyền thoại của mẹ". #2 "Con nhà người
  ta" và #3 "Hồi bằng tuổi mày…" đã kiểm chứng là câu nói quen thuộc
  (BlogRadio, Tripi); thứ hạng là xếp hạng biên tập. #1 là cảm xúc
  ("Mẹ không cần gì đâu, con cứ lo cho con đi.") sau 4 trò đùa — cú
  lật cảm xúc có chủ đích; Victory sting ở #1 dùng NHẸ.
- **Thứ tự sản xuất đề xuất:** v003 → v005 → v004 (rẻ trước; v004 cần
  rig 2 nhân vật + nền góc phố, đắt nhất).
- **Từ cần probe trên PC trước khi sản xuất:** v003 "tám mươi lăm",
  "kẹp chặt ray", "ngửa"; v004 "Tư", "lướt", "sạp"; v005 "phăng phắc",
  "Tao", "trĩu" (đã ghi phương án thay thế trong từng file).
- **Thời gian:** ~5 phút (17:42–17:47). Người dùng chọn lô này lúc
  17:42 và nói "tôi mong chờ kết quả quá" — kịch bản đã gửi cho chủ
  xem trong chat.

### Video #2 (Ep002) — "LOG IN" Visual Essay 45s (F2, #81) — DONE 2026-11-15 17:36 +07
- **File:** `video_production/v002-login-45s/v002.mp4` — 46,8s, 1080x1920
  30fps, H.264 + AAC 192k, 13,7 MB, sha256 `b8b4f7cf18e338ccb645…`
  (Torque kiểm chứng: ffprobe + sha khớp; xem frame 1s và 46,2s: hook
  "MỖI LẦN ĐĂNG NHẬP, BẠN ĐANG DÙNG MẸO CỦA THỦY THỦ 500 NĂM TRƯỚC?"
  to, rõ, đúng dấu, tàu Schotel đủ khung; thẻ cuối "Bạn biết chuyện
  này chưa? Bình luận nhé!" hiện đủ sau khi sửa).
- **Chủ đề:** #81 "WHY DO WE 'LOG IN'?!" (87) — kịch bản gốc 125 từ (F2),
  hook kép → thủy thủ + dây thừng thắt nút → sổ log → đăng nhập máy tính
  → payoff "Đăng nhập là ký tên vào sổ log của tàu" + poll/CTA.
  Nguồn gốc từ đã kiểm chứng: Etymonline ("log") — log-book (1670s) từ
  chip log trên dây log, nút thắt đo tốc độ; nghĩa máy tính "log in" từ
  1963; + Wikipedia "Logbook (nautical)" + Turner Publishing. Lưu ý ghi
  trong script.md: có ý kiến cho rằng "log in" có thể từ "log on" (lệnh
  mainframe) — kịch bản trình bày theo cách hiểu phổ biến, không khẳng
  định tuyệt đối.
- **Đã đo:** **-16,39 LUFS** (đúng mục tiêu — lỗi -17,40 của Ep001 đã
  tránh được, không cần pass loudnorm thêm), true peak **-2,42 dBTP**,
  LRA 3,80, giọng bắt đầu **0,00s** (hết dead air 1,49s của bản gốc),
  **160 từ/phút** (125 từ / 46,8s, trong vùng an toàn). Phụ đề 33 events,
  khớp kịch bản 125/125 từ; 10 frame đã xem (`qc.md`).
- **Giọng MMS-TTS TRÊN PC** (CUDA, tổng hợp 0,9s): kiểm bằng
  faster-whisper large-v3 trên PC: **113/123 = 91,9%** từ nghe đúng
  (v001 chỉ ~70% bằng Whisper Base trên VPS). Tốc độ từng câu 168–200
  từ/phút, nối bằng khoảng nghỉ 1,2s kéo về 160 tổng. 2 vòng thử trên PC
  (13 câu) chốt từ rủi ro: "Ngày xưa" ổn, "buộc"/"đếm"/"hải lý" ổn,
  "cột" tệ hơn "buộc" (nghe "cục") — loại; câu beat-2 cũ hỏng ổn định
  (71% hai lần) đã viết lại. **Giới hạn MMS: "log" đọc thành "lô/lố"**
  (rớt phụ âm cuối; viết "lốc" cũng không sửa được) — giữ nguyên trong
  giọng nói, chữ trên màn hình ("CHIP LOG", "SỔ LOG") giữ đúng chính tả.
- **Nhạc + SFX — video đầu tiên CÓ nhạc:** `bgm_calm.ogg` volume 0,12
  (đo ở khoảng nghỉ -41,1 dB, thấp hơn giọng ~22 dB) + whoosh + pop ở
  0,1s, ding ở 6,68/18,34/30,00s, camera_click ở 18,34s, boom (vol 0,8)
  ở 41,12s — toàn bộ CC0 từ thư viện Core_SFX. SFX kiểm chứng bằng cấu
  trúc filtergraph + đo khoảng nghỉ của nhạc; độ nghe của từng SFX riêng
  không tách đo được (chúng trùng với giọng theo thiết kế) — ghi thật
  trong qc.md.
- **Hình:** 4 ảnh đã dùng, toàn CC0/CC BY (Schotel "Ships in a Turbulent
  Sea" 1826 CC0 Rijksmuseum; dây thừng hoàng hôn CC0; trang sổ log thật
  1944 CC BY PhillipC; màn hình đăng nhập Facebook CC BY Homedust);
  4 ảnh khác tải về rồi loại có lý do. Tất cả 1024px (Openverse
  editor_1024) — hơi mềm khi crop 9:16, như v001, chấp nhận được.
- **Lỗi đã sửa:** thẻ cuối bị cắt ở build 1 (24 ký tự, fontsize 88 tràn
  1080px) → giảm fontsize 64, encode lại, kiểm lại ở 45,5s + 46,2s:
  hiện đủ. Mix treo >4 phút lần đầu — `apad` trên track giọng +
  `amix duration=first` không bao giờ kết thúc → bỏ `apad`, dùng
  `duration=longest`; mix xong trong 4,7s.
- **Giới hạn thật:** chưa ai nghe bằng tai (chỉ Whisper 91,9%) — chủ nên
  nghe một lần trước khi đăng, nhất là "log" ("lô") và "Bạn gõ mật khẩu";
  độ nghe từng SFX chưa đo riêng; ảnh 1024px hơi mềm; phụ đề "luận nhé!"
  trùng chữ thẻ cuối trong 2s cuối (thừa nhỏ như v001). PC chạy tốt suốt
  (SSH, TTS + Whisper ~10s/lần); không cần fallback VPS.
- **Chưa đăng/upload đâu cả.** Thời gian: ~21 phút (17:15–17:36) — nhanh
  gấp ~3 lần v001 (65 phút) nhờ TTS + Whisper trên PC.
- **Thay đổi hệ thống:** `auto_push.sh` nay thêm `video_production/` vào
  danh sách git-add (chỉ file text — mp4/wav/jpg vẫn bị .gitignore chặn);
  lần đầu tiên file sản xuất (script.md, qc.md, captions) được đưa lên
  git cùng đợt push này.

### AI stack local trên PC (PyTorch cu128 + faster-whisper + TTS Việt) — DONE 2026-11-15 17:15 +07
- **Bắt đầu:** 2026-11-15 ~17:03 +07. Tiếp sau test render Manim (DONE).
- **Nội dung:** kiểm tra driver NVIDIA (cần ≥572.60, nếu thấp hơn thì dừng
  và báo, không tự cập nhật driver) → cài PyTorch ≥2.7.0 cu128 vào venv
  riêng (không chạm hệ Python của chủ) → faster-whisper large-v3, thử
  với voice.wav Ep001 → TTS Việt local (MMS-TTS). Ghi PC_AI_SETUP.md.
- **Kết quả: CHẠY ĐƯỢC, cả 3 công cụ đã kiểm chứng bằng chạy thật.**
  - Driver NVIDIA **610.88** (cần ≥572.60 — đạt, không cần làm gì),
    RTX 5060 Ti 16 GB VRAM.
  - **PyTorch 2.11.0+cu128, CUDA 12.8**: `cuda.is_available()` True,
    capability (12, 0) = sm_120, matmul 512×512 trên CUDA ok. Cài ~100s
    (torch có sẵn trong pip cache của PC).
  - **faster-whisper 1.2.1, large-v3** (ctranslate2 4.9.0, av ghim 14.0.0):
    voice.wav Ep001 (48,8s) nghe xong trong **4,7s (RTF 0,10x — nhanh
    gấp ~10 lần VPS)**, khớp kịch bản **130/137 = 94,9%**. Cùng file trên
    VPS whisper.cpp Base: 113/137 = 82,5% ở ~1x real-time.
  - **MMS-TTS Việt** (transformers 5.23.0, mms-tts-vie trên CUDA): 3 câu
    (55 từ, 19,6s audio) tổng hợp trong **0,9s** (VPS mất ~58s cho cả
    giọng Ep001). Whisper tự kiểm output: **52/55 = 94,5%** (trượt: lả,
    cày, tiếp — đúng các từ yếu đã biết của MMS). File test đã copy về
    VPS: `stickman-shorts/test_audio/pc_tts_test.wav` (21,1s, 16 kHz
    mono — Torque kiểm chứng ffprobe: 21,116s, 675.756 byte).
- **Venv riêng:** `C:\Users\w\agentnet-corner\ai-stack\.venv-ai`
  (Python 3.12.10) — tách khỏi `.venv-win` và hệ Python của chủ; không
  chạm gì của chủ. Thư mục ai-stack ~4,7 GB; ổ C: còn trống 61,8 GB.
- **Model đã có sẵn trong cache chung của chủ** (`HF_HOME` =
  `D:\0.1_FACE_BOOK\DUNG_CHUNG\MODELS\HF_CACHE`) — không tải gì,
  không ghi gì vào cache; large-v3 load ~3s, MMS-TTS ~13,7s. Venv phụ
  thuộc cache này — không dời/xóa.
- **Lỗi đã sửa:** faster-whisper 1.2.1 + av 19 hỏng (ghim `av==14.0.0`);
  ctranslate2 không tìm thấy cuBLAS (torch 2.11 để DLL trong
  `site-packages\torch\lib` — phải thêm vào `$env:PATH` trước khi chạy
  python); console cp1252 crash khi in tiếng Việt (reconfigure utf-8).
- **Hồ sơ:** `stickman-shorts/PC_AI_SETUP.md` (131 dòng) + 9 script
  (`ai_*.ps1` / `ai_*.py`).
- **Giới hạn thật:** chưa ai nghe output TTS của PC bằng tai (chỉ kiểm
  Whisper 94,5%); câu hook MMS chạy 195 từ/phút (trên vùng an toàn
  150–165); đường truyền file-path của faster-whisper chưa thử sau khi
  ghim av (khuyên dùng đường numpy-array). Chưa làm: không có service
  nền, không Ollama/ComfyUI, large-v3-turbo chưa thử (không cần ở
  RTF 0,10x), chưa render tập thật trên PC, `assemble.py --srt` vẫn
  chưa thử trên PC.
- **Thời gian:** ~12 phút làm việc thật (17:03–17:15), không bị chặn.


### PC Windows — test render stickman qua SSH — DONE 2026-11-15 17:02 +07
- **Kết quả: CHẠY ĐƯỢC.** Demo render trên PC **4,58s** (VPS: 17,2s lạnh /
  8,6s ấm). File `StickmanScene-pc.mp4` 263.107 byte, h264 1080x1920
  30fps 5,000s (Torque kiểm chứng: ffprobe khớp; xem frame 1s và 4s:
  dáng đi + vẫy tay + thẻ "TÂM SỰ NGƯỜI QUE" đúng dấu, nội dung giống
  hệt bản render trên VPS).
- **Môi trường trên PC** (DESKTOP-01O3HNF, 100.101.158.71): Python **3.12.10**
  đã có sẵn (lệnh `python` trần là 3.10.11 — KHÔNG dùng; dùng `py -3.12`
  hoặc đường dẫn đầy đủ), ffmpeg 8.1.2 + git 2.54.0 đã có sẵn, không cần
  cài. Repo `C:\Users\w\agentnet-corner` (HEAD 58b70a2), venv
  `.venv-win` (manim 0.22.1). Font Be Vietnam Pro đã cài + nhìn thấy
  được — chỉ thấy sau khi thêm entry HKLM (HKCU + copy file chưa đủ).
- **Hồ sơ:** `stickman-shorts/PC_SETUP.md` + 5 script `.ps1` dùng lại
  được (commit f89d9c5); render + frame đã copy về VPS
  (`test_frames/pc/`).
- **Sự cố đã sửa:** quoting lồng nhau của `-Command` hỏng 2 lần → chuyển
  sang file `.ps1` scp lên PC (mẫu bền vững); lần thử venv+pip đầu treo
  **62 phút** (ssh exit 255) — còn sót 1 `python.exe` nhàn (PID 4368) +
  `powershell.exe` (PID 38548) từ 15:49, ~0 CPU, không rõ là của session
  treo hay REPL của chủ — **để nguyên, không chạm**; script `Start-Process`
  detached chết im → chạy foreground + `< NUL` + transcript (pip xong
  trong 68s); render script gọi nhầm `ffmpeg` thay vì `ffprobe`.
- **Không chạm** hệ Python riêng của chủ trên PC (3.10/3.14,
  `D:\02_CONG_CU\youtube-reup-pipeline\venv`). Log trên PC:
  `C:\Users\w\pip_install.log`, `font_install.log`, `font_fix.log`,
  `render_demo.log`.
- **Chưa thử trên PC:** `render_all.sh`, `assemble.py --srt`, render tập
  thật. Bước tiếp theo (AI stack local) chưa bắt đầu.


### Thư viện Core_SFX (18 SFX + 4 nhạc nền) — DONE 2026-11-15 16:21 +07
- **Vị trí:** `stickman-shorts/src/assets/audio/` — `sfx/` 18 file + `music/`
  4 file, tổng **7,0 MB** (sfx 808 KB, nhạc 6,0 MB), định dạng Ogg Vorbis
  q5 48 kHz; `sfx_manifest.json` (22 entries) + `sfx_report.md` + script
  tải/chuẩn hóa (`search_openverse.py`, `download_sfx.py`,
  `normalize_sfx.py`, `build_manifest.py`).
- **Nguồn:** toàn bộ **CC0 1.0** (public domain, dùng thương mại được,
  không cần ghi nguồn) — file preview HQ của Freesound tìm qua Openverse
  API (`license=cc0`); mỗi entry có source URL + creator + license.
- **Đã đo (Torque kiểm chứng):** 18 sfx + 4 nhạc đúng số lượng; whoosh
  0,45s, bgm_calm 95,7s khớp manifest; tích hợp **-19,8 đến -21,27 LUFS**,
  true peak **≤ -1,2 dBTP**; git KHÔNG ignore `.ogg` (check-ignore exit 1)
  nên thư viện vào được git (không cần sửa .gitignore).
- **Lỗi đã sửa:** Vorbis overshoot đẩy TP lên trên -1 dBTP → limiter hạ
  0,85; ffmpeg loudnorm tự upsample 11 file lên 192 kHz → thêm
  `aresample=48000`, encode lại toàn bộ. Cắt bớt: boom 3,94s→2,5s,
  footsteps/crickets 17s→4s loop, bgm_upbeat 160s→90s; fade 2s cho nhạc.
- **Giới hạn thật:** chưa ai nghe bằng tai (chỉ đo bằng ffprobe/loudnorm);
  `boing` từ nguồn rất nhỏ (max -25 dB, tăng ~+25 dB) nên có thể nghe
  thấy noise floor khi phát riêng — cần nghe thử cả 22 file trước khi
  dùng cho video đăng. File là preview HQ mp3 của Freesound, không phải
  WAV gốc (cần API key Freesound mới lấy được). Mixkit không dùng được
  từ VPS này (URL asset trả 403 dù có Referer + UA trình duyệt).
- **Chưa dùng trong video nào.** Tập sau dùng `--music` với file `.ogg`.

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

- **VPS bị thay lần 4 trong ngày 2026-11-15 ~16:50 +07** (trước đó ~11:10,
  ~12:50, ~14:50). Watchdog 16:53 tự chữa đúng thiết kế: tạo lại unit
  systemd đã bị xóa + restart gateway (pid 1857), /health ok; Torque đưa
  gateway về dưới systemd (active). Các subagent đang chạy (test PC,
  Core_SFX) có thể bị gián đoạn bởi lần thay này — kiểm tra lại khi nhận
  báo cáo.

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
- `STATUS.md` (bản này) — Drive file id: `1NO2YbnSivxUuJpS1Mk-ZlunRZ-4ev7Qb`
  (upload 2026-11-15 ~21:04 +07 — bản mới nhất, có v005 DONE; các bản
  cũ `1gpLAunMiYnQhwknN-QNgmFlBYfrOUXCj` (15:55),
  `1lAPg14W9pW43zq6aQCyWEIahxgbI6MKc` (16:06),
  `1bDWx5BH9HUeomr1d9PyIV0_9fIXskNNk` (16:22),
  `1BK-Z-i-dpdvjPTk4Gut92ixHw7DOwUxS` (17:03),
  `1892dptIIhhY5DIkyHEoW9o7iVk5N_XIH` (17:15),
  `13LCpNYKXjKu2WQ6bebXS_4SCiSLtmzdz` (17:38),
  `1Z6wmJj9G63AGYU7skALHfTyaE5Fodx0k` (17:48),
  `13PPFSztw50aqrQxndmon3hiGV_mCgTCX` (18:21),
  `1xlYJmXcMkUYTm1W_H0B2Oqnf6MX2IAkU` (18:33) và
  `1DOow24syLHrfa5iphufUXCJmVSQilVd-` (18:48) đã lỗi thời, giữ lại làm
  bản sao cũ, không xóa theo quy tắc không xóa dữ liệu Drive)
- `HANDOFF.md` — Drive file id: `16lcqICKbi8ZvurA-T4O4_eXhe6ZoKaZ7`
  (upload 2026-11-15 ~15:55 +07)
- Video thành phẩm (bản sao dự phòng, không lên git):
  - `v001.mp4` (Video #1) — Drive file id: `1oVxOPRVSl5HmjdzI47RQiVGKHotAdCxn`
  - `ep001-cam-dau-lam-viec.mp4` (Ep001) — Drive file id: `152--2bfxwsQIjKi_5bCmKbO3V8jsdu9f`
  - `v002-login-45s.mp4` (Video #2 / Ep002) — Drive file id: `1m_c6zADoYLb3zxvg-dnTHGRTZrJiX3mq`
  - `v005.mp4` (Video #5) — Drive file id: `1D9ZG8q4C0odQkdXp1y0-09YnAEEpzVb4`
- Lưu ý: bản trên git là bản chính, mới nhất.
