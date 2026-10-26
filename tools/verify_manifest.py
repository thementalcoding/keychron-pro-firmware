#!/usr/bin/env python3
"""Cross-check firmware/manifest.json, the published binaries and SHA256SUMS.

Usage:
    python3 tools/verify_manifest.py [--manifest firmware/manifest.json]

Exit code 0 only if every check passes:
  * every manifest entry points to an existing file (and no binary is unlisted)
  * size and SHA-256 match the file on disk
  * model folder, variant folder and keymap are consistent with the entry
  * totals match the actual number of entries
  * SHA256SUMS lists exactly those files with the same hashes
  * the tested flag is a boolean and at least the maintainer-tested image exists
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import re
import sys

SHA_RE = re.compile(r"^[0-9a-f]{64}$")


def sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=os.path.join("firmware", "manifest.json"))
    parser.add_argument("--sums", default="SHA256SUMS")
    args = parser.parse_args()

    if not os.path.exists(args.manifest):
        print(f"missing manifest: {args.manifest}", file=sys.stderr)
        return 1

    with open(args.manifest, encoding="utf-8") as handle:
        manifest = json.load(handle)

    errors: list[str] = []
    listed: dict[str, str] = {}
    variants = 0
    tested = 0

    for model in manifest.get("models", []):
        folder = model.get("model", "")
        if not os.path.isdir(os.path.join("firmware", folder)):
            errors.append(f"{folder}: model folder missing")
        for variant in model.get("variants", []):
            variants += 1
            path = variant.get("file", "")
            label = f"{folder}/{variant.get('folder', '?')}/{os.path.basename(path)}"
            if not path.startswith(f"firmware/{folder}/"):
                errors.append(f"{label}: file outside the model folder")
            if not os.path.exists(path):
                errors.append(f"{label}: file missing")
                continue
            listed[path] = variant.get("sha256", "")
            size = os.path.getsize(path)
            if size != variant.get("size"):
                errors.append(f"{label}: size {size} != manifest {variant.get('size')}")
            actual = sha256(path)
            if actual != variant.get("sha256"):
                errors.append(f"{label}: sha256 mismatch")
            if not SHA_RE.match(variant.get("sha256", "")):
                errors.append(f"{label}: malformed sha256")
            wanted_dir = os.path.join("firmware", folder, variant.get("folder", ""))
            if os.path.dirname(path) != wanted_dir:
                errors.append(f"{label}: path does not match model/variant folder")
            if not isinstance(variant.get("tested"), bool):
                errors.append(f"{label}: tested must be a boolean")
            elif variant["tested"]:
                tested += 1

    on_disk = {p.replace(os.sep, "/") for p in glob.glob("firmware/**/*.bin", recursive=True)}
    for extra in sorted(on_disk - set(listed)):
        errors.append(f"{extra}: binary not listed in the manifest")
    for missing in sorted(set(listed) - on_disk):
        errors.append(f"{missing}: listed but not on disk")

    totals = manifest.get("totals", {})
    expected = {
        "models": len(manifest.get("models", [])),
        "variants": variants,
        "tested": tested,
    }
    for key, value in expected.items():
        if totals.get(key) != value:
            errors.append(f"totals.{key}={totals.get(key)} != actual {value}")
    if tested < 1:
        errors.append("no image is marked as hardware-tested")

    sums: dict[str, str] = {}
    if not os.path.exists(args.sums):
        errors.append(f"missing {args.sums}")
    else:
        with open(args.sums, encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(maxsplit=1)
                if len(parts) != 2 or not SHA_RE.match(parts[0]):
                    errors.append(f"{args.sums}: malformed line: {line[:60]}")
                    continue
                sums[parts[1].lstrip("*")] = parts[0]
        for path, digest in sorted(listed.items()):
            if sums.get(path) != digest:
                errors.append(f"{args.sums}: missing or wrong hash for {path}")
        for path in sorted(set(sums) - set(listed)):
            errors.append(f"{args.sums}: unknown file {path}")

    if errors:
        print(f"FAIL: {len(errors)} problem(s)", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(
        "OK: {models} models, {variants} images, {tested} hardware-tested, "
        "checksums consistent".format(**expected)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
