# K11 Pro — community QMK firmware

[← All models](https://github.com/thementalcoding/keychron-pro-firmware/blob/main/README.md) · v1.0.1 (build 2026-11-03a) · GPL-2.0

Unofficial build for the **K11 Pro** (CKBT51 · UART), based on
Keychron `wls_2025q1` @ `c8b2b23` plus the Claude audit patch series.

> **Untested on hardware.** This image compiles and passes the automated
> DFU-suffix, CRC, size, manifest and checksum checks, but it has not been
> flashed on this model. Report a result through the hardware-test form.

## Images

| Variant | Keymap | USB PID | File | Tested |
|---|---|---|---|---|
| `ansi/rgb` | `via` | `0x02B0` | [`keychron_k11_pro_ansi_rgb_via.bin`](ansi-rgb/keychron_k11_pro_ansi_rgb_via.bin) | no |
| `ansi/white` | `via` | `0x02B3` | [`keychron_k11_pro_ansi_white_via.bin`](ansi-white/keychron_k11_pro_ansi_white_via.bin) | no |
| `ansi_encoder/rgb` | `via` | `0x02B6` | [`keychron_k11_pro_ansi_encoder_rgb_via.bin`](ansi_encoder-rgb/keychron_k11_pro_ansi_encoder_rgb_via.bin) | no |
| `ansi_encoder/white` | `via` | `0x02B9` | [`keychron_k11_pro_ansi_encoder_white_via.bin`](ansi_encoder-white/keychron_k11_pro_ansi_encoder_white_via.bin) | no |

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
  firmware/k11_pro/ansi-rgb/keychron_k11_pro_ansi_rgb_via.bin
```

Windows: QMK Toolbox (STM32 DFU). The STM32 ROM bootloader cannot be
overwritten, so DFU can always be re-entered.
