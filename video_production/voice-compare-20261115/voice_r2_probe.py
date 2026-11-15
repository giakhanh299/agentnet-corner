"""Probe: does the installed transformers VitsModel.forward support length_scale?

Prints transformers version, VitsModel.forward signature, and the
VitsConfig length_scale default (if any). No synthesis, no downloads.
"""
import inspect
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import transformers
print(f"transformers version: {transformers.__version__}", flush=True)

from transformers import VitsModel, VitsConfig

sig = inspect.signature(VitsModel.forward)
print(f"VitsModel.forward params: {list(sig.parameters.keys())}", flush=True)
ls = sig.parameters.get("length_scale")
if ls is not None:
    print(f"length_scale param: default={ls.default}", flush=True)
    print("LENGTH_SCALE_SUPPORTED", flush=True)
else:
    print("LENGTH_SCALE_NOT_SUPPORTED", flush=True)

cfg = VitsConfig.from_pretrained("facebook/mms-tts-vie")
print(f"VitsConfig.length_scale = {getattr(cfg, 'length_scale', 'N/A')}", flush=True)
print("PROBE_DONE", flush=True)
