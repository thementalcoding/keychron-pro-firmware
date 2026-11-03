# Q1 Pro — community QMK firmware

[← All models](https://github.com/thementalcoding/keychron-pro-firmware/blob/main/README.md) · v1.0.1 (build 2026-11-03a) · GPL-2.0

Unofficial build for the **Q1 Pro** (CKBT51 · UART), based on
Keychron `wls_2025q1` @ `c8b2b23` plus the Claude audit patch series.

> **Untested on hardware.** This image compiles and passes the automated
> DFU-suffix, CRC, size, manifest and checksum checks, but it has not been
> flashed on this model. Report a result through the hardware-test form.

## Images

| Variant | Keymap | USB PID | File | Tested |
|---|---|---|---|---|
| `ansi_knob` | `via` | `0x0610` | [`keychron_q1_pro_ansi_knob_via.bin`](ansi_knob/keychron_q1_pro_ansi_knob_via.bin) | no |
| `iso_knob` | `via` | `0x0611` | [`keychron_q1_pro_iso_knob_via.bin`](iso_knob/keychron_q1_pro_iso_knob_via.bin) | no |
| `jis_encoder` | `via` | `0xA612` | [`keychron_q1_pro_jis_encoder_via.bin`](jis_encoder/keychron_q1_pro_jis_encoder_via.bin) | no |

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
  firmware/q1_pro/ansi_knob/keychron_q1_pro_ansi_knob_via.bin
```

Windows: QMK Toolbox (STM32 DFU). The STM32 ROM bootloader cannot be
overwritten, so DFU can always be re-entered.
