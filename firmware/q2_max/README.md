# Q2 Max — community QMK firmware

[← All models](https://github.com/thementalcoding/keychron-pro-firmware/blob/main/README.md) · v1.0.1 (build 2026-11-03a) · GPL-2.0

Unofficial build for the **Q2 Max** (LKBT51 · SPI), based on
Keychron `wls_2025q1` @ `c8b2b23` plus the Claude audit patch series.

> **Untested on hardware.** This image compiles and passes the automated
> DFU-suffix, CRC, size, manifest and checksum checks, but it has not been
> flashed on this model. Report a result through the hardware-test form.

## Images

| Variant | Keymap | USB PID | File | Tested |
|---|---|---|---|---|
| `ansi_encoder` | `via` | `0x0820` | [`keychron_q2_max_ansi_encoder_via.bin`](ansi_encoder/keychron_q2_max_ansi_encoder_via.bin) | no |
| `iso_encoder` | `via` | `0x0821` | [`keychron_q2_max_iso_encoder_via.bin`](iso_encoder/keychron_q2_max_iso_encoder_via.bin) | no |

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
  firmware/q2_max/ansi_encoder/keychron_q2_max_ansi_encoder_via.bin
```

Windows: QMK Toolbox (STM32 DFU). The STM32 ROM bootloader cannot be
overwritten, so DFU can always be re-entered.
