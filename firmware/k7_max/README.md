# K7 Max — community QMK firmware

[← All models](https://github.com/thementalcoding/keychron-pro-firmware/blob/main/README.md) · v1.0.1 (build 2026-11-03a) · GPL-2.0

Unofficial build for the **K7 Max** (LKBT51 · SPI), based on
Keychron `wls_2025q1` @ `c8b2b23` plus the Claude audit patch series.

> **Untested on hardware.** This image compiles and passes the automated
> DFU-suffix, CRC, size, manifest and checksum checks, but it has not been
> flashed on this model. Report a result through the hardware-test form.

## Images

| Variant | Keymap | USB PID | File | Tested |
|---|---|---|---|---|
| `ansi/rgb` | `via` | `0x0A70` | [`keychron_k7_max_ansi_rgb_via.bin`](ansi-rgb/keychron_k7_max_ansi_rgb_via.bin) | no |
| `ansi/white` | `via` | `0x0A73` | [`keychron_k7_max_ansi_white_via.bin`](ansi-white/keychron_k7_max_ansi_white_via.bin) | no |
| `iso/rgb` | `via` | `0x0A71` | [`keychron_k7_max_iso_rgb_via.bin`](iso-rgb/keychron_k7_max_iso_rgb_via.bin) | no |
| `iso/white` | `via` | `0x0A74` | [`keychron_k7_max_iso_white_via.bin`](iso-white/keychron_k7_max_iso_white_via.bin) | no |
| `jis/rgb` | `via` | `0x0A72` | [`keychron_k7_max_jis_rgb_via.bin`](jis-rgb/keychron_k7_max_jis_rgb_via.bin) | no |
| `jis/white` | `via` | `0x0A75` | [`keychron_k7_max_jis_white_via.bin`](jis-white/keychron_k7_max_jis_white_via.bin) | no |

## Verify

```bash
cd <extracted folder>
sha256sum -c SHA256SUMS
```

## Flash (Linux / macOS)

1. Back up your keymap (Keychron Engine or VIA JSON export).
2. Power **Off**, hold **Esc**, switch to **Cable** until `0483:df11` appears.
3. Flash the image matching your PID:

```bash
sudo dfu-util -d 0483:df11 -a 0 -s 0x08000000:leave -D \
  firmware/k7_max/ansi-rgb/keychron_k7_max_ansi_rgb_via.bin
```

Windows: QMK Toolbox (STM32 DFU). The STM32 ROM bootloader cannot be
overwritten, so DFU can always be re-entered.
