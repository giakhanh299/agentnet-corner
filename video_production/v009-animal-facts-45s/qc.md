# QC — V009 "Top 5 sự thật về động vật" (F3 Countdown, T04 #84)

## Kết quả: PASS

- **File:** `v009.mp4` — 51,23s, 1080x1920, 30fps, H.264 2082 kbps + AAC 192k
  48 kHz stereo, 14.661.744 byte
- **sha256:** `dc6c97c0e52e7ba322ac80b4845733e5b92afe563d48f914247e977d1f08db9b`
- **Âm lượng (đo trên mp4 cuối): -16,12 LUFS, true peak -2,95 dBTP, LRA 3,80**
  — trong chuẩn (-16 ± 1, TP ≤ -1). Mix trên PC đo -16,13 LUFS / -2,95 dBTP.
- **Giọng:** MMS-TTS trên PC, speaking_rate 0.92, 120 từ, speech-only 47,23s =
  **152 từ/phút (trong vùng 150–165)**; tổng 141 từ/phút (khoảng lặng đếm
  ngược có chủ ý, như v005 143 / v007 145). Giọng từ 0,00s (0–0,4s đầu
  -20,0 dB, không có khoảng lặng chết).
- **Whisper large-v3 (PC): 102/120 = 85,0%** — ngang v003 (85,4%) / v005 (85,7%).
- **Tốc độ từng beat:** hook 209, n5a 190, n5b 140, n4a 135, n4b 132, n3a 152,
  n3b 139, n2a 147, n2b 177, n1a 146, n1b 151, cta 126 từ/phút.

## Probe (PC, rate 0.92, faster-whisper large-v3)
- **"huýt" FAIL** ("quyết", 67%) → **đổi thành "kêu"** (fallback, 100%).
  Câu n5b cuối: "Mỗi con kêu một điệu riêng, cả đàn nghe là biết ai."
- **"bạch tuộc" GIỮ** ("tụ"/"tuột" ở cả bản chính lẫn fallback "con bạch
  tuộc" — lỗi thanh như nhau; chữ trên hình + phụ đề gánh chính tả, tiền lệ
  "log" của v002).
- **"lướt" GIỮ** (nghe đúng; lỗi chỉ là Whisper chuẩn hóa số "200 mét").
  Fallback "bay" tệ hơn ("bày", 62%).
- **"cọ" GIỮ** ("có", 80%); fallback "chà" không tốt hơn ("trả", 80%).
- **"Top" GIỮ** ("Tốt", lỗi MMS đã biết như v005 "Tốc"; chữ trên hình +
  phụ đề gánh chính tả).

## Nhạc + SFX (toàn CC0, thư viện Core_SFX)
- Nhạc nền `bgm_comedy.ogg` vol 0.12, fade out 2s cuối. Đo ở cửa sổ chỉ
  có nhạc (38,0–38,3s, khoảng lặng 0,6s trước số 1): **-39,4 dB so với
  giọng -19,7 dB → ~19,7 dB dưới giọng**, trong mục tiêu -18 đến -24 dB
  (v003 nóng -11 dB, không lặp lại).
- SFX: whoosh + pop ở 0,1s; pop ở mỗi lần đổi số (3,74 / 11,78 / 21,03 /
  29,28 / 38,40s); ding ở 38,40s (số 1). Không riser (kịch bản không gọi).
- Độ nghe từng SFX riêng lẻ không đo được (chúng trùng với giọng theo
  thiết kế, như v004/v007).

## Hình ảnh (toàn CC0 qua Openverse, nguồn + loại trừ trong `images/sources.txt`)
- 5 ảnh: cá heo nhảy (3504x2336) · châu chấu cận cảnh (2048x1365) · kiến
  cắt lá (606x768) · cá bay (minh họa British Fishes, 3039x1815) · bạch
  tuộc trên rạn san hô (2048x1536). Không dùng mèo AI của video gốc —
  dùng số lớn + ảnh từng con vật (đúng chỉ đạo).
- Ảnh cá bay là **minh họa cổ, không phải ảnh chụp** (không tìm được ảnh
  thật nào tải được — các ứng viên ảnh thật đều 403 hoặc là tranh cổ điển
  sai chủ đề). Ảnh kiến 606px phóng ~1,8x, hơi mềm.

## Render (toàn bộ trên PC, không fallback VPS)
- Mix + loudnorm 2-pass trên PC (`v009_mix.py`, ffmpeg 8.1.2).
- Encode trên PC 15,3s, FFMPEG_EXIT=0, đúng 1537 khung hình, không `-loop 1`,
  giới hạn cứng `-frames:v 1537`. PC không lỗi lần nào.
- Phụ đề SRT→ASS PlayRes 1080x1920, Be Vietnam Pro Bold 56, MarginV 360,
  32 sự kiện, 120 từ.

## Khung hình đã xem
- 1s: card hook "TOP 5 SỰ THẬT VỀ ĐỘNG VẬT" rõ, đúng dấu; kiến + lá rõ;
  #3 mở sẵn "Kiến trồng nấm"; phụ đề "Top 5 sự thật" hiện. PASS.
- 21,5s: card số 3 (kiến), #3 tô sáng, #4/#5 đã mở; phụ đề "Số ba: kiến
  biết" chạm mép dưới hàng #4 (xem Hạn chế). PASS.
- 50,5s: end card "BẠN TIN KHÔNG?" + "Bình luận nhé!" + câu "Bạch tuộc có
  tới ba trái tim." đầy đủ, không cắt; ảnh bạch tuộc rõ; phụ đề "luận
  nhé!" hiện. PASS.

## Hạn chế thật
- Chưa có người nghe (chỉ Whisper 85,0%) — chủ nên nghe một lần trước khi
  đăng, nhất là câu n4b và từ "bạch tuộc" / "Top".
- Câu n4b yếu nhất: Whisper nghe lộn cả đoạn ở file dài ("Nó cỏ trên màu
  thanh kiến, Thiếu thành một bản nhà"); probe rời 80% ("cọ"→"có"). Chữ
  trên hình "NHẠC BẰNG CHÂN" + phụ đề gánh nghĩa.
- "Top" nghe "Tóc", "tuộc" nghe "tuột", "cọ" nghe "có" — đều là lỗi thanh
  của MMS/Whisper; chữ trên hình + phụ đề mang chính tả đúng.
- Hook 209 từ/phút / n2b 177 từ/phút là nhịp nhanh (model đọc câu hỏi
  nhanh, đã biết); tổng speech-only vẫn trong vùng.
- Phụ đề (MarginV 360) nằm trong vùng danh sách: ở 21,5s phụ đề chạm mép
  dưới hàng #4 — vẫn đọc được cả hai, nit cũ như v007.
- Phụ đề trùng chữ end card 2s cuối ("luận nhé!", nit cũ như
  v002/v005/v007).
- Ảnh cá bay là minh họa, không phải ảnh chụp; ảnh kiến hơi mềm (606px).
- Video ngắn hơn audio_final 0,07s (51,23 so với 51,30 — cắt đuôi không
  nghe thấy, như v007 0,033s).
- **Chưa đăng/upload đâu.**

## Sự cố trong quá trình làm (đã sửa)
- `scp` 2 file nguồn tới 1 đường dẫn file đích trên PC tạo ra một THƯ MỤC
  tên `v009_probe.py` chứa cả 2 file (lỗi "can't find '__main__' module").
  Sửa bằng lệnh `move`/`rmdir` trên PC, đặt file đúng chỗ rồi chạy lại.
  Bài học: mỗi lần `scp` chỉ 1 file tới đích là file, hoặc đích phải là
  thư mục có sẵn.
