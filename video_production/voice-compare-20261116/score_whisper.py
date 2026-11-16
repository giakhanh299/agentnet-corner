"""Score Whisper transcripts against the 40-word test script.
Rules (same convention as rounds 1-2):
- lowercase, strip punctuation
- Whisper writes spoken numbers as digits: "500" counts as "năm trăm"
  (2 words) — a Whisper normalization artifact, not a TTS error.
- Everything else must match exactly ("số" != "sổ", "hốc" != "log").
Alignment via difflib SequenceMatcher on token lists.
"""
import difflib
import re

SCRIPT = ("Mỗi lần đăng nhập, bạn đang dùng mẹo của thủy thủ năm trăm năm trước? "
          "Thủy thủ viết tất cả vào sổ nhật ký của tàu, gọi là sổ log. "
          "Đăng nhập là ký tên vào sổ log của tàu.")

FILES = {
    "vieneu": "whisper_vieneu.txt",
    "vieneu_slow": "whisper_vieneu_slow.txt",
    "vietvoice": "whisper_vietvoice.txt",
    "mms_round2c_base": "whisper_mms_round2c_base.txt",
}


def norm(text):
    text = text.lower()
    text = re.sub(r"[,.?!;:]", " ", text)
    text = text.replace("500", "năm trăm")
    return text.split()


expected = norm(SCRIPT)
print(f"Script: {len(expected)} words")
for name, path in FILES.items():
    with open(path, encoding="utf-8") as f:
        heard = norm(f.read())
    sm = difflib.SequenceMatcher(a=expected, b=heard, autojunk=False)
    matched = sum(block.size for block in sm.get_matching_blocks())
    print(f"\n=== {name}: {matched}/{len(expected)} = {matched/len(expected)*100:.1f}% "
          f"(heard {len(heard)} tokens) ===")
    # list mismatches
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            print(f"  {tag}: expected {' '.join(expected[i1:i2]) or '(none)'} "
                  f"| heard {' '.join(heard[j1:j2]) or '(none)'}")
