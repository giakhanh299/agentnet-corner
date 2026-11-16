# Kịch bản V014 — Đừng làm thêm kiểu cũ (T07) — 50 giây, tiếng Việt

## Chủ đề
**Đừng làm thêm giờ nữa — máy tính nhà bạn làm video nhanh hơn bạn
tưởng** — Làm lại từ **T07 #99 "Don't Get a Part Time Job!!" (74
điểm, TikTok, 48,2s, nói tiếng Anh ~190 từ/phút)** — video gốc: tuyên
bố ngược đời ("Đừng làm thêm!") + con số tiền (600/ngày → 18.000/
tháng) + bằng chứng (video học cho bé làm bằng AI có nhiều lượt xem)
→ hướng dẫn 4 bước (tìm video viral → chép transcript → dán vào
swagga.ai). Bản Việt: giữ cấu trúc "tuyên bố ngược đời → bằng chứng →
hướng dẫn", nhưng thay con số tiền **không kiểm chứng được** bằng
**số liệu thật của chính mình** (quy trình sản xuất video của kênh),
và thay công cụ swagga.ai bằng quy trình mình đang dùng.

## Nguồn đã kiểm chứng — số liệu thật của chính mình (không hứa thu nhập)
1. **Giọng đọc MMS-TTS trên PC: 55 từ / 19,6s audio trong 0,9 giây**
   (PC local AI stack, 2026-11-15 — RTX 5060 Ti, transformers 5.23.0,
   model facebook/mms-tts-vie trên CUDA).
2. **Kiểm tra giọng bằng faster-whisper large-v3: 48,8s audio trong
   4,7 giây** (PC, RTF 0,10x — nhanh gấp ~10 lần VPS).
3. **Render trên PC: v003 encode 12 giây cho 1.504 khung hình**; tập
   v008 render trọn vẹn trên PC ~28 giây (2026-11-16).
4. **Cơ chế + cảnh báo từ phân tích sâu T07**
   (`deep-analysis-25-20261115.md`): hook kép xác nhận (giọng nói
   đúng chữ trên màn hình) + con số cụ thể; âm thanh gốc cực kỳ nhỏ
   (-36,72 LUFS) là lỗi kỹ thuật — bản làm lại bắt buộc chuẩn hóa về
   ~-16 LUFS; **rủi ro lớn nhất: nội dung "kiếm tiền bằng AI" dễ bị
   coi là lừa đảo nếu không có bằng chứng thật — bản làm lại phải dùng
   số liệu thật của chính mình, không hứa hẹn thu nhập**; video gốc
   quay màn hình YouTube của người khác + giao diện swagga.ai — bản
   làm lại chỉ dùng màn hình của chính mình.

## Sự thật KHÔNG đưa vào lời thoại (chỉ hiện trên hình)
- Các con số **0,9 giây / 4,7 giây / 12 giây** chỉ hiện dưới dạng chữ
  trên hình (thẻ "ĐỌC GIỌNG: 0,9 GIÂY", "KIỂM GIỌNG: 4,7 GIÂY",
  "DỰNG: 12 GIÂY"), **không đưa số vào lời thoại** (MMS-TTS đọc số
  thập phân kém — bài học v001/v003). Lời thoại nói bằng chữ: "chưa
  đầy một giây", "chưa đầy năm giây", "mười hai giây".
- **Không có con số tiền nào** trong video này — không hứa thu nhập,
  không nhắc 600/18.000 của video gốc.

## Kịch bản (129 từ — mục tiêu 50s ở 150–165 từ/phút)

| Giây | Beat | Lời thoại |
|---|---|---|
| 0–5 | Hook kép | Đừng làm thêm giờ nữa. Máy tính nhà bạn làm video nhanh hơn bạn tưởng. |
| 5–15 | Beat 1 — bằng chứng | Tôi làm video bốn mươi lăm giây thế này: giọng đọc xong trong chưa đầy một giây, kiểm tra giọng chỉ mất chưa đầy năm giây. |
| 15–32 | Beat 2 — 4 bước | Bốn bước thôi. Một, viết kịch bản ngắn, khoảng một trăm hai mươi từ. Hai, cho máy đọc giọng. Ba, vẽ hình bằng trí tuệ nhân tạo. Bốn, dựng trên máy nhà, mười hai giây là xong. |
| 32–42 | Beat 3 — thành thật | Không hứa bạn giàu nhanh. Nhưng một buổi tối, bạn làm được một video. Một tuần, bạn có bảy video, mà không cần quay phim gì cả. |
| 42–50 | Payoff + CTA | Làm thêm kiểu cũ đổi giờ lấy tiền. Làm kiểu này, máy làm hộ giờ của bạn. Bạn chọn cách nào? Bình luận nhé! |

**Đếm từ (kiểm bằng script):** Hook 15 · Beat 1: 26 · Beat 2: 37 ·
Beat 3: 27 · Payoff + CTA: 24 = **129 từ**. Mục tiêu 50s ≈ 155
từ/phút — trong vùng an toàn 150–165 (kiểm thực tế sau khi tổng hợp;
giọng vào từ 0,1s, không có khoảng lặng trong 3s đầu).

**Khung hình (quay màn hình thật của chính mình + chữ lớn — bỏ
facecam như video gốc, nhưng không quay lại nội dung của người khác):**
- 0–5s: màn hình máy tính đang dựng video + chữ lớn "ĐỪNG LÀM THÊM
  GIỜ NỮA".
- 5–15s: màn hình tổng hợp giọng chạy + thẻ "ĐỌC GIỌNG: 0,9 GIÂY" →
  màn hình kiểm tra giọng + thẻ "KIỂM GIỌNG: 4,7 GIÂY".
- 15–32s: 4 màn hình bước nối nhau (kịch bản → giọng → hình AI →
  dựng), mỗi bước một số lớn 1–2–3–4.
- 32–42s: lịch 7 video/tuần + chữ "7 VIDEO / TUẦN — KHÔNG CẦN QUAY
  PHIM".
- 42–50s: thẻ payoff "MÁY LÀM HỘ GIỜ CỦA BẠN" + CTA "BẠN CHỌN CÁCH
  NÀO?"

**Ghi chú hình ảnh:** chỉ quay màn hình của chính mình (quy trình
thật: kịch bản → MMS-TTS → hình AI/Manim → dựng); **không quay màn
hình YouTube của người khác, không quay giao diện công cụ của người
khác** (cảnh báo bản quyền T07). Nếu chưa quay được màn hình thật thì
dùng ảnh chụp màn hình thật + zoom (đã chứng minh được ở v002/v006).

## Nhạc + SFX (thư viện Core_SFX, toàn CC0)
- Nhạc nền: `bgm_upbeat.ogg` (hướng dẫn nhanh, năng lượng — như v013).
- SFX: `ding.ogg` ở mỗi bước (15s, 20s, 25s, 30s); `pop.ogg` ở 42s
  (thẻ payoff); `whoosh.ogg` ở 5s (chuyển sang bằng chứng).
- BGM -18 đến -24 dB dưới giọng (bài học v003).

## Từ cần probe trên PC trước khi sản xuất
- "trí tuệ nhân tạo" (cụm dài — nếu MMS vấp thì đổi thành "máy vẽ
  hình").
- "video" (đã dùng trong các kịch bản trước, vẫn probe lại cho chắc).
- "bốn mươi lăm giây" (nếu hỏng thì đổi thành "video ngắn").
- "mười hai giây" (nếu hỏng thì đổi thành "chưa đầy nửa phút" — nhưng
  phải đổi đồng nhất cả lời thoại lẫn chữ trên hình).
- "kịch bản" (nếu hỏng thì đổi thành "bài viết").

## QUYẾT ĐỊNH — KHÔNG HỨA THU NHẬP, CHỈ KHOE TỐC ĐỘ THẬT
Video gốc: 600/ngày → 18.000/tháng (không kiểm chứng được, dễ bị coi
là lừa đảo). Bản làm lại **bỏ toàn bộ con số tiền**, thay bằng tốc độ
thật của chính mình (0,9s / 4,7s / 12s) và câu thành thật "Không hứa
bạn giàu nhanh" ở beat 3 — giữ đúng câu này, đừng xóa khi dựng. Đây là
video hậu trường về quy trình của kênh, không phải video dạy làm giàu.
