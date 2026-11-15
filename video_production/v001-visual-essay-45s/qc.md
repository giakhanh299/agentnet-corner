# QC — V001 "Vì sao cửa sổ máy bay lại tròn?" (15/11/2026 ~15:57 +07)

## Kết quả đo (file cuối `v001.mp4`, sha256 `e65285dd625caccc…`)

| Hạng mục | Chuẩn | Đo được | Kết luận |
|---|---|---|---|
| Thời lượng | 40–55s | **47,10s** | ✓ |
| Độ phân giải | 1080x1920 | **1080x1920** | ✓ |
| FPS | 30 | **30** (h264, yuv420p, crf 20) | ✓ |
| Âm lượng tích hợp | ~-16 LUFS | **-16,74 LUFS** | ✓ |
| True peak | ≤ -1 dBTP | **-3,05 dBTP** | ✓ |
| Sample peak | — | -3,1 dB (volumedetect) | ✓ |
| LRA | — | 3,70 LU | — |
| Giọng bắt đầu | ~0,1s | ~0,05s (không dead air) | ✓ |
| Tốc độ nói | 150–165 từ/phút | **160 từ/phút** (126 từ / 47,1s) | ✓ |
| Kích thước file | — | 12,6 MB (video 12.594.940 byte) | — |

## Khung hình đã xem (thư mục `qc_frames/`, xem trực tiếp từng ảnh)

| Giây | Nội dung khung hình | Quan sát |
|---|---|---|
| 0 | Hook: cửa sổ tròn, núi/mây + chữ "Bạn có biết / cửa sổ máy bay tròn / không phải để đẹp?" | Chữ lớn, rõ, dấu tiếng Việt đúng, không bị cắt. Ảnh lấp đầy khung, không viền đen. (Phụ đề chưa hiện ở đúng 0,00s vì đoạn phụ đề đầu bắt đầu 0,05s — đúng thiết kế.) |
| 1–2 | Hook (tiếp) | Zoom chậm đang chạy, chữ vẫn rõ. |
| 6,5 | Beat 1: mũi Comet 4 trong bảo tàng + nhãn "1952 · Comet" + phụ đề "phản lực đầu tiên" | Nhãn rõ; phụ đề trắng viền đen, đúng vị trí 1/3 dưới giữa, dễ đọc trên nền sáng. |
| 11,8 | Beat 1 (cuối): Comet + nhãn + phụ đề "tan giữa trời." | Rõ, không che nhau. |
| 20 | Beat 2: cửa sổ tròn lúc hoàng hôn, cánh máy bay | Ảnh đẹp, hơi mềm (nguồn 960px upscale ~2x) nhưng chấp nhận được — trời + cánh đơn giản nên ít thấy mờ. |
| 23,6 | Beat 2: cửa sổ hoàng hôn + phụ đề "suất lên nhiều lần," | Phụ đề rõ trên nền tối. |
| 35,3 | Beat 3: nhìn từ máy bay xuống cửa sông Đạm Thủy + phụ đề "suất trải đều —" | Ảnh nét (nguồn 4000px), phụ đề rõ. |
| 46,0 | End card: nền tối + chữ lớn "Bạn có tin không? / Bình luận nhé!" + phụ đề "Bình luận nhé!" | Chữ end card rõ, không bị cắt. Phụ đề cuối trùng câu CTA — hơi thừa nhưng không xấu (nhỏ ở dưới, chữ lớn ở giữa). |

## Những gì đã sửa trong quá trình QC (3 lần build)

1. **Build 1 — phụ đề không hiện.** Nguyên nhân: dùng filter `subtitles` với
   `force_style` trên file SRT. libass dùng PlayRes mặc định 384x288 cho SRT
   nên FontSize 56 bị phóng 1920/288 = 6,67 lần (~375px) và MarginV 300 đẩy
   chữ ra khỏi khung. `original_size` không sửa được. **Cách sửa:** chuyển
   sang file ASS (`captions.ass`, PlayResX 1080 / PlayResY 1920, style Noto
   Sans Bold 56, MarginV 300) và dùng filter `ass`. Đã kiểm bằng test riêng
   trước khi build lại.
2. **Build 2 — true peak +0,24 dBTP sau khi đã giảm âm lượng -1,2 dB.**
   Nguyên nhân: bộ mã hóa AAC 128k tạo overshoot đỉnh thật tới +2,4 dB trên
   giọng MMS (nhiều âm bật). **Cách sửa:** không giảm âm lượng toàn cục
   (làm video nhỏ tiếng) mà giới hạn đỉnh bằng `alimiter` — nhưng lần đầu
   dùng sai `level=true` (đó là "auto level" = tự tăng gain, làm âm lượng
   vọt lên -13,16 LUFS). **Cách đúng:** `alimiter=limit=0.7:level=false`
   (chỉ cắt đỉnh, không tự tăng gain) + AAC 192k (overshoot nhỏ hơn).
   Kết quả cuối: -16,74 LUFS / -3,05 dBTP.
3. **Âm thanh cuối được remux** (video build 3 giữ nguyên, chỉ thay track âm
   thanh đã giới hạn đỉnh) — tránh mã hóa lại video.

## Những gì KHÔNG kiểm được

- **Không nghe được âm thanh** (agent không có tai nghe/loa): giọng chỉ được
  kiểm bằng Whisper Base (khớp 70% từ kịch bản; các từ khóa đều nghe được —
  xem script.md). Người nghe thật (người dùng) nên nghe thử 1 lần trước khi
  đăng, nhất là các từ "góc nhọn", "khoang phồng", "vuông vức".
- **Nhạc nền:** không có (chưa có thư viện nhạc có bản quyền) — video chỉ có
  giọng đọc + phụ đề, đúng kế hoạch v1.
- **Độ giữ chân thật:** không có dữ liệu view/retention — chỉ đo được cơ chế
  (hook kép, nhịp cắt, phụ đề), không đo được hiệu quả thực tế.

## File trong thư mục

- `v001.mp4` (12,6 MB) — video cuối. `script.md` — kịch bản + nguồn + ghi
  chú giọng. `script_text.txt` — lời thoại thuần. `voice.wav` (4,4 MB) —
  giọng MMS-TTS đã chuẩn hóa (-16,13 LUFS / -1,00 dBTP trước khi giới hạn).
- `captions.srt` (32 đoạn, chữ đúng kịch bản) + `captions.ass` (bản dùng để
  đốt vào video) + `captions_whisper.srt` (bản Whisper nghe được — chỉ để đối
  chiếu, chữ sai ~30%).
- `images/` — 4 ảnh + `sources.txt` (nguồn + giấy phép từng ảnh).
- `assemble_filter.txt` — filtergraph ffmpeg đầy đủ (tái tạo được video).
- `synth_sentences.py`, `synth_mms.py`, `gen_voice.py` — code tổng hợp giọng.
- `voice_piper.wav`, `probe*.wav`, `voice_*check*.txt` — mẫu đối chứng các
  giọng đã thử và kết quả Whisper.
- `qc_frames/` — 9 khung hình QC đã xem (f_0/1/2/6.5/11.8/20/23.6/35.3/46.0).

## Tình trạng: PASS — đủ điều kiện xem thử / đăng thử (chưa đăng, chưa upload đâu cả)
