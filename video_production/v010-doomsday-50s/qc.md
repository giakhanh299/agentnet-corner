# QC — v010 "Bài báo 1960 nói thế giới tận thế 13/11/2026"

- **Verdict: PASS** (with honest limits below). NOT posted.
- **File:** `v010.mp4` — 12,300,627 bytes
- **SHA-256:** `c7bca083059c8973344c8e0699a38603aa9a5eeb3b70f47cc1018905805c15f7`
- **Format:** H.264, 1080x1920, 30 fps, exactly 1636 frames, 54.533 s
- **Audio:** AAC 192k, 48 kHz stereo
- **Loudness (final mp4, loudnorm measure):** -16.24 LUFS, true peak -1.06 dBTP, LRA 4.10
  (PC mix verify agreed: -16.25 LUFS / -1.06 dBTP)
- **Voice:** MMS-TTS take 3, 137 words, speech-only 160 wpm (per-beat 155/165/160/158/164,
  all in the 150–165 zone), Whisper large-v3 83.9% vs script.
  Per-beat speaking rates: hook 0.95, beat1 0.95, beat2 0.85, beat3 0.95, payoff 0.90.
  Takes 1 (57.86 s, uneven 139–171 wpm) and 2 (beat1 171 / payoff 174 wpm,
  hook garbled "video này") rejected; take-2 voice kept on PC as `v010_voice_take2.wav`.
- **Probes (PC, rate 0.92, Whisper large-v3):** all PASS, no swaps —
  "tận thế" 82.4%, "vô cùng" 95.0%, "đạt đỉnh" 75.0%, "trưởng nhóm" 100%.
  (Misses are Whisper normalisation artefacts: "mười ba"→"13", "video"→"gieo",
  "một chín sáu ba"→"1963" — the spoken words are correct.)
- **Captions:** 37 events (captions.srt + captions_pc.ass, PlayRes 1080x1920,
  Be Vietnam Pro Bold). First caption starts 00:00:00,000.
- **Segments:** 8 concat hard cuts, no crossfades (v006 pattern):
  S0 hook calendar 207f, S1 Science & Invention 1928 cover 186f,
  S2 Popular Science 1940 cover 198f, S3 forecast graph 216f,
  S4 forecast zoom 191f, S5 growth-rate graph 253f, S6 bars 187f, S7 night sky 198f.
  `-frames:v 1637` cap; `setsar=1` per segment. Render+mux entirely on PC (~23 s).
- **SFX / BGM:** bgm_suspense.ogg vol 0.12; ding at 6.89 s + 33.26 s,
  whoosh 19.71 s, pop 47.94 s (take-3 beat starts).
- **Frames viewed:** 1 s (hook calendar, 13 circled red, label legible),
  12 s (Science & Invention 1928 cover, label "BÀI BÁO THẬT — NĂM 1960"),
  25 s (forecast graph, "DÂN SỐ LÊN TỚI VÔ CÙNG?", 1960: 3 tỉ dot),
  40 s (growth-rate graph, đỉnh 1963 ~2,2%, 2023: 0,87%),
  53.5 s (end card: "KÉO QUÁ KHỨ RA TƯƠNG LAI, TOÁN CŨNG NÓI DỐI" +
  "DỰ BÁO 1960: 96–205 TỈ NGƯỜI" / "THỰC TẾ 2026: 8,2 TỈ NGƯỜI" / "BẠN NGHĨ SAO?").
  All legible; all numbers on screen only, never in voiceover.
- **Images:** CC0/CC BY only + own drawn assets (calendar, 3 graphs);
  sources + rejections in `images/sources.txt`. No assets reused from original #82.
  Rejected: 1960 post-office photo, medieval calendar page, busy galaxy photo,
  log-scale bars draft, zoom graph with misleading "2000: 6 tỉ" dot.
- **Debunk framing kept:** "chính họ cũng không tin" at beat 2; hook in past tense
  ("ngày mười ba vừa rồi") — 13/11/2026 already passed, never "hôm nay".

## Honest limits

- **No human listened** — Whisper 83.9% only. MMS monotone as usual; pauses are
  the varied 0.3/0.4/0.6 s set, but no human has judged this take.
- **Voice onset 0.39 s, not ~0.1 s.** `voice.wav` starts with ~0.39 s of digital
  silence (sample-level check: rms=1, max=4–5 until 0.387 s; first audible
  speech 0.39–0.40 s). Captions start at 0.000 s, so the first caption line
  appears ~0.4 s before the voice. Same class of defect as v008 (which was
  trimmed there, 0.41 s → 0.36 s). NOT fixed here: captions + SFX timings are
  built on the untrimmed take-3 windows, so trimming now would shift every
  beat. Fix for future batches: trim leading silence in the TTS wav BEFORE
  building captions/SFX timings. The visual hook (label + calendar) is on
  screen from frame 0, so the delay is a nit, not a failure.
- **Per-SFX audibility not measured individually** — SFX levels were set by
  the v006 mix recipe (ding/whoosh/pop at mix level, BGM 0.12); no per-SFX
  loudness check was run on the final mix.
- **BGM level not measured in dB below voice** on this video (v006 measured
  ~19–20 dB below voice, in target; v003 was -11 dB, too hot). The mix recipe
  is the same as v006, but no number was verified for v010.
- **Caption duplicates end-card text in the last ~2 s** (same nit as v003):
  end card shows "BẠN NGHĨ SAO?" while the caption shows the tail of the
  payoff line ("...luận nhé!").
- **1928 magazine cover is cropped at the right edge** by the 9:16 zoompan
  ("Science and Invention" title runs off-frame). The cover is still clearly
  a vintage science magazine; the label carries the meaning.
- **Beat-3 label band overlaps the growth-rate curve** near 1963–1970; the
  peak dot stays visible above the band, and the "ĐỈNH 1963: ~2,2%" annotation
  is unobstructed.
- **MMS says "Cáp"-type first-word artefacts were not an issue here**, but
  Whisper mishears "mười ba" as "13" in the hook — captions carry the correct
  words; nothing was swapped.
- **Render log:** PC `C:\Users\w\v010_render\render.log` + `v010_mix.log`
  (mix 13:39:33–13:39:39, render 13:40:06). PC render dir kept for now.
