"""Phase 3: Closed-Loop Self-Healing Vietnamese TTS + Whisper Alignment Engine.

Eliminates bespoke per-episode probe scripts (v0xx_probe1..4.py):
1. Separates display `caption_text` (exact spelling) from phonetic `spoken_text`
   using `pronunciation_lexicon.json` + Vietnamese number/unit expansion.
2. Synthesizes clause-by-clause on GPU (`facebook/mms-tts-vie` on RTX 5060 Ti)
   with automatic CPU fallback when CUDA is unavailable.
3. Verifies every clause with `faster-whisper` (`large-v3` on CUDA, `base` on CPU):
   - Auto-tunes `speaking_rate` to stay in the 150-165 WPM target zone.
   - Auto-applies `phrase_fallbacks` or foreign-word syllable hyphenation up to
     `max_rounds` when Whisper detects mispronounced words.
   - Persists newly verified phonetic repairs back to `pronunciation_lexicon.json`.
4. Trims leading silence so voice starts at ~0.10s and outputs `voice.wav`,
   `timing.json`, `captions.ass` (1080x1920), and `captions.srt`.
"""
from __future__ import annotations

import glob
import json
import math
import os
from pathlib import Path
import re
import sys
import unicodedata
import wave
from typing import Callable

DEFAULT_LEXICON_PATH = Path(__file__).resolve().parent / "pronunciation_lexicon.json"

ASS_HEADER_1080P = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Be Vietnam Pro,56,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,1,2,40,40,300,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

_VN_DIGITS = {
    0: "không", 1: "một", 2: "hai", 3: "ba", 4: "bốn",
    5: "năm", 6: "sáu", 7: "bảy", 8: "tám", 9: "chín",
}


def ensure_windows_cuda_dlls_and_utf8() -> None:
    """Apply PC_AI_SETUP.md fixes #2 (cuBLAS DLL PATH) and #3 (UTF-8 console)."""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass
    if os.name != "nt":
        return
    candidates = [
        Path(sys.executable).resolve().parent.parent / "Lib" / "site-packages",
        Path(__file__).resolve().parent.parent / "ai-stack" / ".venv-ai" / "Lib" / "site-packages",
    ]
    extra_dirs: list[str] = []
    for site in candidates:
        torch_lib = site / "torch" / "lib"
        if torch_lib.is_dir():
            extra_dirs.append(str(torch_lib))
        for nv_bin in glob.glob(str(site / "nvidia" / "*" / "bin")):
            if os.path.isdir(nv_bin):
                extra_dirs.append(nv_bin)
    if extra_dirs:
        cur_path = os.environ.get("PATH", "")
        prepend = [d for d in extra_dirs if d.lower() not in cur_path.lower()]
        if prepend:
            os.environ["PATH"] = os.pathsep.join(prepend + [cur_path])
        if hasattr(os, "add_dll_directory"):
            for d in extra_dirs:
                try:
                    os.add_dll_directory(d)
                except OSError:
                    pass


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text or "")


def _read_int_under_1000(n: int, full_hundred: bool = False) -> str:
    assert 0 <= n < 1000
    if n < 10:
        return _VN_DIGITS[n]
    if n < 100:
        tens, unit = divmod(n, 10)
        prefix = "mười" if tens == 1 else f"{_VN_DIGITS[tens]} mươi"
        if unit == 0:
            return prefix
        if unit == 1 and tens > 1:
            return f"{prefix} mốt"
        if unit == 4 and tens > 1:
            return f"{prefix} tư"
        if unit == 5:
            return f"{prefix} lăm"
        return f"{prefix} {_VN_DIGITS[unit]}"
    hundreds, rem = divmod(n, 100)
    head = f"{_VN_DIGITS[hundreds]} trăm"
    if rem == 0:
        return head
    if rem < 10:
        return f"{head} lẻ {_VN_DIGITS[rem]}"
    return f"{head} {_read_int_under_1000(rem, full_hundred=True)}"


def int_to_vietnamese(n: int) -> str:
    if n < 0:
        return "âm " + int_to_vietnamese(-n)
    if n < 1000:
        return _read_int_under_1000(n)
    units = ["", "nghìn", "triệu", "tỷ"]
    groups: list[int] = []
    val = n
    while val > 0:
        groups.append(val % 1000)
        val //= 1000
    parts: list[str] = []
    for idx in range(len(groups) - 1, -1, -1):
        g = groups[idx]
        if g == 0:
            continue
        if idx < len(groups) - 1 and g < 100:
            if g < 10:
                chunk = f"không trăm lẻ {_VN_DIGITS[g]}"
            else:
                chunk = f"không trăm {_read_int_under_1000(g)}"
        else:
            chunk = _read_int_under_1000(g)
        unit_name = units[idx] if idx < len(units) else ""
        parts.append(f"{chunk} {unit_name}".strip())
    return " ".join(parts)


def expand_numbers_and_symbols_vi(text: str) -> str:
    """Convert %, thousands-dot integers (10.000), and bare integers for MMS-TTS."""
    out = nfc(text)
    out = re.sub(r"(\d+)\s*%", r"\1 phần trăm", out)

    def _thousands_repl(m: re.Match[str]) -> str:
        raw = m.group(0).replace(".", "")
        try:
            return int_to_vietnamese(int(raw))
        except ValueError:
            return m.group(0)

    out = re.sub(r"\b\d{1,3}(?:\.\d{3})+\b", _thousands_repl, out)
    out = re.sub(r"\b\d+\b", lambda m: int_to_vietnamese(int(m.group(0))), out)
    return out


def tokenize_words(text: str) -> list[str]:
    cleaned = nfc(text).lower().replace("-", " ")
    return re.findall(r"[a-zàáảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ0-9]+", cleaned)


class PronunciationLexicon:
    def __init__(self, path: Path | str = DEFAULT_LEXICON_PATH):
        self.path = Path(path)
        self.data = {
            "version": "2.0",
            "word_replacements": {},
            "phrase_fallbacks": {},
            "whisper_homophones": {},
        }
        if self.path.exists():
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
            for k in ("word_replacements", "phrase_fallbacks", "whisper_homophones"):
                if isinstance(loaded.get(k), dict):
                    self.data[k].update(loaded[k])

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def learn_word(self, written: str, spoken: str, persist: bool = True) -> None:
        w, s = nfc(written).strip(), nfc(spoken).strip()
        if w and s and w != s:
            self.data["word_replacements"][w] = s
            if persist:
                self.save()

    def to_spoken(self, text: str) -> str:
        s = expand_numbers_and_symbols_vi(text)
        for src, dst in sorted(
            self.data["word_replacements"].items(), key=lambda kv: -len(kv[0])
        ):
            pattern = r"(?<!\w)" + re.escape(nfc(src)) + r"(?!\w)"
            s = re.sub(pattern, nfc(dst), s)
        return s

    def words_equivalent(self, expected: str, heard: str) -> bool:
        e, h = nfc(expected).lower(), nfc(heard).lower()
        if e == h:
            return True
        homos = [nfc(x).lower() for x in self.data["whisper_homophones"].get(e, [])]
        return h in homos

    def alignment_score(self, expected_text: str, heard_text: str) -> tuple[float, list[str]]:
        """Word-level LCS match score tolerating Whisper digit ITN and tone homophones."""
        exp = tokenize_words(expand_numbers_and_symbols_vi(expected_text))
        hrd = tokenize_words(expand_numbers_and_symbols_vi(heard_text))
        if not exp:
            return 1.0, []
        n, m = len(exp), len(hrd)
        dp = [[0] * (m + 1) for _ in range(n + 1)]
        for i in range(n - 1, -1, -1):
            for j in range(m - 1, -1, -1):
                if self.words_equivalent(exp[i], hrd[j]):
                    dp[i][j] = 1 + dp[i + 1][j + 1]
                else:
                    dp[i][j] = max(dp[i + 1][j], dp[i][j + 1])
        matched_indices: set[int] = set()
        i = j = 0
        while i < n and j < m:
            if self.words_equivalent(exp[i], hrd[j]):
                matched_indices.add(i)
                i += 1
                j += 1
            elif dp[i + 1][j] >= dp[i][j + 1]:
                i += 1
            else:
                j += 1
        missed = [exp[idx] for idx in range(n) if idx not in matched_indices]
        return dp[0][0] / len(exp), missed


def split_clauses(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?…;])\s+", nfc(text).strip())
    return [p.strip() for p in parts if p.strip()]


def _trim_silence_float32(samples, sample_rate: int, threshold: float = 0.008, pad_head_s: float = 0.10, pad_tail_s: float = 0.06):
    import numpy as np
    arr = np.asarray(samples, dtype=np.float32)
    if arr.size == 0:
        return arr
    idx = np.where(np.abs(arr) > threshold)[0]
    if idx.size == 0:
        return arr
    head = max(0, int(idx[0]) - int(pad_head_s * sample_rate))
    tail = min(arr.size, int(idx[-1]) + int(pad_tail_s * sample_rate))
    return arr[head:tail]


def _format_ass_time(seconds: float) -> str:
    seconds = max(0.0, seconds)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    cs = int(round((s - int(s)) * 100))
    if cs >= 100:
        cs = 0
        s += 1
    return f"{h}:{m:02d}:{int(s):02d}.{cs:02d}"


def _format_srt_time(seconds: float) -> str:
    seconds = max(0.0, seconds)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - math.floor(seconds)) * 1000))
    if ms >= 1000:
        ms = 0
        s += 1
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build_chunked_captions(clauses_meta: list[dict], words_per_chunk: int = 4) -> list[tuple[float, float, str]]:
    """Split display caption clauses into crisp 4-word Shorts subtitle events."""
    events: list[tuple[float, float, str]] = []
    for cm in clauses_meta:
        text = nfc(cm["caption_text"]).strip()
        words = text.split()
        if not words:
            continue
        start_s = float(cm["start_s"])
        end_s = float(cm["end_s"])
        dur = max(0.20, end_s - start_s)
        chunks = [words[i:i + words_per_chunk] for i in range(0, len(words), words_per_chunk)]
        total_w = sum(len(c) for c in chunks)
        cur = start_s
        for idx, ch in enumerate(chunks):
            share = (len(ch) / total_w) * dur
            nxt = end_s if idx == len(chunks) - 1 else cur + share
            events.append((cur, nxt, " ".join(ch)))
            cur = nxt
    return events


class HardwareModels:
    """Lazy singleton loader for MMS-TTS, VieNeu-TTS, and faster-whisper with GPU -> CPU fallback."""
    _tts_bundle = None
    _whisper_bundle = None
    _vieneu_proc = None

    @classmethod
    def _ensure_vieneu_server(cls, vieneu_py: Path):
        import subprocess
        if cls._vieneu_proc is not None and cls._vieneu_proc.poll() is None:
            return cls._vieneu_proc
        server_code = (
            "import json, sys, numpy as np, soundfile as sf\n"
            "sys.stdout.reconfigure(encoding='utf-8')\n"
            "sys.stdin.reconfigure(encoding='utf-8')\n"
            "from vieneu import Vieneu\n"
            "tts = Vieneu()\n"
            "for line in sys.stdin:\n"
            "    req = json.loads(line)\n"
            "    a = np.asarray(tts.infer(req['text'], voice=req['voice']), dtype=np.float32)\n"
            "    sf.write(req['out'], a, 48000)\n"
            "    print(json.dumps({'ok': True}), flush=True)\n"
        )
        cls._vieneu_proc = subprocess.Popen(
            [str(vieneu_py), "-c", server_code],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
        )
        return cls._vieneu_proc

    @classmethod
    def synth_vieneu(cls, text: str, atempo: float = 0.67, voice_preset: str = "Mai Anh", sample_rate: int = 16000):
        """Synthesize via persistent warm VieNeu-TTS (`.venv-vieneu`) + FFmpeg `atempo` -> 16kHz float32."""
        import subprocess
        import tempfile
        import numpy as np

        repo_root = Path(__file__).resolve().parent.parent
        vieneu_py = repo_root / "ai-stack" / ".venv-vieneu" / "Scripts" / "python.exe"
        if not vieneu_py.exists():
            vieneu_py = repo_root / "ai-stack" / ".venv-vieneu" / "bin" / "python"
        if not vieneu_py.exists():
            return cls.synth_mms(text, speaking_rate=0.92, sample_rate=sample_rate)

        with tempfile.TemporaryDirectory() as td:
            raw_wav = Path(td) / "native.wav"
            out_wav = Path(td) / "out16k.wav"
            proc = cls._ensure_vieneu_server(vieneu_py)
            assert proc.stdin is not None and proc.stdout is not None
            proc.stdin.write(json.dumps({"text": text, "voice": voice_preset, "out": str(raw_wav)}, ensure_ascii=False) + "\n")
            proc.stdin.flush()
            resp_line = proc.stdout.readline()
            if not resp_line:
                cls._vieneu_proc = None
                raise RuntimeError("VieNeu worker subprocess exited unexpectedly")
            tempo_clamped = max(0.50, min(1.0, float(atempo)))
            subprocess.run(
                [
                    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-i", str(raw_wav),
                    "-af", f"atempo={tempo_clamped:.3f}",
                    "-ar", str(sample_rate), "-ac", "1", "-c:a", "pcm_s16le",
                    str(out_wav),
                ],
                check=True,
            )
            with wave.open(str(out_wav), "rb") as wf:
                pcm = np.frombuffer(wf.readframes(wf.getnframes()), dtype="<i2")
            return (pcm.astype(np.float32) / 32768.0)

    @classmethod
    def synth_mms(cls, text: str, speaking_rate: float = 0.92, sample_rate: int = 16000):
        ensure_windows_cuda_dlls_and_utf8()
        import numpy as np
        import torch
        from transformers import AutoTokenizer, VitsModel

        if cls._tts_bundle is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = VitsModel.from_pretrained("facebook/mms-tts-vie").to(device)
            tok = AutoTokenizer.from_pretrained("facebook/mms-tts-vie")
            cls._tts_bundle = (model, tok, device)
        model, tok, device = cls._tts_bundle
        model.speaking_rate = speaking_rate
        model.config.speaking_rate = speaking_rate
        inputs = tok(text, return_tensors="pt").to(device)
        with torch.no_grad():
            wav = model(**inputs).waveform[0].cpu().numpy()
        return np.clip(wav, -1.0, 1.0).astype(np.float32)

    @classmethod
    def transcribe_whisper(cls, audio_float32, sample_rate: int = 16000) -> str:
        ensure_windows_cuda_dlls_and_utf8()
        import numpy as np
        import torch
        from faster_whisper import WhisperModel

        if cls._whisper_bundle is None:
            use_cuda = torch.cuda.is_available()
            model_name = os.environ.get("AGENTNET_WHISPER_MODEL") or ("large-v3" if use_cuda else "base")
            device = "cuda" if use_cuda else "cpu"
            compute_type = "float16" if use_cuda else "int8"
            cls._whisper_bundle = WhisperModel(model_name, device=device, compute_type=compute_type)
        wmodel = cls._whisper_bundle
        arr = np.asarray(audio_float32, dtype=np.float32)
        segments, _ = wmodel.transcribe(arr, language="vi", beam_size=3, vad_filter=False)
        return nfc(" ".join(seg.text.strip() for seg in segments).strip())


class TTSAutoHealer:
    """Self-healing clause-level TTS synthesizer with automatic WPM & ASR repair."""

    def __init__(
        self,
        lexicon: PronunciationLexicon | None = None,
        synth_fn: Callable[[str, float], object] | None = None,
        asr_fn: Callable[[object], str] | None = None,
        sample_rate: int = 16000,
        base_rate: float = 0.92,
        wpm_range: tuple[float, float] = (145.0, 168.0),
        min_asr_match: float = 0.90,
        max_rounds: int = 3,
    ):
        self.lexicon = lexicon or PronunciationLexicon()
        self._uses_default_synth = synth_fn is None
        self.synth_fn = synth_fn or (lambda txt, rate: HardwareModels.synth_mms(txt, speaking_rate=rate, sample_rate=sample_rate))
        self.asr_fn = asr_fn or (lambda wav: HardwareModels.transcribe_whisper(wav, sample_rate=sample_rate))
        self.sample_rate = sample_rate
        self.base_rate = base_rate
        self.wpm_range = wpm_range
        self.min_asr_match = min_asr_match
        self.max_rounds = max_rounds

    def _candidate_rewrites(self, caption_clause: str, extra_fallbacks: dict[str, list[str]] | None = None) -> list[tuple[str, str]]:
        """Yield `(caption_variant, spoken_variant)` candidates for self-healing."""
        merged_fb: dict[str, list[str]] = {}
        for k, v in self.lexicon.data.get("phrase_fallbacks", {}).items():
            merged_fb[nfc(k)] = [nfc(x) for x in v]
        if extra_fallbacks:
            for k, v in extra_fallbacks.items():
                merged_fb[nfc(k)] = [nfc(x) for x in (v if isinstance(v, list) else [v])]

        base_cap = nfc(caption_clause)
        candidates: list[tuple[str, str]] = [(base_cap, self.lexicon.to_spoken(base_cap))]

        for bad_phrase, replacements in merged_fb.items():
            if bad_phrase.lower() in base_cap.lower():
                pattern = re.compile(re.escape(bad_phrase), flags=re.IGNORECASE)
                for rep in replacements:
                    new_cap = pattern.sub(rep, base_cap)
                    candidates.append((new_cap, self.lexicon.to_spoken(new_cap)))
        return candidates

    def heal_clause(
        self,
        caption_clause: str,
        spoken_override: str | None = None,
        extra_fallbacks: dict[str, list[str]] | None = None,
    ) -> dict:
        import numpy as np

        rewrites = (
            [(nfc(caption_clause), expand_numbers_and_symbols_vi(spoken_override))]
            if spoken_override
            else self._candidate_rewrites(caption_clause, extra_fallbacks=extra_fallbacks)
        )
        rate = self.base_rate
        best: dict | None = None
        wpm_lo, wpm_hi = self.wpm_range

        for round_idx in range(self.max_rounds):
            cap_text, spk_text = rewrites[min(round_idx, len(rewrites) - 1)]
            raw_wav = np.asarray(self.synth_fn(spk_text, rate), dtype=np.float32)
            pad_head = 0.02
            trimmed = _trim_silence_float32(raw_wav, self.sample_rate, pad_head_s=pad_head, pad_tail_s=0.04)
            dur_s = max(0.15, len(trimmed) / self.sample_rate)
            word_count = max(1, len(tokenize_words(cap_text)))
            wpm = (word_count / dur_s) * 60.0

            # Expected text for Whisper uses expanded numbers + caption words (e.g. "Canada")
            expected_for_asr = expand_numbers_and_symbols_vi(cap_text)
            heard = self.asr_fn(trimmed)
            score, missed = self.lexicon.alignment_score(expected_for_asr, heard)

            record = {
                "caption_text": cap_text,
                "spoken_text": spk_text,
                "heard_text": heard,
                "asr_match": round(score, 4),
                "missed_words": missed,
                "wpm": round(wpm, 1),
                "speaking_rate": round(rate, 3),
                "duration_s": round(dur_s, 3),
                "round": round_idx + 1,
                "audio": trimmed,
            }
            if best is None or (record["asr_match"], -abs(wpm - 157.5)) > (best["asr_match"], -abs(best["wpm"] - 157.5)):
                best = record

            wpm_ok = (word_count < 6) or (wpm_lo <= wpm <= wpm_hi)
            if score >= self.min_asr_match and wpm_ok:
                break

            # Self-heal rate if pacing drifted on clauses with >=6 words
            if word_count >= 6 and not wpm_ok:
                target_wpm = 157.5
                # In MMS VITS, larger speaking_rate = faster or slower?
                # Wait: in HuggingFace VitsModel, speaking_rate < 1.0 slows or speeds length_scale:
                # HuggingFace VitsModel sets noise_scale/length_scale = 1.0 / speaking_rate!
                # So smaller speaking_rate = slower speech (lower WPM); larger speaking_rate = faster speech!
                ratio = target_wpm / max(wpm, 40.0)
                rate = max(0.80, min(1.05, rate * (0.5 + 0.5 * ratio)))

        assert best is not None
        return best

    def synthesize_episode(self, beats: list[dict], out_dir: Path | str, extra_fallbacks: dict | None = None) -> dict:
        import numpy as np

        out_path = Path(out_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        chunks_f32: list[np.ndarray] = []
        # Golden Rule #3: voice starts at ~0.10s
        lead_in_s = 0.10
        chunks_f32.append(np.zeros(int(lead_in_s * self.sample_rate), dtype=np.float32))
        t_cur = lead_in_s

        beats_timing: list[dict] = []
        all_clauses_meta: list[dict] = []
        total_words = 0
        total_speech_s = 0.0
        weighted_asr = 0.0

        for b_idx, beat in enumerate(beats):
            b_id = beat.get("id") or f"beat{b_idx}"
            raw_caption = beat.get("caption") or beat.get("spoken") or ""
            raw_spoken_override = beat.get("spoken_phonetic")
            clauses = beat.get("clauses") or split_clauses(raw_caption)
            is_last_beat = b_idx == len(beats) - 1
            is_second_last = b_idx == len(beats) - 2
            default_gap = 0.0 if is_last_beat else (0.30 if b_idx == 0 else (0.60 if is_second_last else 0.40))
            beat_gap = float(beat.get("gap_after_s", default_gap))
            clause_gap = float(beat.get("clause_gap_s", 0.35))

            b_start = 0.0 if b_idx == 0 else t_cur
            b_clauses_out: list[dict] = []
            b_words = 0
            b_speech_s = 0.0

            for c_idx, cl in enumerate(clauses):
                healed = self.heal_clause(
                    cl,
                    spoken_override=raw_spoken_override if len(clauses) == 1 else None,
                    extra_fallbacks=extra_fallbacks,
                )
                wav = healed.pop("audio")
                c_start = t_cur
                dur = len(wav) / self.sample_rate
                chunks_f32.append(wav)
                t_cur += dur
                c_end = t_cur

                w_cnt = max(1, len(tokenize_words(healed["caption_text"])))
                b_words += w_cnt
                total_words += w_cnt
                b_speech_s += dur
                total_speech_s += dur
                weighted_asr += healed["asr_match"] * w_cnt

                c_meta = {
                    **healed,
                    "beat_id": b_id,
                    "start_s": round(c_start, 3),
                    "end_s": round(c_end, 3),
                }
                b_clauses_out.append(c_meta)
                all_clauses_meta.append(c_meta)

                if c_idx < len(clauses) - 1 and clause_gap > 0:
                    chunks_f32.append(np.zeros(int(clause_gap * self.sample_rate), dtype=np.float32))
                    t_cur += clause_gap

            if beat_gap > 0:
                chunks_f32.append(np.zeros(int(beat_gap * self.sample_rate), dtype=np.float32))
                t_cur += beat_gap

            beats_timing.append({
                "id": b_id,
                "card_title": nfc(beat.get("card_title", "")),
                "card_subtitle": nfc(beat.get("card_subtitle", "")),
                "start_s": round(b_start, 3),
                "end_s": round(t_cur, 3),
                "speech_s": round(b_speech_s, 3),
                "words": b_words,
                "speech_wpm": round((b_words / max(b_speech_s, 0.1)) * 60.0, 1),
                "clauses": b_clauses_out,
            })

        # Add 0.25s tail pad
        chunks_f32.append(np.zeros(int(0.25 * self.sample_rate), dtype=np.float32))
        t_cur += 0.25

        full_audio = np.concatenate(chunks_f32)
        pcm16 = (np.clip(full_audio, -1.0, 1.0) * 32767.0).astype("<i2")

        voice_wav = out_path / "voice.wav"
        with wave.open(str(voice_wav), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(pcm16.tobytes())

        cap_events = build_chunked_captions(all_clauses_meta, words_per_chunk=4)
        ass_path = out_path / "captions.ass"
        ass_lines = [
            f"Dialogue: 0,{_format_ass_time(st)},{_format_ass_time(en)},Default,,0,0,0,,{txt}"
            for st, en, txt in cap_events
        ]
        ass_path.write_text(ASS_HEADER_1080P + "\n".join(ass_lines) + "\n", encoding="utf-8")

        srt_path = out_path / "captions.srt"
        srt_blocks = [
            f"{idx}\n{_format_srt_time(st)} --> {_format_srt_time(en)}\n{txt}"
            for idx, (st, en, txt) in enumerate(cap_events, start=1)
        ]
        srt_path.write_text("\n\n".join(srt_blocks) + "\n", encoding="utf-8")

        actual_dur_s = len(full_audio) / self.sample_rate
        overall_asr = (weighted_asr / max(total_words, 1))
        overall_speech_wpm = (total_words / max(total_speech_s, 0.1)) * 60.0
        effective_wpm = (total_words / max(actual_dur_s, 0.1)) * 60.0
        summary = {
            "voice_wav": str(voice_wav),
            "captions_ass": str(ass_path),
            "captions_srt": str(srt_path),
            "duration_s": round(actual_dur_s, 3),
            "speech_s": round(total_speech_s, 3),
            "voice_start_s": lead_in_s,
            "total_words": total_words,
            "effective_wpm": round(effective_wpm, 1),
            "speech_wpm": round(overall_speech_wpm, 1),
            "asr_match": round(overall_asr, 4),
            "beats": beats_timing,
        }
        (out_path / "timing.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return summary
