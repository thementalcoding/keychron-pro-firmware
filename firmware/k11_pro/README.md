# K11 Pro — community QMK firmware

[← All models](../../README.md) · v1.0.0 (build 2026-10-26c) · GPL-2.0

Unofficial build for the **K11 Pro** (STM32L432 + CKBT51 Bluetooth module), based on
Keychron `wls_2025q1` @ `c8b2b23`. Fixes Bluetooth link robustness and raises the
report rate to 133 Hz. Read the [main README](../../README.md) and the
[recovery guide](../../docs/RECOVERY.md) before flashing.

> ⚠️ **Untested on hardware.** This model compiles and passes all automated
> checks (DFU suffix, CRC, size, manifest), but has not been flashed on a
> device. Report your result with the
> [hardware-test form](https://github.com/thementalcoding/keychron-pro-firmware/issues/new?template=hardware_test.yml).

## Images

| Variant | Keymap | USB PID | File | Tested |
|---|---|---|---|---|
| ansi/rgb | `via` | `0x02B0` | [`keychron_k11_pro_ansi_rgb_via.bin`](ansi-rgb/keychron_k11_pro_ansi_rgb_via.bin) | ⚠️ no |
| ansi/white | `via` | `0x02B3` | [`keychron_k11_pro_ansi_white_via.bin`](ansi-white/keychron_k11_pro_ansi_white_via.bin) | ⚠️ no |
| ansi_encoder/rgb | `via` | `0x02B6` | [`keychron_k11_pro_ansi_encoder_rgb_via.bin`](ansi_encoder-rgb/keychron_k11_pro_ansi_encoder_rgb_via.bin) | ⚠️ no |
| ansi_encoder/white | `via` | `0x02B9` | [`keychron_k11_pro_ansi_encoder_white_via.bin`](ansi_encoder-white/keychron_k11_pro_ansi_encoder_white_via.bin) | ⚠️ no |

`_via` images keep VIA / Keychron Engine keymap support. `_default` images do not
speak VIA. Verify the download with `sha256sum -c SHA256SUMS` from the repository
root.

## Flash (Linux / macOS)

1. Back up your keymap (Keychron Engine or VIA JSON export).
2. Power **Off**, hold **Esc**, switch to **Cable** → `lsusb` shows `0483:df11`.
3. Flash:

```bash
sudo dfu-util -d 0483:df11 -a 0 -s 0x08000000:leave -D \
  firmware/k11_pro/ansi-rgb/keychron_k11_pro_ansi_rgb_via.bin
```

Replace the path with the image for your PID. Windows: use QMK Toolbox.

## Identify your PID

| Variant | PID |
|---|---|
| ansi/rgb | `0x02B0` |
| ansi/white | `0x02B3` |
| ansi_encoder/rgb | `0x02B6` |
| ansi_encoder/white | `0x02B9` |

If your PID is not listed, do not flash this model folder — open an issue.
