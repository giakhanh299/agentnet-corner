# Production Framework — Tuần 1 (2026-11-15)

**Mốc tổng hợp tuần 1: 30/30 video đã phân tích sâu → 8 công thức sản xuất.**
Tài liệu này là bản tổng hợp duy nhất để viết kịch bản tuần 2 (từ 23/11/2026).
Mọi công thức đều rút từ bằng chứng đã đo, không bịa số liệu.

**Nguồn:** `deep-analysis-5x85-20261115.md` (5 video 85+) ·
`deep-analysis-25-20261115.md` (25 video còn lại) ·
`selection-30-20261115.md` + `.csv` (bản FB-05) ·
`deep-analysis-hook-sheet-20261115.md` (hook nói + ngôn ngữ) ·
`chatgpt-followup-20261115.md` (cửa tuần 2) · `gemini-followup-20261115.md`
(ngày 7: 30 hook, khung 5 giây, Core SFX, 3 template trống).

## Giới hạn trung thực (đọc trước khi dùng)

- **Transcript chỉ có 30 giây đầu** (audio.wav là clip 30s). Mọi nhận xét về
  lời nói/pacing/audio sau 30s là **chưa đánh giá được**.
- **Không nghe được audio.** Nhạc/SFX cụ thể của từng video gốc là chưa đánh
  giá được — chỉ có độ lớn (LUFS), khoảng lặng (silencedetect) và transcript.
- **Chỉ xem frame tĩnh**, không xem video chạy: chuyển động thực (zoom/pan,
  hiệu ứng) chỉ suy ra từ cụm frame.
- **Whisper Base THẤT BẠI trên tiếng Hindi** (H05, H08, C03, D02 — transcript
  lặp/vô nghĩa). Hook nói của 4 video này là **chưa xác định, không phải
  "không có"** — không được trích dẫn lời nói của chúng như sự thật.
- **Không có dữ liệu view/retention/CTR thật** — điểm số là chất lượng cơ chế,
  không phải dự đoán lượt xem. Không bịa con số hiệu quả.

## Quy tắc cứng (áp dụng cho MỌI video làm lại)

1. **KHÔNG BAO GIỜ dùng máy quay.** Người dùng không có thiết bị quay —
   chỉ dùng ảnh AI/stock, stickman/animation, chữ, giọng AI, nhạc/SFX.
2. **Mọi bản làm lại cắt/kéo về 40–55 giây.** Chỉ 13/95 video đã phân tích
   nằm trong cửa sổ 38–65s; video ngắn thì thêm beat, video dài thì cắt.
3. **Hook phải có ở ít nhất một kênh trong 3s đầu** (chữ HOẶC giọng HOẶC
   hình); tốt nhất là cả hai kênh (chữ + giọng) nói cùng một câu.
4. **Chỉ dùng tài sản của mình.** 15/25 video gốc dùng lại clip/âm thanh/hình
   của người khác — bản làm lại không được dùng lại bất cứ thứ gì của họ.
   Riêng #50 có dòng "© 2026 Christopher Thomas. All Rights Reserved." trên
   mọi frame — phải vẽ/kể lại hoàn toàn mới, chỉ học cơ chế.
5. **Giọng vào từ 0,1s, không dead air đầu video.** 6/25 video gốc mở đầu
   bằng im lặng (0,5–1,14s) — lỗi phổ biến nhất, dễ sửa nhất.
6. **Chuẩn hóa âm lượng về ~-16 LUFS, true peak ≤ -1 dBTP.** Video gốc chênh
   nhau 25 dB (-12,09 tới -36,95 LUFS); 4 video bị clip (true peak > 0 dBTP).
7. **Tốc độ nói 150–165 từ/phút là vùng an toàn.** Nhanh hơn 200 từ/phút là
   quá nhanh (#77 214, FB-05 246, B04 260 — đều phải đọc chậm lại khi làm lại).

## Ngân sách từ (150–165 từ/phút)

| Độ dài | Số từ |
|---|---|
| 40s | 100–110 từ |
| 45s | 112–124 từ |
| 50s | 125–138 từ |
| 55s | 138–151 từ |

Lưu ý: Gemini đề xuất kịch bản Tò mò 48s khoảng 140–160 từ — con số đó tính
theo tốc độ ~175–200 từ/phút, **nhanh hơn vùng an toàn đã kiểm chứng
(150–165)**. Khung này dùng 120–132 từ cho 48s, trừ khi giọng đọc đã được
kiểm chứng là nghe rõ ở tốc độ cao hơn.

---

# Bảng tổng kết 30 video (điểm đã chấm lại sau phân tích sâu)

Tổng điểm mới **2082** (cũ 2090), trung bình **69,4** (cũ 69,67). 4 video đạt
85+: #77 (90), #81 (87), #50 (85), FB-05 (85). 2 video đổi điểm: H06 #23
59 → **54** (không có hook nói, dead air 0,6s, frame 0s mờ); B06 #24
49 → **54** (hook nói "It's jelly. That's a pool." mà chấm từ frame bỏ sót).

## 8 cơ chế (xếp theo thứ tự ưu tiên làm thử)

| # | Cơ chế | Video gốc | Độ khó làm lại | Công thức |
|---|---|---|---|---|
| 1 | Hook kép (chữ + giọng cùng câu) | #77, #81, #80, FB-05, T04, T05, T07 | Dễ | F1 |
| 2 | Visual Essay (câu hỏi → dữ liệu → lật lại) | #81, #80, T05, T06, #77 | Dễ–trung bình | F2 |
| 3 | Danh sách đếm ngược (tiết lộ một phần) | H02, H03, T04 | Dễ | F3 |
| 4 | Một hình ảnh phi lý | B01, B06, D01 | Trung bình–khó | F4 |
| 5 | X vs Y / Kỳ vọng vs Thực tế | B04, D04, H05 | Dễ–trung bình | F5 |
| 6 | Quá trình biến đổi | D02, H01 | Dễ | F6 |
| 7 | Truyện tranh AI / stickman cảm xúc | #50, FB-05, C03, C02 | Trung bình | F7 |
| 8 | Nhãn "POV:" | B05, H07, T07 | Dễ nhất (nhãn) / trung bình–khó (hành động) | F8 |

---

# 8 công thức sản xuất

## F1 — Hook kép: chữ + giọng hỏi CÙNG một câu trong 3s đầu

**Cơ chế (1 dòng):** Câu đầu tiên trên màn hình và câu đầu tiên trong lời
thoại là cùng một câu hỏi/lời hứa — người xem tắt tiếng vẫn dính (chữ), người
nghe vẫn dính (giọng).

**Bằng chứng:** 4/5 video 85+ dùng hook kép (#77, #81, #80, FB-05); thêm T04
("Did you know…?"), T05 ("the world ends today"), T07 ("Don't get a part time
job"), B04 (đối thoại = tiền đề trên màn hình), B06 ("It's jelly. That's a
pool."). Ngược lại: #50 không có giọng — hook chỉ có chữ + nhạc, và đó là hook
yếu nhất về chuyển động trong 5 video. H04 có câu hỏi hoài niệm chỉ ở dạng
chữ, giọng không bao giờ nói lại — điểm H=3 đã tính.

**Cấu trúc (0–3s, áp dụng cho MỌI video):**

| Giây | Hình | Chữ | Giọng | SFX |
|---|---|---|---|---|
| 0,0–0,1 | Ảnh mở (không fade-in từ đen) | Câu hỏi hiện ngay | Từ đầu tiên nói ngay | Whoosh + Pop |
| 0–1 | Chữ lớn, 3–5 từ, giữa màn hình | Câu hỏi đầy đủ | Hỏi câu đó | — |
| 1–3 | Hình minh họa câu hỏi (1 ảnh/clip) | Giữ câu hỏi trên màn hình | Nói hết câu hỏi (8–15 từ) | Ding nhẹ ở từ khóa |
| 3 | Cắt sang beat 1 | Chữ hook biến mất | Câu đầu beat 1 | Whoosh chuyển cảnh |

**Khung kịch bản:** câu hook 8–15 từ, phải đọc được to lên và viết lên màn
hình mà không đổi một chữ nào. Ví dụ mẫu (từ video gốc): "Nếu cáp thang máy
đứt ở tầng 85, nhảy lên 1 giây trước khi chạm đất thì có sống không?" (#77);
"Every time you log into an app, you're using a 500-year-old sailor trick."
(#81); "Cách làm giàu nhanh nhất chính là làm một con buôn trung gian thông
minh." (FB-05).

**Tài sản hình ảnh:** 1 thẻ tiêu đề chữ lớn + 1 ảnh minh họa câu hỏi.
**Giọng/nhạc/SFX:** giọng vào từ 0,1s (không dead air); ≥2 lớp SFX trong 3s
đầu (Whoosh + Pop/Ding); nhạc nền bắt đầu nhỏ, dưới giọng -18 đến -24 dB.
**Chi phí:** dễ — cộng thêm ~15 phút cho bất kỳ video nào (thẻ chữ + 1 câu
thoại).
**Tránh:** chữ và giọng hỏi HAI câu khác nhau; giọng vào muộn (#81 mất 1,5s
đầu chỉ vì giọng vào muộn); frame 0s tối đen (T04 fade-in từ đen + dead air
0,67s); hook chỉ có ở một kênh trong khi kênh còn lại im lặng hoàn toàn.

## F2 — Visual Essay: một câu hỏi lạ → 2–3 beat dữ liệu → lật lại nhận thức

**Cơ chế (1 dòng):** Một câu hỏi về thứ quen thuộc → trả lời bằng lịch sử/khoa
học ngắn gọn qua 2–3 hình → payoff làm thứ quen thuộc trở nên lạ → câu chốt
đáng nhớ + poll/CTA.

**Bằng chứng:** #81 "LOG IN" (87; 30,9s → kéo lên 45s); T05 (78; 175,5s →
cắt xuống 50s, chỉ giữ 3 beat: tin đồn → bài báo Science 1960 → số liệu
thật 8,2 tỉ người); #80 (83; 80,3s → cắt xuống 50s, bỏ ví dụ núi cao); T06
(76; Canada → 60% hồ trên thế giới → kỷ băng hà); #77 là phiên bản mini
(câu hỏi → sốc → đáp án vật lý → poll).

**Cấu trúc (45s, mục tiêu 112–124 từ):**

| Giây | Beat | Nội dung | Từ |
|---|---|---|---|
| 0–3 | Hook kép | Câu hỏi về thứ quen thuộc (F1) | 10–12 |
| 3–12 | Beat 1 — nguồn gốc/lịch sử | Câu chuyện gốc (thủy thủ ném khúc gỗ, bài báo 1960) | ~30 |
| 12–25 | Beat 2 — bằng chứng/số liệu | Con số hoặc hình ảnh chứng minh (biểu đồ tự vẽ) | ~35 |
| 25–38 | Beat 3 — lật lại | Sự thật ngược với suy nghĩ ban đầu | ~30 |
| 38–45 | Payoff + chốt | Câu đáng nhớ + poll/CTA ("Bạn có tin không? Bình luận…") | 12–15 |

**Khung kịch bản (45s, 112–124 từ):** hook 10–12 từ → beat 1 ~30 từ → beat
2 ~35 từ → beat 3 ~30 từ → payoff 12–15 từ. Kéo dài lên 50s (125–138 từ)
bằng cách thêm 1 số liệu vào beat 2, không thêm beat mới.
**Tài sản hình ảnh:** 3–4 ảnh AI/stock + 1 biểu đồ tự vẽ (nếu có số liệu) +
phụ đề hiện TỪNG CHỮ (phụ đề là chuyển động giữ mắt khi gần như không có cắt
— #80, FB-05 chứng minh). Không bao giờ để phụ đề hiện cả câu một lúc.
**Giọng/nhạc/SFX:** giọng điềm đạm, 150–165 từ/phút (#80 152, #81 162 là
mẫu); Ding khi mỗi beat hiện; Whoosh khi đổi hình; Boom nhẹ ở payoff lật lại.
Chuẩn hóa -16 LUFS (T05 gốc -31,77 LUFS — gần như không nghe được trên loa
ngoài, bắt buộc phải sửa).
**Chi phí:** dễ, 1,5–3 giờ/video (#81: 1,5–2,5 giờ — dễ nhất trong 5 video
85+; T05: 4–6 giờ vì phải cắt 175s xuống 50s và làm 5–6 hình/biểu đồ — giữ
tối đa 2 biểu đồ để không đội chi phí).
**Tránh:** quá 3 beat (T05 gốc có 1 beat/15–19s — quá chậm cho Shorts); chỉ
dùng crossfade chậm mà không có cắt cứng nào (#80: 0 cắt trong 80s); số liệu
không ghi nguồn (T05 dùng bài báo Science 1960 + U.S. Census — phải ghi nguồn
trong ghi chú kịch bản, không bịa số).

## F3 — Danh sách đếm ngược / xếp hạng: tiết lộ một phần, giữ #1 đến cuối

**Cơ chế (1 dòng):** Danh sách đã mở 1 mục ở giây 1 nhưng còn nhiều mục trống
— người xem ở lại để xem #1 là gì; mỗi mục là một payoff nhỏ, #1 là payoff
lớn.

**Bằng chứng:** H02 (78; xếp hạng 6 khoảnh khắc, mở mục 3 "Shower 🥉" trước,
các mục 1/2/4/5/6 còn trống; mục mới mỗi ~5–8s; 68,5s → cắt xuống 45s, 6 mục
→ 5 mục); H03 (67; top 5 âm thanh, mở mục 5 trước); T04 (80; 4 sự thật trong
10s → kéo lên 40s bằng 8–10 sự thật).

**Cấu trúc (45s, mục tiêu 112–124 từ):**

| Giây | Beat | Nội dung | Từ |
|---|---|---|---|
| 0–3 | Hook | Tiêu đề danh sách + 1 mục đã mở (mục giữa, KHÔNG phải #1) | 10–12 |
| 3–10 | Mục 5 | Mục yếu nhất, giới thiệu luật chơi | ~20 |
| 10–18 | Mục 4 | Mục khá hơn | ~20 |
| 18–26 | Mục 3 | Mục hay | ~20 |
| 26–34 | Mục 2 | Mục rất hay, suýt #1 | ~20 |
| 34–42 | Mục 1 | Payoff lớn nhất, giữ đến cuối | ~20 |
| 42–45 | CTA | "Số 1 của bạn là gì? Bình luận…" | 8–10 |

**Khung kịch bản (45s, 112–124 từ):** giọng phản ứng ngắn (H02 chỉ 57
từ/30s — danh sách tự gánh nội dung, giọng chỉ phản ứng với từng mục). Mỗi
mục 1–2 câu ngắn. Kéo dài lên 50s bằng cách thêm 1 mục, không kéo dài từng
mục.
**Tài sản hình ảnh:** 1 khung danh sách (tiêu đề + ô số trống dần được điền)
+ 5 clip/hình ngắn (stock/AI — KHÔNG dùng lại clip meme của người khác: clip
của H02 là meme lấy lại, L=3).
**Giọng/nhạc/SFX:** giọng phản ứng, 114–160 từ/phút; khoảng lặng 0,5–1,3s
GIỮA các mục là nhịp thở tự nhiên, không phải dead air (H02) — nhưng không
được có khoảng lặng nào trong 3s đầu. Pop/Ding mỗi lần 1 mục hiện; Riser
(drum roll) trước #1; Victory sting ở #1.
**Chi phí:** dễ, 2–3 giờ/video (H02).
**Tránh:** lộ #1 sớm (mất lý do ở lại); các mục không thật sự hay với đúng
khán giả mục tiêu (mục của H02 là hài Ấn Độ — bản làm lại chọn chủ đề quen
thuộc với khán giả Việt: âm thanh tuổi thơ, khoảnh khắc đi học, sự thật lạ);
mở đầu bằng danh sách trống (không có hook).

## F4 — Một hình ảnh phi lý: show, don't explain

**Cơ chế (1 dòng):** Một hình ảnh không thể có thật xuất hiện ngay giây 1,
không giải thích — người xem ở lại để biết "cái gì đang xảy ra vậy?".

**Bằng chứng:** B01 (76; bóng bay đỏ khổng lồ che mặt người trong hành lang,
leo thang: bóng → bóng phản ứng với 1 người → bóng to dần → cả nhóm phát
hiện; 67,6s → cắt xuống 45s); B06 (54; thạch phủ cả bể bơi, người đứng được
trên nước — "It's jelly. That's a pool. Wanna try? It bounces!"; leo thang:
thìa thạch → thạch rơi → lớp thạch → người đứng lên; 26,1s → kéo lên 40s);
D01 (80; chó chihuahua cười như người, 20,1s → kéo lên 40s bằng 3 cảnh leo
thang).

**Cấu trúc (45s, mục tiêu 40–60 từ — giọng RẤT ít):**

| Giây | Beat | Nội dung | Từ |
|---|---|---|---|
| 0–3 | Hook | Hình phi lý toàn màn hình + 1 câu giọng nói tối thiểu | 5–8 |
| 3–15 | Leo thang 1 | Vật thể xuất hiện / nhỏ | ~10 |
| 15–30 | Leo thang 2 | Vật thể to hơn / người khác phản ứng | ~10 |
| 30–42 | Leo thang 3 | Tương tác lớn nhất (người đứng lên / cả nhóm phát hiện) | ~10 |
| 42–45 | Payoff | Phản ứng cuối / nụ cười / reveal | 5–8 |

**Khung kịch bản (45s, 40–60 từ):** giọng chỉ giải thích tối thiểu, mỗi câu
1 nhịp (B06: 10 từ/30s; B01: 43 từ/30s). Không giải thích trò đùa — giải
thích là giết chết nó.
**Tài sản hình ảnh:** 3–4 cảnh AI video với CÙNG một vật thể phi lý
(Veo/Kling/Wan 2.2). Video gốc B01 vốn đã là AI (nhãn "豆包AI生成") — format
này sinh ra cho AI video.
**Giọng/nhạc/SFX:** giọng tối thiểu, ≤86 từ/phút (B01: 86); SFX gánh video:
tiếng gõ cửa ngay 0,1s (B01), Boing khi thạch nảy (B06), Whoosh khi vật thể
to lên, Record scratch khi reveal. Nhạc căng thẳng nhẹ dưới giọng.
**Chi phí:** trung bình–khó, 3–6 giờ/video (B01: 3–5 giờ; B06: 4–6 giờ).
Rủi ro lớn nhất: AI video không giữ được vật thể/nhân vật nhất quán qua các
cảnh (bóng bay/thạch đổi hình giữa các cảnh là hỏng) — cần thử prompt nhiều
lần.
**Tránh:** dead air đầu video (B01 mất 1,14s im lặng trước tiếng gõ cửa);
giọng giải thích dài dòng; vật thể đổi hình giữa các cảnh; leo thang không
tăng (cảnh sau phải to/lạ hơn cảnh trước).

## F5 — X vs Y / Kỳ vọng vs Thực tế

**Cơ chế (1 dòng):** Cùng một tình huống, hai phiên bản trái ngược — sự đối
lập là trò đùa / là cảm xúc; người xem ở lại để xem phiên bản thứ hai.

**Bằng chứng:** B04 (58; đi muộn: đại học "30 phút muộn, không ai quan tâm"
vs cấp 3 "30 giây muộn cũng không được vào"; 31,7s → kéo lên 45s); D04 (52;
ảnh cưới lãng mạn vs đời sống ngốc nghếch; 12,2s → kéo lên 40s); H05 (61;
2010 vs 2026, cùng một bức tường; 23,5s → kéo lên 40s).

**Cấu trúc (45s, mục tiêu 112–124 từ):**

| Giây | Beat | Nội dung | Từ |
|---|---|---|---|
| 0–3 | Hook | Chữ tiền đề: "X vs Y:" + tình huống | 8–10 |
| 3–15 | Phiên bản X | Phiên bản thứ nhất (kỳ vọng / bên A) | ~35 |
| 15–18 | Chuyển | Sting chuyển cảnh (record scratch / error buzz) | 0 |
| 18–33 | Phiên bản Y | Phiên bản trái ngược (thực tế / bên B) | ~35 |
| 33–42 | Đối chiếu | Hai phiên bản cạnh nhau — punchline là sự đối lập | ~28 |
| 42–45 | CTA | "Bạn thuộc team nào? Bình luận…" | 8–10 |

**Khung kịch bản (45s, 112–124 từ):** thoại là chính, 2 giọng AI khác nhau
cho 2 phía (B04 gốc: 1 người đóng 2 vai bằng cách đổi áo — bản làm lại dùng
2 giọng cho dễ phân biệt). Tốc độ tối đa ~160 từ/phút.
**Tài sản hình ảnh:** 2 cảnh đối lập (cùng một bối cảnh, 2 phiên bản);
stickman làm được (B04: người que + đối thoại nhanh + chữ tiền đề).
**Giọng/nhạc/SFX:** đối thoại nhanh nhưng KHÔNG quá 160 từ/phút (B04 gốc
260 từ/phút — quá nhanh, người không phải bản xứ không theo kịp); Record
scratch/Error buzz ở điểm chuyển; Pop khi 2 phiên bản hiện cạnh nhau.
**Chi phí:** dễ–trung bình, 3–4 giờ/video (B04).
**Tránh:** thoại 260 từ/phút; hai phiên bản không thật sự trái ngược (không
có đối lập thì không có cười); dựa vào diễn xuất (người que không diễn được
— sự đối lập phải nằm trong lời thoại và hình ảnh, không nằm trong diễn xuất).

## F6 — Quá trình biến đổi: tiến độ nhìn thấy được

**Cơ chế (1 dòng):** Người xem thấy tiến độ thay đổi từng chút — ở lại để xem
"xong chưa, thành cái gì?"; payoff là trạng thái cuối.

**Bằng chứng:** D02 (58; sơn gạch sân xám → đỏ, từng viên một; 94,7s → cắt
xuống 45s bằng tua nhanh); H01 (78; chuỗi clip "vừa khít" — mỗi clip là một
tiến độ nhỏ: bánh xe tải → bản lề → đá vừa tay → chốt cửa; 60,6s → cắt xuống
45s).

**Cấu trúc (45s, mục tiêu 30–60 từ — giọng thưa):**

| Giây | Beat | Nội dung | Từ |
|---|---|---|---|
| 0–3 | Hook | Trạng thái TRƯỚC + lời hứa: "Xem cái này biến thành…" | 8–10 |
| 3–12 | Tiến độ 1 | ~25% xong (gạch đầu tiên đỏ / clip vừa khít 1) | ~8 |
| 12–22 | Tiến độ 2 | ~50% xong | ~8 |
| 22–32 | Tiến độ 3 | ~75% xong | ~8 |
| 32–42 | Trạng thái cuối | 100% xong — payoff (sân đỏ, chốt cửa vừa khít) | ~10 |
| 42–45 | CTA | "Trước/sau — bạn thích bên nào?" | 8–10 |

**Khung kịch bản (45s, 30–60 từ):** giọng phản ứng thưa (H01: giọng phản ứng
liên tục, 124 từ/phút, phấn khích — "that was such a perfect fit… holy
moly"); nhạc là xương sống. D02 không có bằng chứng lời nói (transcript Hindi
hỏng) — không trích dẫn.
**Tài sản hình ảnh:** quay quá trình thật bằng điện thoại rồi tua nhanh
(không cần máy quay chuyên nghiệp) HOẶC ảnh AI từng bước (trước → giữa →
sau); khung chia đôi trước/sau ở payoff.
**Giọng/nhạc/SFX:** giọng phản ứng thưa; nhạc nhịp đều; Pop ở mỗi mốc tiến độ
(25/50/75%); Victory sting ở trạng thái cuối; Whoosh tua nhanh giữa các bước.
**Chi phí:** dễ, 2–3 giờ/video (D02).
**Tránh:** khoảng lặng dài mà không có gì xảy ra (D02 có khoảng lặng 5,67s ở
12,69–18,37s — điểm rơi tiềm năng); quá trình không có tiến độ rõ ràng (người
xem phải THẤY thay đổi); để nguyên 94s không tua nhanh.

## F7 — Truyện tranh AI / stickman cảm xúc: thẻ chữ + nhạc, có hoặc không có giọng kể

**Cơ chế (1 dòng):** Tranh AI hoặc stickman + thẻ chữ kể chuyện + nhạc gánh
cảm xúc — chữ LÀ kịch bản nên dịch thẻ chữ là sang ngôn ngữ khác được, không
rào cản ngôn ngữ, không tốn giọng đọc.

**Bằng chứng:** #50 (85; truyện câm: cô đơn dưới mưa → bị lãng quên → níu giữ
quá khứ → cô gái quay lại với bảng "I SEE YOU" → được nhìn thấy → "EVERYONE
DESERVES TO BE SEEN."; 90,1s → cắt xuống 50–55s, mỗi beat ~12s thay vì 22s);
FB-05 (85; stickman bài học tiền: lời hứa → định nghĩa "con buôn trung gian
thông minh" → nguyên tắc → ẩn dụ cầu → kết; 141,4s → cắt xuống 50–55s; kịch
bản ChatGPT 50–55s đã có sẵn); C03 (74; tranh AI phong cách Ghibli: xếp vali
→ chạy ra ga → trang điểm → cầu nguyện về quê ăn lễ; 105,3s → cắt xuống 50s,
giữ 5–6 ảnh); C02 (79; hoạt hình 3D khoảnh khắc cha–con gái; 23,2s → kéo lên
45s).

**Cấu trúc (50s, mục tiêu 125–138 từ nếu có giọng kể; 5–6 thẻ chữ nếu câm):**

| Giây | Beat | Nội dung | Thẻ chữ / lời kể |
|---|---|---|---|
| 0–3 | Hook | 1 hình + 1 thẻ chữ: nỗi cô đơn / lời hứa | 6–10 từ |
| 3–15 | Beat 1 — setup | Một mình / bị lãng quên | 6–10 từ |
| 15–28 | Beat 2 — níu giữ / bước ngoặt | Giữ quá khứ / người kia xuất hiện | 6–10 từ |
| 28–42 | Beat 3 — được nhìn thấy | Thay đổi: ánh sáng ấm lên, nụ cười | 6–10 từ |
| 42–50 | Payoff | Câu chốt đáng chia sẻ + CTA theo dõi | 8–12 từ |

**Khung kịch bản (50s):** bản câm: 5–6 thẻ chữ × 6–10 từ (mỗi thẻ là 1
beat). Bản có giọng kể: 125–138 từ, tốc độ 150–165 từ/phút — phân bổ: mở
10–12 từ, beat 1 ~30 từ, beat 2 ~38 từ, beat 3 ~35 từ, payoff 12–15 từ.
KHÔNG đọc nhanh như FB-05 gốc (246 từ/phút). Nếu dùng giọng Việt AI thì đọc
chậm lại ~160–200 từ/phút và kiểm tra từng câu (giọng Việt AI dễ nghe máy
móc ở tốc độ cao).
**Tài sản hình ảnh:** 5–6 ảnh AI phong cách NHẤT QUÁN + cùng một nhân vật
(phần khó nhất — C03: nhân vật AI đổi mặt/phong cách giữa các ảnh là mất cảm
xúc) HOẶC 1 rig stickman + 1 nền tái dùng (#50: 1 nền công viên đêm + 2 rig
stickman; FB-05: 1 rig stickman + 3–4 hình minh họa).
**Giọng/nhạc/SFX:** giọng kể tùy chọn; NHẠC là xương sống cảm xúc (#50: nhạc
liên tục, LRA 5,10 — nhạc lên xuống theo cảm xúc; chọn sai nhạc là hỏng cả
video). SFX tối thiểu: 1 Ding nhẹ ở bước ngoặt; 0,5s lặng trước câu chốt.
Nhạc phải có giấy phép thương mại (Mixkit/Pixabay/Freesound CC0).
**Chi phí:** trung bình, 2–6 giờ/video (#50: 2–3 giờ — rẻ nhất trong các
format cảm xúc; FB-05: 3–4 giờ; C03: 4–6 giờ).
**Tránh:** dùng lại BẤT KỲ hình/chữ/nhạc nào của bản gốc (#50: "© 2026
Christopher Thomas. All Rights Reserved." trên mọi frame; C03: watermark
"@Ghiblidaysmotion"; C02: watermark "NVV" — vẽ/phong cách của mình, không sao
chép); beat chậm hơn ~12s (#50 gốc mỗi beat 22s — quá chậm); nhân vật AI đổi
mặt/phong cách giữa các ảnh; nhạc sai cảm xúc.

## F8 — Nhãn "POV:": đặt người xem vào trong cảnh

**Cơ chế (1 dòng):** Hai chữ "POV:" + một tình huống — người xem lập tức là
nhân vật chính, không cần giới thiệu; đây là hook chữ rẻ nhất trong 30 video.

**Bằng chứng:** B05 (55; "POV:when you're just too thief" — trốn trong lá →
chạy → đánh nhau → trốn sau tường; 59,6s → cắt xuống 45s; không có lời nói,
chỉ nhạc); H07 (54; slapstick không chữ/không lời thật — hài hành động thuần);
T07 (74; gọi thẳng người xem "Don't get a part-time job, do this instead" —
ngôi thứ hai, cùng họ với POV).

**Cấu trúc (45s, mục tiêu 0–30 từ — giọng tối thiểu hoặc không có):**

| Giây | Beat | Nội dung | Từ |
|---|---|---|---|
| 0–3 | Hook | Nhãn "POV: …" (5–8 từ) + hành động đầu tiên | 5–8 |
| 3–15 | Vào cảnh | Người xem ĐANG ở trong tình huống | 0–5 |
| 15–30 | Leo thang | Tình huống tệ hơn / buồn cười hơn | 0–5 |
| 30–42 | Cao trào | Bị bắt / thoát / twist | 0–5 |
| 42–45 | Phản ứng | Khuôn mặt / thở phào + CTA | 0–5 |

**Khung kịch bản (45s, 0–30 từ):** nhãn POV 5–8 từ là toàn bộ kịch bản chữ;
phần còn lại là hành động + nhạc. Ví dụ nhãn (theo mẫu B05): "POV: Bạn đi học
muộn mà gặp đúng thầy hiệu trưởng", "POV: Bạn là người duy nhất trong nhóm
chưa làm bài tập".
**Tài sản hình ảnh:** stickman hoặc ảnh AI; 1 bối cảnh + 1 nhân vật.
**Giọng/nhạc/SFX:** không có lời nói hoặc tối thiểu; NHẠC + SFX gánh video
(B05: nhạc lên xuống mạnh, LRA 23,80): tiếng bước chân, nhịp tim/suspense
drone khi trốn, Record scratch khi bị bắt, Fail sting ở cuối.
**Chi phí:** nhãn thì rẻ nhất; hành động thì trung bình–khó, 4–6 giờ/video
(B05) vì timing hành động phải chính xác từng nhịp.
**Tránh:** nhãn POV trên tình huống người xem không hình dung được ngay;
timing hành động sai nhịp (sai 0,5s là mất cười); nhãn dài dòng (quá 8 từ là
người xem không đọc kịp trong 3s).

---

# 3 format ưu tiên (rẻ nhất làm trước)

## Ưu tiên 1 — Visual Essay: hỏi → đáp (ngách Tò mò)

**Video tham chiếu (≥3):** #81 "LOG IN" (87; 30,9s) · #80 "WATER CAN BOIL"
(83; 80,3s) · T05 (78; 175,5s) · T06 (76; 66,0s).
**Vì sao làm trước:** rẻ nhất trong các format có lời kể — 3–4 ảnh AI/stock
+ giọng AI + phụ đề từng chữ; 1,5–3 giờ/video; 4/7 video Tò mò đã là Visual
Essay (Gemini xếp Tò mò dễ làm nhất + dễ viral nhất). Công thức: F2 + hook
kép F1.
**Lịch thử:** 2 video đầu tuần 2 (kịch bản 03 trong kế hoạch ChatGPT: tò mò,
motion graphics + quiz, 40–50s).

## Ưu tiên 2 — Countdown / xếp hạng: tiết lộ một phần (ngách Hài / Tò mò)

**Video tham chiếu (≥3):** H02 (78; 68,5s) · H03 (67; 61,8s) · T04 (80;
10,1s).
**Vì sao thứ hai:** dễ thứ hai — khung danh sách + 5 clip/hình + giọng phản
ứng; 2–3 giờ/video; cơ chế giữ chân rõ ràng nhất (người xem ở lại vì #1 chưa
lộ). Công thức: F3 + hook kép F1.
**Lịch thử:** 1 video tuần 2 (kịch bản 01/02 hài: stickman 2D hoặc tình huống
phi lý, 40–45s — dùng khung countdown cho phiên bản "Top 5…" nếu kịch bản
stickman gặp khó về rig).

## Ưu tiên 3 — Truyện tranh AI / stickman cảm xúc (ngách Cảm xúc)

**Video tham chiếu (≥3):** #50 (85; 90,1s) · FB-05 (85; 141,4s) · C03 (74;
105,3s) · C02 (79; 23,2s).
**Vì sao thứ ba:** đắt nhất trong 3 format ưu tiên (2–6 giờ/video) nhưng là
format duy nhất của ngách Cảm xúc — ngách có 2 video 85+ (#50, FB-05) và kịch
bản FB-05 50–55s đã có sẵn (ChatGPT). Công thức: F7 + hook kép F1. **Điều
kiện tiên quyết:** phải có rig stickman hoặc quy trình ảnh AI nhất quán trước
— hiện repo stickman CHƯA TỒN TẠI (khoảng trống lớn nhất; xem mục "Còn thiếu").
**Lịch thử:** 1 video tuần 2 (kịch bản 05: cảm xúc, ảnh AI + lời dẫn, 50–55s
— lưu ý ChatGPT ghi 50–60s, khung này chốt tối đa 55s theo quy tắc cứng).

---

# 3 template trống (điền vào là viết được kịch bản)

## Template A — Visual Essay (45s, 112–124 từ)

| Giây | Hình | Chữ trên màn hình | Giọng (số từ) | SFX / nhạc |
|---|---|---|---|---|
| 0–3 | Ảnh mở + thẻ tiêu đề | [Câu hỏi — 3–5 từ lớn] | [Câu hỏi đầy đủ — 10–12 từ] | Whoosh + Pop |
| 3–12 | Ảnh 1: nguồn gốc/lịch sử | [Từ khóa beat 1] | [~30 từ] | Ding khi ảnh hiện |
| 12–25 | Ảnh 2: bằng chứng/số liệu | [Con số lớn] | [~35 từ] | Ding khi số hiện |
| 25–38 | Ảnh 3: lật lại | [Từ khóa lật lại] | [~30 từ] | Whoosh + Boom nhẹ |
| 38–45 | Thẻ cuối | [Câu chốt + "Bạn nghĩ sao?"] | [12–15 từ] | Ding + nhạc kết |
| Ghi chú | Nguồn số liệu: [ghi nguồn, không bịa số] | Phụ đề hiện TỪNG CHỮ | Tổng: ___ từ (mục tiêu 112–124) | Chuẩn hóa -16 LUFS |

## Template B — Countdown / xếp hạng (45s, 112–124 từ)

| Giây | Hình | Chữ trên màn hình | Giọng (số từ) | SFX / nhạc |
|---|---|---|---|---|
| 0–3 | Khung danh sách | [Tiêu đề Top 5…] + mục [__] đã mở | [Tiêu đề + phản ứng — 10–12 từ] | Whoosh + Pop |
| 3–10 | Mục 5 | [#5: ___] | [Phản ứng — ~20 từ] | Pop |
| 10–18 | Mục 4 | [#4: ___] | [Phản ứng — ~20 từ] | Pop |
| 18–26 | Mục 3 | [#3: ___] | [Phản ứng — ~20 từ] | Pop |
| 26–34 | Mục 2 | [#2: ___] | [Phản ứng — ~20 từ] | Pop |
| 34–42 | Mục 1 | [#1: ___] (lớn nhất) | [Phản ứng — ~20 từ] | Riser + Victory |
| 42–45 | Thẻ cuối | ["Số 1 của bạn là gì?"] | [CTA — 8–10 từ] | Ding |
| Ghi chú | Mục 1 KHÔNG được lộ trước giây 34 | Clip/hình: stock/AI của mình | Tổng: ___ từ (mục tiêu 112–124) | Khoảng lặng giữa mục là nhịp, không phải lỗi |

## Template C — Truyện stickman / tranh AI cảm xúc (50s, 125–138 từ nếu có giọng kể)

| Giây | Hình | Chữ trên màn hình (thẻ chữ) | Giọng kể (số từ) | SFX / nhạc |
|---|---|---|---|---|
| 0–3 | Ảnh 1: cảnh mở | [Thẻ 1: ___ — 6–10 từ] | [Mở — 10–12 từ, hoặc câm] | Nhạc bắt đầu, nhỏ |
| 3–15 | Ảnh 2: setup | [Thẻ 2: ___] | [~30 từ] | Nhạc lên nhẹ |
| 15–28 | Ảnh 3: bước ngoặt | [Thẻ 3: ___] | [~38 từ] | Ding nhẹ ở ngoặt |
| 28–42 | Ảnh 4: được nhìn thấy | [Thẻ 4: ___] | [~35 từ] | Nhạc swell |
| 42–50 | Ảnh 5: payoff | [Câu chốt — 8–12 từ] | [12–15 từ] + 0,5s lặng trước câu chốt | Nhạc kết |
| Ghi chú | 5–6 ảnh CÙNG phong cách + CÙNG nhân vật | Thẻ chữ LÀ kịch bản (bản câm) | Tổng: ___ từ (mục tiêu 125–138) | Nhạc có giấy phép thương mại |

---

# Thư viện SFX lõi (18 file — cần sưu tầm trước khi sản xuất)

Nguồn gợi ý: Mixkit / Pixabay Sound Effects / Freesound (ưu tiên CC0) —
chỉ dùng file có giấy phép cho phép dùng thương mại. Chưa có file nào được
tải về (thư mục Core_SFX chưa tồn tại — xem mục "Còn thiếu").

| # | SFX | Dùng ở đâu (giây) | Công thức | Ghi chú |
|---|---|---|---|---|
| 1 | Whoosh | 0,1s (mở đầu) + mỗi lần đổi cảnh | Mọi công thức | Lớp SFX đầu tiên trong 3s đầu |
| 2 | Pop | Khi chữ/ảnh/mục hiện | F1, F2, F3, F6 | Lớp SFX thứ hai trong 3s đầu |
| 3 | Ding | Khi số liệu/beat quan trọng hiện | F2, F3, F7 | Nhấn từ khóa |
| 4 | Boom | Payoff lật lại | F2, F4 | Không dùng quá 1 lần/video |
| 5 | Bass Hit | Mở đầu mạnh / reveal | F4, F8 | Thay Boom khi cần nhẹ hơn |
| 6 | Riser (drum roll) | Trước #1 / trước payoff | F3, F6 | Kéo căng 2–3s trước reveal |
| 7 | Victory sting | Ở #1 / trạng thái cuối | F3, F6 | Ngắn, 1–2s |
| 8 | Record Scratch | Điểm chuyển X→Y / khi bị bắt | F5, F8 | Dừng nhạc đột ngột = gây cười |
| 9 | Fail sting | Cuối X vs Y / POV bị bắt | F5, F8 | Kiểu "wah-wah" |
| 10 | Error buzz | Chuyển phiên bản / sai lầm | F5 | Ngắn, không chói |
| 11 | Cartoon boing | Khi thạch/vật nảy | F4 | B06: "It bounces!" |
| 12 | Door knock | 0,1s mở đầu | F4 | B01: tiếng gõ cửa là nhịp đầu tiên |
| 13 | Footsteps | Khi trốn/chạy | F8 | B05: nhạc + bước chân gánh video |
| 14 | Laugh (cười) | Sau punchline | F3, F5 | Nhẹ, không át giọng |
| 15 | Crickets (dế kêu) | Sau câu đùa nhạt / im lặng | F5 | Chỉ dùng khi cố tình gây ngượng |
| 16 | Suspense drone | Khi trốn / trước reveal | F8, F4 | Nhạc nền căng thẳng, dưới giọng |
| 17 | Camera click | Khi ảnh/bằng chứng hiện | F2 | Nhấn "đây là bằng chứng" |
| 18 | Transition swoosh | Giữa các beat dài | F2, F7 | Khác Whoosh ở chỗ nhẹ hơn, dài hơn |

**Quy tắc đặt SFX (Gemini + đã kiểm chứng):** từ đầu tiên + SFX ở 0,05–0,1s;
≥2 lớp SFX trong 3s đầu; SFX mỗi 1,5–2s trong 10s đầu (sau đó thưa dần);
BGM thấp hơn giọng -18 đến -24 dB; SFX không bao giờ át giọng.

---

# Checklist

## Hook 3 giây (kiểm tra trước khi duyệt kịch bản)

- [ ] Giọng vào từ 0,1s — không có khoảng lặng nào ở đầu (0,0s).
- [ ] Từ đầu tiên + SFX (Whoosh/Pop) ở 0,05–0,1s.
- [ ] ≥2 lớp SFX trong 3s đầu.
- [ ] Chữ lớn trên màn hình và giọng nói hỏi CÙNG một câu (hook kép F1).
- [ ] Frame 0s không tối đen, không fade-in từ đen.
- [ ] Câu hỏi/lời hứa hiểu được khi TẮT TIẾNG (chỉ đọc chữ vẫn hiểu).
- [ ] Câu hỏi/lời hứa hiểu được khi NHẮM MẮT (chỉ nghe giọng vẫn hiểu).
- [ ] Hình ở giây 1 đủ lạ/đẹp để dừng tay lướt (bóng bay, số liệu sốc, chữ lớn).
- [ ] 3s cuối có câu hỏi gợi bình luận hoặc poll (engagement bait).

## Tiêu đề (title)

- 38–45 ký tự hiển thị đầy đủ trên mobile (ChatGPT: tối đa 35–60 ký tự).
- Từ khóa chính nằm trong 5 từ đầu tiên.
- Tối đa 1–2 hashtag.
- 4 dạng đã kiểm chứng (Gemini): câu hỏi / tuyên bố sốc / "Top 5…" / "POV: …".
- Không clickbait sai nội dung — tiêu đề phải là đúng câu hook trong video.

## Thumbnail (khung thumbnail nhúng sẵn — baked-in frame)

- Chèn 1 frame 0,1s có độ tương phản cao ngay đầu video (nền + chủ thể +
  chữ lớn), vì Shorts lấy thumbnail từ frame đầu.
- Chủ thể chiếm ~60% khung hình; 3–5 từ lớn ở 1/3 giữa màn hình.
- Tránh 25% dưới cùng (vùng phụ đề/nút bị che).

## Audio (kiểm tra trước khi xuất file)

- [ ] Giọng vào từ 0,1s, không dead air đầu.
- [ ] Chuẩn hóa ~-16 LUFS (đo bằng ffmpeg loudnorm).
- [ ] True peak ≤ -1 dBTP (không clip — 4/25 video gốc bị clip).
- [ ] Tốc độ nói 150–165 từ/phút (đo từ transcript/SRT).
- [ ] BGM thấp hơn giọng -18 đến -24 dB.
- [ ] SFX mỗi 1,5–2s trong 10s đầu, sau đó thưa dần; không át giọng.
- [ ] Khoảng lặng giữa các mục/beat ≤1,3s (là nhịp thở); không có khoảng lặng
      >2s trừ khi cố tình (0,5s lặng trước câu chốt F7).
- [ ] Phụ đề hiện TỪNG CHỮ, không hiện cả câu một lúc.

---

# Cửa sang tuần 2 — kiểm tra (ChatGPT + Gemini)

| Điều kiện (ChatGPT) | Trạng thái | Bằng chứng |
|---|---|---|
| ≥24 video phân tích đầy đủ | ✅ ĐẠT — 30/30 | `deep-analysis-5x85-20261115.md` (5) + `deep-analysis-25-20261115.md` (25) |
| ≥5 công thức có ví dụ cụ thể | ✅ ĐẠT — 8 công thức | Tài liệu này (F1–F8), mỗi công thức 2–4 video gốc |
| 3 format ưu tiên đã chọn | ✅ ĐẠT | Visual Essay · Countdown · Truyện tranh AI/stickman |
| Mỗi format ≥3 video tham chiếu | ✅ ĐẠT | VE: #81/#80/T05/T06 · Countdown: H02/H03/T04 · Truyện: #50/FB-05/C03/C02 |
| Kế hoạch sản xuất trong 38–65s, không quay phim | ✅ ĐẠT | Mọi công thức chốt 40–55s, không máy quay |

| Điều kiện (Gemini — gác cổng sang tuần 2) | Trạng thái |
|---|---|
| Nhìn chủ đề mới là ghép ngay được ≥3 kiểu hook 3s | ✅ ĐẠT — 8 cơ chế, F1 áp dụng cho mọi video |
| Biết chính xác kịch bản Tò mò 48s cần bao nhiêu từ và cắt ở đâu | ⚠️ MỘT PHẦN — khung này: 48s = 120–132 từ (150–165 từ/phút); con số 140–160 từ của Gemini tính theo ~175–200 từ/phút, nhanh hơn vùng an toàn — cần chốt tốc độ giọng trước khi viết |
| Biết chèn Boom/Whoosh ở giây nào và tắt nhạc nền ở giây nào | ✅ ĐẠT — bảng SFX lõi + quy tắc đặt SFX ở trên |

**Kết luận cửa:** 5/5 điều kiện ChatGPT đạt, 2/3 điều kiện Gemini đạt (1
một phần). Đủ điều kiện bắt đầu viết kịch bản 23/11/2026 theo kế hoạch.

## Còn thiếu trước khi viết kịch bản (23/11)

1. **Người dùng duyệt task b4413e82** (bản chọn 30 đã được Verify ce4f147d
   kiểm chứng — đang chờ duyệt). Không duyệt thì vẫn viết được kịch bản từ
   tài liệu này, nhưng bản chọn chưa chính thức chốt.
2. **Repo stickman CHƯA TỒN TẠI** — không có rig/template/animation nào.
   Khoảng trống lớn nhất. Cần xây trước khi làm F7 (và các phần stickman của
   F1/F5/F8): đề xuất Manim + Remotion (1 rig, tái dùng cho mọi video).
3. **Thư viện Core_SFX chưa có file nào** — cần sưu tầm 18 SFX trên với
   giấy phép thương mại (Mixkit/Pixabay/Freesound CC0) trước 25–26/11.
4. **Giọng Việt AI chưa thử trên VPS này** (Kokoro/Qwen3-TTS hoặc Edge TTS)
   — FB-05 cần giọng Việt; phải thử và kiểm tra từng câu trước khi sản xuất.
   Kịch bản FB-05 50–55s của ChatGPT đã có sẵn.
5. **API key provider: chưa có key nào** (Pexels/Pixabay/GIPHY/Tenor/
   Freesound/Unsplash đều trống; task đăng ký chết 12:18 do chờ đăng nhập
   Google Pixabay). Không chặn sản xuất: gateway vẫn chạy bằng nguồn miễn phí
   không cần key (Openverse, Wikimedia, Mixkit, Imgflip) — nhưng Pexels/
   Pixabay sẽ mở rộng kho ảnh cho Visual Essay.
6. **File SRT: chưa có file nào** (chỉ có transcript.txt 30s đầu). Cần SRT
   có timestamp nếu phụ đề từng chữ được căn thời gian từ transcript.
7. **4 link Facebook share/p vẫn chưa đọc được** (Apify bị chặn từ VPS này,
   Facebook chưa liên kết) — 4 video đó nằm ngoài 30 nên không chặn tuần 2.
8. **Hook nói của 4 video Hindi chưa xác định** (H05, H08, C03, D02 —
   Whisper thất bại) — không trích dẫn lời nói của chúng; dùng bằng chứng
   hình ảnh/audio đo được thôi.

## Lịch tuần 2 (từ kế hoạch ChatGPT, đã khớp với khung này)

- **T2 23/11 — viết 5 kịch bản gốc:** 01 hài stickman 40–45s (F7/F3) · 02
  hài tình huống phi lý 40–45s (F4) · 03 tò mò Visual Essay/quiz 40–50s (F2)
  · 04 bất ngờ story animation 45–55s (F5/F8) · 05 cảm xúc ảnh AI + lời dẫn
  50–55s (F7). Dùng 3 template trống ở trên; mỗi kịch bản phải qua đủ 9 mục
  checklist hook 3s.
- **T3 24/11 — duyệt/sửa/chốt kịch bản + chuẩn bị tài sản/giọng** (rig
  stickman, ảnh AI, giọng Việt AI, thư viện SFX).
- **25–26/11 — làm + kiểm tra 5 video mẫu** (audio checklist + hook
  checklist trước khi xuất).
- **27–29/11 — đăng thử 11:30/20:00**, báo cáo sơ bộ 24–72h, kiểm tra lại
  7 ngày và 28 ngày.

---

*Hoàn thành 2026-11-15. 30/30 video đã phân tích sâu → 8 công thức → 3
format ưu tiên → 3 template trống. Bước tiếp theo: viết 5 kịch bản gốc
23/11/2026.*
