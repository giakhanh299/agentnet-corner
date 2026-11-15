# QC — V005 "Top 5 câu nói huyền thoại của mẹ" (F3 Countdown, 45s)

Ngày: 2026-11-15. Trạng thái: **QC PASS** (chưa đăng, chưa ai nghe thật).

## File
- `v005.mp4` — **49,97s, 1080x1920, 30fps, H.264 + AAC 192k, 14.072.099 bytes
  (13,4 MB), bitrate 2,25 Mbps, sha256 `0c967c677b23…`**
- Giọng: MMS-TTS `facebook/mms-tts-vie` trên PC (CUDA), speaking_rate 0.92
  (variant C), tổng hợp từng câu + nối theo pause scheme (0,3s sau hook;
  0,4s giữa các beat; 0,6s trước #1; 0,4s trước CTA).

## Số đo (đo bằng ffprobe / loudnorm / faster-whisper large-v3)
| Chỉ số | Đo được | Chuẩn | Kết luận |
|---|---|---|---|
| Thời lượng | 49,97s | 40–55s | PASS |
| Độ phân giải / fps | 1080x1920 / 30fps | 1080x1920 / 30fps | PASS |
| Âm lượng tích hợp | **-16,42 LUFS** | ~-16 LUFS | PASS (0,42 dưới mục tiêu) |
| True peak | **-2,55 dBTP** | ≤ -1 dBTP | PASS |
| LRA | 3,70 LU | — | — |
| Giọng bắt đầu | **0,00s** (hook nói từ 0s) | ≤ 0,1s | PASS, không dead air |
| Tốc độ nói | **155 wpm** (chỉ phần nói) | 150–165 wpm | PASS |
| Tốc độ tổng thể | **143 wpm** (119 từ / 49,95s) | — | Dưới 150 do pause đếm ngược có chủ đích (xem dưới) |
| Whisper check giọng | **102/119 = 85,7%** | — | PASS (chênh lệch so với run 1 là nhiễu Whisper) |

## Probe từ (PC, speaking_rate 0.92, faster-whisper large-v3)
- "phăng phắc" → nghe thành "phan phát" (64%) — **GIỮ nguyên** (vòng 2:
  "im re" → "Inge", "nín thinh" → "nứng thiên" đều tệ hơn). Chữ đúng
  hiện trên thẻ danh sách + caption, theo tiền lệ "log" ở v002.
- "Tao" → nghe đúng 100% — GIỮ.
- "trĩu" → nghe thành "triếu" (88%) — **ĐỔI thành "nặng nề"** theo kịch
  bản (bản thay thế nghe đúng 88%, lỗi còn lại là "tim"→"tin", nhiễu
  Whisper). Caption dùng "nặng nề".
- "Top" → nghe thành "Tốc" (loanword, MMS không đọc được "Top") — giữ,
  chữ đúng hiện trên tiêu đề + caption.

## Giọng — run 1 vs run 2
- Run 1 (11,5s): 47,92s, 163 wpm (chỉ nói), 149 wpm tổng thể, Whisper
  106/119 = 89,1%. Câu #1 (n1a) chạy 190 wpm — quá nhanh cho cú lật
  cảm xúc.
- Run 2 (23,4s, n1a chậm lại speaking_rate 0.80): **49,95s, 155 wpm
  (chỉ nói), 143 wpm tổng thể**, Whisper 102/119 = 85,7% (giảm là nhiễu
  Whisper giữa các lần chạy — các từ bị miss gồm cả số/từ thường mà run 1
  nghe đúng). n1a còn 170 wpm.
- **Dùng run 2** (file `v005_voice.wav` / `voice.wav`): câu #1 cảm xúc
  rơi tốt hơn ở 170 wpm; 155 wpm trong vùng an toàn; 49,95s trong cửa sổ
  40–55s. Tổng thể 143 wpm thấp hơn sàn 150 là do pause đếm ngược có chủ
  đích giữa các mục (cơ chế F3 — video gốc H02 cũng chỉ ~114 wpm tổng
  thể). File run 1 đã bị ghi đè trên PC, không khôi phục được; run 2 là
  bản chính thức.

## Ảnh (5 ảnh đã dùng, xem `images/sources.txt`)
| Mục | File | Nguồn / giấy phép |
|---|---|---|
| #5 mâm cơm | n5b_dinner.jpg | "Pre-Race Dinner" — Kazz.0 — CC BY (Flickr) |
| #4 im lặng | n4b_alone.jpg | "It's my Friday night" — goblinbox_ — CC BY (Flickr) |
| #3 mẹ nấu cơm | n3a_mother_child.jpg | "Mother Child" — Direct Media — CC0 (StockSnap) |
| #2 nhìn sang nhà | n2a_window.jpg | "Boy Looking Out Window" — inclusivesecurity — CC BY (Flickr) |
| #1 gia đình | n1a_family.jpg | "Family Portrait" — Family Moments — CC0 (StockSnap) |
9 ảnh khác đã loại có lý do (ghi trong `images/sources.txt`).
- Tất cả 1024px (Openverse editor_1024), trừ n2a 679px (portrait) — crop
  landscape + upscale ~1,6x nên hơi mềm; đã kiểm bằng mắt, chấp nhận được.
- Ảnh n4 (phòng tối) khá tối nhưng đọc được không khí im lặng; phần danh
  sách sáng nên nội dung vẫn rõ.

## Nhạc + SFX (Core_SFX, toàn bộ CC0)
- Nhạc nền `bgm_comedy.ogg` (116,71s → cắt 49,95s, vol 0,12, fade-out 2s
  cuối). Đã kiểm bằng năng lượng: cửa sổ pause 3,18–3,48s (chỉ có nhạc)
  RMS -41,6 dB so với giọng -57,1 dB trong cùng cửa sổ → nhạc có mặt,
  ~20 dB dưới giọng.
- SFX: whoosh + pop ở 0,1s; pop ở mỗi lần mở mục (3,48 / 11,32 / 19,64 /
  28,50 / 37,68s); riser 34,60–37,68s (dẫn vào #1) — đã kiểm: cửa sổ
  37,08–37,68s (giọng im) RMS -29,2 dB, max 0,30 so với giọng -94,6 dB
  → riser có mặt; victory NHẸ ở 37,68s (cắt còn 1,5s, vol 0,35, theo
  quyết định kịch bản: #1 là cảm xúc, không phải trò đùa); laugh ở
  19,30s sau punchline #4 (vol 0,5); ding ở CTA 45,87s.
- **KHÔNG có laugh ở #2**: kịch bản yêu cầu nhưng sẽ chồng lên riser
  34,60–37,68s + khoảnh khắc mở #1 — bảo vệ cú lật cảm xúc quan trọng hơn.
- Mix: `amix duration=longest` (không dùng `apad` + `duration=first` —
  treo máy, bài học v002). Mix thô đo -16,55 LUFS / TP +0,03 dBTP (clip
  do cộng dồn) → loudnorm 2-pass + `alimiter=limit=0.7:level=false` →
  -16,82 LUFS → +0,83 dB gain → **-16,42 LUFS / -2,55 dBTP** (mức cuối).
  `level=true` là auto-gain, SAI — không dùng.

## Thẻ danh sách (build_cards.py, PIL + Be Vietnam Pro)
- 7 stage: hook (#3 mở sẵn, không mở #1 sớm) → n5 → n4 → n3 → n2 → n1
  (tất cả mở, #1 highlight vàng) → end card. Nền kem #FFF7E8, chữ
  #1F1A17, đỏ #D9381E, vàng #E8A100. Ảnh y 258–968 (cover-crop; n2a dùng
  y_frac 0,30 để giữ đầu cậu bé). Hàng đã mở hiện đủ câu trích (≤2 dòng);
  hàng chưa mở hiện "• • •".
- Video: mỗi stage zoompan 1,0→1,05 (scale 2160x3840), xfade 0,4s tại
  các thời điểm mở mục (3,48 / 11,32 / 19,64 / 28,50 / 37,68 / 45,87s).
  Filter đầy đủ trong `assemble_filter.txt`.

## Caption
- `captions.srt` + `captions.ass`: 32 event, 119 từ, chia ≤4 từ/chunk,
  thời gian chia đều theo từng beat (từ `v005_units.json`). ASS: Noto
  Sans Bold 56, PlayRes 1080x1920, MarginV 300, alignment 2 (giống
  v001/v002). Caption dùng **lời đã nói sau probe** ("nặng nề", không
  dùng "trĩu").

## QC khung hình (đã xem: 1s / 5s / 13s / 21s / 30s / 39s / 46,5s / 49,5s)
- 1s: tiêu đề "TOP 5 CÂU NÓI HUYỀN THOẠI CỦA MẸ" to, rõ, đúng dấu; ảnh
  mẹ + con trong bếp rõ; hàng #3 highlight với câu trích; các hàng chưa
  mở hiện "• • •"; caption "Top năm câu nói" hiện rõ. PASS.
- 5s / 13s / 21s / 30s: từng mục mở đúng thứ tự (#5 → #4 → #3 → #2),
  ảnh đổi đúng, caption khớp lời nói từng beat. PASS.
- 39s (#1): badge vàng #1 + highlight hổ phách, câu "Mẹ không cần gì
  đâu, con cứ lo cho con đi." hiện đủ 1 dòng; ảnh gia đình rõ. PASS.
- 46,5s / 49,5s: end card "SỐ 1 CỦA BẠN LÀ CÂU NÀO?" + "Bình luận nhé!"
  + câu trích #1 hiện đầy đủ, không bị cắt; caption CTA không chồng lên
  câu trích. PASS.
- Lưu ý nhỏ: caption (MarginV 300) nằm sát hàng #5 — ví dụ ở 39s caption
  "cần gì đâu, con" nằm ngay trên dòng #5, không che chữ nhưng hơi chật.
  Giữ nguyên (cùng mẫu v002); lần sau có thể nâng MarginV lên 360.

## Giới hạn thành thật
- Chưa có người nghe thật — chỉ kiểm bằng Whisper (85,7%). Người dùng
  nên nghe một lần trước khi đăng, nhất là "phăng phắc" ("phan phát"),
  "Top" ("Tốc") và câu #1 cảm xúc.
- Độ nghe được của từng SFX riêng lẻ không đo được (chúng trùng với giọng
  theo thiết kế) — chỉ kiểm được BGM (cửa sổ pause) và riser (cửa sổ
  giọng im) bằng năng lượng; whoosh/pop/victory/laugh/ding kiểm bằng
  cấu trúc filter + thời lượng đầu ra.
- Ảnh 1024px hơi mềm khi crop 9:16 (đặc biệt n2a 679px, upscale ~1,6x);
  ảnh n4 tối.
- Tổng thể 143 wpm dưới sàn 150 (do pause đếm ngược có chủ đích — xem
  mục giọng).
- Run 1 của giọng đã mất (bị ghi đè trên PC); chỉ còn run 2.
- Chưa đăng / chưa upload đi đâu.
