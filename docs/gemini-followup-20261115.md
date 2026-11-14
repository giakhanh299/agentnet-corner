# Gemini — Câu hỏi tiếp theo: làm gì tiếp + web tải video (15/11/2026, 01:47–01:51 +07)

Cùng cuộc hội thoại "Phân tích video Facebook Faceless", tài khoản GCM Cong ty
(giakhanhgcm@gmail.com, Pro), mode Argon.
Lưu ý: Gemini từ chối câu hỏi gốc ("Tôi chỉ là một mô hình ngôn ngữ..."), sau khi
diễn đạt lại thành quy trình nghiên cứu/phân tích (học hook/nhịp/cấu trúc âm thanh,
không re-upload video người khác) thì nó trả lời đầy đủ cả 2 phần.

## Phần 1 — Kế hoạch 7 ngày (tuần 1) và bàn giao sang viết kịch bản (tuần 2)

Khung của Gemini: hoàn thành việc mổ xẻ 30 video mẫu, tránh "analysis paralysis";
toàn bộ lọc → tải → transcript → tổng hợp vừa trong 7 ngày (tuần 1), viết kịch
bản bắt đầu sáng ngày 8 (đầu tuần 2) khi đã có bộ template kịch bản.

- Bước 1, Ngày 1 (2–3h) — Lọc 30 từ 100: chấm nhanh 100 video bằng bộ lọc
  (hiểu được khi tắt tiếng/nhắm mắt + độ dài gốc 30–75s); chốt cấu trúc 8 Tò mò,
  7 Bất ngờ, 5 Kể chuyện cảm xúc, 3 Ấm áp/Cảm xúc, 4 Hài, 2 Đời thường, 1 Giải trí.
  Done: bảng tính đúng 30 dòng / 30 link đã duyệt, mỗi video có mã ID
  (vd TM_01–TM_08, BN_01–BN_07…).
- Bước 2, Ngày 2 (2–3h) — Tải, tách audio và transcript hàng loạt: chạy script tải
  cả 30 video đặt tên theo ID; dùng FFmpeg tách 30 file .wav, qua tách nhạc
  (UVR5/web) + transcript có timestamp (Groq Whisper / Subtitle Edit).
  Done: thư mục có 30 .mp4 + 30 .srt/.json + 30 cặp Vocal / Music_SFX, không link
  hỏng/thiếu.
- Bước 3, Ngày 3–4 (3–4h/ngày) — Đào sâu, Wave 1 "Retention killers" (15 video):
  8 Tò mò + 7 Bất ngờ; đo 4 chỉ số bằng Audacity/Subtitle Edit — câu hook 0–3s,
  tốc độ đọc (CPS/WPM), vị trí pause, điểm drop nhạc / chuyển BGM.
  Done: đủ dữ liệu 15 video đầu; ít nhất 10 mẫu câu hook mở đầu và 3 cấu trúc
  plot-twist (twist bắt đầu ở giây nào).
- Bước 4, Ngày 5 (3h) — Wave 2 "Emotion & Humanity" (8 video): 5 Kể chuyện cảm
  xúc + 3 Ấm áp/Cảm xúc; tập trung nhịp pause câu, điểm chuyển BGM, cấu trúc
  3 hồi trong 55–63s. Done: đủ dữ liệu 8 video cảm xúc; xác định giây chuyển
  cảm xúc chuẩn (thường ở giây 12, 28 và 45).
- Bước 5, Ngày 6 (2.5h) — Wave 3 "Humour & Everyday life" (7 video): 4 Hài +
  2 Đời thường + 1 Giải trí; tập trung cắt gọn thoại (bỏ từ thừa) và nhịp đổi
  cảnh / bong bóng chat. Done: bảng phân tích 30/30 hoàn thành 100%; hiểu quy
  tắc câu hỏi gợi bình luận (engagement bait) trong 3 giây cuối.
- Bước 6, Ngày 7 (3h) — Tổng hợp, "Production Framework": gom 30 video thành
  tài liệu chuẩn riêng: 1) ngân hàng 30 công thức hook, 2) khung kịch bản chia
  theo mốc 5 giây, 3) thư viện 15–20 file SFX lõi cắt ra hoặc tìm tương đương.
  Done: 3 template kịch bản trống (1 Tò mò, 1 Bất ngờ, 1 Cảm xúc) ghi rõ số từ
  và mốc giây, + thư mục Core_SFX (Whoosh, Boom, Riser, Ding, Pop) sẵn kéo vào
  editor.
- Bước 7, sáng ngày 8 (đầu tuần 2) — Bàn giao sang viết kịch bản: dừng hẳn việc
  tải/phân tích video mới; dùng 3 template viết loạt 7 kịch bản đầu (110–175 từ
  mỗi cái) theo lịch đăng. Done: 7 kịch bản hoàn chỉnh trong ngày 8–9, mỗi cái
  đạt 9/9 tiêu chí trong Hook Checklist 3 giây.

Tiêu chí gác cổng — chỉ sang tuần 2 khi cả 3 đều "yes": (1) nhìn chủ đề mới là
ghép ngay được ít nhất 3 kiểu hook mở đầu 3 giây từ bảng phân tích; (2) biết
chính xác kịch bản Tò mò 48 giây cần khoảng 140–160 từ và cắt ở đâu; (3) biết
chèn Boom/Whoosh ở giây nào và tắt nhạc nền ở giây nào để nhấn.

## Phần 2 — Web tải video so với yt-dlp, và vấn đề link /share/p/

Web miễn phí, không cần đăng nhập, không watermark mà Gemini liệt kê:
1. Cobalt (cobalt.tools, hoặc community instances) — YouTube Shorts, TikTok,
   Instagram, X/Twitter; Full HD 1080p, chất lượng gốc, không watermark, có chế
   độ chỉ audio (.mp3/.wav). Cách dùng: dán link vào ô giữa → chọn Auto (video)
   hoặc Audio → bấm icon ">>". Điểm mạnh: mã nguồn mở, không quảng cáo/pop-up,
   giao diện tối giản — "sạch nhất hiện tại".
2. SnapTik (snaptik.app) / TikWM (tikwm.com) — TikTok; nguồn HD gốc, không logo/
   ID TikTok nhảy trên màn hình. Cách dùng: dán link TikTok → chọn Download
   Server 01 (HD); trên TikWM chọn "Original Video No Watermark". TikWM còn trả
   file MP4 gốc không nén lại từ server TikTok + file nhạc nền riêng.
3. FDown (fdown.net) / SnapSave (snapsave.app) — Facebook Reels, Watch, video đã
   đăng; HD 720p / Full HD 1080p render lại, không watermark. Cách dùng: dán link
   Facebook chuẩn (/reel/... hoặc /videos/...) → chờ gộp audio + video → tải bản
   1080p. Lưu ý: Facebook tách stream video và audio ở 1080p, SnapSave gộp lại.
4. Publer Media Downloader (publer.io/tools/media-downloader) — đa nền tảng
   (YouTube Shorts, TikTok, FB Reels); chất lượng gốc, không watermark. Cách dùng:
   dán link vào tool miễn phí của Publer → Download. Điểm mạnh: tool của công ty
   SaaS uy tín nên không quảng cáo/redirect độc hại.

So sánh trực tiếp (yt-dlp trên VPS vs web): tốc độ tải hàng loạt 30 video —
yt-dlp "không đối thủ": một lệnh `yt-dlp -a 30_links.txt` tải cả 30 và tự đặt tên
trong 1–2 phút, web cần 30 lần copy-paste/tải/đổi tên thủ công (25–30 phút).
Metadata phục vụ phân tích — yt-dlp mạnh hơn hẳn: cờ `--write-info-json
--write-subs` kéo cả tiêu đề, ngày đăng, view, like, độ dài chính xác vào bảng
tính; web chỉ trả file .mp4 nên phải nhập tay. Vượt tường lửa TikTok/Facebook —
đôi khi IP datacenter của VPS bị Facebook/TikTok chặn cứng hoặc cần `--cookies`;
web như SnapTik/SnapSave linh hoạt hơn cho trường hợp lẻ vì backend có proxy
dân cư xoay vòng. Tiện cho video lẻ — yt-dlp cần mở terminal/SSH vào VPS rồi
kéo file về máy cá nhân để xem trong Audacity; web tải thẳng về máy cá nhân
trong 5 giây khi đang lướt thấy video hay. Kết luận: dùng yt-dlp cho 90% công
việc — Bước 2 (Ngày 2), khi đã chốt danh sách 30 link (23 Shorts + 7 TikTok
trong file .txt), một lệnh tải video + .info.json hàng loạt và tự tách .wav
bằng FFmpeg. Dùng web cho 10% — khi lướt/tìm trên máy cá nhân thấy thêm 1–2
video, hoặc khi yt-dlp bị chặn ở link cụ thể.

4 link Facebook /share/p/ bị lỗi (1DxY4V3H7t, 1EyCuKvnxD, 19jdovvPvH,
1EqozQFzGi): Gemini nói KHÔNG web bên thứ ba nào tự giải mã được link /share/p/
nếu bài đăng nằm sau tường đăng nhập Facebook. Vì sao fsave.net (và hầu hết web
tải) lỗi: /share/p/<hash>/ là "opaque share link" mới của Meta, giấu ID thật;
"/p/" là Post (bài text/ảnh hoặc bài được share lại), khác /share/v/ hay
/share/r/; khi server (FSave, hoặc VPS không cookies) mở link, Facebook trả về
trang bắt đăng nhập (facebook.com/login/?next=…) hoặc bài gốc thực ra không phải
file video (bài nhiều ảnh/text hoặc bài trong group). Cách sửa: (Cách 1 — nhanh
nhất, qua mbasic/canonical URL) dán từng link vào trình duyệt đã đăng nhập
Facebook; kiểm tra trước nó có thực là video hay chỉ là bài ảnh/text; nếu là
video, chuột phải vào khung video → "Show video URL" để lấy link canonical
(vd facebook.com/watch/?v=123456… hoặc facebook.com/reel/123456…), rồi dán link
ID số đó vào SnapSave.app, FDown.net hoặc yt-dlp là tải được ngay. (Cách 2 —
yt-dlp + cookies trình duyệt, nếu bài bị hạn chế/nhóm riêng) xuất cookies từ
trình duyệt đã đăng nhập (cookies.txt) và chạy
`yt-dlp --cookies cookies.txt "https://www.facebook.com/share/p/1DxY4V3H7t/"`.

Trang/form nên TRÁNH: trang bắt cài extension rác hoặc tải file .exe/.apk lạ
(vd bản nhái SaveFrom / Y2Mate); nhiều trang đổi domain liên tục (.guru, .biz,
.cc) và ở cú bấm Download đầu tiên mở tab mới tự tải file kiểu Video_HD_Setup.exe,
hoặc ép "Allow Notifications" — nếu cho phép, trình duyệt bị spam quảng cáo.
Quy tắc an toàn: luôn dùng trình duyệt có chặn quảng cáo (Brave hoặc uBlock
Origin) khi dùng web tải. Tránh cả web nén lại audio xuống chất lượng thấp
(64kbps mono): một số web tải YouTube Shorts/TikTok rẻ tiền hạ chất lượng âm
thanh, phá hỏng phân tích audio; luôn kiểm tra dung lượng file — quy tắc của
Gemini là Shorts 45–60s chuẩn 1080p + audio 128kbps phải là file đủ lớn, không
phải file nhỏ đáng ngờ.
