# Data formats and contracts

Everything here is consumed by code (CI, workflows, tools). Change a shape and you
must update `tools/verify_manifest.py`, `tools/gen_firmware_docs.py`,
`tools/hardware_tests.py` and the workflows together.

## 1. Path conventions

```
firmware/<model>/<variant-folder>/<keyboard>_<model>_<variant>_<keymap>.bin
firmware/<model>/README.md
firmware/manifest.json
SHA256SUMS                      (repo root, paths relative to root)
```

- `<model>`: upstream folder name, lowercase, e.g. `k13_pro`, `q6_pro`.
- `<variant-folder>`: upstream variant path with `/` → `-`, e.g. `iso/rgb` →
  `iso-rgb`.
- Domain separator: `k13_pro/iso-rgb`, `q1_pro/ansi-knob`.
- The binary name is the QMK output name and must not be renamed.

## 2. `firmware/manifest.json`

```json
{
  "version": "1.0.0",
  "build": "2026-10-26c",
  "baseline": {
    "upstream": "Keychron/qmk_firmware",
    "branch": "wls_2025q1",
    "commit": "c8b2b23"
  },
  "totals": { "models": 26, "variants": 95, "tested": 1 },
  "models": [
    {
      "model": "k13_pro",
      "name": "Keychron K13 Pro",
      "variants": [
        {
          "variant": "iso/rgb",
          "folder": "iso-rgb",
          "keymap": "via",
          "pid": "0x02D1",
          "file": "firmware/k13_pro/iso-rgb/keychron_k13_pro_iso_rgb_via.bin",
          "size": 62968,
          "sha256": "<64 hex>",
          "tested": true,
          "tested_note": "one physical unit, maintainer"
        }
      ]
    }
  ]
}
```

Invariants enforced by `tools/verify_manifest.py`:

- `file` starts with `firmware/<model>/<folder>/` and exists on disk;
- `size` and `sha256` match the file; hash is 64 lowercase hex;
- no `.bin` under `firmware/` that is not listed, and no listed file missing;
- `totals` equals the actual model/variant/tested counts;
- `totals.tested >= 1`;
- every path has an entry in `SHA256SUMS` with the same hash, and no extra rows.

`tested: true` requires a physical unit; the only allowed source of truth is
`docs/tested-seed.json` (maintainer) or an issue labelled `tested-ok`.

## 3. `builds_v1.0.0/build-status.json` (build input, not published)

Array of build records produced by the build job:

```json
[
  {
    "board": "k13_pro",
    "variant": "iso/rgb",
    "keymap": "via",
    "target": "keychron/k13_pro/iso/rgb",
    "file": "k13_pro/iso-rgb/keychron_k13_pro_iso_rgb_via.bin",
    "size": 62968,
    "sha256": "<64 hex>",
    "status": "ok",
    "error": null
  }
]
```

`file` is relative to the build directory. `status` is `ok` or `fail`; failed
records carry `error`. `gen_firmware_docs.py` refuses to assemble a missing file.

## 4. `docs/tested-seed.json` (maintainer unit tests)

Array of already-verified reports merged into the index:

```json
[
  {
    "model": "k13_pro",
    "model_label": "K13 Pro",
    "variant": "ISO RGB",
    "pid": "3434:02d1",
    "firmware": "keychron_k13_pro_iso_rgb_via.bin",
    "sha256": "<64 hex>",
    "host": "Linux 6.12 · Intel AX210",
    "date": "2026-10-26",
    "source": "maintainer"
  }
]
```

`sha256` must equal the manifest entry for that model/variant; otherwise the seed
is wrong (a new build requires updating the seed).

## 5. `tested-index` branch output

`TESTED.md` — generated table (do not edit), plus:

`docs/tested.json` — shields.io endpoint badge:

```json
{
  "schemaVersion": 1,
  "label": "hardware tested",
  "message": "1 report · 1 model",
  "color": "brightgreen"
}
```

The README reads it from
`https://raw.githubusercontent.com/thementalcoding/keychron-pro-firmware/tested-index/docs/tested.json`.

## 6. Issue form ↔ parser contract

`tools/hardware_tests.py` parses the issue body by `### <label>` headings. These
labels are the contract (renaming one silently breaks counting):

| Heading (exact) | Used for |
|---|---|
| `Model` | dropdown; must match a key in `MODELS` |
| `Variant / layout` | free text, required for counting |
| `USB PID (optional)` | informational |
| `Firmware file` | basename shown in the index |
| `Firmware SHA-256` | 64-hex; **required** for counting |
| `Result` | `Works…` → `tested-ok`; `Problems…` → `tested-problem` |
| `Tested over` | informational |
| `Host OS and Bluetooth adapter` | shown in the index |
| `Notes` | human reading |
| `How long have you been using it?` | human reading |

Labels: `hardware-test` (all reports), `tested-ok`, `tested-problem`.
A report with an unknown model, empty variant or invalid SHA is ignored by the
index (still visible as an issue).

## 7. `SHA256SUMS`

GNU format, two spaces, sorted by path:

```
<64 hex>  firmware/k13_pro/iso-rgb/keychron_k13_pro_iso_rgb_via.bin
```

Validated from the repository root with `sha256sum -c SHA256SUMS`.

## 8. DFU binary format

- STM32L432 flash image ≤ 256 KiB.
- 16-byte DFU 1.1a suffix: `bcdDevice`, `idProduct = 0xDF11`,
  `idVendor = 0x0483`, `bcdDFU = 0x0100` (raw DFU, **not** DfuSe `0x011A`),
  `"UFD"`, `bLength = 0x10`, CRC = `~crc32(image + first 12 suffix bytes)`.
- `tools/verify_bins.py` enforces all of the above.

## 9. Repository files written by automation

| Path | Producer | Committed by |
|---|---|---|
| `firmware/**` | `tools/gen_firmware_docs.py` | maintainer/agent, then reviewed |
| `SHA256SUMS` | same | same |
| `firmware/manifest.json` | same | same |
| `docs/tested-seed.json` | same (`--tested`) | same |
| `TESTED.md`, `docs/tested.json` | `tools/hardware_tests.py index` | `tested-index` branch only |
| labels on issues | workflow + `hardware_tests.py label` | n/a |
