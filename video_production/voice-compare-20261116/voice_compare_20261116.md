# Voice comparison — round 4 (2026-11-16): VieNeu / valtec / VietVoice vs MMS baseline

**Date:** 2026-11-16 ~02:00–03:40 +07. **Tester:** subagent (controller VPS).
**User's request:** test 3 Vietnamese TTS options the user found, compare against the
current MMS-TTS baseline. Work dir:
`~/workspace/agentnet-corner/video_production/voice-compare-20261116/`
(new — the 20261115 round-1/2/3 dir was not touched).

## Verdict (ranked recommendation)

1. **KEEP MMS-TTS as the production voice.** Nothing tested beats it overall:
   in-zone speed at speaking_rate 0.92 (160 wpm), Whisper 72.5% on the weak Base
   model (82.5% on large-v3 in round 2), fastest synthesis by far (PC CUDA:
   3 sentences / 55 words in 0.9 s), zero new install, proven across 9 finished
   videos. Its only real weakness is the **CC-BY-NC-4.0 licence
   (non-commercial)** — that is the one thing that could force a switch later.
2. **VieNeu-TTS is the best fallback — and the commercial-safe alternative.**
   Highest Whisper score this round (**80.0%**, Base), **Apache 2.0
   (commercial-safe — the only one of the three)**, OpenAI-compatible server,
   CPU-friendly ONNX. Two problems, both fixable: it speaks at **238 wpm
   natively** and v3 Turbo has **no speed control** in the SDK (needs ffmpeg
   `atempo=0.65` → ~155 wpm; accuracy after slowing 77.5%); and it is slow on
   this VPS (RTF 1.5–1.9, ~197 s cold load) — on the user's PC with GPU it
   should be much faster. **Worth a listen by the user:** if they like the
   voice, this is the monetisation-safe path.
3. **VietVoice-TTS: not viable on this VPS.** Accuracy is fine (70.0% Base,
   close to MMS) and the code is MIT, and a `speed` config exists (default 1.0,
   untested) — but synthesis runs at **RTF 74–256 on this VPS CPU**: a 45 s
   video would take roughly an hour of synthesis. Native speed 203 wpm (too
   fast). Only worth revisiting on the PC with GPU (onnxruntime-gpu) and with
   `speed < 1.0` tested.
4. **valtec-tts (v-tts): BLOCKED, untestable.** The code installs fine, but the
   model weights live in **private/gated Hugging Face repos** — `TTS()` fails
   with HTTP 401, no weights anywhere public. Also CC BY-NC (same licence
   problem as MMS). Do not pursue unless the author publishes the weights or
   the user supplies them. The 394 MB Windows .exe is an untested manual-only
   path (cannot run it from this Linux VPS).

## Per-option table

| | MMS-TTS (baseline, round-2 C) | VieNeu-TTS v3 Turbo | valtec-tts / v-tts | VietVoice-TTS |
|---|---|---|---|---|
| Repo | facebook/mms-tts-vie (HF) | github.com/pnnbao97/VieNeu-TTS @ 22dd2ef (2026-11-09) | github.com/tronghieuit/valtec-tts @ e22eef3 (2026-07-23) | github.com/nguyenvulebinh/VietVoice-TTS @ d4e8a22 (2025-07-14) |
| Licence | **CC-BY-NC-4.0 (non-commercial)** | **Apache 2.0 — commercial-safe** (repo LICENSE + HF model card) | **CC BY-NC 4.0 — non-commercial** (LICENSE file + README: "Commercial use requires written permission") | **MIT (code)** — commercial-safe on the code side; model-weights licence not separately stated in the repo |
| Install size (this VPS) | model already in HF cache; no new install this round | venv 918 MB + model ~503 MB (ONNX fp32, 6 files, sha256-verified) ≈ 1.4 GB | venv 2.0 GB (torch CPU + torchaudio + librosa + gruut + viphoneme + underthesea + vinorm + gradio); model: **not downloadable** | venv 1.1 GB (incl. torch CPU) + model 1.44 GB (`model-bin.pt`, 1,508,003,328 B) ≈ 2.5 GB |
| Model | VITS, `facebook/mms-tts-vie` | ~131 M params, v3 Turbo, 48 kHz, 25 preset voices (N/C/S) | 74.8 M params (README claim), VITS-based, 5 built-in voices | ONNX flow-matching diffusion, 24 kHz, `speed` config (default 1.0), gender/area/group/emotion presets |
| Output | 16 kHz mono | 48 kHz native (`vieneu_48k.wav`), 16 kHz mono sample saved too | — (never ran) | 24 kHz native (`vietvoice_24k.wav`), 16 kHz mono sample saved too |
| Speed (native) | 160 wpm speech-only @ rate 0.92 | **238 wpm** speech-only (211 overall) — far above 150–165 | unknown (blocked) | **203 wpm** speech-only (183 overall) — above 150–165 |
| Synthesis RTF (this VPS, 1.5 CPU) | not re-measured this round; PC CUDA 0.9 s / 3 sentences (round 1) | **1.49–1.92** (slower than real-time); cold model load **197 s** | — (blocked) | **74–256** (see § VietVoice); total wall 1089.6 s for 4 segments incl. load |
| Whisper check (Base, `-l vi`, same tool for all) | **29/40 = 72.5%** | **32/40 = 80.0%** native; 31/40 = 77.5% after atempo 0.65 | — (blocked) | **28/40 = 70.0%** (corrected run; first run's 20% was my test bug, see § VietVoice) |
| "log" pronounced? | No — "lá"/"luôn" | No — "hốc"/"lắc"/"lớp" | unknown | No — "lót" |
| Scriptable (CLI/Python, headless) | Yes — proven in production | **Yes** — Python API + `vieneu` CLI; OpenAI-compatible server `apps/openai_speech.py` (POST /v1/audio/speech) | Code: yes (Python API, CLI `infer.py`, Gradio demo) — **moot, weights blocked** | **Yes** — Python API + Gradio UI (`app.py`); no OpenAI-compatible endpoint in the repo |
| Runs on user's PC (RTX 5060 Ti) | Yes — proven (CUDA) | Yes — ONNX Runtime; GPU build would be much faster than this VPS | Windows .exe v1.0.5 (394 MB) exists, untested here | Yes in principle (ONNX); needs onnxruntime-gpu + `speed` test |
| Verdict | **Keep — production voice** | **Best fallback; commercial-safe** | **Blocked** | **Not viable on this VPS** |

## Test protocol

Same 3 sentences as rounds 1–3 (40 words total), same pause scheme as round 2
(0.3 s after hook, 0.4 s at the comma split inside sentence 2, 0.6 s before
payoff; 1.3 s pauses total):

- Hook: "Mỗi lần đăng nhập, bạn đang dùng mẹo của thủy thủ năm trăm năm trước?"
  (15 words)
- Beat: "Thủy thủ viết tất cả vào sổ nhật ký của tàu, gọi là sổ log."
  (11 + 4 words)
- Payoff: "Đăng nhập là ký tên vào sổ log của tàu." (10 words)

Whisper check: `whisper.cpp/build/bin/whisper-cli -m models/ggml-base.bin -l vi`
on each 16 kHz mono sample. **Base is weaker than the faster-whisper large-v3
used in rounds 1–2, so these % are NOT directly comparable to the 90.0% /
82.5% large-v3 figures** — the MMS round-2 C sample was re-checked with the
same Base tool (72.5%) as the fair baseline. Scoring is objective and
reproducible: `score_whisper.py` (difflib alignment; "500" counts as "năm
trăm" — a Whisper number-normalisation artifact, same convention as rounds
1–2; everything else must match exactly, "số" ≠ "sổ", "hốc" ≠ "log").

## VieNeu-TTS — tested, works, fastest-talking

- Repo: https://github.com/pnnbao97/VieNeu-TTS, commit
  `22dd2ef2a89bba24a77da6dbc84c75f7f4fda05b` (2026-11-09). SDK `vieneu`
  3.8.4 (PyPI). Licence Apache 2.0 (repo LICENSE + HF model card
  `pnnbao-ump/VieNeu-TTS-v3-Turbo`, also Apache 2.0) — **commercial-safe**,
  unlike MMS. v3 Turbo is the latest open-source version (v4 is proprietary,
  API-only). ~131 M params, 48 kHz, 25 preset voices (North/Central/South),
  voice cloning, OpenAI-compatible server (`apps/openai_speech.py`,
  POST /v1/audio/speech). CPU path is torch-free ONNX Runtime.
- Install: venv `venv-vieneu` 918 MB. Model files for the fp32 ONNX path
  (~503 MB total, all sha256-verified against LFS oids): backbone 396.1 MB,
  acoustic 13.6 MB, heads 24.6 MB, decode/prefill ~0.3 MB each, denoiser
  40.7 MB, speaker encoder 27.0 MB.
  **Install lesson:** `huggingface_hub` download stalled at 0 bytes for
  4.5 min through the proxy — the fix was downloading the blobs directly
  with curl into `~/.cache/huggingface/hub/blobs/<oid>` (curl to the HF CDN
  runs ~1.5–4 MB/s); the SDK then reused them.
- Voice tested: preset **"Mai Anh"** (female).
- Speed: native **238 wpm speech-only (211 wpm overall)** — per-segment
  239/250/200/242 wpm. Synthesis RTF **1.49–1.92** on this VPS (slower than
  real-time; README claims CPU RTF ~0.5 on a 12th-gen i5). **Cold model load
  197.0 s** (~3.3 min per process — ONNX session init on 1.5 CPU).
- **v3 Turbo has NO speed control in the SDK** (checked `fast.py` infer
  signature: temperature, top_k, silence_p, crossfade_p only; `speed` exists
  only for v3 Nano, which is lower quality, 24 kHz). Workaround tested:
  ffmpeg `atempo=0.65` → ~155 wpm.
- Whisper (Base, -l vi): **native 32/40 = 80.0%**, **atempo-slowed 31/40 =
  77.5%** — atempo does NOT help accuracy (gap is 1 word, noise-level).
  Errors, native: "thủy"→"kỳ", "Thủy" (sentence 2) dropped, "viết"→"vết",
  "sổ"→"số" (×2), "log"→"hốc"/"lắc", "Đăng"→"Năng". Slowed: "thủy"→"khủy"
  (×2), "viết"→"vết", "nhật"→"nhất", "tàu"→"tao" (×2), "log"→"lớp" (×2),
  "Đăng"→"Năng".
- Samples: `vieneu.wav` (16 kHz mono, 11.38 s), `vieneu_48k.wav` (48 kHz
  original), `vieneu_slow.wav` (atempo 0.65, 17.48 s), `vieneu_slow48k.wav`.
  Test script `vieneu_test.py`, timing `vieneu_timing.txt`, log
  `vieneu_test.log`.

## valtec-tts (v-tts) — BLOCKED (private model repos)

- Repo: https://github.com/tronghieuit/valtec-tts, commit
  `e22eef3267869375e40a096b376cde94aa41e610` (2026-07-23). Licence
  **CC BY-NC 4.0 — non-commercial** ("Commercial use requires written
  permission" — same licence problem as MMS).
- Claimed (README): VITS-based, **74.8 M params** zero-shot / 57.97 M
  multi-speaker, 5 built-in voices (NF, SF, NM1, SM, NM2), Python API
  `from v_tts import TTS`, CLI `infer.py`, Gradio demo, Windows .exe v1.0.5
  (394 MB). Claimed CPU RTF ~0.24–0.34 (i5-14500).
- Install: venv `venv-valtec` 2.0 GB (torch 2.15.0+cpu + torchaudio 2.11.1+cpu
  + librosa + gruut + viphoneme + underthesea + vinorm + gradio 6.32 + …).
  First install attempt failed with "No space left on device": **/tmp is a
  512 MB tmpfs** and pip builds wheels there — fixed by
  `TMPDIR=<workdir>/tmpbuild` (on the 150 GB disk); second attempt succeeded.
  (Also note: no `espeak`/`espeak-ng` binary exists on this VPS.)
- **Blocker (verified, twice):** `TTS()` calls
  `snapshot_download(repo_id="v-tts/v-tts-pretrained")` (and
  `v-tts/v-zeroshot-voice-cloning` for zero-shot), but the HF author `v-tts`
  has NO public models (API list empty) and the repo URL returns HTTP 401.
  Probe (`valtec_probe.py`) captured the exact error:
  `RuntimeError: Failed to download model from v-tts/v-tts-pretrained:
  401 Client Error. Repository Not Found for url:
  https://huggingface.co/api/models/v-tts/v-tts-pretrained/revision/main.
  Invalid username or password.` — the model repos are private/gated or
  deleted. No weights in the cloned repo (no `pretrained/` dir). No fallback
  URL in the code. Cannot test without HF auth (not allowed: no signups).
  The code accepts a local `model_path` if weights are ever obtained
  elsewhere.
- No wav sample exists for valtec (nothing to synthesise with).

## VietVoice-TTS — tested, accurate enough, far too slow on this VPS

- Repo: https://github.com/nguyenvulebinh/VietVoice-TTS, commit
  `d4e8a22525437fc976ee9bc4dfd41ceb4b311248` (2025-07-14). Licence **MIT**
  (code). ONNX Runtime flow-matching diffusion, 24 kHz, `speed` config
  exists (default 1.0 — **not tested at other values**), gender/area/group/
  emotion presets, Gradio UI + Python API. No OpenAI-compatible endpoint in
  the repo.
- Install: package `vietvoicetts 0.1.0` in light venv `venv-vietvoice`
  (1.1 GB after adding torch — see below). Model file `model-bin.pt` is a
  tarfile of ONNX models, **1,508,003,328 bytes (1.44 GB)**, downloaded in
  full to `~/.cache/vietvoicetts/model-bin.pt` (first curl died at 95.9%,
  resumed with `curl -C -`; ~1.5–4 MB/s).
  **Undocumented dependency:** the README's install steps do not list torch,
  but `tts_engine.py` imports torch at module level — the first test run
  died with `ModuleNotFoundError: No module named 'torch'`; fixed with
  `pip install torch --index-url https://download.pytorch.org/whl/cpu`
  (torch 2.15.0+cpu).
- Voice tested: female / northern / **news** (group default) / neutral — the
  engine picks a built-in reference sample matching the preset
  (`select_sample`); the 6.8 s reference clip is processed on every call,
  which is part of why short segments are so slow.
- Speed: native **203 wpm speech-only (183 wpm overall)** — per-segment
  223/186/242/185 wpm. Synthesis RTF **74–178 per segment** (see table);
  total wall 1089.6 s for the 4 segments including model load. A 45 s video
  would take roughly an hour of synthesis on this VPS. The `speed` config
  (default 1.0) was NOT tested — it would not fix the RTF problem anyway
  (fewer diffusion steps via `nfe_step`, default 32, is the other knob;
  halving it would still leave RTF ~40+).
- Whisper (Base, -l vi): **28/40 = 70.0%** on the corrected run. Errors are
  mostly tone-mark confusions Whisper Base makes on this voice: "mẹo"→"mẹ",
  "viết"→"vết", "sổ"→"số" (×2), "ký"→"kí" (×2), "tàu"→"tau" (×2),
  "log"→"lót" (×2), "tên"→"tiên".
- Samples: `vietvoice.wav` (16 kHz mono, 13.12 s), `vietvoice_24k.wav`
  (24 kHz original). Test script `vietvoice_test.py`, timing
  `vietvoice_timing.txt`, logs `vietvoice_test.log` (first run) /
  `vietvoice_test2.log` (corrected re-run).

### The VietVoice clipping incident — my test bug, corrected

The first VietVoice run produced a Whisper score of **20.0%** and a wav that
measured -0.94 LUFS / TP +4.81 dBTP with 77.84% of samples saturated. That
was **my script's bug, not the model's**: the decode ONNX model returns
**int16-scale audio** (raw dtype `int16`, max |value| 31613 — confirmed by
printing the returned array and by the library's own code:
`normalize_to_int16`, `.astype(np.int16)` throughout the crossfade path,
`fix_clipped_audio` checks `max_val >= 32767`). My script converted the
array to float32 without rescaling, so `soundfile.write` (PCM_16) clipped
everything to ±1.0. The library's own `save_audio` writes the int16 array
directly (no scaling), which is why the UI/CLI output is fine. I re-ran all
4 segments with `/32768.0` (log `vietvoice_test2.log`); the corrected wav
measures RMS 0.142, 0% clipped, and Whisper 70.0%. The invalid files are
kept, renamed `vietvoice_24k_CLIPPED_INVALID.wav`,
`vietvoice_CLIPPED_INVALID.wav`, `whisper_vietvoice_CLIPPED_INVALID.txt` —
**do not use them as samples**. Anyone re-running VietVoice must divide the
returned array by 32768 (or keep int16 dtype) before saving as float WAV.

### Per-segment RTF (VietVoice, corrected run)

| Segment | Audio | Words | wpm | Synth | RTF |
|---|---|---|---|---|---|
| Hook | 4.03 s | 15 | 223 | 314.58 s | 78.02 |
| Beat-a | 3.55 s | 11 | 186 | 315.50 s | 88.82 |
| Beat-b | 0.99 s | 4 | 242 | 176.70 s | 178.12 |
| Payoff | 3.24 s | 10 | 185 | 260.62 s | 80.37 |

(The short segment is slowest in RTF because the 6.8 s reference clip is
re-processed on every call — a fixed ~250–315 s overhead per call.)

## Cross-cutting finding: nobody says "log"

All three testable voices mispronounce the English loanword "log" in "sổ
log": MMS "lá"/"luôn", VieNeu "hốc"/"lắc"/"lớp", VietVoice "lót". This is
consistent with the round-1/2 MMS finding. **On-screen text must keep
carrying the correct spelling** ("SỔ LOG", "CHIP LOG") for every voice.
"Đăng" is also fragile (VieNeu "Năng", MMS "nhật" in one place); "sổ" vs
"số" is confused by Whisper Base for all three voices (counted wrong for
all equally, so the comparison stays fair — but a human listen is the only
way to know whether the models really say "sổ" or "số").

## Files produced (this dir)

- `voice_compare_20261116.md` — this report.
- Samples (16 kHz mono, same as the MMS samples): `vieneu.wav`,
  `vieneu_slow.wav` (atempo 0.65), `vietvoice.wav`, `mms_round2c_base.wav`
  (copy of round-2 variant C for the fair Base re-check). Originals:
  `vieneu_48k.wav`, `vieneu_slow48k.wav`, `vietvoice_24k.wav`.
- Test scripts: `vieneu_test.py`, `vietvoice_test.py` (corrected),
  `valtec_probe.py`, `score_whisper.py`, `whisper_check.py`.
- Whisper transcripts: `whisper_vieneu.txt`, `whisper_vieneu_slow.txt`,
  `whisper_vietvoice.txt`, `whisper_mms_round2c_base.txt`.
- Logs: `vieneu_test.log`, `vietvoice_test.log` (first run),
  `vietvoice_test2.log` (corrected re-run), `valtec_install.log`,
  `valtec_install2.log`.
- Cloned repos (NOT in git — excluded by auto_push/.gitignore, as are the
  venvs): `vieneu/`, `valtec/`, `vietvoice/`. Venvs: `venv-vieneu` (918 MB),
  `venv-vietvoice` (1.1 GB), `venv-valtec` (2.0 GB).

## Honest limits

- **No human listened to any sample** — Whisper word accuracy only, not
  naturalness/prosody. The user is the judge and must listen, especially to
  `vieneu.wav` (the commercial-safe candidate) vs the MMS baseline.
- Whisper Base is weak: the % gaps between the three voices are small
  (VieNeu 80.0 / MMS 72.5 / VietVoice 70.0 — a 2–3 word gap), and several
  "errors" are Whisper's own tone confusions (sổ/số, ký/kí, tàu/tau) rather
  than proven mispronunciations. The decisive differences are **speed
  (VieNeu 238 / VietVoice 203 / MMS 160 wpm)** and **RTF (MMS ≪ VieNeu 1.5–1.9
  ≪ VietVoice 74–256)** — those are measured, not judged.
- Speed was measured at default settings except MMS (rate 0.92) and the
  VieNeu atempo variant. VietVoice's `speed` config and `nfe_step` were not
  tested; neither would make it viable on this VPS CPU.
- valtec could not be tested at all — no weights. Its README speed/license
  claims are unverified.
- All synthesis ran on this VPS (1.5 shared CPUs, ~8 GB RAM, no GPU).
  VieNeu and VietVoice would both be much faster on the user's PC
  (RTX 5060 Ti) with GPU runtimes — not measured here.
