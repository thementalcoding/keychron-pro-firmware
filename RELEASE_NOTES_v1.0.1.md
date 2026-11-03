# v1.0.1 final — CKBT51 + LKBT51

Build `2026-11-03a` · baseline `Keychron/qmk_firmware` `wls_2025q1` @ `c8b2b23`.

## Scope

- **67 products / 231 images**
  - 26 CKBT51 Pro models: 95 images.
  - 41 LKBT51 Max/Version models: 136 images.
- Previous local release renamed to **v1.0.1-beta** (historical folder, build `2026-11-02a`,
  26 CKBT51 models / 95 images).

## Applied

CKBT51:
- `01-CK-BT01`: bounded parser, incomplete-frame timeout, `ckbt51_rx_idle()`.
- `02-CK-OTA01`: OTA RX minimum/length validation.
- `03-CK-LPM01`: LPM gate checks parser idle and pending retry.
- `04-BT-02`, `05-BT-03`: queue flush on reconnect and host change.
- `06-BT-05`, `07-BT-06`, `08-BT-08`: retry guards, PIN direct send, connect rate limit.
- `11-BT-07`: pairing timer moved out of the ISR.
- `14-Q1-02`: q1_pro reset pin released high.
- `15-MTX-01`, `16-MTX-02`: K13 16-bit shift output and HC595 DS setup delay.
- `17-Q3-01`: Q3 column mask fix.
- `18-ENC-01`: encoder ISR/task atomicity.
- P5: `USB_ENUMERATION_WAIT_MS=500` retained for all CKBT51.

LKBT51:
- `19-LK-01`: bounded `lkbt51_read()`.
- `20-LK-02`: safe `0xAA 0x57` parser.
- `21-LK-03`: chunked OTA TX and OTA RX bounds.
- `22-LK-04`: queue flush on reconnect/host/suspend.
- `23-LK-05`: consumer retry guard.
- `24-LK-06`: encoder init after mode-pin EXTI handling.
- P5: same 500 ms USB enumeration wait applied to the SPI family.

## Not applied

- `09-DFU-01`: superseded by the P5 wait already present in the beta tree; the
  project keeps the 500 ms value for all CKBT51 and now LKBT51.
- `10-BT-04`, `12-Q6-01`, `13-Q1-01`: already fixed by the v1.0.0/v1.0.1-beta
  commits.
- `LK-07`, `LK-08`: analysed, no patch proposed.

## Verification

- 231/231 builds, 0 warnings.
- Manifest: 67 models / 231 images / 1 tested.
- `verify_bins.py`: 231/231 binary size, SHA-256 and DFU suffix checks pass
  (WB32F3G71 raw images intentionally have no DFU suffix).
- `verify_manifest.py`, `verify_repo.py`, `sha256sum -c SHA256SUMS` and
  `check_sanitization.py` pass.
- **K13 Pro ISO RGB (`0x02D1`) flashed with the v1.0.1 final bytes**; DFU was
  correct and post-DFU enumeration confirmed on 2026-11-03. The keymap was
  restored and works as before. The remaining 230 images have no hardware
  report yet.

## DFU

The MCU waits 500 ms after USB init before RGB/BT/keyboard init. On the K13 Pro
ISO RGB this removed the first-boot-after-DFU enumeration failure and is now
confirmed with the final v1.0.1 bytes. For the other models and for LKBT51 this
remains a defensive change pending hardware confirmation. The ROM bootloader
remains recoverable by DFU on STM32 boards.
