# Kịch bản V001 — Visual Essay (F2) — 45–50 giây, tiếng Việt

## Chủ đề
**Vì sao cửa sổ máy bay lại tròn?** — Câu hỏi về thứ quen thuộc, trả lời bằng
lịch sử + vật lý (cơ chế F2: câu hỏi lạ → 2–3 beat dữ liệu → lật lại nhận
thức → câu chốt + poll/CTA). Kiểu #81 ("mỗi lần đăng nhập là mẹo thủy thủ
500 năm") và T05 (Visual Essay bác bỏ một huyền thoại bằng số liệu).

## Nguồn đã kiểm chứng (không bịa số)
1. **FAA, "Lessons Learned — de Havilland Comet 1"** (tóm tắt báo cáo điều tra
   1955): chênh lệch áp suất khoang Comet ≈ 8,25 psi (56,9 kPa); vết nứt
   G-ALYP bắt đầu từ ô cửa sổ ăng-ten trên nóc thân máy bay; G-ALYU nứt ở
   góc cửa thoát hiểm trong thử nghiệm bể nước.
   Đọc qua: https://www.freeastroscience.com/unveiling-science-behind-aircraft/
   (bài này đối chiếu từng con số với trang FAA và báo cáo điều tra 1955,
   có hiệu đính ngày 13/10/2026).
2. **Gustav Kirsch (1898)**: lỗ tròn trong tấm kim loại bị kéo làm ứng suất
   tại mép tăng gấp 3 lần. **Charles Inglis (1913)**: góc nhọn nhân ứng suất
   theo công thức 1 + 2√(a/ρ) — góc 1 mm cho hệ số tới 21, góc bằng 0 cho
   hệ số vô cùng.
3. **Số chuyến bay đã kiểm chứng**: G-ALYP vỡ ngày 10/01/1954 sau 1.290
   chuyến bay có tăng áp; G-ALYY vỡ ngày 08/04/1954 ngoài khơi Naples sau
   900 chuyến; thân G-ALYU nứt trong bể thử sau 3.060 chu kỳ áp suất.
4. **Hiệu đính quan trọng (đã ghi vào kịch bản)**: câu chuyện phổ biến "cửa
   sổ vuông làm máy bay rơi" là giản lược quá mức — vết nứt đầu tiên bắt đầu
   từ ô cửa ăng-ten trên nóc, không phải cửa sổ hành khách. Bài học thật là
   về **góc nhọn**, không phải về cửa sổ. Kịch bản nói đúng điều này.

## Kịch bản (126 từ — mục tiêu ~47s ở 150–165 từ/phút)

| Giây | Beat | Lời thoại |
|---|---|---|
| 0–3 | Hook kép | Bạn có biết cửa sổ máy bay tròn không phải để đẹp? |
| 3–13 | Beat 1 — lịch sử | Ngày xưa, máy bay phản lực đầu tiên ra đời, cửa sổ vuông vức. Hai năm sau, hai chiếc vỡ tan giữa trời. |
| 13–27 | Beat 2 — bằng chứng | Điều tra phát hiện vết nứt bắt đầu từ một góc nhọn. Mỗi chuyến bay, khoang phồng lên rồi xẹp xuống — góc nhọn nhân ứng suất lên nhiều lần, tới khi kim loại mỏi và nứt. |
| 27–40 | Beat 3 — lật lại | Một lỗ tròn nhân ứng suất lên ba lần, nhưng góc nhọn nhân lên gấp hàng chục lần. Bo tròn góc, ứng suất trải đều — và vết nứt hết chỗ bắt đầu. |
| 40–47 | Payoff + CTA | Nhìn ra cửa sổ — bạn đang nhìn một bài học bằng kim loại. Bạn có tin không? Bình luận nhé! |

**Đếm từ (kiểm bằng script):** Hook 12 · Beat 1: 23 · Beat 2: 37 · Beat 3: 33 ·
Payoff + CTA 21 = **126 từ**. Giọng cuối 47,1s ≈ 160 từ/phút — trong vùng an
toàn 150–165.

**Thay đổi so với bản nháp đầu (lý do đã kiểm chứng):** bỏ "Năm 1952, Comet"
và "hai mươi mốt lần" khỏi lời thoại — MMS-TTS đọc số năm, tên nước ngoài
"Comet" và số ghép "hai mươi mốt" thành tiếng không nghe được (kiểm bằng
probe riêng: "Năm 1952, Comet ra đời" → Whisper nghe "Năm hì, có ý trở đời";
"Hai mươi mốt lần" → "Khả người mất lần"). Thay bằng "Ngày xưa" và "gấp hàng
chục lần" (21 là hàng chục — đúng số liệu, không bịa). Năm 1952 và tên Comet
vẫn đúng sự thật và được ghi ở đây + hiện dưới dạng chữ trên hình Beat 1
("1952 · Comet"), không cần giọng đọc.

**Hook kép (F1):** câu đầu tiên "Bạn có biết cửa sổ máy bay tròn không phải
để đẹp?" vừa là chữ lớn trên màn hình 0–3s, vừa là câu nói đầu tiên.

**Ghi chú sản xuất:** không nhạc nền (chưa có thư viện nhạc có bản quyền);
giọng vào từ 0,1s; chuẩn hóa -16 LUFS, true peak ≤ -1 dBTP; phụ đề từng
đoạn ngắn, không hiện cả câu một lúc.

## Giọng đọc (đã chốt — file `voice.wav`)

**Giọng cuối: MMS-TTS** (`facebook/mms-tts-vie`, Meta, chạy local trên VPS bằng
torch CPU + transformers, miễn phí). Tổng hợp theo từng câu, nối bằng khoảng
nghỉ 0,9s giữa các beat (không dùng atempo — atempo không cải thiện độ rõ).
Cắt 0,36s im lặng đầu, chuẩn hóa loudnorm 2-pass về **-16,1 LUFS**.

- Thời lượng: **47,10s** · giọng bắt đầu ở ~0,05s (không dead air) ·
  **160 từ/phút** (vùng an toàn 150–165) · true peak **-1,00 dBTP** ✓
- Kiểm Whisper Base (tiếng Việt): khớp **70%** từ của kịch bản (86/123).
  Các từ khóa đều nghe được: "góc nhọn", "kim loại, mỏi", "3 lần",
  "hàng chục lần", "2 năm sau, 2 chiếc", "bình luận nhé". Lỗi còn lại chủ yếu
  là Whisper nhầm âm gần giống (Bạn→bản, cửa sổ→cửa số, vết nứt→nước,
  kim loại→kinh loại, ứng suất→tướng xuất) — **không phải** giọng đọc sai;
  phụ đề đốt vào video dùng đúng chữ kịch bản (xem mục Phụ đề).

**Các giọng đã thử và loại (ghi lại để không thử lại):**
- **Edge TTS** (ưu tiên đầu): websocket tới speech.platform.bing.com bị
  proxy chặn (SSL WRONG_VERSION_NUMBER, rồi timeout, rồi lỗi handshake 101).
  Chặn ở hạ tầng VPS, không sửa được từ đây.
- **gTTS**: 429 Too Many Requests 2 lần — IP proxy dùng chung bị Google giới
  hạn. Chết tạm thời.
- **Piper TTS** (`vi_VN-vais1000-medium`): tổng hợp được, 50,98s ở
  length-scale 2.4 (154 từ/phút), nhưng **giọng phá dấu tiếng Việt** — kiểm
  Whisper chỉ 65% và sai đúng từ khóa: "góc nhọn"→"khóc ngọt",
  "vuông vức"→"vùng với", "khoang phồng"→"quang phòng", "Comet" không nghe
  được. Lỗi ở phonemizer espeak-ng, không phải do tốc độ (thử 3 tốc độ đều
  sai). File `voice_piper.wav` giữ lại làm mẫu đối chứng, KHÔNG dùng.
- **MMS-TTS probe riêng** (quyết định): "Năm 1952, Comet ra đời" →
  "Năm hì, có ý trở đời"; "Hai mươi mốt lần" → "Khả người mất lần" —
  giọng này **không đọc được số năm, tên nước ngoài và số ghép có "mốt"**,
  nên kịch bản đã bỏ 2 chỗ đó khỏi lời thoại (xem trên).

## Phụ đề

`captions.srt` (32 đoạn, 3–5 từ/đoạn) dùng **đúng chữ kịch bản**, thời gian
căn theo 6 đoạn Whisper phát hiện trên chính file voice.wav
(`captions_whisper.srt` giữ lại làm bản ghi — chữ Whisper sai ~30% nên
KHÔNG đốt bản đó vào video). **Bản đốt vào video là `captions.ass`** (chuyển
từ SRT, PlayRes 1080x1920, style Noto Sans Bold 56, trắng viền đen,
MarginV 300 — đặt ở 1/3 dưới giữa), qua filter `ass`. Lý do: filter
`subtitles` với file SRT dùng PlayRes mặc định 384x288 nên FontSize 56 bị
phóng 6,67 lần và MarginV 300 đẩy chữ ra khỏi khung (đã thử
`original_size`, không sửa được) — xem chi tiết trong qc.md.
