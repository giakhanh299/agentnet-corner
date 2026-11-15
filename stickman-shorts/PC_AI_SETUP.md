# PC local AI stack — setup (verified 2026-11-15 ~17:15 +07)

PC: DESKTOP-01O3HNF, Windows 11 Pro, 32 GB RAM, user `w`, Tailscale 100.101.158.71.
GPU: **NVIDIA GeForce RTX 5060 Ti, 16 GB VRAM, driver 610.88** (checked with
`nvidia-smi`; minimum for Blackwell sm_120 is 572.60 — passed, no driver work needed).

## Result: WORKS. All three tools verified with real runs.

| Tool | Version | Verified result |
|---|---|---|
| PyTorch (cu128) | torch **2.11.0+cu128**, CUDA **12.8** | `torch.cuda.is_available()` True, device `NVIDIA GeForce RTX 5060 Ti`, capability `(12, 0)` = sm_120; 512×512 matmul on CUDA ok (mean \|x\| 18.04) |
| faster-whisper | **1.2.1** (ctranslate2 4.9.0), model **large-v3** FP16 on CUDA | Ep001 voice.wav (48.8s): transcribed in **4.7s (RTF 0.10x)**; **130/137 words = 94.9%** match vs the script (7 misheard: tone confusions lả→lã, tiếp→kiếp, vẫn→nhận, khi→thì, nghĩ→nghỉ). VPS whisper.cpp Base on the same file: 113/137 = 82.5% at ~1x real-time. PC is ~10x faster and ~12 points more accurate. |
| MMS-TTS (Vietnamese) | transformers **5.23.0**, model **facebook/mms-tts-vie** on CUDA | 3 sentences (55 words, 19.6s audio) synthesized in **0.9s** (hook 0.68s / beat1 0.11s / payoff 0.07s). Whisper self-check of the output: **52/55 = 94.5%** words heard correctly (missed: lả, cày, tiếp — the same known MMS weak words). |

Paths on the PC:

- venv: `C:\Users\w\agentnet-corner\ai-stack\.venv-ai` (Python **3.12.10**, pip 26.3) — **separate** from the stickman venv (`.venv-win`) and from the user's own Python ecosystem (Python 3.10/3.14, `D:\02_CONG_CU\...`) — **none of it touched**.
- Test files: `C:\Users\w\agentnet-corner\ai-stack\` — `ai_whisper_test.py`, `ai_tts_test.py`, `ep001_voice.wav` (+ `ep001_voice_16k.wav`), `ep001_fw_transcript.txt`, `tts_test.wav`.
- Logs on the PC: `C:\Users\w\ai_torch_install.log`, `ai_whisper_install.log`, `ai_whisper_fix.log`, `ai_whisper_fix2.log`, `ai_whisper_rerun.log`, `ai_cublas_diag.log`, `ai_tts_install.log`.
- Size: ai-stack folder **~4.7 GB** (venv only; models live in the shared HF cache, see below). C: free **61.8 GB** after install.
- A copy of the TTS test output is on VPS 1: `stickman-shorts/test_audio/pc_tts_test.wav` (21.1s, 16 kHz mono, 675,756 bytes, ffprobe-verified).

## Models — already cached, nothing downloaded

The PC has a user-level env var `HF_HOME=D:\0.1_FACE_BOOK\DUNG_CHUNG\MODELS\HF_CACHE`
(the user's own shared model cache). Both models were **already in that cache**,
so no download was needed: large-v3 loads in ~3s, MMS-TTS in ~13.7s.
Do NOT move or delete that cache — the venv depends on it. If it is ever gone,
both tools will re-download their models there on first use (large-v3 ~3 GB,
mms-tts-vie ~0.5 GB). No new files were written into the user's cache by this setup.

## How it was installed (exact commands)

All steps run from VPS 1 over SSH with the pattern in `PC_SETUP.md`
(.ps1 files scp'd to the PC, foreground run with `< NUL` + `Start-Transcript`).
Python used: `C:\Users\w\AppData\Local\Programs\Python\Python312\python.exe`
(bare `python` is 3.10.11 — do NOT use it).

```powershell
# 1. venv + PyTorch cu128
C:\...\Python312\python.exe -m venv C:\Users\w\agentnet-corner\ai-stack\.venv-ai
.venv-ai\Scripts\python.exe -m pip install --upgrade pip
.venv-ai\Scripts\python.exe -m pip install torch --index-url https://download.pytorch.org/whl/cu128
# (torch 2.11.0+cu128 came from the PC's own pip cache — install took ~100s)

# 2. faster-whisper (+ av pin, see Bugs)
.venv-ai\Scripts\python.exe -m pip install faster-whisper
.venv-ai\Scripts\python.exe -m pip install "av==14.0.0" soundfile

# 3. MMS-TTS
.venv-ai\Scripts\python.exe -m pip install transformers
```

Full pinned versions in the venv (from `pip list` 2026-11-15 ~17:14):
torch 2.11.0+cu128, faster-whisper 1.2.1, ctranslate2 4.9.0, av 14.0.0,
transformers 5.23.0, numpy 2.5.4, soundfile 0.14.0, tokenizers 0.23.3,
huggingface-hub 2.4.0, onnxruntime 1.32.0, safetensors 0.8.0.

## How to re-run each tool

```powershell
$VenvPy = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Scripts\python.exe"
$TorchLib = "C:\Users\w\agentnet-corner\ai-stack\.venv-ai\Lib\site-packages\torch\lib"
$env:PATH = "$TorchLib;$env:PATH"   # required for faster-whisper (see Bugs #2)

# Transcribe any wav (16 kHz mono) with large-v3 on CUDA:
& $VenvPy C:\Users\w\agentnet-corner\ai-stack\ai_whisper_test.py large-v3
# (edit AUDIO/OUT at the top of ai_whisper_test.py for a different file;
#  use "medium" instead of "large-v3" if VRAM is ever tight)

# Synthesize Vietnamese with MMS-TTS on CUDA (edit SENTENCES in the script):
& $VenvPy C:\Users\w\agentnet-corner\ai-stack\ai_tts_test.py
```

Reusable scripts (in this repo, next to the other PC scripts):
`ai_torch_install.ps1`, `ai_whisper_install.ps1`, `ai_whisper_fix.ps1`,
`ai_whisper_fix2.ps1`, `ai_whisper_rerun.ps1`, `ai_cublas_diag.ps1`,
`ai_tts_install.ps1`, `ai_whisper_test.py`, `ai_tts_test.py`.

## Bugs found and fixed (all three are real — do not skip them)

1. **faster-whisper 1.2.1 + av 19 = broken.** pip installs av 19.0.2, but
   faster-whisper calls `av.open(..., metadata_errors="ignore")`, a parameter
   av 19 removed → `TypeError: open() got an unexpected keyword argument
   'metadata_errors'`. Fix: pin **`av==14.0.0`** (has a cp312 wheel).
   `av==14.4.0` has NO cp312 wheel — pip falls back to building from source
   and fails (no MSVC Build Tools on the PC). Do NOT install Build Tools just
   for this.
2. **ctranslate2 cannot find cuBLAS.** torch 2.11 keeps its CUDA DLLs in
   `site-packages\torch\lib` (there is NO `site-packages\nvidia` dir in this
   install). `os.add_dll_directory()` does NOT help — ctranslate2 loads the
   DLL with plain LoadLibrary, which searches PATH, not AddDllDirectory dirs.
   Fix: **prepend torch\lib to `$env:PATH` before launching python**
   (done in `ai_whisper_rerun.ps1` and `ai_tts_install.ps1`). The
   `os.add_dll_directory` preamble in the .py files is kept as belt-and-braces
   but is NOT sufficient on its own. Error if missed:
   `RuntimeError: Library cublas64_12.dll is not found or cannot be loaded`.
3. **Vietnamese text crashes console printing.** The Windows console is cp1252;
   printing a transcript with diacritics raises
   `UnicodeEncodeError: 'charmap' codec can't encode characters`. Fix:
   `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` at the top of
   every script (file output was already UTF-8 and was unaffected).

## Honest limits

- **No human has listened** to the PC's TTS output (only the Whisper check,
  94.5%). The 3 missed words (lả, cày, tiếp) are tone confusions — the same
  words MMS-TTS got wrong on the VPS. Before using the voice in a posted
  video, a human should listen once.
- MMS-TTS pacing: the hook sentence came out at **195 wpm** (14 words in
  4.30s), above the 150–165 safe zone — that is the model's own pacing on
  short sentences, same as on the VPS, not a PC issue. Beat 1 was 164 wpm,
  payoff 155 wpm.
- The "~30% mishearing" figure quoted for the VPS Whisper Base in earlier
  reports is an overestimate: measured on the same file it is **17.5%**
  (113/137). large-v3 is 5.1% — the gap is real but smaller than claimed.
- faster-whisper's file-path route is untested after the av pin (the test
  scripts use the soundfile + numpy-array route, which bypasses av entirely).
  The numpy route is the recommended one for scripts.

## NOT done yet

- No background service started; nothing runs on boot. These are on-demand
  tools, run by hand or from a script.
- No Ollama / LM Studio / ComfyUI installed (out of scope for this task;
  see `codexreply.md` §2.1 for the checklist if they are wanted later).
- large-v3-turbo not tested (large-v3 already runs at RTF 0.10x — turbo
  would be faster still but is not needed yet).
- No real episode rendered on the PC yet; `assemble.py --srt` still
  untested there (see `PC_SETUP.md` Notes).
- The venv is NOT in git (only this doc + the .ps1/.py scripts are).
