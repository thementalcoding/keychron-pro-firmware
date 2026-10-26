#!/usr/bin/env python3
"""Build reproducible release assets from firmware/manifest.json.

Creates, in --out:

    keychron-<model>-v<version>.zip     one standalone ZIP per model:
                                        README.md + SHA256SUMS + firmware/<model>/...
    keychron-pro-firmware-v<version>-full.zip
                                        the complete published tree

The model ZIPs are self-contained: extracting one and running
``sha256sum -c SHA256SUMS`` verifies every binary. Entries are written in a
stable order with fixed timestamps so the same tree produces the same ZIP.

Usage:
    python3 tools/make_release_assets.py --out /tmp/rel --version 1.0.0
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

REPO_URL = "https://github.com/thementalcoding/keychron-pro-firmware"
FIXED_DATE = (2026, 10, 26, 0, 0, 0)
FULL_TOP_FILES = [
    "README.md",
    "README.es.md",
    "AGENTS.md",
    "llms.txt",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "LICENSE",
    "SHA256SUMS",
]
FULL_DIRS = ["docs", "firmware", "patches", "tools"]
SKIP_DIRS = {".git", ".github", "__pycache__"}


def sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def zip_info(arcname: str, mode: int) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(arcname, date_time=FIXED_DATE)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (mode & 0xFFFF) << 16
    info.create_system = 3
    return info


def write_zip(path: str, entries: list[tuple[str, bytes, int]]) -> None:
    entries.sort(key=lambda item: item[0])
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for arcname, data, mode in entries:
            archive.writestr(zip_info(arcname, mode), data)


def file_entry(root: str, relative: str, arcname: str) -> tuple[str, bytes, int]:
    source = os.path.join(root, relative)
    mode = 0o755 if os.access(source, os.X_OK) else 0o644
    with open(source, "rb") as handle:
        return arcname, handle.read(), mode


def model_readme(model: dict, version: str, build: str) -> bytes:
    name = model["name"]
    variants = model["variants"]
    tested = [variant for variant in variants if variant.get("tested")]
    first = variants[0]
    first_file = os.path.basename(first["file"])

    if tested:
        labels = ", ".join(variant["variant"].upper() for variant in tested)
        status = (
            f"> ✅ **Tested on hardware:** {labels} on one physical unit.\n"
            "> All other variants in this ZIP are **untested builds**."
        )
    else:
        status = (
            "> ⚠️ **Untested on hardware.** This model compiles and passes the\n"
            "> automated DFU/CRC/size/manifest checks, but has not been flashed on a\n"
            "> device. Report your result through the hardware-test form."
        )

    rows = [
        "| Variant | Keymap | USB PID | File | Tested |",
        "|---|---|---|---|---|",
    ]
    for variant in variants:
        rows.append(
            "| {variant} | `{keymap}` | `{pid}` | `{file}` | {tested} |".format(
                variant=variant["variant"],
                keymap=variant["keymap"],
                pid=variant["pid"],
                file=os.path.basename(variant["file"]),
                tested="✅ yes (1 unit)" if variant.get("tested") else "⚠️ no",
            )
        )

    body = f"""# {name} — community QMK firmware

v{version} (build {build}) · GPL-2.0 · unofficial build

Firmware for the **{name}** (STM32L432 + CKBT51 module), built from the patched
Keychron `wls_2025q1` tree. This ZIP is standalone: everything needed to verify
and flash the model is inside.

- Documentation: {REPO_URL}/blob/main/README.md
- Recovery guide: {REPO_URL}/blob/main/docs/RECOVERY.md
- Hardware-test form: {REPO_URL}/issues/new?template=hardware_test.yml

{status}

## Images

{chr(10).join(rows)}

## Verify

```bash
cd <extracted folder>
sha256sum -c SHA256SUMS
```

Every line in `SHA256SUMS` must end in `OK` before flashing.

## Flash (Linux / macOS)

1. Back up your keymap (Keychron Engine or VIA JSON export).
2. Power **Off**, hold **Esc**, switch to **Cable** → `lsusb` shows `0483:df11`.
3. Flash the image matching your PID:

```bash
sudo dfu-util -d 0483:df11 -a 0 -s 0x08000000:leave -D \\
  {os.path.dirname(first['file'])}/{first_file}
```

Replace the path with the variant for your PID. Windows: use QMK Toolbox and the
same `.bin`. A brick is practically impossible: the STM32 ROM bootloader cannot
be overwritten, so DFU can always be re-entered.
"""
    return body.encode("utf-8")


def sums_text(model: dict) -> bytes:
    lines = [
        f"{variant['sha256']}  {variant['file']}\n"
        for variant in sorted(model["variants"], key=lambda item: item["file"])
    ]
    return "".join(lines).encode("utf-8")


def build_model_zip(root: str, out_dir: str, model: dict, version: str, build: str) -> str:
    board = model["model"]
    entries: list[tuple[str, bytes, int]] = []
    entries.append(("README.md", model_readme(model, version, build), 0o644))
    entries.append(("SHA256SUMS", sums_text(model), 0o644))
    entries.append(
        (
            f"firmware/{board}/README.md",
            *_read_model_readme(root, board),
        )
    )
    for variant in model["variants"]:
        entries.append(file_entry(root, variant["file"], variant["file"]))

    name = f"keychron-{board}-v{version}.zip"
    target = os.path.join(out_dir, name)
    write_zip(target, entries)
    return target


def _read_model_readme(root: str, board: str) -> tuple[bytes, int]:
    path = os.path.join(root, "firmware", board, "README.md")
    with open(path, "rb") as handle:
        return handle.read(), 0o644


def collect_tree(root: str, relative_dir: str) -> list[tuple[str, bytes, int]]:
    entries: list[tuple[str, bytes, int]] = []
    for current, dirs, files in os.walk(os.path.join(root, relative_dir)):
        dirs[:] = sorted(name for name in dirs if name not in SKIP_DIRS)
        for name in sorted(files):
            if name.endswith((".pyc", ".pyo")):
                continue
            source = os.path.join(current, name)
            relative = os.path.relpath(source, root).replace(os.sep, "/")
            entries.append(file_entry(root, relative, relative))
    return entries


def build_full_zip(root: str, out_dir: str, version: str) -> str:
    entries: list[tuple[str, bytes, int]] = []
    for name in FULL_TOP_FILES:
        if os.path.exists(os.path.join(root, name)):
            entries.append(file_entry(root, name, name))
    for directory in FULL_DIRS:
        if os.path.isdir(os.path.join(root, directory)):
            entries.extend(collect_tree(root, directory))

    target = os.path.join(out_dir, f"keychron-pro-firmware-v{version}-full.zip")
    write_zip(target, entries)
    return target


def validate_model_zip(zip_path: str, model: dict) -> list[str]:
    problems: list[str] = []
    with tempfile.TemporaryDirectory(prefix="release-check-") as temporary:
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(temporary)
        try:
            result = subprocess.run(
                ["sha256sum", "-c", "SHA256SUMS"],
                cwd=temporary,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                problems.append(f"{zip_path}: sha256sum -c failed: {result.stdout}{result.stderr}")
        except FileNotFoundError:
            # Fallback when sha256sum is unavailable (non-Linux hosts).
            with open(os.path.join(temporary, "SHA256SUMS"), encoding="utf-8") as handle:
                for line in handle:
                    digest, relative = line.strip().split("  ", 1)
                    candidate = os.path.join(temporary, relative)
                    if sha256_file(candidate) != digest:
                        problems.append(f"{zip_path}: hash mismatch for {relative}")
        for variant in model["variants"]:
            if not os.path.exists(os.path.join(temporary, variant["file"])):
                problems.append(f"{zip_path}: missing {variant['file']}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, help="output directory for the ZIPs")
    parser.add_argument("--version", default=None, help="release version (defaults to manifest)")
    parser.add_argument("--root", default=".", help="repository root")
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    manifest_path = os.path.join(root, "firmware", "manifest.json")
    if not os.path.exists(manifest_path):
        print(f"missing {manifest_path}", file=sys.stderr)
        return 1
    manifest = read_json(manifest_path)
    version = args.version or str(manifest["version"])
    build = str(manifest.get("build", ""))

    os.makedirs(args.out, exist_ok=True)
    out_dir = os.path.abspath(args.out)

    produced: list[str] = []
    problems: list[str] = []
    for model in manifest["models"]:
        zip_path = build_model_zip(root, out_dir, model, version, build)
        produced.append(zip_path)
        problems.extend(validate_model_zip(zip_path, model))

    full_path = build_full_zip(root, out_dir, version)
    produced.append(full_path)

    print(f"{len(produced)} asset(s) in {out_dir}:")
    for path in produced:
        print(f"  {os.path.basename(path):<52} {os.path.getsize(path):>10} bytes")

    if problems:
        print(f"\nFAIL: {len(problems)} problem(s)", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    print(
        "\nOK: {models} standalone model ZIPs validated, full ZIP written".format(
            models=len(manifest["models"])
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
