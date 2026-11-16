# QC — V013 "Top 5 âm thanh nghe là nhớ ngay" — PENDING PC STEPS

**Status: NOT QC-PASSED. No v013.mp4 exists yet.** The PC was unreachable
from this session (see v013_production_notes.md), so the mix + encode +
final QC could not run. Everything below the "PENDING" line is pre-computed
on the VPS and ready for the parent agent to finish on the PC.

## Verified on the VPS (2026-11-16)
- **Voice:** VieNeu-TTS v3 Turbo, preset "Mai Anh", per-unit atempo=0.70.
  `voice.wav` 45.75s, 116 words, **161 wpm speech-only** (150–165 zone),
  152 wpm overall. Leading silence trimmed 0.062s (voice onset ~0.06s).
  Unit timings in `v013_units.json` (hook 0.00–7.35, n5 7.65–12.78,
  n4 13.18–18.77, n3 19.17–24.29, n2 24.69–33.13, n1 33.53–40.94,
  cta 41.54–45.75).
- **Whisper check: VPS whisper.cpp Base 83/116 = 71.6%** — BELOW the 75%
  target, BUT this is Base, not faster-whisper large-v3. Base also mangled
  common words ("nghe"→"nè", "giây"→"xây", "Số năm"→"số 5"). The parent
  MUST re-run the check with faster-whisper large-v3 on the PC before
  finalizing; large-v3 typically scores 5–10 points higher than Base.
  If large-v3 is still <75%, revisit "chuông trường" first (Base heard
  "chương trường" in the full take; fallback "chuông tan học" heard
  slightly better in probes).
- **Probe swaps (VPS Base):** "rao"→"bán" (FAIL "sau", fallback clean);
  "modem"→"quay số" (FAIL "1 đam", fallback clean). Kept: "chuông
  trường", "đề nổ" ("để nổ", tone only), "cục gạch" ("cực gạch", tone
  only — on-screen text carries spelling).
- **5 sound samples, all loudnorm-measured:** bell -23.00, motorbike
  -22.99, modem -23.00, ringtone -23.13, vendor -23.00 LUFS (target
  I=-23, matched within 0.17 LU). Ringtone is self-synthesized Gran Vals
  (public domain); modem is a real CC0 recording (synth fallback kept
  unused). Sources in `images/sources.txt`.
- **Cards:** 7/7 built, 1080x1920. Viewed: hook, n2, n1, end — all
  legible, diacritics correct, tags + waveform strips correct.
  (n5/n4/n3 use the same builder, not individually viewed.)
- **Captions:** 31 events, 116 words, SRT + ASS (PlayRes 1080x1920,
  Be Vietnam Pro Bold 56, MarginV 360).

## PENDING — PC run checklist (parent agent)
1. `bash v013_to_pc.sh` (transfer + mix + encode + copy back), OR run the
   steps manually: mkdir → scp files → `v013_mix_run.ps1` →
   `v013_encode_run.ps1` → scp `v013.mp4` + `audio_final.m4a` back.
2. Re-run the Whisper check with faster-whisper large-v3 on the PC
   (see above); apply probe-swap consequences if <75%.
3. Verify: ffprobe (1080x1920 30fps H.264+AAC, 1373 frames, 45.75s),
   loudness (~-16 LUFS, TP ≤ -1 dBTP), sha256, view frames at ~1s and
   ~45s, confirm all 5 samples audible at -18 to -24 dB below voice,
   confirm BGM ~-19 dB below voice.
4. Update this file with the measured numbers and mark QC-PASSED or list
   failures. Do NOT mark passed on VPS-only evidence.

## Known limits / deviations (carry into the final QC)
- No human listened (Whisper only, Base so far).
- n2 unit runs 171 wpm, cta 171 wpm (fast bursts; n5/n4 slowest at 152).
- Vendor call uses VieNeu "Mai Anh" (script says MMS; same voice as the
  narration — the parent may swap it for an MMS take on the PC).
- Sample level conflict: script says samples at voice level; the task
  instruction says -18 to -24 dB below voice. The mix script implements
  the task target (vol 0.12). If the parent wants the script's level,
  change sample volumes to 1.0 in `v013_mix.py`.
- n2/n3/n4 photos are 1024px Rawpixel previews (slightly soft when
  upscaled to 1080px wide); n5/n1 are full-res.
- End card has empty space below the recap line (same as the v009 template).
- Caption duplicates end-card CTA words in the last ~2s (known nit).
