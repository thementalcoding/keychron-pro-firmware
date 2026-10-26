# Keychron Pro wireless firmware (CKBT51) — community QMK builds

[![CI](https://github.com/thementalcoding/keychron-pro-firmware/actions/workflows/ci.yml/badge.svg)](https://github.com/thementalcoding/keychron-pro-firmware/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/thementalcoding/keychron-pro-firmware?include_prereleases&sort=semver)](https://github.com/thementalcoding/keychron-pro-firmware/releases)
[![Hardware tested](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fthementalcoding%2Fkeychron-pro-firmware%2Ftested-index%2Fdocs%2Ftested.json)](https://github.com/thementalcoding/keychron-pro-firmware/blob/tested-index/TESTED.md)
[![License: GPL-2.0](https://img.shields.io/badge/license-GPL--2.0-blue.svg)](LICENSE)

**English** · [Español](README.es.md)

Unofficial, community-built QMK firmware for **26 Keychron Pro wireless
keyboards** (STM32L432 + **CKBT51** Bluetooth module), based on Keychron's own
`wls_2025q1` branch.

The builds fix a family of Bluetooth-link defects that cause **bursts of repeated
keystrokes** and silent reconnects, and raise the Bluetooth report rate from the
stock 90 Hz to the module's documented maximum of **133 Hz**.

> ⚠️ **Unofficial.** Not affiliated with Keychron. Flashing is your
> responsibility. A brick is practically impossible: the STM32 **ROM bootloader
> cannot be overwritten**, so DFU can always be re-entered
> (see [Recovery](docs/RECOVERY.md)).

**Upstream proposal:** [Keychron/qmk_firmware#529](https://github.com/Keychron/qmk_firmware/pull/529)

---

## Hardware test status

| | |
|---|---|
| ✅ **Tested on real hardware** | **1 unit**: Keychron K13 Pro **ISO RGB** (`0x02D1`) |
| ⚠️ **Compiled + automatically verified, never flashed** | Every other model and variant (94 images) |

Every binary in this repository is compiled from the same patched source, passes
the DFU-suffix/CRC/size checks in CI, and is published with its SHA-256. **No
other unit has been tested**, so treat those images as *untested builds* until a
community report says otherwise.

The original symptom (bursts of repeated keys) is **not yet confirmed as fixed**
long-term: preliminary results on the tested unit are good (+40 % polling rate,
no episodes), but only a few days of use have passed.

Have you flashed one? **[Report it in 30 seconds →](https://github.com/thementalcoding/keychron-pro-firmware/issues/new?template=hardware_test.yml)**
The counters on this page update automatically from those reports
([how it works](docs/TESTING.md)). The generated table lives on the
[`tested-index` branch](https://github.com/thementalcoding/keychron-pro-firmware/blob/tested-index/TESTED.md).

<!-- BEGIN TESTED -->
**1 verified report · 1 model** (maintainer unit, K13 Pro ISO RGB). Live table: [tested-index](https://github.com/thementalcoding/keychron-pro-firmware/blob/tested-index/TESTED.md).
<!-- END TESTED -->

---

## Quick start

1. **Identify your exact variant** (PID) in cable mode:
   ```bash
   lsusb | grep -i 3434
   ```
   Match the PID in the table below. Flashing the wrong variant is recoverable,
   but the keyboard will behave oddly (wrong layout/backlight) until you flash the
   right one.
2. **Back up your keymap**: Keychron Engine (engine.keychron.com) or VIA → export
   the layout JSON.
3. **Verify the download** before flashing:
   ```bash
   sha256sum -c SHA256SUMS
   ```
4. **Flash**: see [Flashing](#flashing) (Linux, macOS, Windows).
5. **Restore your keymap** and [report the result](https://github.com/thementalcoding/keychron-pro-firmware/issues/new?template=hardware_test.yml).

## Downloads

All images are grouped by model. Each model folder has a README with its PIDs,
variants and per-file notes.

<!-- BEGIN MODELS -->
| Model | Variants | USB PIDs | Images | Hardware-tested |
|---|---|---|---|---|
| [K1 Pro](firmware/k1_pro/README.md) | 4 | `0x0210`, `0x0211`, `0x0213`, `0x0214` | 4 | — (untested) |
| [K2 Pro](firmware/k2_pro/README.md) | 6 | `0x0220`, `0x0221`, `0x0222`, `0x0223`, `0x0224`, `0x0225` | 6 | — (untested) |
| [K3 Pro](firmware/k3_pro/README.md) | 6 | `0x0230`, `0x0231`, `0x0232`, `0x0233`, `0x0234`, `0x0235` | 6 | — (untested) |
| [K4 Pro](firmware/k4_pro/README.md) | 4 | `0x0240`, `0x0241`, `0x0243`, `0x0244` | 4 | — (untested) |
| [K5 Pro](firmware/k5_pro/README.md) | 6 | `0x0250`, `0x0251`, `0x0252`, `0x0253`, `0x0254`, `0x0255` | 6 | — (untested) |
| [K6 Pro](firmware/k6_pro/README.md) | 5 | `0x0260`, `0x0261`, `0x0262`, `0x0263`, `0x0264` | 5 | — (untested) |
| [K7 Pro](firmware/k7_pro/README.md) | 4 | `0x0270`, `0x0271`, `0x0273`, `0x0274` | 4 | — (untested) |
| [K8 Pro](firmware/k8_pro/README.md) | 6 | `0x0280`, `0x0281`, `0x0282`, `0x0283`, `0x0284`, `0x0285` | 6 | — (untested) |
| [K9 Pro](firmware/k9_pro/README.md) | 6 | `0x0290`, `0x0291`, `0x0292`, `0x0293`, `0x0294`, `0x0295` | 6 | — (untested) |
| [K10 Pro](firmware/k10_pro/README.md) | 6 | `0x02A0`, `0x02A1`, `0x02A2`, `0x02A3`, `0x02A4`, `0x02A5` | 6 | — (untested) |
| [K11 Pro](firmware/k11_pro/README.md) | 4 | `0x02B0`, `0x02B3`, `0x02B6`, `0x02B9` | 4 | — (untested) |
| [K12 Pro](firmware/k12_pro/README.md) | 2 | `0x02C0`, `0x02C3` | 2 | — (untested) |
| [K13 Pro](firmware/k13_pro/README.md) | 4 | `0x02D0`, `0x02D1`, `0x02D3`, `0x02D4` | 4 | ✅ ISO/RGB |
| [K14 Pro](firmware/k14_pro/README.md) | 2 | `0x02E0`, `0x02E3` | 2 | — (untested) |
| [K15 Pro](firmware/k15_pro/README.md) | 2 | `0x02F6`, `0x02F9` | 2 | — (untested) |
| [K17 Pro](firmware/k17_pro/README.md) | 4 | `0x0206`, `0x0207`, `0x0209`, `0x020A` | 4 | — (untested) |
| [Q1 Pro](firmware/q1_pro/README.md) | 3 | `0x0610`, `0x0611`, `0xA612` | 3 | — (untested) |
| [Q2 Pro](firmware/q2_pro/README.md) | 2 | `0x0620`, `0x0621` | 2 | — (untested) |
| [Q3 Pro](firmware/q3_pro/README.md) | 5 | `0x0630`, `0x0631`, `0x0632`, `0x0633`, `0x0634` | 5 | — (untested) |
| [Q4 Pro](firmware/q4_pro/README.md) | 2 | `0x0640`, `0x0641` | 2 | — (untested) |
| [Q5 Pro](firmware/q5_pro/README.md) | 2 | `0x0650`, `0x0651` | 2 | — (untested) |
| [Q6 Pro](firmware/q6_pro/README.md) | 2 | `0x0660`, `0x0661` | 2 | — (untested) |
| [Q8 Pro](firmware/q8_pro/README.md) | 2 | `0x0680`, `0x0681` | 2 | — (untested) |
| [Q10 Pro](firmware/q10_pro/README.md) | 2 | `0x06A0`, `0x06A1` | 2 | — (untested) |
| [Q13 Pro](firmware/q13_pro/README.md) | 2 | `0x06D0`, `0x06D1` | 2 | — (untested) |
| [Q14 Pro](firmware/q14_pro/README.md) | 2 | `0x06E0`, `0x06E1` | 2 | — (untested) |

Every image is built from the same patched source. Only the rows marked ✅ have been flashed on hardware; the rest are untested builds.
<!-- END MODELS -->

Machine-readable index with sizes, SHA-256, PIDs and tested flags:
[`firmware/manifest.json`](firmware/manifest.json).

> **`_via` vs `_default`:** `_via` images keep the VIA / Keychron Engine keymap
> protocol. `_default` images do not speak VIA — use them only if you don't need
> VIA. If a variant has no `_via` image, that keymap does not exist upstream.

## What it changes

**Bluetooth link robustness** (shared code — benefits all 26 models)

- Bounded UART frame parser (64-byte buffer; no overflow, and legitimate 42–61
  byte module frames are no longer discarded).
- Report queue is flushed on `EVT_RECONNECTING` as well as on disconnect — this
  removes the main burst mechanism: replays of a stale report backlog after a
  lost disconnect event.
- Retry timer reset on module FIFO-full ACKs (no resend storm).
- Low-power gate: never enter STOP1 while reports, retries or events are pending.
- `bluetooth_connect()` rate-limited to one attempt per 500 ms.
- Optional `CKBT51_FAST_WAKE` (off by default) to skip the 3 ms module wake
  sequence when the module is already awake.

**Module parameters** (all CKBT51 models)

- `report_rate`: 90 → **133 Hz**
- `reconnect_timeout`: 5 s → **60 s**
- Applied on the **first Bluetooth init**, independent of boot timing (the old
  1 s — and k13_pro's 5 s — uptime windows are gone).

**Per-model specifics** are listed in each model folder.

## Measured result

Keychron K13 Pro ISO RGB, Linux 6.12, Intel AX210, Bluetooth. Tap test, single
key, 10 s (`tools/medir_polling.py -m tap`):

| Metric | Stock (90 Hz) | This firmware (133 Hz) |
|---|---|---|
| Minimum inter-report gap | 7 ms | **5 ms** |
| Estimated report ceiling | ~143 reports/s | **~200 reports/s** |

## Flashing

You need `dfu-util` (Linux/macOS) or QMK Toolbox (Windows). There is no driver
to install on Linux/macOS; Windows needs the WinUSB driver (QMK Toolbox installs
it).

### Enter DFU (all models)

1. Switch the keyboard to **Off**.
2. Hold **Esc**.
3. Switch to **Cable** while holding Esc (or hold the reset button under the
   spacebar, if your model has one).
4. Release. `lsusb` should show `0483:df11 STMicroelectronics STM32 BOOTLOADER`.

### Linux

```bash
sudo dfu-util -d 0483:df11 -a 0 -s 0x08000000:leave -D \
  firmware/k13_pro/iso-rgb/keychron_k13_pro_iso_rgb_via.bin
```

If you get `LIBUSB_ERROR_ACCESS`, add the udev rule from
[`docs/RECOVERY.md`](docs/RECOVERY.md#linux-udev-rule).

### macOS

```bash
brew install dfu-util
dfu-util -d 0483:df11 -a 0 -s 0x08000000:leave -D firmware/<model>/<variant>/<file>.bin
```

### Windows

Use [QMK Toolbox](https://qmk.fm/toolbox): select the `.bin`, enable
"STM32 DFU", plug the keyboard in DFU mode and press **Flash**. Keychron Engine
also works for restoring stock firmware, not for these builds.

The keyboard reboots into the new firmware. Restore your keymap JSON.

## If something goes wrong

Read **[docs/RECOVERY.md](docs/RECOVERY.md)** (Español:
[RECOVERY.es.md](docs/RECOVERY.es.md)). Short version:

- The ROM bootloader is never erased; **re-enter DFU and flash again**.
- Wrong variant / no keys / no backlight → flash the correct PID image.
- Keyboard not detected in DFU → try another cable/port (USB 2.0, no hub),
  switch Off → hold Esc → Cable again.
- Bluetooth dead but USB works → reflash; if it persists, the CKBT51 module
  firmware may need Keychron's official updater (see limitations).
- Last resort: restore stock firmware with Keychron Engine.

## Known limitations

- **Single-unit validation.** Only the K13 Pro ISO RGB has been flashed on
  hardware; everything else is compiled and statically verified only.
- Switching BT → USB → BT in under 500 ms can suppress one connect attempt
  (one keystroke may be delayed until the next retry).
- Module parameters are sent on the first Bluetooth init after power-on; they are
  not re-sent on every reconnect.
- This project changes only the **STM32 (MCU)**. The CKBT51 radio module runs
  closed firmware; for module-side fixes use Keychron's official updater
  (`Keychron_Bt_Firmware_Upgrade_v0.14.exe`). Running it overwrites the MCU
  firmware, so re-flash this build afterwards.
- Some variants have no `via` keymap upstream; their images are `_default` only.

## Verify a download

```bash
sha256sum -c SHA256SUMS
python3 tools/verify_bins.py            # DFU suffix, VID/PID, CRC, size
python3 tools/verify_manifest.py        # manifest ↔ files consistency
```

## Build from source

```bash
git clone https://github.com/thementalcoding/qmk_firmware.git
cd qmk_firmware && git checkout k13-pro-bt-fixes
# QMK CLI, arm-none-eabi-gcc 12–14; clang-format 19.x for CI parity
qmk compile -kb keychron/k13_pro/iso/rgb -km via
```

The patch series applies to a clean `Keychron/qmk_firmware` checkout at
`c8b2b23` (`wls_2025q1`); see [`patches/`](patches/) and
[`CONTRIBUTING.md`](CONTRIBUTING.md).

## Repository layout

```
firmware/<model>/<variant>/<binary>.bin   # one folder per model, one per variant
firmware/manifest.json                    # machine-readable index
SHA256SUMS                                # checksums for every binary
docs/                                     # audit, SDD, recovery, testing guide
patches/                                  # upstream patch series
tools/                                    # flash/verify/measure scripts
```

The generated hardware-test index lives on the `tested-index` branch
(`TESTED.md` + `docs/tested.json`), so `main` stays protected and reviewed.

Model folders use lowercase upstream names (`k13_pro`, `q6_pro`, …). Variant
folders use dashes (`iso-rgb`, `ansi-white`).

## Versioning

[SemVer](https://semver.org/). **The same version number means the same bytes** —
a release is never re-uploaded with different content.

- `v1.0.0` (build **2026-10-26c**): first group-wide release, 26 models, 95
  images. One unit hardware-tested (K13 Pro ISO RGB).
- Future fixes: `1.0.x-alpha.N` (single-unit validation) → `-beta.N` (broader
  hardware reports) → stable.
- Release notes always state the upstream baseline commit.

## Credits & license

- Based on [Keychron/qmk_firmware](https://github.com/Keychron/qmk_firmware)
  (`wls_2025q1`) — QMK Firmware and ChibiOS are GPL-2.0.
- All changes here are released under **GPL-2.0** (see [LICENSE](LICENSE)).
- Audit and design notes: [`docs/AUDIT.md`](docs/AUDIT.md),
  [`docs/SDD.md`](docs/SDD.md), [`docs/GAMA_AUDIT.md`](docs/GAMA_AUDIT.md).
