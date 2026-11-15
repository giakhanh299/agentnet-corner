# QC — v004 "Ông Tư sửa giày" (F7 stickman, #50 85)

**Kết luận: PASS.** Video hoàn chỉnh, đúng spec. Chưa đăng đâu cả.

## File

- `v004.mp4` — **52.36s**, 1080x1920, 30fps, H.264 + AAC 192k, **2,628,973 bytes**
- sha256: `6d2c72d8b20f0cfc7af16d11bcfbeb76f66169ee87d8164cec78d2e57f149c7f`
- Raw Manim: `raw.mp4` 53.03s (dài hơn voice 0.67s; mux dùng `-shortest` nên
  final kết thúc cùng voice 52.36s)
- Script: `script.md` (130 từ theo file gốc; timing.json đếm 131 từ incl. từ
  nối — dùng 131 cho wpm). Voice: `voice.wav` 52.36s. Captions:
  `captions.srt` (31 events) + `captions.ass` (PlayRes 1080x1920,
  Be Vietnam Pro 56, MarginV 300).

## Audio (đo bằng ffmpeg loudnorm / volumedetect)

- **Loudness: -16.05 LUFS** (target ~-16) · **true peak: -2.89 dBTP**
  (≤ -1 dBTP ✓) · LRA 3.40
- **Voice bắt đầu 0.00s** (silencedetect trên voice.wav: silence đầu tiên
  là pause 0.3s sau hook, 3.28–3.79s — không có dead air đầu video)
- **Tốc độ: 150.1 wpm overall** (131 từ / 52.36s, trong vùng an toàn
  150–165). Theo beat (timing.json): hook 167.6 · beat1 140.7 · beat2 160.4 ·
  beat3 136.9 · payoff 170.6 — hook/payoff hơi nhanh (đặc tính MMS: burst nhanh
  đầu câu), beat giữa trong vùng.
- **Whisper large-v3 (PC) check: 122/131 = 93.1%** từ đúng. Lỗi chủ yếu là
  Whisper nghe nhầm ("bé gái"→"bé rái"; "sửa giày"→"sử dài" — nhầm lẫn
  MMS/Whisper đã biết).
- **Probe words (PC, speaking_rate 0.92):** "Tư" OK · "lướt" OK ·
  **"sạp" FAIL — MMS đọc thành "sạc" (xác nhận 2 lần) → đổi thành
  "quầy nhỏ"** theo fallback trong script (probe "quầy" nghe đúng
  "Ông để đôi giày trên quầy nhỏ."). Script.md đã ghi chú swap này.
- **Nhạc + SFX (Core_SFX, CC0):** bgm_calm với volume envelope
  0.11 hook / 0.11 beat1 / 0.12 beat2 / 0.18 beat3 (swell) / 0.0 trong
  0.5s im lặng trước payoff (45.52–46.03) / 0.11 payoff. Ding (0.5) tại
  30.69 (bé gái xuất hiện). Swoosh tại 3.58 / 17.22 / 30.69.
  - BGM đo được: cửa sổ chỉ-nhạc 3.30–3.55s mean **-39.1 dB** (max -29.1),
    so với cửa sổ có voice 20s mean -35.3 / max -17.6 → BGM nghe được,
    rõ ràng dưới voice.
  - Cửa sổ im lặng trước payoff 45.52–46.03: mean **-51.0 dB**, max -29.2 dB
    (không phải silence tuyệt đối — đuôi từ cuối beat 3 còn vang nhẹ).
  - **Swoosh đã hạ 0.4 → 0.2:** file swoosh gốc peak -3.7 dB, ở 0.4 nó chạm
    trần alimiter (-3.1 dB). Sau khi hạ, các cửa sổ transition vẫn đo max
    -3.1/-5.4/-6.2 dB — nhưng kiểm tra voice.wav gốc cho thấy **chính voice
    MMS peak -1.7 dB ở đầu câu 3.58s** (onset to đầu beat), -4.8 dB ở 17.22s,
    -5.9 dB ở 30.69s. Alimiter đang kẹp onset của voice, không phải swoosh.
    Swoosh ở 0.2 giờ nằm dưới voice — an toàn.

## Hình ảnh (Manim rig, SPEC đóng băng — không đổi hằng số rig)

- Render: **VPS** (`.venv/bin/python -m manim render -ql`, nhưng
  `apply_video_config()` ép 1080x1920 30fps nên output là full-res;
  lần 1 ~69s, lần 2 ~3.5 phút tính cả queue). Không render trên PC — VPS
  đã đủ nhanh và cho đúng chất lượng, không cần round-trip PC.
- 2 rig: ông Tư (mũ + tạp dề, `hat_for`/`apron_for` từ `joint_positions`)
  + bé gái (scale 0.62, nơ tóc đỏ accent). Set: sạp (stall), cột đèn
  (sáng lên ở payoff, glow + tint ấm #F2C94C), đường ground. Text card 5
  cái theo beat. Không mưa (đúng script — tránh echo #50).
- **Fix sau lần render 1 (xem frame):**
  1. Người qua đường ở 8s chồng lên ông Tư thành hình 2 đầu — sửa: thu
     nhỏ 0.8 → 0.7 và cho đi SAU ông Tư + sạp (`bring_to_front(tu_sad,
     stall)`), giờ đọc rõ là người nền đi ngang sau sạp.
  2. Đôi giày trên sạp quá nhỏ, khó đọc — phóng to sole 0.55→0.70,
     upper 0.34→0.48.
- Frame đã xem (final v004.mp4): **1s** hook card "KHÔNG AI NHÌN ÔNG MỘT
  LẦN." rõ, đủ dấu, caption "Mỗi ngày, hàng trăm người" rõ ·
  **8s** người qua đường sau lưng ông Tư, không rối · **26s** giày trên
  sạp đọc được, tay ông Tư vươn tới · **33s** bé gái bước vào, chỉ tay,
  card "CỦA AI VẬY ÔNG?" · **40s** bức vẽ (người que + mặt trời đỏ) rõ ·
  **48s/52s** payoff card "CHỈ CẦN MỘT NGƯỜI DỪNG LẠI." đầy đủ, đèn sáng
  ấm, cả hai cười, caption cuối "người dừng lại." rõ.

## Honest limits (chưa nghe bằng tai người — chỉ Whisper)

- Chưa ai nghe thử voice (chỉ Whisper 93.1%). MMS vẫn monotone; pause
  0.3/0.4/0.6s + 0.5s im lặng trước payoff đã làm theo round-2 tuning.
- Per-SFX audibility: ding/swoosh không đo riêng được (chúng trùng với
  voice theo thiết kế); chỉ đo được qua cửa sổ transition (xem mục swoosh).
- Caption trùng lặp text card ở vài chỗ (vd. 52s caption "người dừng lại."
  dưới card "CHỈ CẦN MỘT NGƯỜI DỪNG LẠI." — cùng nit như v002).
- Beat 2 (~13s) gần như tĩnh: ông Tư chỉ có tay đánh bóng dao động; không
  có chuyển động lớn. Walk-cycle của người qua đường/bé gái vẫn là
  stickman đơn giản. Tạp dề đọc hơi giống áo vest dài (hình chữ nhật xám).
- Không dùng gì từ #50 gốc (© Christopher Thomas): story, nhân vật, cảnh,
  câu thoại đều original; chỉ giữ mechanism stickman + text card + nhạc.
- Chưa đăng/upload đâu cả. Không commit/push git (parent xử lý).
