## Summary

Hardening of the Bluetooth link code for both Keychron wireless families, on
top of `wls_2025q1`:

- **CKBT51 (26 Pro models / 95 images):** bounded UART parser with an
  incomplete-frame timeout, low-power gate while the UART is busy, bounded OTA
  RX, report-queue flush on reconnect/host change, retry guards, direct PIN-key
  send, connect rate limit, pairing timer work moved out of ISR context,
  K13/Q3 matrix fixes, q6_pro Fn+F3 factory-reset removal, q1_pro quoted name.
- **LKBT51 (41 Max/Version models / 136 images):** bounded `lkbt51_read()`,
  validated `0xAA 0x57` parser length, chunked OTA TX and bounded OTA RX,
  report-queue flush on reconnect/host change/suspend, consumer retry guard,
  encoder wake ordering.
- **Core (opt-in, no effect on other boards):**
  - `tmk_core/protocol/chibios/chibios.c`: `USB_ENUMERATION_WAIT_MS` may
    override the 50 ms wait after USB init; the Keychron wireless makefiles set
    500 ms so the host finishes enumeration after a DFU flash.
  - `drivers/encoder/encoder_quadrature.c`: `ENCODER_QUADRATURE_ATOMIC_READ`
    makes the polled read atomic for boards that also read the encoder from a
    pin interrupt (`encoder_quadrature_handle_inerrupt_read()`); enabled by the
    Keychron wireless makefiles only.

No JSON, PID or layout changes.

## Why

The original symptom on a K13 Pro was bursts of repeated keystrokes and silent
reconnects after idle. Reviewing the link code found, among others:

- CKBT51: a frame header with a length larger than the 32-byte buffer
  overflowed the stack and then locked the parser permanently.
- LKBT51: `lkbt51_read()` exchanged up to 68 bytes into 64-byte buffers.

Full findings, severity and per-finding status:
https://github.com/thementalcoding/keychron-pro-firmware/blob/main/docs/CLAUDE_AUDIT.md

## Commits

Split by area so they can be reviewed or cherry-picked separately:

1. `bluetooth: harden CKBT51 UART parser, report queue and LPM`
2. `keychron: set CKBT51 report rate to 133 Hz and reconnect timeout to 60 s`
3. `k13_pro: apply module parameters within 5 s of boot`
4. `keychron: apply CKBT51 module parameters on first Bluetooth init`
5. `keychron: remove accidental CKBT51 factory reset from q6_pro Fn+F3`
6. `keychron: fix quoted Bluetooth name on q1_pro`
7. `bluetooth: bound CKBT51 frames and flush stale reports on reconnect`
8. `wireless: bound LKBT51 reads and flush stale reports on reconnect`

## Testing

Run locally on this branch (the repository's own PR workflows are waiting for
maintainer approval):

- **`qmk test-c`:** passes (exit 0), including all 7 encoder test suites.
- **`qmk lint`** on the 26 touched boards: no new findings; the output is
  identical to the base commit `c8b2b23`.
- **`qmk format-c --core-only` / `format-text`** (clang-format 14, as in
  `format.yml`): no changes required.
- **Builds:** 231/231 variants (26 CKBT51 + 41 LKBT51 models) with
  `arm-none-eabi-gcc` 14.2, 0 warnings.
- **Host parser tests** (ASan/UBSan, fake UART/SPI transport, oversized /
  truncated / malformed frames, STOP1 mid-frame): 9/9 pass on this branch; the
  base commit fails 8/9.
  https://github.com/thementalcoding/keychron-pro-firmware/tree/main/tests/host
- **Hardware:** K13 Pro ISO RGB (`0x02D1`) flashed, DFU and post-DFU
  enumeration confirmed without a power cycle, keymap restored.
  Multikey polling: p10 6.99 ms, minimum 5.00 ms, consistent with the CKBT51
  module ceiling of ~133 Hz.
- **Not yet tested on hardware:** the other CKBT51 models and every LKBT51
  model.

Prebuilt images and checksums for all 231 variants:
https://github.com/thementalcoding/keychron-pro-firmware/releases/tag/v1.0.1

## Notes for review

- The CKBT51/LKBT51 module firmware is closed and untouched; only the MCU side
  changes.
- The 500 ms USB wait is a delay after USB init, not a reset.
- `q1_pro`: the CKBT51 reset pin is now driven high like on the other CKBT51
  boards; this has not been checked against the q1_pro schematic.
