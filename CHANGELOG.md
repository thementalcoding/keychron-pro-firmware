# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

No change to the published firmware images: all 231 rebuild bit-identical
from the updated patch, with 0 warnings, when built with the original build
timestamp (QMK embeds `QMK_BUILDDATE` in the image; LKBT51 images embed the
full date and time).

### Added

- `tests/host/`: CKBT51/LKBT51 parser tests under ASan/UBSan, run in CI.
- CI now runs the polling unit tests on every push, not only on pull requests.

### Changed

- `patches/final-v1.0.1.patch`: `encoder_quadrature.c` atomic read is opt-in
  through `ENCODER_QUADRATURE_ATOMIC_READ` (enabled by the Keychron wireless
  makefiles), so QMK's `qmk test-c` encoder tests build again; source comments
  cleaned up for upstream review.
- Docs: process records from v1.0.0 (`AUDIT.md`, `SDD.md`, `GAMA_AUDIT.md`,
  `PER_BOARD_REVIEW.md`, the first PR #529 text and `patches/notes*.md`) moved to
  `docs/history/`; `STATE.md`, `AI_CONTEXT.md`, `AGENTS.md` and `llms.txt`
  now point at `patches/final-v1.0.1.patch` as the source of truth and drop
  duplicated content.
- Field status: the tested K13 Pro ISO RGB has run about 10 days of daily
  Bluetooth use with no freezes or key bursts (single unit).

## [1.0.1] — 2026-11-03 (build a) — final

Full-range release: **67 Keychron wireless products**, **231 binary images**
(26 CKBT51 Pro models / 95 images, plus 41 LKBT51 Max/Version models / 136
images). Based on Keychron `wls_2025q1` @ `c8b2b23` with the previous
`v1.0.1-beta` work and the Claude audit patch series applied.

> **Hardware validation: 1 unit.** The **K13 Pro ISO RGB** (`0x02D1`) was
> flashed with the v1.0.1 final bytes and post-DFU enumeration confirmed on
> 2026-11-03. The other 230 images compile and pass the automated
> DFU/CRC/size/manifest checks, but have not been tested on hardware. LKBT51 has
> never been flashed.

### Added

- LKBT51 SPI-family support in the published tree: 41 models, 136 variants.
- Claude audit fixes: bounded CKBT51 parser with incomplete-frame timeout,
  `ckbt51_rx_idle()` LPM gate, OTA RX length validation, report-queue flush on
  host change, retry guards for NKRO/consumer, PIN-key direct send, connect
  rate-limit on activity, pairing timer moved out of ISR, K13 16-bit shift
  register output, HC595 DS setup delay, Q3 column mask fix, encoder atomicity,
  and the LKBT51 read/parser/OTA/queue/LPM equivalents.
- `v1.0.1-beta` is the previous local beta (historical folder before consolidation, build `2026-11-02a`,
  26 CKBT51 models / 95 images).
- Claude audit findings are documented in `docs/CLAUDE_AUDIT.md`.

### Changed

- The P5 post-DFU USB enumeration wait (500 ms) is retained for CKBT51 and
  extended to LKBT51 as a defensive measure.
- The historical “5 ms / ~200 reports/s” measurement is withdrawn: a single-key
  tap is ~7.5 ms / 133 Hz.

## [1.0.1-beta] — 2026-11-02 (build 2026-11-02a) — beta

Previous local beta. 26 CKBT51 models / 95 images; P1 reconnect flush, P2 clean
host switch, P3 UART parser reset after STOP1, P4 per-board matrix settle and
GPIO atomicity, P5 USB enumeration wait after DFU. Superseded by v1.0.1 final.

## [1.0.0] — 2026-10-26 (build c)

First **group-wide** release: 26 Keychron Pro wireless models (CKBT51), 95
binary images, one folder per model.

> **Hardware validation: 1 unit.** Only the Keychron K13 Pro ISO RGB
> (`3434:02d1`) has been flashed and used. Every other image is compiled from the
> same patched source and passes the automated DFU/CRC/size/manifest checks, but
> **has not been tested on hardware**. Report results through the
> [hardware-test form](https://github.com/thementalcoding/keychron-pro-firmware/issues/new?template=hardware_test.yml).

### Added

- **All 26 CKBT51 models built**: K1–K17 Pro, Q1–Q14 Pro (95 variants), organised
  as `firmware/<model>/<variant>/<binary>.bin`.
- `firmware/manifest.json` with path, size, SHA-256, model, variant, keymap, USB
  PID and `tested` flag for every image; `SHA256SUMS` at the repository root.
- Per-model READMEs with PIDs, variants and tested status.
- **Hardware-test reporting system**: issue form → automatic labels
  (`tested-ok` / `tested-problem`) → generated `TESTED.md` + badge on the
  `tested-index` branch.
- `docs/RECOVERY.md` / `docs/RECOVERY.es.md`: step-by-step bad-flash recovery
  (DFU entry, udev, wrong variant, Bluetooth-only failures, stock restore,
  EEPROM reset).
- `docs/TESTING.md` / `docs/TESTING.es.md`: how reports are counted.
- Bilingual README (`README.md`, `README.es.md`).
- `tools/verify_manifest.py`, `tools/hardware_tests.py`.
- CI: manifest ↔ files ↔ checksums cross-check; all binaries validated.

### Fixed

- Module parameters (`report_rate=133`, `reconnect_timeout=60 s`) are applied on
  the **first Bluetooth init on all 26 CKBT51 boards**: the 1 s MCU-uptime window
  (and k13_pro's 5 s window) is removed, so a slow module boot or a late switch to
  Bluetooth no longer leaves the module on factory defaults.
- Bluetooth link robustness: bounded UART frame parser, chunked DFU TX,
  report-queue flush on reconnect, FIFO-full retry backoff, low-power gate and
  connect rate limit (plus opt-in `CKBT51_FAST_WAKE`, off by default).
- Report rate 90 → **133 Hz**; reconnect timeout 5 → **60 s** on every CKBT51
  board.
- q6_pro: removed an accidental `ckbt51_factory_reset()` on Fn+F3 that wiped
  pairing/parameters.
- q1_pro: Bluetooth name is now published without surrounding quotes.

### Changed

- Release assets repackaged: each `keychron-<model>-v1.0.0.zip` is now standalone
  (brief `README.md` + model `SHA256SUMS` + `firmware/<model>/...`), plus a
  `keychron-pro-firmware-v1.0.0-full.zip` with the complete tree. Per-model
  documentation links are absolute.
- Repository renamed and reorganised for the whole Keychron Pro wireless range.
- Binaries built from the 4-commit series on upstream `Keychron/qmk_firmware`
  `wls_2025q1` @ `c8b2b23` (arm-none-eabi-gcc 14.2, QMK CLI).
- `_via` keymaps are used wherever they exist upstream; otherwise `_default`.

### Notes

- The original burst/duplicate-keystroke symptom is **not yet confirmed fixed**
  long-term; field use on the tested unit continues.
- This project does not modify the closed CKBT51 module firmware.
- Some variants have no `via` keymap upstream and are published as `_default`
  only.

## [1.0.0] — 2026-10-26 (build b) — withdrawn

Removed on 2026-10-26 to rebuild v1.0.0 for all models. The release, its assets
and the `v1.0.0` tag were deleted; notes archived in
[`docs/history/release-v1.0.0-build-b.md`](docs/history/release-v1.0.0-build-b.md).

Scope was K13 Pro (4 variants + 1 VIA build) plus one K14 Pro spot check. All
four patch commits, the group audit (26 boards / 95 variants) and the first
public repository layout were introduced in this build.
