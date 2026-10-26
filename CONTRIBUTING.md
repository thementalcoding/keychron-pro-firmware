# Contributing

Thanks for helping improve the Keychron Pro wireless firmware. This repository
publishes patched QMK builds for 26 CKBT51 keyboards plus the audit and tooling;
the authoritative source is the patch series in `patches/`, applied on top of
Keychron's `wls_2025q1` branch.

## Building

Requirements:

- QMK CLI (Python 3.10+)
- `arm-none-eabi-gcc` 12/13/14
- clang-format **19.x** (CI parity; this tree is formatted with 19.1.7)

```bash
git clone https://github.com/thementalcoding/qmk_firmware.git
cd qmk_firmware && git checkout k13-pro-bt-fixes
qmk compile -kb keychron/k13_pro/iso/rgb -km via
```

The Build (QMK) workflow re-applies `patches/k13-audit.patch` on Keychron's tree
at the pinned base commit and compiles the ISO RGB `via` variant inside the
`ghcr.io/qmk/qmk_cli` container, so a green build job means the patch still
applies cleanly upstream.

## Test matrix

Every firmware change must build **all 26 models / 95 variants** before a
release. During development, at minimum:

| Board | Variants |
|---|---|
| `keychron/k13_pro` | all four (`ansi/rgb`, `ansi/white`, `iso/rgb`, `iso/white`) |
| `keychron/k14_pro` | `ansi/rgb` (shared-code spot check) |
| `keychron/q1_pro` | any variant (HC595 common matrix spot check) |

The release build enumerates every variant with
`qmk list-keyboards | grep '^keychron/<board>/'` and compiles it with the `via`
keymap where one exists, otherwise `default`.

Hardware results are tracked with the `hardware-test` / `tested-ok` labels —
please file a [hardware test report](https://github.com/thementalcoding/keychron-pro-firmware/issues/new?template=hardware_test.yml)
instead of adding a note to a PR.

## Measuring the report rate

```bash
sudo python3 tools/medir_polling.py -m tap -t 10
```

Tap a single key ~200 times, compare Bluetooth against USB, and report the
minimum inter-report gap (expected floor ~5 ms at 133 Hz, ~7 ms at stock 90 Hz).
Include before/after numbers in the PR.

## Rebuilding published binaries

```bash
# 1. build every variant into builds_v1.0.0/ (see the tester role / build-status.json)
# 2. assemble firmware/, per-model READMEs, manifest.json and SHA256SUMS
python3 tools/gen_firmware_docs.py \
  --builds /path/to/builds_v1.0.0 \
  --qmk-root /path/to/qmk_firmware \
  --out . \
  --tested k13_pro/iso/rgb \
  --version 1.0.0 --build 2026-10-26c

# 3. verify
python3 tools/verify_bins.py
python3 tools/verify_manifest.py
sha256sum -c SHA256SUMS
```

## Pull request checklist

- [ ] Builds pass for the full matrix (95 variants for a release).
- [ ] `tools/verify_bins.py`, `tools/verify_manifest.py` and
      `sha256sum -c SHA256SUMS` pass.
- [ ] `firmware/`, `firmware/manifest.json` and root `SHA256SUMS` regenerated
      together if firmware changed.
- [ ] Tap-test before/after numbers included.
- [ ] No personal data anywhere (MAC addresses, serial numbers, hostnames, user
      paths, LAN or tunnel IPs); the CI privacy guard
      (`tools/check_sanitization.py`) must stay green.
- [ ] README (both languages) and docs updated for user-visible changes.
- [ ] Contribution accepted under GPL-2.0 (inbound = outbound).

## Style

- Keep diffs minimal and focused; do not reformat unrelated code.
- Follow upstream QMK style; the tree is checked with clang-format 19.x.

## Proposing MCU firmware changes

1. Modify the source in your QMK checkout (branch `k13-pro-bt-fixes`).
2. Rebuild the affected variants and regenerate `firmware/`,
   `firmware/manifest.json` and `SHA256SUMS`.
3. Regenerate `patches/k13-audit.patch` from the diff against the base commit.
4. Open a PR; the Build (QMK) workflow verifies that the patch applies and that
   the resulting image passes `tools/verify_bins.py`.

## Reporting a hardware test

Use the issue form (30 seconds). The workflow labels it and regenerates the
compatibility index on the `tested-index` branch. Do not edit `TESTED.md` by hand
— it is generated.
