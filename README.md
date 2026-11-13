# Keychron wireless firmware (CKBT51 / LKBT51) — community QMK builds

[![CI](https://github.com/thementalcoding/keychron-pro-firmware/actions/workflows/ci.yml/badge.svg)](https://github.com/thementalcoding/keychron-pro-firmware/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/thementalcoding/keychron-pro-firmware?include_prereleases&sort=semver)](https://github.com/thementalcoding/keychron-pro-firmware/releases)
[![Hardware tested](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fthementalcoding%2Fkeychron-pro-firmware%2Ftested-index%2Fdocs%2Ftested.json)](https://github.com/thementalcoding/keychron-pro-firmware/blob/tested-index/TESTED.md)
[![License: GPL-2.0](https://img.shields.io/badge/license-GPL--2.0-blue.svg)](LICENSE)

**English** · [Español](README.es.md)

Unofficial, community-built QMK firmware for **67 Keychron wireless products**:
**26 Pro models with the CKBT51 UART module** and **41 Max / Version models with
the LKBT51 SPI module**, based on Keychron's own `wls_2025q1` branch.

The builds fix a family of Bluetooth-link defects that cause **bursts of repeated
keystrokes** and silent reconnects. On CKBT51 they also raise the report rate from
the stock 90 Hz to the module's documented maximum of **133 Hz**; LKBT51 fixes are
defensive and have not been hardware-validated yet.

Symptoms addressed: **key chatter, double typing and bursts of repeated keys**
over Bluetooth, plus silent reconnects and a low report rate.

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
| ⚠️ **Compiled + automatically verified, never flashed** | Every other model and variant (230 images) |

Every binary in this repository is compiled from the same patched source, passes
the DFU-suffix/CRC/size checks in CI, and is published with its SHA-256. **No
other unit has been tested**, so treat those images as *untested builds* until a
community report says otherwise.

**Field status (2026-11-13):** the tested unit has run v1.0.1 final for about
10 days of daily Bluetooth use with no freezes and no key bursts, both of which
happened with the stock firmware. This is still a single unit, so the fix is not
confirmed for the rest of the range.

Have you flashed one? **[Report it in 30 seconds →](https://github.com/thementalcoding/keychron-pro-firmware/issues/new?template=hardware_test.yml)**
The counters on this page update automatically from those reports
([how it works](docs/TESTING.md)). The generated table lives on the
[`tested-index` branch](https://github.com/thementalcoding/keychron-pro-firmware/blob/tested-index/TESTED.md).

<!-- BEGIN TESTED -->
**1 verified report · 1 model** (maintainer unit, K13 Pro ISO RGB, v1.0.1 final, post-DFU enumeration OK 2026-11-03). Live table: [tested-index](https://github.com/thementalcoding/keychron-pro-firmware/blob/tested-index/TESTED.md).
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
6. **Measure the link**: run the [multikey polling test v0.0.1](docs/POLLING_TEST.md).

## Downloads

All images are grouped by model. Each model folder has a README with its PIDs,
variants and per-file notes.

<!-- BEGIN MODELS -->
| Model | Variants | USB PIDs | Images | Hardware-tested |
|---|---|---|---|---|
| [K0 Max](firmware/k0_max/README.md) | 1 | `0x0A06` | 1 | no |
| [K10 Max](firmware/k10_max/README.md) | 4 | `0x0AA0`, `0x0AA3`, `0x0AA1`, `0x0AA4` | 4 | no |
| [K10 Pro](firmware/k10_pro/README.md) | 6 | `0x02A0`, `0x02A3`, `0x02A1`, `0x02A4`, `0x02A2`, `0x02A5` | 6 | no |
| [K10 Version 2](firmware/k10_version_2/README.md) | 6 | `0x0DA0`, `0x0DA3`, `0x0DA1`, `0x0DA4`, `0x0DA2`, `0x0DA5` | 6 | no |
| [K11 Max](firmware/k11_max/README.md) | 6 | `0x0AB3`, `0x0AB9`, `0x0AB4`, `0x0ABA`, `0x0AB5`, `0x0ABB` | 6 | no |
| [K11 Pro](firmware/k11_pro/README.md) | 4 | `0x02B0`, `0x02B3`, `0x02B6`, `0x02B9` | 4 | no |
| [K12 Pro](firmware/k12_pro/README.md) | 2 | `0x02C0`, `0x02C3` | 2 | no |
| [K13 Max](firmware/k13_max/README.md) | 4 | `0x0AD0`, `0x0AD3`, `0x0AD1`, `0x0AD4` | 4 | no |
| [K13 Pro](firmware/k13_pro/README.md) | 4 | `0x02D0`, `0x02D3`, `0x02D1`, `0x02D4` | 4 | ✅ ISO RGB |
| [K14 Pro](firmware/k14_pro/README.md) | 2 | `0x02E0`, `0x02E3` | 2 | no |
| [K15 Max](firmware/k15_max/README.md) | 4 | `0x0AF0`, `0x0AF3`, `0x0AF1`, `0x0AF4` | 4 | no |
| [K15 Pro](firmware/k15_pro/README.md) | 2 | `0x02F6`, `0x02F9` | 2 | no |
| [K17 Max](firmware/k17_max/README.md) | 6 | `0x0A00`, `0x0A03`, `0x0A01`, `0x0A04`, `0x0A02`, `0x0A05` | 6 | no |
| [K17 Pro](firmware/k17_pro/README.md) | 4 | `0x0206`, `0x0209`, `0x0207`, `0x020A` | 4 | no |
| [K1 Max](firmware/k1_max/README.md) | 6 | `0x0A10`, `0x0A13`, `0x0A11`, `0x0A14`, `0x0A12`, `0x0A15` | 6 | no |
| [K1 Pro](firmware/k1_pro/README.md) | 4 | `0x0210`, `0x0213`, `0x0211`, `0x0214` | 4 | no |
| [K1 Version 6](firmware/k1_version_6/README.md) | 6 | `0x0D10`, `0x0D13`, `0x0D11`, `0x0D14`, `0x0D12`, `0x0D15` | 6 | no |
| [K2 Max](firmware/k2_max/README.md) | 6 | `0x0A20`, `0x0A23`, `0x0A21`, `0x0A24`, `0x0A22`, `0x0A25` | 6 | no |
| [K2 Pro](firmware/k2_pro/README.md) | 6 | `0x0220`, `0x0223`, `0x0221`, `0x0224`, `0x0222`, `0x0225` | 6 | no |
| [K2 Version 3](firmware/k2_version_3/README.md) | 6 | `0x0D20`, `0x0D23`, `0x0D21`, `0x0D24`, `0x0D22`, `0x0D25` | 6 | no |
| [K3 Max](firmware/k3_max/README.md) | 6 | `0x0A30`, `0x0A33`, `0x0A31`, `0x0A34`, `0x0A32`, `0x0A35` | 6 | no |
| [K3 Pro](firmware/k3_pro/README.md) | 6 | `0x0230`, `0x0233`, `0x0231`, `0x0234`, `0x0232`, `0x0235` | 6 | no |
| [K3 Version 3](firmware/k3_version_3/README.md) | 6 | `0x0D30`, `0x0D33`, `0x0D31`, `0x0D34`, `0x0D32`, `0x0D35` | 6 | no |
| [K4 Pro](firmware/k4_pro/README.md) | 4 | `0x0240`, `0x0243`, `0x0241`, `0x0244` | 4 | no |
| [K4 Version 3](firmware/k4_version_3/README.md) | 6 | `0x0D40`, `0x0D43`, `0x0D41`, `0x0D44`, `0x0D42`, `0x0D45` | 6 | no |
| [K5 Max](firmware/k5_max/README.md) | 4 | `0x0A50`, `0x0A53`, `0x0A51`, `0x0A54` | 4 | no |
| [K5 Pro](firmware/k5_pro/README.md) | 6 | `0x0250`, `0x0253`, `0x0251`, `0x0254`, `0x0252`, `0x0255` | 6 | no |
| [K5 Version 2](firmware/k5_version_2/README.md) | 6 | `0x0D50`, `0x0D53`, `0x0D51`, `0x0D54`, `0x0D52`, `0x0D55` | 6 | no |
| [K6 Pro](firmware/k6_pro/README.md) | 5 | `0x0260`, `0x0263`, `0x0261`, `0x0264`, `0x0262` | 5 | no |
| [K7 Max](firmware/k7_max/README.md) | 6 | `0x0A70`, `0x0A73`, `0x0A71`, `0x0A74`, `0x0A72`, `0x0A75` | 6 | no |
| [K7 Pro](firmware/k7_pro/README.md) | 4 | `0x0270`, `0x0273`, `0x0271`, `0x0274` | 4 | no |
| [K8 Max](firmware/k8_max/README.md) | 6 | `0x0A80`, `0x0A83`, `0x0A81`, `0x0A84`, `0x0A82`, `0x0A85` | 6 | no |
| [K8 Pro](firmware/k8_pro/README.md) | 6 | `0x0280`, `0x0283`, `0x0281`, `0x0284`, `0x0282`, `0x0285` | 6 | no |
| [K8 Version 2](firmware/k8_version_2/README.md) | 6 | `0x0D80`, `0x0D83`, `0x0D81`, `0x0D84`, `0x0D82`, `0x0D85` | 6 | no |
| [K9 Pro](firmware/k9_pro/README.md) | 6 | `0x0290`, `0x0293`, `0x0291`, `0x0294`, `0x0292`, `0x0295` | 6 | no |
| [Q0 Max](firmware/q0_max/README.md) | 1 | `0x0800` | 1 | no |
| [Q10 Max](firmware/q10_max/README.md) | 2 | `0x08A0`, `0x08A1` | 2 | no |
| [Q10 Pro](firmware/q10_pro/README.md) | 2 | `0x06A0`, `0x06A1` | 2 | no |
| [Q12 Max](firmware/q12_max/README.md) | 1 | `0x08C3` | 1 | no |
| [Q13 Max](firmware/q13_max/README.md) | 1 | `0x08D0` | 1 | no |
| [Q13 Pro](firmware/q13_pro/README.md) | 2 | `0x06D0`, `0x06D1` | 2 | no |
| [Q14 Max](firmware/q14_max/README.md) | 1 | `0x08E0` | 1 | no |
| [Q14 Pro](firmware/q14_pro/README.md) | 2 | `0x06E0`, `0x06E1` | 2 | no |
| [Q15 Max](firmware/q15_max/README.md) | 1 | `0x08F0` | 1 | no |
| [Q1 Max](firmware/q1_max/README.md) | 3 | `0x0810`, `0x0811`, `0x0812` | 3 | no |
| [Q1 Pro](firmware/q1_pro/README.md) | 3 | `0x0610`, `0x0611`, `0xA612` | 3 | no |
| [Q2 Max](firmware/q2_max/README.md) | 2 | `0x0820`, `0x0821` | 2 | no |
| [Q2 Pro](firmware/q2_pro/README.md) | 2 | `0x0620`, `0x0621` | 2 | no |
| [Q3 Max](firmware/q3_max/README.md) | 2 | `0x0830`, `0x0831` | 2 | no |
| [Q3 Pro](firmware/q3_pro/README.md) | 5 | `0x0633`, `0x0630`, `0x0634`, `0x0631`, `0x0632` | 5 | no |
| [Q4 Pro](firmware/q4_pro/README.md) | 2 | `0x0640`, `0x0641` | 2 | no |
| [Q5 Max](firmware/q5_max/README.md) | 2 | `0x0850`, `0x0851` | 2 | no |
| [Q5 Pro](firmware/q5_pro/README.md) | 2 | `0x0650`, `0x0651` | 2 | no |
| [Q60 Max](firmware/q60_max/README.md) | 1 | `0x08C0` | 1 | no |
| [Q65 Max](firmware/q65_max/README.md) | 1 | `0x08B0` | 1 | no |
| [Q6 Max](firmware/q6_max/README.md) | 2 | `0x0860`, `0x0861` | 2 | no |
| [Q6 Pro](firmware/q6_pro/README.md) | 2 | `0x0660`, `0x0661` | 2 | no |
| [Q8 Max](firmware/q8_max/README.md) | 1 | `0x0880` | 1 | no |
| [Q8 Pro](firmware/q8_pro/README.md) | 2 | `0x0680`, `0x0681` | 2 | no |
| [V10 Max](firmware/v10_max/README.md) | 1 | `0x09A0` | 1 | no |
| [V1 Max](firmware/v1_max/README.md) | 3 | `0x0913`, `0x0914`, `0x0915` | 3 | no |
| [V2 Max](firmware/v2_max/README.md) | 2 | `0x0920`, `0x0921` | 2 | no |
| [V3 Max](firmware/v3_max/README.md) | 2 | `0x0933`, `0x0934` | 2 | no |
| [V4 Max](firmware/v4_max/README.md) | 1 | `0x0940` | 1 | no |
| [V5 Max](firmware/v5_max/README.md) | 2 | `0x0950`, `0x0951` | 2 | no |
| [V6 Max](firmware/v6_max/README.md) | 2 | `0x0960`, `0x0961` | 2 | no |
| [V8 Max](firmware/v8_max/README.md) | 1 | `0x0980` | 1 | no |
<!-- END MODELS -->

Machine-readable index with sizes, SHA-256, PIDs and tested flags:
[`firmware/manifest.json`](firmware/manifest.json).

> **`_via` vs `_default`:** `_via` images keep the VIA / Keychron Engine keymap
> protocol. `_default` images do not speak VIA — use them only if you don't need
> VIA. If a variant has no `_via` image, that keymap does not exist upstream.

## What it changes

**Bluetooth link robustness** (shared CKBT51 code — benefits all 26 Pro models)

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

**LKBT51 SPI family** (41 Max / Version models)

- `lkbt51_read()` is bounded to the 64-byte packet buffer.
- The `0xAA 0x57` parser validates `len >= 3`, keeps packets inside `buf[]`, and
  no longer locks permanently on an out-of-range header.
- OTA TX is chunked and RX rejects payloads shorter than the sub-header.
- Report queues are flushed on reconnect, host change and suspend; consumer
  reports wait for a pending retry.
- Encoder initialization is moved after mode-pin EXTI handling on wake.

**Per-model specifics** are listed in each model folder.

## Measured result

Keychron K13 Pro ISO RGB, Linux 6.12, Intel AX210, Bluetooth. Tap test, single
key, 10 s (`tools/medir_polling.py -m tap`):

| Metric | Stock (90 Hz) | This firmware (133 Hz) |
|---|---|---|
| Module report-rate ceiling | 90 Hz | **133 Hz** |
| Single-key tap floor | ~7.5 ms | ~7.5 ms |

The earlier “5 ms / ~200 reports/s” figure was a multi-key measurement and is
withdrawn; a single-key tap is limited to roughly 7.5 ms / 133 Hz by the closed
module.

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
  hardware; everything else is compiled and statically verified only. The 41
  LKBT51 images have never been flashed.
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
# QMK CLI, arm-none-eabi-gcc 12–14; clang-format 14 (QMK CI) for core files
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
- `v1.0.1-beta` (build **2026-11-02a**, historical): 26 CKBT51 models, 95 images;
  the previous local beta with P1–P5.
- `v1.0.1` (build **2026-11-03a**): 67 models, 231 images; Claude audit patches
  plus the P5 USB enumeration wait. The previous v1.0.1 is renamed to
  `v1.0.1-beta`.
- Future fixes: `1.0.x-alpha.N` (single-unit validation) → `-beta.N` (broader
  hardware reports) → stable.
- Release notes always state the upstream baseline commit.

## Credits & license

- Based on [Keychron/qmk_firmware](https://github.com/Keychron/qmk_firmware)
  (`wls_2025q1`) — QMK Firmware and ChibiOS are GPL-2.0.
- All changes here are released under **GPL-2.0** (see [LICENSE](LICENSE)).
- Audit status: [`docs/CLAUDE_AUDIT.md`](docs/CLAUDE_AUDIT.md); earlier audit
  and design notes: [`docs/history/`](docs/history/README.md).
