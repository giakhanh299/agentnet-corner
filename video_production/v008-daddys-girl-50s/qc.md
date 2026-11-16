# QC — v008 "Con gái của bố" (F7 stickman, C02 #47 79)

**Kết luận: PASS.** Video hoàn chỉnh, đúng spec. Chưa đăng đâu cả.

## File

- `v008.mp4` — **48.36s**, 1080x1920, 30fps, H.264 + AAC 192k stereo 48kHz,
  **2,419,585 bytes**
- sha256: `4fcd530b3e1e632badf3a1114fedb3dd255164df1164c7832044de302d034680`
- Raw Manim: `raw.mp4` 49.40s (PC render; dài hơn voice 0.78s sau trim;
  mux dùng `-shortest` nên final kết thúc cùng voice 48.36s)
- Script: `script.md` (130 từ theo file gốc — đếm bằng script ra **127 từ**,
  xem mục Voice). Voice: `voice.wav` 48.36s (đã trim 0.36s đầu, file gốc
  `voice_pc.wav` 48.72s). Captions: `captions.srt` (30 events) +
  `captions.ass` (PlayRes 1080x1920, Be Vietnam Pro 56, MarginV 300).

## Audio (đo bằng ffmpeg loudnorm / volumedetect)

- **Loudness: -15.90 LUFS** (target ~-16) · **true peak: -2.94 dBTP**
  (≤ -1 dBTP ✓) · LRA 3.20
- **Voice bắt đầu ~0.05s** (sau khi trim — xem mục fix): 0.4s đầu của
  final mean -16.9 dB / max -3.1 dB. Không có dead air đầu video.
- **Tốc độ: 157.6 wpm overall** (127 từ / 48.36s, trong vùng an toàn
  150–165). Theo beat (timing.json, tính trên beat duration incl. pause):
  hook 162.6 · beat1 140.8 · beat2 154.3 · beat3 166.7 · payoff 161.1 ·
  cta 152.7. Beat 3 hơi nhanh (speech-only ~176 wpm — burst nhanh đầu
  câu, cùng pattern như v004 payoff 170.6).
- **Whisper large-v3 (PC) check: 114/127 = 89.8%** từ đúng (run 3, file
  gốc chưa trim). Lỗi chủ yếu là Whisper nghe nhầm thanh điệu
  ("vỡ"→"dở", "mẹ"→"lẹ", "cúi"→"cuối", "dỗi"→"dũi", "cái"→"khẽ" —
  nhầm lẫn MMS/Whisper đã biết). Tất cả từ khóa nội dung đều nghe đúng.
- **Probe words (PC, speaking_rate 0.92, 3 runs):**
  - "Na" — **OK, giữ.** Nghe đúng 3/3 lần trong file full run 2+3
    ("câu na", "Na giận dũi", "Na bật cười"); 1 lần probe ngắn bị
    Whisper nuốt mất ("Là...") — artifact ở biên câu ngắn, không phải
    MMS sai.
  - "phăng phắc" — **OK, giữ** (theo precedent v005). Nghe đúng
    "phăng phắc" trong file full run 2 và run 3. 2 lần probe báo FAIL là
    lỗi matcher của script: Whisper render không dấu ("phang phác") hoặc
    "phăng phát" — cả hai đều là cách Whisper viết lại từ đúng, không
    phải MMS đọc sai.
  - "dỗi" — **OK, giữ.** Nghe đúng trong probe cả 3 runs.
  - "rã rời" — **FAIL → đổi thành "mệt lắm"** (fallback trong script).
    2/2 lần Whisper nghe sai thanh điệu ("dã rời", "rá rời"). Sau swap,
    "mệt lắm" nghe đúng trong file full.
  - "cởi giày" — **FAIL → đổi thành "bước vào thật khẽ".** 2/2 lần nghe
    hỏng một nửa ("cởi dậy", "gởi giày") — MMS nuốt cụm "cởi giày"
    (2 từ thanh ngã/huyền liền nhau). Sau swap, probe "bước vào" OK và
    file full nghe đúng "bước vào thật khẻ". Visual vẫn vẽ bố cởi giày
    ở cửa (hành động trên hình, không cần nói ra).
- **Đếm từ:** script ghi 130 (bảng) / 129 (header) — đếm bằng script trên
  text thoại thực tế là **128 từ** (bảng đếm thừa hook 14 thay vì 13,
  payoff 27 thay vì 26); sau 2 swap ("mệt rã rời" 3 từ → "mệt lắm" 2 từ)
  còn **127 từ**. WPM tính trên 127.
- **Nhạc + SFX (Core_SFX, CC0):** bgm_calm với volume envelope
  0.11 hook / 0.11 beat1 / 0.12 beat2 / 0.18 beat3 (swell khi bố về) /
  0.0 trong 0.6s im lặng trước payoff (34.54–35.14) / 0.11 payoff+cta.
  door_knock (0.4) tại 24.342 (bố về). pop (0.35) tại 35.14 (cái ôm).
  Không dùng victory (đúng script — sẽ phá cảm xúc ấm).
  - BGM đo được: cửa sổ chỉ-nhạc 4.15–4.43s mean **-39.6 dB**
    (max -29.3) — BGM nghe được, rõ ràng dưới voice.
  - Cửa sổ im lặng trước payoff 34.6–35.1s: mean **-91.0 dB** (silence
    tuyệt đối — BGM dip hoạt động đúng).
  - Per-SFX audibility: knock/pop không đo riêng được (chúng trùng với
    onset của voice theo thiết kế); cửa sổ knock mean -22.9 / max -4.8,
    pop mean -24.3 / max -5.4 — cả hai đều có mặt cùng voice.

## Hình ảnh (Manim rig, SPEC đóng băng — không đổi hằng số rig)

- **Render: PC** (lần đầu một episode đầy đủ render end-to-end trên PC:
  `.venv-win` python -m manim render, ~28s cả giải nén tar sync +
  render; raw 49.40s). Sync source VPS → PC bằng tarball (loại .venv /
  media / __pycache__), giải nén trên PC rồi render. Không render trên
  VPS — đúng lệnh của chủ 21:53 15/11.
- 3 rig: Na (scale 0.62, nơ tóc đỏ accent) + mẹ (búi tóc + váy xám) +
  bố (cà vạt đỏ accent). Set: cửa trước (trái), đồng hồ treo tường,
  lọ hoa vỡ + mảnh vỡ + bông hoa rơi, gối ôm của Na. Text card 7 cái
  theo beat. Không dùng gì từ #47 gốc (watermark NVV): story, nhân vật,
  cảnh, câu thoại đều original; chỉ giữ mechanism mắng → giận → bố
  mệt → ôm → cười.
- **Fix sau lần render 1 (xem frame):**
  1. **Cái ôm ở payoff rối thành một khối** (đầu Na chồng lên thân bố,
     tay chân đan nhau — lỗi "2 đầu" như v004) — sửa: Na về lại góc
     x=3.0, giảm lean (bố 0.28→0.12, Na -0.18→-0.10), tay bố duỗi ít
     hơn (shoulder_r 1.15→0.5, elbow_r 0.35→1.0) — giờ hai figure ngồi
     cạnh nhau, cười, tay bố chạm vai Na, rõ ràng.
  2. Card payoff 2 dòng che mất nửa đồng hồ — sửa: nâng card lên y=5.0,
     giờ không chạm đồng hồ nữa.
  3. Gối ôm đọc như hộp trắng lạ ở payoff — sửa: fade out cùng lúc với
     card payoff.
- **Fix âm thanh sau lần assemble 1 (đo bằng ffmpeg):** MMS thải ra
  **0.41s pad câm ở đầu voice** (0–0.408s mean -81.3 dB — lỗi dead air
  đầu video, đúng lỗi phổ biến nhất trong deep-analysis). Sửa: trim
  0.36s đầu voice (giữ 0.05s pad), shift toàn bộ timing/caption/BGM/
  SFX đi -0.36s, và trim 0.36s đầu raw video ở bước mux (`-ss` trước
  `-i`) để hình khớp giọng. Voice giờ bắt đầu ~0.05s (0.4s đầu final
  mean -16.9 dB). File gốc giữ lại: `voice_pc.wav` + `timing_pc.json`.
- Frame đã xem (final v008.mp4): **1s** hook card "LÀM VỠ LỌ HOA RỒI."
  rõ, đủ dấu, caption "Con gái làm vỡ lọ" rõ · **10s** mẹ chỉ tay vào
  Na, card "MẸ MẮNG MỘT CÂU." · **20s** Na ngồi ôm gối, mặt buồn, card
  "KHÔNG THÈM NÓI VỚI AI." · **28s** bố đi bộ từ cửa vào, cà vạt đỏ,
  card "BỐ VỀ RỒI." · **33s** bố ngồi xuống bên Na, card "BỐ CHỈ NGỒI
  XUỐNG." · **40s/48s** payoff: cả hai cười trong ánh ấm, card
  "CON GÁI CỦA BỐ ĐÂY RỒI." rồi end card "AI LÀ CON GÁI CỦA BỐ?"
  đầy đủ, không clip, caption cuối "bố? Bình luận nhé!" rõ.

## Honest limits (chưa nghe bằng tai người — chỉ Whisper)

- Chưa ai nghe thử voice (chỉ Whisper 89.8%). MMS vẫn monotone; pause
  0.3/0.4/0.6s + 0.6s im lặng trước payoff đã làm theo round-2 tuning.
- Per-SFX audibility: knock/pop không đo riêng được (chúng trùng với
  voice theo thiết kế); chỉ đo được qua cửa sổ transition.
- Beat 3 speech-only ~176 wpm (burst nhanh) — trên vùng an toàn nhưng
  cùng pattern v004; overall 157.6 wpm vẫn trong vùng.
- Tay mẹ chỉ chạm đúng đầu Na ở beat 1 (tay dài 1.8 chạm tới đầu bé) —
  đọc như mẹ chạm đầu con, hơi vụng nhưng không rối.
- Chân bố chạm mép lọ hoa vỡ ở 33s (bàn chân đáp ngay cạnh mảnh vỡ).
- Lọ hoa vỡ đọc như hộp nghiêng nhỏ + chấm đỏ — cần giọng + card mới rõ
  đó là lọ hoa; không phải vật đọc được ngay.
- Caption trùng lặp text card ở cuối (48s caption "bố? Bình luận nhé!"
  dưới end card "AI LÀ CON GÁI CỦA BỐ?" — cùng nit như v002/v004).
- Beat 2 (~10s) gần như tĩnh: Na chỉ ngồi ôm gối; không có chuyển động
  lớn. Walk-cycle của bố vẫn là stickman đơn giản.
- Không dùng gì từ #47 gốc (watermark NVV): story, nhân vật, cảnh, câu
  thoại đều original; chỉ giữ mechanism. Bố KHÔNG mắng, KHÔNG nói thêm
  câu dạy dỗ nào — câu duy nhất của bố là "con gái của bố đây rồi"
  (đúng quyết định biên tập trong script).
- Chưa đăng/upload đâu cả. Không commit/push git (parent xử lý).
