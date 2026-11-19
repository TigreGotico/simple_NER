"""
12_locale_system.py — locale system: load_rx, load_intents, load_wordlist, intent_to_regex
===========================================================================================
Goal: Demonstrate the locale utilities directly; write a custom .rx file and
      load it to match text.
Run:  python examples/12_locale_system.py
"""

import os
import re

# simple_NER locale utilities
from simple_NER.utils import load_rx, load_intents, load_wordlist, intent_to_regex


# ---------------------------------------------------------------------------
# 1.  intent_to_regex — convert a template string to a compiled regex
# ---------------------------------------------------------------------------

print("=== intent_to_regex ===")
templates = [
    "{amount} dollars",
    "send {amount} to {recipient}",
    "meeting on {date} at {time}",
]
for tmpl in templates:
    pattern = intent_to_regex(tmpl)
    print(f"  {tmpl!r:<40}  →  {pattern.pattern!r}")


# ---------------------------------------------------------------------------
# 2.  load_rx — load compiled patterns from a locale .rx file
# ---------------------------------------------------------------------------

print("\n=== load_rx (en-us/phone) ===")
try:
    patterns = load_rx("phone", "en-us")
    print(f"  Loaded {len(patterns)} pattern(s) from locale/en-us/phone.rx")
    sample = "+1-800-555-0199"
    matched = any(p.search(sample) for p in patterns)
    print(f"  Does {sample!r} match?  {matched}")
except FileNotFoundError as exc:
    print(f"  (skipped — {exc})")


# ---------------------------------------------------------------------------
# 3.  load_wordlist — load a plain wordlist
# ---------------------------------------------------------------------------

print("\n=== load_wordlist (en-us/currency) ===")
try:
    words = load_wordlist("currency", "en-us")
    print(f"  Loaded {len(words)} entries.  First 5: {words[:5]}")
except FileNotFoundError as exc:
    print(f"  (skipped — {exc})")


# ---------------------------------------------------------------------------
# 4.  load_intents — load intent templates and match text
# ---------------------------------------------------------------------------

print("\n=== load_intents (en-us/currency) ===")
try:
    intents = load_intents("currency", "en-us")
    print(f"  Loaded {len(intents)} intent pattern(s)")
    text = "I paid fifty dollars for lunch"
    for pattern in intents:
        m = pattern.search(text)
        if m:
            print(f"  Match on {text!r}: groups={m.groupdict()}")
            break
    else:
        print(f"  No match for {text!r}")
except FileNotFoundError as exc:
    print(f"  (skipped — {exc})")


# ---------------------------------------------------------------------------
# 5.  Custom .rx file: write, load, match
# ---------------------------------------------------------------------------

print("\n=== Custom locale file ===")

# Write a temporary locale file
TMP_DIR = os.path.join(os.path.dirname(__file__), "_tmp_locale", "en-us")
TMP_FILE = os.path.join(TMP_DIR, "order_id.rx")
os.makedirs(TMP_DIR, exist_ok=True)

ORDER_PATTERNS = [
    r"ORD-\d{6}",
    r"ORDER#\d{4,8}",
    r"PO-[A-Z]{2}\d{4}",
]
with open(TMP_FILE, "w") as fh:
    for p in ORDER_PATTERNS:
        fh.write(p + "\n")
print(f"  Wrote {TMP_FILE}")

# Load and compile
compiled: list[re.Pattern] = []
with open(TMP_FILE) as fh:
    for line in fh:
        line = line.strip()
        if line:
            compiled.append(re.compile(line))
print(f"  Loaded {len(compiled)} pattern(s)")

# Match
test_texts = [
    "Your order ORD-123456 has shipped.",
    "Reference: ORDER#9876 and PO-AB1234.",
    "No order ID in this line.",
]
for text in test_texts:
    matches = []
    for pat in compiled:
        for m in pat.finditer(text):
            matches.append(m.group(0))
    print(f"  {text!r:<45}  →  {matches}")

# Clean up temp file
os.remove(TMP_FILE)
os.rmdir(TMP_DIR)
os.rmdir(os.path.dirname(TMP_DIR))
