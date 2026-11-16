"""valtec-tts (v-tts) probe: does TTS() download the pretrained weights?
Expected failure (from earlier API checks): HF repo v-tts/v-tts-pretrained is
private/gated (401). Capture the exact exception, do NOT authenticate.
"""
import traceback

try:
    from v_tts import TTS
    print("import v_tts OK", flush=True)
    tts = TTS()
    print("TTS() constructed OK — weights were found locally?!")
    print("speaker:", getattr(tts, "speaker", None))
except Exception:
    traceback.print_exc()
print("VALTEC_PROBE_DONE")
