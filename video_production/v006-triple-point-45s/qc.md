# QC — V006 "Nước vừa sôi vừa đóng băng cùng một lúc"

- File: `v006.mp4` — 53,133s, 18.522.052 byte, sha256
  `84757475ef0e4ce5bd53b1ab2beeceee3e49912107c3f1e7745f0c8da0489010`
- Video: H.264, 1080x1920, 30 fps, 1594 khung hình, CRF 20 preset medium
- Audio: AAC 192k, 48 kHz stereo
- **Độ lớn: -16,19 LUFS / -3,04 dBTP** (loudnorm; LRA 4,90) — đúng mục
  tiêu ~-16 LUFS, true peak ≤ -1 dBTP.
- **Giọng bắt đầu 0,00s** (đo mẫu trực tiếp trên voice.wav: cửa sổ 0,0-0,2s
  RMS -44,5 dB, peak -34,6 dB — âm đầu câu đã có ngay từ khung hình đầu;
  trên mix cuối: RMS -26,7 dB, peak -11,2 dB).
- **Tốc độ: 147 wpm tổng** (130 từ / 53,14s); **158 wpm chỉ tính lúc nói**
  (trong vùng an toàn 150-165). Theo beat: hook 179, beat1 129, beat2 161,
  beat3 158, payoff 172 wpm.
- **Whisper (faster-whisper large-v3, PC): 124/127 = 97,6%** trên file
  giọng (cao nhất từ trước tới nay: v003 85,4%, v005 85,7%). Sai sót còn
  lại: "buồng kín" nghe "đùn kính" trong lời nối (probe riêng 100% — lỗi
  Whisper ở lời nối nhanh, không phải MMS), "lúc" bị nuốt 1 lần. Các từ
  nội dung chính đều nghe đúng: "sức ép không khí", "mỏng hơn", "đóng
  băng", "điểm ba trạng thái", "Bình luận nhé".

## Probe (PC, MMS-TTS speaking_rate 0.92, faster-whisper large-v3)
- "áp suất" → nghe "ác súc" (P1, 88,2%, cả 2 token đều sai). ĐỔI thành
  **"sức ép không khí"** (fallback trong kịch bản), đồng nhất cả 4 lần
  xuất hiện (beat1 x1, beat2 x2, beat3 x1). Số từ 122 → 130.
- "loãng" → nghe "loạn" 2 lần (cả file tổng + probe riêng P5, 84,6%).
  ĐỔI thành **"mỏng hơn"** (P6, 100,0%) ở beat 2. Số từ không đổi.
- "đóng băng" → nghe đúng (P2, 90,9%; chỉ sai "Nước"→"Đất" ở đầu câu —
  lỗi từ đầu câu như v003 "Cáp"→"Các"; chữ trên màn hình mang đúng chính
  tả). GIỮ.
- "buồng kín" → 100,0% (P3). GIỮ. "trạng thái" → 100,0% (P4). GIỮ.
- Take giọng: take 1 (53,32s, 157 wpm, 96,1%) bị loại vì còn "loãng";
  take 2 (49,41s, 171 wpm chỉ tính lúc nói — beat2 185, payoff 184) bị
  loại vì quá nhanh; **take 3 được chọn** (53,14s, 158 wpm, 97,6%).

## Ảnh (7 dùng, toàn CC0 — xem images/sources.txt)
- Hook: "Boiling water" (Flickr, CC0) — tranh trừu tượng màu xanh nước.
- Beat 1: đồng hồ áp suất HELICOID (StockSnap, Tim Sullivan, CC0) — ảnh
  chân dung, kim + mặt số rõ.
- Beat 2a: dãy núi tuyết trời xanh (Flickr, pixellaphoto, CC0).
- Beat 2b: thung lũng núi tuyết (StockSnap, Burst, CC0) — đổi cảnh giữa
  beat 2 (cắt cứng theo kịch bản).
- Beat 3a: buồng chân không thật (Wikimedia, Darth luigi, CC0) — 3024px,
  ảnh nét nhất lô.
- Beat 3b: bình thí nghiệm neon (Rawpixel, usdoe, CC0) — đổi cảnh giữa
  beat 3.
- Payoff: bông tuyết macro trên nền đen (Flickr, Don Komarechka, CC0).
- 25+ ảnh tải về nhưng LOẠI (ghi lý do trong sources.txt): cocktail,
  hũ mứt/canning, hoa trắng chiếm khung, icon SVG (403), bình hoa, cỏ
  sương, giọt dầu vàng...
- Không dùng gì từ video gốc #80: toàn bộ ảnh CC0 + chữ tự vẽ; kịch bản
  gốc tiếng Việt; số liệu đã kiểm chứng (0,01°C / 611,657 Pa / 1/166 —
  chỉ hiện trên hình, không đưa vào lời thoại, đúng kịch bản).

## Nhạc + SFX (Core_SFX, toàn CC0)
- Nhạc nền: bgm_calm, volume 0,12, fade-out 2s cuối.
- SFX: ding ở 4,33s và 27,82s (đầu beat 1/3); whoosh ở 14,35s (vào núi);
  pop ở 44,76s (thẻ payoff).
- Đo năng lượng theo cửa sổ (đo mẫu trực tiếp trên audio đã decode,
  không dùng volumedetect với -ss sau -i — xem mục Lỗi đo): giọng
  -18,7 đến -23,7 dB RMS; **nền nhạc lúc lặng -38,1 dB (cửa sổ
  27,42-27,82s) và -40,2 dB (44,16-44,76s) — tức nhạc ~19-20 dB dưới
  giọng, ĐÚNG mục tiêu -18 đến -24 dB** (v003 là -11 dB, quá nóng).
- Độ nghe từng SFX: không đo riêng được (mọi SFX đều trùng với giọng
  theo thiết kế, không có cửa sổ chỉ-SFX) — và không nghe được bằng tai.
  Ghi rõ ở đây để không nói quá. Hai cửa sổ chỉ-nhạc (27,42s và 44,16s)
  chứng minh mix hoạt động và không có SFX lạ trong khoảng lặng.

## Khung hình QC (đã xem — thư mục qc_frames/)
| Thời điểm | Nội dung | Kết quả |
|---|---|---|
| 1s | Hook: tranh nước xanh + "NƯỚC VỪA SÔI / VỪA ĐÓNG BĂNG?" + phụ đề "Nước vừa sôi vừa" | Rõ, dấu đúng, chữ không cắt. Nền trừu tượng nhưng màu nước nổi bật. |
| 10s | Beat 1: đồng hồ HELICOID + nhãn "ĐIỂM SÔI DO / SỨC ÉP QUYẾT ĐỊNH" + phụ đề "nước quyết định, mà" | Rõ, dấu đúng. Đồng hồ nét, lấp đầy khung. |
| 17s | Beat 2a: dãy núi tuyết + nhãn "NÚI CAO: / SÔI SỚM HƠN" + phụ đề "khí mỏng hơn, sức" | Rõ, dấu đúng. Núi kịch tính, trời xanh. |
| 24s | Beat 2b: thung lũng núi tuyết + nhãn "CÀNG THẤP: / CÀNG KHÓ SÔI" + phụ đề "sức ép không khí" | Rõ. Đã đổi cảnh so với 17s (cắt cứng giữa beat 2 đúng kịch bản). Nửa trên khung hơi nhiều trời trống. |
| 32s | Beat 3a: buồng chân không + nhãn "BUỒNG KÍN: / RÚT HẾT KHÔNG KHÍ" + phụ đề "hết không khí ra." | Rõ, dấu đúng. Ảnh nét nhất lô; nền kim loại hơi rối nhưng nhãn có hộp đen nên đọc được. |
| 42s | Beat 3b: bình thí nghiệm neon + nhãn "MỘT PHẦN SÔI — / MỘT PHẦN ĐÓNG BĂNG" + phụ đề "lại — cùng một" | Rõ. Đổi cảnh màu sắc mạnh so với 32s. Dấu "—" render đúng. |
| 52,5s | End card: bông tuyết đen + "ĐIỂM BA TRẠNG THÁI" + "0,01°C · 611,657 Pa" + "1/166 ÁP SUẤT KHÍ QUYỂN" + "BẠN CÓ DÁM THỬ KHÔNG?" + phụ đề "không? Bình luận nhé!" | Đầy đủ, không cắt. Số liệu chỉ trên hình, đúng kịch bản. Dấu "·" và "°C" render đúng. |

## Cắt cứng (khác v003 — lần đầu dùng concat thay vì xfade)
- 7 đoạn, cắt cứng tại 4,33s / 14,35s / 20,84s (giữa beat 2) / 27,82s /
  39,78s (giữa beat 3) / 44,76s — không có crossfade nào. Đoạn dài nhất
  là beat 3a (11,97s); không đoạn nào tĩnh quá ~12s (v003: beat 2 ~13s
  một ảnh; video gốc #80: 0 cắt cứng trong 80s — lỗi đã sửa).

## Render — CHẠY TRÊN PC (lệnh user 21:53 ngày 15/11)
- PC: ffmpeg 8.1.2-full_build (gyan.dev), render + mux xong trong một
  lần chạy foreground (~29s wall cho cả lệnh SSH, gồm render + mux).
  Video-only 1594 khung hình đúng (ffprobe nb_read_frames=1594).
  File video-only 18,5 MB, mux với audio_final.m4a → v006.mp4 18,5 MB.
- Font: Be Vietnam Pro Bold (C:\Users\w\v006_render\BeVietnamPro-Bold.ttf,
  copy từ C:\Windows\Fonts) — assemble_filter_pc.txt + captions_pc.ass
  (bản PC). Phụ đề đốt bằng Be Vietnam Pro, dấu tiếng Việt render đúng
  (đã kiểm ở 7 khung hình).
- **Sự cố render (đã sửa):** lần chạy đầu lỗi concat — các output zoompan
  có SAR khác nhau (ảnh 3024x4032 vs ảnh 1024px): "Input link parameters
  do not match... SAR 204800:204823 vs 40960:40963". Cách sửa: thêm
  `setsar=1` sau mỗi zoompan (ghi chú cho các video sau: concat yêu cầu
  SAR giống hệt nhau).
- **Sự cố script (đã sửa):** ký tự em-dash "—" trong chuỗi PowerShell
  (.ps1 UTF-8 không BOM) bị PowerShell 5.1 đọc sai và phá vỡ chuỗi —
  **không dùng ký tự non-ASCII trong file .ps1** (dùng "-" thay "—").
- **Sự cố mix (đã sửa):** `$ErrorActionPreference = "Stop"` biến stderr
  của ffmpeg thành lỗi dừng (NativeCommandError) ở bước loudnorm pass 1
  (dùng `-v info`). Cách sửa: dùng "Continue" trong script mix/render.
- **Lưu ý loudnorm:** JSON của ffmpeg 8.1 KHÔNG có khóa "linear" (chỉ có
  "normalization_type") — pass 2 nhận `linear=` rỗng nhưng vẫn chạy và
  cho kết quả -16,21 LUFS (đúng chuẩn). Lần sau lấy linear từ
  normalization_type ("dynamic" → linear=false).
- **Lỗi đo (đã sửa):** `volumedetect` với `-ss` đặt SAU `-i` cho kết quả
  sai trên build này (cửa sổ lặng 27,42s đo -18,9 dB trong khi mẫu thực
  là silence tuyệt đối). Đo năng lượng phải decode toàn bộ audio ra wav
  rồi đo mẫu bằng Python — đó là số liệu thật trong mục Nhạc + SFX.

## Những gì KHÔNG kiểm được / Nits (trung thực)
- **Không có người nghe thật** (agent không có tai nghe/loa): giọng chỉ
  kiểm bằng faster-whisper large-v3 trên PC (97,6%); nhạc/SFX chỉ đo
  năng lượng từng cửa sổ. Người dùng nên nghe thử 1 lần trước khi đăng,
  nhất là từ "Nước" đầu câu (MMS đọc thành "Đất" — lỗi từ đầu câu như
  v003 "Cáp"→"Các") và tốc độ hook (179 wpm) / payoff (172 wpm).
- **Ảnh hook trừu tượng:** không tìm được ảnh thật nào vừa sôi vừa đóng
  băng trong một bình (Openverse trả cocktail/hũ mứt) — dùng tranh nước
  xanh CC0 làm nền cho chữ hook; 1024px nên hơi mềm khi crop 9:16
  (upscale ~6x). Chấp nhận được vì chữ hook chiếm khung.
- **Beat 2b nửa trên trống:** ảnh thung lũng có nhiều trời xanh trống —
  nhãn vẫn đọc tốt, không sửa.
- **Beat 3a nền hơi rối:** tấm pegboard kim loại nhiều chi tiết — nhãn có
  hộp đen nên vẫn đọc được.
- **Phụ đề trùng end card:** 2s cuối phụ đề "không? Bình luận nhé!" đè
  lên chữ end card (giống v002/v003/v005) — nhỏ ở dưới, chữ lớn ở giữa,
  không xấu nhưng hơi thừa.
- **Hook/payoff hơi nhanh:** hook 179 wpm, payoff 172 wpm (model đọc câu
  hỏi nhanh — đã biết từ vòng 2; tổng thể 158 wpm vẫn trong vùng an
  toàn).
- **"buồng kín" trong lời nối:** Whisper nghe "đùn kính" ở tốc độ lời
  nối (probe riêng 100% — lỗi Whisper, không phải MMS); phụ đề mang
  đúng chính tả.
- Không dùng gì từ video gốc #80: toàn bộ ảnh CC0 + chữ tự vẽ; kịch bản
  gốc tiếng Việt; số liệu đã kiểm chứng.

## File trong thư mục
- `v006.mp4` (18,5 MB) — video cuối. `script.md` — kịch bản + nguồn +
  ghi chú giọng + kết quả probe. `script_text.txt` — lời thoại thuần
  (5 câu, 130 từ sau 2 lần đổi từ probe).
- `voice.wav` (1,7 MB, 16 kHz mono, 53,14s) — giọng MMS-TTS từ PC
  (speaking_rate 0,92, take 3). `v006_voice.wav` — bản copy cùng file.
  `audio_final.m4a` — mix cuối (giọng + nhạc + SFX; -16,19 LUFS /
  -3,04 dBTP).
- `v006_video.mp4` (18,5 MB) — video-only render từ PC.
  `captions.srt` (34 đoạn) + `captions.ass` (bản Noto Sans) +
  `captions_pc.ass` (bản Be Vietnam Pro đã đốt vào video).
  `assemble_filter_pc.txt` (filtergraph PC: concat cắt cứng + drawtext +
  ass). `v006_beat_timing.txt` / `v006_fw_segments.txt` (take 3).
- `v006_probe.py` / `v006_probe2.py` (+ .ps1) — probe từ rủi ro của MMS.
  `v006_tts.py` / `v006_tts_run.ps1` — tổng hợp giọng + kiểm Whisper
  trên PC. `v006_mix_run.ps1` / `v006_render_run.ps1` — mix + render
  trên PC. `search_images.py` / `search_images2.py` (+ download_images.py)
  — tìm + tải ảnh Openverse. `build_captions.py` — ráp phụ đề từ timing
  TTS + chữ kịch bản.
- `images/` — 31 ảnh tải về (7 dùng + 24 loại, xem `images/sources.txt`)
  + `contact_sheet.jpg` / `contact_sheet2.jpg` + `img_candidates*.json`.
- `qc_frames/` — 7 khung hình QC đã xem (f_1/10/17/24/32/42/52.5).
