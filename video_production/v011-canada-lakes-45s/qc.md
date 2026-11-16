# QC — v011 "Canada có 60% số hồ trên thế giới" (T06 #83, F2 Visual Essay)

Date: 2026-11-16 ~13:50 +07. Status: **QC-PASSED**. NOT posted.

## File
- `v011.mp4` — 21,583,334 bytes
- SHA-256: `1fade7c08b4d03d314b5769d7d49e57fbc4bd6eecaad4a5bfe4b48389f428fa7`
- Duration: 49.60 s (1488 frames) — script target was 45 s; inside the 40–55 s remake window and the 38–65 s Shorts spec.
- Video: H.264, 1080x1920, 30 fps, yuv420p. Audio: AAC 192k, 48 kHz, stereo.
- Render + mix + mux entirely on the user's PC (user order 2026-11-15 ~21:53). No VPS fallback used.

## Audio (measured on the final muxed file)
- Loudness: **-16.09 LUFS**, true peak **-2.94 dBTP**, LRA 4.40 — in spec (~-16 LUFS, TP ≤ -1 dBTP).
- Voice: MMS-TTS (facebook/mms-tts-vie), speaking_rate 0.92, take 1 accepted.
  - 115 words; speech-only **151 wpm** (in the 150–165 zone); overall 138 wpm (pauses included).
  - Per beat: hook 150, beat 1 169, beat 2 157, beat 3 147, payoff 130 wpm.
  - Voice onset **0.041 s** — raw take had 0.291 s of leading near-silence (MMS head padding, same as v008's 0.41 s); trimmed 0.25 s off the voice head BEFORE building captions/SFX timings (v010's lesson).
- Whisper large-v3 check (PC): **98/115 = 85.2%** heard correctly.
  - Most misses are Whisper number normalization ("sáu mươi phần trăm"→"60%", "ba mươi mốt nghìn"→"31.000", "mười nghìn năm"→"10.000 năm") — not real errors.
  - Real tone confusions: sâu→"su", đọng→"động", cụm→"cụng", ngọt→"mọt" (×2), riêng→"khiên". Captions carry the correct words.
  - All key words heard: "Canada" (×2), "băng tuyết khổng lồ", "cào xới", "hồ Thượng", "Trái Đất", "Bình luận nhé!".
- BGM (bgm_calm, vol 0.12): measured **23.5 dB below voice** in the inter-beat gaps (-41.9 dBFS vs -18.3 dBFS speech) — inside the -18 to -24 dB target. SFX: ding at 6.83 s and 28.43 s, whoosh at 15.79 s, pop at 40.43 s.

## Probe swaps (all 4 probe rounds on PC, see v011_probe*.py)
- "Canada" FAILS in MMS ("ca la"/"Kalala") → TTS input **"Ca-na-đa"** (round 4: Whisper hears it as "Canada" in both sentences). Captions + on-screen text use "Canada".
- "băng hà" FAIL (tone swap) → **"băng tuyết khổng lồ"** (94.4%).
- "hố trũng" FAIL (tone swap) → **"hố sâu"** (94.4%).
- KEPT: "cào xới" (fallback "cào nát" scored worse), "Thượng" (heard correctly), "Trái Đất" (94.7%), "Mười" (first-word issue; on-screen label carries it).
- Final script 115 words (113 + 2 from "băng hà"→"băng tuyết khổng lồ").

## Video structure (7 segments, concat hard cuts, no crossfades)
- hook 0–6.83 s (Earth from space) · beat 1 6.83–15.79 s (own redrawn Canada map) · beat 2a 15.79–22.11 s (Hardangerjøkulen glacier) · beat 2b 22.11–28.43 s (Mount Chudleigh) · beat 3a 28.43–34.33 s (Lake Superior aerial) · beat 3b 34.33–40.43 s (Nunavut satellite lakes) · payoff 40.43–49.58 s (Moraine Lake, end card).
- Numbers appear ON SCREEN only (60%, 31.752, 18%, 82.100 km² on the map/labels/end card), never in voiceover. Exactly 3 beats — no 4th beat about forests/oil.

## Frames viewed
- 1 s: hook label "MỘT NƯỚC GIỮ HƠN NỬA / SỐ HỒ THẾ GIỚI?" legible over the 1960s Earth photo; caption "Một nước giữ hơn" correct.
- 10 s: Canada map (red border, 260 lake dots, Great Lakes ellipses) + label "CANADA — 60% HỒ THẾ GIỚI" legible.
- 45 s + 48.5 s: end card complete — title "MỘT NƯỚC, HƠN NỬA SỐ HỒ", "60% HỒ THẾ GIỚI · 31.752 HỒ LỚN", "NGŨ ĐẠI HỒ: 18% NƯỚC HỒ NGỌT", CTA "BẠN ĐÃ TỪNG TỚI CANADA CHƯA?" — all legible over the Moraine Lake photo.

## Incident fixed during this build (drawtext "%" bug)
- First PC render (sha e82c59e1…) silently dropped 3 texts containing "%": the beat-1 label and both end-card numbers lines. ffmpeg drawtext logged "Stray %" per frame and drew nothing for those instances; exit code was still 0.
- `%%` does NOT escape it (tested on VPS: whole drawtext still blank).
- Fix: `expansion=none` on all 10 drawtext instances in assemble_filter_pc.txt (verified on VPS first, then re-rendered on the PC). New sha 1fade7c0…, frames re-checked at 10 s and 45 s — all % lines now render.
- **Lesson for future batches: never put a bare "%" in a drawtext textfile without `expansion=none`; and always view a frame inside every label's window, not just the hook and the end card.**

## Honest limits
- No human has listened to the voice (Whisper % only). The user should listen once before posting.
- Payoff speech is slow (130 wpm) and beat 1 is fast (169 wpm); overall speech-only 151 wpm is in zone, but the per-beat spread is wider than ideal.
- Caption duplicates the end-card CTA words in the last ~2 s ("Bạn đã" appears in the caption and in the end-card "BẠN ĐÃ TỪNG TỚI CANADA CHƯA?") — same nit as v003.
- Beat 3b uses the Nunavut satellite photo as a generic "lakes from space" visual — it is not the Great Lakes.
- beat3_superior.jpg is 1024 px (slightly soft when upscaled to 1080x1920); the hook Earth photo is a 1960s film scan (grainy, historic look).
- Per-SFX audibility was not individually verified (only the mix-level BGM/voice delta was measured); the ding/whoosh/pop are at vol 0.5 in the mix.
- Whisper's tone confusions (sâu/đọng/cụm/ngọt/riêng) mean those words may sound slightly off to a native ear even though the captions are correct.
