# QC — Ep001 "Cùng làm 10 tiếng, sao người giàu, người nghèo?" (2026-11-15)

**Kết luận: ĐẠT.** Video đầu tiên của repo stickman đã hoàn thành, đo đạc đầy đủ.
Chưa đăng/upload đâu cả. Chưa có người nghe thật (chỉ kiểm bằng Whisper).

## File

- `output/final.mp4` — sha256 `3f40bf21a0616d30baaa92e52cf6bd43241e067dbf94da6cdf508b72378fb405`,
  3.214.593 byte
- `output/raw.mp4` (Manim, chưa tiếng) — sha256 `a6be05ce884f5cd36add7ca7a5cc59969e201386ce374b0eb69f15437b17b6ee`
- `voice.wav` — sha256 `6c37649ff4e14792bea7dd1d051bb8e257764958452b91a63e9ad7a3870133c9`

## Thông số đo được (ffprobe / ffmpeg loudnorm / silencedetect)

| Hạng mục | Đo được | Chuẩn | Kết quả |
|---|---|---|---|
| Độ phân giải | 1080x1920 | 1080x1920 | ĐẠT |
| FPS | 30/1 | 30 | ĐẠT |
| Thời lượng | 48,80s | 40–55s | ĐẠT |
| Codec | h264 + aac 192k | — | ĐẠT |
| Độ lớn tích hợp | **-17,40 LUFS** | ~-16 LUFS | LỆCH NHẸ (thấp hơn 1,4 LUFS; xem ghi chú) |
| True peak | **-2,91 dBTP** | ≤ -1 dBTP | ĐẠT (có biên an toàn) |
| LRA | 3,60 | — | — |
| Giọng bắt đầu | 0,105s | ~0,1s | ĐẠT |
| Lời thoại | 137 từ / 48,75s ≈ 174 từ/phút | F7: 125–138 từ; 150–165 từ/phút | Từ ĐẠT; tốc độ hơi nhanh (xem ghi chú) |

## Khung hình đã xem (final.mp4)

- **0s:** caption đã hiện ("Cùng làm mười tiếng mỗi ngày, / sao một người giàu,
  một người vẫn nghèo?"); thẻ hook đang fade-in (xong ở 0,5s); stickman
  surprised — hai tay rõ, chân dang nhẹ.
- **1s:** thẻ hook "CÙNG LÀM 10 TIẾNG / Sao người giàu, người nghèo?" rõ, dấu
  đúng; caption 2 dòng rõ, không cắt.
- **2s:** giống 1s (hook giữ nguyên).
- **12s (25%):** beat 1 — An đang đi bộ (giữa nhịp), đồng hồ treo bên phải,
  thẻ "AN ĐỔI GIỜ LẤY TIỀN" rõ; caption "sáng mai lại cày tiếp," rõ.
- **24s (50%):** beat 2 — Bình chỉ tay phải, mặt cười, chân dang; túi tiền
  trái + chồng xu phải rõ; caption 2 dòng rõ, dấu đúng.
- **36s (75%):** beat 3 — An (trái, mặt buồn, đang đi tại chỗ) + Bình (phải,
  mặt cười) + túi tiền ĐÃ DỜI sang bên phải Bình (không còn đè lên chân);
  caption "Bình không bán giờ nữa." rõ.
- **46s:** payoff — Bình giữa khung vẫy tay (tay vẫy rõ, không bị đầu che),
  thẻ "GIÀU LÀ LÀM KHÁC ĐI / Bạn chọn bên nào?"; caption 2 dòng rõ.

Không có frame nào: chữ mất dấu, chữ bị cắt, tay/chân chui vào đầu,
caption tàng hình hay tràn khung.

## Caption

- 16 events, từ `captions.srt` (timestamp Whisper Base) + chữ KHỚP KỊCH BẢN
  (không dùng chữ Whisper nghe nhầm). Kiểm đếm: 137/137 từ khớp script.
- Burn bằng filter `ass` từ `captions.ass` (PlayRes 1080x1920, Be Vietnam Pro 56,
  trắng + viền đen, dưới-giữa, MarginV 300). Đã xem trực tiếp: caption hiện
  rõ ở mọi frame kiểm tra.

## Âm thanh / giọng

- Giọng: MMS-TTS facebook/mms-tts-vie (local, miễn phí), tổng hợp từng beat
  riêng (`synth_voice.py`), nối bằng khoảng lặng 0,3 / 0,4 / 0,4 / 0,7s
  (0,7s trước câu chốt theo F7), cắt 0,28s lặng đầu → giọng bắt đầu 0,105s.
- Thời lượng từng beat (đo thật): hook 4,46s · beat 1 12,59s · beat 2 13,70s ·
  beat 3 10,75s · payoff 5,73s · tổng 48,75s.
- Whisper Base nghe lại MMS: nghe nhầm nhiều (vd "Giàu" → "Dầu", "túi" →
  "tuyết") — đây là lỗi Whisper trên giọng MMS đơn điệu, đã biết từ v001
  (~30% nghe sai). Caption đã sửa theo kịch bản nên không ảnh hưởng video.
- Piper đã thử so sánh: 29,9s cho 137 từ ≈ 275 từ/phút (quá nhanh) và theo
  kết quả v001 thì phá dấu tiếng Việt ("góc nhọn" → "khóc ngọt") → LOẠI.
  Edge TTS: file 0 byte (WebSocket bị egress proxy chặn) → LOẠI. gTTS: 429.

## Lỗi đã tìm và sửa trong lúc làm

1. **Pose "một tay + cột":** `POSE_SURPRISED` hai tay cùng góc 1,4 vẽ chồng
   thành một tay; chân thẳng + thân thẳng vẽ thành một cột. Sửa:
   tay trái 1,15/khuỷu 0,7, tay phải giữ 1,4; thêm thế chân
   hip_l=0,12 / hip_r=-0,12 cho `POSE_SURPRISED`, `POSE_HAPPY`, `POSE_SAD`,
   `think_pose()`, `point_pose()` (chỉ sửa pose, SPEC đóng băng không đụng).
   Rig test `tests/test_rig.py` chạy lại: ALL PASSED. Render lại 48s.
2. **Túi tiền đè chân Bình (beat 3):** `bag3` đặt cùng x=2,2 với Bình →
   dời sang x=3,2, cạnh chân Bình.
3. **`assemble.py --srt` CHƯA DÙNG ĐƯỢC như cũ:** filter `subtitles` trên .srt
   render ở PlayRes 384x288 rồi scale 6,67x → chữ tàng hình/ngoài khung
   (bài học v001). ĐÃ SỬA `tools/assemble.py`: tự convert .srt → .ass
   (PlayRes 1080x1920, Be Vietnam Pro 56) rồi dùng filter `ass`; thêm
   `alimiter=limit=0.7:level=false` sau loudnorm để chặn true peak
   (`level=true` là auto-gain, từng đẩy một bản v001 lên -13,16 LUFS).
   Đường `--srt` nay ĐÃ TEST XONG: assemble chạy ngon lần đầu (42s),
   caption hiện rõ ở mọi frame kiểm tra.

## Ghi chú / giới hạn (trung thực)

- Độ lớn -17,40 LUFS thấp hơn mục tiêu ~-16 đúng 1,4 LUFS (loudnorm 1-pass
  + alimiter cắt đỉnh). Nghe trên Shorts vẫn ổn (YouTube tự chuẩn hóa);
  nếu muốn đúng -16,0 thì làm thêm 1 pass loudnorm đo lại — chưa làm.
- Tốc độ nói ~174 từ/phút, trên vùng an toàn 150–165 nhưng trong dải
  160–200 mà F7 cho phép với giọng Việt AI. Giọng MMS đơn điệu, không
  có nhạc nền (thư viện nhạc/SFX vẫn trống) — video nghe "khô" hơn bản
  có nhạc. Đây là điểm yếu lớn nhất của tập này.
- Không có người nghe thật: độ rõ của giọng MMS với tai người chưa được
  xác nhận (chỉ có Whisper, mà Whisper nghe sai ~30%).
- Ảnh tĩnh giữa nhịp đi bộ đôi khi trông hơi gượng (chân chéo nhau) —
  khi chạy video thì đọc là đang đi, đã chấp nhận.
- Beat 2 dài 13,7s với một tư thế suy nghĩ tĩnh ~4s — hơi dài cho một
  hình tĩnh; tập sau nên thêm chuyển động nhỏ (gật đầu / túi tiền nảy).
