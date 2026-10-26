#!/usr/bin/env python3
"""Assemble the published firmware tree from a build report.

Reads builds_v1.0.0/build-status.json (produced by the build job), then writes:

    <out>/firmware/<model>/<variant>/<binary>.bin
    <out>/firmware/<model>/README.md
    <out>/firmware/manifest.json
    <out>/SHA256SUMS
    <out>/docs/tested-seed.json          (when --tested is given)
    <out>/README_MODELS.md               (markdown fragment for README.md)

Usage:
    python3 tools/gen_firmware_docs.py \
        --builds /path/to/builds_v1.0.0 \
        --qmk-root /path/to/firmware_qmk/wls_2025q1 \
        --out /path/to/public_release \
        --tested k13_pro/iso/rgb \
        --version 1.0.0 --build 2026-10-26c
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys

ORDER = [
    "k1_pro", "k2_pro", "k3_pro", "k4_pro", "k5_pro", "k6_pro", "k7_pro",
    "k8_pro", "k9_pro", "k10_pro", "k11_pro", "k12_pro", "k13_pro", "k14_pro",
    "k15_pro", "k17_pro", "q1_pro", "q2_pro", "q3_pro", "q4_pro", "q5_pro",
    "q6_pro", "q8_pro", "q10_pro", "q13_pro", "q14_pro",
]
BASELINE = {
    "upstream": "Keychron/qmk_firmware",
    "branch": "wls_2025q1",
    "commit": "c8b2b23",
}
REPO_URL = "https://github.com/thementalcoding/keychron-pro-firmware"
TESTED_NOTE = (
    "Flashed and used on one physical unit (maintainer). Bursts of repeated keys "
    "not yet confirmed fixed long-term; see README warnings."
)


def sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def find_keyboard_json(qmk_root: str, board: str, variant: str) -> str | None:
    base = os.path.join(qmk_root, "keyboards", "keychron", board)
    path = os.path.join(base, *variant.split("/"), "keyboard.json")
    if os.path.exists(path):
        return path
    # Variants sometimes inherit usb/pid from an ancestor directory.
    parts = variant.split("/")
    while parts:
        parts.pop()
        candidate = os.path.join(base, *parts, "keyboard.json") if parts else os.path.join(base, "keyboard.json")
        if os.path.exists(candidate):
            return candidate
    return None


def usb_pid(qmk_root: str, board: str, variant: str) -> str:
    path = find_keyboard_json(qmk_root, board, variant)
    if not path:
        return "?"
    data = read_json(path)
    pid = (data.get("usb") or {}).get("pid")
    if pid is None:
        return "?"
    if isinstance(pid, str):
        return pid if pid.startswith("0x") else f"0x{int(pid, 0):04X}"
    return f"0x{pid:04X}"


def display_name(qmk_root: str, board: str, variant: str) -> str:
    path = find_keyboard_json(qmk_root, board, variant)
    if path:
        data = read_json(path)
        name = data.get("keyboard_name")
        if name:
            return name
    return board.replace("_", " ").title()


def folder_of(variant: str) -> str:
    return variant.replace("/", "-")


def fold(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--builds", required=True)
    parser.add_argument("--qmk-root", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--version", default="1.0.0")
    parser.add_argument("--build", default="2026-10-26c")
    parser.add_argument("--tested", action="append", default=[],
                        help="variant target to mark as hardware-tested, e.g. k13_pro/iso/rgb")
    args = parser.parse_args()

    status = read_json(os.path.join(args.builds, "build-status.json"))
    entries = [item for item in status if item.get("status") == "ok"]
    failed = [item for item in status if item.get("status") != "ok"]
    if failed:
        print(f"warning: {len(failed)} failed build(s) in the report", file=sys.stderr)

    entries.sort(key=lambda item: (
        ORDER.index(item["board"]) if item["board"] in ORDER else 999,
        item["variant"],
    ))

    firmware_dir = os.path.join(args.out, "firmware")
    if os.path.isdir(firmware_dir):
        shutil.rmtree(firmware_dir)
    os.makedirs(firmware_dir, exist_ok=True)

    models: dict[str, dict] = {}
    sums: list[tuple[str, str]] = []
    tested_rows: list[dict] = []

    for item in entries:
        board, variant, keymap = item["board"], item["variant"], item.get("keymap", "default")
        source = os.path.join(args.builds, item["file"]) if not os.path.isabs(item["file"]) else item["file"]
        if not os.path.exists(source):
            print(f"missing build output: {source}", file=sys.stderr)
            return 1
        variant_folder = folder_of(variant)
        target_dir = os.path.join(firmware_dir, board, variant_folder)
        os.makedirs(target_dir, exist_ok=True)
        filename = os.path.basename(source)
        destination = os.path.join(target_dir, filename)
        shutil.copy2(source, destination)

        size = os.path.getsize(destination)
        digest = sha256(destination)
        relative = os.path.relpath(destination, args.out).replace(os.sep, "/")
        sums.append((digest, relative))

        pid = usb_pid(args.qmk_root, board, variant)
        name = display_name(args.qmk_root, board, variant)
        is_tested = variant in args.tested or f"{board}/{variant}" in args.tested
        record = {
            "variant": variant,
            "folder": variant_folder,
            "keymap": keymap,
            "pid": pid,
            "file": relative,
            "size": size,
            "sha256": digest,
            "tested": bool(is_tested),
            "tested_note": TESTED_NOTE if is_tested else None,
        }
        model = models.setdefault(board, {"model": board, "name": name, "variants": []})
        model["variants"].append(record)
        if is_tested:
            tested_rows.append({
                "model": board,
                "model_label": name.replace("Keychron ", ""),
                "variant": variant.replace("/", " ").upper(),
                "pid": pid,
                "firmware": filename,
                "sha256": digest,
                "host": "Linux 6.12 · Intel AX210",
                "date": "2026-10-26",
                "source": "maintainer",
            })

    ordered = [models[board] for board in ORDER if board in models]
    for board in models:
        if board not in ORDER:
            ordered.append(models[board])

    manifest = {
        "version": args.version,
        "build": args.build,
        "baseline": BASELINE,
        "totals": {
            "models": len(ordered),
            "variants": sum(len(model["variants"]) for model in ordered),
            "tested": sum(1 for model in ordered for variant in model["variants"] if variant["tested"]),
        },
        "models": ordered,
    }
    with open(os.path.join(firmware_dir, "manifest.json"), "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
        handle.write("\n")

    with open(os.path.join(args.out, "SHA256SUMS"), "w", encoding="utf-8") as handle:
        for digest, relative in sorted(sums, key=lambda pair: pair[1]):
            handle.write(f"{digest}  {relative}\n")

    for model in ordered:
        write_model_readme(firmware_dir, model, args.version, args.build)

    write_models_fragment(os.path.join(args.out, "README_MODELS.md"), ordered)

    if tested_rows:
        seed_path = os.path.join(args.out, "docs", "tested-seed.json")
        os.makedirs(os.path.dirname(seed_path), exist_ok=True)
        with open(seed_path, "w", encoding="utf-8") as handle:
            json.dump(tested_rows, handle, indent=2)
            handle.write("\n")

    print(
        "wrote {models} models, {variants} images, {tested} tested, {size:.1f} MiB".format(
            **manifest["totals"],
            size=sum(size for _, size in [(p, os.path.getsize(os.path.join(args.out, p))) for _, p in sums]) / 1048576,
        )
    )
    return 0


def write_model_readme(firmware_dir: str, model: dict, version: str, build: str) -> None:
    board = model["model"]
    name = model["name"]
    tested = [variant for variant in model["variants"] if variant["tested"]]
    rows = [
        "| Variant | Keymap | USB PID | File | Tested |",
        "|---|---|---|---|---|",
    ]
    for variant in model["variants"]:
        rows.append(
            "| {variant} | `{keymap}` | `{pid}` | [`{file}`]({folder}/{file}) | {tested} |".format(
                variant=variant["variant"],
                keymap=variant["keymap"],
                pid=variant["pid"],
                file=os.path.basename(variant["file"]),
                folder=variant["folder"],
                tested="✅ yes (1 unit)" if variant["tested"] else "⚠️ no",
            )
        )

    if tested:
        warning = (
            "> ✅ **Hardware-tested:** {n} variant(s) of this model were flashed on a "
            "physical unit. See [TESTED](https://github.com/thementalcoding/keychron-pro-firmware/blob/tested-index/TESTED.md).\n"
            "> The other variants of this model are **untested builds**."
        ).format(n=len(tested))
    else:
        warning = (
            "> ⚠️ **Untested on hardware.** This model compiles and passes all automated\n"
            "> checks (DFU suffix, CRC, size, manifest), but has not been flashed on a\n"
            "> device. Report your result with the\n"
            "> [hardware-test form](https://github.com/thementalcoding/keychron-pro-firmware/issues/new?template=hardware_test.yml)."
        )

    first = model["variants"][0]
    body = f"""# {name} — community QMK firmware

[← All models]({REPO_URL}/blob/main/README.md) · v{version} (build {build}) · GPL-2.0

Unofficial build for the **{name}** (STM32L432 + CKBT51 Bluetooth module), based on
Keychron `wls_2025q1` @ `c8b2b23`. Fixes Bluetooth link robustness and raises the
report rate to 133 Hz. Read the [main README]({REPO_URL}/blob/main/README.md) and the
[recovery guide]({REPO_URL}/blob/main/docs/RECOVERY.md) before flashing.

{warning}

## Images

{chr(10).join(rows)}

`_via` images keep VIA / Keychron Engine keymap support. `_default` images do not
speak VIA. Verify the download with `sha256sum -c SHA256SUMS` from the repository
root.

## Flash (Linux / macOS)

1. Back up your keymap (Keychron Engine or VIA JSON export).
2. Power **Off**, hold **Esc**, switch to **Cable** → `lsusb` shows `0483:df11`.
3. Flash:

```bash
sudo dfu-util -d 0483:df11 -a 0 -s 0x08000000:leave -D \\
  firmware/{board}/{first['folder']}/{os.path.basename(first['file'])}
```

Replace the path with the image for your PID. Windows: use QMK Toolbox.

## Identify your PID

| Variant | PID |
|---|---|
{chr(10).join(f"| {v['variant']} | `{v['pid']}` |" for v in model['variants'])}

If your PID is not listed, do not flash this model folder — open an issue.
"""
    with open(os.path.join(firmware_dir, board, "README.md"), "w", encoding="utf-8") as handle:
        handle.write(body)


def write_models_fragment(path: str, models: list[dict]) -> None:
    lines = [
        "| Model | Variants | USB PIDs | Images | Hardware-tested |",
        "|---|---|---|---|---|",
    ]
    for model in models:
        pids = sorted({variant["pid"] for variant in model["variants"] if variant["pid"] != "?"})
        tested = [variant for variant in model["variants"] if variant["tested"]]
        tested_text = (
            "✅ " + ", ".join(v["variant"].upper() for v in tested) if tested else "— (untested)"
        )
        lines.append(
            "| [{name}](firmware/{board}/README.md) | {n} | {pids} | {imgs} | {tested} |".format(
                name=model["name"].replace("Keychron ", ""),
                board=model["model"],
                n=len(model["variants"]),
                pids=", ".join(f"`{pid}`" for pid in pids) if pids else "—",
                imgs=len(model["variants"]),
                tested=tested_text,
            )
        )
    lines.append("")
    lines.append(
        "Every image is built from the same patched source. Only the rows marked ✅ "
        "have been flashed on hardware; the rest are untested builds."
    )
    lines.append("")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


if __name__ == "__main__":
    sys.exit(main())
