# v1.0.0 — build 2026-10-26b (withdrawn release notes)

> **Withdrawn on 2026-10-26** to rebuild v1.0.0 with **all affected CKBT51
> models**. The release, its assets and the `v1.0.0` tag were deleted from the
> repository; the notes below are preserved for historical reference only.
>
> Original release name: `v1.0.0 — build 2026-10-26b (experimental)`
> Original tag: `v1.0.0`
> Original assets: 6 `.bin` files, `manifest.json`, `SHA256SUMS`.

---

## ⚠️ Warnings

- **Unofficial** community firmware; not affiliated with Keychron.
- **Hardware-tested on a single unit only**: a Keychron K13 Pro ISO RGB (`firmware/k13_pro/iso-rgb/keychron_k13_pro_iso_rgb_via.bin`). The other images compile and pass the automated verification, but have **not been flashed** on a device.
- The original symptom (bursts of repeated keystrokes / silent Bluetooth reconnects) is **not yet confirmed as fixed**: preliminary results are good (+40 % polling rate, no episodes so far), but 2–3 days of field use are still pending.
- This project does **not** modify the closed CKBT51 Bluetooth module firmware; only the STM32 MCU firmware changes.
- **Back up your keymap** before flashing. Recovery is always possible: the STM32 **ROM DFU bootloader cannot be overwritten** (switch Off → hold **Esc** → switch to **Cable**).

## Model matrix

| Brand | Model | Variant | PID | Binary | Hardware-tested |
|---|---|---|---|---|---|
| Keychron | K13 Pro | **ISO RGB** | `0x02D1` | **`firmware/k13_pro/iso-rgb/keychron_k13_pro_iso_rgb_via.bin`** ← recommended | ✅ yes (1 unit) |
| Keychron | K13 Pro | ISO RGB | `0x02D1` | `firmware/k13_pro/iso-rgb/keychron_k13_pro_iso_rgb_default.bin` | ⚠️ no |
| Keychron | K13 Pro | ANSI RGB | `0x02D0` | `firmware/k13_pro/ansi-rgb/keychron_k13_pro_ansi_rgb_default.bin` | ⚠️ no |
| Keychron | K13 Pro | ANSI white | `0x02D3` | `firmware/k13_pro/ansi-white/keychron_k13_pro_ansi_white_default.bin` | ⚠️ no |
| Keychron | K13 Pro | ISO white | `0x02D4` | `firmware/k13_pro/iso-white/keychron_k13_pro_iso_white_default.bin` | ⚠️ no |
| Keychron | K14 Pro | ANSI RGB | `0x02E0` | `firmware/k14_pro/ansi-rgb/keychron_k14_pro_ansi_rgb_default.bin` | ⚠️ no (spot check) |

## What changed in this build

- Module parameters (`report_rate=133`, `reconnect_timeout=60 s`) applied on the **first Bluetooth init on all 26 CKBT51 boards** (no uptime window).
- Link robustness (bounded UART parser, chunked DFU TX, queue flush on reconnect, FIFO-full backoff, LPM gate, connect rate limit).
- Group-wide audit of the CKBT51 range: 26 boards / 95 variants (`docs/GAMA_AUDIT.md`).

## Upstream baseline

`Keychron/qmk_firmware` `wls_2025q1` @ `c8b2b23` (4 commits). Upstream PR: https://github.com/Keychron/qmk_firmware/pull/529

## Verify

`sha256sum -c SHA256SUMS` (the same hashes are mirrored in `manifest.json`).

**This build (2026-10-26b) supersedes the 02:34 build of the same day: the binaries were rebuilt, so the SHA-256 hashes changed.**

## Per-model notes

- K13 Pro: `firmware/k13_pro/README.md`
- K14 Pro: `firmware/k14_pro/README.md`

## Asset names

GitHub requires unique asset filenames, so the release assets are prefixed with
`keychron_<model>_`. They are byte-identical to:

| Asset | Repository path |
|---|---|
| `keychron_k13_pro_iso_rgb_via.bin` | `firmware/k13_pro/iso-rgb/keychron_k13_pro_iso_rgb_via.bin` |
| `keychron_k13_pro_iso_rgb_default.bin` | `firmware/k13_pro/iso-rgb/keychron_k13_pro_iso_rgb_default.bin` |
| `keychron_k13_pro_iso_white_default.bin` | `firmware/k13_pro/iso-white/keychron_k13_pro_iso_white_default.bin` |
| `keychron_k13_pro_ansi_rgb_default.bin` | `firmware/k13_pro/ansi-rgb/keychron_k13_pro_ansi_rgb_default.bin` |
| `keychron_k13_pro_ansi_white_default.bin` | `firmware/k13_pro/ansi-white/keychron_k13_pro_ansi_white_default.bin` |
| `keychron_k14_pro_ansi_rgb_default.bin` | `firmware/k14_pro/ansi-rgb/keychron_k14_pro_ansi_rgb_default.bin` |

The `SHA256SUMS` inside the repository uses the repository-relative paths; the
hashes are identical either way.
