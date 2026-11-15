# Phân tích sâu 25 video còn lại — báo cáo Engineer (2026-11-15)

**Nguồn:** `selection-30-20261115.md` + `.csv` (bản FB-05, trung bình 69,67) ·
`deep-analysis-hook-sheet-20261115.md` · `deep-analysis-5x85-20261115.md` (5 video 85+
đã phân tích trước) · `video_analysis/<thư mục>/` (summary.json, timeline.md,
keyframes, audio.wav 30s, transcript.txt Whisper.cpp Base) · khung hình bổ sung tự
trích bằng ffmpeg vào `video_analysis/deep25/` (0/1/2s + 25%/50%/75% mỗi video +
contact sheet 2×3).

**Thứ tự:** theo ngách — Hài H01–H08 → Tò mò T04–T07 → Bất ngờ B01–B06 →
Cảm xúc C02, C03, C05 → Đời thường D01–D04. 5 video 85+ (#77, #50, #81, #80,
FB-05) đã có trong `deep-analysis-5x85-20261115.md`, không lặp lại ở đây.

## Giới hạn trung thực (áp dụng cho cả 25 video)

- **Transcript chỉ có 30 giây đầu** (audio.wav là clip 30s). Hook nói 3s ĐƯỢC đánh giá,
  nhưng pacing/audio sau 30s KHÔNG được đánh giá.
- **Không nghe được audio.** Mọi nhận xét về âm thanh dựa trên transcript +
  phân tích ffmpeg (loudnorm/ebur128, silencedetect) trên audio.wav — không phải
  nghe trực tiếp. Nhạc/SFX cụ thể (có nhạc nền hay không, tiếng hiệu ứng nào) là
  **chưa đánh giá được**, trừ khi transcript hoặc phép đo chứng minh.
- **Chỉ xem frame tĩnh**, không xem video chạy: mỗi video xem 1 contact sheet 6
  frame (0/1/2s + 25%/50%/75%). Chuyển động thực (zoom/pan, hiệu ứng) chỉ suy ra
  từ cụm frame, không quan sát trực tiếp.
- **Ngôn ngữ là Whisper Base tự nhận**, có thể nhận nhầm. Đặc biệt: Whisper
  THẤT BẠI trên một số audio tiếng Hindi (H05, H08, C03, D02) — transcript lặp
  một từ/vô nghĩa, coi như **không có bằng chứng hook nói** cho các video đó.
- **Keyframe = 0 là lỗi đo, không phải "video tĩnh".** Nhiều video TikTok HEVC
  (H03, H04, B04, B05, C02, C05) ghi 0 keyframe đổi cảnh ở ngưỡng 0,4 nhưng
  contact sheet cho thấy nội dung đổi rõ rệt — phép đo không bắt được cắt, không
  có nghĩa video không có cắt.
- Trong mỗi mục, **Quan sát** = điều thấy/đo được; **Suy luận** = điều rút ra.
  Không trình bày suy luận như sự thật quan sát.

## Cách chấm lại

Công thức gốc: tổng = 5H + 4R + 4F + 3P + 2C + A + L
(H hook 25%, R retention 20%, F faceless 20%, P payoff 15%, C tốc độ sản xuất 10%,
A khán giả 5%, L bản quyền 5%). Chỉ đổi điểm khi có bằng chứng mới (hook nói,
audio, pacing) — không đổi điểm vì cảm tính.

---

# H01 — #68 — 78 điểm — KẾT LUẬN: GIỮ NGUYÊN 78

- **URL:** https://www.tiktok.com/@nickbuthappy/video/7556282924430118199
- **Kênh / ngách / thời lượng:** @nickbuthappy / humor / 60,65s, 1080x1920 hevc
- **Ngôn ngữ nói:** tiếng Anh · 62 từ/30s ≈ 124 từ/phút
- **Điểm gốc:** H=4 R=4 F=4 P=4 C=4 A=4 L=2 → 78

## 1. Hook (3s đầu)

- **Quan sát:** Frame 0/1/2s: chữ lớn "Things meant to be perfect" + "Perfect
  fit..." trên clip bánh xe tải lăn khít vào rãnh; góc dưới-phải là facecam người
  đàn ông đang phản ứng (mắt mở to, miệng há). Transcript: giọng nói vào ngay từ
  đầu — "things meant to be perfect… that was such a perfect fit… wait it was
  like that little crevice was made for your vacuum… holy moly". Audio: không có
  khoảng lặng nào ≥0,5s; độ lớn -17,38 LUFS.
- **Suy luận:** Hook nói trùng đúng với chữ trên màn hình ("perfect fit") — hook
  kép, dù không phải cùng một câu hỏi như #77 mà là cùng một lời hứa (sự vừa khít
  hoàn hảo). Facecam phản ứng là "người dẫn cảm xúc": anh ta nói hộ cảm giác của
  người xem ("this is insane"). **H giữ 4.**

## 2. Pacing

- **Quan sát:** Phép đo ghi 1 keyframe (55,37s) — là lỗi đo (xem Giới hạn): sheet
  cho thấy ít nhất 4 clip khác nhau (bánh xe tải → bản lề cửa → đá vừa tay →
  chốt cửa). Transcript: giọng liên tục, phấn khích, không khoảng lặng.
- **Suy luận:** Mỗi clip là một payoff nhỏ ("vừa khít"), dồn liên tiếp — đúng cơ
  chế compilation: người xem ở lại để xem clip vừa khít tiếp theo. **R giữ 4.**

## 3. Audio

- **Quan sát:** Giọng Anh liên tục, phấn khích; không khoảng lặng ≥0,5s; độ lớn
  -17,38 LUFS, LRA 6,50. Không có bằng chứng về nhạc nền/SFX trong dữ liệu đo được.
- **Suy luận:** Giọng phản ứng liên tục là xương sống — bản làm lại cần giọng AI
  phấn khích tương tự, không được đọc đều đều. **Nhạc/SFX: chưa đánh giá được.**

## 4. Cấu trúc câu chuyện

- **Quan sát (từ frame + transcript):** Lời hứa ("things meant to be perfect") →
  clip 1 bánh xe → clip 2 bản lề → clip 3 đá → clip 4 chốt cửa (clip cuối là cái
  vừa khít nhất, ở ~55s).
- **Suy luận:** Không có cốt truyện, chỉ có chuỗi payoff nhỏ tăng dần. Payoff cuối
  (chốt cửa) là cái thỏa mãn nhất — đúng quy tắc compilation: để cái hay nhất
  cuối cùng. **P giữ 4.**

## 5. Cách làm lại không cần máy quay

- Compilation clip vừa khít: clip stock/AI (vật vừa khít vào chỗ của nó) + chữ lớn
  + giọng AI phản ứng. **Bỏ facecam** — người đàn ông trong video gốc là người
  thật, bản làm lại không cần và không được dùng lại mặt anh ta. **F giữ 4.**

## 6. Chi phí sản xuất

- **Độ khó: dễ.** Thời gian làm lại ước tính 2–3 giờ (4–5 clip stock/AI + chữ +
  giọng). Công cụ: Pexels/Pixabay hoặc ảnh AI + giọng AI + CapCut. Rủi ro lớn
  nhất: tìm đủ clip "vừa khít" thật sự thỏa mãn (clip dở là hỏng cả video); và
  giọng AI phải phấn khích, không được đều. **C giữ 4.**

## Phán quyết điểm: GIỮ NGUYÊN 78 (H=4 R=4 F=4 P=4 C=4 A=4 L=2)

Hook nói xác nhận hook chữ (cùng lời hứa "perfect fit"), giọng vào ngay 0s.
**Cảnh báo bản quyền:** các clip là video satisfying lấy lại + giao diện TikTok
và hashtag "#perfectfit" hiện trên frame; facecam là người thật. Bản làm lại
phải dùng clip stock/AI của mình, không lấy clip gốc. L=2 đã tính điều này.

---

# H02 — #69 — 78 điểm — KẾT LUẬN: GIỮ NGUYÊN 78

- **URL:** https://www.tiktok.com/@top__rankings/video/7483949038782483734
- **Kênh / ngách / thời lượng:** @top__rankings / humor / 68,55s, 1080x1920 hevc
- **Ngôn ngữ nói:** tiếng Anh · 57 từ/30s ≈ 114 từ/phút
- **Điểm gốc:** H=4 R=4 F=4 P=4 C=4 A=3 L=3 → 78

## 1. Hook (3s đầu)

- **Quan sát:** Frame 0/1/2s: danh sách "Ranking Indian moments (Number 1 is the
  best)", mục 3 "Shower 🥉" đã hiện, các mục 1/2/4/5/6 còn trống; dưới là clip
  một người đàn ông trong xe. Transcript: giọng phản ứng — "I find like where
  okay where where does he shower shower. Oh no. Oh wait man. No, no, no, no. No
  You don't have to do that. Why did you redeem it? Why did you redeem it?"
- **Suy luận:** Hook là **tiết lộ một phần**: danh sách đã mở 1 mục (số 3) nhưng
  còn 5 mục trống — người xem ở lại để xem số 1 là gì. Giọng không nói lại tiêu
  đề danh sách, chỉ phản ứng với clip — nhưng danh sách tự nó đã là hook.
  **H giữ 4.**

## 2. Pacing

- **Quan sát:** 9 keyframe đổi cảnh (5,87 / 27,9 / 33,53 / 37,9 / 41,87 / 46,6 /
  47,3 / 65,37 / 65,47s). Các mục hiện dần: mục 5 "Why did you redeem it" ở
  ~25%, mục 2 "I'm under water" + mục 4 "Indian tinder" ở ~50%, mục 6 "How can
  you slap" ở ~75%. Audio: 6 khoảng lặng 0,5–1,3s ở 13,4–27,1s — đúng khoảng
  giữa các mục (nhịp ngắt tự nhiên giữa các clip). Độ lớn -15,30 LUFS, LRA 3,80.
- **Suy luận:** Nhịp của danh sách: một mục mới mỗi ~5–8s sau phút đầu, mỗi mục
  là một clip ngắn. Các khoảng lặng là nhịp thở giữa các mục, không phải dead
  air. **R giữ 4.**

## 3. Audio

- **Quan sát:** Giọng Anh phản ứng liên tục; các khoảng lặng 0,5–1,3s nằm giữa
  các mục danh sách. Độ lớn -15,30 LUFS (gần chuẩn -16).
- **Suy luận:** Giọng phản ứng + ngắt giữa các mục là nhịp đúng của format
  countdown. **Nhạc/SFX: chưa đánh giá được.**

## 4. Cấu trúc câu chuyện

- **Quan sát (từ frame + transcript):** Danh sách 6 mục, mở dần từ dưới lên:
  #3 "Shower" → #5 "Why did you redeem it" → #2 "I'm under water" → #4
  "Indian tinder" → #6 "How can you slap" → #1 (chưa lộ trong 30s đầu, nằm sau
  65s). Mỗi mục là một meme clip Ấn Độ.
- **Suy luận:** Cấu trúc countdown chuẩn: tiết lộ từ từ, giữ #1 đến cuối. Payoff
  là #1 — người xem phải ở lại 68s mới biết. **P giữ 4.**

## 5. Cách làm lại không cần máy quay

- Danh sách xếp hạng: chữ lớn + clip stock/AI + giọng AI phản ứng; mở một mục
  mỗi ~8s, giữ #1 đến cuối. Không cần mặt người. **F giữ 4.**

## 6. Chi phí sản xuất

- **Độ khó: dễ.** Thời gian làm lại ước tính 2–3 giờ (6 clip ngắn + danh sách
  chữ + giọng). Công cụ: clip stock/AI + giọng AI + CapCut. Rủi ro lớn nhất:
  các mục trong danh sách phải thật sự buồn cười với đúng khán giả mục tiêu
  (hài Ấn Độ ở đây — bản làm lại nên chọn chủ đề quen thuộc với khán giả Việt).
  **C giữ 4.**

## Phán quyết điểm: GIỮ NGUYÊN 78 (H=4 R=4 F=4 P=4 C=4 A=3 L=3)

Tiết lộ một phần (mục 3 đã mở, 5 mục còn trống) là hook đúng của format
countdown; các khoảng lặng là nhịp giữa các mục, không phải lỗi. **Cảnh báo bản
quyền:** các clip là meme lấy lại (người thật, clip mạng) — L=3 đã tính; bản làm
lại phải dùng clip stock/AI của mình.

---

# H03 — #61 — 67 điểm — KẾT LUẬN: GIỮ NGUYÊN 67

- **URL:** https://www.tiktok.com/@clippyy07/video/7490969521017130262
- **Kênh / ngách / thời lượng:** @clippyy07 / humor / 61,81s, 1080x1920 hevc
- **Ngôn ngữ nói:** tiếng Anh · 54 từ/30s ≈ 108 từ/phút
- **Điểm gốc:** H=4 R=3 F=3 P=3 C=4 A=4 L=2 → 67

## 1. Hook (3s đầu)

- **Quan sát:** Frame 0/1/2s: danh sách "TOP 5 MOST ICONIC SOUNDS", mục 5 "What
  Did He Do?" đã hiện, các mục 1–4 còn trống; dưới là clip một thanh niên đeo
  tai nghe đang phản ứng. Transcript: giọng nói — "Just go to the office. What I
  do, just go to the office. What I do? Yo bro, who got you smiling like that
  like man happy Yo, come on bro. Hey, man, these lights look pretty good for
  real bro check out these colors."
- **Suy luận:** Cũng là tiết lộ một phần như H02, nhưng ở đây **mỗi mục là một
  âm thanh** — người xem ở lại để nghe âm thanh số 1. Giọng trong transcript là
  lời của chính các clip âm thanh (không phải giọng dẫn), nên hook là danh sách
  chữ + âm thanh mẫu. **H giữ 4.**

## 2. Pacing

- **Quan sát:** Phép đo ghi 0 keyframe — là lỗi đo (xem Giới hạn): sheet cho thấy
  nội dung đổi rõ (phản ứng trong nhà → ngoài trời → phòng đèn đỏ → cận cảnh
  giày). Các mục hiện dần: #5 ở 1s, #3 "Who Got You Smilling Like That" +
  #4 "You Need To Leave" ở ~25%, #2 "Where You Clothes At?" ở ~50%, #1 "What
  The Hell" ở ~75%. Audio: độ lớn -23,09 LUFS (nhỏ), LRA 14,10 (dải động rất
  rộng — các âm thanh mẫu lúc to lúc nhỏ); 3 khoảng lặng 0,5–0,6s ở 22,9–28,5s.
- **Suy luận:** Nhịp của danh sách âm thanh: mỗi mục là một âm thanh ngắn + phản
  ứng. Dải động rộng là đặc trưng của format (âm thanh mẫu to, khoảng giữa nhỏ).
  **R giữ 3.**

## 3. Audio

- **Quan sát:** Độ lớn -23,09 LUFS (nhỏ — cần tăng khi làm lại); LRA 14,10 cho
  thấy âm thanh mẫu có lúc rất to, lúc nhỏ. Các khoảng lặng ở 22,9–28,5s là ngắt
  giữa các mục.
- **Suy luận:** Âm thanh LÀ nội dung ở đây, không phải nền. Bản làm lại phải
  chuẩn hóa âm lượng từng mục về cùng một mức, không để mục to/mục nhỏ chênh
  nhau như bản gốc. **Nhạc nền: chưa đánh giá được.**

## 4. Cấu trúc câu chuyện

- **Quan sát (từ frame + transcript):** Danh sách 5 âm thanh, mở dần từ #5 lên
  #1: "What Did He Do?" → "You Need To Leave" → "Who Got You Smilling Like
  That" → "Where You Clothes At?" → "What The Hell".
- **Suy luận:** Countdown âm thanh — payoff là âm thanh #1 ("What The Hell").
  Không có cốt truyện, chỉ có thứ tự. **P giữ 3.**

## 5. Cách làm lại không cần máy quay

- Danh sách top-5 âm thanh: chữ lớn + hình AI/stock + **âm thanh gốc tự tạo**
  (không lấy lại âm thanh meme có bản quyền). Mỗi mục là một âm thanh ngắn do
  mình làm (giọng AI + SFX). **F giữ 3** — khó hơn H02 vì âm thanh phải tự làm,
  không thể lấy clip có sẵn.

## 6. Chi phí sản xuất

- **Độ khó: trung bình.** Thời gian làm lại ước tính 3–4 giờ (5 âm thanh tự tạo
  + hình + giọng). Công cụ: giọng AI + SFX miễn phí thương mại (Pixabay/Mixkit)
  + CapCut. Rủi ro lớn nhất: âm thanh tự tạo không đủ "iconic" — phải chọn âm
  thanh thật sự quen thuộc với khán giả (tiếng quen thuộc trong đời sống, không
  phải âm thanh lạ). **C giữ 4.**

## Phán quyết điểm: GIỮ NGUYÊN 67 (H=4 R=3 F=3 P=3 C=4 A=4 L=2)

Tiết lộ một phần đúng format countdown; dải động rộng là đặc trưng của danh sách
âm thanh. **Cảnh báo bản quyền:** các âm thanh mẫu là meme audio lấy lại — L=2
đã tính; bản làm lại phải dùng âm thanh tự tạo hoặc SFX miễn phí thương mại.

---

# H04 — #66 — 61 điểm — KẾT LUẬN: GIỮ NGUYÊN 61

- **URL:** https://www.tiktok.com/@dylangg/video/7311950005701463338
- **Kênh / ngách / thời lượng:** @dylangg / humor / 62,93s, 1080x1920 hevc
- **Ngôn ngữ nói:** tiếng Anh · 79 từ/30s ≈ 158 từ/phút
- **Điểm gốc:** H=3 R=3 F=3 P=3 C=4 A=3 L=2 → 61

## 1. Hook (3s đầu)

- **Quan sát:** Frame 0/1/2s: chữ "what are culturally significant moments in
  history that you still think about regularly?" trên clip một cậu bé (chương
  trình "KIDS REACT", có dòng chú thích thống kê tội phạm thù ghét ở dưới —
  không liên quan đến câu hỏi). Transcript: lời thoại ngẫu nhiên, KHÔNG phải câu
  hỏi trên màn hình — "If someone was your friend and they turned out to be gay,
  would you still be their friend? - No, dad is not for you. - Walk pink. (bell
  rings) Oh my god, my god, my god, my god."
- **Suy luận:** Hook chỉ có chữ — giọng nói KHÔNG nói lại câu hỏi, không có hook
  kép. Câu hỏi thì hay (bắt người xem so sánh ký ức của mình), nhưng giọng nói
  là lời thoại rời rạc từ các clip, không củng cố hook. H=3 đã tính việc hook chỉ
  có chữ — bằng chứng mới không làm nó tệ hơn. **H giữ 3.**

## 2. Pacing

- **Quan sát:** Phép đo ghi 0 keyframe — là lỗi đo: sheet cho thấy clip đổi
  (cậu bé Kids React → trường quay game show → hai cô gái Disney → Justin Bieber
  phỏng vấn). Audio: độ lớn -23,37 LUFS (nhỏ), LRA 11,00; 3 khoảng lặng 0,5–0,9s
  ở 19,8–25,2s.
- **Suy luận:** Mỗi clip là một "khoảnh khắc văn hóa" — người xem ở lại vì nhận
  ra clip quen thuộc. Nhịp phụ thuộc vào độ nhận biết của từng clip, không đều.
  **R giữ 3.**

## 3. Audio

- **Quan sát:** Nhiều giọng nói khác nhau (lời thoại từ các clip gốc); độ lớn
  -23,37 LUFS (nhỏ). Các khoảng lặng ở 19,8–25,2s là ngắt giữa các clip.
- **Suy luận:** Audio là tập hợp lời thoại rời rạc, không có giọng dẫn thống
  nhất — đây là điểm yếu của format: không có ai "dẫn" người xem qua danh sách.
  Bản làm lại nên thêm giọng dẫn. **Nhạc/SFX: chưa đánh giá được.**

## 4. Cấu trúc câu chuyện

- **Quan sát (từ frame + transcript):** Câu hỏi mở ("khoảnh khắc văn hóa nào bạn
  vẫn nghĩ tới?") → chuỗi clip trả lời (Kids React → game show → Disney →
  Justin Bieber) → câu thoại cuối "In the end, you're gonna be the one on the
  floor and I'm gonna be the one who walks away. [laughter]".
- **Suy luận:** Cấu trúc hỏi → đáp bằng clip. Payoff là sự nhận ra ("à, mình nhớ
  cái này!"), không có cú twist. **P giữ 3.**

## 5. Cách làm lại không cần máy quay

- Video hỏi-đáp hoài niệm: một câu hỏi hoài niệm làm chữ lớn + hình AI/stock làm
  "câu trả lời" + giọng AI dẫn. Không dùng clip TV gốc. **F giữ 3.**

## 6. Chi phí sản xuất

- **Độ khó: dễ.** Thời gian làm lại ước tính 2–3 giờ (1 câu hỏi + 4–5 hình
  AI/stock + giọng). Công cụ: ảnh AI/stock + giọng AI + CapCut. Rủi ro lớn nhất:
  chọn sai "khoảnh khắc" — phải là thứ khán giả mục tiêu thật sự nhớ (với khán
  giả Việt: VTV, phim truyền hình cũ, quảng cáo xưa). **C giữ 4.**

## Phán quyết điểm: GIỮ NGUYÊN 61 (H=3 R=3 F=3 P=3 C=4 A=3 L=2)

Câu hỏi hoài niệm là hook chữ tốt; giọng không nói lại câu hỏi nhưng H=3 đã tính
điều đó. **Cảnh báo bản quyền:** toàn bộ clip là TV lấy lại (Disney, Access
Hollywood, Kids React) — L=2 đã tính; bản làm lại tuyệt đối không dùng clip gốc.

---

# H05 — #4 — 61 điểm — KẾT LUẬN: GIỮ NGUYÊN 61

- **URL:** https://www.youtube.com/shorts/O36oAfR4yE8
- **Kênh / ngách / thời lượng:** Bablucomedians / humor / 23,46s, 1080x1920 h264
- **Ngôn ngữ nói:** tiếng Hindi (Whisper nhận hi) — **transcript không dùng được**
- **Điểm gốc:** H=3 R=3 F=3 P=3 C=3 A=3 L=4 → 61

## 1. Hook (3s đầu)

- **Quan sát:** Frame 0/1/2s: nhãn "2010" + một người đàn ông cúi người với quả
  pháo hoa ban đêm, một bé gái ló đầu sau tường gạch. Không có chữ lớn. Transcript
  là ký tự rác lặp đi lặp lại ("ॠ ां ाीं ां ाीं…") — Whisper tự nhận Hindi nhưng
  không chuyển được lời nói thật, coi như **không có bằng chứng hook nói**.
  Audio: độ lớn -14,06 LUFS, **true peak +1,22 dBTP (clip — méo tiếng)**,
  không có khoảng lặng.
- **Suy luận:** Hook là hình ảnh đối lập (2010 vs 2026, cùng một bức tường, bé gái
  đã lớn thành thiếu nữ) — không có chữ lớn, không có bằng chứng giọng nói. H=3
  đã tính việc hook chỉ có hình; bằng chứng mới không làm nó tốt hơn hay tệ hơn.
  **H giữ 3.**

## 2. Pacing

- **Quan sát:** 12 keyframe đổi cảnh trong 23,46s (3,87 / 4,5 / 5,07 / 5,5 /
  7,87 / 8,57 / 9,13 / 10,27 / 13,77 / 19,13 / 20,33 / 20,93s) — cắt nhanh.
  Frame 50%: pháo hoa; frame 75%: nhãn "2026" đỏ, cô gái đã lớn ở cùng bức tường.
- **Suy luận:** 12 cắt trong 23s là nhanh — mỗi cắt là một nhịp nhỏ. Nhịp nhanh
  bù cho việc không có lời dẫn rõ. **R giữ 3.**

## 3. Audio

- **Quan sát:** True peak +1,22 dBTP — **âm thanh bị clip (vỡ tiếng)**, đây là
  lỗi kỹ thuật của bản gốc. Độ lớn -14,06 LUFS. Transcript rác — không biết có
  nhạc hay lời nói thật hay không, chỉ biết có âm thanh liên tục (không khoảng lặng).
- **Suy luận:** Không thể đánh giá nội dung âm thanh (transcript hỏng). Bản làm
  lại phải chuẩn hóa âm lượng và kiểm tra true peak ≤ -1 dBTP. **Nội dung audio:
  chưa đánh giá được (transcript hỏng).**

## 4. Cấu trúc câu chuyện

- **Quan sát (từ frame):** "2010" (bé gái + pháo) → pháo hoa → "2026" (cô gái
  đã lớn, cùng bức tường, cùng quả pháo).
- **Suy luận:** Cấu trúc "trước — sau": cùng một cảnh, 16 năm sau. Payoff là sự
  nhận ra (cô gái chính là bé gái ngày xưa). Đơn giản nhưng hiệu quả — cơ chế
  "thì ra là cùng một người/cùng một chỗ". **P giữ 3.**

## 5. Cách làm lại không cần máy quay

- "Trước — sau" bằng ảnh AI: cùng một bối cảnh, nhân vật trẻ → già (hoặc vật
  cũ → mới), 2–3 ảnh + chữ năm + nhạc. Không cần diễn viên. **F giữ 3** — dễ
  hơn sketch người thật, nhưng ảnh AI phải giữ được cùng bối cảnh (nhân vật AI
  khó giữ nhất quán qua 2 thời điểm).

## 6. Chi phí sản xuất

- **Độ khó: trung bình.** Thời gian làm lại ước tính 3–4 giờ (2–3 ảnh AI giữ
  nhất quán bối cảnh + nhạc). Công cụ: ảnh AI + CapCut. Rủi ro lớn nhất: nhân
  vật AI không giống nhau giữa 2 thời điểm (mất hiệu ứng "cùng một người").
  **C giữ 3.**

## Phán quyết điểm: GIỮ NGUYÊN 61 (H=3 R=3 F=3 P=3 C=3 A=3 L=4)

Hook là hình đối lập thì-quá khứ, không có bằng chứng hook nói (transcript Hindi
hỏng). Cắt nhanh 12 lần/23s xác nhận R=3. **Cảnh báo bản quyền:** video gốc là
người thật quay bằng máy — không có watermark, L=4 đã tính; bản làm lại dùng ảnh
AI của mình, không dùng lại hình người thật.

---

# H06 — #23 — 59 điểm — KẾT LUẬN: ĐIỀU CHỈNH 59 → 54 (H 3→2)

- **URL:** https://www.youtube.com/shorts/4Ix1k7Aou1c
- **Kênh / ngách / thời lượng:** unknown / humor / 26,09s, 1080x1920 h264
- **Ngôn ngữ nói:** tiếng Anh · 9 từ/30s ≈ 18 từ/phút (gần như không có lời)
- **Điểm gốc:** H=3 R=3 F=3 P=3 C=3 A=3 L=2 → 59
- **Điểm mới:** H=2 R=3 F=3 P=3 C=3 A=3 L=2 → **54**

## 1. Hook (3s đầu)

- **Quan sát:** Frame 0s: cận cảnh xe hơi bị nhòe (đang chuyển động nhanh), hộp
  chữ vàng "COMMENTS GOT ME 😂". Frame 1/2s: bàn tay đổ nước lên xe đồ chơi trong
  tuyết + hình nhỏ người dẫn (phụ nữ đội mũ cam) ở góc dưới-phải. Transcript chỉ
  có 9 từ: "Whoop, whoop, whoop…" — không có câu nói nào, chỉ có tiếng "whoop".
  Audio: **khoảng lặng 0–0,6s ngay đầu video (dead air)**; độ lớn -18,63 LUFS,
  LRA 22,90 (dải động rất rộng — tiếng whoop to, khoảng giữa nhỏ).
- **Suy luận:** Ba bằng chứng mới đều xấu cho hook: (1) frame 0s nhòe, không đọc
  được gì; (2) dead air 0,6s đầu; (3) **không có hook nói** — chỉ có tiếng whoop.
  Hook duy nhất là hộp chữ "COMMENTS GOT ME 😂" + hình xe đồ chơi — yếu hơn điểm
  H=3 đã chấm (lúc chấm chỉ nhìn frame 1s, chưa biết không có giọng và có dead
  air). **H 3→2.**

## 2. Pacing

- **Quan sát:** Phép đo ghi 4 keyframe (6,8 / 7,2 / 17,2 / 18,13s). Frame 25%:
  phòng khách; 50%: phụ nữ đồ ngủ + người đàn ông; 75%: thẻ bình luận
  "becky_vibes07: He stood there holding a toy car like a clown while she
  absolutely soaked his shorts" + người đàn ông giơ ngón cái. Các khoảng lặng ở
  22,16 / 23,2 / 24,03s.
- **Suy luận:** Cấu trúc: clip (xe đồ chơi bị dội nước) → phản ứng → đọc bình
  luận hay nhất. Nhịp chậm, phụ thuộc vào bình luận. **R giữ 3.**

## 3. Audio

- **Quan sát:** Gần như không có lời (9 từ/30s); âm thanh chính là tiếng whoop +
  khoảng lặng. Độ lớn -18,63 LUFS, LRA 22,90.
- **Suy luận:** Video này gần như câm — hiệu quả hoàn toàn dựa vào hình + chữ.
  Bản làm lại cần thêm giọng (đọc bình luận) để bù. **Nhạc/SFX: chưa đánh giá
  được.**

## 4. Cấu trúc câu chuyện

- **Quan sát (từ frame + transcript):** Clip gốc (xe đồ chơi bị dội nước tuyết)
  → phản ứng của cặp đôi → bình luận hay nhất được đọc/hiện ("holding a toy car
  like a clown while she absolutely soaked his shorts") → ngón cái.
- **Suy luận:** Cơ chế "clip + bình luận hay nhất": bình luận là punchline.
  Payoff là bình luận của becky_vibes07. **P giữ 3.**

## 5. Cách làm lại không cần máy quay

- "Clip + bình luận hay nhất": clip stock/AI ngắn + thẻ bình luận (tự viết hoặc
  lấy bình luận thật có xin phép) + giọng AI đọc bình luận. Không cần người thật.
  **F giữ 3.**

## 6. Chi phí sản xuất

- **Độ khó: dễ.** Thời gian làm lại ước tính 2–3 giờ (1 clip + 1 thẻ bình luận
  + giọng). Công cụ: clip stock/AI + giọng AI + CapCut. Rủi ro lớn nhất: bình
  luận phải thật sự hài — bình luận dở là hỏng video. **C giữ 3.**

## Phán quyết điểm: ĐIỀU CHỈNH 59 → 54 (H 3→2)

Bằng chứng mới: không có hook nói (chỉ có tiếng whoop) + dead air 0,6s đầu +
frame 0s nhòe. Hook thực tế chỉ còn hộp chữ "COMMENTS GOT ME 😂". **Cảnh báo bản
quyền:** clip gốc là video người thật + hình người dẫn overlay + bình luận của
tài khoản becky_vibes07 — L=2 đã tính; bản làm lại dùng clip của mình và bình
luận tự viết.

---

# H07 — #52 — 54 điểm — KẾT LUẬN: GIỮ NGUYÊN 54

- **URL:** https://www.tiktok.com/@duchu_tz/video/7697269939761057057
- **Kênh / ngách / thời lượng:** @duchu_tz / humor / 60,36s, 1080x1920 h264
- **Ngôn ngữ nói:** không có lời nói thật (transcript là ảo giác của Whisper)
- **Điểm gốc:** H=2 R=4 F=2 P=3 C=2 A=3 L=4 → 54

## 1. Hook (3s đầu)

- **Quan sát:** Frame 0/1/2s: một người đàn ông mặc đồng phục đi về phía camera
  ngoài trời, **không có chữ nào**. Transcript: "*Sounds of a dead man*" lặp 14
  lần + "shot." — đây là ảo giác của Whisper trên tiếng hiệu ứng, không phải lời
  nói thật. Audio: 1 khoảng lặng ở 7,29s; độ lớn -16,76 LUFS, **true peak +0,61
  dBTP (clip nhẹ)**.
- **Suy luận:** Không có chữ, không có lời nói — hook duy nhất là hình người đàn
  ông đồng phục đi tới (người xem tự hỏi "anh ta là ai, sắp làm gì?"). H=2 đã
  tính việc này. **H giữ 2.**

## 2. Pacing

- **Quan sát:** 7 keyframe (15,83 / 25,83 / 26,77 / 33,83 / 38,77 / 40,03 /
  40,13s). Frame 25%: người áo đỏ tát người đồng phục; 50%: võ sĩ áo trắng đối
  mặt; 75%: võ sĩ đá ngã khỏi cây, nằm dưới đất (thua).
- **Suy luận:** Chuỗi leo thang slapstick: đi tới → bị tát → võ sĩ xuất hiện →
  võ sĩ thua. Mỗi nhịp là một bất ngờ nhỏ. **R giữ 4.**

## 3. Audio

- **Quan sát:** Không có lời nói thật (transcript là ảo giác); âm thanh là
  nhạc/SFX. Độ lớn -16,76 LUFS (gần chuẩn), true peak +0,61 dBTP (clip nhẹ).
- **Suy luận:** Video này là slapstick câm — hiệu quả dựa vào hình + tiếng hiệu
  ứng. Không đánh giá được nhạc/SFX cụ thể vì không nghe. **Nội dung audio: chưa
  đánh giá được (không có transcript thật).**

## 4. Cấu trúc câu chuyện

- **Quan sát (từ frame):** Người đồng phục đi tới → bị tát → võ sĩ xuất hiện
  (tưởng là cứu tinh) → võ sĩ bị đá ngã, nằm dưới đất.
- **Suy luận:** Cấu trúc "kỳ vọng — đảo ngược": võ sĩ xuất hiện tưởng thắng, hóa
  ra thua. Payoff là cú ngã cuối. **P giữ 3.**

## 5. Cách làm lại không cần máy quay

- Slapstick người que: 3 nhân vật que (đồng phục, áo đỏ, võ sĩ), cùng chuỗi
  leo thang — đi tới → tát → võ sĩ → ngã. Không cần diễn viên. **F giữ 2** —
  khó hơn các format khác vì slapstick cần timing hình ảnh chính xác (cú tát,
  cú đá phải đúng nhịp), người que khó diễn đạt bằng ảnh tĩnh.

## 6. Chi phí sản xuất

- **Độ khó: trung bình-khó.** Thời gian làm lại ước tính 4–6 giờ (vẽ/animate 3
  nhân vật que + timing cú đánh). Công cụ: Manim/Remotion hoặc Pivot Animator +
  SFX. Rủi ro lớn nhất: timing — slapstick sai nhịp 0,2s là mất cười.
  **C giữ 2.**

## Phán quyết điểm: GIỮ NGUYÊN 54 (H=2 R=4 F=2 P=3 C=2 A=3 L=4)

Không có chữ, không có lời nói — H=2 đã tính đúng. Cú đảo ngược võ sĩ thua là
payoff tốt. Không có watermark/bản quyền rõ ràng trên frame; L=4.

---

# H08 — #22 — 54 điểm — KẾT LUẬN: GIỮ NGUYÊN 54

- **URL:** https://www.youtube.com/shorts/lcTsAQ8qf_g
- **Kênh / ngách / thời lượng:** unknown / humor / 46,80s, 1080x1920 h264
- **Ngôn ngữ nói:** tiếng Hindi (Whisper nhận hi) — **transcript không dùng được**
- **Điểm gốc:** H=2 R=4 F=2 P=3 C=2 A=3 L=4 → 54

## 1. Hook (3s đầu)

- **Quan sát:** Frame 0/1/2s: một thanh niên áo trắng đi về phía camera trong
  làng, **không có chữ nào**. Transcript là từ Hindi "बाहीं" lặp đi lặp lại —
  Whisper vòng lặp, không phải lời nói thật. Audio: độ lớn -13,43 LUFS (to),
  **true peak +0,29 dBTP (clip nhẹ)**, không có khoảng lặng.
- **Suy luận:** Không có chữ, không có bằng chứng lời nói — hook duy nhất là
  hình người đi tới + bối cảnh làng. H=2 đã tính đúng. **H giữ 2.**

## 2. Pacing

- **Quan sát:** 19 keyframe trong 46,8s — cắt rất nhanh. Frame 25%: người đàn
  ông đi xa + cận mặt người áo xanh lá (mặt phản ứng); 50%: người đàn ông từ sau
  chỉ tay lên trời + cận mặt người áo đen "GANT" làm mặt.
- **Suy luận:** Cắt nhanh + mặt phản ứng liên tục — đúng format sketch đối thoại
  nhanh. Nhịp nhanh là điểm mạnh nhất của video. **R giữ 4.**

## 3. Audio

- **Quan sát:** Độ lớn -13,43 LUFS (to nhất nhóm Hài sau H01), true peak +0,29
  dBTP (clip nhẹ). Transcript hỏng — không biết nội dung lời thoại.
- **Suy luận:** Không đánh giá được nội dung lời thoại (transcript Hindi hỏng).
  Bản làm lại cần chuẩn hóa âm lượng (bản gốc hơi to và clip nhẹ). **Nội dung
  audio: chưa đánh giá được (transcript hỏng).**

## 4. Cấu trúc câu chuyện

- **Quan sát (từ frame):** Người đàn ông đi tới → đi xa → mặt phản ứng → chỉ
  tay lên trời → mặt phản ứng khác. Không đọc được câu chuyện cụ thể từ frame
  (không có chữ, không có transcript).
- **Suy luận:** Đây là sketch đối thoại nhanh bằng tiếng Hindi — cấu trúc cụ thể
  không xác định được từ dữ liệu có. Payoff có lẽ là câu thoại cuối (không biết
  là gì). **P giữ 3** — không có bằng chứng để tăng hay giảm, giữ điểm gốc.

## 5. Cách làm lại không cần máy quay

- Sketch đối thoại nhanh bằng người que: 2 nhân vật que, cắt nhanh, mặt phản ứng
  phóng đại. Cần kịch bản thoại Việt ngắn, nhanh, hài. **F giữ 2** — khó vì hài
  nằm ở lời thoại và diễn xuất, người que khó truyền đạt bằng ảnh tĩnh.

## 6. Chi phí sản xuất

- **Độ khó: trung bình-khó.** Thời gian làm lại ước tính 4–6 giờ (kịch bản thoại
  + animate người que + giọng). Công cụ: Manim/Remotion + giọng AI. Rủi ro lớn
  nhất: thoại không hài bằng bản gốc (hài đối thoại là khó nhất để viết lại).
  **C giữ 2.**

## Phán quyết điểm: GIỮ NGUYÊN 54 (H=2 R=4 F=2 P=3 C=2 A=3 L=4)

Không có chữ, không có bằng chứng lời nói — H=2 đã tính đúng. Cắt nhanh 19
lần/46,8s xác nhận R=4. **Hạn chế:** cấu trúc câu chuyện không xác định được
(transcript Hindi hỏng, không có chữ trên frame) — đây là video có bằng chứng
yếu nhất trong 25 video. Không có watermark; L=4.

---

# T04 — #84 — 80 điểm — KẾT LUẬN: GIỮ NGUYÊN 80

- **URL:** https://www.youtube.com/shorts/9lPFW5CeaNI
- **Kênh / ngách / thời lượng:** unknown / curiosity / 10,09s, 1080x1920 h264
- **Ngôn ngữ nói:** tiếng Anh · 44 từ/30s ≈ 88 từ/phút (nói hết trong 10s → ~264 từ/phút thực tế)
- **Điểm gốc:** H=4 R=3 F=5 P=3 C=5 A=4 L=5 → 80

## 1. Hook (3s đầu)

- **Quan sát:** Frame 0s: gần như đen (mở đầu mờ dần từ đen), chữ "FACTS?!" vàng
  + con mèo xám mờ. Frame 1/2s: mèo AI mặc smoking, chữ "Did you know these
  amazing animal facts? ✨". Transcript: "Did you know these amazing animal facts?
  Ants actually farm fungi to feast has three hearts. Grasshoppers make music by
  rubbing their legs on. And flying fish can leap up to 200 metres." Audio:
  **khoảng lặng 0–0,67s đầu (dead air)**; độ lớn -22,92 LUFS (nhỏ), LRA 2,30
  (dải động rất hẹp — giọng nén mạnh).
- **Suy luận:** Hook nói trùng đúng câu hỏi trên màn hình — **hook kép**
  (chữ + giọng cùng hỏi "Did you know…?"). Điểm trừ nhỏ: frame 0s tối (fade-in
  từ đen) + dead air 0,67s đầu. Nhưng từ 1s trở đi mèo + câu hỏi đã rõ — H=4 đã
  tính được mức này. **H giữ 4.**

## 2. Pacing

- **Quan sát:** Phép đo ghi 0 keyframe — đúng ở đây: một ảnh mèo tĩnh, miệng mèo
  cử động (AI talking cat), các icon nhỏ (châu chấu, cá bay, bạch tuộc) bay quanh.
  Frame 25%: "Ants actually farm fungi to feed themselves. 🍄"; 50%: "And an
  octopus has three hearts. ❤️" + nút FOLLOW; 75%: "Grasshoppers make music by
  rubbing their legs on wings. 🎵". Tổng thời lượng chỉ **10,09s** — ngắn nhất
  trong 30 video.
- **Suy luận:** 4 sự thật trong 10s — nhịp rất nhanh (mỗi sự thật ~2,5s). Nhưng
  10s là quá ngắn so với cửa sổ 38–65s; bản làm lại phải kéo dài (thêm sự thật).
  Hình mèo tĩnh + chữ đổi là đủ cho format này. **R giữ 3.**

## 3. Audio

- **Quan sát:** Giọng Anh đọc sự thật, liên tục trong 10s; độ lớn -22,92 LUFS
  (nhỏ), LRA 2,30 (nén mạnh — giọng đều một mức). Không có bằng chứng nhạc/SFX.
- **Suy luận:** Giọng đọc nhanh, đều — phù hợp format sự thật nhanh. Cần tăng
  âm lượng khi làm lại (-22,92 là nhỏ). **Nhạc/SFX: chưa đánh giá được.**

## 4. Cấu trúc câu chuyện

- **Quan sát (từ frame + transcript):** Câu hỏi mở ("Did you know…?") → sự thật
  1 kiến trồng nấm → sự thật 2 bạch tuộc 3 tim → sự thật 3 châu chấu làm nhạc →
  sự thật 4 cá bay nhảy 200m → (hết video, không có kết).
- **Suy luận:** Cấu trúc danh sách sự thật — không có payoff riêng, chính các sự
  thật là payoff. **P giữ 3.**

## 5. Cách làm lại không cần máy quay

- "Mèo nói sự thật": 1 nhân vật AI cố định (mèo mặc smoking, hoặc nhân vật khác
  — chó, cú, robot) + danh sách 8–10 sự thật + giọng AI đọc. Đây là format dễ
  nhất trong 30 video: một ảnh + chữ + giọng. **F giữ 5.**

## 6. Chi phí sản xuất

- **Độ khó: dễ nhất.** Thời gian làm lại ước tính 1–2 giờ (1 ảnh AI + 8–10 sự
  thật đã viết + giọng). Công cụ: ảnh AI + giọng AI + CapCut. Rủi ro lớn nhất:
  nhân vật AI phải đủ duyên (mèo này duyên vì mặc smoking + mắt to); sự thật
  phải thật sự lạ (sự thật thường thì không ai xem). **C giữ 5.**

## Phán quyết điểm: GIỮ NGUYÊN 80 (H=4 R=3 F=5 P=3 C=5 A=4 L=5)

Hook kép xác nhận (giọng nói đúng câu hỏi trên màn hình); dead air 0,67s + frame
0s tối là điểm trừ nhỏ đã tính trong H=4. Không có watermark; L=5. **Lưu ý:** 10s
quá ngắn — bản làm lại phải kéo dài lên 40–45s (thêm sự thật), không sao chép
nguyên 10s.

---

# T05 — #82 — 78 điểm — KẾT LUẬN: GIỮ NGUYÊN 78

- **URL:** https://www.youtube.com/shorts/43xG97eD-j0
- **Kênh / ngách / thời lượng:** Compound Curiosity / curiosity / 175,54s, 720x1280 h264
- **Ngôn ngữ nói:** tiếng Anh · 66 từ/30s ≈ 132 từ/phút
- **Điểm gốc:** H=4 R=3 F=5 P=4 C=3 A=4 L=4 → 78

## 1. Hook (3s đầu)

- **Quan sát:** Frame 0s: đám đông ban đêm, đèn mờ, không có chữ. Frame 1s: chữ
  lớn "THE WORLD DIDN'T END TODAY". Frame 2s: thêm dòng "Feed said the world
  ends today — Fri, Nov 13, 2026? Here is the fact-check." Transcript: "If your
  feed told you the world ends today, Friday, November 13th, 2026, here's the
  fact check. The claim is real enough to fool people. A paper in Science, 1960,
  really is titled Doomsday, Friday, 13 November, AD, 2026." Audio: **khoảng
  lặng 0–0,69s đầu (dead air)**; độ lớn **-31,77 LUFS (rất nhỏ)**, true peak
  -10,01 dBTP; thêm 1 khoảng lặng ở 7,66s.
- **Suy luận:** Hook nói trùng đúng tiêu đề trên màn hình — **hook kép** (giọng
  nói đúng câu "the world ends today"). Điểm trừ: dead air 0,69s + âm thanh rất
  nhỏ (-31,77 LUFS — gần như không nghe được trên loa điện thoại). Nhưng hook
  chữ đủ mạnh để người xem tắt tiếng vẫn hiểu — H=4 đã tính được mức này.
  **H giữ 4.**

## 2. Pacing

- **Quan sát:** 14 keyframe trong 175,54s (19,13 / 38,27 / 54,4 / 61,2 / 80,07 /
  96,4 / 114,67 / 124,67 / 140,33 / 156,67 / 162,13 / 169,73 / 170,13 /
  170,4s) — trung bình một beat mỗi ~15–19s. Frame 25%: Trái Đất từ không gian,
  "Von Foerster said he did not believe humanity would breed itself to
  infinity."; 50%: phố Tokyo ban đêm, "Reality (U.S. Census): ~8.2 billion
  people. Off by 10x — gap still grows. MODEL: 100s OF BILLIONS / REALITY: 8.2
  BILLION"; 75%: tòa nhà LHQ, "The real lesson: extrapolate past the behavior
  driving it — math will confidently lie."
- **Suy luận:** 175s là dài nhất trong 30 video — quá dài cho Shorts. Nhịp một
  beat/15–19s là chậm cho Shorts nhưng phù hợp video essay dài. Bản làm lại phải
  cắt xuống ~50s (chỉ giữ 3 beat: lời đồn → bài báo 1960 → số liệu thật).
  **R giữ 3.**

## 3. Audio

- **Quan sát:** Giọng Anh kể chuyện, liên tục; độ lớn **-31,77 LUFS — rất nhỏ**,
  true peak -10,01 dBTP. 2 khoảng lặng (0,69s đầu + 0,76s ở 7,66s).
- **Suy luận:** Âm thanh quá nhỏ là lỗi kỹ thuật nghiêm trọng của bản gốc — người
  xem trên loa ngoài gần như không nghe được. Bản làm lại bắt buộc chuẩn hóa về
  ~-16 LUFS. **Nhạc/SFX: chưa đánh giá được.**

## 4. Cấu trúc câu chuyện

- **Quan sát (từ frame + transcript):** Tin đồn ("thế giới tận thế hôm nay") →
  nguồn gốc thật (bài báo Science 1960, tiêu đề "Doomsday, Friday, 13 November,
  AD, 2026") → số liệu thật (8,2 tỉ người, không phải hàng trăm tỉ) → bài học
  ("ngoại suy quá đà thì toán cũng nói dối").
- **Suy luận:** Đây là **Visual Essay chuẩn**: câu hỏi gây sốc → 2–3 beat dữ
  liệu → lật lại nhận thức → bài học. Payoff là câu cuối ("math will confidently
  lie") — một câu đáng nhớ, đáng chia sẻ. **P giữ 4.**

## 5. Cách làm lại không cần máy quay

- Visual Essay: ảnh AI/stock + biểu đồ + chữ lớn + giọng AI. Không cần quay.
  Cắt 175s xuống ~50s: giữ 3 beat (lời đồn → nguồn gốc → số liệu thật + bài
  học). **F giữ 5.**

## 6. Chi phí sản xuất

- **Độ khó: trung bình.** Thời gian làm lại ước tính 4–6 giờ (kịch bản 50s +
  5–6 hình/biểu đồ + giọng). Công cụ: ảnh AI + biểu đồ tự vẽ + giọng AI +
  CapCut. Rủi ro lớn nhất: rút gọn 175s xuống 50s mà không mất logic (dễ cắt
  nhầm beat quan trọng); và số liệu phải kiểm chứng (không được bịa số).
  **C giữ 3.**

## Phán quyết điểm: GIỮ NGUYÊN 78 (H=4 R=3 F=5 P=4 C=3 A=4 L=4)

Hook kép xác nhận (giọng nói đúng tiêu đề). Dead air + âm thanh rất nhỏ là lỗi
kỹ thuật, không phải lỗi hook — bản làm lại sửa bằng cách chuẩn hóa âm lượng.
Không có watermark; L=4 (dữ liệu lấy từ bài báo Science 1960 và U.S. Census —
cần ghi nguồn khi làm lại).

---

# T06 — #83 — 76 điểm — KẾT LUẬN: GIỮ NGUYÊN 76

- **URL:** https://www.youtube.com/shorts/vVX-t7rAo4w
- **Kênh / ngách / thời lượng:** unknown / curiosity / 60,09s, 1080x1920 h264
- **Ngôn ngữ nói:** tiếng Pháp · 106 từ/30s ≈ 212 từ/phút (nói nhanh)
- **Điểm gốc:** H=3 R=4 F=5 P=3 C=4 A=4 L=4 → 76

## 1. Hook (3s đầu)

- **Quan sát:** Frame 0s: Trái Đất từ không gian, Canada phủ cờ, chú thích "le
  Canada". Frame 1/2s: Canada viền đỏ phát sáng + chấm hồ, chữ "le Canada" rồi
  "très grand". Không có chữ lớn. Transcript (tiếng Pháp): "Le Canada, c'est
  grand, très grand, mais ce n'est pas ça qui rentre ce pays unique, c'est ce
  qui se cache à l'intérieur. Le Canada possède plus de la moitié des lacs du
  monde entier, 60% exactement, plus de 31 000 lacs de plus de trois kilomètres
  carrés…"
- **Suy luận:** Hook nói tốt (nước lớn — nhưng điều đặc biệt là thứ ẩn bên trong
  → hứa hẹn bí mật), nhưng **hook hình yếu**: chỉ có bản đồ + chữ nhỏ "le
  Canada", không có chữ lớn gây tò mò. Người xem tắt tiếng chỉ thấy bản đồ Canada
  — không đủ giữ. H=3 đã tính đúng. **H giữ 3.**

## 2. Pacing

- **Quan sát:** Phép đo ghi 4 keyframe — tất cả ở 0,0 / 0,1 / 1,0 / 2,0s (chỉ
  có frame hook, không có cắt cứng sau 2s). Sheet cho thấy bản đồ **biến hình từ
  từ** (zoom/morph, không cắt): Trái Đất → Canada viền đỏ → Trái Đất phủ cờ →
  ảnh vệ tinh hồ. Frame 50%: "Dernière ère glaciaire - 10 000 ans" + thanh tiến
  trình; 75%: ảnh vệ tinh hồ, "60% de tous les lacs du monde". Audio: 106 từ/30s
  = 212 từ/phút (nói nhanh); không có khoảng lặng; độ lớn -18,22 LUFS.
- **Suy luận:** Nhịp nằm ở giọng nói nhanh + bản đồ biến hình chậm — hai nhịp
  đối lập bù nhau (giọng nhanh giữ người xem, hình chậm cho mắt nghỉ). 212
  từ/phút là nhanh (vùng an toàn 150–165), nhưng tiếng Pháp nói nhanh là bình
  thường; bản Việt nên chậm lại ~160 từ/phút. **R giữ 4.**

## 3. Audio

- **Quan sát:** Giọng Pháp liên tục, nhanh (212 từ/phút), không khoảng lặng;
  độ lớn -18,22 LUFS.
- **Suy luận:** Giọng là xương sống — bản làm lại cần giọng đọc nhanh vừa phải,
  không được đọc chậm (sẽ buồn ngủ vì hình biến hình chậm). **Nhạc/SFX: chưa
  đánh giá được.**

## 4. Cấu trúc câu chuyện

- **Quan sát (từ frame + transcript):** Câu hỏi ngầm (Canada lớn — nhưng có gì
  đặc biệt?) → dữ kiện 1 (60% hồ thế giới) → dữ kiện 2 (31.000 hồ lớn hơn
  3 km²) → nguyên nhân (kỷ băng hà 10.000 năm trước).
- **Suy luận:** Visual Essay mini: một câu hỏi → 2–3 dữ kiện → nguyên nhân.
  Payoff là con số 60% — một con số đáng nhớ. **P giữ 3.**

## 5. Cách làm lại không cần máy quay

- Visual Essay bản đồ: ảnh vệ tinh/bản đồ (Openverse/Wikimedia — miễn phí
  thương mại) + chữ lớn + giọng AI. Không cần quay. **F giữ 5.**

## 6. Chi phí sản xuất

- **Độ khó: dễ.** Thời gian làm lại ước tính 2–3 giờ (3–4 hình bản đồ + chữ +
  giọng). Công cụ: ảnh bản đồ miễn phí + giọng AI + CapCut. Rủi ro lớn nhất:
  tìm đúng ảnh bản đồ/vệ tinh đẹp và đúng dữ liệu (số liệu phải kiểm chứng).
  **C giữ 4.**

## Phán quyết điểm: GIỮ NGUYÊN 76 (H=3 R=4 F=5 P=3 C=4 A=4 L=4)

Hook nói tốt nhưng hook hình yếu (không có chữ lớn) — H=3 đúng. Nhịp giọng nhanh
+ bản đồ biến hình là cơ chế giữ người xem. Không có watermark; L=4 (số liệu về
hồ Canada cần kiểm chứng khi làm lại).

---

# T07 — #99 — 74 điểm — KẾT LUẬN: GIỮ NGUYÊN 74

- **URL:** https://www.tiktok.com/@lateese.miller/video/7706316280051059998
- **Kênh / ngách / thời lượng:** LaTeese M. / curiosity / 60,37s, 1080x1920 hevc
- **Ngôn ngữ nói:** tiếng Anh · 95 từ/30s ≈ 190 từ/phút
- **Điểm gốc:** H=4 R=4 F=3 P=4 C=3 A=4 L=4 → 74

## 1. Hook (3s đầu)

- **Quan sát:** Frame 0/1s: phụ nữ ngồi trước laptop, chữ "Don't Get a Part Time
  Job!!" + "600". Frame 2s: "600x7 = 4,200", "600x30 = 18,000 every month.
  Don't get a part time job." Transcript: "Every day, every week, every month.
  Don't get a part-time job, do this instead. The YouTube found a kids show,
  preferably one with a lot of views. Look at all these views, and all of these
  were made with AI."
- **Suy luận:** Hook nói trùng đúng chữ trên màn hình — **hook kép** (giọng nói
  "Don't get a part-time job, do this instead" đúng lúc chữ hiện). Thêm con số
  cụ thể (600 → 4.200 → 18.000) — số tiền là móc câu. **H giữ 4.**

## 2. Pacing

- **Quan sát:** 7 keyframe (4,4 / 9,6 / 14,0 / 16,67 / 21,87 / 39,4 / 44,27s).
  Frame 25%: màn hình YouTube video học cho bé, "Look at all these views. And
  all of these were made with AI."; 50%: màn hình swagga.ai, "Go to swagga.ai
  and then to the chat tab"; 75%: "Paste in the transcript. Make sure it's C
  dance or clean". Audio: 4 khoảng lặng ở 2,36 / 6,52 / 15,74 / 19,49s.
- **Suy luận:** Nhịp là chuỗi bước hướng dẫn (tìm video → xem lượt xem → chép
  transcript → dán vào AI). Mỗi bước là một màn hình mới. Các khoảng lặng là ngắt
  giữa các bước. **R giữ 4.**

## 3. Audio

- **Quan sát:** Giọng Anh nhanh (190 từ/phút), liên tục; độ lớn **-36,72 LUFS
  (cực kỳ nhỏ)**, true peak -20,47 dBTP. 4 khoảng lặng 0,5–1s.
- **Suy luận:** Âm thanh cực kỳ nhỏ là lỗi kỹ thuật nghiêm trọng của bản gốc —
  gần như không nghe được trên loa ngoài. Nhưng hook chữ + số tiền đủ mạnh để
  người xem tắt tiếng vẫn hiểu. Bản làm lại bắt buộc chuẩn hóa về ~-16 LUFS.
  **Nhạc/SFX: chưa đánh giá được.**

## 4. Cấu trúc câu chuyện

- **Quan sát (từ frame + transcript):** Tuyên bố ngược đời ("Đừng làm thêm!") +
  con số (600/ngày → 18.000/tháng) → bằng chứng (video học cho bé có nhiều lượt
  xem, đều làm bằng AI) → cách làm (tìm video viral → chép transcript → dán vào
  swagga.ai để tạo prompt tương tự).
- **Suy luận:** Cấu trúc "tuyên bố ngược đời → bằng chứng → hướng dẫn": người
  xem ở lại vì muốn biết "làm thế nào". Payoff là bước hướng dẫn cuối (dán
  transcript vào AI). **P giữ 4.**

## 5. Cách làm lại không cần máy quay

- Hướng dẫn màn hình: chỉ quay màn hình (không cần facecam — **bỏ người phụ nữ
  trong video gốc**), chữ lớn + số tiền + giọng AI. **F giữ 3** — cần quay màn
  hình thật (không phải quay người), vẫn làm được không cần máy quay, nhưng khó
  hơn ảnh AI vì cần màn hình thật + tài khoản công cụ.

## 6. Chi phí sản xuất

- **Độ khó: trung bình.** Thời gian làm lại ước tính 3–4 giờ (quay màn hình 3–4
  bước + chữ + giọng). Công cụ: quay màn hình + giọng AI + CapCut. Rủi ro lớn
  nhất: nội dung "kiếm tiền bằng AI" dễ bị coi là lừa đảo nếu không có bằng
  chứng thật — bản làm lại phải dùng số liệu thật của chính mình, không hứa
  hẹn thu nhập.
  **C giữ 3.**

## Phán quyết điểm: GIỮ NGUYÊN 74 (H=4 R=4 F=3 P=4 C=3 A=4 L=4)

Hook kép xác nhận (giọng nói đúng chữ "Don't get a part time job") + con số cụ
thể. Âm thanh cực kỳ nhỏ là lỗi kỹ thuật, không phải lỗi hook. **Cảnh báo bản
quyền:** video gốc quay màn hình YouTube (video học cho bé của người khác) và
giao diện swagga.ai — bản làm lại chỉ dùng màn hình của chính mình, không quay
lại nội dung người khác. L=4 đã tính.

---

# B01 — #8 — 76 điểm — KẾT LUẬN: GIỮ NGUYÊN 76

- **URL:** https://www.youtube.com/shorts/mjpiKDOczh4
- **Kênh / ngách / thời lượng:** unknown / surprise / 67,57s, 1080x1920 h264
- **Ngôn ngữ nói:** tiếng Anh · 43 từ/30s ≈ 86 từ/phút
- **Điểm gốc:** H=3 R=4 F=5 P=3 C=4 A=4 L=4 → 76

## 1. Hook (3s đầu)

- **Quan sát:** Frame 0/1s: một thanh niên tóc xanh trong hành lang, quả bóng bay
  đỏ khổng lồ che mặt anh ta. Frame 2s: bóng bay buộc vào tay anh ta. Góc
  dưới-phải frame 1s có watermark chữ Trung "豆包AI生成" (Doubao AI-generated —
  nhãn video do AI tạo). Transcript: tiếng gõ cửa + "Who's there?" + đối thoại —
  "What? What's with the balloon? I didn't touch that door. Bro, you can't hide
  that! … I knocked on the door. It only reacts to you." Audio: **khoảng lặng
  0–1,14s đầu (dead air hơn 1 giây)**; độ lớn **-12,09 LUFS (to nhất trong 25
  video)**, true peak -0,17 dBTP.
- **Suy luận:** Hook là hình ảnh phi lý (bóng bay khổng lồ) + tiếng gõ cửa. Dead
  air 1,14s đầu là lỗi — người xem vào video nghe im lặng hơn 1s trước tiếng gõ.
  Nhưng hình bóng bay đủ mạnh để giữ người xem qua 1s im lặng đó. H=3 đã tính
  việc không có chữ lớn. **H giữ 3.**

## 2. Pacing

- **Quan sát:** Phép đo ghi 4 keyframe (0,0 / 1,0 / 2,0 / 60,17s) — video gần như
  một cảnh hành lang liên tục, bóng bay trôi theo người. Frame 25%: hai người
  khác đi tới, bóng bay lơ lửng; 50%: bóng bay phồng to gần cửa, cả nhóm cười;
  75%: người tóc xanh cầm dây bóng, bạn bè chỉ tay cười.
- **Suy luận:** Nhịp là sự leo thang của trò đùa: bóng bay → bóng bay phản ứng
  với người → bóng bay to dần → cả nhóm phát hiện. Một cảnh duy nhất nhưng có
  leo thang. **R giữ 4.**

## 3. Audio

- **Quan sát:** Đối thoại tiếng Anh + tiếng gõ cửa (SFX gõ cửa là nhịp đầu
  tiên); độ lớn -12,09 LUFS (to); chỉ 1 khoảng lặng (1,14s đầu).
- **Suy luận:** Tiếng gõ cửa là SFX mở đầu — đúng nguyên tắc "âm thanh vào từ
  0,1s" (trừ dead air 1,14s). Bản làm lại: gõ cửa ngay từ 0,1s, không để im lặng.
  **Nhạc nền: chưa đánh giá được.**

## 4. Cấu trúc câu chuyện

- **Quan sát (từ frame + transcript):** Bóng bay bí ẩn xuất hiện → gõ cửa →
  bóng bay chỉ phản ứng với một người → cả nhóm phát hiện → cười.
- **Suy luận:** Cấu trúc "vật thể phi lý + quy tắc bí ẩn" (bóng bay chỉ phản ứng
  với bạn) — người xem ở lại để biết quy tắc là gì. Payoff là lúc cả nhóm phát
  hiện. **P giữ 3.**

## 5. Cách làm lại không cần máy quay

- Video AI: dùng Veo/Kling tạo cảnh hành lang + bóng bay đỏ khổng lồ + giọng AI
  (đối thoại gõ cửa). Video gốc vốn đã là AI (nhãn Doubao) — format này sinh ra
  cho AI video. **F giữ 5.**

## 6. Chi phí sản xuất

- **Độ khó: trung bình.** Thời gian làm lại ước tính 3–5 giờ (prompt AI video
  3–4 cảnh + giọng). Công cụ: Veo/Kling/Wan 2.2 + giọng AI + CapCut. Rủi ro lớn
  nhất: AI video khó giữ nhân vật/bóng bay nhất quán qua các cảnh (bóng bay đổi
  hình là hỏng); cần thử nhiều lần.
  **C giữ 4.**

## Phán quyết điểm: GIỮ NGUYÊN 76 (H=3 R=4 F=5 P=3 C=4 A=4 L=4)

Bóng bay khổng lồ là hook hình mạnh; dead air 1,14s là lỗi nhưng không phá được
hook. **Lưu ý nhãn AI:** watermark "豆包AI生成" là nhãn "do AI tạo" (Doubao),
không phải bản quyền — bản làm lại nên tự gắn nhãn AI tương tự. L=4.

---

# B02 — #10 — 67 điểm — KẾT LUẬN: GIỮ NGUYÊN 67

- **URL:** https://www.youtube.com/shorts/4yCLm_7abDY
- **Kênh / ngách / thời lượng:** unknown / surprise / 32,15s, 720x1280 h264
- **Ngôn ngữ nói:** tiếng Anh · 57 từ/30s ≈ 114 từ/phút
- **Điểm gốc:** H=3 R=4 F=3 P=4 C=3 A=3 L=3 → 67

## 1. Hook (3s đầu)

- **Quan sát:** Frame 0s: cận mặt người đàn ông trong xe, chữ "WHAT SHOULD I
  TELL YOU". Frame 1/2s: thẻ tiêu đề "A DATE, A DEALERSHIP, AND A SPENDING
  TEST" trên hình xe. Transcript: giọng nữ kể chuyện — "I think someone likes to
  go out to expensive restaurants like he take care of the bill… Let me go
  shopping after that… I deserve to be spoiled. Why not?" Audio: độ lớn
  **-36,95 LUFS (cực kỳ nhỏ)**, true peak -10,35 dBTP, LRA 12,60; 8 khoảng lặng
  0,5–1,0s (2,86 / 6,27 / 9,36 / 12,35 / 14,85 / 21,39 / 22,26 / 29,43s).
- **Suy luận:** Thẻ tiêu đề 3 phần (hẹn hò + đại lý xe + bài kiểm tra chi tiêu)
  là hook tốt — người xem tự hỏi "bài kiểm tra là gì?". Giọng kể trùng nội dung
  chữ phụ đề (kể chuyện đi ăn nhà hàng đắt tiền). Âm thanh cực kỳ nhỏ là lỗi kỹ
  thuật, không phải lỗi hook. **H giữ 3.**

## 2. Pacing

- **Quan sát:** 26 keyframe trong 32,15s — cắt rất nhanh (chữ phụ đề đổi liên
  tục). Frame 25%: phụ nữ áo vàng + người đàn ông trong xe, chữ "I THINK
  SOMEONE LIKES" / "EXPENSIVE RESTAURANTS" / "LIKE A DEALERSHIP OR SOMETHING";
  50%: cận mặt phụ nữ "IF YOU CAN GO" + xe + emoji 👍 "I MEAN I DESERVE".
  Watermark "OpusClip" hiện trên nhiều frame (video được cắt/chú thích tự động
  bằng OpusClip).
- **Suy luận:** 26 cắt/32s là nhịp nhanh nhất nhóm Bất ngờ — chữ phụ đề đổi liên
  tục giữ mắt người xem. Các khoảng lặng là ngắt giữa các câu kể. **R giữ 4.**

## 3. Audio

- **Quan sát:** Giọng nữ kể chuyện; độ lớn **-36,95 LUFS — cực kỳ nhỏ**; 8
  khoảng lặng 0,5–1,0s.
- **Suy luận:** Âm thanh gần như không nghe được trên loa ngoài — lỗi kỹ thuật
  nghiêm trọng. Nhưng chữ phụ đề lớn + cắt nhanh bù lại cho người xem tắt tiếng.
  Bản làm lại bắt buộc chuẩn hóa về ~-16 LUFS. **Nhạc/SFX: chưa đánh giá được.**

## 4. Cấu trúc câu chuyện

- **Quan sát (từ frame + transcript):** Thẻ tiêu đề (3 phần) → cô gái kể: thích
  đi nhà hàng đắt tiền, có người trả tiền → "I deserve to be spoiled. Why not?"
- **Suy luận:** Cấu trúc "thẻ tiêu đề hứa hẹn → kể chuyện → câu kết tự tin".
  Payoff là câu "I deserve" — thái độ tự tin gây tranh cãi (người xem bình luận
  đồng tình hoặc phản đối). **P giữ 4.**

## 5. Cách làm lại không cần máy quay

- Kể chuyện bằng chữ phụ đề: hình AI/stock (xe, nhà hàng) + chữ phụ đề lớn đổi
  nhanh + giọng AI kể. Không cần người thật. **F giữ 3** — cần chữ phụ đề đổi
  nhanh đúng nhịp (công phu hơn ảnh tĩnh).

## 6. Chi phí sản xuất

- **Độ khó: trung bình.** Thời gian làm lại ước tính 3–4 giờ (kịch bản kể chuyện
  + 5–6 hình + phụ đề + giọng). Công cụ: ảnh AI/stock + giọng AI + CapCut (tự
  làm phụ đề, không dùng OpusClip có watermark). Rủi ro lớn nhất: câu chuyện
  phải thật sự gây tranh cãi/đồng cảm — kể chuyện nhạt là hỏng.
  **C giữ 3.**

## Phán quyết điểm: GIỮ NGUYÊN 67 (H=3 R=4 F=3 P=4 C=3 A=3 L=3)

Thẻ tiêu đề 3 phần là hook tốt; 26 cắt/32s xác nhận R=4. Âm thanh cực kỳ nhỏ là
lỗi kỹ thuật. **Cảnh báo bản quyền:** watermark OpusClip trên frame — video gốc
được cắt bằng công cụ có watermark; bản làm lại tự làm phụ đề, không dùng lại
video gốc. L=3 đã tính.

---

# B03 — #67 — 61 điểm — KẾT LUẬN: GIỮ NGUYÊN 61

- **URL:** https://www.tiktok.com/@vxzz888/video/7459407862738193666
- **Kênh / ngách / thời lượng:** @vxzz888 / surprise / 81,29s, 576x1024 hevc
- **Ngôn ngữ nói:** tiếng Anh · 67 từ/30s ≈ 134 từ/phút
- **Điểm gốc:** H=3 R=3 F=3 P=3 C=4 A=3 L=2 → 61

## 1. Hook (3s đầu)

- **Quan sát:** Frame 0/1/2s: chữ "Pop culture moments we don't talk about
  enough" trên clip một phụ nữ đang hét (ngoài trời, tường hồng). Transcript:
  lời thoại ngẫu nhiên từ các clip — "Oh, sorry, I was I was saying hello. I
  was just a Mexico earlier to shut the fuck up. Name something that might be
  curvy. Me. Oh, if you could say something to Janelle right now, what would it
  be? Um, that we miss you…"
- **Suy luận:** Hook là tiêu đề ("những khoảnh khắc văn hóa đại chúng mà ta ít
  nói tới") — hứa hẹn hoài niệm. Giọng không nói lại tiêu đề, chỉ là lời thoại
  rời rạc từ các clip. H=3 đã tính việc hook chỉ có chữ. **H giữ 3.**

## 2. Pacing

- **Quan sát:** Phép đo ghi 2 keyframe (41,6 / 49,0s) — là lỗi đo: sheet cho thấy
  clip đổi (phụ nữ hét → bản tin TV "today NOW! HELP NOW! Sacramento Teen
  Janelle Kelly Missing For Six Days" → phụ nữ che miệng → hai người bên xe).
  Audio: độ lớn -21,57 LUFS; 1 khoảng lặng ở 18,02s. Thời lượng 81,29s — dài.
- **Suy luận:** Nhịp là chuỗi clip hoài niệm, mỗi clip vài giây. Người xem ở lại
  vì nhận ra clip quen thuộc. 81s là dài — bản làm lại nên cắt xuống ~50s.
  **R giữ 3.**

## 3. Audio

- **Quan sát:** Nhiều giọng nói khác nhau (lời thoại từ các clip gốc); độ lớn
  -21,57 LUFS; 1 khoảng lặng ở 18,02s.
- **Suy luận:** Audio là tập hợp lời thoại rời rạc, không có giọng dẫn — giống
  điểm yếu của H04. Bản làm lại nên thêm giọng dẫn. **Nhạc/SFX: chưa đánh giá
  được.**

## 4. Cấu trúc câu chuyện

- **Quan sát (từ frame + transcript):** Tiêu đề hoài niệm → chuỗi clip (phụ nữ
  hét → bản tin Janelle Kelly mất tích → phản ứng → hai người bên xe).
- **Suy luận:** Cấu trúc hỏi → đáp bằng clip, giống H04 (cùng format, khác chủ
  đề). Payoff là sự nhận ra. **P giữ 3.**

## 5. Cách làm lại không cần máy quay

- Video hoài niệm: một tiêu đề hoài niệm + hình AI/stock làm "khoảnh khắc" +
  giọng AI dẫn. Không dùng clip TV gốc. **F giữ 3.**

## 6. Chi phí sản xuất

- **Độ khó: dễ.** Thời gian làm lại ước tính 2–3 giờ (1 tiêu đề + 4–5 hình +
  giọng). Công cụ: ảnh AI/stock + giọng AI + CapCut. Rủi ro lớn nhất: chọn sai
  "khoảnh khắc" — phải là thứ khán giả mục tiêu thật sự nhớ.
  **C giữ 4.**

## Phán quyết điểm: GIỮ NGUYÊN 61 (H=3 R=3 F=3 P=3 C=4 A=3 L=2)

Tiêu đề hoài niệm là hook chữ tốt; giọng không nói lại tiêu đề nhưng H=3 đã tính.
**Cảnh báo bản quyền:** toàn bộ clip là TV/tin tức lấy lại (chương trình TODAY,
bản tin Janelle Kelly) — L=2 đã tính; bản làm lại tuyệt đối không dùng clip gốc.

---

# B04 — #55 — 58 điểm — KẾT LUẬN: GIỮ NGUYÊN 58

- **URL:** https://www.tiktok.com/@.alecmiller/video/7700263791073725727
- **Kênh / ngách / thời lượng:** @.alecmiller / surprise / 44,87s, 1080x1920 hevc
- **Ngôn ngữ nói:** tiếng Anh · 130 từ/30s ≈ 260 từ/phút (nói rất nhanh)
- **Điểm gốc:** H=3 R=3 F=2 P=3 C=3 A=4 L=4 → 58

## 1. Hook (3s đầu)

- **Quan sát:** Frame 0/1/2s: cùng một thanh niên trong phòng, chữ "Being late
  to a college class vs a high school class:" — anh ta đóng cả hai vai (áo len
  xanh đậm = một vai, áo polo xanh nhạt = vai kia). Transcript: đối thoại vào
  ngay — "All right, class, let's just make sure-- - I'm so sorry for being late.
  My moped didn't start… - You're like 30 minutes late, no one cares… - I am so
  sorry for the fuck up. Shut the fuck up, 30 seconds late… - No, you can't come
  in. Go get a tardy slip from across the fucking school…"
- **Suy luận:** Hook nói trùng đúng tiền đề trên màn hình (đi học muộn) — giọng
  nói là đối thoại của chính tiền đề đó. Đây là hook kép dạng "tiền đề + đối
  thoại". **H giữ 3.**

## 2. Pacing

- **Quan sát:** Phép đo ghi 0 keyframe — đúng ở đây: một cảnh tĩnh duy nhất (cùng
  một phòng, cùng một người, chỉ đổi áo). Frame 25%/50%/75%: cùng phòng, cùng
  người, áo đổi (xanh đậm ↔ xanh nhạt) = hai vai. Audio: 130 từ/30s = 260
  từ/phút (nói rất nhanh); 1 khoảng lặng ở 5,11s; độ lớn -23,84 LUFS.
- **Suy luận:** Nhịp nằm ở đối thoại nhanh (260 từ/phút — nhanh gấp rưỡi vùng an
  toàn) + đổi áo đánh dấu đổi vai. Một cảnh tĩnh nhưng không buồn vì thoại nhanh
  và đổi vai liên tục. **R giữ 3.**

## 3. Audio

- **Quan sát:** Đối thoại tiếng Anh rất nhanh (260 từ/phút), hai giọng (một người
  đóng hai vai); độ lớn -23,84 LUFS (nhỏ); 1 khoảng lặng ở 5,11s.
- **Suy luận:** 260 từ/phút là quá nhanh — người xem không phải bản xứ khó theo
  kịp. Bản làm lại nên chậm lại ~160 từ/phút và dùng hai giọng AI khác nhau cho
  hai vai (dễ phân biệt hơn một người đổi giọng). **Nhạc/SFX: chưa đánh giá
  được.**

## 4. Cấu trúc câu chuyện

- **Quan sát (từ frame + transcript):** Tiền đề (đi muộn) → vai 1 (đại học: "30
  phút muộn, không ai quan tâm") → vai 2 (cấp 3: "30 giây muộn cũng không được
  vào, đi lấy giấy phép muộn") → câu kết chửi thề.
- **Suy luận:** Cấu trúc **X vs Y** (đại học vs cấp 3): cùng một tình huống, hai
  phản ứng trái ngược. Payoff là sự đối lập (đại học thoải mái, cấp 3 nghiêm
  khắc). **P giữ 3.**

## 5. Cách làm lại không cần máy quay

- Sketch X vs Y bằng người que: 2 nhân vật que (hoặc 1 nhân vật đổi màu áo như
  bản gốc) + đối thoại nhanh + chữ tiền đề. Không cần diễn viên. **F giữ 2** —
  khó vì hài nằm ở đối thoại và diễn xuất, người que khó truyền đạt.

## 6. Chi phí sản xuất

- **Độ khó: trung bình.** Thời gian làm lại ước tính 3–4 giờ (kịch bản đối thoại
  + animate người que + 2 giọng). Công cụ: Manim/Remotion + giọng AI + CapCut.
  Rủi ro lớn nhất: thoại phải thật sự hài và nhanh vừa phải (260 từ/phút là quá
  nhanh — chậm lại sẽ mất nhịp, nhanh quá thì không nghe kịp).
  **C giữ 3.**

## Phán quyết điểm: GIỮ NGUYÊN 58 (H=3 R=3 F=2 P=3 C=3 A=4 L=4)

Hook kép xác nhận (đối thoại nói đúng tiền đề trên màn hình). Đối thoại 260
từ/phút là quá nhanh — bản làm lại chậm lại ~160 từ/phút. Không có watermark;
L=4.

---

# B05 — #15 — 55 điểm — KẾT LUẬN: GIỮ NGUYÊN 55

- **URL:** https://www.youtube.com/shorts/KWliupgtYN4
- **Kênh / ngách / thời lượng:** unknown / surprise / 59,57s, 1080x1920 h264
- **Ngôn ngữ nói:** không có lời nói (transcript chỉ có "[Music]")
- **Điểm gốc:** H=3 R=3 F=2 P=3 C=2 A=3 L=4 → 55

## 1. Hook (3s đầu)

- **Quan sát:** Frame 0/1/2s: một người đàn ông ló mặt qua lá cây, chữ
  "POV:when you're just too thief". Transcript chỉ có "[Music]" — **không có lời
  nói nào trong 30s đầu**. Audio: độ lớn -21,17 LUFS, LRA 23,80 (dải động rất
  rộng — nhạc lúc to lúc nhỏ); 3 khoảng lặng ở 5,62 / 7,44 / 12,51s.
- **Suy luận:** Hook duy nhất là nhãn "POV:" + khuôn mặt ló qua lá — nhãn POV đặt
  người xem vào trong cảnh ("bạn là tên trộm"). Không có hook nói, nhưng nhãn
  POV là hook chữ đủ mạnh cho format này. H=3 đã tính việc hook chỉ có chữ.
  **H giữ 3.**

## 2. Pacing

- **Quan sát:** Phép đo ghi 0 keyframe — là lỗi đo: sheet cho thấy cảnh đổi (trốn
  trong lá → chạy → đánh nhau trên đường → trốn sau tường đá). Frame 25%: bãi
  cỏ trống (anh ta đã chạy); 50%: hai người đánh nhau trên đường; 75%: hai người
  trốn sau tường đá (một người áo caro đỏ).
- **Suy luận:** Chuỗi: trốn → chạy → đánh nhau → trốn lại. Nhịp là hành động
  (không có lời). **R giữ 3.**

## 3. Audio

- **Quan sát:** Không có lời nói; chỉ có nhạc. Độ lớn -21,17 LUFS, LRA 23,80
  (nhạc lên xuống mạnh). Các khoảng lặng ở 5,62 / 7,44 / 12,51s là ngắt nhạc.
- **Suy luận:** Video này là nhạc + hình — hiệu quả dựa vào nhạc và hành động.
  Không đánh giá được nhạc cụ thể vì không nghe. Bản làm lại nên dùng nhạc có
  nhịp căng thẳng (trốn/chạy) + SFX bước chân.
  **Nội dung nhạc: chưa đánh giá được (không nghe).**

## 4. Cấu trúc câu chuyện

- **Quan sát (từ frame):** Trốn trong lá → chạy → đánh nhau → trốn sau tường
  (bị bắt/trốn lại).
- **Suy luận:** Cấu trúc "trốn — chạy — bị bắt": người xem ở lại để xem anh ta
  có thoát không. Payoff là cảnh cuối (trốn sau tường, thở phào hoặc bị bắt —
  không xác định được từ frame tĩnh).
  **P giữ 3.**

## 5. Cách làm lại không cần máy quay

- Sketch POV bằng người que: nhãn "POV:" + nhân vật que trốn/chạy/đánh nhau.
  Không cần diễn viên. **F giữ 2** — khó vì hài hành động cần timing hình ảnh
  chính xác.

## 6. Chi phí sản xuất

- **Độ khó: trung bình-khó.** Thời gian làm lại ước tính 4–6 giờ (animate người
  que trốn/chạy + nhạc). Công cụ: Manim/Remotion + nhạc miễn phí thương mại +
  CapCut. Rủi ro lớn nhất: timing hành động — sai nhịp là mất cười.
  **C giữ 2.**

## Phán quyết điểm: GIỮ NGUYÊN 55 (H=3 R=3 F=2 P=3 C=2 A=3 L=4)

Nhãn "POV:" là hook chữ đủ mạnh; không có hook nói nhưng H=3 đã tính. Video
nhạc + hình, không có lời. Không có watermark; L=4.

---

# B06 — #24 — 49 điểm — KẾT LUẬN: ĐIỀU CHỈNH 49 → 54 (H 2→3)

- **URL:** https://www.youtube.com/shorts/ERweupp9eVU
- **Kênh / ngách / thời lượng:** unknown / surprise / 26,08s, 1080x1920 h264
- **Ngôn ngữ nói:** tiếng Anh · 10 từ/30s ≈ 20 từ/phút (ít lời, chủ yếu nhạc/SFX)
- **Điểm gốc:** H=2 R=3 F=2 P=3 C=2 A=3 L=3 → 49
- **Điểm mới:** H=3 R=3 F=2 P=3 C=2 A=3 L=3 → **54**

## 1. Hook (3s đầu)

- **Quan sát:** Frame 0s: phụ nữ ngồi bên bể bơi, tay cầm thìa có thạch xanh,
  người đàn ông cầm phao xanh sau lưng. Frame 1s: cô ta hạ thìa xuống nước.
  Frame 2s: chữ "JELLY" khi thạch rơi xuống nước. Không có chữ lớn ở 1s.
  Transcript: "It's jelly. That's a pool. Wanna try? It bounces! HIGHER!" —
  **giọng nói vào ngay và giải thích đúng hình ảnh đang thấy** (thạch + bể bơi +
  nảy). Audio: độ lớn -15,51 LUFS (gần chuẩn); không có khoảng lặng; chỉ 10
  từ/30s (lời ít, chủ yếu là nhạc/SFX).
- **Suy luận:** Lúc chấm khung hình, H=2 vì "không có chữ ở 1s". Nhưng bằng chứng
  mới: **giọng nói là hook** — "It's jelly. That's a pool. Wanna try? It
  bounces!" nói đúng thứ kỳ lạ trên màn hình (thạch trên mặt nước bể bơi). Đây
  là hook kép dạng "hình kỳ lạ + giọng giải thích": mắt thấy thạch nổi trên
  nước, tai nghe "nó nảy được!". **H 2→3.**

## 2. Pacing

- **Quan sát:** 9 keyframe trong 26,08s (3,17 / 3,4 / 3,87 / 5,77 / 6,07 / 6,3 /
  7,87 / 12,2 / 24,87s). Frame 25%: chân người đàn ông bước tới mép bể (phao nằm
  dưới đất); 50%: chân nhảy lên + tay cô gái chạm mặt nước (thạch tạo thành lớp
  trên mặt nước); 75%: toàn cảnh — cô gái đứng trên tấm phủ xanh trên mặt bể
  (lớp thạch che cả bể bơi).
- **Suy luận:** Nhịp là sự leo thang của lớp thạch: thìa thạch → thạch rơi →
  lớp thạch → người đứng được trên thạch. Mỗi bước là một bất ngờ. **R giữ 3.**

## 3. Audio

- **Quan sát:** Lời ít (10 từ/30s); độ lớn -15,51 LUFS (gần chuẩn); không có
  khoảng lặng. Âm thanh chính là nhạc + tiếng hiệu ứng (tiếng thạch nảy — không
  xác định được cụ thể vì không nghe).
- **Suy luận:** Lời ít nhưng đúng chỗ (4 câu ngắn, mỗi câu một nhịp). Bản làm
  lại: giữ lời ngắn, thêm SFX "boing" khi thạch nảy.
  **Nhạc/SFX cụ thể: chưa đánh giá được.**

## 4. Cấu trúc câu chuyện

- **Quan sát (từ frame + transcript):** Thạch trên thìa → thạch rơi xuống nước
  → thạch tạo thành lớp → người đứng được trên lớp thạch ("It bounces! HIGHER!").
- **Suy luận:** Cấu trúc "thử nghiệm kỳ lạ leo thang": mỗi bước to hơn bước
  trước (thìa → cả bể → người đứng lên). Payoff là người đứng được trên mặt
  nước. **P giữ 3.**

## 5. Cách làm lại không cần máy quay

- Thử nghiệm bằng AI video: Veo/Kling tạo cảnh thạch trên bể bơi + giọng AI
  ("It's jelly. That's a pool."). Không cần người thật, không cần bể bơi thật.
  **F giữ 2** — khó vì AI video phải giữ thạch/bể bơi nhất quán qua các cảnh,
  và hiệu ứng "người đứng trên nước" khó làm thuyết phục bằng AI.

## 6. Chi phí sản xuất

- **Độ khó: trung bình-khó.** Thời gian làm lại ước tính 4–6 giờ (prompt AI
  video nhiều lần + giọng). Công cụ: Veo/Kling/Wan 2.2 + giọng AI + CapCut.
  Rủi ro lớn nhất: AI video không giữ được thạch nhất quán (thạch đổi hình giữa
  các cảnh là hỏng); và hiệu ứng người đứng trên nước dễ trông giả.
  **C giữ 2.**

## Phán quyết điểm: ĐIỀU CHỈNH 49 → 54 (H 2→3)

Bằng chứng mới: giọng nói là hook — "It's jelly. That's a pool. Wanna try? It
bounces!" giải thích đúng hình kỳ lạ trên màn hình, tạo thành hook kép (hình +
giọng). H=2 lúc chấm khung hình chỉ vì không có chữ ở 1s — đã bỏ qua hook nói.
Không có watermark; L=3.

---

# C02 — #47 — 79 điểm — KẾT LUẬN: GIỮ NGUYÊN 79

- **URL:** https://www.youtube.com/shorts/LTHa_2wTxkI
- **Kênh / ngách / thời lượng:** unknown / emotional / 23,22s, 1080x1920 h264
- **Ngôn ngữ nói:** tiếng Anh · 32 từ/30s ≈ 64 từ/phút (ít lời)
- **Điểm gốc:** H=4 R=3 F=5 P=4 C=3 A=5 L=4 → 79

## 1. Hook (3s đầu)

- **Quan sát:** Frame 0/1/2s: bé gái 3D (tóc xoăn vàng, nơ hồng, đồ ngủ hồng) mặt
  buồn, chữ "She is Daddy's girl 💖" + người mẹ (nửa mặt, tay chỉ) đang mắng.
  Watermark "NVV" góc dưới-phải mọi frame. Transcript: "No, no, you shouldn't
  do that. Gabu, Gaba. Gaba? Gaba? Huh? Oh, come here, sweetheart. Blue, blue,
  blip. Gaba, Gaba, blue. Who's my good girl? You are. I love you so much."
  Audio: độ lớn -26,73 LUFS (nhỏ); không có khoảng lặng.
- **Suy luận:** Chữ "She is Daddy's girl" + mặt bé buồn + mẹ mắng là hook cảm
  xúc mạnh (người xem tự hỏi "bé làm gì sai, bố sẽ làm gì?"). Giọng nói trùng
  cảnh (mẹ mắng "No, no, you shouldn't do that" rồi bố dỗ "come here,
  sweetheart"). **H giữ 4.**

## 2. Pacing

- **Quan sát:** Phép đo ghi 0 keyframe — là lỗi đo: sheet cho thấy cảnh đổi (mẹ
  mắng → bé bĩu môi khoanh tay → bố ngủ mệt trên giường → bố ôm bé → bố con
  cười). Frame 25%: bố nằm ngủ (mệt); 50%: bố ôm bé, cả hai nhắm mắt; 75%: bố
  bế bé, cả hai cười. Thời lượng 23,22s.
- **Suy luận:** Một dòng cảm xúc liên tục, không cắt nhiều — nhịp là cảm xúc
  (mắng → giận → mệt → ôm → cười). 23s là ngắn, vừa đủ cho một câu chuyện nhỏ.
  **R giữ 3.**

## 3. Audio

- **Quan sát:** Lời thoại tiếng Anh ít (32 từ/30s — chủ yếu là tiếng gọi "Gaba,
  Gaba" và câu dỗ); độ lớn -26,73 LUFS (nhỏ); không có khoảng lặng.
- **Suy luận:** Lời thoại ít nhưng đúng chỗ (mắng → dỗ → yêu). Âm thanh nhỏ —
  bản làm lại cần tăng về ~-16 LUFS. **Nhạc/SFX: chưa đánh giá được.**

## 4. Cấu trúc câu chuyện

- **Quan sát (từ frame + transcript):** Mẹ mắng bé → bé giận (bĩu môi, khoanh
  tay) → bố mệt (nằm ngủ) → bố ôm bé → bé cười, bố nói "Who's my good girl?
  You are. I love you so much."
- **Suy luận:** Cấu trúc "xung đột nhỏ → an ủi": bé bị mắng, bố là người an ủi.
  Payoff là câu "Who's my good girl? You are" + nụ cười của bé — cảm xúc ấm.
  **P giữ 4.**

## 5. Cách làm lại không cần máy quay

- Hoạt hình 3D/AI: nhân vật AI (bé gái + bố + mẹ) + câu chuyện nhỏ 20–25s +
  giọng AI. **F giữ 5** — format sinh ra cho AI (không cần người thật).
  Nhưng nhân vật AI phải giữ nhất quán qua các cảnh (bé gái đổi mặt là hỏng).

## 6. Chi phí sản xuất

- **Độ khó: trung bình.** Thời gian làm lại ước tính 4–6 giờ (tạo nhân vật AI
  nhất quán + 4–5 cảnh + giọng). Công cụ: ảnh AI/Video AI + giọng AI + CapCut.
  Rủi ro lớn nhất: nhân vật AI không nhất quán (mặt bé đổi giữa các cảnh);
  và cảm xúc "ấm" khó làm bằng AI (dễ thành vô cảm).
  **C giữ 3.**

## Phán quyết điểm: GIỮ NGUYÊN 79 (H=4 R=3 F=5 P=4 C=3 A=5 L=4)

Chữ "She is Daddy's girl" + mặt bé buồn là hook cảm xúc mạnh; giọng trùng cảnh.
**Cảnh báo bản quyền:** watermark "NVV" trên mọi frame — đây là hoạt hình 3D của
người khác; bản làm lại phải tạo nhân vật của mình, không dùng lại hình ảnh gốc.
L=4 đã tính.

---

# C03 — #30 — 74 điểm — KẾT LUẬN: GIỮ NGUYÊN 74

- **URL:** https://www.youtube.com/shorts/JjPMsIxr9Mw
- **Kênh / ngách / thời lượng:** unknown / emotional / 105,32s, 1080x1920 h264
- **Ngôn ngữ nói:** tiếng Hindi (Whisper nhận hi) — **transcript không dùng được**
- **Điểm gốc:** H=2 R=4 F=5 P=4 C=4 A=4 L=4 → 74

## 1. Hook (3s đầu)

- **Quan sát:** Frame 0/1/2s: tranh AI phong cách Ghibli — phụ nữ áo vàng đang
  xếp vali trong phòng ấm cúng (đồng hồ, vòng hoa cúc, gấu bông, laptop). Không
  có chữ nào. Watermark mờ "@Ghiblidaysmotion" ở dưới mỗi frame. Transcript là
  từ Hindi "चलोगलस में गलती है" lặp đi lặp lại — Whisper vòng lặp, không phải lời
  nói thật. Audio: **khoảng lặng 0–0,94s và 1,42–1,92s đầu (hai khoảng im lặng
  ngay đầu video)**; độ lớn -18,11 LUFS.
- **Suy luận:** Không có chữ, không có bằng chứng lời nói, giọng vào muộn (hai
  khoảng lặng đầu). Hook duy nhất là hình tranh Ghibli đẹp (phòng ấm cúng, cô
  gái xếp vali — người xem tự hỏi "cô ấy đi đâu?"). H=2 đã tính đúng.
  **H giữ 2.**

## 2. Pacing

- **Quan sát:** 34 keyframe trong 105,32s — nhiều ảnh AI đổi liên tục. Frame
  25%: cùng phòng, cô gái ngẩng lên ngạc nhiên; 50%: ga tàu, cô gái chạy với
  vali về phía tàu xanh; 75%: cận mặt cô gái trang điểm (bông tai, gương) rồi
  chắp tay cầu nguyện (áo tím, nhang).
- **Suy luận:** Mỗi ảnh là một beat: xếp vali → ngạc nhiên → chạy ra ga → trang
  điểm → cầu nguyện. 34 ảnh/105s là nhịp đều (~3s/ảnh). 105s là dài — bản làm
  lại nên cắt xuống ~50s (giữ 5–6 ảnh).
  **R giữ 4.**

## 3. Audio

- **Quan sát:** Transcript hỏng (Whisper vòng lặp trên tiếng Hindi) — không biết
  nội dung lời kể. Độ lớn -18,11 LUFS. Hai khoảng lặng đầu (0–0,94s,
  1,42–1,92s) cho thấy giọng kể vào muộn.
- **Suy luận:** Không đánh giá được nội dung lời kể. Bản làm lại: giọng vào từ
  0,1s, không để im lặng đầu. **Nội dung audio: chưa đánh giá được (transcript
  hỏng).**

## 4. Cấu trúc câu chuyện

- **Quan sát (từ frame):** Xếp vali (chuẩn bị) → chạy ra ga (đi) → trang điểm
  (chuẩn bị gặp ai đó) → cầu nguyện (về nhà ăn lễ — vòng hoa cúc, đèn diya gợi
  Diwali).
- **Suy luận:** Cấu trúc "chuẩn bị → hành trình → trở về": cô gái về quê ăn lễ.
  Payoff là cảnh cầu nguyện cuối (ấm cúng, sum họp). Cảm xúc là nỗi nhớ nhà.
  **P giữ 4.**

## 5. Cách làm lại không cần máy quay

- Tranh AI kể chuyện: 5–6 ảnh AI phong cách nhất quán (cùng nhân vật, cùng
  phong cách vẽ) + giọng AI kể. **F giữ 5** — format sinh ra cho ảnh AI.
  Nhưng phong cách + nhân vật phải nhất quán qua các ảnh (khó nhất của format
  này).

## 6. Chi phí sản xuất

- **Độ khó: trung bình.** Thời gian làm lại ước tính 4–6 giờ (5–6 ảnh AI nhất
  quán + kịch bản kể + giọng). Công cụ: ảnh AI + giọng AI + CapCut. Rủi ro lớn
  nhất: nhân vật AI đổi mặt/phong cách giữa các ảnh (mất cảm xúc); và câu chuyện
  phải có cảm xúc thật (nhớ nhà), không chỉ là ảnh đẹp.
  **C giữ 4.**

## Phán quyết điểm: GIỮ NGUYÊN 74 (H=2 R=4 F=5 P=4 C=4 A=4 L=4)

Không có chữ, không có bằng chứng lời nói, giọng vào muộn — H=2 đúng. 34 ảnh/
105s xác nhận R=4. **Cảnh báo bản quyền:** watermark "@Ghiblidaysmotion" —
phong cách Ghibli + ảnh của người khác; bản làm lại dùng ảnh AI của mình với
phong cách riêng (không sao chép ảnh gốc). L=4 đã tính.

---

# C05 — #43 — 66 điểm — KẾT LUẬN: GIỮ NGUYÊN 66

- **URL:** https://www.youtube.com/shorts/dn8Eru1veuA
- **Kênh / ngách / thời lượng:** unknown / emotional / 84,06s, 1080x1920 h264
- **Ngôn ngữ nói:** tiếng Tây Ban Nha · 79 từ/30s ≈ 158 từ/phút
- **Điểm gốc:** H=4 R=3 F=2 P=5 C=2 A=5 L=2 → 66

## 1. Hook (3s đầu)

- **Quan sát:** Frame 0/1/2s: định dạng reaction-video — khung nhỏ trên/dưới là
  một cặp đôi (nam + nữ đeo tai nghe) đang xem; khung chính là bố mẹ đang đeo
  thiết bị trợ thính cho bé gái ~3 tuổi. Chữ lớn: "EL MOMENTO MÁS EMOTIVO Y
  GRACIOSO DE ESTOS PAPÁS" + "Y después de casi 3 años nuestra hija por primera
  vez escucha un sonido 😭😭😭😭😭😭". Transcript (tiếng Tây Ban Nha): "Y después
  de casi tres años nuestra hija por primera vez, escucha un sonido. - Espera,
  que ya me estemos quemados de ti. - Bueno, dos. - Ay no. - ¡Ah! - ¡Ah!"
- **Suy luận:** Chữ hứa hẹn ("sau gần 3 năm, con gái lần đầu nghe được âm
  thanh") + giọng nói trùng đúng chữ đó — **hook kép**. Đây là hook cảm xúc
  mạnh nhất trong 25 video (lời hứa về một khoảnh khắc có thật, không thể bịa).
  **H giữ 4.**

## 2. Pacing

- **Quan sát:** Phép đo ghi 0 keyframe — là lỗi đo: sheet cho thấy cảnh đổi
  (bố mẹ đeo thiết bị → bé nghe → bố mẹ cười/khóc). Frame 25%/50%: bố mẹ giữ
  thiết bị ở tai bé; 75%: chữ "Mi Amor, escuchaste" / "escuchaste" — bé nghe
  được, bố mẹ cười khóc. Audio: độ lớn -24,24 LUFS (nhỏ); không có khoảng lặng.
- **Suy luận:** Nhịp là sự chờ đợi: đeo thiết bị → im lặng chờ → bé phản ứng →
  bố mẹ vỡ òa. 84s là dài cho một khoảnh khắc — bản làm lại nên cắt xuống ~50s.
  **R giữ 3.**

## 3. Audio

- **Quan sát:** Đối thoại tiếng Tây Ban Nha thật (gia đình thật, không phải giọng
  dẫn); độ lớn -24,24 LUFS (nhỏ); không có khoảng lặng; 79 từ/30s = 158
  từ/phút (đúng vùng an toàn).
- **Suy luận:** Âm thanh là đối thoại thật của gia đình — cảm xúc nằm ở giọng
  nói thật (tiếng reo "¡Ah!"). Bản làm lại bằng hoạt hình phải dùng giọng AI
  diễn cảm (khó bằng giọng thật). **Nhạc/SFX: chưa đánh giá được.**

## 4. Cấu trúc câu chuyện

- **Quan sát (từ frame + transcript):** Lời hứa (3 năm chờ đợi) → đeo thiết bị
  → bé nghe được âm thanh đầu tiên → bố mẹ cười khóc ("Mi Amor, escuchaste").
- **Suy luận:** Cấu trúc "chờ đợi dài → khoảnh khắc vỡ òa": 3 năm chờ đợi dồn
  vào 1 giây bé nghe được. Payoff là phản ứng của bé + bố mẹ — đây là cơ chế
  cảm xúc mạnh nhất trong 30 video (khoảnh khắc thật, không thể diễn). **P giữ
  5.**

## 5. Cách làm lại không cần máy quay

- **Không được dùng lại footage gốc** (đây là khoảnh khắc riêng tư của một gia
  đình thật). Bản làm lại phải là hoạt hình AI với câu chuyện gốc tương tự: một
  đứa trẻ nghe được âm thanh đầu tiên (hoặc nhìn thấy màu sắc đầu tiên, hoặc
  bước đi đầu tiên) — nhân vật AI, giọng AI. **F giữ 2** — khó vì cảm xúc nằm
  ở sự thật (gia đình thật), hoạt hình khó bằng.

## 6. Chi phí sản xuất

- **Độ khó: khó.** Thời gian làm lại ước tính 5–7 giờ (kịch bản cảm xúc + nhân
  vật AI nhất quán + giọng diễn cảm). Công cụ: ảnh/video AI + giọng AI +
  CapCut. Rủi ro lớn nhất: hoạt hình không đủ cảm xúc (dễ thành sến); và câu
  chuyện phải tôn trọng (không được khai thác trẻ em thật).
  **C giữ 2.**

## Phán quyết điểm: GIỮ NGUYÊN 66 (H=4 R=3 F=2 P=5 C=2 A=5 L=2)

Hook kép xác nhận (giọng nói đúng chữ hứa hẹn). Payoff là khoảnh khắc thật mạnh
nhất trong 30 video. **Cảnh báo bản quyền/đạo đức:** đây là footage gia đình
thật (trẻ em) — L=2 đã tính; bản làm lại tuyệt đối không dùng lại video gốc,
phải làm hoạt hình với câu chuyện gốc.

---

# D01 — #39 — 80 điểm — KẾT LUẬN: GIỮ NGUYÊN 80

- **URL:** https://www.youtube.com/shorts/RQWBynpDvHU
- **Kênh / ngách / thời lượng:** Panchayati Chowk / everyday / 20,10s, 1080x1920 h264
- **Ngôn ngữ nói:** tiếng Hindi/Urdu (Whisper nhận hi) · 18 từ/30s ≈ 36 từ/phút (rất ít lời)
- **Điểm gốc:** H=4 R=3 F=5 P=3 C=5 A=4 L=5 → 80

## 1. Hook (3s đầu)

- **Quan sát:** Frame 0/1/2s: chó chihuahua AI ngồi trên ghế, mắt to, miệng cười
  kiểu người (nụ cười kỳ lạ, hơi rợn), không có chữ nào. Transcript chỉ 18 từ
  (tiếng Hindi/Urdu): "بھائی تو دل کا بھرا نہیں ہے تو انسان ہی گھٹیا ہے بھائی
  بات سیدھی دل پہلے نہ" — một câu ngắn (đại ý: "anh bạn, nếu lòng không đầy thì
  con người thật nhỏ nhen…"). Audio: độ lớn -16,74 LUFS (gần chuẩn); không có
  khoảng lặng.
- **Suy luận:** Hook là khuôn mặt con chó — nụ cười người trên mặt chó vừa dễ
  thương vừa kỳ lạ, người xem dừng lại vì "con chó này sao cười như người?".
  Không có chữ, nhưng mặt chó đủ mạnh. Lời nói ngắn (1 câu) là punchline, không
  phải hook. **H giữ 4.**

## 2. Pacing

- **Quan sát:** 2 keyframe (2,9 / 10,0s). Frame 25%: cận mặt chó, nụ cười to
  hơn; 50%/75%: chân chó đặt lên bàn, nút "SUBSCRIBE 🔔" hiện ở frame 75%.
  Thời lượng 20,10s.
- **Suy luận:** Một con chó, một câu nói, 20s — nhịp là khuôn mặt chó thay đổi
  (miệng cử động theo lời). 20s là ngắn; bản làm lại nên kéo dài lên 40s (2–3
  câu nói). **R giữ 3.**

## 3. Audio

- **Quan sát:** Lời rất ít (18 từ/30s — một câu ngắn); độ lớn -16,74 LUFS (gần
  chuẩn); không có khoảng lặng.
- **Suy luận:** Một câu nói là đủ cho format "động vật nói một câu". Giọng (AI
  hay người lồng tiếng — không xác định được) là yếu tố quyết định: phải hài
  hước, không được đều. **Nhạc/SFX: chưa đánh giá được.**

## 4. Cấu trúc câu chuyện

- **Quan sát (từ frame + transcript):** Chó cười → nói một câu triết lý hài
  ("lòng không đầy thì con người nhỏ nhen") → nút SUBSCRIBE.
- **Suy luận:** Cấu trúc "động vật nói một câu": một nhân vật + một câu nói
  đáng nhớ. Payoff là câu nói — phải là câu đáng chia sẻ. **P giữ 3.**

## 5. Cách làm lại không cần máy quay

- "Động vật nói": 1 ảnh/video AI động vật (chó, mèo, cú) + 1–3 câu nói bằng
  giọng AI + miệng cử động (AI talking animal). **F giữ 5** — format sinh ra
  cho AI.

## 6. Chi phí sản xuất

- **Độ khó: dễ nhất.** Thời gian làm lại ước tính 1–2 giờ (1 ảnh AI + 1–3 câu
  thoại + giọng). Công cụ: ảnh AI + giọng AI + CapCut. Rủi ro lớn nhất: câu nói
  phải thật sự hay (câu dở là hỏng); và nụ cười AI phải đủ duyên, không được
  rợn quá.
  **C giữ 5.**

## Phán quyết điểm: GIỮ NGUYÊN 80 (H=4 R=3 F=5 P=3 C=5 A=4 L=5)

Khuôn mặt chó cười như người là hook hình mạnh; một câu nói là payoff. Không có
watermark; L=5. **Lưu ý:** 20s quá ngắn — bản làm lại kéo dài lên 40s (2–3 câu
nói). Nút SUBSCRIBE ở cuối là thẻ CTA — bản làm lại nên có CTA tương tự.

---

# D02 — #97 — 58 điểm — KẾT LUẬN: GIỮ NGUYÊN 58

- **URL:** https://www.youtube.com/shorts/bVNawgQ2FDE
- **Kênh / ngách / thời lượng:** HappyStruggle / everyday / 94,71s, 1080x1920 h264
- **Ngôn ngữ nói:** tiếng Hindi (Whisper nhận hi) — **transcript không dùng được**
- **Điểm gốc:** H=2 R=3 F=3 P=3 C=4 A=3 L=4 → 58

## 1. Hook (3s đầu)

- **Quan sát:** Frame 0/1/2s: người đàn ông áo vàng ngồi sơn gạch sân màu đỏ,
  chữ nhỏ tiếng Hindi "Yaha se koi ni ana abhi pota hun!" + "Follow
  @happystrugle" ở dưới. Transcript là từ Hindi "भी भी भी…" lặp đi lặp lại —
  Whisper vòng lặp, không phải lời nói thật. Audio: độ lớn -14,07 LUFS, LRA
  18,50 (dải động rất rộng — nhạc lúc to lúc nhỏ); 9 khoảng lặng, trong đó có
  **một khoảng lặng dài 5,67s ở 12,69–18,37s**; khoảng lặng đầu 0–0,51s.
- **Suy luận:** Hook yếu: chỉ có hình người sơn gạch + chữ nhỏ tiếng Hindi (người
  không biết tiếng Hindi không đọc được). Không có bằng chứng lời nói. H=2 đã
  tính đúng. **H giữ 2.**

## 2. Pacing

- **Quan sát:** 8 keyframe (18,2 / 43,2 / 66,9 / 76,6 / 77,8 / 79,4 / 80,0 /
  81,9s) — cắt thưa, mỗi cảnh dài (người sơn gạch liên tục). Frame 25%: anh ta
  ngẩng lên (có người tới?); 50%: mở nắp thùng sơn / cầm túi; 75%: khiêng bàn /
  quỳ trên gạch đỏ. Thời lượng 94,71s — rất dài.
- **Suy luận:** Nhịp là tiến độ sơn (gạch xám → gạch đỏ, từng viên một) — người
  xem ở lại vì muốn xem sân sơn xong. Khoảng lặng 5,67s ở 12,69–18,37s là đoạn
  im lặng dài (có lẽ chỉ có nhạc, không có gì xảy ra) — điểm rơi tiềm năng.
  **R giữ 3.**

## 3. Audio

- **Quan sát:** Transcript hỏng — không biết nội dung lời nói. Độ lớn -14,07
  LUFS, LRA 18,50. 9 khoảng lặng (nhiều nhất trong 25 video).
- **Suy luận:** Không đánh giá được nội dung lời nói. Nhiều khoảng lặng + một
  khoảng lặng dài 5,67s cho thấy audio thưa (có lẽ nhạc nền là chính).
  **Nội dung audio: chưa đánh giá được (transcript hỏng).**

## 4. Cấu trúc câu chuyện

- **Quan sát (từ frame):** Sơn gạch (xám → đỏ) → ngẩng lên → mở thùng sơn →
  khiêng bàn → quỳ trên gạch đã sơn xong.
- **Suy luận:** Cấu trúc "quá trình biến đổi": sân từ xám thành đỏ, từng viên
  gạch. Payoff là sân sơn xong (đỏ, đẹp). Không có twist — chính tiến độ là
  payoff. **P giữ 3.**

## 5. Cách làm lại không cần máy quay

- Video quá trình: quay tay (hoặc ảnh AI) quá trình biến đổi một thứ gì đó
  (sơn, dọn, nấu, xếp) + chữ + nhạc. **F giữ 3** — cần quay quá trình thật
  (bằng điện thoại, không cần máy quay chuyên nghiệp), hoặc dùng ảnh AI từng
  bước.

## 6. Chi phí sản xuất

- **Độ khó: dễ.** Thời gian làm lại ước tính 2–3 giờ (quay quá trình 5–10 phút
  rồi tua nhanh + nhạc). Công cụ: điện thoại quay + CapCut (tua nhanh). Rủi ro
  lớn nhất: quá trình phải có tiến độ rõ ràng (người xem phải thấy thay đổi);
  và 94s là quá dài — bản làm lại cắt xuống ~45s (tua nhanh).
  **C giữ 4.**

## Phán quyết điểm: GIỮ NGUYÊN 58 (H=2 R=3 F=3 P=3 C=4 A=3 L=4)

Hook yếu (chữ Hindi nhỏ, không có bằng chứng lời nói) — H=2 đúng. Tiến độ sơn
là cơ chế giữ người xem. **Cảnh báo:** watermark "Follow @happystrugle" trên
frame; khoảng lặng dài 5,67s là điểm rơi. L=4.

---

# D03 — #96 — 57 điểm — KẾT LUẬN: GIỮ NGUYÊN 57

- **URL:** https://www.youtube.com/shorts/WPj15NQYffE
- **Kênh / ngách / thời lượng:** unknown / everyday / 41,67s, 1080x1920 h264
- **Ngôn ngữ nói:** không có lời nói (transcript rỗng — 0 từ)
- **Điểm gốc:** H=2 R=2 F=4 P=2 C=5 A=3 L=4 → 57

## 1. Hook (3s đầu)

- **Quan sát:** Frame 0/1s: bình minh trên thành phố, chữ "Good Morning frnds".
  Frame 2s: trà + bánh mì nướng, chữ "Subha ki chaye is my favorite". Transcript
  **rỗng (0 từ)** — không có lời nói nào trong 30s đầu. Audio: độ lớn -16,92
  LUFS, LRA 22,10 (dải động rất rộng — nhạc); 1 khoảng lặng dài 2,86s ở 17,71s.
- **Suy luận:** Hook là "Good Morning frnds" trên nền bình minh — yếu (chào buổi
  sáng không có gì bất ngờ). Không có hook nói. H=2 đã tính đúng. **H giữ 2.**

## 2. Pacing

- **Quan sát:** 10 keyframe (3,0–17,5s) — ảnh đổi mỗi ~2s. Frame 25%: bếp,
  "Cleaning ke baad kitchen or room kitna sunder lgta h..khid p hi proud hota
  h 🥰"; 50%: phòng ngủ tối, "Ab thoda rest v kr lete h 😪"; 75%: bữa tối,
  "Dinner bhot testy tha 😋" (paneer + bánh roti).
- **Suy luận:** Ảnh đổi mỗi 2s nhưng không có câu chuyện — chỉ là danh sách
  khoảnh khắc trong ngày (sáng → trà → dọn bếp → nghỉ → tối). Người xem không có
  lý do ở lại ngoài tò mò xem tiếp theo là gì. **R giữ 2.**

## 3. Audio

- **Quan sát:** Không có lời nói; chỉ có nhạc. Độ lớn -16,92 LUFS (gần chuẩn),
  LRA 22,10. Khoảng lặng dài 2,86s ở 17,71s (gần cuối — có lẽ nhạc ngắt).
- **Suy luận:** Video này là ảnh + nhạc — hiệu quả dựa vào nhạc và chữ. Không
  đánh giá được nhạc cụ thể vì không nghe. **Nội dung nhạc: chưa đánh giá được
  (không nghe).**

## 4. Cấu trúc câu chuyện

- **Quan sát (từ frame):** Sáng (bình minh) → trà sáng → dọn bếp → nghỉ trưa →
  tối (bữa tối).
- **Suy luận:** Không có câu chuyện — chỉ là nhật ký ngày bằng ảnh. Không có
  payoff (bữa tối không phải payoff, chỉ là ảnh cuối). **P giữ 2.**

## 5. Cách làm lại không cần máy quay

- Nhật ký ngày bằng ảnh: ảnh stock/AI + chữ Hinglish/Việt + nhạc. Đây là format
  rẻ nhất (chỉ cần ảnh + chữ + nhạc). **F giữ 4.**

## 6. Chi phí sản xuất

- **Độ khó: dễ nhất.** Thời gian làm lại ước tính 1–2 giờ (5–6 ảnh + chữ +
  nhạc). Công cụ: ảnh stock/AI + CapCut. Rủi ro lớn nhất: format này không có
  câu chuyện — dễ bị xem là "ảnh slideshow" và bị lướt qua; cần thêm một twist
  nhỏ (ví dụ: một khoảnh khắc bất ngờ trong ngày) để giữ người xem.
  **C giữ 5.**

## Phán quyết điểm: GIỮ NGUYÊN 57 (H=2 R=2 F=4 P=2 C=5 A=3 L=4)

"Good Morning frnds" là hook yếu; không có lời nói; không có câu chuyện — H=2,
R=2, P=2 đều đã tính đúng. Đây là video yếu nhất trong 25 video về cấu trúc
(nhưng rẻ nhất để làm). Không có watermark; L=4.

---

# D04 — #34 — 52 điểm — KẾT LUẬN: GIỮ NGUYÊN 52

- **URL:** https://www.youtube.com/shorts/hINC6z3iww0
- **Kênh / ngách / thời lượng:** Disha Stories / everyday / 12,18s, 1080x1920 h264
- **Ngôn ngữ nói:** tiếng Tamil · 15 từ/30s ≈ 30 từ/phút (rất ít lời)
- **Điểm gốc:** H=3 R=2 F=2 P=3 C=3 A=3 L=3 → 52

## 1. Hook (3s đầu)

- **Quan sát:** Frame 0s: ảnh đôi (người đàn ông hôn trán phụ nữ, bó hoa hồng
  đỏ), không có chữ. Frame 1s: thêm chữ Tamil vàng "Veedu eppa vangivinga?"
  (góc trên-phải). Frame 2s: chữ "Car vangiyacha?" (vàng, lớn). Transcript là
  tiếng Tamil (15 từ/30s) — không đọc được tiếng Tamil, không xác định được nội
  dung lời nói. Audio: độ lớn -17,31 LUFS, LRA 2,40 (dải động rất hẹp — nén
  mạnh); không có khoảng lặng.
- **Suy luận:** Hook là sự đối lập giữa ảnh lãng mạn (hoa hồng, hôn trán) và câu
  hỏi thực tế bằng tiếng Tamil (nhà? xe?) — người xem tự hỏi "hai người này là
  ai, sao lại hỏi nhà/xe?". Không đọc được lời nói nên không xác định được hook
  nói. **H giữ 3.**

## 2. Pacing

- **Quan sát:** 5 keyframe — tất cả trong 4s đầu (0,0 / 1,0 / 2,0 / 3,0 / 3,9s).
  Frame 25%: thẻ "MEANWHILE..." (phong cách SpongeBob). Frame 50%/75%: "Us —
  Still playing like kids and unserious about our life 😂" trên cảnh hai người
  đùa giỡn trên giường. Thời lượng 12,18s — rất ngắn.
- **Suy luận:** Chỉ có 2 cảnh (ảnh đôi + đùa trên giường), nối bằng thẻ
  "MEANWHILE...". Nhịp là sự đối lập (lãng mạn → ngốc nghếch). 12s là quá ngắn;
  bản làm lại nên kéo dài lên 40s (thêm 1–2 cảnh đối lập nữa).
  **R giữ 2.**

## 3. Audio

- **Quan sát:** Lời tiếng Tamil rất ít (15 từ/30s); độ lớn -17,31 LUFS, LRA
  2,40 (nén mạnh); không có khoảng lặng.
- **Suy luận:** Không đọc được tiếng Tamil nên không đánh giá được nội dung lời
  nói. **Nội dung audio: chưa đánh giá được (không đọc được tiếng Tamil).**

## 4. Cấu trúc câu chuyện

- **Quan sát (từ frame):** Ảnh lãng mạn + câu hỏi (nhà? xe?) → "MEANWHILE..."
  → thực tế (hai người đùa như trẻ con, không nghiêm túc về cuộc sống).
- **Suy luận:** Cấu trúc **kỳ vọng — thực tế**: ảnh cưới lãng mạn vs đời sống
  ngốc nghếch. Payoff là câu "Still playing like kids and unserious about our
  life 😂" — tự giễu. **P giữ 3.**

## 5. Cách làm lại không cần máy quay

- "Kỳ vọng vs thực tế" bằng ảnh AI: 2 ảnh đối lập (lãng mạn vs ngốc nghếch) +
  chữ + giọng AI. Không cần người thật. **F giữ 2** — khó vì hài nằm ở sự đối
  lập phải thật sự buồn cười (ảnh AI khó diễn "ngốc nghếch" tự nhiên).

## 6. Chi phí sản xuất

- **Độ khó: trung bình.** Thời gian làm lại ước tính 3–4 giờ (2–3 ảnh AI đối lập
  + chữ + giọng). Công cụ: ảnh AI + giọng AI + CapCut. Rủi ro lớn nhất: ảnh AI
  "ngốc nghếch" dễ trông giả; và câu chuyện phải có sự thật (tự giễu thật, không
  phải diễn).
  **C giữ 3.**

## Phán quyết điểm: GIỮ NGUYÊN 52 (H=3 R=2 F=2 P=3 C=3 A=3 L=3)

Đối lập lãng mạn vs ngốc nghếch là hook tốt; chỉ có 2 cảnh nên R=2 đúng.
**Hạn chế:** không đọc được tiếng Tamil nên không đánh giá được lời nói — đây là
video có bằng chứng yếu thứ hai trong 25 video (sau H08). Không có watermark;
L=3.

---

# Bảng tổng kết 25 phán quyết

| Mã | # | Ngách | Ngôn ngữ nói | Điểm gốc | Điểm mới | Phán quyết | Lý do chính |
|----|---|-------|--------------|----------|----------|------------|-------------|
| H01 | 68 | Hài | Anh | 78 | 78 | GIỮ | Hook nói trùng chữ "perfect fit"; giọng vào ngay 0s |
| H02 | 69 | Hài | Anh | 78 | 78 | GIỮ | Tiết lộ một phần đúng format countdown; khoảng lặng là nhịp giữa các mục |
| H03 | 61 | Hài | Anh | 67 | 67 | GIỮ | Countdown âm thanh; dải động rộng là đặc trưng format |
| H04 | 66 | Hài | Anh | 61 | 61 | GIỮ | Câu hỏi hoài niệm là hook chữ tốt; giọng không nói lại nhưng H=3 đã tính |
| H05 | 4 | Hài | Hindi (transcript hỏng) | 61 | 61 | GIỮ | Đối lập 2010→2026 là hook hình; không có bằng chứng hook nói |
| H06 | 23 | Hài | Anh (gần như không lời) | 59 | **54** | **ĐIỀU CHỈNH H 3→2** | Không có hook nói (chỉ tiếng whoop) + dead air 0,6s + frame 0s nhòe |
| H07 | 52 | Hài | Không lời thật | 54 | 54 | GIỮ | Không chữ, không lời — H=2 đã tính đúng; cú đảo ngược võ sĩ thua tốt |
| H08 | 22 | Hài | Hindi (transcript hỏng) | 54 | 54 | GIỮ | Không chữ, không bằng chứng lời; cắt nhanh 19 lần xác nhận R=4 |
| T04 | 84 | Tò mò | Anh | 80 | 80 | GIỮ | Hook kép (giọng nói đúng câu hỏi); dead air 0,67s là trừ nhỏ đã tính |
| T05 | 82 | Tò mò | Anh | 78 | 78 | GIỮ | Hook kép (giọng nói đúng tiêu đề); âm thanh rất nhỏ là lỗi kỹ thuật |
| T06 | 83 | Tò mò | Pháp | 76 | 76 | GIỮ | Hook nói tốt, hook hình yếu (không chữ lớn) — H=3 đúng |
| T07 | 99 | Tò mò | Anh | 74 | 74 | GIỮ | Hook kép + con số cụ thể; âm thanh cực kỳ nhỏ là lỗi kỹ thuật |
| B01 | 8 | Bất ngờ | Anh | 76 | 76 | GIỮ | Bóng bay khổng lồ là hook hình mạnh; dead air 1,14s không phá được hook |
| B02 | 10 | Bất ngờ | Anh | 67 | 67 | GIỮ | Thẻ tiêu đề 3 phần tốt; 26 cắt/32s xác nhận R=4; âm thanh cực kỳ nhỏ |
| B03 | 67 | Bất ngờ | Anh | 61 | 61 | GIỮ | Tiêu đề hoài niệm là hook chữ tốt; giọng không nói lại nhưng H=3 đã tính |
| B04 | 55 | Bất ngờ | Anh | 58 | 58 | GIỮ | Hook kép (đối thoại nói đúng tiền đề); thoại 260 từ/phút quá nhanh |
| B05 | 15 | Bất ngờ | Không lời (nhạc) | 55 | 55 | GIỮ | Nhãn "POV:" là hook chữ đủ mạnh; video nhạc + hình |
| B06 | 24 | Bất ngờ | Anh (ít lời) | 49 | **54** | **ĐIỀU CHỈNH H 2→3** | Giọng nói là hook: "It's jelly. That's a pool. Wanna try? It bounces!" |
| C02 | 47 | Cảm xúc | Anh | 79 | 79 | GIỮ | Chữ "She is Daddy's girl" + mặt bé buồn là hook cảm xúc mạnh |
| C03 | 30 | Cảm xúc | Hindi (transcript hỏng) | 74 | 74 | GIỮ | Không chữ, không bằng chứng lời, giọng vào muộn — H=2 đúng |
| C05 | 43 | Cảm xúc | Tây Ban Nha | 66 | 66 | GIỮ | Hook kép (giọng nói đúng chữ hứa hẹn); payoff là khoảnh khắc thật |
| D01 | 39 | Đời thường | Hindi/Urdu | 80 | 80 | GIỮ | Mặt chó cười như người là hook hình mạnh; một câu nói là payoff |
| D02 | 97 | Đời thường | Hindi (transcript hỏng) | 58 | 58 | GIỮ | Hook yếu (chữ Hindi nhỏ) — H=2 đúng; tiến độ sơn là cơ chế giữ |
| D03 | 96 | Đời thường | Không lời (nhạc) | 57 | 57 | GIỮ | "Good Morning frnds" là hook yếu; không có câu chuyện — H/R/P đã tính đúng |
| D04 | 34 | Đời thường | Tamil (không đọc được) | 52 | 52 | GIỮ | Đối lập lãng mạn vs ngốc nghếch là hook tốt; chỉ có 2 cảnh nên R=2 |

**Tổng 25 video:** 1.652 điểm (trung bình 66,08) — không đổi so với điểm khung hình,
vì hai điều chỉnh triệt tiêu nhau (H06 -5, B06 +5).

**Tổng 30 video (cộng 5 video 85+ đã điều chỉnh trong báo cáo trước: #77 90, #50
85, #81 87, #80 83, FB-05 85 = 430):** 430 + 1.652 = **2.082 điểm, trung bình
69,40** — không đổi so với báo cáo 5 video. Số video đạt 85+ vẫn là **4**
(#77 90, #81 87, #50 85, FB-05 85).

**2 video điều chỉnh:** H06 (59→54) và B06 (49→54). 23 video còn lại giữ nguyên.
Không video nào đổi hạng ngách, không video nào rơi khỏi top 30 vì điều chỉnh
(H06 54 ngang B06 54 và trên D04 52; B06 54 ngang H06/H07/H08).

## Ngôn ngữ nói của 25 video

Anh 14 (H01, H02, H03, H04, H06, T04, T05, T07, B01, B02, B03, B04, B06, C02) · Hindi 5
(H05, H08, C03, D02 + D01 Hindi/Urdu) · Pháp 1 (T06) · Tây Ban Nha 1 (C05) ·
Tamil 1 (D04) · Không có lời nói thật 3 (H07 ảo giác Whisper, B05 nhạc, D03
nhạc). H06 tính trong nhóm Anh nhưng gần như không lời (chỉ 9 từ — tiếng whoop).
**Whisper thất bại trên 4 video tiếng Hindi** (H05, H08, C03, D02 — transcript
lặp/vô nghĩa); **1 video không đánh giá được lời nói vì không đọc được tiếng
Tamil** (D04).

## Audio — số liệu tổng hợp (đo bằng ffmpeg loudnorm + silencedetect, 30s đầu)

- **Độ lớn (LUFS):** to nhất B01 -12,09 · nhỏ nhất B02 -36,95 · T07 -36,72 ·
  T05 -31,77. Chênh lệch 25 dB giữa video to nhất và nhỏ nhất — **chuẩn hóa về
  ~-16 LUFS là bắt buộc** khi làm lại (xem Quy tắc kỹ thuật dưới đây).
- **Dead air đầu video (khoảng lặng bắt đầu ở 0,0s):** B01 1,14s · C03 0,94s +
  thêm 0,51s ở 1,42s · T05 0,69s · T04 0,67s · H06 0,60s · D02 0,51s. **6/25
  video mở đầu bằng im lặng** — lỗi phổ biến nhất trong đợt này.
- **True peak vượt 0 dBTP (clip — méo tiếng):** H05 +1,22 · H07 +0,61 · B06
  +0,62 · H08 +0,29. 4/25 video bị clip.
- **Khoảng lặng dài trong 30s đầu:** D02 có khoảng lặng 5,67s (12,69–18,37s) ·
  D03 có khoảng lặng 2,86s (17,71s) · B02 có 8 khoảng lặng 0,5–1,0s · H02 có 6
  khoảng lặng 0,5–1,3s (nhịp giữa các mục danh sách — không phải lỗi).
- **Tốc độ nói:** nhanh nhất B04 260 từ/phút (quá nhanh) · T06 212 từ/phút
  (tiếng Pháp — nhanh nhưng chấp nhận được) · T07 190 từ/phút · chậm nhất D01
  36 từ/phút (một câu nói) · H06 18 từ/phút (gần như không lời). Vùng an toàn
  150–165 từ/phút (từ báo cáo 5 video) vẫn đứng vững: các video trong vùng này
  (H04 158, C05 158) có nhịp nghe thoải mái nhất theo transcript.

## Bản quyền / watermark — những gì thấy trên frame

| Video | Watermark / nguồn gốc | Ghi chú cho bản làm lại |
|-------|----------------------|------------------------|
| H01 | TikTok UI + hashtag "#perfectfit" + facecam người thật | Dùng clip stock/AI của mình; bỏ facecam |
| H02 | Clip meme lấy lại (người thật) | Dùng clip stock/AI của mình |
| H03 | Âm thanh meme lấy lại | Dùng âm thanh tự tạo / SFX miễn phí thương mại |
| H04 | Clip TV lấy lại (Disney, Access Hollywood, Kids React) | Tuyệt đối không dùng clip gốc |
| H05 | Người thật quay bằng máy | Dùng ảnh AI của mình |
| H06 | Clip người thật + hình người dẫn overlay + bình luận của becky_vibes07 | Dùng clip của mình; bình luận tự viết |
| H07, H08 | Người thật quay bằng máy | Dùng người que |
| B01 | "豆包AI生成" (Doubao AI-generated) | Nhãn AI, không phải bản quyền — tự gắn nhãn AI tương tự |
| B02 | Watermark "OpusClip" | Tự làm phụ đề, không dùng lại video gốc |
| B03 | Clip TV/tin tức lấy lại (chương trình TODAY, bản tin Janelle Kelly) | Tuyệt đối không dùng clip gốc |
| C02 | Watermark "NVV" | Tạo nhân vật của mình |
| C03 | Watermark "@Ghiblidaysmotion" | Dùng ảnh AI của mình, phong cách riêng |
| C05 | Footage gia đình thật (trẻ em) | Tuyệt đối không dùng lại; làm hoạt hình với câu chuyện gốc |
| D02 | Watermark "Follow @happystrugle" | Quay quá trình của mình |
| T07 | Màn hình YouTube (video của người khác) + swagga.ai | Chỉ dùng màn hình của chính mình |
| D01, D03, D04, B04, B05, B06, T04, T05, T06 | Không có watermark rõ ràng | Vẫn làm lại bằng tài sản của mình |

**Không video nào trong 25 video có bản quyền "© … All Rights Reserved" như #50.**
Nhưng 15/25 video dùng lại clip/âm thanh/hình ảnh của người khác — bản làm lại
phải dùng tài sản của mình trong mọi trường hợp.

---

# Tổng hợp: các cơ chế có thể chuyển giao mạnh nhất trong 25 video này

## So sánh với 3 cơ chế từ báo cáo 5 video

| Cơ chế từ báo cáo 5 video | Trong 25 video này | Kết luận |
|---------------------------|--------------------|----------|
| **(1) Hook kép** — chữ + giọng hỏi CÙNG một câu trong 3s đầu | Xác nhận mạnh: T04 (mèo hỏi "Did you know…?"), T05 ("the world ends today"), T07 ("Don't get a part time job"), B04 (tiền đề đi muộn), C05 ("sau 3 năm con nghe được"), B06 ("It's jelly. That's a pool.") — 6/25 video có hook kép rõ rệt | **Đứng vững, mở rộng.** Nhưng đợt này còn cho thấy mặt ngược: 8/25 video KHÔNG có hook nói (H05/H08/C03/D02 transcript hỏng, H07 ảo giác, B05/D03 nhạc, H06 chỉ có whoop) mà vẫn có hook — vì **hook chỉ cần tồn tại ở ít nhất một kênh** (chữ HOẶC giọng HOẶC hình). Quy tắc tinh chỉnh: *hook phải có ở ít nhất một kênh trong 3s đầu; tốt nhất là cả hai kênh (chữ + giọng) cùng nói một câu.* |
| **(2) Visual Essay** — câu hỏi gây sốc → 2–3 beat dữ liệu → lật nhận thức → payoff | Xác nhận: T05 (tin đồn tận thế → bài báo 1960 → số liệu thật → bài học), T06 (Canada lớn → 60% hồ → kỷ băng hà), T04 là phiên bản mini (câu hỏi → 4 sự thật) | **Đứng vững.** T05 là ví dụ Visual Essay hoàn chỉnh nhất trong 30 video (cùng với #81/#80 trong báo cáo 5 video). |
| **(3) Truyện người que câm** — thẻ chữ + nhạc, không cần giọng | Xác nhận một phần: C03 là "anh em" của cơ chế này nhưng bằng tranh AI Ghibli (ảnh + giọng kể, không cần quay); C02 là hoạt hình 3D (có giọng thoại ít). Không có video người que câm thuần túy trong 25 video này | **Đứng vững, mở rộng thành "truyện tranh AI câm/có giọng kể".** C03 chứng minh tranh AI phong cách nhất quán + giọng kể cũng làm được truyện cảm xúc dài 105s. |

## 5 cơ chế MỚI rút ra từ 25 video này

### Cơ chế 4 — Danh sách đếm ngược / xếp hạng (tiết lộ một phần)
- **Ví dụ:** H02 (xếp hạng 6 khoảnh khắc Ấn Độ, mở mục 3 trước), H03 (top 5 âm
  thanh, mở mục 5 trước), H04/B03 (câu hỏi hoài niệm → chuỗi clip trả lời).
- **Cách hoạt động:** Danh sách đã mở 1 mục ở 1s nhưng còn nhiều mục trống —
  người xem ở lại để xem #1 là gì. Mỗi mục là một payoff nhỏ; #1 là payoff
  lớn, giữ đến cuối.
- **Chi phí:** dễ nhất (chữ + clip/hình + giọng). **Áp dụng ngay:** danh sách
  "Top 5…" về bất kỳ chủ đề nào (âm thanh quen thuộc, khoảnh khắc tuổi thơ,
  sự thật lạ) — chỉ cần 1 danh sách + 5 mục, không cần quay.

### Cơ chế 5 — Một hình ảnh phi lý (show, don't explain)
- **Ví dụ:** B01 (bóng bay đỏ khổng lồ), D01 (chó chihuahua cười như người),
  B06 (thạch phủ cả bể bơi, người đứng được trên nước).
- **Cách hoạt động:** Một hình ảnh không thể có thật xuất hiện ngay 1s, không
  giải thích — người xem ở lại để biết "cái gì đang xảy ra vậy?". Giọng nói (nếu
  có) chỉ giải thích tối thiểu ("It's jelly. That's a pool.").
- **Chi phí:** trung bình-khó (cần AI video giữ được vật thể phi lý nhất quán).
  **Áp dụng ngay:** 1 vật thể phi lý + 3 cảnh leo thang (nhỏ → to → người tương
  tác với nó).

### Cơ chế 6 — X vs Y / Kỳ vọng vs Thực tế
- **Ví dụ:** B04 (đi muộn: đại học vs cấp 3), D04 (ảnh cưới lãng mạn vs đời
  sống ngốc nghếch), H05 (2010 vs 2026, cùng một bức tường).
- **Cách hoạt động:** Cùng một tình huống, hai phiên bản trái ngược — sự đối lập
  là trò đùa / là cảm xúc. Người xem ở lại để xem phiên bản thứ hai.
- **Chi phí:** dễ đến trung bình (2 ảnh/cảnh đối lập + chữ + giọng).
  **Áp dụng ngay:** mọi cặp đối lập quen thuộc (trước/sau, kỳ vọng/thực tế,
  giàu/nghèo, đi làm/ở nhà).

### Cơ chế 7 — Quá trình biến đổi (tiến độ nhìn thấy được)
- **Ví dụ:** D02 (sơn gạch xám → đỏ, từng viên), H01 (chuỗi "vừa khít" —
  mỗi clip là một tiến độ nhỏ).
- **Cách hoạt động:** Người xem thấy tiến độ thay đổi từng chút — ở lại để xem
  "xong chưa, thành cái gì?". Payoff là trạng thái cuối (sân đỏ, chốt cửa vừa
  khít).
- **Chi phí:** dễ (quay quá trình thật bằng điện thoại rồi tua nhanh, hoặc ảnh
  AI từng bước). **Áp dụng ngay:** mọi quá trình có "trước → sau" rõ ràng
  (sơn, dọn, nấu, xếp, vẽ).

### Cơ chế 8 — Nhãn "POV:" (đặt người xem vào trong cảnh)
- **Ví dụ:** B05 ("POV:when you're just too thief").
- **Cách hoạt động:** Hai chữ "POV:" + một tình huống — người xem lập tức là
  nhân vật chính, không cần giới thiệu. Đây là hook chữ rẻ nhất trong 30 video.
- **Chi phí:** dễ nhất (chữ + clip/hình). **Áp dụng ngay:** "POV: …" + một tình
  huống quen thuộc (đi học muộn, bị mẹ gọi, mất điện thoại).

## 8 cơ chế tổng hợp (3 cũ + 5 mới) — thứ tự ưu tiên làm thử

| # | Cơ chế | Video gốc | Độ khó làm lại | Nên thử đầu tiên? |
|---|--------|-----------|----------------|-------------------|
| 1 | Hook kép (chữ + giọng cùng câu) | T04, T05, T07, #77, #81 | Dễ | **Có — áp dụng cho mọi video** |
| 2 | Visual Essay (câu hỏi → dữ liệu → lật lại) | T05, T06, #81, #80, #82 | Trung bình | **Có — ngách Tò mò** |
| 3 | Danh sách đếm ngược (tiết lộ một phần) | H02, H03 | Dễ | **Có — ngách Hài/Tò mò** |
| 4 | Một hình ảnh phi lý | B01, D01, B06 | Trung bình-khó | Có — ngách Bất ngờ |
| 5 | X vs Y / Kỳ vọng vs Thực tế | B04, D04, H05 | Dễ–trung bình | **Có — ngách Hài/Đời thường** |
| 6 | Quá trình biến đổi | D02, H01 | Dễ | **Có — ngách Đời thường/Hài** |
| 7 | Truyện tranh AI (người que/Ghibli/3D) | C03, C02, #50, FB-05 | Trung bình | Có — ngách Cảm xúc |
| 8 | Nhãn "POV:" | B05 | Dễ nhất | Có — mọi ngách |

## Quy tắc kỹ thuật bổ sung (từ 25 video này)

1. **Giọng vào từ 0,1s, không để dead air đầu video.** 6/25 video mở đầu bằng
   im lặng (0,5–1,14s) — đây là lỗi phổ biến nhất trong đợt này, dễ sửa nhất.
2. **Chuẩn hóa âm lượng về ~-16 LUFS, true peak ≤ -1 dBTP.** Chênh lệch 25 dB
   giữa các video gốc (-12,09 đến -36,95 LUFS); 4 video bị clip (true peak
   > 0 dBTP). Ba video có âm thanh nhỏ nhất (B02 -36,95, T07 -36,72, T05
   -31,77) gần như không nghe được trên loa ngoài.
3. **Tốc độ nói 150–165 từ/phút là vùng an toàn** (xác nhận lại từ báo cáo 5
   video). B04 nói 260 từ/phút là quá nhanh; T06 nói 212 từ/phút (tiếng Pháp)
   là nhanh nhưng chấp nhận được.
4. **Keyframe = 0 là lỗi đo trên video TikTok HEVC, không phải "video tĩnh".**
   Đừng dùng số keyframe để kết luận video tĩnh — xem contact sheet.
5. **Whisper Base thất bại trên tiếng Hindi** (4/5 video Hindi có transcript
   lặp/vô nghĩa). Video tiếng Hindi cần kiểm chứng transcript bằng tai người
   hoặc mô hình khác trước khi dùng làm bằng chứng.
6. **Độ dài: chỉ 13/95 video đã phân tích nằm trong cửa sổ 38–65s.** Trong 25
   video này: quá ngắn T04 10,1s · D04 12,2s · D01 20,1s · H05 23,5s · C02
   23,2s · B06 26,1s · H06 26,1s · B02 32,2s; quá dài T05 175,5s · C03 105,3s ·
   D02 94,7s · C05 84,1s · B03 81,3s. Quy tắc cắt/kéo vẫn đứng vững: video ngắn
   thì thêm beat, video dài thì cắt xuống ~50s (giữ 3 beat).

## Những gì KHÔNG đánh giá được trong đợt này

- **Nhạc nền và SFX cụ thể** của từng video (không nghe được audio — chỉ có
  transcript + phép đo). Mọi nhận xét về nhạc/SFX trong báo cáo này đều ghi rõ
  "chưa đánh giá được".
- **Pacing và audio sau 30s** (transcript + audio.wav chỉ có 30s đầu). Với các
  video dài (T05 175s, C03 105s, D02 95s, C05 84s, B03 81s), phần sau 30s là
  chưa đánh giá.
- **Nội dung lời nói của 4 video tiếng Hindi** (H05, H08, C03, D02 — transcript
  hỏng) và **1 video tiếng Tamil** (D04 — không đọc được tiếng Tamil). Hook nói
  của 5 video này là chưa xác định, không phải "không có".
- **Chuyển động thực** (zoom/pan, hiệu ứng) — chỉ xem frame tĩnh, không xem
  video chạy.
- **Hiệu quả thực tế** (retention, lượt xem, CTR) — không có dữ liệu Analytics
  của người tạo; điểm số là đánh giá cơ chế, không phải dự đoán lượt xem.

---

*Báo cáo hoàn thành 2026-11-15. 30/30 video trong selection đã được phân tích
sâu (5 video 85+ trong `deep-analysis-5x85-20261115.md` + 25 video trong báo cáo
này). Bước tiếp theo theo kế hoạch tuần 1: tổng hợp 5–8 công thức sản xuất
(Production Framework) từ 8 cơ chế trên, rồi mới sang tuần 2 (kịch bản).*
