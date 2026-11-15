# QC — V002 "Mỗi lần đăng nhập, bạn đang dùng mẹo của thủy thủ 500 năm trước?" (15/11/2026 ~17:40 +07)

## Kết quả đo (file cuối `v002.mp4`, sha256 `b8b4f7cf18e338ccb645e7753668c925fd889d8553f9612e86b5cb3962a1845b`)

| Hạng mục | Chuẩn | Đo được | Kết luận |
|---|---|---|---|
| Thời lượng | 40–55s | **46,80s** | ✓ |
| Độ phân giải | 1080x1920 | **1080x1920** | ✓ |
| FPS | 30 | **30** (h264, yuv420p, crf 20) | ✓ |
| Âm lượng tích hợp | ~-16 LUFS | **-16,39 LUFS** | ✓ |
| True peak | ≤ -1 dBTP | **-2,42 dBTP** | ✓ |
| LRA | — | 3,80 LU | — |
| Giọng bắt đầu | ~0,1s | **~0,0s** (Whisper segment đầu bắt đầu 0,00s; không dead air) | ✓ |
| Tốc độ nói | 150–165 từ/phút | **160 từ/phút** (125 từ / 46,8s) | ✓ |
| Kích thước file | — | 13,7 MB (video 13.744.485 byte) | — |
| Phụ đề | 125 từ khớp kịch bản | **33 events, 125/125 từ** (chữ kịch bản, thời gian theo Whisper) | ✓ |

## Giọng đọc (MMS-TTS trên PC, kiểm bằng faster-whisper large-v3 trên PC)

- **Giọng cuối: MMS-TTS** (`facebook/mms-tts-vie`, chạy trên PC bằng torch
  CUDA + transformers, miễn phí). Tổng hợp theo từng câu, nối bằng khoảng
  nghỉ 1,2s giữa các câu (kéo tốc độ tổng từ 168 về 160 từ/phút).
- Kiểm Whisper large-v3 trên cả file: khớp **113/123 = 91,9%** từ kịch bản
  (v001 chỉ 70% bằng Whisper Base trên VPS). Các từ khóa đều nghe được:
  "thủy thủ", "khúc gỗ", "nút thắt", "hải lý", "nhật ký", "mật khẩu".
  Lỗi còn lại: "log"→"lô" (2 lần — MMS bỏ phụ âm cuối, xem Giới hạn),
  "năm trăm năm"→"500" (Whisper tự đổi chữ thành số — không phải lỗi giọng),
  "đếm"→"đứng", "tàu"→"tạo", "ghi"→"hi" (mỗi lỗi 1 lần, do Whisper cắt
  đoạn ở ranh giới câu — probe từng câu riêng cho kết quả tốt hơn, xem
  script.md).
- Tốc độ từng câu: hook 176 · beat1 172 · beat2 168 · beat3 200 · payoff 180
  từ/phút (MMS đọc câu ngắn nhanh — giống v001; tốc độ tổng 160 là con số
  quyết định, trong vùng an toàn).

## Nhạc + SFX (lần đầu video có nhạc — sửa điểm yếu của v001/Ep001)

- **Nhạc nền:** `bgm_calm.ogg` (Core_SFX, CC0) — volume 0,12, fade-out 2s
  cuối. Đo được: cửa sổ ngắt câu (chỉ có nhạc, không giọng) ở 5,5–6,5s là
  **-41,1 dB** — nhạc hiện diện nhưng thấp hơn giọng ~22 dB, đúng khung
  -18..-24 dB của framework. Không còn dead air: khoảng nghỉ giữa các câu
  có nhạc lót, không im lặng.
- **SFX:** whoosh + pop ở 0,1s; ding ở 6,68s / 18,34s / 30,00s (đầu mỗi
  beat); camera_click ở 18,34s (cùng ding, khi bằng chứng hiện); boom nhẹ
  (volume 0,8) ở 41,12s (payoff). Tất cả từ Core_SFX (CC0).
- **Mức kiểm chứng SFX:** filtergraph chạy sạch, cả 9 input đều decode
  được, file ra đúng 46,80s; cửa sổ chỉ-nhạc chứng minh đường mix hoạt
  động; so sánh năng lượng từng cửa sổ với track giọng riêng cho thấy mix
  khác giọng riêng ở mọi cửa sổ (do SFX cộng thêm + limiter làm việc).
  **Không** kiểm được từng SFX riêng lẻ bằng đo đạc (mọi SFX đều trùng
  với giọng theo thiết kế, không có cửa sổ chỉ-SFX) — và không nghe được
  bằng tai. Ghi rõ ở đây để không nói quá.

## Khung hình đã xem (thư mục `qc_frames/`, xem trực tiếp từng ảnh)

| Giây | Nội dung khung hình | Quan sát |
|---|---|---|
| 1 | Hook: tranh tàu buồm Schotel 1826 + chữ "MỖI LẦN ĐĂNG NHẬP, / BẠN ĐANG DÙNG MẸO CỦA / THỦY THỦ 500 NĂM TRƯỚC?" + phụ đề "Mỗi lần đăng nhập," | Chữ lớn, rõ, dấu tiếng Việt đúng, không bị cắt. Tàu buồm hiện đầy đủ, kịch tính. Hook kép rõ (chữ + giọng cùng câu). |
| 2 | Hook (tiếp) | Chữ vẫn rõ; phụ đề "bạn đang dùng một". Zoom chậm đang chạy. |
| 8 | Beat 1: dây thừng cuộn trên boong lúc hoàng hôn + nhãn "THẾ KỶ 16 · CHIP LOG" + phụ đề "muốn biết tàu chạy" | Nhãn rõ, dấu đúng (cả "·" và "Ế"). Dây thừng nét, hoàng hôn đẹp. Ảnh hợp nội dung (dây thắt nút). |
| 11,7 | Beat 1 (25%): dây thừng + phụ đề "xuống biển, buộc vào" | Rõ, không che nhau. |
| 20 | Beat 2: trang sổ logbook viết tay 1944 + phụ đề "bằng nút thắt —" | Chữ viết tay + giờ giấc (1050, 1135, 1230) rõ — đúng là sổ logbook thật. Phụ đề rõ trên nền giấy sáng. |
| 23,4 | Beat 2 (50%): sổ logbook + phụ đề "hải lý mỗi giờ." | Rõ. |
| 32 | Beat 3: màn hình đăng nhập Facebook trên điện thoại + phụ đề "cũng cần sổ ghi" | Logo "facebook" + ô Email/Password + nút "Login" đều thấy. Ảnh hơi mềm (nguồn 1024px upscale) nhưng nền xanh phẳng + chữ lớn nên không đáng kể. |
| 35,1 | Beat 3 (75%): màn hình đăng nhập + phụ đề "ghi một dòng vào" | Rõ. |
| 45,5 | End card: nền tối + chữ "Bạn biết chuyện này chưa? / Bình luận nhé!" + phụ đề "luận nhé!" | Chữ end card rõ, KHÔNG bị cắt (đã sửa fontsize 88→64 ở build 2). Phụ đề cuối trùng câu CTA — hơi thừa nhưng không xấu (nhỏ ở dưới, chữ lớn ở giữa). |
| 46,2 | End card (cuối) | Như trên, chữ vẫn đầy đủ. |

## Những gì đã sửa trong quá trình QC (2 lần build)

1. **Build 1 — chữ end card bị cắt hai bên.** Nguyên nhân: dòng "Bạn biết
   chuyện này chưa?" dài 24 ký tự, fontsize 88 vượt quá 1080px (chữ "B"
   đầu dòng bị cắt cả hai dòng). **Cách sửa:** giảm fontsize end card
   88→64 (vẫn đủ lớn, vừa khung với biên an toàn). Build 2 kiểm lại ở
   45,5s và 46,2s: chữ đầy đủ.
2. **Build 0 (chưa build) — `apad` làm ffmpeg chạy vô hạn.** Lần mix âm
   thanh đầu dùng `apad` trên track giọng + `amix duration=first` — apad
   kéo dài track giọng tới vô hạn nên amix không bao giờ kết thúc (chạy
   >4 phút, phải kill). **Cách sửa:** bỏ `apad`, dùng
   `amix duration=longest` (track nhạc đã trim đúng 46,8s). Mix xong
   trong 4,7s.

## Những gì KHÔNG kiểm được

- **Không nghe được âm thanh** (agent không có tai nghe/loa): giọng chỉ được
  kiểm bằng faster-whisper large-v3 trên PC (91,9%); nhạc/SFX chỉ kiểm
  bằng đo năng lượng từng cửa sổ + filtergraph chạy sạch (xem mục Nhạc +
  SFX). Người nghe thật (người dùng) nên nghe thử 1 lần trước khi đăng,
  nhất là từ "log" (MMS đọc thành "lô") và câu beat 3 "Bạn gõ mật khẩu".
- **Từ "log":** MMS-TTS đọc "log" thành "lô/lố" (bỏ phụ âm cuối) — đã thử
  viết "lốc" cũng thành "lô", không sửa được bằng chính tả. Chữ trên màn
  hình ("SỔ LOG" trong phụ đề, "CHIP LOG" ở nhãn beat 1) + phụ đề mang
  đúng chính tả, người xem nghe "lô" nhưng đọc "LOG" sẽ hiểu là từ vay
  mượn. Đây là giới hạn đã biết của MMS, không phải lỗi nghe nhầm ngẫu
  nhiên (xem script.md, mục probe).
- **Độ giữ chân thật:** không có dữ liệu view/retention — chỉ đo được cơ chế
  (hook kép, nhịp cắt, phụ đề, nhạc/SFX), không đo được hiệu quả thực tế.
- **Ảnh nguồn 1024px:** cả 4 ảnh đều là bản 1024px (Openverse trả bản
  editor_1024; đã thử tìm bản gốc Schotel trên Wikimedia Commons nhưng
  không thấy). Crop 9:16 upscale ~2,6x nên ảnh hơi mềm — rõ nhất ở ảnh
  đăng nhập (32s), ít thấy ở tranh tàu và dây thừng. Chấp nhận được cho
  v1, giống mức mềm của v001.

## File trong thư mục

- `v002.mp4` (13,7 MB) — video cuối. `script.md` — kịch bản + nguồn + ghi
  chú giọng + kết quả probe. `script_text.txt` — lời thoại thuần (5 câu).
- `voice.wav` (1,5 MB, 16 kHz mono, 46,77s) — giọng MMS-TTS từ PC.
  `voice_norm.wav` — giọng đã chuẩn hóa -16,44 LUFS. `audio_final.m4a` —
  mix cuối (giọng + nhạc + SFX, -16,39 LUFS / -2,42 dBTP).
- `captions.srt` (33 đoạn, chữ đúng kịch bản) + `captions.ass` (bản dùng để
  đốt vào video) + `v002_fw_segments.txt` / `v002_fw_heard.txt` (bản
  Whisper large-v3 nghe được trên PC — chỉ để đối chiếu).
- `images/` — 8 ảnh tải về (4 dùng + 4 loại, xem `images/sources.txt`) +
  `img_candidates.json`.
- `assemble_filter.txt` — filtergraph ffmpeg đầy đủ (tái tạo được video).
- `v002_tts.py` / `v002_tts_run.ps1` — tổng hợp giọng + kiểm Whisper trên PC.
- `v002_probe.py` / `v002_probe2.py` (+ .ps1) — probe từ rủi ro của MMS.
- `search_images.py`, `download_images.py` — tìm + tải ảnh Openverse.
- `build_captions.py` — ráp phụ đề từ segment Whisper + chữ kịch bản.
- `qc_frames/` — 10 khung hình QC đã xem (f_1/2/8/11.7/20/23.4/32/35.1/45.5/46.2).

## Tình trạng: PASS — đủ điều kiện xem thử / đăng thử (chưa đăng, chưa upload đâu cả)
