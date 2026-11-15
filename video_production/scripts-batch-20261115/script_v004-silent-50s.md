# Kịch bản V004 — Truyện stickman cảm xúc (F7) — 50 giây, tiếng Việt

## Chủ đề
**Ông Tư sửa giày — chỉ cần một người dừng lại.** — Truyện cảm xúc về
một người bị cả phố lướt qua mỗi ngày, và một bé gái đã dừng lại nhìn
ông (cơ chế F7: stickman + thẻ chữ + nhạc gánh cảm xúc; giọng kể + thẻ
chữ song song). Làm lại từ **#50 (85 điểm, Silent Stories of the Heart,
90,14s)** — video gốc là truyện câm (không lời, chỉ nhạc + thẻ chữ):
cô đơn dưới mưa → bị lãng quên → níu giữ quá khứ → cô gái quay lại với
bảng "I SEE YOU" → được nhìn thấy → "EVERYONE DESERVES TO BE SEEN.",
mỗi beat cách nhau ~22s (quá chậm — phân tích sâu điều chỉnh R 4→3 và
yêu cầu bản làm lại mỗi beat ~12s).

## QUYẾT ĐỊNH QUAN TRỌNG — VÌ SAO CÓ GIỌNG KỂ (không làm bản câm)
Bản này **có giọng kể** (125–138 từ), không làm bản câm như video gốc,
vì 3 lý do:
1. Pipeline giọng kể + kiểm Whisper đã được chứng minh qua v001/v002/
   Ep001 (MMS-TTS trên PC + faster-whisper large-v3 kiểm 91,9–94,9%);
   còn bản câm thì cảm xúc phụ thuộc hoàn toàn vào việc chọn nhạc —
   rủi ro cao hơn.
2. Giọng kể + thẻ chữ là hook kép (F1): người tắt tiếng vẫn theo được
   truyện qua thẻ chữ, người nghe vẫn theo được qua giọng kể.
3. Giọng kể giúp beat nhanh hơn (~12s/beat thay vì 22s như bản gốc)
   mà vẫn giữ được cảm xúc — bản câm mà cắt nhanh thì thẻ chữ đọc
   không kịp.

## CẢNH BÁO BẢN QUYỀN — TRUYỆN NÀY HOÀN TOÀN MỚI
Video gốc #50 có dòng "© 2026 Christopher Thomas. All Rights Reserved."
trên MỌI frame. Bản này **không dùng lại bất cứ thứ gì của bản gốc**:
- Nhân vật khác: ông Tư (thợ sửa giày già) + bé gái — không phải
  người đàn ông cô đơn + cô gái áo vàng của bản gốc.
- Bối cảnh khác: góc phố, sạp sửa giày lúc chập tối — không phải ghế
  công viên ban đêm dưới mưa.
- Câu chuyện khác: đôi giày nhỏ không ai lấy + bức vẽ của bé gái —
  không phải khung ảnh cũ + bảng "I SEE YOU".
- Câu chốt khác: "Chỉ cần một người dừng lại." — không phải
  "EVERYONE DESERVES TO BE SEEN."
- Chỉ giữ lại **cơ chế** (điều framework cho phép): người bị lãng quên
  mỗi ngày → níu giữ một vật → một người dừng lại → được nhìn thấy →
  câu chốt đáng chia sẻ; beat nhanh ~12s; nhạc là xương sống cảm xúc.

## Nguồn đã kiểm chứng
- **Không có khẳng định sự thật nào cần kiểm chứng — truyện hư cấu
  hoàn toàn.** Cơ chế + nhịp + cảnh báo bản quyền lấy từ phân tích
  sâu C01 #50 (`deep-analysis-5x85-20261115.md`) và công thức F7
  (`production-framework-20261115.md`): 1 nền tái dùng + 2 rig
  stickman; beat ~12s; nhạc liên tục, swell theo cảm xúc; 0,5s lặng
  trước câu chốt.

## Kịch bản (130 từ — mục tiêu 50s ở 150–165 từ/phút)

| Giây | Beat | Lời kể |
|---|---|---|
| 0–3 | Hook | Mỗi ngày, hàng trăm người đi qua góc phố này. |
| 3–15 | Beat 1 — setup | Ông Tư sửa giày ở góc phố này đã ba mươi năm. Người ta lướt qua mỗi ngày — không ai dừng lại, không ai hỏi tên ông, không ai nhớ mặt ông. |
| 15–28 | Beat 2 — níu giữ | Tối nào ông cũng đánh bóng một đôi giày nhỏ — của một người khách bỏ quên từ lâu, không bao giờ quay lại lấy. Ông để đôi giày trên sạp, như đang đợi ai đó. |
| 28–42 | Beat 3 — bước ngoặt | Một chiều, một bé gái dừng lại, chỉ vào đôi giày nhỏ: "Của ai vậy ông?" Hôm sau, bé quay lại — tay cầm một bức vẽ: ông Tư ngồi sửa giày dưới ánh đèn vàng. |
| 42–50 | Payoff | Ông cười — lần đầu sau bao năm, có người nhìn thấy ông. Chỉ cần một người dừng lại. |

**Đếm từ (kiểm bằng script):** Hook 10 · Beat 1: 32 · Beat 2: 35 ·
Beat 3: 35 · Payoff 18 = **130 từ**. Mục tiêu 50s ≈ 156 từ/phút —
trong vùng an toàn 150–165 (kiểm thực tế sau khi tổng hợp; nối bằng
khoảng nghỉ 0,9–1,2s giữa các beat như v001/v002).

**Thẻ chữ trên màn hình (F7: thẻ chữ LÀ một phần kịch bản):**
- Thẻ 1 (0–3s): "KHÔNG AI NHÌN ÔNG MỘT LẦN."
- Thẻ 2 (3–15s): "BA MƯƠI NĂM Ở GÓC PHỐ NÀY."
- Thẻ 3 (15–28s): "ĐÔI GIÀY KHÔNG AI LẤY."
- Thẻ 4 (28–42s): "CỦA AI VẬY ÔNG?" → sau đó "BỨC VẼ CỦA BÉ."
- Thẻ 5 (42–50s): "CHỈ CẦN MỘT NGƯỜI DỪNG LẠI."

**Ghi chú hình ảnh:** rig stickman Manim (đã có) × 2 — ông Tư (thêm
mũ + tạp dề) và bé gái (nhỏ hơn, tóc buộc) + 1 nền góc phố tái dùng
(sạp sửa giày + đèn đường); ánh sáng chuyển lạnh → ấm ở payoff (đèn
vàng bật sáng); đạo cụ: đôi giày nhỏ trên sạp, bức vẽ (giấy vẽ hình
stickman). Mưa KHÔNG dùng (tránh trùng bối cảnh mưa của bản gốc) —
cảnh là chập tối khô ráo, đèn vàng là điểm ấm duy nhất.

**Nhạc + SFX (từ thư viện Core_SFX, toàn CC0):** nhạc nền
`music/bgm_calm.ogg` — nhạc LÀ xương sống cảm xúc của video này
(F7): bắt đầu nhỏ, swell dần, lên cao nhất ở beat 3 (bé gái quay
lại với bức vẽ), lắng xuống ở payoff. Âm lượng thấp hơn giọng -18
đến -24 dB. SFX tối thiểu: transition_swoosh nhẹ giữa các beat; ding
nhẹ ở 28s (bé gái xuất hiện — bước ngoặt); **0,5s lặng hoàn toàn
trước câu chốt ở 42s** ("Ông cười…") — khoảng lặng cố tình theo F7,
không phải lỗi. Không dùng boom/victory (sai cảm xúc).

## Kế hoạch giọng đọc (CHƯA TỔNG HỢP — chờ bước sản xuất)
- **MMS-TTS** (`facebook/mms-tts-vie`) trên PC (CUDA), tổng hợp từng
  câu, nối bằng khoảng nghỉ 0,9–1,2s giữa các beat; riêng trước câu
  chốt ở 42s để 0,5s lặng (xem mục SFX).
- Giọng kể chậm, ấm (150–165 từ/phút, không đọc nhanh như FB-05 gốc
  246 từ/phút). Kiểm bằng faster-whisper large-v3 trên PC, từng câu
  riêng (probe) rồi mới kiểm cả file.
- **Từ cần probe trước khi chốt (MMS-TTS dễ đọc hỏng):**
  - "Tư" (tên riêng) — probe câu "Ông Tư sửa giày…"; nếu hỏng, đổi
    tên thành "ông Ba" (probe lại).
  - "lướt" (trong "lướt qua") — probe; nếu hỏng, đổi thành "đi qua"
    (nhưng mất nghĩa "không thèm nhìn" — chỉ đổi khi bắt buộc).
  - "sạp" (từ ít gặp) — probe; nếu hỏng, đổi thành "quầy nhỏ" hoặc
    "góc sửa giày".
  - Không có số, không có từ nước ngoài trong lời thoại.

## Ghi chú sản xuất
- Giọng vào từ 0,1s; chuẩn hóa -16 LUFS, true peak ≤ -1 dBTP; phụ đề
  từng đoạn ngắn (3–5 từ/đoạn), không hiện cả câu một lúc; phụ đề dùng
  đúng chữ kịch bản.
- Thẻ chữ dùng font Be Vietnam Pro Bold (như Ep001), chữ lớn, đọc
  được trong 3s — thẻ dài nhất 7 từ ("CHỈ CẦN MỘT NGƯỜI DỪNG LẠI.").
- Tiêu đề gợi ý (38–45 ký tự): "Ông lão sửa giày và bé gái dừng lại
  nhìn ông" (38 ký tự).
