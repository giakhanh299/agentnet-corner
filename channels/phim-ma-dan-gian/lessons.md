# Bài Học Thực Chiến Series *Phim Ma Dân Gian Việt Nam* (`lessons.md`)

> Muse Biên Kịch (`script_draft`) và Muse Chính (`script_rebuttal`) đọc file này trước khi làm Tập 11+ để mỗi lô sau đều tốt hơn lô trước.

## 1. Nhịp lời dẫn & chia shot
- **Chia 11–12 shot ngắn (`4–6s/shot`, tổng `60–70s`)** mượt và hút hơn hẳn kiểu 5 cảnh dài `15–20s`.
- **Đơn vị tốc độ giọng `Góc Nhỏ Phố Núi`:** tính theo **TỪ** (~`2.3 từ/giây`, không phải ký tự). Shot `5s` với `vo_at=0.6` chỉ nên viết **tối đa 8–9 từ**; câu 10 từ bắt buộc tăng `duration_s` lên `6s` và đặt `vo_at=0.5` để không cắt chữ cuối (đã bắt được lỗi này ở `ep02`, `ep03`, `ep04`, `ep08` cảnh 2).
- **Hook 3 giây đầu:** từ khóa gây tò mò phải rơi ngay vào **2 giây đầu của Shot 1** (`vo_at: 0.0` hoặc `<= 0.5`).
- **Phụ đề `.ass`:** `studio/assemble_episode.py` đã tách câu dài thành từng cụm tối đa 12 từ theo tỷ lệ thời gian — không bao giờ bị cắt dòng.

## 2. Giọng đọc & Chính tả tiếng Việt
- **Bắt buộc gõ tiếng Việt có dấu đầy đủ 100%** ở mọi trường (`title`, `publish_title`, `cover_title`, `cover_hook`, `description`, `voiceover`). Không bao giờ nộp tiếng Việt không dấu (rút kinh nghiệm từ `cd6820ff` ở `ep05`/`06`/`07`/`09`).
- **Rủi ro phát âm giọng Phố Núi:** các từ dễ đọc trệch (`giò → dò`, `chài → trải`, `hong áo → hơ áo`, `kéo kẹt → kẽo kẹt`) cần kiểm tra trước khi dựng.

## 3. Mỹ thuật & Kiểm soát hình ảnh (`RealVisXL V5.0 Lightning` / Muse)
- **Chống ảnh trắng đen:** luôn thêm `Color film still, ` đầu prompt, tránh cụm `black-and-white` (đổi thành `checkered`), và đưa `black and white, monochrome, grayscale` vào `negative_prompt`.
- **Giới hạn 77 token CLIP:** đưa ánh sáng (`dark midnight`, `warm amber oil lamp`, `cold blue moonlight`) và nhân vật Việt Nam (`Vietnamese ... dark brown eyes`) lên **40 từ đầu** của `image_prompt` để không bị cắt mất ngữ cảnh (tránh lỗi mắt xanh ở `ep08` cảnh 7 và lỗi ban ngày ở `ep01` cảnh 2).
- **Luôn soi `storyboard.png` trước khi dựng** và dùng `--only <id>` vẽ lại duy nhất tấm lỗi thay vì vẽ lại cả tập.
- **Chọn `cover_image` ăn khớp `cover_title`:** ảnh bìa phải đúng hình ảnh được nhắc trên chữ bìa (ví dụ `TƯỢNG ĐÁ QUAY ĐẦU` dùng `scene_08.png` cận tượng đá ướt sương).

## 4. Âm thanh & SFX
- **Không để `horror_stinger` / `human_eerie` đè lên câu thoại hoặc giọng ma** — đẩy stinger về cuối shot (`dur - 1.2s`), hạ tiếng nền dưới `-24 dB` đến `-28 dB`.
- **Kho SFX hiện có 39 file sạch bản quyền (`assets/sfx/`):** vẫn còn thiếu nhóm **`fire_lamp`** (đèn dầu/lửa lách tách) và **`night_creatures`** (ếch/dế/gà gáy mới đang dùng fallback `crickets.ogg`) — ưu tiên bổ sung 2 nhóm này ở đợt săn SFX tiếp theo.

## 5. Năng lực thật của đội Muse
- Muse trên Hub cực mạnh ở: **Săn đề tài có kiểm chứng văn hóa (`content_scout`)**, **Biên kịch 12 shot (`script_draft`)**, **Phản biện bắt lỗi thật (`script_rebuttal` – `355c4b87`)**, và **Săn link SFX Freesound/Mixkit (`sfx_candidates`)**.
- Trình duyệt Muse bị chặn upload file local lên `catbox.moe`/`litterbox` → kết hợp **GPU RTX 5060 Ti local (`studio/image_gen.py` + `studio/assemble_episode.py` + `studio/thumbnail.py`)** cho khâu vẽ ảnh 9:16 và dựng hậu kỳ là công thức ổn định, không nghẽn, không 503 và đủ tốc độ **10+ video/giờ**.
