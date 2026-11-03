# keychron: harden CKBT51/LKBT51 links and fix the Claude audit findings

## Summary

This PR now covers the **v1.0.1 final** hardening for both Keychron wireless
families:

- **CKBT51 (26 Pro models / 95 images):** parser bounds and incomplete-frame
  timeout, LPM gate, OTA RX bounds, report-queue flushes, retry guards,
  PIN-key direct send, connect rate limit, pairing timer moved out of ISR,
  K13/Q3 matrix fixes, encoder atomicity, q1 reset-pin polarity, and the
  500 ms post-DFU USB enumeration wait.
- **LKBT51 (41 Max/Version models / 136 images):** bounded `lkbt51_read()`,
  safe `0xAA 0x57` parser, chunked OTA TX and bounded OTA RX, queue flushes on
  reconnect/host/suspend, consumer retry guard, encoder wake ordering, and the
  same post-DFU USB wait.

The two new commits are deliberately split by module:

1. `ckbt51: v1.0.1 link hardening and Claude audit fixes` — 53 files.
2. `lkbt51: bound read/parser/OTA and flush report queues` — 4 files.

The earlier six commits in this PR (v1.0.0: parser/queue/LPM/rate-limit,
module parameters, q6 Fn+F3, q1 name) are unchanged.

## Why

The original K13 Pro symptom was bursts of repeated keystrokes and silent
reconnects after idle. The Claude audit then found additional defects, including
two P0 issues:

- CKBT51 parser overflow/permanent lock on oversized frames.
- LKBT51 `lkbt51_read()` exchanging 68 bytes in 64-byte buffers.

Full findings, severity and per-finding status:
https://github.com/thementalcoding/keychron-pro-firmware/blob/main/docs/CLAUDE_AUDIT.md

## Scope

- CKBT51: `keyboards/keychron/bluetooth/`, `keyboards/keychron/*_pro/`,
  `keyboards/keychron/common/matrix.c`, encoder driver, ChibiOS USB wait.
- LKBT51: `keyboards/keychron/common/wireless/`.
- No JSON/PID/layout changes.

## Build evidence

- **231/231 variants** (26 CKBT51 + 41 LKBT51) built from the final tree with
  QMK CLI and `arm-gcc 14.2`, **0 warnings**.
- Every image passed DFU-suffix, VID/PID, size, CRC, manifest and checksum
  checks; WB32F3G71 images are raw by design.
- Community release: https://github.com/thementalcoding/keychron-pro-firmware/releases/tag/v1.0.1

## Hardware testing

- **K13 Pro ISO RGB (`0x02D1`)**: flashed with the v1.0.1 final bytes. DFU
  correct and **post-DFU enumeration confirmed** without a power cycle; keymap
  restored and working.
- Multikey polling test: p10 **6.99 ms**, minimum **5.00 ms**, consistent with
  the closed module ceiling of **~133 Hz**. It is not a 1000 Hz USB result.
- No other model has been flashed. LKBT51 has no hardware validation yet.

## Review notes

- The CKBT51 and LKBT51 stacks are independent; the commits are split so they
  can be reviewed or cherry-picked separately.
- The CKBT51 module firmware is closed and untouched. Only the STM32/QMK side
  changes.
- The 500 ms wait is a defensive delay after USB init, not a forced reset.

## Checklist

- [x] 231/231 variants compile, 0 warnings
- [x] DFU/CRC/size/manifest/checksum checks pass
- [x] K13 Pro ISO RGB hardware flash + post-DFU enumeration
- [x] Changes limited to `keyboards/keychron/**`, the encoder driver and the
      ChibiOS USB init path
- [ ] Hardware validation on the remaining models
