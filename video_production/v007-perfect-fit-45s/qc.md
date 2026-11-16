# QC — V007 "Top 5 thứ vừa khít hoàn hảo" (F3 Countdown, H01 #68)

**Kết quả: PASS.** Không đăng/upload ở đâu. File: `v007.mp4`.

## Số đo (đo bằng ffprobe / loudnorm / faster-whisper large-v3 trên PC)

- `v007.mp4`: **48,37s, 1080x1920, 30fps, H.264 2.085.538 bps + AAC 191.522
  bps, 48 kHz stereo, 13.821.811 bytes, sha256
  `ab6fbf2cb4726710150e36de117534b128fb2e3649664b5181806f7ea76a8b5b`**
  (1.451 khung hình; cap `-frames:v 1452`).
- Âm thanh (đo trên mp4 cuối): **-15,99 LUFS, true peak -5,01 dBTP, LRA 3,50**
  — đúng chuẩn ~-16 LUFS, TP ≤ -1 dBTP. (Mix thô -19,03 LUFS → loudnorm
  2-pass + `alimiter=limit=0.7:level=false` ra -16,87 → cộng thêm
  `volume=0.87dB` rồi đo lại = -16,00 trên `audio_final.m4a`; mp4 cuối
  -15,99. `level=true` là auto-gain, SAI — không dùng.)
- Giọng: vào từ **0,00s** (unit đầu tiên bắt đầu 0,0; không có dead air —
  silencedetect ≥0,2s ở -50 dB: 0 đoạn im). **117 từ, 158 từ/phút
  speech-only, 145 từ/phút tổng thể** (4,0s khoảng lặng giữa các mục là
  nhịp thở countdown có chủ đích, như v005: 143 tổng thể).
- Whisper large-v3 trên PC: **97/117 = 82,9%** nghe đúng. Các từ nghe sai
  chủ yếu là Whisper nghe nhầm giọng nhanh ("video"→"gieo", "Số năm"→"Số
  mâm", "tải"→"phải", "sinh"→"xin", "đúng"→"đung", "lỗ"→"lộ") — các probe
  riêng lẻ đã chứng minh MMS nói đúng những từ này (q4 "chốt cửa sập vào
  đúng lỗ" 100%, t2 n4a 100%, t3 CTA 88%).
- BGM + SFX có mặt (đo bằng năng lượng cửa sổ): cửa sổ riser 35,87–36,47s
  (giọng im) RMS -28,1 dB, peak -10,5 dB → riser rõ; cửa sổ pause
  5,76–6,06s (chỉ BGM) RMS -40,7 dB so với giọng -17,9 dB → BGM ~23 dB
  dưới giọng, trong vùng -18 đến -24 dB.

## Kịch bản + probe (MMS-TTS speaking_rate 0,92, PC)

- Lời thoại cuối: 117 từ (kịch bản gốc 121 từ). **#1 là chốt cửa, không
  phải bánh xe** — giữ đúng quyết định biên tập; bánh xe chỉ là hook/mục
  #2. Không facecam. Không khẳng định sự thật nào (xếp hạng biên tập).
- Đổi từ sau probe (5 vòng probe trên PC, xem `v007_probe*.py`):
  - "tra vào ổ" → **"cắm vào ổ khóa"** (q5/r1/r2/s1 đều hỏng "tra"/"ổ";
    s2 "cắm vào ổ khóa" 85%, tốt nhất; "cắm"+"khóa" nghe sạch).
  - "bánh xe tải lăn đúng vào rãnh, khít từng milimét" → **"bánh xe tải
    chạy đúng vào khe. Như thể cái khe sinh ra cho nó."** ("lăn"→"lăng"
    mọi lần probe; "rãnh"→"rảnh"; "milimét"→"mi nát"; q3 "chạy đúng vào
    khe" 100%, s3 câu 2 100%).
  - "khít" **GIỮ** ("khít"→"khiếp" 3/3 trong track đầy đủ nhưng probe
    riêng lẻ cùng câu đó nghe đúng: t1 86%, t2 100%, t3 88% — đó là
    nhiễu phân đoạn của Whisper, không phải lỗi MMS; không đổi sang
    "vừa vặn").
  - "bản lề" GIỮ (100%), "cạch" GIỮ (100%), "chốt cửa" GIỮ (q4 100%).
  - "—" thay bằng "," chỉ khi tổng hợp (hook, n1b); caption giữ "—" như
    kịch bản. Caption: 32 event, 119 token (2 dấu "—" tính riêng).
- Pauses: 0,3s sau hook, 0,3s trong beat, 0,4s giữa các beat, 0,6s trước
  #1 (vùng riser), 0,4s trước CTA.

## Hình ảnh (5 ảnh, toàn CC0/CC BY qua Openverse — xem images/sources.txt)

- #5 chìa khóa trong ổ (WDnet Studio, CC0, 960x640); #4 bản lề đồng chạm
  khắc (Wmpearl, CC0, 1500x2670 dọc); #3 hai bàn tay nâng sỏi (CC0,
  1024x683); #2 bánh xe đạp trong rãnh ray (joshua_putnam, CC BY,
  1024x768); #1 chốt cửa thép (Jeffrey, CC BY, 1024x576). 11+ ảnh khác
  bị loại có lý do (xe hơi, nhà kho, LEGO, tàu nguyên chiếc…).
- Thẻ danh sách (build_cards.py, PIL + Be Vietnam Pro): 7 stage — hook
  (#3 mở sẵn, #1 chưa lộ) → #5 → #4 → #3 → #2 → #1 (highlight hổ phách)
  → end card "CÁI NÀO VỪA KHÍT NHẤT?". Nền kem, chữ Be Vietnam Pro.

## Nhạc + SFX (Core_SFX, toàn bộ CC0)

- Nhạc nền `bgm_comedy.ogg` (cắt 48,40s, vol 0,12, fade-out 2s cuối).
- SFX: whoosh + pop ở 0,1s; pop ở mỗi lần mở mục (6,06 / 14,98 / 22,04 /
  29,57 / 36,47s); riser 33,47–36,47s dẫn vào #1; ding ở 36,47s (mở #1);
  victory NHẸ ở 40,13s (cắt 1,5s, vol 0,35 — #1 là payoff, không át
  giọng). Không có laugh (kịch bản không yêu cầu).
- Mix: `amix duration=longest` (không dùng `apad` + `duration=first` —
  treo máy, bài học v002).

## Render (PC, theo lệnh của chủ 21:53 15/11)

- Encode trên PC: ffmpeg 8.1.2, **12,5s, FFMPEG_EXIT=0, 1.451 khung hình**,
  zoompan 1,0→1,05 + xfade 0,4s + `ass=captions.ass` (Be Vietnam Pro,
  MarginV 360), mux `audio_final.m4a` luôn trong cùng lệnh.
- KHÔNG dùng `-loop 1` (bài học v003: input vô hạn → encode chạy mãi);
  cap cứng `-frames:v 1452`.
- Không fallback về VPS: PC reachable suốt quá trình.

## QC khung hình (đã xem: 1s / 8s / 17s / 31s / 38s / 47,5s)

- 1s: tiêu đề "TOP 5 THỨ VỪA KHÍT HOÀN HẢO" to, rõ, đúng dấu; ảnh sỏi
  trong tay rõ; hàng #3 highlight; các hàng chưa mở "• • •"; caption
  "Mọi thứ sinh ra" hiện rõ. PASS.
- 8s (#5): ảnh chìa khóa trong ổ rõ; #5 highlight "Chìa khóa cắm vào ổ";
  caption "cắm vào ổ khóa," rõ. PASS.
- 17s (#4): ảnh bản lề đồng rõ; #4 highlight "Bản lề cửa khép lại";
  caption "cửa khép lại vừa" rõ. PASS.
- 31s (#2): ảnh bánh xe trong rãnh ray rõ; #2 highlight "Bánh xe chạy
  vào khe"; caption "tải chạy đúng vào" rõ. PASS.
- 38s (#1): ảnh chốt cửa rõ; cả 5 hàng đã mở, #1 highlight hổ phách
  "Chốt cửa sập vào lỗ"; caption "sập vào đúng lỗ." rõ. PASS.
- 47,5s: end card "CÁI NÀO VỪA KHÍT NHẤT?" + "Bình luận nhé!" + câu
  trích "Chốt cửa sập vào đúng lỗ." hiện đầy đủ, không bị cắt. PASS.

## Giới hạn trung thực (chưa nghe bằng tai người)

- Không ai nghe giọng bằng tai — chỉ Whisper 82,9% (xem phân tích ở trên:
  phần lớn là Whisper nghe nhầm, không phải MMS nói sai; riêng "khít"
  đã được probe riêng lẻ xác nhận đúng). Người dùng nên nghe một lần
  trước khi đăng, nhất là "khít" (hook/#4/CTA), "ổ khóa", "cắm".
- SFX pop/ding/victory không đo riêng được từng cái (chúng trùng với
  giọng theo thiết kế) — chỉ riser + BGM đo được bằng cửa sổ năng lượng.
- Ảnh 960–1500px, upscale nhẹ khi cắt 1080x710 — hơi mềm, chấp nhận
  được như v002/v005.
- Caption trùng chữ end card trong 2s cuối (nit như v002/v003/v005).
- Caption nằm trong vùng danh sách (MarginV 360) — đọc được, không che
  chữ nhãn nào, nhưng hơi chật (nit như v005; sửa sau: MarginV ~420
  hoặc dời danh sách lên).
- Video ngắn hơn audio 0,033s (1.451 vs 1.452 khung) — đuôi audio cuối
  bị cắt 33ms, không nghe được.
- Tổng thể 145 từ/phút dưới sàn 150 (có chủ đích, nhịp thở countdown —
  như v005: 143).
- Ảnh #4 là bản lề bảo tàng (trang trí, tối) — đọc được là bản lề nhưng
  không phải cảnh "cửa đang khép"; ảnh #2 là bánh xe đạp trong rãnh ray,
  không phải bánh xe tải (ghi chú kịch bản cho phép đổi nếu không tìm
  được clip #2 đủ đã — cơ chế "bánh trong rãnh" được giữ).
- KHÔNG đăng. Chờ lệnh của chủ.
