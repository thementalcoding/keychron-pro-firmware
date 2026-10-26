# K13 Pro — community QMK firmware

[← All models](../../README.md) · v1.0.0 (build 2026-10-26c) · GPL-2.0

Unofficial build for the **K13 Pro** (STM32L432 + CKBT51 Bluetooth module), based on
Keychron `wls_2025q1` @ `c8b2b23`. Fixes Bluetooth link robustness and raises the
report rate to 133 Hz. Read the [main README](../../README.md) and the
[recovery guide](../../docs/RECOVERY.md) before flashing.

> ✅ **Hardware-tested:** 1 variant(s) of this model were flashed on a physical unit. See [TESTED](https://github.com/thementalcoding/keychron-pro-firmware/blob/tested-index/TESTED.md).
> The other variants of this model are **untested builds**.

## Images

| Variant | Keymap | USB PID | File | Tested |
|---|---|---|---|---|
| ansi/rgb | `via` | `0x02D0` | [`keychron_k13_pro_ansi_rgb_via.bin`](ansi-rgb/keychron_k13_pro_ansi_rgb_via.bin) | ⚠️ no |
| ansi/white | `via` | `0x02D3` | [`keychron_k13_pro_ansi_white_via.bin`](ansi-white/keychron_k13_pro_ansi_white_via.bin) | ⚠️ no |
| iso/rgb | `via` | `0x02D1` | [`keychron_k13_pro_iso_rgb_via.bin`](iso-rgb/keychron_k13_pro_iso_rgb_via.bin) | ✅ yes (1 unit) |
| iso/white | `via` | `0x02D4` | [`keychron_k13_pro_iso_white_via.bin`](iso-white/keychron_k13_pro_iso_white_via.bin) | ⚠️ no |

`_via` images keep VIA / Keychron Engine keymap support. `_default` images do not
speak VIA. Verify the download with `sha256sum -c SHA256SUMS` from the repository
root.

## Flash (Linux / macOS)

1. Back up your keymap (Keychron Engine or VIA JSON export).
2. Power **Off**, hold **Esc**, switch to **Cable** → `lsusb` shows `0483:df11`.
3. Flash:

```bash
sudo dfu-util -d 0483:df11 -a 0 -s 0x08000000:leave -D \
  firmware/k13_pro/ansi-rgb/keychron_k13_pro_ansi_rgb_via.bin
```

Replace the path with the image for your PID. Windows: use QMK Toolbox.

## Identify your PID

| Variant | PID |
|---|---|
| ansi/rgb | `0x02D0` |
| ansi/white | `0x02D3` |
| iso/rgb | `0x02D1` |
| iso/white | `0x02D4` |

If your PID is not listed, do not flash this model folder — open an issue.
