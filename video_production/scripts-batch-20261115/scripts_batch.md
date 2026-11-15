# Tóm tắt lô kịch bản — 2026-11-15 (v003 + v004 + v005)

**Bối cảnh:** người dùng chọn "Viết sẵn 3 kịch bản tiếp theo" (17:42).
Ba kịch bản viết theo lô từ ngân hàng 30 video đã phân tích sâu — mỗi
kịch bản một format ưu tiên khác nhau (Visual Essay · Truyện stickman
cảm xúc · Countdown). **Chỉ kịch bản — chưa sản xuất video, chưa tổng
hợp giọng, chưa đăng/upload gì.**

## Bảng tổng kết

| # | Video | Chủ đề | Công thức | Từ | Tốc độ (45/50s) | Nguồn gốc |
|---|---|---|---|---|---|---|
| v003 | #77 (90) | Cáp thang máy đứt ở tầng 85 — nhảy lên thì sống không? | F2 Visual Essay, 45s | 123 | ~164 từ/phút | T01, deep-analysis-5x85 |
| v004 | #50 (85) | Ông Tư sửa giày — chỉ cần một người dừng lại | F7 stickman cảm xúc, 50s, có giọng kể | 130 | ~156 từ/phút | C01, deep-analysis-5x85 |
| v005 | H02 #69 (78) | Top 5 câu nói huyền thoại của mẹ | F3 Countdown, 45s | 119 | ~159 từ/phút | H02, deep-analysis-25 |

**Thứ tự sản xuất đề xuất:** v003 → v005 → v004. Lý do: v003 và v005
là format rẻ nhất (Visual Essay + Countdown, 1,5–3 giờ/video, dùng
ảnh stock + giọng AI); v004 là stickman cảm xúc, cần rig 2 nhân vật
+ nền góc phố, đắt hơn (2–6 giờ). Nếu muốn thử stickman sớm thì đổi
v004 lên trước v005 — cả ba kịch bản đều đã sẵn sàng, thứ tự không
ảnh hưởng chất lượng.

## Điểm chung của cả 3 kịch bản
- **Kịch bản gốc tiếng Việt hoàn toàn**, không dịch lời thoại của video
  gốc; hook kép (chữ + giọng cùng một câu) trong 3s đầu; giọng vào từ
  0,1s; chuẩn -16 LUFS; phụ đề từng đoạn ngắn.
- **MMS-TTS-friendly:** không có số, năm, tên nước ngoài trong lời
  thoại (chỉ hiện trên hình); mỗi kịch bản có danh sách từ cần probe
  trên PC trước khi chốt giọng (xem từng file).
- **Nhạc + SFX từ thư viện Core_SFX** (toàn CC0): v003 dùng
  bgm_suspense; v004 dùng bgm_calm; v005 dùng bgm_comedy — mỗi kịch
  bản ghi rõ tên file + vị trí đặt SFX theo giây.
- **Không dùng lại tài sản của video gốc:** v004 đặc biệt lưu ý —
  truyện hoàn toàn mới (nhân vật, bối cảnh, câu chuyện, câu chốt đều
  khác #50; chỉ giữ cơ chế).

## Sự thật đã kiểm chứng (mỗi kịch bản có nguồn đầy đủ trong file)
- **v003:** nhảy lên chỉ trừ ~4 m/s (ScienceABC); rơi từ tầng 20 đã
  ~108 km/h (ScienceABC); thang máy có ≥4 lớp an toàn độc lập, bộ điều
  tốc tác động ở ~115% tốc độ định mức (Otis / AboutElevators); phanh
  Otis trình diễn 1854; "nằm ngửa" là tư thế được gợi ý nhiều nhất
  nhưng chỉ mang tính lý thuyết, không đảm bảo sống sót (ZestyHabit).
- **v004:** không có khẳng định sự thật nào — truyện hư cấu hoàn toàn.
- **v005:** #2 "Con nhà người ta" và #3 "Hồi bằng tuổi mày…" được xác
  nhận là câu nói quen thuộc trong văn hóa Việt (BlogRadio, Tripi);
  thứ hạng là xếp hạng biên tập, không phải khảo sát.

## Sự thật KHÔNG kiểm chứng được (và cách xử lý)
- **v003 — con số "72 km/h" của video gốc #77: không kiểm chứng
  được.** Không nguồn nào xác nhận tốc độ rơi 72 km/h cho cú rơi từ
  tầng 85. **Không dùng trong kịch bản.** Thay bằng con số đã kiểm
  chứng của ScienceABC: rơi từ tầng 20, tốc độ chạm đất khoảng
  108 km/h ("hơn một trăm cây số một giờ").
- **v003 — Betty Lou Oliver** (sống sót sau khi rơi 75 tầng, Empire
  State Building 1945): đã kiểm chứng qua ScienceABC, nhưng KHÔNG đưa
  vào lời thoại (không đủ ngân sách từ); chỉ ghi trong mục nguồn của
  file v003 để bước sản xuất tham khảo.
- **v005:** không có sự thật nào chưa kiểm chứng — danh sách không
  chứa khẳng định số liệu.
- **v004:** không áp dụng (truyện hư cấu).

## Từ cần probe trên PC trước khi sản xuất (tổng hợp từ 3 file)
- v003: "tám mươi lăm", "kẹp chặt ray", "ngửa".
- v004: "Tư" (tên riêng), "lướt", "sạp".
- v005: "phăng phắc", "Tao", "trĩu".
- Quy tắc probe theo bài học v002: probe từng câu riêng bằng MMS-TTS
  trên PC + kiểm bằng faster-whisper large-v3; nếu hỏng thì đổi từ
  theo gợi ý trong từng file (đã ghi sẵn phương án thay thế).

## Quyết định biên tập đáng chú ý (ghi lại để không bị "sửa" mất)
1. **v003:** nói "không chắc sống, nhưng là cơ hội tốt nhất" cho tư
   thế nằm ngửa — không hứa hẹn tuyệt đối (nguồn ZestyHabit). Đừng
   sửa thành "chắc chắn sống sót".
2. **v004:** có giọng kể, không làm bản câm như video gốc — lý do ghi
   trong file (pipeline giọng đã chứng minh; giọng + thẻ chữ = hook
   kép; bản câm phụ thuộc hoàn toàn vào nhạc).
3. **v005:** #1 là cảm xúc ("Mẹ không cần gì đâu…"), không phải trò
   đùa — cú lật cảm xúc sau 4 trò đùa là payoff có chủ đích. Đừng
   sửa #1 thành một trò đùa khác. Victory sting ở #1 dùng NHẸ.

## File trong thư mục này
- `script_v003-lift-45s.md` — kịch bản v003 (123 từ) + nguồn + từ
  cần probe.
- `script_v004-silent-50s.md` — kịch bản v004 (130 từ) + cảnh báo
  bản quyền + quyết định có giọng kể.
- `script_v005-countdown-45s.md` — kịch bản v005 (119 từ) + nguồn +
  quyết định #1 cảm xúc.
- `scripts_batch.md` — file này.

## Việc còn lại trước khi sản xuất (cho bước sau, không phải lô này)
- Probe các từ rủi ro trên PC (danh sách ở trên) và chốt từ thay thế
  nếu cần.
- Chuẩn bị tài sản theo ghi chú từng file (đồ họa trục thang máy v003;
  rig ông Tư + bé gái + nền góc phố v004; khung danh sách + 5 hình
  v005).
- Sản xuất theo thứ tự đề xuất (v003 → v005 → v004) với pipeline
  v001/v002 (MMS-TTS trên PC → faster-whisper kiểm → assemble +
  loudnorm -16 LUFS → QC frame).
