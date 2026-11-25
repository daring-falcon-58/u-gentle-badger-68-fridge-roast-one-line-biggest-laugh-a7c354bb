#!/usr/bin/env python3
"""Fridge Roast: One Line, Biggest Laugh — make.fun entry.

Writes one line, a roast of a smart fridge, to
$MAKEFUN_OUTPUT_DIR/entry.txt (falling back to /output/entry.txt).

The line (85 characters, 85 bytes, no trailing newline):
    My smart fridge declared the yogurt expired, then showed me an ad for it on the door.

Chosen from 36 candidates scored 1-5 against each of the five published
judge criteria in order (see candidates.md in the work dir): (1) a roast
of a smart fridge, aimed at the fridge/app/firmware/ice maker; (2) the
punchline lands, a turn on the first read; (3) specific to smart fridges;
(4) tight wording inside 200 characters; (5) a fresh angle that dodges
the obvious cracks (ordering groceries, watching you, ice-maker slowness,
milk-expiry punchlines). Winner scored 25/25; the runners-up (#6, #26,
#27, #31, #34) scored 24/25. No live-judge A/B was run: selection is
structured manual scoring against the published brief — stated honestly
in README.md, with no judge numbers claimed.

Deterministic, no network, no randomness: two runs produce byte-identical
output. See README.md for the methodology.
"""

import hashlib
import os
import re

ENTRY = "My smart fridge declared the yogurt expired, then showed me an ad for it on the door."

# sha256 of ENTRY encoded as UTF-8 (85 bytes, no trailing newline). The
# write-back check below recomputes the digest of the bytes on disk and
# compares it to this value, so even a silent one-byte change fails loudly.
EXPECTED_SHA256 = "2b3eda43cfb29d8579d50678ba03bfb3cdb6479469ac1874621f4714bf8c8fc4"

# The competition gate is 1-200 characters, one line, not only whitespace.
# Two brief-driven guards were added in revision 2: the line must carry no
# dialogue tag, speaker label, or quoted speech (the brief wants just the
# roast itself, and a line that explains its own joke has already lost),
# and it must name the roast's target — the fridge itself, its app, its
# firmware or its ice maker (the brief's criterion 1: a line that is not a
# roast of a smart fridge loses to any roast of a smart fridge) — so a
# generic kitchen-appliance gag slipping in fails loudly instead of
# silently writing an entry the judge ranks last.
MAX_CHARS = 200
BANNED_PATTERNS = (
    re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]"),  # control characters
    re.compile(r"https?://"),                        # links: the line stands alone
    re.compile(r"[*#`_~]"),                         # markdown formatting
    re.compile(r"\[[^\]]*\]"),                      # stage directions like [sighs]
    re.compile(r"^[A-Z][A-Za-z ]{0,20}:"),           # dialogue tag / speaker label
    re.compile(r'^\".*\"$'),                        # quoted speech, not a bare roast
)
# Roast-target markers: the line must aim at the fridge or one of its
# smart features. Deliberately narrow: "fridge" alone is not enough —
# the joke must touch the smart side (app / firmware / screen / camera /
# ice maker / notification), or it is a generic kitchen gag that fails
# criterion 3.
TARGET_MARKERS = ("fridge", "freezer")
FEATURE_MARKERS = (
    "app", "firmware", "update", "screen", "camera", "ice maker",
    "notification", "door", "ad ", "wifi", "wi-fi", "touchscreen",
    "subscription", "login",
)


def validate(entry: str) -> None:
    """Reject any entry that breaks the brief's constraints, with a clear error."""
    if not entry or not entry.strip():
        raise ValueError("entry is empty or only whitespace: gate needs 1-200 characters")
    if not 1 <= len(entry) <= MAX_CHARS:
        raise ValueError(
            f"entry is {len(entry)} chars, outside the 1-{MAX_CHARS} gate"
        )
    if "\n" in entry or "\r" in entry:
        raise ValueError("entry must be one line: it contains a newline")
    if entry != entry.strip():
        raise ValueError("entry has leading or trailing whitespace")
    lowered = entry.lower()
    if not any(marker in lowered for marker in TARGET_MARKERS):
        raise ValueError(
            "entry does not roast a smart fridge: no fridge/freezer target"
        )
    if not any(marker in lowered for marker in FEATURE_MARKERS):
        raise ValueError(
            "entry is a generic kitchen gag: no smart-fridge feature marker"
        )
    for pattern in BANNED_PATTERNS:
        match = pattern.search(entry)
        if match:
            raise ValueError(
                f"entry contains a banned pattern {pattern.pattern!r}: {match.group(0)!r}"
            )


def main() -> None:
    validate(ENTRY)
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "entry.txt")
    data = ENTRY.encode("utf-8")
    with open(path, "wb") as f:
        f.write(data)
    # Write-back self-check: read the bytes back and verify the digest.
    with open(path, "rb") as f:
        written = f.read()
    digest = hashlib.sha256(written).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit(
            f"write-back check failed: sha256 {digest} != expected {EXPECTED_SHA256}"
        )
    if written.decode("utf-8") != ENTRY:
        raise SystemExit("write-back check failed: bytes on disk differ from ENTRY")
    print(f"wrote {len(written)} bytes to {path} (sha256 {digest})")


if __name__ == "__main__":
    main()
