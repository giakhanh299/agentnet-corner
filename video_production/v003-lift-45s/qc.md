# QC — V003 "Cáp thang máy đứt ở tầng 85 — nhảy lên thì sống không?"

- File: `v003.mp4` — 50,133s, 19.733.840 byte, sha256
  `b9fb43a4762a90b83d2aa1cb79797b2f024815686217dad5871e6b5e7071b0a6`
- Video: H.264, 1080x1920, 30 fps, 1504 khung hình, CRF 20 preset medium
- Audio: AAC 192k, 48 kHz stereo
- **Độ lớn: -16,41 LUFS / -5,34 dBTP** (loudnorm; LRA 4,30) — đúng mục
  tiêu ~-16 LUFS, true peak ≤ -1 dBTP. volumedetect: mean -19,4 dB,
  max -5,6 dB.
- **Giọng bắt đầu 0,00s** (cửa sổ 0,0-0,2s đo -21,4 dB, cao hơn nền nhạc
  -31,2 dB rõ rệt — giọng có ngay từ khung hình đầu).
- **Tốc độ: 147 wpm tổng** (123 từ / 50,13s); ~152 wpm chỉ tính lúc nói
  (trừ 1,7s khoảng lặng giữa các beat). Theo beat: hook 172, beat1 170,
  beat2 166, beat3 154, payoff 146 wpm (tính theo token, gồm cả khoảng
  lặng trong beat). Tổng 147 hơi dưới vùng an toàn 150-165 nhưng người
  dùng phàn nàn giọng NHANH chứ không phải chậm nên giữ nguyên.
- **Whisper (faster-whisper large-v3, PC): 105/123 = 85,4%** trên file
  giọng (toàn file; phần lớn là chuẩn hóa số — "tám mươi lăm"→"85",
  "bốn"→"4", "hai mươi"→"20", "một trăm"→"100" — cộng lỗi biên "rơi"→
  "Thời", "ôm"→"ôn", "lực"→"Lợt", "trừ"→"chưa"). Các từ nội dung chính
  đều nghe đúng: "thang máy", "nhảy lên", "sống không", "bốn lớp an
  toàn", "phanh kẹp chặt", "nằm dài xuống sàn", "cơ hội tốt nhất",
  "Bình luận nhé".

## Probe (PC, MMS-TTS speaking_rate 0.92, faster-whisper large-v3)
- "tám mươi lăm" → nghe "85" (chuẩn hóa số của Whisper, PASS — như
  "500" ở v002); nhưng "Cáp"→"Các" ở từ đầu câu. GIỮ nguyên hook
  (thử "Dây cáp..." tệ hơn, 60,0%); chữ trên màn hình "CÁP ĐỨT Ở TẦNG
  85?" mang đúng chính tả.
- "kẹp chặt ray" → "rai" (88,2%). ĐỔI thành **"phanh kẹp chặt"**
  (94,1%, chỉ lỗi "bốn"→"4").
- "nằm ngửa" → "năng ngựa" (76,5%). ĐỔI thành **"nằm dài xuống sàn"**
  (94,1%). Nhãn beat 3 đổi theo: "NẰM DÀI — TRẢI ĐỀU LỰC".
- Số từ không đổi: 123 từ.

## Ảnh (4 dùng, toàn CC0 — xem images/sources.txt)
- Hook: "Central Elevator Shaft" (Wikimedia, neil.dalphin, CC0) — giếng
  thang B&W, cửa sổ vòm, kịch tính.
- Beat 1: "Looking inside to elevator" (Wikimedia, Tomasz Rynkiewicz,
  CC0) — nội thất thang máy hiện đại.
- Beat 2: "Central elevator shaft" (Wikimedia, neil.dalphin, CC0) —
  giếng thang thấy rõ ray dẫn hướng.
- Payoff: "WTC Towers looking up" (Flickr, DanielC743, CC0) — hai tòa
  tháp nhìn từ dưới lên.
- Beat 3: clip stickman Manim tự render (beat3_stickman.mp4) — người que
  nằm dài, tay gập trên ngực; 4 lần chỉnh pose mới đúng (xem
  v003_beat3.py).
- 11 ảnh tải về nhưng LOẠI (ghi lý do trong sources.txt): hầm đi bộ,
  thợ mỏ, bản vẽ "elevation" (Openverse nhầm với "elevator"), hoàng hôn,
  mẫu cây, sơ đồ thang máy vũ trụ, chân dung, ảnh mờ, 2 ảnh tháp kém
  kịch tính hơn.
- Ảnh hơi mềm: ảnh payoff chỉ 1024px (upscale ~2x khi crop 9:16); 3 ảnh
  kia 4883-6000px nên nét.

## Nhạc + SFX (Core_SFX, toàn CC0)
- Nhạc nền: bgm_suspense, volume 0,12, fade-out 2s cuối.
- SFX: whoosh + pop ở 0,1s; ding ở 5,53s và 14,06s (đầu beat 1/2);
  camera_click ở 26,86s (đầu beat 3); boom (volume 0,8) ở 41,91s
  (payoff).
- Đo năng lượng theo cửa sổ (v003.mp4): giọng -19,6 đến -21,6 dB;
  nền nhạc lúc lặng (41,35-41,85s) -31,2 dB — tức nhạc **~11 dB dưới
  giọng**, nóng hơn mục tiêu -18 đến -24 dB (xem mục Nits).
- Độ nghe từng SFX: ding -20,3 / -21,0 dB (nghe rõ, ngang giọng);
  camera_click -27,9 dB (nhỏ nhưng trên nền nhạc); boom -13,3 dB
  (to, ~6 dB trên giọng — xem mục Nits).

## Khung hình QC (đã xem)
| Thời điểm | Nội dung | Kết quả |
|---|---|---|
| 1s | Hook: giếng thang B&W + "CÁP ĐỨT Ở TẦNG 85?" + phụ đề "Cáp thang máy đứt" | Rõ, dấu đúng, chữ không cắt. Ảnh kịch tính, nét. |
| 11s | Beat 1: nội thất thang máy + nhãn "NHẢY LÊN = TRỪ 4 M/S" + phụ đề "chỉ trừ được bốn" | Rõ, dấu đúng. Nhãn hơi đè lên thanh ngang giữa ảnh nhưng vẫn đọc được. |
| 15s | Beat 2: giếng thang + ray + nhãn "HƠN 100 KM/H" + phụ đề "Rơi từ tầng hai" | Rõ, dấu đúng. Ảnh tối nhưng nhãn có hộp đen nên đọc được. |
| 30s | Beat 3: stickman nằm dài + nhãn "NẰM DÀI — TRẢI ĐỀU LỰC" + phụ đề "rơi, cách khoa học" | Rõ. Stickman nằm phẳng, tay gập trên ngực, không chạm sàn. Dấu "—" render đúng. |
| 45,5s | End card: 2 tòa WTC + "BẠN CÓ DÁM ĐI THANG / TẦNG 85 KHÔNG?" + "YES / NO" đỏ + phụ đề "có dám đi thang" | Đầy đủ, không cắt. |
| 49,5s | End card cuối + phụ đề "không? Bình luận nhé!" | Như trên, chữ vẫn đầy đủ. |

## Render — CHẠY TRÊN PC (lệnh user 21:53)
- PC: ffmpeg 8.1.2-full_build (gyan.dev), render 22:15:49-22:16:01 =
  **12 giây**, FFMPEG_EXIT=0, 1504 khung hình đúng. File video-only
  18.499.270 byte, copy về VPS rồi mux với audio_final2.m4a.
- Font: Be Vietnam Pro Bold (C:\Users\w\v003_render\BeVietnamPro-Bold.ttf,
  copy từ C:\Windows\Fonts) — assemble_filter_pc.txt + captions_pc.ass
  (bản PC) khác bản VPS ở tên font (VPS: Noto Sans). Noto Sans không có
  trên PC (chỉ có NotoSansJP-VF). Phụ đề đốt bằng Be Vietnam Pro, dấu
  tiếng Việt render đúng (đã kiểm ở khung 1s/30s).
- **Sự cố render (bài học pipeline):** 2 lần chạy đầu CHẠY VÔ HẠN.
  (1) VPS 20:58-21:53: ~98 MB sau 56 phút, bị kill (không có moov).
  (2) PC 21:58-22:14: 238 MB sau 16 phút, bị kill. Nguyên nhân: `-loop 1`
  trên 4 input ảnh — zoompan xuất d khung/ảnh đầu vào, input vô hạn
  nên xfade không bao giờ thấy EOF. Cách sửa: BỎ `-loop 1` (1 ảnh = 1
  khung → zoompan xuất đúng d khung rồi EOF) + thêm `-frames:v 1505`
  làm giới hạn cứng. Chạy lại trên PC xong trong 12 giây.
  (VPS render cũng bị lỗi này — không phải crash, mà là chạy vô hạn.)
- Lỗi font lần đầu trên PC: `fontfile=C\:/Windows/...` làm filtergraph
  parse lỗi (Invalid argument, exit -22). Cách sửa: copy font vào thư
  mục render, dùng đường dẫn tương đối `fontfile=BeVietnamPro-Bold.ttf`
  (đã test 1 khung trước khi chạy lại).

## Âm thanh — ghi chú kỹ thuật
- Mix lần đầu ra AAC 96 kHz mono (loudnorm xuất 192 kHz, encoder AAC
  giới hạn 96 kHz; amix lấy layout của input đầu = giọng mono). Đã sửa
  bằng re-encode `-ac 2 -ar 48000` → AAC 48 kHz stereo 191k như v002.
  Sau sửa: -16,41 LUFS / -5,34 dBTP (trước sửa: -16,40 / -2,84).
  Lưu ý: RMS/peak thô giảm ~3 dB sau re-encode (do lấy mẫu lại 96→48
  kHz) nhưng LUFS đo được không đổi (-16,41) — độ lớn cảm nhận giữ
  nguyên, đạt chuẩn.

## Những gì KHÔNG kiểm được / Nits (trung thực)
- **Không có người nghe thật** (agent không có tai nghe/loa): giọng chỉ
  kiểm bằng faster-whisper large-v3 trên PC (85,4%); nhạc/SFX chỉ đo
  năng lượng từng cửa sổ. Người dùng nên nghe thử 1 lần trước khi đăng,
  nhất là từ "Cáp" (MMS đọc thành "Các" ở đầu câu) và tốc độ hook
  (172 wpm theo token — nhanh nhất video).
- **Nhạc nền nóng hơn mục tiêu:** ~11 dB dưới giọng, mục tiêu -18 đến
  -24 dB. Giọng vẫn trội rõ (11 dB) nên không át lời, nhưng lần sau thử
  volume 0,06 cho bgm_suspense (hoặc đo lại ở đoạn swell to nhất của
  nhạc — đoạn 41s có thể là đoạn to của bed 86s).
- **Boom payoff hơi to:** -13,3 dB, ~6 dB trên giọng. Có chủ ý (điểm
  nhấn payoff) nhưng lần sau thử volume 0,6 thay vì 0,8.
- **Phụ đề trùng end card:** 2s cuối phụ đề "không? Bình luận nhé!" đè
  lên chữ end card (giống v002) — nhỏ ở dưới, chữ lớn ở giữa, không xấu
  nhưng hơi thừa.
- **Ảnh payoff 1024px:** hơi mềm khi crop 9:16 (giống mức mềm của v002).
- **Beat 2 ~13s gần như tĩnh:** chỉ có zoompan chậm trên ảnh giếng thang
  (không có chuyển động nào khác) — chấp nhận được cho Visual Essay,
  nhưng là đoạn dễ mất tập trung nhất.
- **Không dùng gì từ video gốc #77:** toàn bộ ảnh CC0 + stickman tự
  render; kịch bản gốc tiếng Việt, số liệu đã kiểm chứng (không dùng
  "72 km/h" — không kiểm chứng được; dùng ~108 km/h từ tầng 20).

## File trong thư mục
- `v003.mp4` (19,7 MB) — video cuối. `script.md` — kịch bản + nguồn +
  ghi chú giọng + kết quả probe. `script_text.txt` — lời thoại thuần
  (5 câu, 123 từ).
- `voice.wav` (1,6 MB, 16 kHz mono, 50,13s) — giọng MMS-TTS từ PC
  (speaking_rate 0,92). `voice_norm.wav` — giọng chuẩn hóa.
  `audio_final.m4a` / `audio_final2.m4a` — mix cuối (giọng + nhạc +
  SFX; bản 2 đã loudnorm 2-pass: -16,42 LUFS / -2,84 dBTP trước khi
  re-encode stereo).
- `v003_video.mp4` (18,5 MB) — video-only render từ PC.
  `captions.srt` (32 đoạn) + `captions.ass` (bản Noto Sans) +
  `captions_pc.ass` (bản Be Vietnam Pro đã đốt vào video).
  `assemble_filter.txt` (bản VPS) + `assemble_filter_pc.txt` (bản PC).
  `render_pc.log` — log render trên PC. `v003_beat3.py` — scene Manim
  beat 3. `images/sources.txt` — nguồn + giấy phép từng ảnh.
- `qc_f1.jpg`, `qc_f11.jpg`, `qc_f15.jpg`, `qc_f30.jpg`, `qc_f45.5.jpg`,
  `qc_f49.5.jpg` — khung hình QC.
