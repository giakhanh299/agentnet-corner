# V013 production notes — BLOCKED at the PC step (2026-11-16 ~14:00 +07)

## The blocker (read first)
**v013.mp4 does NOT exist yet.** This session could not reach the user's PC,
so the mix + encode + final QC never ran. Per the task instruction, NO
VPS-rendered fallback was produced.

Exact failure, SSH via the tunnel proxy:
```
nc: Proxy error: "muse: Other TCP connections is turned off for this assistant.
To allow it, ask the user to open Muse settings -> Permissions -> Direct
network protocols and switch other_tcp from Deny to Ask."
```
- Direct SSH (no proxy): `ssh: connect to host 100.101.158.71 port 22:
  Operation not permitted` (sandbox blocks direct tailnet egress).
- `curl --proxy <tunnel-proxy>:3130 http://100.101.158.71:22/` DID connect
  ("Connected to hatch-egress-proxy port 3130", then "Empty reply from
  server" — the SSH daemon answering a non-HTTP probe). So the tunnel
  itself works and the PC's port 22 answers; only raw-TCP `nc`/SSH from
  THIS subagent session is denied by the other_tcp=Deny policy.
- `permissions.list_pending` is empty (Deny raises no approval card);
  `permissions.list_active` shows a durable allow rule for host
  100.101.158.71 itself. The v009–v011 subagents used the same nc pattern
  successfully hours earlier — the Deny state likely arrived with one of
  today's VM replacements (gateway self-healed 4x today).
- **Fix options for the parent:** (a) ask the user to flip other_tcp
  Deny → Ask in Muse settings → Permissions → Direct network protocols,
  then re-run; or (b) run the PC steps from the parent agent's own session
  (which has done PC SSH before); or (c) spawn a fresh subagent and retry
  the SSH once — the Deny may be scoped to this session.

## What is DONE on the VPS (all in this dir)
- `script.md` (copy of the v013 script), `voice.wav` (VieNeu "Mai Anh",
  atempo 0.70, 45.75s, 116 words, 161 wpm speech-only, onset ~0.06s),
  `v013_units.json`, `captions.srt` + `captions.ass` (31 events),
  `cards/` (7 stages, 4 viewed: hook/n2/n1/end — all legible),
  `images/` (5 CC0 photos, all viewed) + `images/picked.json` +
  `images/sources.txt`, `sounds/` (5 normalized samples + 1 unused synth
  fallback + raw downloads), `probes/` (10 probe wavs + vendor call +
  `probe_results.json`), `v013_whisper_base.txt` (Base 71.6% — see qc.md),
  `qc.md` (pending-status QC doc), all scripts below.
- **Voice synthesis ran on the VPS** (venv-vieneu). PC VieNeu install was
  never attempted — not needed anymore (voice is done); the PC only needs
  to mix + encode.
- **Probe swaps applied:** "rao"→"bán", "modem"→"quay số". Kept:
  "chuông trường", "đề nổ", "cục gạch". Word count 117 → 116.
- **atempo note:** round-4 test sentences ran 238 wpm native so 0.65 gave
  ~155 wpm; this script runs 222 wpm native, so 0.65 gave only 144 wpm
  (below the 150–165 zone) — 0.70 was used instead → 161 wpm. Same voice,
  same method; rate chosen to hit the zone. Documented in `v013_tts.py`.
- **First-run bug fixed in `v013_tts.py`:** hook start went to -0.14
  after leading-silence trim (now clamped to 0.0).

## What remains (parent agent, on the PC)
1. Run `bash v013_to_pc.sh` from this dir. It does: mkdir on PC →
   scp (one file per call) → run `v013_mix_run.ps1` → run
   `v013_encode_run.ps1` → scp `v013.mp4` + `audio_final.m4a` back.
   Expected: 1373 frames, 45.75s, 1080x1920 30fps.
2. **Re-run the Whisper check with faster-whisper large-v3 on the PC**
   on the final voice/audio. VPS Base scored 71.6% (see qc.md) — if
   large-v3 is <75%, revisit "chuông trường" first.
3. Final QC per `qc.md` checklist (ffprobe, loudness, sha256, frames at
   ~1s and ~45s, sample audibility), then update `qc.md` with measured
   numbers and mark QC-PASSED/FAILED. Then deliver + log per the usual
   flow (STATUS.md, Drive) — NOT done by this session.
4. Optional: swap the vendor-call sample for an MMS take on the PC
   (script says MMS; this session used VieNeu — see `images/sources.txt`).

## File inventory (this dir)
- `v013_probe.py`, `v013_tts.py`, `v013_synth_sounds.py`,
  `build_cards.py`, `build_captions.py`, `v013_mix.py`,
  `v013_mix_run.ps1`, `v013_encode_run.ps1`, `v013_mkdir.ps1`,
  `v013_to_pc.sh`, `assemble_filter_pc.txt`
- `probe_log.txt`, `tts_log.txt`, `tts_log2.txt` (run logs)
- `tts_tmp/` (native + slowed per-unit wavs, intermediate)
- `probes/`, `sounds/`, `images/`, `cards/`
- NOT created: `v013.mp4`, `audio_final.m4a`, `mix_raw.wav` (PC only)
