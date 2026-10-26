#!/usr/bin/env python3
"""Fail if personal data leaked into the published tree.

This repository is published from a private workstation: MAC addresses,
hostname, user paths and LAN/tunnel addresses must never appear in it.
Patterns are split so that this file does not match itself.

Usage: python3 tools/check_sanitization.py
"""
import os
import re
import sys

# Assembled at runtime so the checker never flags its own source.
PATTERNS = [
    "6c:93" + ":08:66",
    "70:cd" + ":0d:45",
    "d8:bb" + ":c1",
    "kody" + "system",
    "/" + "home/" + "kody",
    "192" + ".168.",
    "100" + ".97.",
    "fd7a" + ":115c",
    "enp38s0",
]

SKIP_DIRS = {".git"}
SKIP_FILES = {os.path.abspath(__file__)}


def main() -> int:
    hits = []
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            path = os.path.join(root, name)
            if os.path.abspath(path) in SKIP_FILES:
                continue
            try:
                with open(path, "rb") as fh:
                    blob = fh.read()
            except OSError:
                continue
            if b"\0" in blob[:4096]:  # binary file (firmware), no PII expected
                continue
            text = blob.decode("utf-8", "ignore").lower()
            for pattern in PATTERNS:
                if pattern in text:
                    hits.append(f"{path}: {pattern}")
    if hits:
        print("personal data found:")
        print("\n".join(hits))
        return 1
    print(f"sanitization OK ({len(PATTERNS)} patterns, 0 hits)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
