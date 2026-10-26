# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
