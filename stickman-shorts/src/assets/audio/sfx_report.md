# Core_SFX library — report (2026-11-15)

Thư viện nhạc/SFX cho repo stickman-shorts. Lấp khoảng trống mà QC của v001
và Ep001 cùng chỉ ra: cả hai video đều không có nhạc nền.

## Tổng quan

- **22 file, tất cả OK, không thiếu file nào.** 18 SFX theo đúng bảng Core_SFX
  của `production-framework-20261115.md` + 4 nhạc nền.
- **Tổng dung lượng 7,04 MB** (sfx 808 KB, music 6,0 MB) — dưới giới hạn 50 MB.
- **Giấy phép: toàn bộ CC0 1.0** (public domain, dùng thương mại được, không
  cần ghi nguồn). Nguồn: file preview HQ của Freesound, tìm qua API Openverse
  với bộ lọc `license=cc0` — mỗi file trong `sfx_manifest.json` đều ghi đủ
  source URL, landing page Freesound, creator và license URL để kiểm chứng.
- **Định dạng: Ogg Vorbis q5 (~160 kbps), 48 kHz.** Chọn .ogg vì `.gitignore`
  của repo chặn `*.wav`/`*.mp3` toàn cục nhưng không chặn `.ogg` — thư viện
  được track trong git, VPS thay thế và PC đều nhận được. Đã kiểm chứng bằng
  `git check-ignore`: `.ogg` và `.json` đều NOT IGNORED — **không cần sửa
  `.gitignore`**. Script rsync của `auto_push.sh` cũng không loại `.ogg`.
- **Chuẩn hóa: integrated ≈ -20 LUFS (đo lại -19,8 tới -21,27), true peak
  ≤ -1,2 dBTP** (loudnorm two-pass + alimiter; xem chi tiết bên dưới).
  Giọng đọc chuẩn của dự án là -16 LUFS — SFX ở -20 LUFS nằm dưới giọng
  khoảng 4 dB ngay từ file gốc, trước cả volume ducking lúc assemble.

## Danh sách file (nguồn + giấy phép)

| File | Nguồn (Freesound / Openverse CC0) | Dài | I (LUFS) | TP (dB) |
|---|---|---|---|---|
| sfx/whoosh.ogg | Swipe Whoosh — qubodup | 0,45s | -20,15 | -2,86 |
| sfx/pop.ogg | game sound sfx (menu) — waveplaySFX | 0,34s | —* | -2,3† |
| sfx/ding.ogg | Ding 1 — greenvwbeetle | 0,52s | -19,91 | -15,11 |
| sfx/boom.ogg | Bass Impact - Ki_01 — Kievinay | 2,50s | -19,80 | -2,23 |
| sfx/bass_hit.ogg | super low bass hit — phluidbox | 0,33s | —* | -1,2† |
| sfx/riser.ogg | 13 drum roll 01 — zuluonedrop | 3,08s | -20,16 | -1,72 |
| sfx/victory.ogg | game-win — mickleness | 2,50s | -19,95 | -9,66 |
| sfx/record_scratch.ogg | Record Scratch #4 — musicvision31 | 1,88s | -20,29 | -10,52 |
| sfx/fail.ogg | wah wah sad trombone — kirbydx | 5,21s | -19,97 | -8,44 |
| sfx/error_buzz.ogg | buzzer — Loyalty_Freak_Music | 0,46s | -20,05 | -7,49 |
| sfx/boing.ogg | Cartoon Boing — reelworldstudio | 2,25s | -20,82 | -7,72 |
| sfx/door_knock.ogg | Door Knock (urgency) — FreqMan | 1,90s | -20,02 | -8,12 |
| sfx/footsteps.ogg | footstep on wood foley — martian | 4,00s | -21,27 | -1,26 |
| sfx/laugh.ogg | Crowd laugh — deleted_user_2104797 | 3,31s | -20,42 | -4,36 |
| sfx/crickets.ogg | crickets night short (Montreal) — kyles | 4,00s | -20,36 | -9,93 |
| sfx/suspense_drone.ogg | Drone of suspense — reacthor | 22,96s | -19,99 | -7,63 |
| sfx/camera_click.ogg | Camera Shutter — roachpowder | 0,29s | —* | -1,6† |
| sfx/transition_swoosh.ogg | Transition Swoosh — adh.dreaming | 1,49s | -19,99 | -3,69 |
| music/bgm_calm.ogg | ps Calm Aurorae — arseniiv | 95,69s | -19,97 | -7,19 |
| music/bgm_upbeat.ogg | Free Uplifting Music — Seth_Makes_Sounds | 90,00s | -20,22 | -1,21 |
| music/bgm_suspense.ogg | Atmospheric horror music #1 — Magmi.Soundtracks | 86,31s | -20,01 | -1,92 |
| music/bgm_comedy.ogg | Country Bumpkin — Beetlemuse | 116,71s | -20,16 | -6,07 |

\* 3 file dưới 0,5s (pop, bass_hit, camera_click): loudnorm không đo được
integrated (cửa sổ đo EBU R128 dài hơn cả file) nên dùng peak normalization
về -1 dBTP rồi đo lại bằng volumedetect.
† TP của 3 file này là sample peak đo bằng volumedetect (không phải true peak);
cả 3 đều ≤ -1,2 dB.

Chi tiết từng file (URL tải, landing page, creator, sample rate, kênh,
phương pháp chuẩn hóa) xem `sfx_manifest.json` — file này là nguồn duy nhất
đáng tin cho metadata; bảng trên chỉ là tóm tắt.

## Cắt / xử lý đã làm

- **boom:** 3,94s → 2,50s (đuôi sau 2,2s là im lặng — silencedetect xác nhận;
  cắt + fade-out 0,3s, không fade-in để giữ attack).
- **footsteps:** 17,0s → 4,0s (0–4s; các bước cách đều ~0,5s suốt file,
  silencedetect xác nhận; fade 0,2s hai đầu; lặp bằng crossfade khi cần dài hơn).
- **crickets:** 16,9s → 4,0s (1–5s; tiếng dế liên tục, không khoảng lặng;
  fade 0,3s hai đầu; lặp bằng crossfade).
- **bgm_upbeat:** 160s → 90s (0–90s, fade 2s hai đầu).
- **bgm_calm / bgm_suspense / bgm_comedy:** giữ nguyên độ dài, chỉ fade 2s hai đầu.
- **suspense_drone:** giữ nguyên 22,96s (đủ dài làm bed cho một cảnh).

## Hai lỗi đã gặp và đã sửa (ghi lại để không lặp lại)

1. **Vorbis overshoot làm true peak vượt -1 dBTP** (footsteps -0,8;
   bgm_upbeat -0,89 ở lần chuẩn hóa đầu). Nguyên nhân: lossy encode đẩy
   true peak lên sau khi limiter đã cắt ở -1 dB. Sửa: hạ limiter xuống
   0,85 (≈ -1,4 dB) để chừa headroom cho codec; đo lại tất cả TP ≤ -1,21.
2. **loudnorm upsample ngầm lên 192 kHz.** Filter loudnorm của ffmpeg dùng
   192 kHz nội bộ để đo true peak và giữ luôn sample rate đó ở đầu ra nếu
   không resample lại. 11 file bị đẩy lên 192 kHz ở lần chạy đầu. Sửa: thêm
   `aresample=48000` vào cuối chuỗi filter; đo lại toàn bộ 22 file đều 48 kHz.
   (Lần sửa này tôi đã xóa nhầm thư mục `raw/` trước khi chạy lại nên phải
   tải lại 22 file — may là `download_sfx.py` tải lại được từ URL trong
   manifest. Bài học: chỉ xóa `raw/` SAU khi chạy normalize xong.)

## Nguồn nào KHÔNG dùng được (ghi lại để khỏi thử lại)

- **Mixkit:** URL trực tiếp `assets.mixkit.co/...` trả 403 kể cả khi gửi
  Referer + User-Agent trình duyệt — Mixkit chặn egress của VPS này.
  Không tải được file nào từ Mixkit; toàn bộ thư viện lấy từ Openverse/Freesound.
- **Pixabay:** không cần dùng tới (Openverse CC0 đã đủ 22/22); để dành làm
  fallback nếu Freesound/Openverse thiếu file sau này.
- **Freesound bản WAV gốc:** cần API key để tải qua `apiv2/sounds/.../download/`
  (chỉ có preview HQ mp3 là tải trực tiếp được). Preview đủ tốt cho SFX dưới
  giọng đọc; nếu sau này cần chất lượng cao hơn thì đăng ký key Freesound.

## Cách dùng cho tập tiếp theo (Ep002 trở đi)

Quy tắc đặt SFX (framework): từ đầu tiên + SFX ở 0,05–0,1s; ≥2 lớp SFX
trong 3s đầu; SFX mỗi 1,5–2s trong 10s đầu, sau đó thưa dần; BGM thấp hơn
giọng -18 đến -24 dB; SFX không bao giờ át giọng.

| Công thức | Nhạc nền | SFX chính |
|---|---|---|
| F1 Hook kép (mọi video) | bất kỳ bed nào, bắt đầu nhỏ | whoosh + pop ở 0,1s; ding ở từ khóa |
| F2 Visual Essay | bgm_calm | ding mỗi beat; camera_click khi bằng chứng hiện; boom nhẹ ở payoff |
| F3 Countdown | bgm_upbeat | pop mỗi mục hiện; riser trước #1; victory ở #1; laugh sau punchline |
| F4 Một hình phi lý | bgm_suspense (nhẹ) | door_knock 0,1s; boing khi vật nảy; record_scratch khi reveal; bass_hit thay boom |
| F5 X vs Y | bgm_comedy | record_scratch ở điểm chuyển; error_buzz khi sai; fail sting ở cuối; crickets chỉ khi cố tình gây ngượng |
| F6 Transformation | bgm_upbeat | pop ở mỗi mốc 25/50/75%; riser + victory ở trạng thái cuối; whoosh tua nhanh giữa bước |
| F7 Stickman story | bgm_calm | ding nhẹ ở bước ngoặt; transition_swoosh giữa beat dài; 0,5s lặng trước câu chốt |
| F8 "POV:" | bgm_suspense | footsteps khi trốn/chạy; suspense_drone trước reveal; record_scratch khi bị bắt; fail sting cuối |

**Volume khi assemble (`tools/assemble.py`):** nhạc nền đã ở -20 LUFS; assemble
mặc định `volume=0.12` cho BGM (≈ -18 dB) nên nhạc cuối cùng nằm ~-38 LUFS,
tức ~22 dB dưới giọng -16 LUFS — đúng khung -18..-24 dB của framework.
SFX ở -20 LUFS thì giữ nguyên volume (1.0) khi mix, hoặc 0.8 nếu thấy át giọng.
**Lưu ý:** `assemble.py` nhận mọi file ffmpeg đọc được — truyền đường dẫn
`.ogg` vào `--music` (ví dụ `--music src/assets/audio/music/bgm_calm.ogg`),
không cần đổi tên thành `.mp3`.

**Chưa nghe bằng tai người:** tất cả file chỉ mới kiểm chứng bằng ffprobe +
volumedetect/loudnorm (không im lặng, đúng độ dài, đúng mức). Trước khi dùng
cho video đăng chính thức, nên nghe thử 22 file một lượt (đặc biệt `boing` —
file gốc rất nhỏ, gain +25 dB nên có thể nghe rõ noise nền mp3 khi solo;
dưới giọng đọc thì không đáng kể).

## File trong thư mục này

- `sfx/*.ogg` (18), `music/*.ogg` (4) — thư viện.
- `sfx_manifest.json` — metadata đầy đủ cho từng file (nguồn, license, đo đạc).
- `sfx_report.md` — file này.
- `search_openverse.py`, `search_fallback.py` — tìm ứng viên CC0 qua Openverse.
- `download_sfx.py` — tải 22 file đã chọn + kiểm chứng ffprobe/volumedetect.
- `normalize_sfx.py` — trim + loudnorm two-pass + alimiter + resample 48k.
- `build_manifest.py` — ráp manifest từ 2 report JSON.
- `sfx_candidates.json`, `sfx_candidates_fallback.json` — toàn bộ ứng viên
  tìm được (để đổi file khác sau này không cần tìm lại).
- `download_report.json`, `normalize_report.json` — số đo gốc từng bước.
- Không còn thư mục `raw/` (đã xóa sau khi chuẩn hóa xong; tải lại được bất
  cứ lúc nào bằng `download_sfx.py`).
