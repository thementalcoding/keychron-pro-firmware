# Contributing

Thanks for helping improve the Keychron Pro wireless firmware. This repository
publishes patched QMK builds for 67 Keychron wireless products (26 CKBT51 Pro
+ 41 LKBT51 Max/Version) plus the audit and tooling;
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

The Build (QMK) workflow re-applies `patches/final-v1.0.1.patch` on Keychron's tree
at the pinned base commit and compiles the ISO RGB `via` variant inside the
`ghcr.io/qmk/qmk_cli` container, so a green build job means the patch still
applies cleanly upstream.

## Automated tests

| Test | What it covers | Run locally |
|---|---|---|
| Host parser tests | `ckbt51_task()` and `lkbt51_read()`/`lkbt51_task()` from the patched tree, built with ASan/UBSan against a fake UART/SPI transport (oversized, truncated and malformed frames, STOP1 mid-frame) | `bash tests/host/run_host_tests.sh <patched qmk tree>` |
| Polling unit tests | Parser and batching logic of the multikey polling test | `python3 -m unittest discover -s tests -v` |
| QMK unit tests | QMK's own `qmk test-c` suite on the PR branch; the encoder tests cover the `encoder_quadrature.c` change | `qmk test-c` in the `qmk_firmware` checkout |
| QMK lint/format | `qmk lint` on every touched board (no errors beyond the ones already present upstream) and `qmk format-c --core-only` with clang-format 14, as in Keychron's PR checks | see Keychron's `lint.yml`/`format.yml` |

The host parser tests run in CI on every push. Run against Keychron's
unpatched base they fail 8 of 9 cases (stack overflows and lost frames), which
is the regression they guard against.

## Test matrix

Every firmware change must build **all 67 models / 231 variants** before a
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

The main test is the standalone multikey script v0.0.1. See
[`docs/POLLING_TEST.md`](docs/POLLING_TEST.md) for requirements and
interpretation.

```bash
sudo python3 tools/polling_multikey_v0.0.1.py --list
sudo python3 tools/polling_multikey_v0.0.1.py -t 10 -d /dev/input/event19
```

Press 3-5 keys simultaneously during the whole test and compare Bluetooth
against USB on the same host. Report `p10`, minimum, and estimated reports/s.
The CKBT51 module ceiling is ~133 Hz (~7.5 ms); a 143/s estimate is heuristic
noise, not a 1000 Hz link.

An optional single-key tap test is also available:

```bash
sudo python3 tools/medir_polling.py -m tap -t 10
```

## Rebuilding published binaries

```bash
# 1. build every variant into builds_v1.0.1/ (see the tester role / build-status.json)
# 2. assemble firmware/, per-model READMEs, manifest.json and SHA256SUMS
python3 tools/gen_firmware_docs.py \
  --builds /path/to/builds_v1.0.1 \
  --qmk-root /path/to/qmk_firmware \
  --out . \
  --tested k13_pro/iso/rgb \
  --version 1.0.1 --build 2026-11-03a

# 3. verify
python3 tools/verify_bins.py
python3 tools/verify_manifest.py
sha256sum -c SHA256SUMS

# 4. build the release assets (67 standalone model ZIPs + full ZIP)
python3 tools/make_release_assets.py --out /tmp/release --version 1.0.1
```

`tools/make_release_assets.py` reads `firmware/manifest.json` and produces, per
model, `keychron-<model>-v<version>.zip` containing a short `README.md`, a model
`SHA256SUMS` and `firmware/<model>/...`. The `...-full.zip` asset contains the
whole published tree (without `.github`, `.git` or caches). The script extracts
every model ZIP into a temporary directory and runs `sha256sum -c SHA256SUMS`, so
a non-zero exit means an asset is broken. ZIPs use fixed timestamps and sorted
entries to keep rebuilds reproducible.

## Pull request checklist

- [ ] Builds pass for the full matrix (231 variants for a release).
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
- Follow upstream QMK style; core files are checked with `qmk format-c`
  (clang-format 14, as in QMK's CI).

## Proposing MCU firmware changes

1. Modify the source in your QMK checkout (branch `k13-pro-bt-fixes`).
2. Rebuild the affected variants and regenerate `firmware/`,
   `firmware/manifest.json` and `SHA256SUMS`.
3. Regenerate `patches/final-v1.0.1.patch` (or the new version's patch) from the
   diff against the base commit `c8b2b23`.
4. Open a PR; the Build (QMK) workflow verifies that the patch applies and that
   the resulting image passes `tools/verify_bins.py`.

## Reporting a hardware test

Use the issue form (30 seconds). The workflow labels it and regenerates the
compatibility index on the `tested-index` branch. Do not edit `TESTED.md` by hand
— it is generated.
