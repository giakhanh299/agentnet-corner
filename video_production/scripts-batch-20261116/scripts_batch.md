# Tóm tắt lô kịch bản — 2026-11-16 (v006 + v007 + v008)

**Bối cảnh:** làm trước theo chỉ đạo của chủ (15/11 ~15:50: làm việc chủ
động, tự tìm việc khi rảnh, làm trước tiến độ; và 15/11 ~17:34: chủ đề lấy
từ ngân hàng 30 video đã phân tích sâu). Lô trước (v003 + v004 + v005)
đã sản xuất xong cả 3 video; chưa có kế hoạch v006+ nào trong workspace
(kiểm tra 16/11 08:31: không có file v006/v007/v008 nào). Ba kịch bản
này viết theo lô từ 3 chủ đề chưa dùng trong ngân hàng 30 — mỗi kịch bản
một format ưu tiên khác nhau (Visual Essay · Countdown · Truyện stickman
cảm xúc). **Chỉ kịch bản — chưa sản xuất video, chưa tổng hợp giọng, chưa
đăng/upload gì.** Sản xuất theo lệnh của chủ như lần trước.

## Bảng tổng kết

| # | Video | Chủ đề | Công thức | Từ | Tốc độ | Nguồn gốc |
|---|---|---|---|---|---|---|
| v006 | T03 #80 (83, điều chỉnh từ 87) | Nước vừa sôi vừa đóng băng cùng một lúc | F2 Visual Essay, 45s | 122 | ~163 từ/phút | T03, deep-analysis-5x85 |
| v007 | H01 #68 (78) | Top 5 thứ vừa khít hoàn hảo | F3 Countdown, 45s | 121 | ~161 từ/phút | H01, deep-analysis-25 |
| v008 | C02 #47 (79) | Con gái của bố | F7 stickman cảm xúc, 50s, có giọng kể | 130 | ~156 từ/phút | C02, deep-analysis-25 |

**Thứ tự sản xuất đề xuất:** v006 → v007 → v008. Lý do: v006 và v007
là format rẻ nhất (Visual Essay + Countdown, 1,5–3 giờ/video, dùng ảnh
stock/AI + giọng AI); v008 là stickman cảm xúc, cần rig 2–3 nhân vật +
bối cảnh nhà, đắt hơn (2–6 giờ, như v004). Nếu muốn thử stickman sớm
thì đổi v008 lên trước v007 — cả ba kịch bản đều đã sẵn sàng, thứ tự
không ảnh hưởng chất lượng.

## Điểm chung của cả 3 kịch bản
- **Kịch bản gốc tiếng Việt hoàn toàn**, không dịch lời thoại của video
  gốc; hook kép (chữ + giọng cùng một câu) trong 3s đầu; giọng vào từ
  0,1s; chuẩn -16 LUFS; phụ đề từng đoạn ngắn.
- **MMS-TTS-friendly:** không có số, năm, tên nước ngoài trong lời
  thoại (chỉ hiện trên hình); mỗi kịch bản có danh sách từ cần probe
  trên PC trước khi chốt giọng (xem từng file).
- **Nhạc + SFX từ thư viện Core_SFX** (toàn CC0): v006 dùng
  bgm_calm; v007 dùng bgm_comedy; v008 dùng bgm_calm — mỗi kịch bản
  ghi rõ tên file + vị trí đặt SFX theo giây.
- **Không dùng lại tài sản của video gốc:** v007 bỏ facecam hoàn toàn;
  v008 truyện hoàn toàn mới (nhân vật, bối cảnh, câu chuyện, câu chốt
  đều khác #47; chỉ giữ cơ chế).

## Sự thật đã kiểm chứng (mỗi kịch bản có nguồn đầy đủ trong file)
- **v006:** điểm ba trạng thái của nước là 0,01°C ở 611,657 Pa
  (Wikipedia "Triple point"; FactsMate/NIST — đo 1976, ±0,010 Pa),
  bằng khoảng 1/166 áp suất khí quyển ở mực nước biển; dưới áp suất
  này nước lỏng không tồn tại được. Các con số chỉ hiện trên hình,
  không đưa vào lời thoại.
- **v007:** không có khẳng định sự thật nào — danh sách là xếp hạng
  biên tập, các mục là vật quen thuộc; "khít từng milimét" chỉ là cách
  nói nhấn mạnh, không phải số đo thật.
- **v008:** không có khẳng định sự thật nào — truyện hư cấu hoàn toàn.

## Sự thật KHÔNG kiểm chứng được (và cách xử lý)
- **v006 — payoff thí nghiệm buồng kín của video gốc #80 nằm sau 30s
  đầu** nên chưa được xác nhận đầy đủ trong phân tích sâu — bản làm lại
  hạ cánh payoff rõ ràng trong 45s, không kéo dài như video gốc.
- **v007/v008:** không có sự thật nào chưa kiểm chứng.

## Từ cần probe trên PC trước khi sản xuất (tổng hợp từ 3 file)
- v006: "áp suất", "đóng băng", "buồng kín", "trạng thái".
- v007: "khít", "rãnh", "bản lề", "milimét", "cạch".
- v008: "Na", "phăng phắc" (dùng lại kết quả v005 nếu có), "dỗi",
  "rã rời".
- Quy tắc probe theo bài học v002/v003: probe từng câu riêng bằng
  MMS-TTS trên PC + kiểm bằng faster-whisper large-v3; nếu hỏng thì đổi
  từ theo gợi ý trong từng file (đã ghi sẵn phương án thay thế).

## Quyết định biên tập đáng chú ý (ghi lại để không bị "sửa" mất)
1. **v006:** cắt về 45s, cắt cứng mỗi ~10s — không kéo dài như video
   gốc 80,3s (không cắt cứng, crossfade chậm là lý do R bị hạ 4 → 3).
   Đừng "bổ sung thêm ví dụ cho đầy đặn".
2. **v007:** #1 là chốt cửa, không phải bánh xe tải — bánh xe chỉ là
   hook, chốt cửa mới là payoff (đúng video gốc).
3. **v008:** bố không mắng, bố chỉ ngồi xuống — đừng thêm cho bố một
   câu dạy dỗ nào. Câu duy nhất bố nói là "con gái của bố đây rồi".
   Ưu tiên stickman Manim thay vì ảnh AI (nhân vật nhất quán — bài học
   C02: nhân vật AI đổi mặt giữa các cảnh là hỏng).

## File trong thư mục này
- `script_v006-triple-point-45s.md` — kịch bản v006 (122 từ) + nguồn +
  từ cần probe.
- `script_v007-perfect-fit-45s.md` — kịch bản v007 (121 từ) + nguồn +
  quyết định #1 là chốt cửa.
- `script_v008-daddys-girl-50s.md` — kịch bản v008 (130 từ) + cảnh báo
  bản quyền + quyết định bố không mắng.
- `scripts_batch.md` — file này.

## Việc còn lại trước khi sản xuất (cho bước sau, không phải lô này)
- Probe các từ rủi ro trên PC (danh sách ở trên) và chốt từ thay thế
  nếu cần.
- Chuẩn bị tài sản theo ghi chú từng file (ảnh bình thí nghiệm đúng
  vật lý cho v006; 5 clip vừa khít cho v007; rig bố + Na + mẹ cho v008).
- Sản xuất theo thứ tự đề xuất (v006 → v007 → v008) với pipeline
  v001/v002 (MMS-TTS trên PC, speaking_rate 0.92 → faster-whisper kiểm
  → assemble + loudnorm -16 LUFS → QC frame), **render trên PC** theo
  lệnh của chủ 21:53 15/11; nhớ bài học v003: bỏ `-loop 1` + giới hạn
  cứng `-frames:v`.
