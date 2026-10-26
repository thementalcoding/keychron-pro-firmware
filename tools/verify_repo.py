#!/usr/bin/env python3
"""Consistency checks for the generated documentation tree.

Verifies that human-facing docs agree with firmware/manifest.json:

  * README.md / README.es.md list all 26 models with links to existing model READMEs
  * tested markers match the manifest (✅ only where tested=true)
  * each model README lists every variant, PID and binary of its manifest entry
  * untested models carry the "Untested on hardware" warning
  * docs/tested-seed.json points at real files with matching hashes
  * relative Markdown links in README, docs/, AGENTS.md and llms.txt resolve
  * SHA256SUMS only contains firmware/ paths and no duplicates

Usage:
    python3 tools/verify_repo.py
Exit code 0 only if every check passes.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

MODEL_LINK = re.compile(r"\]\(firmware/([a-z0-9_]+)/README\.md\)")
LINK = re.compile(r"\[[^\]]*\]\(\s*<?([^)>\s]+)>?(?:\s+\"[^\"]*\")?\s*\)")
SKIP = ("http://", "https://", "mailto:", "#", "tel:")


def load(path: str):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def check_links(path: str, errors: list[str]) -> int:
    base = os.path.dirname(path)
    checked = 0
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    for raw in LINK.findall(text):
        target = raw.split("#", 1)[0].split("?", 1)[0].strip()
        if not target or target.startswith(SKIP) or target.startswith("/"):
            continue
        resolved = os.path.normpath(os.path.join(base, target))
        checked += 1
        if not os.path.exists(resolved):
            errors.append(f"{path}: broken link -> {raw}")
    return checked


def main() -> int:
    manifest_path = os.path.join("firmware", "manifest.json")
    if not os.path.exists(manifest_path):
        print("missing firmware/manifest.json", file=sys.stderr)
        return 1
    manifest = load(manifest_path)
    models = {entry["model"]: entry for entry in manifest.get("models", [])}
    errors: list[str] = []

    # 1. Main READMEs: every model linked exactly once, tested marker consistent.
    for readme in ("README.md", "README.es.md"):
        if not os.path.exists(readme):
            errors.append(f"{readme}: missing")
            continue
        with open(readme, encoding="utf-8") as handle:
            text = handle.read()
        linked = MODEL_LINK.findall(text)
        for model in models:
            count = linked.count(model)
            if count != 1:
                errors.append(f"{readme}: model {model} linked {count} times (expected 1)")
        rows = [line for line in text.splitlines() if "](firmware/" in line and "/README.md)" in line]
        for line in rows:
            match = MODEL_LINK.search(line)
            if not match:
                continue
            entry = models.get(match.group(1))
            if not entry:
                errors.append(f"{readme}: table row for unknown model {match.group(1)}")
                continue
            has_tested = any(variant.get("tested") for variant in entry["variants"])
            marked = "✅" in line
            if has_tested and not marked:
                errors.append(f"{readme}: {entry['model']} has tested images but no ✅ marker")
            if not has_tested and marked:
                errors.append(f"{readme}: {entry['model']} is untested but marked ✅")

    # 2. Per-model READMEs.
    for name, entry in models.items():
        readme = os.path.join("firmware", name, "README.md")
        if not os.path.exists(readme):
            errors.append(f"{readme}: missing")
            continue
        with open(readme, encoding="utf-8") as handle:
            text = handle.read()
        has_tested = any(variant.get("tested") for variant in entry["variants"])
        if has_tested and "Hardware-tested" not in text:
            errors.append(f"{readme}: tested model without hardware-tested banner")
        if not has_tested and "Untested on hardware" not in text:
            errors.append(f"{readme}: untested model without warning")
        for variant in entry["variants"]:
            for needle in (variant["variant"], variant["pid"], os.path.basename(variant["file"])):
                if needle not in text:
                    errors.append(f"{readme}: missing {needle!r}")

    # 3. Tested seed.
    seed_path = os.path.join("docs", "tested-seed.json")
    if os.path.exists(seed_path):
        for row in load(seed_path):
            model = row.get("model")
            entry = models.get(model)
            if not entry:
                errors.append(f"{seed_path}: unknown model {model}")
                continue
            match = [
                variant for variant in entry["variants"]
                if variant["variant"] == row.get("variant").replace(" ", "/").lower()
                or variant["variant"].replace("/", " ").lower() == str(row.get("variant")).lower()
            ]
            if not match:
                errors.append(f"{seed_path}: variant {row.get('variant')!r} not in {model}")
                continue
            variant = match[0]
            if row.get("sha256") != variant["sha256"]:
                errors.append(f"{seed_path}: sha256 mismatch for {model} {variant['variant']}")
            if row.get("firmware") and row["firmware"] != os.path.basename(variant["file"]):
                errors.append(f"{seed_path}: firmware name mismatch for {model}")

    # 4. Relative links.
    link_files = ["README.md", "README.es.md", "AGENTS.md", "llms.txt"]
    link_files += sorted(glob.glob("docs/*.md"))
    checked = 0
    for path in link_files:
        if os.path.exists(path):
            checked += check_links(path, errors)

    # 5. SHA256SUMS paths.
    if os.path.exists("SHA256SUMS"):
        seen = set()
        with open("SHA256SUMS", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(maxsplit=1)
                if len(parts) != 2:
                    errors.append("SHA256SUMS: malformed line")
                    continue
                path = parts[1].lstrip("*")
                if not path.startswith("firmware/"):
                    errors.append(f"SHA256SUMS: path outside firmware/: {path}")
                if path in seen:
                    errors.append(f"SHA256SUMS: duplicate {path}")
                seen.add(path)
    else:
        errors.append("SHA256SUMS: missing")

    if errors:
        print(f"FAIL: {len(errors)} problem(s)", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(
        "OK: {models} model READMEs, {variants} variants, {links} links checked".format(
            models=len(models),
            variants=sum(len(entry["variants"]) for entry in models.values()),
            links=checked,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
