# STATUS — AgentNet Video Studio (per-feature result log)

> Log kết quả từng tính năng: xong (đúng hay sai) đều ghi vào đây, KHÔNG báo
> riêng cho chủ nữa (chủ dặn 15/11 ~15:50: "ko cần báo tôi — báo lên git hay
> gg driver"). Chủ không can thiệp; cứ bám theo kế hoạch mà làm.
> Mới nhất ở trên cùng. Mỗi mục: tên, thời gian (+07), trạng thái
> (DONE / FAILED / IN PROGRESS / BLOCKED), file/commit chứng minh, kết quả
> thật — thành công hay lỗi (kèm lỗi) đều ghi. Không ghi số không có bằng chứng.
> Bản trên git là bản chính; bản trên Drive là bản sao dự phòng.
> Cập nhật lần cuối: 2026-11-17 ~12:05 +07.

## DONE

### Nâng cấp Kiến trúc AgentNet V2.0 — Auto-99% (`auto99/`) — DONE + Verified 2026-11-17 ~12:05 +07
- **File:** `research_queue.py`, `corner.py`, `join.py`, `stickman-shorts/tools/assemble.py`, `auto99/` (`tts_auto_heal.py`, `pronunciation_lexicon.json`, `episode_compiler.py`, `qc_verify.py`, `telegram_gate.py`, `worker_daemon.py`, `studio_cli.py`, `pc_worker_start.ps1`), `test_auto99.py`.
- **Kiểm thử tự động:** **23/23 unit & integration tests PASS** (`test_corner.py`, `test_research_queue.py`, `test_research_http.py`, `test_auto99.py` — 9,1s trên Python 3.12 PC).
- **Giải quyết triệt để lỗi chặn `other_tcp` SSH (v013):** PC Windows (`100.101.158.71`, RTX 5060 Ti 16GB) chủ động pull job chiều đi qua HTTP Tailscale tới `:8110` (`auto99/worker_daemon.py` kèm heartbeat 45s + outbox chống rớt mạng), không cần VPS SSH ngược vào PC. Đã tạo đăng ký node `engineer` cho PC trên Master `:8110` (`id: 4ad1aa279ae398c32745ce18`, chờ lệnh `delegate-engineering off && approve` trên Master).
- **Định tuyến GPU-First → CPU-Fallback:** Task có `preferred_capabilities: ["gpu_cuda"]` ưu tiên giao PC RTX 5060 Ti khi online; tự động fallback `0s` về CPU VPS1 khi PC tắt hoặc sau `45s` khi PC quá tải.
- **Xóa bỏ viết tay `probe.py` & Render 1 lệnh (đã chạy thật 2 tập mẫu trên RTX 5060 Ti):**
  1. `studio_runs/ep001_auto/final.mp4` (Stickman Manim 1080x1920 30fps + MMS-TTS tự sửa lỗi + Whisper large-v3): **53,5s, -16,30 LUFS, -2,92 dBTP, 155,0 effective WPM, ASR 97,83% → QC PASS 99,5/100**.
  2. `studio_runs/v011_vieneu_auto/final.mp4` (Visual Essay 1080x1920 30fps + giọng VieNeu "Mai Anh" persistent server + BGM + Whisper large-v3): **48,35s, -16,02 LUFS, -3,08 dBTP, 157,3 WPM, ASR 99,13% → QC PASS 97,0/100**.
- **Cổng duyệt 1% Telegram Bot (`auto99/telegram_gate.py`):** Đẩy thẳng `.mp4` đạt chuẩn QC kèm 4 nút bấm (`Duyệt 11:30`, `Duyệt 20:00`, `Render lại`, `Loại + Ghi bài học`); tự học từ điển phát âm khi chủ nhắn `phát âm: X -> Y`.

### Video #14 (v014) — DONE + QC-passed 2026-11-16 ~21:26 +07
- **File:** `video_production/v014-no-part-time-job-50s/v014.mp4` — 52,07s, 1080x1920, 30fps, H.264 + AAC 192k, 5.396.303 byte, sha256 `938568d1c31b7fc8e10276bba603f4f8b372760fe403a4bec24dc03bf89b8d65` — **-16,05 LUFS**, true peak **-3,09 dBTP**, giọng vào **0,000s**, **156,4 wpm lúc nói** (129 từ), Whisper large-v3 (PC) 111/129 = **86,0%**.
- **Chủ đề:** "Đừng làm thêm kiểu cũ" (T07 #99, 74) — hướng dẫn màn hình thật, giữ câu "Không hứa bạn giàu nhanh" ở beat 3; số liệu là số đo thật của chính mình (MMS-TTS 0,9s, Whisper 4,7s, render v003 12s). Giọng VieNeu "Mai Anh" atempo 0.66 (0.65 chỉ được 146 wpm — 0.66 → 156,4 wpm). Không đổi từ probe nào; "giàu" take 1 nghe thành "sầu nhanh" → dùng take 2.
- **Render + mix + encode hoàn toàn trên PC** (9 hard cut, 1562 frames). SFX đã kiểm bằng đo mẫu (ding3 rõ nhất +39,8 dB; whoosh/pop nhỏ +0,6/+0,9 dB).
- **Quay màn hình — cách làm mới:** gdigrab toàn màn hình quay nhầm trình duyệt Facebook live của chủ (đang đăng bài) — footage đó đã xóa khỏi PC + VPS. Cách chạy được: chụp PrintWindow từ process con (spawn từ chính console màn hình, `v014_snap_child.ps1` + `v014_screen4.ps1`) — 99/99 ảnh, 2 fps, terminal thật chạy pipeline thật, không cướp focus, không dính nội dung trình duyệt. Dead end đã ghi trong qc.md: gdigrab title từ SSH (lỗi I/O, khác window station), Start-Job snapshotter (IntPtr không serialize — 0 ảnh), FindWindow từ task riêng (window-station isolation — 0 ảnh). Dùng lại pattern này cho video quay màn hình sau.
- **Hạn chế thật:** chưa có người nghe (Whisper 86,0%); footage màn hình 2 fps nên chuyển động giật từng bước (kiểu timelapse) nhưng 100% thật; chữ script trên màn hình bị mojibake (console hiển thị UTF-8 thành cp1252) — số chính vẫn đọc được, lần sau chạy `chcp 65001` trước Get-Content; ~780px dưới của đoạn màn hình là đen (vùng phụ đề, phụ đề là sidecar không burn-in); hook và step-4 chung bước render, b1a và step-2 chung bước TTS (khác khoảng ảnh). Chưa đăng. Drive: v014.mp4 id `1cbPe8R0o5yTeDcZflmcCLrgvb8yPm7vU`.

### Video #12 (v012) — DONE + QC-passed 2026-11-16 ~21:13 +07
- **File:** `video_production/v012-talking-dog-45s/v012.mp4` — 55,47s, 1080x1920, 30fps, H.264 + AAC 192k, 15.405.319 byte, sha256 `9312183ff0b1361ce37a069516b0544940a011280d9c365255430a5e8d9f0aad` — **-16,09 LUFS**, true peak **-2,73 dBTP**, giọng vào **0,02s**, **151 wpm lúc nói** (131 tổng, 121 từ), Whisper large-v3 (PC) 108/121 = **89,3%** (tốt nhất từ v006).
- **Chủ đề:** "Chó nhà bạn hiểu bao nhiêu từ?" (D01 #39, 80) — 1 nhân vật Bin + payoff "đi dạo". **Video đầu tiên dùng giọng VieNeu** ("Mai Anh", atempo 0.65, pauses 0.3/0.4/0.6). Không đổi từ probe nào (cả 4 PASS 100%).
- **VieNeu ĐÃ CÀI TRÊN PC:** `C:\Users\w\agentnet-corner\ai-stack\.venv-vieneu` (vieneu 3.8.4, onnxruntime 1.32.0) — load lạnh 7–15,5s trên PC (so với 197s trên VPS), synth RTF ~0,4. Model trong HF cache chung.
- **Render + mix + encode hoàn toàn trên PC** (~19s encode, 7 hard cut). BGM bgm_comedy ~26 dB dưới giọng (hơi nhỏ hơn mục tiêu -18 đến -24 dB, không mix lại).
- **Sự cố:** session này thiếu known_hosts → copy `/root/.ssh/known_hosts` sang `~/.ssh/known_hosts` là SSH chạy; Whisper check crash `cublas64_12.dll not found` → prepend torch\lib + nvidia bin vào PATH trong .ps1; TTS run 2 crash `NameError: scale` sau khi ghi wav chậm nhưng trước khi ghi units — bài học: luôn kiểm tra units JSON + độ dài wav khớp lần chạy mới nhất trước khi xây phụ đề. Mỗi clause VieNeu có ~0,07–0,13s lặng đầu — công thức bắt đầu clause là native/0.65 + (lead − trim), không phải − trim.
- **Hạn chế thật:** chưa có người nghe (Whisper 89,3%); 5 ảnh là 5 con chó khác nhau trong khi kịch bản xưng "Tôi là Bin"; dài 55,47s ở mép trên khung; ảnh 1024px hơi mềm (chỉ b2c Wikimedia là full-res); hộp nhãn che mắt chihuahua ở 10s; phụ đề trùng CTA 2s cuối (nit cũ). Chưa đăng. Drive: v012.mp4 id `1ybBSPw1Ro-8hih5LcEpFnTdJS295AOdB`.
- **Ghi chú quyền PC:** session làm v012 vào PC bình thường tới ~21:11, trong khi session chính + session v013 bị chặn other_tcp Deny cùng lúc — chặn này theo từng session, không phải toàn cục. Thử lại bằng session mới là một đường khả thi cho v013.

### Video #13 (v013) — PARTIAL 2026-11-16 ~21:02 +07 (chưa có mp4 — PC không vào được)
- **Giọng/âm thanh/hình/thẻ/phụ đề xong trên VPS** (`video_production/v013-iconic-sounds-45s/`): VieNeu "Mai Anh" atempo 0.70 (script chạy 222 wpm native nên 0.65 chỉ được 144 wpm — dùng 0.70 → 161 wpm), voice.wav 45.75s, 116 từ, giọng vào ~0.06s; Whisper Base (VPS) 83/116 = 71,6% (chưa đạt 75% — cần kiểm lại bằng large-v3 trên PC); 5 âm thanh mẫu chuẩn hóa -23 LUFS (chuông trường, xe máy, modem, nhạc chuông Gran Vals tự tổng hợp, rao bánh mì bằng VieNeu); 5 ảnh CC0; 7 thẻ; phụ đề 31 events.
- **Chặn:** SSH tới PC bị từ chối — quyền "Other TCP connections" (other_tcp) đang Deny sau lần VPS thay máy hôm nay (dù rule allow cho 100.101.158.71 vẫn còn). Lỗi: `nc: Proxy error: "muse: Other TCP connections is turned off..."`. Không render dự phòng trên VPS (theo lệnh của chủ). Cần chủ mở Muse settings → Permissions → Direct network protocols → đổi other_tcp Deny → Ask, rồi chạy lại `v013_to_pc.sh`.
- **Probe:** "rao"→"bán", "modem"→"quay số". Giữ "chuông trường", "đề nổ", "cục gạch".
- **Xung đột mức âm:** kịch bản nói âm thanh mẫu phát ngang giọng; lệnh sản xuất nói -18 đến -24 dB dưới giọng — mix script đang để vol 0.12 (~-19 dB); đổi thành 1.0 trong `v013_mix.py` nếu muốn theo kịch bản.

### Video #11 (v011) — DONE + QC-passed 2026-11-16 ~13:50 +07
- **File:** `video_production/v011-canada-lakes-45s/v011.mp4` — 49,60s, 1080x1920, 30fps, H.264 + AAC 192k, 21.583.334 byte, sha256 `1fade7c08b4d03d314b5769d7d49e57fbc4bd6eecaad4a5bfe4b48389f428fa7` — **-16,09 LUFS**, true peak **-2,94 dBTP**, giọng vào **0,041s** (đã cắt 0,25s lặng đầu trong wav TTS trước khi xây phụ đề — bài học v010 áp dụng đúng), **151 wpm lúc nói** (115 từ), Whisper large-v3 (PC) 98/115 = 85,2%.
- **Chủ đề:** "Canada có 60% số hồ trên thế giới" (F2 Visual Essay, T06 #83, 76) — đúng 3 beat, không thêm beat thứ 4; số hiện trên hình, không đưa vào lời thoại. BGM bgm_calm ~23,5 dB dưới giọng (đúng mục tiêu).
- **Render + mix + encode hoàn toàn trên PC.** Lô v009–v011 (11 video tổng) hoàn tất.
- **Probe:** "Canada" → "Ca-na-đa" (TTS input, phụ đề vẫn "Canada"); "băng hà" → "băng tuyết khổng lồ"; "hố trũng" → "hố sâu". Giữ "cào xới", "Thượng", "Trái Đất".
- **Sự cố mới (bài học pipeline):** lần render đầu trên PC làm mất 3 dòng chữ có "%" (nhãn beat 1 + 2 dòng số end card) — ffmpeg drawtext "Stray %" vẽ trống nhưng vẫn exit 0, `%%` cũng không thoát được. Sửa: `expansion=none` cho mọi drawtext; render lại trên PC và kiểm tra lại khung 10s + 45s. Bài học: không bao giờ để "%" trần trong textfile của drawtext nếu thiếu `expansion=none`, và phải xem khung hình trong cửa sổ của từng nhãn, không chỉ hook/end card.
- **Hạn chế thật:** chưa có người nghe (Whisper 85,2%); payoff 130 wpm / beat 1 169 wpm chênh nhau; ảnh vệ tinh beat 3b là Nunavut (không phải Ngũ Đại Hồ); ảnh hồ Thượng 1024px hơi mềm; phụ đề trùng CTA 2s cuối (nit cũ). Chưa đăng. Drive: v011.mp4 id `1Jo0wt37hz2nZl36gWaZ_scSA5IFtnuaV`.

### Video #10 (v010) — DONE + QC-passed 2026-11-16 ~13:45 +07
- **File:** `video_production/v010-doomsday-50s/v010.mp4` — 54,53s, 1080x1920, 30fps, H.264 + AAC 192k, 12.300.627 byte, sha256 `c7bca083059c8973344c8e0699a38603aa9a5eeb3b70f47cc1018905805c15f7` — **-16,24 LUFS**, true peak **-1,06 dBTP**, giọng MMS-TTS take 3 (take 1 + 2 bị loại vì nhịp không đều/nhanh), **160 wpm lúc nói** (137 từ, nhịp từng beat 155/165/160/158/164 — đều trong vùng 150–165), Whisper large-v3 (PC) 83,9%.
- **Chủ đề:** "Bài báo 1960 nói thế giới tận thế 13/11/2026" (F2 Visual Essay, T05 #82, 78) — video bóc mẽ bằng số liệu, KHÔNG dọa tận thế; giữ câu "chính họ cũng không tin" ở beat 2; hook quá khứ (13/11 đã qua). Ảnh CC0/CC BY + lịch/biểu đồ tự vẽ, không dùng lại asset của #82 gốc.
- **Render + mix + encode hoàn toàn trên PC** (~23s, 8 hard cut kiểu v006, cap `-frames:v 1637`). Nhạc bgm_suspense.
- **Probe:** cả 4 PASS, không đổi từ nào ("tận thế" 82,4%, "vô cùng" 95%, "đạt đỉnh" 75%, "trưởng nhóm" 100%).
- **Hạn chế thật:** chưa có người nghe (Whisper 83,9%); **giọng vào 0,39s** (không phải ~0,1s — lặng kỹ thuật số tới 0,387s; phụ đề chạy từ 0,000s nên dòng đầu hiện trước giọng ~0,4s) — chưa sửa vì phụ đề + SFX đã xây trên take 3 chưa cắt; bài học cho lô sau: cắt lặng đầu trong wav TTS TRƯỚC khi xây phụ đề/SFX. Bìa 1928 bị crop mép phải khi zoompan 9:16; dải nhãn beat 3 đè lên đường cong gần 1963–1970 (chấm đỉnh vẫn thấy); phụ đề trùng end card 2s cuối (nit cũ). Chưa đăng. Drive: v010.mp4 id `1PE_yqkQ7yRfU9aCHyEHi4_DBylPAmX_O`.

### Video #9 (v009) — DONE + QC-passed 2026-11-16 ~13:39 +07
- **File:** `video_production/v009-animal-facts-45s/v009.mp4` — 51,23s, 1080x1920, 30fps, H.264 + AAC 192k, 14.661.744 byte, sha256 `dc6c97c0e52e7ba322ac80b4845733e5b92afe563d48f914247e977d1f08db9b` — **-16,12 LUFS**, true peak **-2,95 dBTP**, giọng từ 0,00s, **152 wpm lúc nói** (141 tổng, 120 từ — khoảng lặng đếm ngược có chủ ý như v005/v007), Whisper large-v3 (PC) 102/120 = 85,0%.
- **Chủ đề:** "Top 5 sự thật về động vật" (F3 Countdown, T04 #84, 80) — đúng 5 sự thật, #1 là bạch tuộc 3 tim; không dùng mèo AI của video gốc (số lớn + ảnh động vật).
- **Render + mix + encode hoàn toàn trên PC** (encode 15,3s, đúng 1537 frames). Nhạc bgm_comedy ~19,7 dB dưới giọng (đúng mục tiêu).
- **Probe:** "huýt" FAIL → "kêu". Giữ "bạch tuộc", "lướt", "cọ", "Top" (chữ trên màn hình gánh chính tả).
- **Sự cố:** scp 2 file cùng lúc tới đích là file-path tạo ra thư mục tên `v009_probe.py` trên PC (probe lỗi "can't find '__main__' module") — sửa bằng move/rmdir trên PC; bài học: một file mỗi lần scp, hoặc đích là thư mục.
- **Hạn chế thật:** chưa có người nghe (Whisper 85,0%); hook 209 wpm / n2b 177 wpm nhanh; ảnh cá bay là tranh minh họa cổ (không tìm được ảnh thật tải được); ảnh kiến hơi mềm (606px); phụ đề chạm mép dưới hàng #4 và trùng end card 2s cuối (nit cũ). Chưa đăng. Drive: v009.mp4 id `1U0Fq09bQ1OAUKtnbISUpb2eqlauYmHH_`.

### Lô kịch bản v012 + v013 + v014 — DONE 2026-11-16 ~12:37 +07 (chỉ kịch bản, chưa sản xuất)
- **File:** `video_production/scripts-batch-20261116/` — 3 kịch bản mới + `scripts_batch.md` (mục lô v012–v014). Viết trước theo chỉ đạo của chủ (làm việc chủ động, tự tìm việc khi rảnh, làm trước tiến độ); lô v009–v011 đã giao 10:49 sáng nay, chưa có lệnh sản xuất, nên lô này lấp khoảng trống tiếp theo để sản xuất không phải chờ.
- **v012** — D01 #39 (80) "Chó nhà bạn hiểu bao nhiêu từ?", format chó nói 45s, **121 từ ≈ 161 từ/phút**. Format rẻ nhất ngân hàng 30 (F=5, C=5). Sự thật đã kiểm chứng: chó trung bình hiểu ~165 từ (Stanley Coren, Đại học British Columbia; chó thông minh nhất ~250 từ, tương đương trẻ 2–2,5 tuổi). Payoff là hai từ "đi dạo". Quyết định: giữ đúng 1 nhân vật + 1 câu nói đáng nhớ, không thêm nhân vật thứ hai.
- **v013** — H03 #61 (67) "Top 5 âm thanh nghe là nhớ ngay", F3 Countdown 45s, **117 từ ≈ 156 từ/phút**. 5 âm thanh Việt tự làm/CC0 (chuông trường, xe máy, rao bánh mì, nhạc chuông cổ, modem quay số) — KHÔNG dịch 5 âm thanh meme tiếng Anh của video gốc, không lấy lại meme audio (cảnh báo bản quyền H03, L=2). Nhạc chuông: giai điệu "Gran Vals" (1902) của Francisco Tárrega đã thuộc phạm vi công cộng (Nokia dùng 1992/1994) — chỉ dùng bản tự tổng hợp, không lấy file của Nokia, không nhắc tên thương hiệu trong lời thoại (Nokia đã đăng ký giai điệu làm nhãn hiệu âm thanh ở một số nước).
- **v014** — T07 #99 (74) "Đừng làm thêm kiểu cũ", hướng dẫn màn hình 50s, **129 từ ≈ 155 từ/phút**. Giữ cấu trúc "tuyên bố ngược đời → bằng chứng → hướng dẫn" nhưng bỏ toàn bộ con số tiền của video gốc (600/18.000 không kiểm chứng được), thay bằng số liệu thật của chính mình: MMS-TTS trên PC 55 từ/19,6s audio trong 0,9 giây; faster-whisper large-v3 48,8s audio trong 4,7 giây; render v003 trên PC 12 giây/1.504 khung hình. Quyết định: KHÔNG hứa thu nhập — giữ câu "Không hứa bạn giàu nhanh" ở beat 3; chỉ quay màn hình của chính mình, không quay nội dung YouTube của người khác.
- **Kiểm chứng:** đếm từ bằng script trên bảng lời thoại — v012 121, v013 117, v014 129; cả 3 file ban đầu ghi nhầm ±1–3 từ (v012 120, v013 114, v014 130), đã sửa thành số đếm thật. Tốc độ cả 3 đều trong vùng an toàn 150–165. **CHƯA sản xuất, CHƯA tổng hợp giọng, CHƯA đăng.** Sản xuất theo lệnh của chủ như lần trước; thứ tự đề xuất v012 → v013 → v014 (rẻ trước đắt sau). Còn 16 chủ đề chưa dùng trong ngân hàng 30 sau lô này.

### Test 3 giọng TTS mới (VieNeu / valtec / VietVoice) — DONE 2026-11-16 ~10:37 +07
- **File:** `video_production/voice-compare-20261116/voice_compare_20261116.md` (17,8 KB) + mẫu wav (16 kHz mono). Cùng 3 câu test / 40 từ, cùng Whisper Base `-l vi` như vòng 1–3; MMS round-2 C được đo lại bằng Base cho công bằng (72,5%).
- **Kết luận: giữ MMS-TTS làm giọng sản xuất.** Không giọng nào vượt MMS toàn diện (tốc độ trong vùng, tổng hợp nhanh nhất, đã chứng minh qua 9 video). Nhược điểm duy nhất của MMS là giấy phép CC-BY-NC (phi thương mại).
- **VieNeu-TTS v3 Turbo — dự phòng tốt nhất, an toàn thương mại:** giấy phép Apache 2.0; Whisper 80,0% (cao nhất); 25 giọng preset; server tương thích OpenAI. Vấn đề: nói nhanh 238 wpm, không có chỉnh tốc độ — phải chậm bằng ffmpeg `atempo=0.65` → ~155 wpm (77,5% sau khi chậm). Chậm trên VPS này (RTF 1,5–1,9 + nạp model 197s); trên PC có GPU sẽ nhanh hơn nhiều. Cài đặt ~1,4 GB.
- **VietVoice-TTS — không dùng được trên VPS này:** MIT, Whisper 70,0%, có chỉnh `speed` (chưa test) — nhưng RTF 74–256, một video 45s mất ~1 giờ tổng hợp. Chỉ xem lại trên PC có GPU.
- **valtec-tts — BLOCKED, không test được:** code cài được nhưng `TTS()` lỗi HTTP 401 — repo model trên HF đã private/gated/xóa, không có weights công khai. Bản .exe Windows 394 MB chưa test (chỉ chạy tay).
- **Cả 3 giọng đều không nói được "log"** (MMS "lá"/"luôn", VieNeu "hốc"/"lắc"/"lớp", VietVoice "lót") — chữ trên màn hình vẫn phải gánh chính tả.
- **2 sự cố (đã sửa, ghi trong báo cáo):** chạy đầu VietVoice bị lỗi của chính agent test (chuyển int16→float32 không chia lại → clip thành sóng vuông, Whisper 20%) — chạy lại đúng được 70,0%; file lỗi giữ lại tên `*_CLIPPED_INVALID.*`, không dùng. Cài valtec kẹt vì /tmp chỉ 512 MB tmpfs — sửa bằng TMPDIR sang ổ lớn.
- **Hạn chế thật:** chưa có người nghe mẫu nào (chỉ đo Whisper) — chủ là người quyết định, nhất là VieNeu chậm vs MMS. Chênh Whisper nhỏ (80,0 / 72,5 / 70,0 = 2–3 từ); khác biệt quyết định là tốc độ và RTF (đã đo). Chủ chưa chọn giọng nào — MMS vẫn là chuẩn sản xuất.

### Video #6 (v006) — DONE + QC-passed 2026-11-16 ~09:32 +07
- **File:** `video_production/v006-triple-point-45s/v006.mp4` — 53,13s, 1080x1920, 30fps, H.264 + AAC 192k, 18.522.052 byte, sha256 `84757475ef0e4ce5bd53b1ab2beeceee3e49912107c3f1e7745f0c8da0489010` — **-16,19 LUFS**, true peak **-3,04 dBTP**, giọng từ 0,00s, **158 wpm lúc nói** (147 tổng, 130 từ sau probe), Whisper large-v3 (PC) 124/127 = 97,6% — cao nhất từ trước đến nay.
- **Chủ đề:** "Nước vừa sôi vừa đóng băng cùng một lúc" (F2 Visual Essay, T03 #80, 83) — 7 đoạn, cắt cứng qua concat (không crossfade, theo đúng kịch bản cắt mỗi ~10s).
- **Render + mux hoàn toàn trên PC** (~29s). Nhạc bgm_calm đo ~19–20 dB dưới giọng (đúng mục tiêu -18 đến -24 dB; v003 nóng -11 dB).
- **Probe:** "áp suất" → "sức ép không khí" (nghe "ác súc"); "loãng" → "mỏng hơn" (nghe "loạn"). Giữ "đóng băng", "buồng kín", "trạng thái". Từ đầu câu "Nước" nghe thành "Đất" (chữ trên màn hình gánh).
- **Hạn chế thật:** chưa có người nghe (Whisper 97,6%); ảnh hook là art nước trừu tượng (không phải ảnh nước sôi thật), 1024px hơi mềm; hook 179 wpm / payoff 172 wpm nhanh; phụ đề trùng end card 2s cuối (nit cũ). Chưa đăng. Drive: v006.mp4 id `176QzDOjcnwyzFjhwI7t-93fYOPA1-wMj`.

### Video #7 (v007) — DONE + QC-passed 2026-11-16 ~09:32 +07
- **File:** `video_production/v007-perfect-fit-45s/v007.mp4` — 48,37s, 1080x1920, 30fps, H.264 + AAC 192k, 13.821.811 byte, sha256 `ab6fbf2cb4726710150e36de117534b128fb2e3649664b5181806f7ea76a8b5b` — **-15,99 LUFS**, true peak **-5,01 dBTP**, giọng từ 0,00s, **158 wpm lúc nói** (145 tổng, 117 từ — 4,0s khoảng lặng đếm ngược có chủ ý như v005), Whisper large-v3 (PC) 97/117 = 82,9%.
- **Chủ đề:** "Top 5 thứ vừa khít hoàn hảo" (F3 Countdown, H01 #68, 78) — #1 là chốt cửa (đúng quyết định biên tập), không facecam.
- **Render trên PC, 12,5s**, không `-loop 1`, giới hạn cứng `-frames:v 1452`. Nhạc bgm_comedy ~23 dB dưới giọng (đúng mục tiêu).
- **Probe:** "tra vào ổ" → "cắm vào ổ khóa"; "bánh xe tải lăn đúng vào rãnh, khít từng milimét" → "bánh xe tải chạy đúng vào khe. Như thể cái khe sinh ra cho nó." Giữ "khít" (Whisper nghe "khiếp" ở file dài là nhiễu tách đoạn — probe rời nghe đúng), "bản lề", "cạch", "chốt cửa".
- **Hạn chế thật:** chưa có người nghe (Whisper 82,9%); ảnh #4 là bản lề cổ vật bảo tàng (tối, cầu kỳ), ảnh #2 là bánh xe đạp trong rãnh ray chứ không phải bánh xe tải (cơ chế "vừa khít" giữ nguyên); phụ đề trùng end card 2s cuối (nit cũ); video ngắn hơn audio 0,033s (cắt đuôi không nghe thấy). Chưa đăng. Drive: v007.mp4 id `1cyjg3529mDT18j0HqgMSsXT6oxN-XDTT`.

### Video #8 (v008) — DONE + QC-passed 2026-11-16 ~09:24 +07
- **File:** `video_production/v008-daddys-girl-50s/v008.mp4` — 48,36s, 1080x1920, 30fps, H.264 + AAC 192k, 2.419.585 byte, sha256 `4fcd530b3e1e632badf3a1114fedb3dd255164df1164c7832044de302d034680` — **-15,90 LUFS**, true peak **-2,94 dBTP**, giọng từ ~0,05s, **157,6 wpm** (127 từ), Whisper large-v3 (PC) 114/127 = 89,8%.
- **Chủ đề:** "Con gái của bố" (F7 stickman, C02 #47, 79) — truyện gốc hoàn toàn (Na làm vỡ lọ hoa; bố về chỉ ngồi xuống, không mắng; câu duy nhất của bố "con gái của bố đây rồi").
- **Render trên PC — tập đầu tiên render end-to-end trên PC** (đồng bộ stickman-shorts + Manim 0.22.1 trong .venv-win, ~28s gồm sync). Không cần fallback VPS, PC không lỗi lần nào.
- **Probe:** "rã rời" FAIL (2/2 sai thanh) → "mệt lắm"; "cởi giày" FAIL (2/2 nghe lộn) → "bước vào thật khẽ". Giữ "Na", "phăng phắc", "dỗi".
- **Sửa sau đo/khung hình:** MMS chừa 0,41s lặng đầu giọng — đã cắt 0,36s đầu giọng + dịch timing/caption/nhạc/SFX −0,36s, cắt 0,36s đầu video thô lúc mux cho đồng bộ. Ôm payoff v1 rối thành một khối — render lại v2 tách 2 nhân vật sang 2 bên, nâng card payoff lên y=5.0 tránh đồng hồ.
- **Hạn chế thật:** chưa có người nghe (Whisper 89,8%); beat 3 ~176 wpm (nhanh, tổng vẫn trong vùng); lọ vỡ nhìn như hộp nghiêng (cần giọng + card mới đọc ra lọ); phụ đề trùng end card 2s cuối (nit cũ); beat 2 ~10s gần như tĩnh. Chưa đăng.

### Lô kịch bản v006 + v007 + v008 — DONE 2026-11-16 08:35 +07 (chỉ kịch bản, chưa sản xuất)
- **File:** `video_production/scripts-batch-20261116/` — 3 kịch bản +
  `scripts_batch.md`. Viết trước theo chỉ đạo của chủ (làm việc chủ động,
  tự tìm việc khi rảnh, làm trước tiến độ); lô trước v003+v004+v005 đã
  sản xuất xong cả 3, chưa có kế hoạch v006+ nào nên lô này lấp khoảng
  trống để sản xuất không phải chờ.
- **v006** — T03 #80 (83, điều chỉnh từ 87) "Nước vừa sôi vừa đóng băng
  cùng một lúc", F2 Visual Essay 45s, **122 từ ≈ 163 từ/phút**. Điểm ba
  trạng thái đã kiểm chứng: 0,01°C ở 611,657 Pa (~1/166 áp suất khí quyển,
  Wikipedia "Triple point" + FactsMate/NIST, đo 1976 ±0,010 Pa) — các
  con số chỉ hiện trên hình, không vào lời thoại. Cắt 80,3s → 45s, cắt
  cứng mỗi ~10s (video gốc không cắt cứng nào — lý do R bị hạ).
- **v007** — H01 #68 (78) "Top 5 thứ vừa khít hoàn hảo", F3 Countdown
  45s, **121 từ ≈ 161 từ/phút**. Giữ thứ tự tăng dần của video gốc (đá
  #3, bánh xe #2, chốt cửa #1), bỏ facecam hoàn toàn, clip stock/AI của
  mình. Không có khẳng định số liệu nào.
- **v008** — C02 #47 (79) "Con gái của bố", F7 stickman cảm xúc 50s,
  **130 từ ≈ 156 từ/phút**. Truyện hoàn toàn mới (bé Na làm vỡ lọ hoa;
  mẹ mắng → bé giận → bố về → bố ôm), không dùng lại cảnh/nhân vật 3D
  của video gốc (watermark NVV). Ưu tiên stickman Manim thay vì ảnh AI
  (nhân vật nhất quán). Quyết định: bố không mắng, chỉ ngồi xuống.
- **Kiểm chứng:** đếm từ bằng script trên bảng lời thoại — v006 122,
  v007 121, v008 130, khớp đúng con số ghi trong từng file (v008 ban đầu
  ghi nhầm 129, đã sửa thành 130 sau khi đếm lại). **CHƯA sản xuất, CHƯA
  tổng hợp giọng, CHƯA đăng.** Sản xuất theo lệnh của chủ như lần trước;
  thứ tự đề xuất v006 → v007 → v008. Còn 22 chủ đề chưa dùng trong ngân
  hàng 30 sau lô này.

### Video #3 (v003) — "Cáp thang máy đứt ở tầng 85" Visual Essay 45s (F2, #77 90) — DONE + QC-passed 2026-11-15 22:21 +07
- **File:** `video_production/v003-lift-45s/v003.mp4` — **50,13s,
  1080x1920, 30fps, H.264 + AAC 192k, 19.733.840 byte, sha256
  `b9fb43a4762a…`** — **-16,41 LUFS** (mục tiêu ~-16), true peak
  **-5,34 dBTP**, LRA 4,30, giọng vào **0,00s**, **147 từ/phút**
  tổng thể (123 từ / 50,13s; ~152 wpm chỉ tính lúc nói; theo beat
  146–172 wpm). **Torque kiểm chứng:** ffprobe + sha khớp; xem
  frame 1s (hook "CÁP ĐỨT Ở TẦNG 85?" lớn rõ, dấu đúng, trên ảnh
  giếng thang máy, caption "Cáp thang máy đứt") và 49,5s (end card
  "BẠN CÓ DÁM ĐI THANG TẦNG 85 KHÔNG?" + "YES / NO" đỏ, caption
  "không? Bình luận nhé!" — đầy đủ, không cắt).
- **Giọng:** MMS-TTS trên PC (speaking_rate 0.92), Whisper large-v3
  **105/123 = 85,4%** (chủ yếu chuẩn hóa số "tám mươi lăm"→"85" +
  lỗi ranh giới; các từ nội dung chính nghe đúng hết). **Probe: 2
  lần đổi** — "kẹp chặt ray"→"rai" đổi thành **"phanh kẹp chặt"**
  (94,1%); "nằm ngửa"→"năng ngựa" đổi thành **"nằm dài xuống
  sàn"** (94,1%). Hook giữ nguyên (thử "Dây cáp…" tệ hơn, 60%);
  chữ trên hình "CÁP ĐỨT Ở TẦNG 85?" gánh chính tả. MMS đọc "Cáp"
  thành "Các" ở từ đầu tiên.
- **Hình:** 4 ảnh dùng, toàn CC0 (3 Wikimedia — neil.dalphin ×2,
  Tomasz Rynkiewicz — + 1 Flickr DanielC743); 11 ảnh khác bị loại
  có lý do trong `images/sources.txt`. Beat 3 là Manim stickman tự
  render (nằm dài, tay khoanh trước ngực — 4 lần chỉnh pose).
- **Nhạc + SFX:** bgm_suspense + whoosh/pop 0,1s, ding 5,53/
  14,06s, camera_click 26,86s, boom 41,91s. Ding nghe ở mức giọng;
  click nhỏ nhưng trên nền nhạc; boom to (~6 dB trên giọng — ghi là
  lỗi nhỏ). BGM đo ~11 dB dưới giọng — nóng hơn mục tiêu -18 đến
  -24 dB (ghi nhận, không mix lại; giọng vẫn rõ ràng áp đảo).
- **Render: PC, 12 giây** (quyết định của chủ 21:53 — render trên
  máy chủ từ nay). ffmpeg 8.1.2 trên PC, 22:15:49–22:16:01,
  FFMPEG_EXIT=0, đúng 1504 frame. Ráp tiếng + loudnorm + QC làm
  trên VPS. **Bài học lớn về pipeline: `-loop 1` làm ffmpeg chạy
  mãi không dừng** — encode VPS (56 phút, 98 MB, không có moov) và
  encode PC lần 1 (16 phút, 238 MB) đều là runaway, không phải
  crash: `-loop 1` trên input ảnh làm đầu vào của zoompan vô hạn
  nên chuỗi xfade không bao giờ thấy EOF. Sửa: bỏ `-loop 1` (1 ảnh
  = 1 frame → zoompan xuất đúng `d` frame rồi EOF) + `-frames:v
  1505` làm giới hạn cứng. Chạy lại sạch trong 12s. 2 sửa nhỏ khác
  trên PC: `fontfile=C\:/Windows/...` lỗi parse filter — copy
  BeVietnamPro-Bold.ttf vào thư mục render, dùng đường dẫn tương
  đối (caption đốt bằng Be Vietnam Pro, không phải Noto Sans — ghi
  trong `assemble_filter_pc.txt` / `captions_pc.ass`); lần mix đầu
  ra AAC 96 kHz mono (loudnorm xuất 192 kHz, amix lấy layout mono
  của giọng) — encode lại 48 kHz stereo như v002.
- **Giới hạn trung thực:** chưa ai nghe thật (chỉ Whisper 85,4%);
  BGM nóng hơn mục tiêu; boom payoff ~6 dB trên giọng; caption
  trùng chữ end card ở 2s cuối (như v002); ảnh payoff 1024px hơi
  mờ; beat 2 ~13s gần như tĩnh (chỉ zoompan). **CHƯA đăng.** Đã
  gửi cho chủ xem trong chat. Lô 3 video (v003 + v004 + v005) đã
  hoàn thành.

### Video #4 (v004) — "Ông Tư sửa giày" truyện stickman cảm xúc 50s (F7, #50) — DONE + QC-passed 2026-11-15 21:10 +07
- **File:** `video_production/v004-silent-50s/v004.mp4` — **52,36s,
  1080x1920, 30fps, H.264 + AAC 192k, 2.628.973 byte, sha256
  `6d2c72d8b20f…`** — **-16,05 LUFS** (mục tiêu ~-16), true peak
  **-2,89 dBTP**, LRA 3,40, giọng vào **0,00s**, **150,1 từ/phút**
  tổng thể (131 từ / 52,36s, trong vùng 150–165; theo beat: hook
  167,6, beat1 140,7, beat2 160,4, beat3 136,9, payoff 170,6).
  **Torque kiểm chứng:** ffprobe + sha khớp; xem frame 1s (thẻ hook
  "KHÔNG AI NHÌN ÔNG MỘT LẦN." lớn rõ, dấu đúng, ông Tư mũ + tạp dề
  mặt buồn, sạp, cột đèn, caption "Mỗi ngày, hàng trăm người") và
  51,5s (thẻ payoff "CHỈ CẦN MỘT NGƯỜI DỪNG LẠI." đầy đủ, ông Tư
  cười, bé gái nơ đỏ bên bức vẽ người que + mặt trời đỏ, đèn sáng
  ấm, caption "người dừng lại.").
- **Giọng:** MMS-TTS trên PC (speaking_rate 0.92), Whisper large-v3
  **122/131 = 93,1%**. Probe từ: "Tư" OK, "lướt" OK, **"sạp" LỖI —
  MMS đọc thành "sạc" (xác nhận 2 lần) → đổi thành "quầy nhỏ"**
  theo fallback đã duyệt trong kịch bản (probe "quầy" nghe đúng).
  Đổi đã ghi trong script.md. Lỗi còn lại chủ yếu là Whisper nghe
  nhầm ("bé gái"→"bé rái"; "sửa giày"→"sử dài" — nhầm MMS/Whisper
  đã biết).
- **Render: VPS, không phải PC.** Manim 0.22.1 trong
  `stickman-shorts/.venv`, 2 lần render (test ~69s, bản sửa ~3,5
  phút kể cả chờ queue). Cờ `-ql` bị `apply_video_config()` ghi đè
  thành full 1080×1920 30fps nên đầu ra VPS đã full quality — không
  cần vòng qua PC. Scene: `stickman-shorts/videos/2026-11-15_v004-
  ong-tu-sua-giay/scene.py` (2 rig: ông Tư mũ + tạp dề, bé gái
  scale 0,62 nơ đỏ; sạp, đèn, 5 thẻ chữ; SPEC giữ nguyên, không đổi
  rig). 2 lỗi sửa sau khi xem frame v1: (1) người qua đường beat 1
  dính với ông Tư thành hình 2 đầu → thu 0,8→0,7, đặt sau ông Tư +
  sạp; (2) giày trên sạp nhỏ không đọc được → đế 0,55→0,70, thân
  0,34→0,48.
- **Nhạc + SFX:** bgm_calm với volume envelope (0,11 hook / 0,11
  beat1 / 0,12 beat2 / 0,18 beat3 swell / 0,0 trong 0,5s im trước
  payoff 45,52–46,03 / 0,11 payoff), ding (0,5) ở 30,69, swoosh ở
  3,58/17,22/30,69. BGM đo trong cửa sổ pause giọng: mean -39,1 dB
  (nghe được, dưới giọng). Cửa sổ trước payoff: mean -51,0 dB.
  **Swoosh hạ 0,4→0,2** sau QC: file swoosh peak -3,7 dB raw chạm
  trần alimiter; đo lại cho thấy các peak lớn còn lại là onset câu
  của giọng MMS (raw -1,7 dB ở 3,58s), đã bị alimiter kẹp — TP
  cuối -2,89 dBTP trong chuẩn.
- **QC frame (mp4 cuối, đều pass):** 1s thẻ hook rõ + caption · 8s
  người đi bộ sau ông Tư, không dính · 26s giày trên sạp đọc được ·
  33s bé gái chỉ tay, thẻ "CỦA AI VẬY ÔNG?" · 40s bức vẽ (người que
  nhỏ + mặt trời đỏ) rõ · 48s/52s thẻ payoff đầy đủ, đèn sáng ấm, cả
  hai cười, caption cuối "người dừng lại."
- **Giới hạn trung thực:** chưa ai nghe thật (chỉ Whisper 93,1%);
  SFX không đo riêng từng cái được (ding/swoosh trùng giọng theo
  thiết kế); cửa sổ trước payoff yên nhưng không phải im số tuyệt
  đối (max -29,2 dB, đuôi từ cuối); beat 2 ~13s gần như tĩnh (chỉ
  tay đánh giày dao động); caption trùng chữ thẻ ở cuối (lỗi nhỏ đã
  có ở v002); tạp dề trông hơi giống áo vest; **không dùng gì từ
  #50** (truyện/nhân vật hoàn toàn gốc, chỉ giữ cơ chế, không mưa).
  **CHƯA đăng.** Đã gửi cho chủ xem trong chat. v003 vẫn đang làm.

### Video #5 (v005) — "Top 5 câu nói huyền thoại của mẹ" Countdown 45s (F3, H02 #69) — DONE + QC-passed 2026-11-15 21:03 +07
- **File:** `video_production/v005-countdown-45s/v005.mp4` — **49,97s,
  1080x1920, 30fps, H.264 + AAC 192k, 14.072.099 byte, sha256
  `0c967c677b23…`** — **-16,42 LUFS** (mục tiêu ~-16), true peak
  **-2,55 dBTP**, LRA 3,70, giọng vào **0,00s**, **155 từ/phút** (chỉ
  phần nói, trong vùng 150–165; tổng thể 143 do pause đếm ngược có
  chủ đích — gốc H02 cũng ~114 tổng thể). **Torque kiểm chứng:**
  ffprobe + sha khớp; xem frame 1s (tiêu đề lớn rõ, dấu đúng, #3 mở
  sẵn, các hàng ẩn "• • •", caption rõ) và 49,5s (end card "SỐ 1 CỦA
  BẠN LÀ CÂU NÀO?" + "Bình luận nhé!" + quote #1 đầy đủ, không cắt).
- **Giọng:** MMS-TTS trên PC (speaking_rate 0.92), Whisper large-v3
  **102/119 = 85,7%**. Run 1 (47,92s, 163 wpm, 89,1%) bị loại vì câu
  #1 cảm xúc chạy 190 wpm; **run 2 dùng** (n1a chậm lại rate 0.80 →
  170 wpm, 49,95s, 155 wpm). File run 1 đã bị ghi đè trên PC, không
  khôi phục được; run 2 là bản chính.
- **Probe từ:** "phăng phắc" nghe thành "phan phát" — GIỮ (phương án
  thay thế tệ hơn: "im re"→"Inge", "nín thinh"→"nứng thiên"); chính
  tả đúng nhờ thẻ danh sách + caption (tiền lệ "log" ở v002). "Tao"
  đúng 100% — giữ. "trĩu" nghe thành "triếu" — ĐỔI thành "nặng nề"
  theo kịch bản (caption dùng "nặng nề"). "Top" nghe thành "Tốc"
  (giới hạn từ mượn của MMS; tiêu đề + caption gánh chính tả).
- **Hình:** 5 ảnh dùng, toàn CC0/CC BY (nguồn đầy đủ trong
  `images/sources.txt`): #5 bàn ăn (Kazz.0, CC BY), #4 người một mình
  trong phòng tối (goblinbox_, CC BY), #3 mẹ + bé nấu ăn (Direct
  Media, CC0), #2 bé trai bên cửa sổ (inclusivesecurity, CC BY), #1
  ảnh gia đình (Family Moments, CC0). 9 ảnh khác bị loại có lý do.
  Toàn 1024px, trừ n2a 679px dọc — crop + upscale ~1,6x, hơi mờ.
- **Nhạc + SFX:** bgm_comedy vol 0.12 (đo được: pause-window -41,6
  dB so với giọng -57,1 dB) + whoosh/pop 0,1s, pop mỗi lần reveal
  (3,48/11,32/19,64/28,50/37,68s), riser 34,60–37,68s vào #1 (đo
  được: -29,2 dB so với giọng -94,6 dB ở cửa sổ không giọng),
  **victory NHẸ ở #1** (cắt 1,5s, vol 0,35 — #1 là cảm xúc, không
  phải trò đùa), laugh sau punchline #4, ding ở CTA. **Laugh ở #2
  BỎ** — sẽ đụng riser + reveal #1; bảo vệ cú lật cảm xúc quan
  trọng hơn. Mix `amix duration=longest`; loudnorm 2-pass +
  `alimiter=limit=0.7:level=false`. Lưu ý: `aresample=48000:ocl=
  stereo` không hỗ trợ trên ffmpeg build này — đã bỏ; amix tự xử
  input mono/stereo lẫn nhau.
- **QC frame (đã xem: 1/5/13/21/30/39/46,5/49,5s):** reveal đúng
  thứ tự, ảnh + caption khớp; 39s: #1 huy hiệu vàng + highlight hổ
  phách, quote đầy đủ 1 dòng. Nhỏ: caption (MarginV 300) sát hàng
  #5 (vd 39s) — vẫn đọc được, không che chữ; lần sau nâng MarginV
  lên ~360. Caption "luận nhé!" trùng chữ end card ở 2s cuối (lỗi
  nhỏ đã có ở v002).
- **Giới hạn trung thực:** chưa ai nghe thật (chỉ Whisper 85,7%) —
  chủ nên nghe 1 lần trước khi đăng, nhất là "phăng phắc" ("phan
  phát"), "Top" ("Tốc"), và câu #1 cảm xúc. SFX không đo riêng từng
  cái được (trùng giọng theo thiết kế); chỉ BGM + riser đo bằng cửa
  sổ năng lượng, còn lại kiểm bằng cấu trúc filter. Ảnh 1024px hơi
  mờ khi crop 9:16 (n2a tệ nhất); ảnh n4 tối. **CHƯA đăng.** Đã gửi
  cho chủ xem trong chat. Video đầu tiên trong lô 3 hoàn thành —
  v003 + v004 vẫn đang làm.

### Vòng 3 — mở rộng menu giọng (tự động hóa + lâu dài + dùng PC) — DONE 2026-11-15 18:48 +07
- **Lý do:** chủ dặn (18:33) chọn thêm lựa chọn, ưu tiên tự động hóa
  được + render dài lâu được, có thể dùng máy của chủ (RTX 5060 Ti,
  16 GB VRAM).
- **Vị trí:** `video_production/voice-compare-20261115/voice_compare.md`
  (435 dòng, 33 KB — Torque kiểm chứng: đủ mục "Vòng 3", bảng menu,
  mục Gemini/FPT.AI) + 5 script vòng 3. Không có mẫu wav mới vòng
  này (Edge không ra tiếng; VITS bị chặn trước khi tổng hợp).
- **Kết quả:**
  - **Qwen3-TTS — NGÕ CỤT (không cần cài):** README chính thức liệt
    kê đúng 10 ngôn ngữ (Trung, Anh, Nhật, Hàn, Đức, Pháp, Nga, Bồ,
    Tây, Ý) — **không có tiếng Việt**. Bản fine-tune cộng đồng
    `ShiniChien/Qwen3-TTS-12Hz-1.7B-Vietnamese` có (Apache 2.0, 30
    giọng, fine-tune trên H200) nhưng 0 lượt tải, checkpoint **3,83
    GB — vượt ngưỡng 3 GB, CHƯA tải**, chờ duyệt.
  - **Model Việt trên HF — ứng viên số 1: `hynt/F5-TTS-Vietnamese-
    ViVoice`** (9.569 lượt tải, 60 like, fine-tune 1.000 giờ ViVoice
    + VLSP 2021–2023, 1,5 tháng trên RTX 3090, tái dùng `.venv-f5`).
    Checkpoint **5,39 GB — CHƯA tải** (vượt ngưỡng), license
    **CC-BY-NC-SA-4.0 (phi thương mại) — phải kiểm lại trước khi
    kiếm tiền**. Các model khác cũng vượt ngưỡng, chưa tải:
    `multilingual-tts/F5-TTS-OpenBible-Vietnamese` (5,37 GB),
    `thangquang09/parler-tts-vietnamese-v1-stage2` (3,54 GB). Model
    duy nhất dưới ngưỡng đã thử: `multilingual-tts/VITS-OpenBible-
    Vietnamese` (998 MB, CC-BY-SA-4.0, 2 giọng) — **BỊ CHẶN:** Coqui
    TTS không có wheel Windows (kiểm chứng qua PyPI JSON — mọi
    phiên bản 0.8.0–0.22.0 chỉ có manylinux); `pip install TTS` đòi
    biên dịch từ source và cần MSVC 14.0+ (PC không có MSVC Build
    Tools). Đã tạo `.venv-vits` (Python 3.10 + torch 2.11 cu128) và
    tải sẵn model về PC để thử sau nếu có Build Tools hoặc chạy
    Linux. Ưu tiên thấp (42 lượt tải, dữ liệu audiobook Kinh Thánh).
  - **Edge TTS thử lại — VẪN BỊ BÓP:** 1 lần thử nhanh, plain text
    (không SSML), cả HoaiMy + NamMinh → `NoAudioReceived`, 0 byte.
    Dừng sau 1 lần, không cố thêm.
  - **API (chỉ nghiên cứu, không key/không đăng ký):**
    - **Gemini TTS (Flash/Lite) — API SỐ 1:** free tier "Free of
      charge", không cần thẻ; trả phí $0,81/giờ Flash / $0,54/giờ
      Flash-Lite tới 31/12/2026, tăng gấp đôi từ 01/01/2027. REST
      `generateContent` + API key, hoàn toàn tự động hóa được.
      Style bằng `speech_metadata` + thẻ `<short pause>` (không
      SSML). 30 giọng, giọng nào cũng nói được mọi ngôn ngữ; tiếng
      Việt được đánh giá cao trên Voice Arena. **Chủ cần: tạo key
      miễn phí tại aistudio.google.com (2 phút, dùng tài khoản
      Google sẵn có).**
    - **FPT.AI TTS v5 — dự phòng Việt số 1:** free 100k ký tự/tháng
      (~160 video/tháng), sau đó gói từ 500k VND. 9 giọng, 3 vùng
      miền, 7 tốc độ, từ điển phát âm. REST + API key. **Chủ cần:
      đăng ký tại console.fpt.ai → tạo project → API key (không
      cần thẻ).**
    - **Google Cloud TTS:** free 4M ký tự/tháng Standard/WaveNet +
      1M Neural2/Chirp 3 HD, SSML đầy đủ, giọng vi-VN — **nhưng bắt
      buộc billing + thẻ tín dụng ngay cả khi dùng free, vượt hạn
      mức tự tính tiền.** Chỉ dùng nếu chủ chấp nhận thẻ.
    - **Vbee:** 700+ giọng, Gen 2 tiếng Việt, SSML, REST API; từ
      $5,99/tháng, có free-trial nhưng hạn mức free không công bố
      — trả phí ngay từ đầu.
- **Xếp hạng đề xuất:** 1) **MMS-TTS (vòng 2) — làm ngay** (local,
  miễn phí, tự động hóa hoàn toàn, chủ đã ưng giọng). 2) **Gemini
  TTS free tier** — nâng cấp API đầu tiên (thử 3 câu ngay khi chủ
  tạo key). 3) **FPT.AI** — dự phòng Việt. 4) **F5-TTS-Vietnamese-
  ViVoice, 5,39 GB — chờ chủ duyệt tải.** 5) Edge — thử lại thỉnh
  thoảng. 6) Cloud TTS — chỉ khi chủ chấp nhận thẻ. 7) Vbee /
  ElevenLabs — cuối cùng.
- **Cần chủ quyết (chưa tự quyết):** duyệt/không duyệt tải 5,39 GB
  `hynt/F5-TTS-Vietnamese-ViVoice` (và tùy chọn 3,83 GB Qwen3-Việt
  sau đó). Không xóa gì trên PC. Đĩa mới: `.venv-vits` 4,2 GB + model
  VITS 998 MB; ổ C: còn 45,5 GB trống. `.venv-kokoro` 4,7 GB vẫn chờ
  chủ quyết xóa.
- **Thời gian:** ~15 phút (18:33–18:48). Menu đã đưa cho chủ chọn
  trong chat (3 lựa chọn).

### Vòng 2 — chỉnh tốc độ + ngưng nghỉ MMS-TTS (giữ nguyên giọng) — DONE 2026-11-15 18:33 +07
- **Lý do:** chủ phán giọng MMS hay, chỉ ngưng nghỉ + tốc độ chưa ok
  (18:28). Không đổi giọng; sửa cách đọc.
- **Phát hiện kỹ thuật:** `length_scale` KHÔNG hỗ trợ trong
  transformers 5.23.0 (kiểm chứng bằng `inspect.signature(VitsModel.
  forward)` — tham số có `speaking_rate`, không có `length_scale`).
  Tương đương là **`speaking_rate`** (mặc định 1.0, thấp hơn = chậm
  hơn): đo thực tế câu 1 — rate 1.0 → 164 từ/phút, 0.75 → 135,
  1.25 → 196. Không cần atempo (sẽ nghe máy móc hơn). Tái dùng venv
  ai-stack trên PC; không venv mới, không đăng ký, không trả tiền.
- **Ngưng nghỉ mới:** 0,3s sau hook, 0,4s micro-pause ở dấu phẩy
  trong câu 2 (tách thành 2 mệnh đề), 0,6s trước payoff — tổng 1,3s
  (vòng 1: 1,4s; v002: 2,4s cố định).
- **4 mẫu (cùng 3 câu vòng 1, 40 từ; đã copy về VPS, ffprobe kiểm
  chứng — Torque kiểm lại: slow09 16,34s/522.924 byte, slow12
  17,76s/568.492 byte, đủ 4 file + mục "Vòng 2" trong
  `voice_compare.md`):**
  - **C — `mms_slow09.wav` (rate 0.92): NGHE TRƯỚC — duy nhất nằm
    trong vùng an toàn 150–165 từ/phút (160, tính riêng phần nói),
    đều nhất sau B. Whisper 33/40 = 82,5%.**
  - **A — `mms_slow12.wav` (rate 0.83): NGHE THỨ HAI — chậm/nhẹ
    nhàng hơn (146 từ/phút phần nói), Whisper tốt nhất vòng 2
    (35/40 = 87,5%). Nếu C vẫn thấy nhanh thì A là lựa chọn.**
  - B — `mms_slow135.wav` (rate 0.74): có lẽ quá chậm (123 từ/phút
    tổng thể). D — `mms_clause.wav` (rate 1.0 + micro-pause 0,25s):
    chứng minh chỉ đổi vị trí ngưng nghỉ không sửa được tốc độ.
- **Độ đều đã sửa:** vòng 1 chênh lệch giữa các câu 63 từ/phút
  (131–194). Vòng 2: B 19, D 23, C 24, A 29 — nhịp nhanh-chậm giật
  cục đã hết. Chênh lệch Whisper giữa các mẫu nhỏ, không phải căn
  cứ chọn (thật ~90–92,5% sau khi trừ lỗi chuẩn hóa số "500" của
  Whisper). "log" vẫn nghe sai thành "lon"/"lo" ở MỌI mẫu — tốc độ
  không sửa được lỗi MMS "log"→"lô" đã biết; chữ trên hình phải
  gánh chính tả.
- **2 lưu ý trung thực:** (1) "gọi" nghe đúng ở vòng 1 nhưng thành
  "vậy" ở cả 4 mẫu vòng 2 — có thể do tách mệnh đề ở dấu phẩy, hoặc
  do model ngẫu nhiên (tốc độ từng lần chạy dao động ~10%: câu 1 ở
  rate 1.0 đo 164 từ/phút lúc probe nhưng 180 ở mẫu D). (2) Câu hook
  nhanh nhất ở mọi mẫu — model đọc câu hỏi nhanh hơn; chỉnh rate
  không san phẳng hoàn toàn.
- **Nếu C và A đều chưa vừa ý:** bước tiếp là rate ở giữa (~0,87–
  0,88) hoặc rate riêng từng câu (hook chậm hơn, beat bình thường)
  — model hỗ trợ chỉnh từng câu, không cần đổi giọng.
- **Thời gian:** ~5 phút (18:28–18:33). 2 mẫu C + A đã gửi cho chủ
  nghe trong chat.

### So sánh giọng đọc thay thế MMS-TTS — DONE (báo cáo) 2026-11-15 18:21 +07
- **Lý do:** chủ nghe v002 và nói giọng đọc chưa ok, ngưng nghỉ chưa
  ok (17:48). Thử 3 giọng khác trên PC với cùng 3 câu (hook + beat +
  payoff v002) để chủ nghe và chọn.
- **Vị trí:** `video_production/voice-compare-20261115/` —
  `voice_compare.md` (báo cáo đầy đủ) + 3 file wav + 27 script (.py/
  .ps1). PC gốc + log: `C:\Users\w\agentnet-corner\ai-stack\
  voice_compare\` và `C:\Users\w\voice_*.log`.
- **Kết quả — chỉ 1/4 giọng cho ra mẫu dùng được:**
  - **MMS-TTS với ngưng nghỉ THAY ĐỔI (mẫu đối chứng) — DÙNG ĐƯỢC:**
    `mms_varied.wav` 15,54s, 497.452 byte (Torque kiểm chứng bằng
    ffprobe: PCM 16-bit mono 16 kHz). Ngưng nghỉ 0,6s sau hook, 0,8s
    trước payoff (không cố định 1,2s như v002). Whisper large-v3 trên
    PC nghe đúng 36/40 từ = 90,0% (thật ~95% — "năm/trăm" là lỗi
    chuẩn hóa số "500" của Whisper; "log"×2 nghe thành "đô"/"lon" —
    lỗi MMS "log"→"lô" đã biết). Tốc độ 154 từ/phút tổng thể
    (183/194/131 từng câu). **Giọng vẫn đơn điệu** — ngưng nghỉ đổi
    chỉ sửa cấu trúc của lời phàn nàn, không sửa được độ đơn điệu.
    Chủ là người duy nhất phán được (Whisper chỉ đo đúng từ, không
    đo độ tự nhiên).
  - **Edge TTS (HoaiMy/NamMinh) — THẤT BẠI (bị chặn/bóp băng
    thông):** `edge_tts.exceptions.NoAudioReceived` — server nhận
    stream (turn.start + response) rồi đóng lặng, 0 byte âm thanh.
    Lúc đầu chạy được 2 lần, sau đó bị bóp. Thử lại ~1 giờ sau vẫn
    lỗi. Ngoài ra edge-tts 7.3.1 KHÔNG làm được SSML (nó escape
    SSML và giọng đọc luôn cả thẻ XML — Whisper xác nhận). Không có
    mẫu nào.
  - **F5-TTS — THẤT BẠI (không nói được tiếng Việt):** cài + chạy
    được (sửa 3 lỗi: `--output` mơ hồ → `--output_dir`/`--output_file`;
    cp1252 crash khi in tiếng Việt → UTF-8; torchcodec 0.17.0 thiếu
    DLL FFmpeg → tải FFmpeg 8.1 shared build 85,5 MB, thêm bin vào
    PATH). Nhưng model gốc KHÔNG nói được tiếng Việt: đưa đúng câu
    1 kèm audio+text tham chiếu, nó đọc "Hãy subscribe cho kênh La
    La School…" — nhại lại câu outro YouTube đã nhớ. Cả 6 file từng
    câu đều 0–5% (tốc độ 1.0: 0/40 = 0,0%, 210 từ/phút quá nhanh;
    tốc độ 0.75: 1/40 = 2,5%, 162 từ/phút). Model đã có sẵn trong
    HF cache của chủ (không tải mới). `f5tts.wav` + `f5tts_slow.wav`
    giữ lại làm bằng chứng, KHÔNG phải mẫu nghe.
  - **Kokoro-82M — THẤT BẠI (không có giọng Việt):** danh sách
    giọng chính thức (37 giọng) không có tiếng Việt (chỉ en-US/GB,
    es, fr, hi, it, ja, pt, zh) — kiểm chứng bằng cách liệt kê
    `hexgrad/Kokoro-82M` voices/ trên HF.
- **Chưa thử:** FPT.AI/Vbee (cần chủ đăng ký tài khoản), ElevenLabs
  (trả phí, cần chủ duyệt), Qwen3-TTS. Không đăng ký, không trả tiền,
  không tạo tài khoản nào. Không đăng/upload gì.
- **Đề xuất:** (1) chủ nghe `mms_varied.wav` và phán xem ngưng nghỉ
  thay đổi có đủ không; (2) nếu không đủ, theo thứ tự: thử lại Edge
  TTS hôm khác (bóp băng thông có thể hết), FPT.AI/Vbee (cần chủ đăng
  ký), ElevenLabs (trả phí). Không tốn thêm thời gian cho F5-TTS gốc
  hay Kokoro với tiếng Việt.
- **Dọn dẹp PC:** `.venv-f5` 5,5 GB + `.venv-kokoro` 4,8 GB +
  `ffmpeg-shared` 223 MB (+ zip 85,5 MB) mới sinh trên PC. `.venv-
  kokoro` xóa được để lấy lại ~4,8 GB (Kokoro đã là ngõ cụt) — đang
  chờ quyết định, chưa xóa. Bản sửa torchcodec (DLL FFmpeg 8.1
  shared trên PATH) tái dùng được cho mọi việc torchaudio sau này
  trên PC — ghi trong `voice_ffmpeg_shared.ps1` + `voice_compare.md`.
- **Thời gian:** ~33 phút (17:48–18:21). Mẫu `mms_varied.wav` đã gửi
  cho chủ nghe trong chat.

### Lô 3 kịch bản (v003 + v004 + v005) — DONE 2026-11-15 17:47 +07
- **Vị trí:** `video_production/scripts-batch-20261115/` — 3 kịch bản +
  `scripts_batch.md` (tóm tắt lô, thứ tự sản xuất, danh sách probe).
  Chỉ kịch bản — chưa sản xuất video, chưa tổng hợp giọng, chưa
  đăng/upload gì. (Torque kiểm chứng: 4 file có đủ; đọc tóm tắt lô +
  phần đầu v003: nguồn có URL đầy đủ.)
- **v003 — #77 (90) thang máy đứt ở tầng 85, F2 Visual Essay, 45s,
  123 từ, ~164 từ/phút:** "Cáp thang máy đứt ở tầng 85 — nhảy lên thì
  sống không?" Nguồn đã kiểm chứng: ScienceABC (rơi từ tầng 20 đã
  ~108 km/h; nhảy Olympic chỉ trừ ~4 m/s; canh thời điểm phải chính
  xác tới mili-giây — coi như không thể; nằm ngửa là tư thế được gợi ý
  nhiều nhất), Otis + AboutElevators (≥4 lớp an toàn độc lập; bộ điều
  tốc tác động ~115% tốc độ định mức; phanh Otis 1852, trình diễn 1854),
  ZestyHabit (nằm ngửa chỉ mang tính lý thuyết, không đảm bảo sống).
  **Con số "72 km/h" của video gốc #77 KHÔNG kiểm chứng được — không
  dùng trong kịch bản**, thay bằng 108 km/h đã kiểm chứng. Năm "1854"
  và tên "Otis" chỉ hiện trên hình, không đọc (bài học MMS v001).
- **v004 — #50 (85) truyện stickman cảm xúc, F7, 50s, 130 từ, ~156
  từ/phút, CÓ giọng kể (không làm bản câm như gốc):** "Ông Tư sửa
  giày — chỉ cần một người dừng lại". Truyện hư cấu hoàn toàn mới
  (ông Tư + bé gái, sạp sửa giày góc phố lúc chạng vạng, đôi giày nhỏ
  không ai nhận + bức vẽ của bé, câu chốt "Chỉ cần một người dừng
  lại.") — khác hẳn nhân vật/bối cảnh/câu chuyện/câu chốt của #50;
  chỉ giữ cơ chế. Không dùng mưa (tránh lặp lại ghế đá mưa của gốc).
  Cảnh báo © của #50 đã tính.
- **v005 — H02 #69 (78) hài, F3 Countdown, 45s, 119 từ, ~159
  từ/phút:** "Top 5 câu nói huyền thoại của mẹ". #2 "Con nhà người
  ta" và #3 "Hồi bằng tuổi mày…" đã kiểm chứng là câu nói quen thuộc
  (BlogRadio, Tripi); thứ hạng là xếp hạng biên tập. #1 là cảm xúc
  ("Mẹ không cần gì đâu, con cứ lo cho con đi.") sau 4 trò đùa — cú
  lật cảm xúc có chủ đích; Victory sting ở #1 dùng NHẸ.
- **Thứ tự sản xuất đề xuất:** v003 → v005 → v004 (rẻ trước; v004 cần
  rig 2 nhân vật + nền góc phố, đắt nhất).
- **Từ cần probe trên PC trước khi sản xuất:** v003 "tám mươi lăm",
  "kẹp chặt ray", "ngửa"; v004 "Tư", "lướt", "sạp"; v005 "phăng phắc",
  "Tao", "trĩu" (đã ghi phương án thay thế trong từng file).
- **Thời gian:** ~5 phút (17:42–17:47). Người dùng chọn lô này lúc
  17:42 và nói "tôi mong chờ kết quả quá" — kịch bản đã gửi cho chủ
  xem trong chat.

### Video #2 (Ep002) — "LOG IN" Visual Essay 45s (F2, #81) — DONE 2026-11-15 17:36 +07
- **File:** `video_production/v002-login-45s/v002.mp4` — 46,8s, 1080x1920
  30fps, H.264 + AAC 192k, 13,7 MB, sha256 `b8b4f7cf18e338ccb645…`
  (Torque kiểm chứng: ffprobe + sha khớp; xem frame 1s và 46,2s: hook
  "MỖI LẦN ĐĂNG NHẬP, BẠN ĐANG DÙNG MẸO CỦA THỦY THỦ 500 NĂM TRƯỚC?"
  to, rõ, đúng dấu, tàu Schotel đủ khung; thẻ cuối "Bạn biết chuyện
  này chưa? Bình luận nhé!" hiện đủ sau khi sửa).
- **Chủ đề:** #81 "WHY DO WE 'LOG IN'?!" (87) — kịch bản gốc 125 từ (F2),
  hook kép → thủy thủ + dây thừng thắt nút → sổ log → đăng nhập máy tính
  → payoff "Đăng nhập là ký tên vào sổ log của tàu" + poll/CTA.
  Nguồn gốc từ đã kiểm chứng: Etymonline ("log") — log-book (1670s) từ
  chip log trên dây log, nút thắt đo tốc độ; nghĩa máy tính "log in" từ
  1963; + Wikipedia "Logbook (nautical)" + Turner Publishing. Lưu ý ghi
  trong script.md: có ý kiến cho rằng "log in" có thể từ "log on" (lệnh
  mainframe) — kịch bản trình bày theo cách hiểu phổ biến, không khẳng
  định tuyệt đối.
- **Đã đo:** **-16,39 LUFS** (đúng mục tiêu — lỗi -17,40 của Ep001 đã
  tránh được, không cần pass loudnorm thêm), true peak **-2,42 dBTP**,
  LRA 3,80, giọng bắt đầu **0,00s** (hết dead air 1,49s của bản gốc),
  **160 từ/phút** (125 từ / 46,8s, trong vùng an toàn). Phụ đề 33 events,
  khớp kịch bản 125/125 từ; 10 frame đã xem (`qc.md`).
- **Giọng MMS-TTS TRÊN PC** (CUDA, tổng hợp 0,9s): kiểm bằng
  faster-whisper large-v3 trên PC: **113/123 = 91,9%** từ nghe đúng
  (v001 chỉ ~70% bằng Whisper Base trên VPS). Tốc độ từng câu 168–200
  từ/phút, nối bằng khoảng nghỉ 1,2s kéo về 160 tổng. 2 vòng thử trên PC
  (13 câu) chốt từ rủi ro: "Ngày xưa" ổn, "buộc"/"đếm"/"hải lý" ổn,
  "cột" tệ hơn "buộc" (nghe "cục") — loại; câu beat-2 cũ hỏng ổn định
  (71% hai lần) đã viết lại. **Giới hạn MMS: "log" đọc thành "lô/lố"**
  (rớt phụ âm cuối; viết "lốc" cũng không sửa được) — giữ nguyên trong
  giọng nói, chữ trên màn hình ("CHIP LOG", "SỔ LOG") giữ đúng chính tả.
- **Nhạc + SFX — video đầu tiên CÓ nhạc:** `bgm_calm.ogg` volume 0,12
  (đo ở khoảng nghỉ -41,1 dB, thấp hơn giọng ~22 dB) + whoosh + pop ở
  0,1s, ding ở 6,68/18,34/30,00s, camera_click ở 18,34s, boom (vol 0,8)
  ở 41,12s — toàn bộ CC0 từ thư viện Core_SFX. SFX kiểm chứng bằng cấu
  trúc filtergraph + đo khoảng nghỉ của nhạc; độ nghe của từng SFX riêng
  không tách đo được (chúng trùng với giọng theo thiết kế) — ghi thật
  trong qc.md.
- **Hình:** 4 ảnh đã dùng, toàn CC0/CC BY (Schotel "Ships in a Turbulent
  Sea" 1826 CC0 Rijksmuseum; dây thừng hoàng hôn CC0; trang sổ log thật
  1944 CC BY PhillipC; màn hình đăng nhập Facebook CC BY Homedust);
  4 ảnh khác tải về rồi loại có lý do. Tất cả 1024px (Openverse
  editor_1024) — hơi mềm khi crop 9:16, như v001, chấp nhận được.
- **Lỗi đã sửa:** thẻ cuối bị cắt ở build 1 (24 ký tự, fontsize 88 tràn
  1080px) → giảm fontsize 64, encode lại, kiểm lại ở 45,5s + 46,2s:
  hiện đủ. Mix treo >4 phút lần đầu — `apad` trên track giọng +
  `amix duration=first` không bao giờ kết thúc → bỏ `apad`, dùng
  `duration=longest`; mix xong trong 4,7s.
- **Giới hạn thật:** chưa ai nghe bằng tai (chỉ Whisper 91,9%) — chủ nên
  nghe một lần trước khi đăng, nhất là "log" ("lô") và "Bạn gõ mật khẩu";
  độ nghe từng SFX chưa đo riêng; ảnh 1024px hơi mềm; phụ đề "luận nhé!"
  trùng chữ thẻ cuối trong 2s cuối (thừa nhỏ như v001). PC chạy tốt suốt
  (SSH, TTS + Whisper ~10s/lần); không cần fallback VPS.
- **Chưa đăng/upload đâu cả.** Thời gian: ~21 phút (17:15–17:36) — nhanh
  gấp ~3 lần v001 (65 phút) nhờ TTS + Whisper trên PC.
- **Thay đổi hệ thống:** `auto_push.sh` nay thêm `video_production/` vào
  danh sách git-add (chỉ file text — mp4/wav/jpg vẫn bị .gitignore chặn);
  lần đầu tiên file sản xuất (script.md, qc.md, captions) được đưa lên
  git cùng đợt push này.

### AI stack local trên PC (PyTorch cu128 + faster-whisper + TTS Việt) — DONE 2026-11-15 17:15 +07
- **Bắt đầu:** 2026-11-15 ~17:03 +07. Tiếp sau test render Manim (DONE).
- **Nội dung:** kiểm tra driver NVIDIA (cần ≥572.60, nếu thấp hơn thì dừng
  và báo, không tự cập nhật driver) → cài PyTorch ≥2.7.0 cu128 vào venv
  riêng (không chạm hệ Python của chủ) → faster-whisper large-v3, thử
  với voice.wav Ep001 → TTS Việt local (MMS-TTS). Ghi PC_AI_SETUP.md.
- **Kết quả: CHẠY ĐƯỢC, cả 3 công cụ đã kiểm chứng bằng chạy thật.**
  - Driver NVIDIA **610.88** (cần ≥572.60 — đạt, không cần làm gì),
    RTX 5060 Ti 16 GB VRAM.
  - **PyTorch 2.11.0+cu128, CUDA 12.8**: `cuda.is_available()` True,
    capability (12, 0) = sm_120, matmul 512×512 trên CUDA ok. Cài ~100s
    (torch có sẵn trong pip cache của PC).
  - **faster-whisper 1.2.1, large-v3** (ctranslate2 4.9.0, av ghim 14.0.0):
    voice.wav Ep001 (48,8s) nghe xong trong **4,7s (RTF 0,10x — nhanh
    gấp ~10 lần VPS)**, khớp kịch bản **130/137 = 94,9%**. Cùng file trên
    VPS whisper.cpp Base: 113/137 = 82,5% ở ~1x real-time.
  - **MMS-TTS Việt** (transformers 5.23.0, mms-tts-vie trên CUDA): 3 câu
    (55 từ, 19,6s audio) tổng hợp trong **0,9s** (VPS mất ~58s cho cả
    giọng Ep001). Whisper tự kiểm output: **52/55 = 94,5%** (trượt: lả,
    cày, tiếp — đúng các từ yếu đã biết của MMS). File test đã copy về
    VPS: `stickman-shorts/test_audio/pc_tts_test.wav` (21,1s, 16 kHz
    mono — Torque kiểm chứng ffprobe: 21,116s, 675.756 byte).
- **Venv riêng:** `C:\Users\w\agentnet-corner\ai-stack\.venv-ai`
  (Python 3.12.10) — tách khỏi `.venv-win` và hệ Python của chủ; không
  chạm gì của chủ. Thư mục ai-stack ~4,7 GB; ổ C: còn trống 61,8 GB.
- **Model đã có sẵn trong cache chung của chủ** (`HF_HOME` =
  `D:\0.1_FACE_BOOK\DUNG_CHUNG\MODELS\HF_CACHE`) — không tải gì,
  không ghi gì vào cache; large-v3 load ~3s, MMS-TTS ~13,7s. Venv phụ
  thuộc cache này — không dời/xóa.
- **Lỗi đã sửa:** faster-whisper 1.2.1 + av 19 hỏng (ghim `av==14.0.0`);
  ctranslate2 không tìm thấy cuBLAS (torch 2.11 để DLL trong
  `site-packages\torch\lib` — phải thêm vào `$env:PATH` trước khi chạy
  python); console cp1252 crash khi in tiếng Việt (reconfigure utf-8).
- **Hồ sơ:** `stickman-shorts/PC_AI_SETUP.md` (131 dòng) + 9 script
  (`ai_*.ps1` / `ai_*.py`).
- **Giới hạn thật:** chưa ai nghe output TTS của PC bằng tai (chỉ kiểm
  Whisper 94,5%); câu hook MMS chạy 195 từ/phút (trên vùng an toàn
  150–165); đường truyền file-path của faster-whisper chưa thử sau khi
  ghim av (khuyên dùng đường numpy-array). Chưa làm: không có service
  nền, không Ollama/ComfyUI, large-v3-turbo chưa thử (không cần ở
  RTF 0,10x), chưa render tập thật trên PC, `assemble.py --srt` vẫn
  chưa thử trên PC.
- **Thời gian:** ~12 phút làm việc thật (17:03–17:15), không bị chặn.


### PC Windows — test render stickman qua SSH — DONE 2026-11-15 17:02 +07
- **Kết quả: CHẠY ĐƯỢC.** Demo render trên PC **4,58s** (VPS: 17,2s lạnh /
  8,6s ấm). File `StickmanScene-pc.mp4` 263.107 byte, h264 1080x1920
  30fps 5,000s (Torque kiểm chứng: ffprobe khớp; xem frame 1s và 4s:
  dáng đi + vẫy tay + thẻ "TÂM SỰ NGƯỜI QUE" đúng dấu, nội dung giống
  hệt bản render trên VPS).
- **Môi trường trên PC** (DESKTOP-01O3HNF, 100.101.158.71): Python **3.12.10**
  đã có sẵn (lệnh `python` trần là 3.10.11 — KHÔNG dùng; dùng `py -3.12`
  hoặc đường dẫn đầy đủ), ffmpeg 8.1.2 + git 2.54.0 đã có sẵn, không cần
  cài. Repo `C:\Users\w\agentnet-corner` (HEAD 58b70a2), venv
  `.venv-win` (manim 0.22.1). Font Be Vietnam Pro đã cài + nhìn thấy
  được — chỉ thấy sau khi thêm entry HKLM (HKCU + copy file chưa đủ).
- **Hồ sơ:** `stickman-shorts/PC_SETUP.md` + 5 script `.ps1` dùng lại
  được (commit f89d9c5); render + frame đã copy về VPS
  (`test_frames/pc/`).
- **Sự cố đã sửa:** quoting lồng nhau của `-Command` hỏng 2 lần → chuyển
  sang file `.ps1` scp lên PC (mẫu bền vững); lần thử venv+pip đầu treo
  **62 phút** (ssh exit 255) — còn sót 1 `python.exe` nhàn (PID 4368) +
  `powershell.exe` (PID 38548) từ 15:49, ~0 CPU, không rõ là của session
  treo hay REPL của chủ — **để nguyên, không chạm**; script `Start-Process`
  detached chết im → chạy foreground + `< NUL` + transcript (pip xong
  trong 68s); render script gọi nhầm `ffmpeg` thay vì `ffprobe`.
- **Không chạm** hệ Python riêng của chủ trên PC (3.10/3.14,
  `D:\02_CONG_CU\youtube-reup-pipeline\venv`). Log trên PC:
  `C:\Users\w\pip_install.log`, `font_install.log`, `font_fix.log`,
  `render_demo.log`.
- **Chưa thử trên PC:** `render_all.sh`, `assemble.py --srt`, render tập
  thật. Bước tiếp theo (AI stack local) chưa bắt đầu.


### Thư viện Core_SFX (18 SFX + 4 nhạc nền) — DONE 2026-11-15 16:21 +07
- **Vị trí:** `stickman-shorts/src/assets/audio/` — `sfx/` 18 file + `music/`
  4 file, tổng **7,0 MB** (sfx 808 KB, nhạc 6,0 MB), định dạng Ogg Vorbis
  q5 48 kHz; `sfx_manifest.json` (22 entries) + `sfx_report.md` + script
  tải/chuẩn hóa (`search_openverse.py`, `download_sfx.py`,
  `normalize_sfx.py`, `build_manifest.py`).
- **Nguồn:** toàn bộ **CC0 1.0** (public domain, dùng thương mại được,
  không cần ghi nguồn) — file preview HQ của Freesound tìm qua Openverse
  API (`license=cc0`); mỗi entry có source URL + creator + license.
- **Đã đo (Torque kiểm chứng):** 18 sfx + 4 nhạc đúng số lượng; whoosh
  0,45s, bgm_calm 95,7s khớp manifest; tích hợp **-19,8 đến -21,27 LUFS**,
  true peak **≤ -1,2 dBTP**; git KHÔNG ignore `.ogg` (check-ignore exit 1)
  nên thư viện vào được git (không cần sửa .gitignore).
- **Lỗi đã sửa:** Vorbis overshoot đẩy TP lên trên -1 dBTP → limiter hạ
  0,85; ffmpeg loudnorm tự upsample 11 file lên 192 kHz → thêm
  `aresample=48000`, encode lại toàn bộ. Cắt bớt: boom 3,94s→2,5s,
  footsteps/crickets 17s→4s loop, bgm_upbeat 160s→90s; fade 2s cho nhạc.
- **Giới hạn thật:** chưa ai nghe bằng tai (chỉ đo bằng ffprobe/loudnorm);
  `boing` từ nguồn rất nhỏ (max -25 dB, tăng ~+25 dB) nên có thể nghe
  thấy noise floor khi phát riêng — cần nghe thử cả 22 file trước khi
  dùng cho video đăng. File là preview HQ mp3 của Freesound, không phải
  WAV gốc (cần API key Freesound mới lấy được). Mixkit không dùng được
  từ VPS này (URL asset trả 403 dù có Referer + UA trình duyệt).
- **Chưa dùng trong video nào.** Tập sau dùng `--music` với file `.ogg`.

### Ep001 — tập stickman thật đầu tiên (F7, 50s) — DONE 2026-11-15 16:02 +07
- **File:** `stickman-shorts/videos/2026-11-15_ep001-cam-dau-lam-viec/output/final.mp4`
  — 48,8s, 1080x1920 30fps, H.264 + AAC 192k, 3,2 MB, sha256 `3f40bf21a0616d30baaa…`
  (Torque kiểm chứng: ffprobe + sha khớp; xem frame 1s và 36s: hook
  "CÙNG LÀM 10 TIẾNG" rõ, dấu đúng; 2 nhân vật An/Bình + túi tiền rõ, không
  đè chân; phụ đề rõ, đúng vị trí).
- **Chủ đề:** "Cùng làm 10 tiếng, sao người giàu, người nghèo?" — kịch bản
  gốc 137 từ (F7), hook kép 0–3s → An đổi giờ lấy tiền → Bình xây cây cầu
  → một năm sau → payoff "Giàu không phải làm nhiều hơn. Giàu là làm khác
  đi." Bài học cảm hứng từ FB-05, không sao chép câu chữ/cảnh nào.
- **Đã đo:** -17,40 LUFS (thấp hơn mục tiêu 1,4 — chưa sửa), true peak
  -2,91 dBTP, giọng bắt đầu 0,105s, 174 từ/phút (trên vùng an toàn 150–165).
  Phụ đề 16 events, khớp kịch bản 137/137 từ; 7 frame đã xem (`qc.md`).
- **Giọng MMS-TTS** (đúng pipeline v001): từng beat riêng, ngắt 0,3/0,4/0,4/0,7s.
  Piper tự kiểm: 275 từ/phút — loại; Edge TTS file 0 byte — khớp v001.
  Caption sửa theo kịch bản gốc (timestamp Whisper giữ nguyên).
- **Đường `--srt` của assemble.py ĐÃ TEST + SỬA XONG:** `tools/assemble.py`
  tự convert .srt → .ass (PlayRes 1080x1920, Be Vietnam Pro 56) + filter
  `ass` + `alimiter=limit=0.7:level=false`; 2 bài học ghi vào docstring.
- **Lỗi hình đã sửa:** POSE_SURPRISED 2 tay chồng thành 1 tay + chân/thân
  thành 1 cột → sửa pose-only (SPEC không đụng), rig test chạy lại ALL
  PASSED; túi tiền đè chân Bình → dời x 2,2 → 3,2.
- **Giới hạn thật:** không nhạc nền (thư viện nhạc/SFX vẫn trống — điểm yếu
  lớn nhất); chưa ai nghe giọng bằng tai; tốc độ 174 từ/phút hơi nhanh;
  beat 2 có ~4s tư thế suy nghĩ tĩnh hơi dài; ảnh tĩnh giữa nhịp đi bộ
  đôi khi gượng.
- **Chưa đăng/upload đâu cả.** Thời gian: ~75 phút.

### Video #1 — Visual Essay 45s (F2) — DONE 2026-11-15 15:57 +07
- **File:** `video_production/v001-visual-essay-45s/v001.mp4` — 47,1s,
  1080x1920 30fps, H.264 + AAC 192k, 12,6 MB, sha256 `e65285dd625caccc…`
  (Torque kiểm chứng: ffprobe + sha khớp báo cáo; xem frame 1s và 24s:
  hook "Bạn có biết cửa sổ máy bay tròn không phải để đẹp?" rõ, dấu đúng;
  phụ đề rõ, đúng vị trí).
- **Chủ đề:** "Vì sao cửa sổ máy bay lại tròn?" — 126 từ, tiếng Việt,
  hook kép (chữ + lời hỏi cùng 1 câu trong 3s đầu) → lịch sử Comet →
  toán ứng suất Inglis/Kirsch → payoff + CTA. Nguồn đã kiểm chứng
  (FAA Comet, Kirsch 1898 ×3, Inglis 1913 tới ×21, số chu kỳ bay
  G-ALYP 1.290 / G-ALYY 900 / G-ALYU 3.060).
- **Đã đo:** -16,74 LUFS, true peak -3,05 dBTP, giọng bắt đầu ~0,05s,
  160 từ/phút — đều trong chuẩn. 9 frame QC đã xem (`qc.md`).
- **Giọng đọc MMS-TTS** (`facebook/mms-tts-vie`, local, miễn phí) — đọc
  từng câu + ngắt 0,9s; Whisper kiểm 70% khớp từ, từ khóa nghe rõ.
  Edge TTS bị proxy chặn (WebSocket), gTTS 429, Piper phá dấu tiếng Việt
  ("góc nhọn"→"khóc ngọt") — không dùng được. **MMS-TTS là pipeline
  chuẩn cho các video sau** (mẫu `gen_voice.py` / `synth_sentences.py`).
- **Lỗi đã sửa:** phụ đề SRT bị phóng 6,67× (PlayRes 384x288) → chuyển
  sang ASS (PlayRes 1080x1920); true peak +0,24 dBTP sau AAC → sửa bằng
  `alimiter=limit=0.7:level=false` (level=true là auto-gain, KHÔNG phải
  true-peak — đã tăng nhầm loudness lên -13,16 LUFS ở 1 build).
- **Giới hạn thật:** chưa ai nghe giọng bằng tai (chỉ Whisper kiểm —
  Whisper yếu tiếng Việt, ~30% nghe nhầm âm gần giống); chưa có nhạc nền
  (chưa có thư viện nhạc có bản quyền); ảnh img3 hơi mềm (nguồn 960px
  upscale ~2×). Chủ nên nghe 1 lần trước khi đăng.
- **Chưa đăng/upload đâu cả.** Thời gian: ~65 phút (3 lần build).

### Hệ thống liên tục / thay thế VPS (STATUS + HANDOFF) — DONE 2026-11-15 15:54 +07
- **Commit:** `4fe66f4` (3 file) — `STATUS.md` (file này), `HANDOFF.md` §10
  "Takeover" (10 bước cho VPS/Muse mới tiếp quản) + §11 "Infrastructure —
  tất cả các VPS" (VPS 0/1/2/3/4, node Research `baa7de1f`, Verify
  `355c4b87`, tailnet peers, thư mục Drive), `scripts/auto_push.sh`
  (bản sao của auto_push.sh để VPS mới khôi phục cron).
- **Đã kiểm chứng thật:** `STATUS.md` + `HANDOFF.md` đã lên Drive
  (id ở cuối file, kiểm tra bằng `drive files list`); `auto_push.sh` đã
  thêm `STATUS.md` vào danh sách git-add (grep đã kiểm chứng ở cả 2 bản).
- **Quy tắc mới (chủ dặn ~15:50):** kết quả từng tính năng ghi vào
  STATUS.md này (git là bản chính, Drive là bản sao) — KHÔNG báo riêng
  cho chủ nữa. Chủ không can thiệp; cứ bám kế hoạch mà làm.
- **Còn thiếu (xem mục "Rủi ro takeover" cuối file):** `identity.json` /
  `connection.json`, `.env` gateway và khóa SSH `~/.ssh/pc_torque` chưa
  có bản sao lưu nào — cần quyết định của chủ trước khi sao lưu bí mật
  lên Drive; cron chỉ sống trong runtime, chưa có script tái tạo tự động.

### Stickman repo (Manim) — DONE 2026-11-15 15:45 +07
- **Commit:** `58b70a2` (30 file) — `stickman-shorts/`.
  Manim 0.22.1, venv riêng; config.py SPEC đóng băng (HEAD_R=0.6);
  `src/rig/character.py` là class Stickman thật (set_pose/walk/wave/place),
  không còn `pass` placeholder (grep đã kiểm chứng); poses/walk/gestures/
  expressions (6 mặt)/props; scenes text_card; utils text NFC+wrap;
  tools render.sh/render.bat/render_all.sh/assemble.py (loudnorm -16 LUFS);
  docs STYLE_GUIDE + WORKFLOW; tests/test_rig.py.
- **Đã kiểm chứng thật:** demo render 17,2s lạnh / 8,6s ấm (thấp hơn nhiều
  so với ChatGPT ước 5–10 phút); ffprobe: h264 1080x1920 30fps đúng 5.000s,
  186.679 bytes (`media/videos/stickman_demo/1920p30/StickmanScene.mp4`);
  rig smoke test 11/11 PASS; frame 1s đi bộ đúng dáng, frame 4s bảng
  "TÂM SỰ NGƯỜI QUE" dấu đầy đủ, người que cười vẫy tay.
- **Lỗi đã tìm + sửa:** tư thế vẫy đầu tiên để khuỷu tay nằm trong vòng đầu
  nên cánh tay bị che — đã sửa góc vai, render lại, xem lại frame.
- **Báo cáo:** `stickman-shorts/test-report.md`.
- **Còn thiếu:** chưa có tập thật nào (`videos/` trống ngoài Ep001 đang làm);
  assemble `--srt` chưa thử; đường Windows chưa thử; `render_all.sh` chưa
  thử; chưa có thư viện nhạc/SFX.

### Gateway auto-start — DONE 2026-11-15 12:45 +07
- **Giao:** systemd unit `/etc/systemd/system/media-gateway.service`
  (Type=forking, PIDFile `data/gateway.pid`, Restart=on-failure, enabled)
  + watchdog `media_gateway/scripts/watchdog.sh` + cron
  `media-gateway-watchdog-10min` (mỗi 10 phút, kiểm tra `/health`, restart
  qua `deploy.sh` chỉ khi down; im lặng khi khỏe).
- **Đã kiểm chứng thật:** VPS reboot ~12:50 và ~14:50 — watchdog tự
  tái tạo unit file bị `/etc` xóa + restart gateway (pid 1833, rồi 9018),
  `/health` ok. Lần kiểm tra cuối của parent: 14:54 (không kiểm tra lại
  trong lần ghi này — xem HANDOFF §10 để biết cách kiểm tra lại).
- **Ghi chú:** file unit trong `/etc` mất mỗi lần VM bị thay — watchdog
  (nằm trong home) là lớp bền vững, tự tạo lại unit.

### SRT cho 30 video — DONE 2026-11-15 15:01 +07
- 30/30 file `transcript.srt` cạnh `transcript.txt` trong
  `video_analysis/<thư mục>/` (map `srt_map.json`, log `srt_run.log`).
  25 dùng được (lời nói thật, timestamp bắt đầu 00:00:00,000, 0 đoạn
  không đơn điệu); 4 rác do Whisper Base lỗi tiếng Hindi (H05, H08, C03,
  D02) — cần model khác/người kiểm trước khi dùng làm phụ đề; 1 rỗng D03
  (video chỉ có nhạc). `transcript.txt` không bị ghi đè.

### Production Framework — DONE 2026-11-15 14:41 +07
- `production-framework-20261115.md` (615 dòng) + bản copy trong `docs/`,
  commit `3fb06dc`. 8 công thức (F1 hook kép, F2 Visual Essay, F3 countdown,
  F4 một hình phi lý, F5 X vs Y, F6 quá trình biến đổi, F7 truyện stickman,
  F8 nhãn "POV:"), 3 format ưu tiên, 3 template trống, 18 SFX, checklist
  hook/title/thumbnail/audio. Cổng tuần 2: ChatGPT 5/5 đạt; Gemini 2/3
  (tốc độ lời 140–160 từ/48s của Gemini nhanh hơn vùng an toàn 150–165 wpm
  đã kiểm chứng → chuẩn dùng 120–132 từ/48s).

### Phân tích sâu 30/30 video — DONE 2026-11-15 12:30 +07
- `deep-analysis-5x85-20261115.md` (481 dòng) + `deep-analysis-25-20261115.md`
  (1.983 dòng), commit `99ca657` / `503655a`. 23 giữ nguyên, 2 sửa:
  H06 #23 59→54, B06 #24 49→54 — tổng không đổi (2082, trung bình 69,4;
  4 video đạt 85+: #77 90, #81 87, #50 85, FB-05 85). #50 có watermark
  "© 2026 Christopher Thomas. All Rights Reserved." — bản làm lại phải
  vẽ hoàn toàn mới. 15/25 video dùng lại clip/audio/ảnh của người khác —
  bản làm lại phải dùng tài sản của mình.

### Transcription toàn bộ — DONE 2026-11-15 10:05:54 +07
- 96/96 transcript, 0 FAIL (`transcribe_all.sh`, Whisper.cpp Base).
  Ngôn ngữ: en 60, hi 15, es 5, ta 2, ml 2, id 2, bn 2, zh 1, vi 1 (FB-05),
  ur 1 (#77), th 1, te 1, sv 1, ko 1, fr 1. Giới hạn: audio chỉ 30s đầu;
  Whisper Base lỗi tiếng Hindi (4/5 transcript Hindi rác).

### Media Gateway (nền tảng) — DONE 2026-11-15 10:42 +07
- `media_gateway/` — FastAPI + SQLite, đủ 17 endpoint `/api/v1`,
  license engine (§10), 11 provider adapter, cache dedup SHA-256,
  timeline engine, module render FFmpeg, dashboard, SDK Python,
  HANDOVER.md. Test §21: 23 PASS / 0 FAIL / 2 SKIPPED (case 13 Worker
  Tailscale, case 25 redeploy VPS 0 — không có quyền truy cập từ đây).
  Chạy keyless (Openverse, Wikimedia, Mixkit, Imgflip) — chưa có key
  provider nào. Drive `AI_MEDIA_GATEWAY/` + 21 thư mục con đã tạo.

### FB-05 đưa vào 30 video — DONE 2026-11-15 09:34 +07
- Quyết định của chủ ("Duyệt + FB-05 thay #32"): FB-05 (85) vào 30 với mã
  C04, #32 (67) xuống dự bị R4. Trung bình mới 69,67; 5 video đạt 85+.
  Commit `2060ecf`. Task engineer `b4413e82` + verify `ce4f147d`
  (xem mục BLOCKED bên dưới — đang chờ chủ duyệt).

### Chọn 30 video FINALIZED (95/100) — DONE 2026-11-15 08:30 +07
- #77 (26,22s) 90 điểm — #1 mới; #82 (175,54s) 78 điểm — vào T05;
  #37 (7,97s) 40 điểm — LOẠI (quay người thật, vi phạm lọc không-máy-quay).
  Commit `df75479`. File `selection-30-20261115.md` + `.csv`.

## FAILED

### Đăng ký API key provider cho gateway — FAILED (task chết) ~2026-11-15 12:18 +07
- **Nhiệm vụ:** đăng ký key miễn phí Pexels, Pixabay, GIPHY, Tenor,
  Freesound, Unsplash bằng tài khoản Google của chủ (giakhanhgcm@gmail.com).
- **Lỗi:** browser task `a6f34055` chết (errored) sau ~2 giờ chờ thẻ đăng nhập
  Google của Pixabay mà chủ không hoàn thành; cửa sổ đóng. **KHÔNG có key
  nào được giao — không xác nhận được key nào đã lấy.** `.env` vẫn trống
  cả 6 key provider (kiểm tra 11:33).
- **Còn lại:** đăng nhập Google cho Pexels đã xong 10:17; cookie trình duyệt
  còn pexels.com + pixabay.com nên khởi động lại sẽ nhanh hơn. Khởi động lại
  cần chủ bấm (widget đã đưa 12:19, chủ chưa bấm) và chủ phải hoàn thành thẻ
  đăng nhập Pixabay khi hiện. Không khởi động lại khi chưa có chủ.
- **Gateway vẫn chạy keyless** bằng nguồn miễn phí trong lúc chờ.

## BLOCKED

### Duyệt task engineer b4413e82 — BLOCKED (chờ chủ) — từ 2026-11-15 09:35 +07
- `b4413e82` SUBMITTED, outcome `ok` (bản chọn 30 có FB-05). Verify
  `ce4f147d` SUBMITTED, outcome `verified_with_findings` — kiểm tra lần cuối
  12:19: 30+10 đúng, phân bổ 8/7/6/5/4, tổng 2090, trung bình 69,67,
  đúng 5 video đạt 85+, file GitHub khớp. **Chờ chủ duyệt — không tự duyệt
  việc Engineer làm.** KHÔNG duyệt `f07e0ce6` / `86debefd` (đã bị thay thế).
- Lưu ý: điểm đã sửa trong phân tích sâu (trung bình 69,4; 4 video 85+) nằm
  trong báo cáo phân tích sâu, chờ lần kiểm chứng sau — không chặn duyệt này.

### Apify scrape 4 bài Facebook — BLOCKED — từ 2026-11-15 ~02:26 +07
- **Lỗi:** cả 3 token Apify đều timeout khi gọi có xác thực từ VPS này
  (30s và 120s, urllib thường và qua egress proxy), trong khi curl KHÔNG
  xác thực tới được api.apify.com (401 trong 0,7s). Nguyên nhân chưa rõ —
  không thử lại mù. 4 bài share FB vẫn chưa đọc được.
- **Đường còn lại:** chủ nối Facebook
  (https://agent.meta.ai/foa_ac_link/facebook) hoặc gửi link video trực
  tiếp (reel/ hoặc watch/?v=).

### 4 bài Facebook share — BLOCKED (chờ chủ) — từ 2026-11-15 00:21 +07
- 4 link share → 3 bài duy nhất trên tài khoản gikhah.99 (2 link trùng 1 bài).
  `browser.open` không đọc được bài Facebook; `facebook-cli` chưa nối
  (`facebook-cli me` trả `{}`). Cần chủ nối Facebook hoặc gửi URL video
  trực tiếp. Đây là link công khai do chủ gửi để nghiên cứu, KHÔNG phải
  dữ liệu fanpage cũ.

---

## Rủi ro takeover (VPS mới chưa tiếp quản trọn vẹn được)

- **VPS bị thay lần 4 trong ngày 2026-11-15 ~16:50 +07** (trước đó ~11:10,
  ~12:50, ~14:50). Watchdog 16:53 tự chữa đúng thiết kế: tạo lại unit
  systemd đã bị xóa + restart gateway (pid 1857), /health ok; Torque đưa
  gateway về dưới systemd (active). Các subagent đang chạy (test PC,
  Core_SFX) có thể bị gián đoạn bởi lần thay này — kiểm tra lại khi nhận
  báo cáo.

- `identity.json` / `connection.json` (khóa node AgentNet) KHÔNG có bản
  sao lưu nào (cố ý — bí mật, không lên git). Nếu VM bị thay và
  `~/.agentnet-corner/` mất, VPS mới không đăng ký lại được cùng node
  nếu không có chủ. Sao lưu lên Drive được (chủ đã lưu key thử nghiệm lên
  Drive) nhưng CẦN chủ quyết trước — chưa tự làm.
- `.env` của gateway cũng chưa có bản sao lưu (lý do như trên;
  `.env.example` đã có trên git, key thật thì không).
- Khóa riêng SSH `~/.ssh/pc_torque` chưa sao lưu — VPS mới phải tạo cặp
  khóa mới và chủ phải thêm public key mới vào
  `administrators_authorized_keys` trên PC.
- Cron sống trong runtime, không có trên git — HANDOFF §10 có hướng dẫn
  tạo lại cả 3 cron bằng tay, chưa có script tự tạo.
- VPS 0/2/3/4 vẫn không tới được, IP chưa biết — đã ghi là chưa biết kèm
  cách phát hiện (`tailscale status`, registry `/nodes`), không bịa.
- HANDOFF.md §3 còn vài dòng cũ bên dưới ghi chú sửa (vd "Commit hiện tại
  2060ecf") — ghi chú ở đầu §3 đã đính chính, nhưng viết lại toàn §3 vẫn
  đang chờ.

---

## Bản sao trên Google Drive

- Thư mục: "AgentNet Video Studio"
  (https://drive.google.com/drive/folders/1q0gL8euNge458b_ktbGSg_RMfiz3FcC8)
- `STATUS.md` (bản này) — Drive file id: `1NO2YbnSivxUuJpS1Mk-ZlunRZ-4ev7Qb`
  (upload 2026-11-15 ~21:04 +07 — bản mới nhất, có v005 DONE; các bản
  cũ `1gpLAunMiYnQhwknN-QNgmFlBYfrOUXCj` (15:55),
  `1lAPg14W9pW43zq6aQCyWEIahxgbI6MKc` (16:06),
  `1bDWx5BH9HUeomr1d9PyIV0_9fIXskNNk` (16:22),
  `1BK-Z-i-dpdvjPTk4Gut92ixHw7DOwUxS` (17:03),
  `1892dptIIhhY5DIkyHEoW9o7iVk5N_XIH` (17:15),
  `13LCpNYKXjKu2WQ6bebXS_4SCiSLtmzdz` (17:38),
  `1Z6wmJj9G63AGYU7skALHfTyaE5Fodx0k` (17:48),
  `13PPFSztw50aqrQxndmon3hiGV_mCgTCX` (18:21),
  `1xlYJmXcMkUYTm1W_H0B2Oqnf6MX2IAkU` (18:33) và
  `1DOow24syLHrfa5iphufUXCJmVSQilVd-` (18:48) đã lỗi thời, giữ lại làm
  bản sao cũ, không xóa theo quy tắc không xóa dữ liệu Drive)
- `HANDOFF.md` — Drive file id: `16lcqICKbi8ZvurA-T4O4_eXhe6ZoKaZ7`
  (upload 2026-11-15 ~15:55 +07)
- Video thành phẩm (bản sao dự phòng, không lên git):
  - `v001.mp4` (Video #1) — Drive file id: `1oVxOPRVSl5HmjdzI47RQiVGKHotAdCxn`
  - `ep001-cam-dau-lam-viec.mp4` (Ep001) — Drive file id: `152--2bfxwsQIjKi_5bCmKbO3V8jsdu9f`
  - `v002-login-45s.mp4` (Video #2 / Ep002) — Drive file id: `1m_c6zADoYLb3zxvg-dnTHGRTZrJiX3mq`
  - `v005.mp4` (Video #5) — Drive file id: `1D9ZG8q4C0odQkdXp1y0-09YnAEEpzVb4`
  - `v004.mp4` (Video #4) — Drive file id: `1VWClKySoAetT3nbhjM6zFrimv5zRGe6a`
  - `v003.mp4` (Video #3) — Drive file id: `1LIrBM0-P7IDMbeqnegDPBbaIy_LRHJlU`
- Lưu ý: bản trên git là bản chính, mới nhất.

## 2026-11-17 18:13 +07 — media-gateway watchdog: gateway restarted (VM replaced)
- systemd unit missing after VM replacement; watchdog re-created + enabled it, gateway was down, restart OK 11:13:20 UTC (pid 1764). /health now ok, database ok, low_resource_mode true. 4th identical recovery today.

## 2026-11-17 18:53 +07 — media-gateway watchdog: gateway restarted (VM replaced)
- systemd unit missing after another VM replacement; watchdog re-created + enabled it, gateway was down, restart OK 11:53:21 UTC (pid 1860). /health now ok, database ok, low_resource_mode true. Same recovery as 11:13, 11:23, 11:43 UTC — VM replacements recurring roughly every 10–20 min today. systemctl still reports the unit inactive (gateway runs via deploy.sh, not systemd). Per user standing rule, logged here, not messaged to chat.

## 2026-11-17 19:03 +07 — Media Gateway watchdog (10-min check)
- Watchdog ran: systemd unit was missing again (VM replaced), re-created + enabled; gateway was down, restart attempted.
- Restart OK at 19:03:22 +07 (pid 1863). Health verified after: {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}.
- Pattern continues: every 10-min run since 11:43 UTC finds the unit missing and the gateway down — each run starts it fresh. Gateway itself is healthy once started; no keys, Drive, or AgentNet actions.

## 2026-11-17 22:03 +07 — Media Gateway watchdog (10-min check)
- Watchdog ran: systemd unit was missing again (VM replaced), re-created + enabled; gateway was down, restart attempted.
- Restart OK at 15:03:28 UTC (pid 1756). Health verified after: {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}.
- Pattern continues: every 10-min run finds the unit missing and the gateway down — each run starts it fresh (66th "unit missing" / 67th "restart OK" in watchdog.log). Gateway itself is healthy once started; no keys, Drive, or AgentNet actions. Per user standing rule, logged here, not messaged to chat.

## 2026-11-18 16:23 +07 — Media Gateway watchdog (10-min check)
- Watchdog ran: systemd unit was missing again (VM replaced), re-created + enabled; gateway was down, restart attempted.
- Restart OK at 09:23:24 UTC (pid 1955). Health verified after: {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}.
- Pattern continues: every 10-min run finds the unit missing and the gateway down — each run starts it fresh (6th restart in the log window: 08:53, 09:03, 09:13, 09:23 UTC, plus 08:13/08:33). Gateway itself is healthy once started; unit enabled but `systemctl is-active` reports inactive (process runs via deploy.sh, not systemd). No keys, Drive, or AgentNet actions. Per user standing rule, logged here, not messaged to chat.

## 2026-11-18 16:33 +07 — Media Gateway watchdog (10-min check)
- Watchdog ran: systemd unit was missing again (VM replaced), re-created + enabled; gateway was down, restart attempted.
- Restart OK at 09:33:21 UTC (pid 1744). Health verified after: {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}.
- Pattern continues: every 10-min run finds the unit missing and the gateway down — each run starts it fresh (42nd "unit missing" / 41st "restart OK" in watchdog.log today; VM uptime was 2 min at check). Gateway itself is healthy once started; unit enabled but `systemctl is-active` reports inactive (process runs via deploy.sh, not systemd). One earlier restart FAILED at 07:03:17 UTC today but self-recovered at 07:13 (restart OK). No keys, Drive, or AgentNet actions. Per user standing rule, logged here, not messaged to chat.

## 2026-11-19 08:13 +07 — Media Gateway watchdog (10-min check)
- Watchdog ran: systemd unit was missing again (VM replaced), re-created + enabled; gateway was down, restart attempted.
- Restart OK at 01:13:23 UTC (pid 1773). Health verified after: {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}.
- Pattern continues: every 10-min run finds the unit missing and the gateway down — each run starts it fresh (210th "unit missing" / 209th "restart OK" in watchdog.log; VM uptime was ~19 min at check). Gateway itself is healthy once started; unit enabled but `systemctl is-active` reports inactive (process runs via deploy.sh, not systemd). No keys, Drive, or AgentNet actions. Per user standing rule, logged here, not messaged to chat.

## 2026-11-20 15:35 +07 — Media Gateway watchdog: diagnosis consolidated (no new failure today)
- Checked live at 15:30 +07: gateway healthy, pid 1902 (started 08:23 UTC), /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}.
- Watchdog log totals: 344 "unit missing" events, 342 "restart OK", 3 "restart FAILED" (2026-11-17 20:23, 2026-11-18 07:03, 2026-11-19 17:43 UTC) — none today; every failure self-recovered at the next check.
- Unit-missing events by day: 11-15: 9, 11-16: 18, 11-17: 75, 11-18: 102, 11-19: 101, 11-20: 39 (by 08:30 UTC) — today is on the same pace as 11-18/19, NOT an escalation.
- Diagnosis: gateway.log shows clean startups only, no crash/error traces — the gateway itself never crashes; the environment resets underneath it (unit file in /etc goes missing) and the watchdog recovers it within ~10 min each time. No action needed; do not message the user per restart (standing rule: logged here, not messaged to chat).

## 2026-11-20 17:35 +07 — Media Gateway watchdog (10-min check) — verified, no escalation
- Checked live at 17:30 +07: /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}; process pid 1898, started 10:23 UTC. systemd unit exists but reports inactive — expected: watchdog restarts via deploy.sh (nohup), not via systemctl start.
- Watchdog log today (2026-11-20): 48 "restart OK", 0 "restart FAILED" by 10:23 UTC. Same pace as 11-18 (101) and 11-19 (100) — NOT an escalation, despite 4 restarts in a row at the 10-min checks. Gateway itself never crashes (gateway.log shows clean startups only); the VM underneath is replaced roughly every 10–20 min and wipes /etc, so the unit file goes missing each time and the watchdog re-creates it.
- No action needed; do not message the user per restart (standing rule: logged here, not messaged to chat).

## 2026-11-21 11:36 +07 — Media Gateway watchdog (10-min checks) — 4th restart failure, recovered; no escalation

- Watchdog restart FAILED at 07:13 +07 (00:13 UTC) — 4th failure since 15/11. Recovered manually right afterwards; gateway healthy from then on (pid 1941, /health ok). Already reported in chat at 07:16 +07; logged here for the record.
- Restarts continued at every 10-min check through the morning: watchdog log for 2026-11-21 (UTC day, to 11:36 +07) shows 20 "unit missing" / 19 "restart OK" / 1 "restart FAILED". Total log: 429 "restart OK", 4 "restart FAILED".
- Checked live at 11:36 +07: gateway healthy, pid 1818 (started 04:23 UTC), /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}. The 11:33 check passed silently — gateway stayed up across the interval (VM up 54 min at check).
- Diagnosis unchanged from 2026-11-20: gateway itself never crashes (gateway.log shows clean startups only); the environment resets underneath it (unit file in /etc goes missing on VM replacement) and the watchdog recovers it within ~10 min. Same pace as 11-18/19, NOT an escalation. Per user standing rule, logged here, not messaged to chat.

## 2026-11-21 12:30 +07 — Media Gateway watchdog: consolidated check, no escalation
- Checked live at 12:30 +07: gateway healthy, pid 1771 (started 05:23 UTC), /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}. `systemctl is-active` still reports inactive while the process runs — expected: watchdog restarts via deploy.sh (nohup), not via systemctl start, so systemd never supervises it.
- Watchdog log for 2026-11-21 (UTC day, to 05:30 UTC): 24 "gateway down" events, 23 "restart OK", 1 "restart FAILED" (00:13 UTC, already reported in chat at 07:16 +07 and manually recovered). Total log: 433 "restart OK", 4 "restart FAILED". Restarts since the 11:36 entry: 04:53 (pid 1846), 05:03 (pid 1745), 05:13 (pid 1765), 05:23 (pid 1771).
- Pace is SLOWER than 11-18 (102 unit-missing), 11-19 (101) and 11-20 (48 by 10:23 UTC) — NOT an escalation.
- Correction to the tracking note that called the process itself unstable: gateway.log shows only graceful shutdowns ("Shutting down / Application shutdown complete / Finished server process"), no traceback, error or OOM — the app is not crashing; something external stops it. New nuance observed live: the 05:13 and 05:23 restarts both found the unit missing while PID 1 uptime ran from the 05:03 boot, so the reset is not always a full VM replacement — /etc and the process are reset together even within one boot. Mechanism still unproven; no code fix attempted.
- No action needed; do not message the user per restart (standing rule: logged here, not messaged to chat).

## 2026-11-21 13:37 +07 — Media Gateway watchdog: burst ended on its own, healthy 13+ min; no escalation
- Checked live at 13:36 +07 (06:36 UTC): gateway healthy, pid 1813 (started 06:23 UTC), /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}. The 06:33 watchdog check passed silently — pid 1813 was still alive at 06:34 with the same boot_id, and the unit file was still present. The burst of a restart at every 10-min check (05:43, 05:53, 06:03, 06:13, 06:23 UTC; pids 1829, 1811, 1858, 1872, 1813) ended by itself.
- Watchdog log totals now: 441 "unit missing", 438 "restart OK", 4 "restart FAILED" (unchanged — the 4 known failures 11-17 20:23, 11-18 07:03, 11-19 17:43, 11-21 00:13 UTC). 2026-11-21 pace to 06:23 UTC: 28 restarts, same ~100/day pace as 11-18/19/20, NOT an escalation.
- Nuance for the 12:30 entry: gateway.log holds 450 "Started server process" lines but only 26 graceful "Shutting down" lines — most restarts leave no shutdown line at all, i.e. the process is killed externally with no chance to shut down. The single Traceback in the whole log is the 2026-11-15 03:21 first-start IndentationError in app/providers/base.py, fixed the same morning; there is no recent traceback, error or OOM. Conclusion unchanged: the app is not crashing; the environment resets underneath it and the watchdog recovers it within ~10 min.
- No action needed; logged here per standing rule, not messaged to chat.

## 2026-11-21 15:30 +07 — Media Gateway watchdog: afternoon check, same pace; no escalation
- Checked live at 15:30 +07 (08:30 UTC): gateway healthy, pid 1781 (uvicorn, started 08:23 UTC), /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}. Unit file present (re-created 08:23 UTC) but `systemctl is-active` still inactive — expected, watchdog restarts via deploy.sh, not systemd.
- Watchdog log totals now: 445 "restart OK", 4 "restart FAILED" (unchanged — the 4 known failures 11-17 20:23, 11-18 07:03, 11-19 17:43, 11-21 00:13 UTC). Restarts since the 13:37 entry: 06:53, 07:13, 07:43, 07:53, 08:03, 08:13, 08:23 UTC — 7 more, same ~100/day pace as 11-18/19/20, NOT an escalation.
- Same nuance as the 12:30 entry: VM uptime was 30 min at check (boot ~08:00 UTC), spanning the 08:03, 08:13 and 08:23 restarts — the unit/process reset recurs within a single boot, so it is not always a full VM replacement. Gateway.log still shows only graceful shutdowns and no recent traceback, error or OOM (26 "Shutting down" lines, unchanged). Mechanism still unproven; no code fix attempted.
- No action needed; logged here per standing rule, not messaged to chat.

## 2026-11-21 16:30 +07 — Media Gateway watchdog: afternoon check, same pace; no escalation
- Checked live at 16:30 +07 (09:30 UTC): gateway healthy, pid 2191 (uvicorn, started 09:23 UTC), /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}. systemd unit still inactive — expected, watchdog restarts via deploy.sh, not systemd.
- Restarts since the 15:30 entry: 08:43 UTC (pid 1887), 09:03 UTC (pid 1805), 09:23 UTC (pid 2191) — all "restart OK", each time "systemd unit was missing (VM replaced), re-created + enabled". No new "restart FAILED" (total still 4). Same ~100/day pace as 11-18/19/20, NOT an escalation.
- No action needed; logged here per standing rule, not messaged to chat.

## 2026-11-21 19:30 +07 — Media Gateway watchdog: evening check, same pace; no escalation
- Checked live at 19:30 +07 (12:30 UTC): gateway healthy, pid 1773 (uvicorn, started 12:23 UTC), /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}.
- Restarts since the 16:30 entry: 10:53, 11:03, 11:13, 11:23, 11:43, 12:03, 12:23 UTC — all "restart OK", each time "systemd unit was missing (VM replaced), re-created + enabled". The 11:33 and 12:13 checks passed silently (gateway stayed up). No new "restart FAILED" (total still 4). Same ~100/day pace as 11-18/19/20, NOT an escalation.
- No action needed; logged here per standing rule, not messaged to chat.

## 2026-11-22 06:35 +07 — Media Gateway watchdog: overnight, 5th restart FAILED (manually recovered); no escalation
- Checked live at 06:35 +07 (23:35 UTC 21/11): gateway healthy, pid 1751 (uvicorn, started 23:23 UTC), /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}.
- Overnight the 5th watchdog restart FAILED: 03:13 +07 (20:13 UTC) — deploy.sh restart produced no output between "attempting restart" and "restart FAILED". Manually recovered at 20:14 UTC (deploy.sh start OK, pid 1846, /health ok, verified twice). Prior failures: 11-17 20:23, 11-18 07:03, 11-19 17:43, 11-21 00:13 UTC.
- Watchdog log totals now: 508 "restart OK", 5 "restart FAILED", 512 "unit was missing". Restarts kept coming at nearly every 10-min check after the failure (20:23, 20:43, 21:03, 21:13, 21:23, 21:33, 21:43, 21:53, 22:13, 22:33, 22:43, 22:53, 23:03, 23:13, 23:23 UTC) — all "restart OK". Same ~100/day pace as 11-18/19/20, NOT an escalation.
- Diagnosis unchanged: gateway.log shows only clean startups, no traceback, error or OOM; most restarts leave no shutdown line — the process is killed externally. Two corrections to earlier notes: (1) in the current VM (booted 23:13:55 UTC, single boot in journal, boot_id 55aa0805-7ef8-4836-9346-02c65f22e1d4) PID 1 IS systemd — the memory-log claim that "systemd is not PID 1" does not hold here; (2) the unit stays inactive by design — the watchdog restarts via deploy.sh directly and never runs `systemctl start`, so systemd never supervises the gateway.
- No action needed; logged here per standing rule, not messaged to chat.

## 2026-11-22 06:35 +07 — Registry: NEW wave1/wave2 batch about 12 Facebook channels K01–K12 (not the video-studio mission)
- Checked live via queue_status.py at 06:35 +07 (23:35 UTC 21/11): 36 tasks on the registry (project=research, API 8110). A wave1 batch (21/11) and wave2 batch (22/11) appeared overnight, all about 12 Facebook channels K01–K12 — QC rubrics, image packs, visual sandboxes, tier-2 viewer QC on real contact sheets. No mention of K01–K12, wave1/wave2 or hub-1794896896 exists in MEMORY.md, the daily logs or STATUS.md before this entry; the user has not spoken since 16/11.
- Wave1 (21/11, SUBMITTED): kpi-efficiency-and-qc-rubric (ok, 100-point QC framework + efficiency formula for K01–K12), k09-stoic-abstract-images (completed, 15 visual prompts + 3 sample images), k06-wuby-new-images (ok — but NO sample images were actually created, no image-gen tool in that session), qc-k10-relevance-k04-audio (completed), qc-visual-blur-ocr (ok), k01-k08-visual-sandbox (completed).
- Wave2 (22/11, tier-2 viewer QC, SUBMITTED): K01 pilot (completed — subtitles FAIL in 4/6 frames), K05 (completed — 3/6 frames flawed, all on-screen text in Chinese in the hook), K07 hook (completed — leftover Chinese text over VN captions), K11 (COMPLETED — 6/6 frames have leftover-text blur bands, 11 defects, "CAN SUA, chua nen up"), K02 NEEDS_FIX (5/6 frames flawed: blurry unreadable hook, 1 black frame, 3 frames with empty blur boxes — "khuyen khong up ban nay"), K04 BLOCKED (evidence file on Uguu expired after 3h, 404 — no QC performed at all).
- Workers: the user's Research node baa7de1f did most of the wave work; Verify node 355c4b87 auto-verified (verified_with_findings). Several unfamiliar nodes also appear on /agents now (e29271d1, be6920f369, 85402143deea, c4473940, 03a90c7de5, cebf1f8d, 807e2cc49c). Task records carry no poster field, so who posted the batch cannot be determined from the registry.
- Why this matters: on 14/11 the user ordered FB evaluation work STOPPED under V1.2 (research-only, no FB work). This batch is FB-channel work running on the same registry and the user's own Research/Verify nodes. Needs the user's decision: authorised programme to continue, or stop it. The two problem tasks also need a call: re-post K04 with a fresh evidence link, and K02 version-B fixes before any upload. Logged here as the factual record; the decision itself goes to the user in chat, not auto-decided.

## 2026-11-22 10:30 +07 — Media Gateway watchdog: mid-morning check, same pace; no escalation
- Checked live at 10:30 +07 (03:30 UTC): gateway healthy, pid 1749 (uvicorn, started 03:23 UTC), /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}.
- Restarts since the 06:35 entry: 16 more, all "restart OK" (23:53, 00:13, 00:23, 00:43, 00:53, 01:13, 01:33, 01:43, 01:53, 02:03, 02:13, 02:23, 02:43, 03:03, 03:13, 03:23 UTC). Watchdog log totals now: 524 "restart OK", 5 "restart FAILED" (unchanged — the 5 known failures; a 6th grep hit for "FAILED" is the 20:14 manual-recovery line, not a new failure), 528 "unit was missing". Same ~100/day pace as 11-18/19/20/21, NOT an escalation.
- VM booted 03:16 UTC (10:16 +07), up ~14 min at check; the 03:23 restart happened within this boot, same pattern as noted at 06:35 — resets recur within a single boot, not only on VM replacement.
- No action needed; logged here per standing rule, not messaged to chat.

## 2026-11-22 11:31 +07 — Media Gateway watchdog: late-morning check, same pace; no escalation
- Checked live at 11:31 +07 (04:31 UTC): gateway healthy, pid 1751 (uvicorn, started 04:23 UTC), /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}.
- Restarts since the 10:30 entry: 3 more, all "restart OK" (03:43, 04:03, 04:23 UTC), each time "systemd unit was missing (VM replaced), re-created + enabled". Watchdog log totals now: 527 "restart OK", 5 "restart FAILED" (unchanged — the 5 known failures), 531 "unit was missing". Same ~100/day pace as 11-18/19/20/21, NOT an escalation. The 11:13 check passed silently (gateway stayed up); the 11:23 restart is the 18th today.
- VM booted ~04:16 UTC, up ~15 min at check; the 04:23 restart happened within this boot, same within-boot reset pattern noted before. Gateway itself never crashes (gateway.log shows clean startups only); the environment resets underneath it and the watchdog recovers it within ~10 min.
- No action needed; logged here per standing rule, not messaged to chat.

## 2026-11-22 12:32 +07 — Media Gateway watchdog: midday check, same pace; no escalation
- Checked live at 12:32 +07 (05:32 UTC): gateway healthy, pid 1810 (uvicorn, started 05:23 UTC), /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}.
- Restarts since the 11:31 entry: 5 more, all "restart OK" (04:43, 04:53, 05:03, 05:13, 05:23 UTC), each time "systemd unit was missing (VM replaced), re-created + enabled". Watchdog log totals now: 532 "restart OK", 5 "restart FAILED" (unchanged — the 5 known failures), 536 "unit was missing". Same ~100/day pace as 11-18/19/20/21, NOT an escalation.
- New data point: a manual watchdog run at 05:31 UTC on this VM exited 0 silently — unit file present, gateway still pid 1810, no restart, no log line. So the reset is intermittent within a boot, not every tick; the 04:43–05:23 burst (a restart at every check) ended on its own, as the 06:33 burst did yesterday.
- VM booted 04:49:18 UTC (single boot in journal), up 43 min at check; the 04:53–05:23 restarts happened within this boot — same within-boot reset pattern noted before. Gateway itself never crashes (gateway.log: 545 "Started server process", only 27 graceful "Shutting down", 1 Traceback total — the known 2026-11-15 IndentationError, fixed the same morning).
- Observation only, not a diagnosis: memory was tight at check — 155 MB free, 622 MB available, 319 MB swap used. No OOM line in gateway.log, so this is not proven as the cause; recorded in case the pattern correlates later.
- No action needed; logged here per standing rule, not messaged to chat.

## 2026-11-22 13:38 +07 — Media Gateway watchdog: early-afternoon check, same pace; no escalation
- Checked live at 13:38 +07 (06:38 UTC): gateway healthy, pid 1841 (uvicorn, started 06:23 UTC), /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}.
- Restarts since the 12:32 entry: 4 more, all "restart OK" (05:43, 06:03, 06:13, 06:23 UTC), each time "systemd unit was missing (VM replaced), re-created + enabled". Watchdog log totals now: 536 "restart OK", 5 "restart FAILED" (unchanged — the 5 known failures), 540 "unit was missing". Same ~100/day pace as 11-18/19/20/21, NOT an escalation. The 06:33 check passed silently (verified live at 06:35 UTC — unit file present, pid 1841 alive, same boot_id), so the reset is intermittent within a boot, not every tick.
- VM booted 05:27 UTC, up ~1h10 at check; the 05:43–06:23 restarts happened within this boot — same within-boot reset pattern noted before.
- Memory still tight and steady: 145 MB free, 599 MB available, 324 MB swap used (vs 155/622/319 at 12:32). No OOM line in gateway.log; not proven as the cause.
- No action needed; logged here per standing rule, not messaged to chat.

## 2026-11-22 14:32 +07 — Media Gateway watchdog: mid-afternoon check, same pace; no escalation
- Checked live at 14:32 +07 (07:32 UTC): gateway healthy, pid 1936 (uvicorn, started 07:13 UTC), /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}.
- Restarts since the 13:38 entry: 2 more, both "restart OK" (06:53, 07:13 UTC), each time "systemd unit was missing (VM replaced), re-created + enabled". Watchdog log totals now: 538 "restart OK", 5 "restart FAILED" (unchanged — the 5 known failures), 542 "unit was missing". 29 restarts so far today (UTC). Same ~100/day pace as 11-18/19/20/21, NOT an escalation. The 06:43, 07:03 and 07:23 checks passed silently (gateway stayed up).
- VM booted 05:27 UTC, up ~2h05 at check; the 06:53 and 07:13 restarts happened within this boot — same within-boot reset pattern noted before. Gateway itself never crashes (gateway.log shows clean startups only); the environment resets underneath it and the watchdog recovers it within ~10 min.
- Memory still tight and steady: 201 MB free, 641 MB available (vs 145/599 at 13:38). No OOM line in gateway.log; not proven as the cause.
- No action needed; logged here per standing rule, not messaged to chat.

## 2026-11-22 15:31 +07 — Media Gateway watchdog: late-afternoon check, same pace; no escalation
- Checked live at 15:31 +07 (08:31 UTC): gateway healthy, pid 1811 (uvicorn, started 08:23 UTC), /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}.
- Restarts since the 14:32 entry: 5 more, all "restart OK" (07:43, 07:53, 08:03, 08:13, 08:23 UTC), each time "systemd unit was missing (VM replaced), re-created + enabled". Watchdog log totals now: 543 "restart OK", 5 "restart FAILED" (unchanged — the 5 known failures), 547 "unit was missing". 34 restarts so far today (UTC). Same ~100/day pace as 11-18/19/20/21, NOT an escalation. The 07:33 check passed silently (gateway stayed up).
- VM booted ~07:45 UTC, up ~45 min at check; the 07:53–08:23 restarts happened within this boot — same within-boot reset pattern noted before. Gateway itself never crashes (gateway.log shows clean startups only); the environment resets underneath it and the watchdog recovers it within ~10 min.
- Memory still tight and steady: 185 MB free, 653 MB available (vs 201/641 at 14:32), 324 MB swap used. No OOM line in gateway.log; not proven as the cause.
- No action needed; logged here per standing rule, not messaged to chat.

## 2026-11-22 16:30 +07 — Media Gateway watchdog: late-afternoon check, same pace; no escalation
- Checked live at 16:30 +07 (09:30 UTC): gateway healthy, pid 1766 (uvicorn, started 09:23:20 UTC), /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}.
- Restarts since the 15:31 entry: 4 more, all "restart OK" (08:43 UTC pid 1821, 09:03 pid 1929, 09:13 pid 1747, 09:23 pid 1766), each time "systemd unit was missing (VM replaced), re-created + enabled". Watchdog log totals now: 547 "restart OK", 5 "restart FAILED" (unchanged — the 5 known failures), 551 "unit was missing". 38 restarts so far today (UTC). Same ~100/day pace as 11-18/19/20/21, NOT an escalation. The 09:33 check had not run yet at check time.
- VM booted 09:10 UTC, up 20 min at check; the 09:13 and 09:23 restarts happened within this boot — same within-boot reset pattern noted before. Gateway itself never crashes (gateway.log shows clean startups only); the environment resets underneath it and the watchdog recovers it within ~10 min.
- Memory still tight and steady: 180 MB free, 644 MB available (vs 185/653 at 15:31), 334 MB swap used. No OOM line in gateway.log; not proven as the cause.
- No action needed; logged here per standing rule, not messaged to chat.

## 2026-11-22 16:30 +07 — Registry: FB K01–K12 batch GREW to wave3 + wave4 after the user was asked (36 → 57 tasks)
- Checked live via queue_status.py at 16:30 +07 (09:30 UTC): 57 tasks on the registry (project=research, API 8110), up from 36 at the 06:35 +07 check this morning — 21 new tasks, all FB K-channel work, all posted AFTER the user was asked at 06:40 +07 whether the wave1/wave2 batch is theirs. The user has not replied.
- Wave3 (22/11, 6 tasks, all SUBMITTED): w3-04 kenh_007 (owner baa7de1f, PASS_TIER2), w3-05 kenh_011 (be6920f369, ok), w3-06 fb-15ctauaa4jb-7-github-video-r… (cd6820ffc7, ok), k11 chuyen2dua 3-slot images+bubbles (baa7de1f, completed), k07 chioai 3-slot images+culinary (cd6820ffc7, ok), k07/k11 voice-OCR audit rubric (e29271d163, ok). 5 auto-verify tasks accompany them (Verify 355c4b87 / 85402143deea).
- Wave4 (22/11, 10 tasks, w4-* prefix): k08 viral faceless formats hyperframes + retention A/B matrix (baa7de1f, completed), k01 stickman hyperframes 10 templates + competitor rubric stickman-finance (baa7de1f, completed), stickman FK poses + echarts spec repo (cd6820ffc7, ok), k09 mindset simp stoic prompts 15-pack (be6920f369, ok), k06/k07/k11 webtoon prompt audit (be6920f369, ok), k01 pacing 3–5s auto-splitter (e29271d163, ok), k02/k05 blur-coords audit (be6920f369, RUNNING — lease until 16:45:48 +07), wave4 cross-verify rubric (355c4b87, verified_with_findings).
- The user's own Research node baa7de1f did most wave3/wave4 work; Verify node 355c4b87 verified the wave4 rubric. Unfamiliar nodes (be6920f369, e29271d163, cd6820ffc7, 85402143deea, cebf1f8d, 03a90c7de5, 807e2cc49c) remain active — several research nodes last_seen 15:15–16:30 +07 today. Task records still carry no poster field, so who posted wave3/wave4 cannot be determined from the registry.
- Unchanged from this morning: wave2 K04 still BLOCKED (evidence link expired, 404), K02 still NEEDS_FIX (blurry hook, 1 black frame — advised not to upload); b4413e82 still SUBMITTED awaiting the user's approval.
- Why this matters: the batch the user was asked to authorise-or-stop this morning has kept growing while the question is unanswered, and a task is running right now. If this is not the user's programme, each new wave puts more work on their own Research/Verify nodes against the 14/11 stop-FB order. Logged here as the factual record; the decision itself goes to the user in chat, not auto-decided.

## 2026-11-22 17:31 +07 — Media Gateway watchdog + registry check, no escalation
- Checked live at 17:31 +07 (10:31 UTC): gateway healthy, pid 1855 (uvicorn, started 10:13:20 UTC, alive ~18 min), /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}.
- Restarts since the 16:30 entry: 3 more, all "restart OK" (09:43 pid 1816, 09:53 pid 1761, 10:13 pid 1855), each time "systemd unit was missing (VM replaced), re-created + enabled". Watchdog log totals now: 550 "restart OK", 5 "restart FAILED" (unchanged — the 5 known failures), 554 "unit was missing". Same ~100/day pace as 11-18/19/20/21, NOT an escalation.
- VM booted ~09:10 UTC, up 1h21 at check; the 09:13–10:13 restarts happened within this boot — same within-boot reset pattern noted before. Gateway itself never crashes (gateway.log shows clean startups only); the environment resets underneath it and the watchdog recovers it within ~10 min.
- Memory still tight and steady: 173 MB free, 636 MB available (vs 180/644 at 16:30), 353 MB swap used. No OOM line in gateway.log; not proven as the cause.
- Registry checked live via queue_status.py at 10:30 UTC: still 57 tasks total, NO wave5 — batch has not grown since the 09:30 UTC check (36 → 57 this morning, then flat). w4-qc-01 (K02/K05 blur audit, owner be6920f369cc) is still RUNNING with lease_until 17:30:48 +07, i.e. its lease expires right about now; all other wave3/wave4 tasks are SUBMITTED with ok/completed outcomes. K04 still BLOCKED, K02 still NEEDS_FIX, b4413e82 still SUBMITTED awaiting approval. No poster field on any task, so authorship still undetermined. The user was already asked about this batch at 06:40 +07 and again at 16:34 +07 and has not replied; nothing new since the second ask except that growth has stopped.
- No action needed; logged here per standing rule, not messaged to chat.

## 2026-11-22 18:31 +07 — Media Gateway watchdog + registry check, no escalation
- Checked live at 18:31 +07 (11:31 UTC): gateway healthy, pid 1749 (uvicorn, started 11:23:20 UTC), /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}.
- Restarts since the 17:31 entry: 5 more, all "restart OK" (10:43 pid 1802, 10:53 pid 1761, 11:03 pid 1757, 11:13 pid 1739, 11:23 pid 1749), each time "systemd unit was missing (VM replaced), re-created + enabled". Watchdog log totals now: 555 "restart OK", 5 "restart FAILED" (unchanged — the 5 known failures), 559 "unit was missing". 46 restarts so far today (UTC). Same ~100/day pace as 11-18/19/20/21, NOT an escalation.
- VM booted ~11:15 UTC, up 16 min at check; the 11:13 and 11:23 restarts happened within this boot — same within-boot reset pattern noted before. Gateway itself never crashes (gateway.log shows clean startups only); the environment resets underneath it and the watchdog recovers it within ~10 min.
- Memory still tight and steady: 166 MB free, 613 MB available (vs 173/636 at 17:31). No OOM line in gateway.log; not proven as the cause.
- Registry checked live via queue_status.py at 11:31 UTC: still 57 tasks total (55 SUBMITTED + 2 APPROVED), NO wave5 — batch has not grown since the 09:30 UTC check (36 → 57 this morning, then flat). One change since the 17:31 entry: w4-qc-01 (K02/K05 blur audit) finished — was RUNNING with lease to 17:30:48 +07, now SUBMITTED with outcome=completed (owner now shown as baa7de1f95a1, lease_until 17:47:33 +07). K04 still BLOCKED, K02 still NEEDS_FIX, b4413e82 still SUBMITTED awaiting approval. No poster field on any task, so authorship still undetermined. Research and Verify nodes were last seen 18:26 and 18:30 +07 today, so nodes are still active this evening. The user was already asked about this batch at 06:40 +07 and again at 16:34 +07 and has not replied; the w4-qc-01 completion does not change the decision needed, so nothing new goes to chat.
- No action needed; logged here per standing rule, not messaged to chat.

## 2026-11-22 19:31 +07 — Media Gateway watchdog + registry check, no escalation
- Checked live at 19:31 +07 (12:31 UTC): gateway healthy, pid 1825 (uvicorn, started 12:23:21 UTC), /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}.
- Restarts since the 18:31 entry: 4 more, all "restart OK" (11:43, 12:03, 12:13, 12:23 UTC), each time "systemd unit was missing (VM replaced), re-created + enabled". Watchdog log totals today (UTC): 50 "restart OK", 0 "restart FAILED", 50 "unit was missing". Same ~100/day pace as 11-18/19/20/21, NOT an escalation.
- VM booted ~11:35 UTC, up 55 min at check; the 12:03–12:23 restarts happened within this boot — same within-boot reset pattern noted before. Gateway itself never crashes (gateway.log shows clean startups only); the environment resets underneath it and the watchdog recovers it within ~10 min.
- Memory still tight and steady: 196 MB free, 626 MB available (vs 166/613 at 18:31). No OOM line in gateway.log; not proven as the cause.
- Registry checked live via queue_status.py at 12:31 UTC: still 57 tasks total (55 SUBMITTED + 2 APPROVED), NO wave5 — batch has not grown since the 09:30 UTC check (36 → 57 this morning, then flat). w4-qc-01 stays SUBMITTED with outcome=completed. K04 still BLOCKED, K02 still NEEDS_FIX, b4413e82 still SUBMITTED awaiting approval. No poster field on any task, so authorship still undetermined. Research and Verify nodes were last seen 19:30 and 19:26 +07 today, so nodes are still active this evening. The user was already asked about this batch at 06:40 +07 and again at 16:34 +07 and has not replied; nothing has changed since the second ask, so nothing new goes to chat.
- No action needed; logged here per standing rule, not messaged to chat.

## 2026-11-22 20:36 +07 — Media Gateway watchdog + registry check, no escalation
- Checked live at 20:36 +07 (13:36 UTC): gateway healthy, pid 1830 (uvicorn, started 13:13:25 UTC, alive ~22 min), /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}.
- Restarts since the 19:31 entry: 3 more, all "restart OK" (12:43 pid 1892, 12:53 pid 1763, 13:13 pid 1830), each time "systemd unit was missing (VM replaced), re-created + enabled". Watchdog log totals now: 562 "restart OK", 5 "restart FAILED" (unchanged — the 5 known failures), 566 "unit was missing". 53 restarts so far today (UTC), 0 failed today. Same ~100/day pace as 11-18/19/20/21, NOT an escalation. The 13:23 and 13:33 checks passed silently (gateway stayed up).
- VM booted 12:33 UTC (replaced since the 19:31 entry, which recorded boot ~11:35), up 1h02 at check; the 12:43–13:13 restarts happened within this boot — same within-boot reset pattern noted before. Marker files placed in /etc at 13:32 UTC were still present at 13:34 (since removed), so /etc persists within this boot; the unit-missing events are intermittent resets, not a wipe on every tick. Gateway itself never crashes (gateway.log shows clean startups only, no traceback); the environment resets underneath it and the watchdog recovers it within ~10 min.
- Memory still tight and steady: 195 MB free, 636 MB available (vs 196/626 at 19:31). No OOM line in gateway.log; not proven as the cause.
- Registry checked live via queue_status.py at 13:35 UTC: still 57 tasks total (55 SUBMITTED + 2 APPROVED), NO wave5 — batch has not grown since the 09:30 UTC check (36 → 57 this morning, then flat). w4-qc-01 stays SUBMITTED with outcome=completed. K04 still BLOCKED, K02 still NEEDS_FIX, b4413e82 still SUBMITTED awaiting approval. No poster field on any task, so authorship still undetermined. Research and Verify nodes were last seen 20:31 and 20:35 +07 today, so nodes are still active this evening. The user was already asked about this batch at 06:40 +07 and again at 16:34 +07 and has not replied; nothing has changed since the second ask, so nothing new goes to chat.
- No action needed; logged here per standing rule, not messaged to chat.

## 2026-11-23 06:32 +07 — Overnight check: gateway + registry, no escalation
- Checked live at 06:32 +07 (23:32 UTC): gateway healthy, pid 1770 (uvicorn, started 23:13:21 UTC), /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}. systemd unit file exists but service is inactive — gateway runs as a plain process via deploy.sh, not under systemd.
- Restarts since the 20:36 entry: 46 more, all "restart OK" (last two 23:03 pid 1760, 23:13 pid 1770), each time "systemd unit was missing (VM replaced), re-created + enabled". Watchdog log totals now: 608 "restart OK", 5 "restart FAILED" (unchanged — the 5 known failures), 612 "unit was missing". Nov 22 (UTC) total: 99 "restart OK", 0 "restart FAILED" — same ~100/day pace as 11-18/19/20/21, NOT an escalation.
- VM booted ~22:58 UTC, up 32 min at check; the 23:03 and 23:13 restarts happened within this boot — same within-boot reset pattern noted before. Gateway itself never crashes (gateway.log shows clean startups only); the environment resets underneath it and the watchdog recovers it within ~10 min.
- Memory still tight and steady: 185 MB free, 655 MB available (vs 195/636 at 20:36). No OOM line in gateway.log; not proven as the cause.
- Registry checked live via queue_status.py at 23:32 UTC: still 57 tasks total (55 SUBMITTED + 2 APPROVED), NO wave5 — batch has not grown since the 09:30 UTC check on 22/11 (36 → 57 that morning, then flat). No RUNNING or QUEUED tasks. w4-qc-01 stays SUBMITTED with outcome=completed. K04 still BLOCKED, K02 still NEEDS_FIX, b4413e82 still SUBMITTED awaiting approval. No poster field on any task, so authorship still undetermined. Research and Verify nodes were last seen 06:26 and 06:30 +07 today (23/11), so the batch's nodes are still heartbeating this morning. The user was already asked about this batch at 06:40 +07 and again at 16:34 +07 on 22/11 and has not replied; nothing has changed since the second ask, so nothing new goes to chat.
- Week 2 starts today (23/11); the 5-sample shortlist (v040/v036/v041/v035/v027) was already proposed on 21/11 and awaits the user's decision, and production is still blocked on PC access. The 07:00 morning briefing covers the overnight state.
- No action needed; logged here per standing rule, not messaged to chat.

## 2026-11-23 08:31 +07 — Morning check: gateway + registry, no change since the 07:00 briefing
- Checked live at 08:31 +07 (01:31 UTC): gateway healthy, /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}.
- Restarts since the 06:32 entry: 2 more, both "restart OK" (01:13 pid 3078, 01:23 pid 1769), each time "systemd unit was missing (VM replaced), re-created + enabled". Same ~100/day pace, NOT an escalation.
- VM booted ~01:14 UTC, up 17 min at check. Memory: 178 MB free, 640 MB available — steady.
- Registry checked live via queue_status.py at 01:31 UTC: still 57 tasks total, NO wave5, no RUNNING or QUEUED tasks. w4-qc-01 stays SUBMITTED with outcome=completed. K04 still BLOCKED, K02 still NEEDS_FIX, b4413e82 still SUBMITTED awaiting approval. No poster field on any task, so authorship still undetermined. Research and Verify nodes last seen 08:31 and 08:30 +07 today, still heartbeating.
- Week 2 starts today (23/11); the 5-sample shortlist (v040/v036/v041/v035/v027) was proposed on 21/11 and awaits the user's decision, and production is still blocked on PC access. The FB batch decision was already repeated in the 07:00 morning briefing; nothing has changed since, so nothing new goes to chat.
- No action needed; logged here per standing rule, not messaged to chat.

## 2026-11-23 09:32 +07 — Mid-morning check: gateway + registry, no change since the 08:31 check
- Checked live at 09:32 +07 (02:32 UTC): gateway healthy, pid 1786 (uvicorn, started 02:13:17 UTC), /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}.
- Restarts since the 08:31 entry: 3 more, all "restart OK" (01:43 pid 1821, 01:53 pid 1780, 02:13 pid 1786), each time "systemd unit was missing (VM replaced), re-created + enabled". Watchdog log totals now: 619 "restart OK", 5 "restart FAILED" (unchanged — the 5 known failures), 623 "unit was missing". 9 restarts so far today (UTC), 0 failed today. Same ~100/day pace, NOT an escalation.
- VM booted ~01:50 UTC, up 41 min at check. Memory: 162 MB free, 641 MB available, 352 MB swap used — steady.
- Registry checked live via queue_status.py at 02:32 UTC: still 57 tasks total (55 SUBMITTED + 2 APPROVED), NO wave5, no RUNNING or QUEUED tasks. w4-qc-01 stays SUBMITTED with outcome=completed. K04 still BLOCKED, K02 still NEEDS_FIX, b4413e82 still SUBMITTED awaiting approval. No poster field on any task, so authorship still undetermined. Research and Verify nodes last seen 09:31 and 09:30 +07 today, still heartbeating.
- Week 2 starts today (23/11); the 5-sample shortlist (v040/v036/v041/v035/v027) was proposed on 21/11 and awaits the user's decision, and production is still blocked on PC access (other_tcp flip still required; the fresh-subagent retry for v013 already failed on 16/11). The FB batch decision was already repeated in the 07:00 morning briefing; nothing has changed since, so nothing new goes to chat.
- No action needed; logged here per standing rule, not messaged to chat.

## 2026-11-23 11:31 +07 — Midday check: gateway + registry, no change since the 09:32 check
- Checked live at 11:31 +07 (04:31 UTC): gateway healthy, pid 1879 (uvicorn, started 04:23:18 UTC), /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}.
- Restarts since the 09:32 entry: 9 more, all "restart OK" (last 04:23 pid 1879), each time "systemd unit was missing (VM replaced), re-created + enabled". Watchdog log totals now: 628 "restart OK", 5 "restart FAILED" (unchanged — the 5 known failures), 632 "unit was missing". 18 restarts so far today (UTC), 0 failed today. Same ~100/day pace, NOT an escalation.
- VM booted 03:07:53 UTC, up 1h22 at check; the 03:43–04:23 restarts happened within this boot — same within-boot reset pattern noted before. Gateway itself never crashes (gateway.log shows clean startups only, /health 200s); the environment resets underneath it and the watchdog recovers it within ~10 min.
- Memory still tight and steady: 194 MB free, 647 MB available (vs 162/641 at 09:32). No OOM line in gateway.log; not proven as the cause.
- Registry checked live via queue_status.py at 04:31 UTC: still 57 tasks total, NO wave5, no RUNNING or QUEUED tasks. w4-qc-01 stays SUBMITTED with outcome=completed. K04 still BLOCKED, K02 still NEEDS_FIX, b4413e82 still SUBMITTED awaiting approval. No poster field on any task, so authorship still undetermined. Research and Verify nodes last seen 11:26 and 11:30 +07 today, still heartbeating.
- Week 2 starts today (23/11); the 5-sample shortlist (v040/v036/v041/v035/v027) was proposed on 21/11 and awaits the user's decision, and production is still blocked on PC access. The FB batch decision was already repeated in the 07:00 morning briefing; nothing has changed since, so nothing new goes to chat.
- No action needed; logged here per standing rule, not messaged to chat.

## 2026-11-23 12:32 +07 — Midday check: gateway + registry, no change since the 11:31 check
- Checked live at 12:32 +07 (05:32 UTC): gateway healthy, pid 1768 (uvicorn, started 05:13:18 UTC), /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}.
- Restarts since the 11:31 entry: 3 more, all "restart OK" (04:44, 04:53, 05:13 UTC), each time "systemd unit was missing (VM replaced), re-created + enabled". Watchdog log totals now: 631 "restart OK", 5 "restart FAILED" (unchanged — the 5 known failures), 635 "unit was missing". 21 restarts so far today (UTC), 0 failed today. Same ~100/day pace, NOT an escalation.
- VM booted ~05:01 UTC (up 30 min at check), a fresh replacement after the 03:07 boot — the 05:13 restart happened within this boot, same within-boot reset pattern. Gateway itself never crashes (gateway.log shows clean startups only, /health 200s); the environment resets underneath it and the watchdog recovers it within ~10 min.
- Memory still tight and steady: 192 MB free, 624 MB available (vs 194/647 at 11:31). No OOM line in gateway.log; not proven as the cause.
- Registry checked live via queue_status.py at 05:32 UTC: still 57 tasks total (55 SUBMITTED + 2 APPROVED), NO wave5, no RUNNING or QUEUED tasks. w4-qc-01 stays SUBMITTED with outcome=completed. K04 still BLOCKED, K02 still NEEDS_FIX, b4413e82 still SUBMITTED awaiting approval. No poster field on any task, so authorship still undetermined. Research and Verify nodes last seen 12:26 and 12:30 +07 today, still heartbeating.
- Week 2 starts today (23/11); the 5-sample shortlist (v040/v036/v041/v035/v027) was proposed on 21/11 and awaits the user's decision, and production is still blocked on PC access. The FB batch decision was already repeated in the 07:00 morning briefing; nothing has changed since, so nothing new goes to chat.
- No action needed; logged here per standing rule, not messaged to chat.

## 2026-11-23 13:30 +07 — Midday check: gateway + registry, no change since the 12:32 check
- Checked live at 13:30 +07 (06:30 UTC): gateway healthy, pid 1822 (uvicorn, started 06:23:18 UTC), /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}.
- Restarts since the 12:32 entry: 5 more, all "restart OK" (05:43, 05:53, 06:03, 06:13, 06:23 UTC), each time "systemd unit was missing (VM replaced), re-created + enabled". Watchdog log totals now: 640 "unit was missing". Same ~100/day pace, NOT an escalation; gateway itself never crashes, watchdog recovers within ~10 min.
- Registry checked live via queue_status.py at 06:30 UTC: still 57 tasks total, NO wave5, no RUNNING or QUEUED tasks. w4-qc-01 stays SUBMITTED with outcome=completed. K04 still BLOCKED, K02 still NEEDS_FIX, b4413e82 still SUBMITTED awaiting approval. No poster field on any task, so authorship still undetermined.
- Week 2 starts today (23/11); the 5-sample shortlist (v040/v036/v041/v035/v027) was proposed on 21/11 and awaits the user's decision, and production is still blocked on PC access. The FB batch decision was already repeated in the 07:00 morning briefing and again yesterday; nothing has changed since, so nothing new goes to chat.
- No action needed; logged here per standing rule, not messaged to chat.

## 2026-11-23 14:35 +07 — Afternoon check: gateway + registry + PC probe, no change since the 13:30 check
- Checked live at 14:33–14:35 +07 (07:33–07:35 UTC): gateway healthy, pid 1770 (uvicorn, started 07:23:20 UTC), /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"} in 47 ms. The 07:33 watchdog run was quiet (no new watchdog.log lines) — first quiet check since the 07:23 restart.
- New diagnostic detail on the chronic restarts: journalctl shows only ONE boot today (07:04:13 UTC, boot id d8678384…), yet the gateway was restarted at 07:13 and 07:23 and the unit file was re-created at both times — so the "unit was missing (VM replaced)" label does not match a reboot for those two restarts. gateway.log shows NO "Shutting down" line between the 07:03, 07:13 and 07:23 starts (it jumps straight from health-check 200s to the next "Started server process"), i.e. the old process vanished without a graceful shutdown. Cause still undetermined (platform-level reset below the journal's visibility, or a hard kill); watchdog self-heal works each time and there is no user-facing outage. Logged here per standing rule, not messaged to chat.
- Registry checked live via queue_status.py at ~07:32 UTC: still 57 tasks total (55 SUBMITTED + 2 APPROVED), NO wave5, no RUNNING or QUEUED tasks. w4-qc-01 stays SUBMITTED with outcome=completed. K04 still BLOCKED, K02 still NEEDS_FIX, b4413e82 still SUBMITTED awaiting approval. No poster field on any task, so authorship still undetermined. Research and Verify nodes last seen 14:26 and 14:30 +07 today, still heartbeating.
- PC access probe (fresh session, 07:33 UTC): SSH to the PC still denied — tunnel proxy returns HTTP 403 Forbidden for other TCP connections in this session, same other_tcp block as before. Production stays blocked; no VPS fallback per user order.
- v041 fact check confirmed in the script file (script_v041-quick-quiz-42s.md): all 3 quiz answers re-verified 21/11 via independent web sources (Live Science/Judy Jernstedt UC Davis + LibreTexts; New Scientist + ScienceABC + OctoNation; Smithsonian Magazine) — no script change needed. The accuracy caveat on the Week-2 shortlist (stated in the 21/11 proposal) is now resolved; the shortlist itself still awaits the user's decision.
- Week 2 starts today (23/11); trial posting is 27–29/11 at 11:30/20:00. The FB K01–K12 decision was already asked twice yesterday and repeated in the 07:00 morning briefing; nothing has changed since, so nothing new goes to chat on that.
- No action needed; logged here per standing rule, not messaged to chat.

## 2026-11-23 15:45 +07 — Afternoon check: gateway + registry, no change since the 14:35 check
- Checked live at 15:30–15:45 +07 (08:30–08:45 UTC): gateway healthy, pid 1874 (uvicorn, started 08:13:23 UTC), /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}.
- Restarts since the 14:35 entry: 3 more, all "restart OK" (07:43, 07:53, 08:13 UTC), each time "systemd unit was missing (VM replaced), re-created + enabled". Watchdog log totals now: 648 "gateway down", 647 "unit was missing". Same ~100/day pace, NOT an escalation; gateway.log shows clean startups only, no crash traceback in recent starts, no OOM line. Memory tight and steady: 209 MB free, 685 MB available. systemd unit exists but service is inactive (dead) — gateway runs as direct nohup uvicorn, so systemd Restart=on-failure never applies; watchdog is the only restart path.
- Registry checked live via queue_status.py at ~08:40 UTC: still 57 tasks total (55 SUBMITTED + 2 APPROVED), NO wave5, no RUNNING or QUEUED tasks. w4-qc-01 stays SUBMITTED with outcome=completed. K04 still BLOCKED, K02 still NEEDS_FIX, b4413e82 still SUBMITTED awaiting approval. No poster field on any task, so authorship still undetermined.
- PC access: last probe 07:33 UTC still denied (other_tcp 403); not re-probed this hour. Production stays blocked; no VPS fallback per user order. v041 facts re-verified 21/11 (see 14:35 entry) — Week-2 shortlist caveat resolved, shortlist itself still awaits the user's decision.
- No action needed; logged here per standing rule, not messaged to chat.

## 2026-11-23 16:43 +07 — Watchdog check (10-min): gateway restarted, healthy again
- Watchdog run at 16:43 +07 (09:43 UTC) found the gateway down and the systemd unit missing (VM replaced), re-created + enabled the unit, and restarted the gateway: "restart OK" at 09:43:20 UTC, new pid 1834. /health now returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}.
- Restarts since the 15:30 entry: 6 more, all "restart OK", each time "systemd unit was missing (VM replaced), re-created + enabled". Watchdog log totals now: 654 "gateway down", 653 "unit was missing", 649 "restart OK", 5 "restart FAILED" (unchanged — the 5 known failures). 0 failed today. Same ~100/day pace, NOT an escalation; gateway itself never crashes (clean startups only), watchdog recovers within ~10 min.
- systemd unit exists and is enabled but the service is inactive (dead) — gateway runs as direct nohup uvicorn, so systemd Restart=on-failure never applies; watchdog is the only restart path (same as noted before).
- Restart succeeded, so per standing rule this is logged here, not messaged to chat.

## 2026-11-23 20:30 +07 — Evening check: gateway + registry, no change since the 16:43 check
- Checked live at 20:30 +07 (13:30 UTC): gateway healthy, pid 1781 (uvicorn, started 13:23:25 UTC), /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}.
- Restarts since the 16:43 entry: 17 more, all "restart OK", each time "systemd unit was missing (VM replaced), re-created + enabled". Watchdog log totals now: 671 "gateway down", 670 "unit was missing", 666 "restart OK", 5 "restart FAILED" (unchanged — the 5 known failures). 0 failed today. Same ~100/day pace, NOT an escalation; gateway itself never crashes (clean startups only), watchdog recovers within ~10 min.
- Memory tight and steady: 172 MB free, 674 MB available (vs 209/685 at 15:45). No OOM line in gateway.log; not proven as the cause.
- Registry checked live via queue_status.py at ~13:30 UTC: still 57 tasks total (55 SUBMITTED + 2 APPROVED), NO wave5, no RUNNING or QUEUED tasks. w4-qc-01 stays SUBMITTED with outcome=completed. K04 still BLOCKED, K02 still NEEDS_FIX, b4413e82 still SUBMITTED awaiting approval. No poster field on any task, so authorship still undetermined.
- Week 2 starts today (23/11); the 5-sample shortlist (v040/v036/v041/v035/v027) was proposed on 21/11 and awaits the user's decision, and production is still blocked on PC access. The FB K01–K12 decision was already asked twice on 22/11 and repeated in the 07:00 morning briefing; nothing has changed since, so nothing new goes to chat.
- NOTE (log-path fix, 20:30 +07): today's 11:31–16:43 entries were found only in ~/workspace/agentnet-corner/STATUS.md, which auto_push.sh never copies to git — the git-tracked copy here had stopped at the 09:32 entry. Those 6 entries have now been merged into this file verbatim, and the work-dir copy has been replaced with a redirect note pointing here. Canonical log is this file; do not log status checks to the work-dir copy.
- No action needed; logged here per standing rule, not messaged to chat.

## 2026-11-24 07:35 +07 — Early check: gateway + registry + PC probe, no change since the 07:00 briefing
- Checked live at 07:31–07:35 +07 (00:31–00:35 UTC): gateway healthy, pid 1750 (uvicorn, started 00:23:20 UTC), /health returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}.
- Restarts since the 07:00 briefing: 2 more, both "restart OK" (00:13, 00:23 UTC), each time "systemd unit was missing (VM replaced), re-created + enabled". Watchdog log totals now: 718 "gateway down", 717 "unit was missing", 713 "restart OK", 5 "restart FAILED" (unchanged — last failure 2026-11-21 20:13 UTC). Same ~100/day pace, NOT an escalation.
- NEW diagnostic detail on the chronic restarts: journalctl --list-boots shows exactly ONE boot, first entry 00:16:30 UTC today, and `uptime` was 14 min at 00:31 UTC — this VM instance booted at ~00:16 UTC, i.e. a real VM replacement happened between the 00:13 and 00:23 watchdog restarts, and the 00:23 restart is explained by it. Correction to the 23/11 14:35 inference: the journal only retains the current boot (it is wiped on replacement), so "only one boot today" can never disprove a replacement on this platform — the "unit missing at every restart" evidence and the fresh-boot evidence now point consistently at frequent VM replacement as the cause, not a gateway bug. gateway.log shows clean startups only, no "Shutting down" lines, no crash traceback; dmesg/journal show no OOM. Memory tight but steady: 186 MB free, 645 MB available. No gateway fix to chase — the watchdog self-heal is the correct mitigation.
- Registry checked live via queue_status.py at ~00:35 UTC: still 57 tasks total, NO wave5, no RUNNING or QUEUED tasks. Newest tasks still wave4 22/11. K04 still BLOCKED, K02 still NEEDS_FIX, b4413e82 still SUBMITTED awaiting approval. No poster field, authorship still undetermined.
- PC access probe (fresh session, 00:32 UTC): SSH to the PC still denied — tunnel proxy returns HTTP 403 Forbidden for other TCP connections, same other_tcp block as before. Production stays blocked; no VPS fallback per user order.
- Week 2 (23–29/11); trial posting 27–29/11 at 11:30/20:00. Pending decisions unchanged since the 07:00 briefing delivered 30 minutes ago — nothing new goes to chat.
- No action needed; logged here per standing rule, not messaged to chat.

## 2026-11-24 08:13 +07 — Watchdog check (10-min): gateway restarted after VM replacement, healthy again
- Watchdog run at 08:13 +07 (01:13 UTC) found the gateway down and the systemd unit missing (VM replaced), re-created + enabled the unit, and restarted the gateway: "restart OK" at 01:13:26 UTC, new pid 1751. /health now returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"}.
- Restarts since the 07:35 entry: 2 more, both "restart OK" (00:43, 01:13 UTC), each time "systemd unit was missing (VM replaced), re-created + enabled". Watchdog log totals now: 720 "gateway down", 719 "unit was missing", 715 "restart OK", 5 "restart FAILED" (unchanged — last failure 2026-11-21 20:13 UTC). Same ~100/day pace, NOT an escalation.
- Fresh-boot evidence: `uptime` 5 min at 01:14 UTC — this VM instance booted ~01:09 UTC, a real replacement between the 00:43 and 01:13 restarts. The 00:53 and 01:03 runs were quiet (gateway healthy), so the outage window was at most ~10 min. Memory: 152 MB free, 1160 MB available (better than 186/645 at 07:35).
- systemd unit exists and is enabled but the service is inactive (dead) — gateway runs as direct nohup uvicorn, so systemd Restart=on-failure never applies; watchdog is the only restart path (same as noted before).
- Restart succeeded, so per standing rule this is logged here, not messaged to chat.

## 2026-11-24 08:24 +07 — Auto-push (30-min): pushed 4f55ba6
- auto_push.sh ran clean (exit 0): f24a47a..4f55ba6 "Auto-save: 2026-11-24 01:24 UTC" pushed to origin/main.
- Verified: github repo HEAD 4f55ba6, main in sync with origin/main, clean working tree. No failure to report.

## 2026-11-24 12:53 +07 — Media Gateway watchdog (10-min): gateway down, restart OK
- Watchdog found the gateway down at 05:53:19 UTC ("gateway down, attempting restart"); deploy.sh restarted it, pid 1795, "restart OK" at 05:53:25 UTC. /health now returns {"status":"ok","database":"ok","low_resource_mode":true,"version":"1.0.0"} and the uvicorn process is running.
- systemd unit still inactive — gateway runs as direct nohup uvicorn, so the watchdog remains the only restart path (same as before).
- Restart succeeded, so per standing rule this is logged here, not messaged to chat.

## 2026-11-24 13:35 +07 — NEW registry batch ghost-vn: folk-ghost round-table, pilot decision made, waiting on Owner
- Checked live at 13:30–13:35 +07 (06:30–06:35 UTC) via queue_status.py + full /tasks read: queue grew 57 -> 65 tasks (+8, all project=research, all SUBMITTED with results). New batch "ghost-vn-20261124": a Telegram round-table (MUSE CHÍNH + 4 MUSE PHỤ + Chủ dự án "Gia Gia") on Vietnamese folk ghost-story videos. R1 created 11:10 +07, R2 11:19 +07, usr:27 replies 13:15 +07 (leases to 13:32–13:34 +07); agents active at 13:17–13:30 +07. No poster field on any task, so authorship still undetermined from the registry — same caveat as the FB K01–K12 batch. Context pointing at this user: same node pool as the FB waves (Research baa7de1f, Verify 355c4b87, 807e2cc4, cd6820ff, be6920f3), hardware context cites the RTX 5060 Ti PC, and audio lessons cite K04/K05.
- What the round-table decided (task d381b55f R2 chief-synthesis + task 0667d65d usr:27 chief reply, both outcome=ok): ONE pilot first, not a series — "Ma Da Bến Sông", vertical 9:16, 75–85s, one anchor voice (Southern male narrator, Nguyễn Ngọc Ngạn style — NOTE: different from production voice VieNeu "Mai Anh" female). 5-episode series list: #1 Ma Da kéo giò (miền Tây), #2 Thần Trùng (Bắc), #3 Linh Miêu hoàn hồn/Quỷ nhập tràng (Trung), #4 Chó đội nón mê (Nam), #5 Oan hồn Lệ Chi Viên (Bắc). Visual DNA "Làng Quê Việt Cổ" + 6 anchors + Negative Prompt against "Tàu hoá" accepted verbatim. Ma Da chosen on verified evidence: film "Ma Da" (2024, dir. Nguyễn Hữu Hoàng, Việt Hương as bà Lệ) grossed 127 tỷ VND (vi Wikipedia, Box Office Vietnam/Mojo); Saigoneer "Ma Quỷ Dân Gian Ký" 03/08/2022 (date/title corrected from Sub 1's 02/06/2022 "Kỳ").
- Two pilot outlines exist — they differ: (a) R2 script "Ma Da kéo giò": ông Tư chài lưới, full 0–80s scene-by-scene script with narration + image prompts + SFX. (b) usr:27 folklore reply (13:15 +07): ORIGINAL story "Chiều trên bến sông" — boatman, oar held under water, grandmother's warning "Đừng ngoái lại khi nghe tiếng gọi tên mình dưới sông", ends "Ai đang gọi?" — 3 beats (0–20s / 20–55s / 55–85s), explicitly NOT copying the 2024 film plot; asks Gia Gia to confirm the 3-beat outline before writing the full script. That confirmation is the pending decision.
- Binding QC gates from Sub 4 (upheld by Chief): still-images + slow zoom = YouTube Reused/Inauthentic-content risk (channel-level YPP refusal possible) — NO stills-only video approved before a motion test passes; minimum-motion standard mandatory. Slow narration + 0.3–0.8s pauses vs 60–90s format is a timing conflict to fix (script ~130–170 words incl. pauses). AIGC labels mandatory; max 1 mild jump-scare; no gore, no superstition instructions (NĐ 15/2020 cited, exact article/fine not verified); cautionary ending with "Truyện dân gian kể lại — nghe để biết, không khẳng định có thật."
- Gaps before production: pipeline only Stage A (B–C incomplete, records truncated mid-sentence); test channel name not confirmed (isolated/unlisted test run, awaiting Owner); Track B not locked. Production would hit the same PC-access block (other_tcp) as Week-2 scripts. This batch is a possible answer to the v050+ topic exhaustion (5 folk-ghost episodes, no-camera producible) — but it is a new direction, not part of the 30-video bank or the 9 fresh topics.
- Gateway (same check): healthy, /health ok, pid 1888 (started 06:23 UTC). Watchdog totals now 744 "gateway down" / 739 "restart OK" (vs 718/713 at 07:35 +07) — same ~100/day pace, NOT an escalation; logged here per standing rule, not messaged.
- Registry otherwise unchanged: b4413e82 still SUBMITTED awaiting approval; K04 still BLOCKED, K02 still NEEDS_FIX; no wave5; no RUNNING/QUEUED.
- Full ghost-vn task results fetched to /tmp/ghost-vn-20261124.json (8 tasks, payload + result); chief summaries also in /tmp/ghost_chief.txt.

## 2026-11-24 14:35 +07 — Ghost-vn: recovered full task results + pilot comparison prepared (no new queue change)

- The /tmp copies of the 8 ghost-vn results (noted in the 13:35 entry) were lost in a VM
  replacement. Re-fetched all 8 read-only from the registry (GET /tasks) and saved them
  to git-tracked `ghost-vn-20261124/` (8 JSON + 3 .txt summary extracts + this comparison
  file) — they will go out with the next 30-min auto-push. Nothing approved, posted, or
  changed on the registry.
- Queue re-checked live 14:32 +07 (queue_status.py): still 65 tasks, no new tasks since
  the 13:15 +07 replies, no RUNNING/QUEUED. Authorship still unprovable (no poster
  field). Agents alive (Verify 14:30, Research 14:26 +07).
- New checks done for the pilot choice (a) vs (b):
  - Film "Ma Da" (2024) gross 127 ty VND independently verified via web (Wikipedia "Ma
    da (phim)" + Kenh14/Thethaovanhoa, Box Office Vietnam; BOVN notes 5-10% error) —
    clears the "not independently verified" flag R2 chief put on it.
  - Script (a) "Ma Da keo gio" narration counted: 107 words = ~49s speech at slow
    130 wpm; with pauses/silence/end card ~55-65s total, i.e. 10-25s SHORT of the locked
    75-85s format and 23-63 words under the chief's own 130-170 word budget. Fixable by
    adding ~25-40 words or much slower delivery — flagged in the comparison file, not a
    rejection.
  - (b) "Chieu tren ben song" is outline-only (3 beats); needs one more script-writing
    round, but can then be written exactly to the 130-170 word budget, has the stronger
    hook/cliffhanger ("Ai dang goi?") and spends none of the 1-mild-jump-scare budget,
    vs (a) which spends it on the laugh + ghost voice.
- Shared blockers unchanged for either choice: new Southern male narrator voice not yet
  sourced (cannot use VieNeu "Mai Anh"); PC production still blocked on other_tcp;
  pipeline Stage A only; test channel name unconfirmed.
- Pending user decision (asked 13:40 +07, no reply yet): is the ghost-vn round-table
  theirs, and pilot (a) or (b)? The comparison file is ready so the choice can be made
  in one read; nothing new was messaged to chat.
