# Tóm tắt lô kịch bản — 2026-11-16 (v009 + v010 + v011)

**Bối cảnh:** làm trước theo chỉ đạo của chủ (15/11 ~15:50: làm việc chủ
động, tự tìm việc khi rảnh, làm trước tiến độ; và 15/11 ~17:34: chủ đề lấy
từ ngân hàng 30 video đã phân tích sâu). Lô trước (v006 + v007 + v008)
đã sản xuất xong cả 3 video sáng nay (09:24–09:32); chưa có kế hoạch
v009+ nào trong workspace (kiểm tra 16/11 10:30: không có file
v009/v010/v011 nào). Ba kịch bản này viết theo lô từ 3 chủ đề chưa dùng
trong ngân hàng 30 — mỗi kịch bản một format ưu tiên khác nhau
(Countdown · Visual Essay · Visual Essay). **Chỉ kịch bản — chưa sản
xuất video, chưa tổng hợp giọng, chưa đăng/upload gì.** Sản xuất theo
lệnh của chủ như lần trước. File sẽ lên git qua auto-push 30 phút
(`auto_push.sh` đã sync `video_production/`).

## Bảng tổng kết

| # | Video | Chủ đề | Công thức | Từ | Tốc độ | Nguồn gốc |
|---|---|---|---|---|---|---|
| v009 | T04 #84 (80) | Top 5 sự thật về động vật | F3 Countdown, 45s | 120 | ~160 từ/phút | T04, deep-analysis-25 |
| v010 | T05 #82 (78) | Bài báo 1960 nói thế giới tận thế 13/11/2026 | F2 Visual Essay, 50s | 137 | ~164 từ/phút | T05, deep-analysis-25 |
| v011 | T06 #83 (76) | Canada có 60% số hồ trên thế giới | F2 Visual Essay, 45s | 113 | ~151 từ/phút | T06, deep-analysis-25 |

**Thứ tự sản xuất đề xuất:** v009 → v010 → v011. Lý do: v009 là format
rẻ nhất trong 30 video (F=5, C=5 — 1 ảnh nhân vật + chữ + giọng, 1–2
giờ); v010 và v011 đều là Visual Essay (ảnh/bản đồ + giọng, 1,5–3
giờ/video). Cả ba đều không cần quay, không cần rig stickman.

## Điểm chung của cả 3 kịch bản
- **Kịch bản gốc tiếng Việt hoàn toàn**, không dịch lời thoại của video
  gốc; hook kép (chữ + giọng cùng một câu) trong 3s đầu; giọng vào từ
  0,1s; chuẩn -16 LUFS; phụ đề từng đoạn ngắn.
- **MMS-TTS-friendly:** không có số, năm, tên nước ngoài trong lời
  thoại (chỉ hiện trên hình); mỗi kịch bản có danh sách từ cần probe
  trên PC trước khi chốt giọng (xem từng file).
- **Nhạc + SFX từ thư viện Core_SFX** (toàn CC0): v009 dùng
  bgm_comedy; v010 dùng bgm_suspense; v011 dùng bgm_calm — mỗi kịch bản
  ghi rõ tên file + vị trí đặt SFX theo giây.
- **Không dùng lại tài sản của video gốc:** v009 bỏ mèo AI gốc (vẽ lại
  nhân vật của mình hoặc dùng số lớn + ảnh từng con vật); v010/v011
  vẽ lại đồ thị/bản đồ của mình.

## Sự thật đã kiểm chứng (mỗi kịch bản có nguồn đầy đủ trong file)
- **v009:** cá bay lướt tới 200m (National Wildlife Federation /
  Britannica); cá heo có tên riêng — signature whistle (Janik, Sayigh
  & Wells, PNAS 2006); bạch tuộc 3 tim, kiến trồng nấm, châu chấu cọ
  chân — khớp nội dung video gốc #84.
- **v010:** bài báo Science 1960 thật (von Foerster, Mora & Amiot,
  "Doomsday: Friday, 13 November, A.D. 2026", Science 132:1291–1295);
  ngày 13/11 là sinh nhật của von Foerster, ông tự nói không tin;
  tốc độ tăng dân số đạt đỉnh ~2,1–2,3% năm 1963 rồi giảm; thực tế
  11/2026 khoảng 8,2 tỉ người, công thức 1960 dự báo 96–205 tỉ
  (Science.org + U.S. Census Bureau).
- **v011:** Canada giữ ~60–62% số hồ thế giới; 31.752 hồ lớn hơn
  3 km² (Atlas of Canada); Ngũ Đại Hồ chứa 18% nước hồ ngọt thế giới;
  hồ Thượng là hồ nước ngọt lớn nhất thế giới theo diện tích; băng hà
  10.000 năm trước tạo hồ (Wikipedia "List of lakes of Canada" +
  Science.org qua video gốc).

## Sự thật KHÔNG kiểm chứng được (và cách xử lý)
- **v009:** không có — cả 5 sự thật đều có nguồn.
- **v010:** không có — các con số đều từ Science.org / Census Bureau.
- **v011:** không có — các con số đều từ Atlas of Canada / Wikipedia.
- **Lưu ý thời điểm v010:** ngày 13/11/2026 đã qua 3 ngày — hook dùng
  thì quá khứ ("ngày mười ba vừa rồi"), không dùng "hôm nay" như video
  gốc.

## Từ cần probe trên PC trước khi sản xuất (tổng hợp từ 3 file)
- v009: "huýt", "bạch tuộc", "lướt", "cọ", "Top" (bài học v005).
- v010: "tận thế", "vô cùng", "đạt đỉnh", "trưởng nhóm".
- v011: "Canada", "băng hà", "hố trũng", "Thượng", "Trái Đất".
- Quy tắc probe theo bài học v002/v003: probe từng câu riêng bằng
  MMS-TTS trên PC + kiểm bằng faster-whisper large-v3; nếu hỏng thì đổi
  từ theo gợi ý trong từng file (đã ghi sẵn phương án thay thế).

## Quyết định biên tập đáng chú ý (ghi lại để không bị "sửa" mất)
1. **v009:** giữ đúng 5 sự thật, số 1 là bạch tuộc 3 tim — đừng thêm
   sự thật thứ 6 "cho đầy đặn".
2. **v010:** đây là video bóc tin đồn bằng số liệu, không phải video
   gieo tin đồn — phải giữ câu "chính họ cũng không tin" ở beat 2.
3. **v011:** giữ đúng 3 beat của video gốc (nước lớn → hồ → băng hà),
   đừng thêm beat thứ 4 về rừng/dầu mỏ.

## File trong thư mục này
- `script_v009-animal-facts-45s.md` — kịch bản v009 (120 từ) + nguồn +
  từ cần probe.
- `script_v010-doomsday-50s.md` — kịch bản v010 (137 từ) + nguồn +
  quyết định bóc tin đồn.
- `script_v011-canada-lakes-45s.md` — kịch bản v011 (113 từ) + nguồn +
  từ cần probe.
- `scripts_batch.md` — file này.

## Việc còn lại trước khi sản xuất (cho bước sau, không phải lô này)
- Probe các từ rủi ro trên PC (danh sách ở trên) và chốt từ thay thế
  nếu cần.
- Chuẩn bị tài sản theo ghi chú từng file (5 ảnh động vật + mèo cho
  v009; đồ thị dân số cho v010; bản đồ Canada + ảnh vệ tinh hồ cho v011).
- Sản xuất theo thứ tự đề xuất (v009 → v010 → v011) với pipeline
  v001/v002 (MMS-TTS trên PC, speaking_rate 0.92 → faster-whisper kiểm
  → assemble + loudnorm -16 LUFS → QC frame), **render trên PC** theo
  lệnh của chủ 21:53 15/11; nhớ bài học v003: bỏ `-loop 1` + giới hạn
  cứng `-frames:v`.
