#!/usr/bin/env python3
"""Whisper check with whisper.cpp Base (same method for every voice in this round).
Usage: whisper_check.py <wav16k> <label>
Compares heard text vs the 40-word test script using difflib token matching
(same approach as the v003 TTS self-check).
"""
import difflib
import re
import subprocess
import sys
import os

WHISPER = "/home/hatch/workspace/agentnet-corner/whisper.cpp/build/bin/whisper-cli"
MODEL = "/home/hatch/workspace/agentnet-corner/whisper.cpp/models/ggml-base.bin"

EXPECTED = ("Mỗi lần đăng nhập, bạn đang dùng mẹo của thủy thủ năm trăm năm trước? "
            "Thủy thủ viết tất cả vào sổ nhật ký của tàu, gọi là sổ log. "
            "Đăng nhập là ký tên vào sổ log của tàu.")

def tokens(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return text.split()

def main():
    wav, label = sys.argv[1], sys.argv[2]
    out_base = f"/tmp/whisper_{label}"
    r = subprocess.run([WHISPER, "-m", MODEL, "-f", wav, "-l", "vi",
                        "--output-txt", "--output-file", out_base, "-t", "2"],
                       capture_output=True, text=True)
    txt_path = out_base + ".txt"
    heard = open(txt_path, encoding="utf-8").read().strip() if os.path.exists(txt_path) else ""
    # strip whisper [xx:xx:xx.xxx --> ...] timestamps if present
    heard = re.sub(r"\[\d\d:\d\d:\d\d\.\d+ --> \d\d:\d\d:\d\d\.\d+\]\s*", " ", heard)
    heard = re.sub(r"\s+", " ", heard).strip()
    E, H = tokens(EXPECTED), tokens(heard)
    sm = difflib.SequenceMatcher(a=E, b=H, autojunk=False)
    matched = sum(b.size for b in sm.get_matching_blocks())
    matched_idx = set()
    for b in sm.get_matching_blocks():
        matched_idx.update(range(b.a, b.a + b.size))
    missed = [E[i] for i in range(len(E)) if i not in matched_idx]
    print(f"[{label}] Expected ({len(E)} words): {EXPECTED}")
    print(f"[{label}] Heard    ({len(H)} words): {heard}")
    print(f"[{label}] Whisper (whisper.cpp Base, -l vi): {matched}/{len(E)} = {matched/len(E)*100:.1f}%")
    print(f"[{label}] Missed/misheard: {missed}")
    with open(f"/tmp/whisper_{label}.result.txt", "w", encoding="utf-8") as f:
        f.write(f"heard: {heard}\nmatch: {matched}/{len(E)} = {matched/len(E)*100:.1f}%\nmissed: {missed}\n")

if __name__ == "__main__":
    main()
