# Claude audit — findings and status in v1.0.1 final

Source: `Teclado5/reports/` (Claude). The report files were read-only and were
not modified while preparing this release.

## Summary

| Severity | Count |
|---|---:|
| P0 | 2 |
| P1 | 9 |
| P2 | 6 |
| P3 | 12 |
| Informational / discarded | 4 |

Total with ID: **33** (29 real findings plus 2 observations, 1 discard and the
LKBT51 DFU route). Scope: **67 products / 231 variants** (26 CKBT51 Pro +
41 LKBT51 Max/Version).

## Findings

| ID | Severity | Finding | Status in v1.0.1 final | Patch |
|---|---|---|---|---|
| CK-BT01 | P0 | CKBT51 UART parser without bounds/reset; stack overflow and permanent lock | Fixed; timeout and `ckbt51_rx_idle()` added | 01 |
| CK-LPM01 | P1 | STOP1 with a half-parsed frame or pending report | Fixed; LPM gate checks parser and retry | 03 |
| BT-02 | P1 | Report queue not flushed on reconnect | Fixed; unconditional flush | 04 |
| BT-03 | P1 | Old host reports follow a host change | Fixed; flush on `connect_ex` | 05 |
| BT-04 | P1 | Module parameters only applied if first DISCONNECTED arrives under 1 s | Already fixed in v1.0.0 (`1d66356`) | — |
| BT-05 | P1 | NKRO/consumer reports advance the retry and leave a key pressed | Fixed; direct paths wait for retry 0 | 06 |
| BT-06 | P2 | PIN keys queue but are not sent before CONNECTED | Fixed; direct send while pairing | 07 |
| BT-07 | P2 | Pairing timer calls the UART driver from ISR | Fixed; work moved to task | 11 |
| BT-08 | P3 | Every report during RECONNECTING re-sends CONNECT | Fixed; activity connect is rate-limited | 08 |
| CK-OTA01 | P2 | OTA path without bounds | Fixed; TX chunked, RX minimum/length checked | 02 |
| Q6-01 | P1 | Q6 Pro Fn+F3 calls `ckbt51_factory_reset()` | Already fixed in v1.0.0 (`5c5e03f`) | — |
| Q1-01 | P2 | Q1 Pro Bluetooth name includes quotes | Already fixed in v1.0.0 (`36dd12e`) | — |
| Q1-02 | P2 | Q1 Pro reset pin A9 low at boot | Fixed; pin released high (pending HW check) | 14 |
| Q1-03 | P3 | Third parameter block is dead code | Informational; no binary change | — |
| DFU-01 | P1 | First USB enumeration after DFU (`-71`) | Fixed and hardware-confirmed on K13 Pro ISO RGB (P5, 500 ms) | 09/P5 |
| MTX-01 | P3 | K13 shifts 17 bits in a 16-bit chain | Fixed; 16 bits | 15 |
| MTX-02 | P3 | No DS setup time before SHCP in 74HC595 | Fixed; setup delay added | 16 |
| ENC-01 | P3 | Encoder ISR/task race on shared state | Fixed; atomic block | 18 |
| Q3-01 | P3 | Q3 mask `(7 << 0)` selects all columns | Fixed; inverted mask | 17 |
| Q3-02 | P3 | Q3 16-column map uses a 19-bit layout | Deferred; needs schematic/HW | — |
| Q3-03 | P3 | Q3 EXTI4 shared between encoder and row | Deferred; low impact | — |
| OBS-01 | P3 | 30 retries every 7 ms (~217 ms per report) | Design behaviour; documented | — |
| OBS-02 | — | `connected_idle_timeout=7200 s`, `reconnect_timeout=5 s` | Informational | — |
| BOARD-01 | — | Generic settle/atomicity finding | Discarded as formulated; replaced by MTX-01/MTX-02 | — |
| DFU-01L | P3 | LKBT51 shares the post-DFU USB route | P5 wait extended defensively; no HW evidence | 09/P5 |
| LK-01 | P0 | `lkbt51_read()` exchanges 68 bytes in 64-byte buffers | Fixed | 19 |
| LK-02 | P1 | LKBT51 parser out-of-range and permanent lock | Fixed | 20 |
| LK-03 | P2 | LKBT51 OTA path without bounds | Fixed; TX chunked, RX bounded | 21 |
| LK-04 | P1 | LKBT51 queue not flushed on reconnect/host/suspend | Fixed | 22 |
| LK-05 | P3 | LKBT51 consumer path ignores retry | Fixed | 23 |
| LK-06 | P3 | `encoder_cb_init()` before mode EXTI disable on wake | Fixed | 24 |
| LK-07 | P3 | 1 s `firstDisconnect` window | Mitigated by `EVT_RESET`; no patch | — |
| LK-08 | P3 | k0_max mode-pin EXTI shares row lines | Deferred; needs HW | — |

## Validation

- 231/231 builds, 0 warnings.
- Manifest: 67 models / 231 images / 1 tested.
- K13 Pro ISO RGB (`0x02D1`, sha256 `de9bbdc9…fe0c`) flashed on hardware;
  DFU correct and post-DFU enumeration confirmed 2026-11-03.
- Pending: polling-rate measurement and hardware reports for the other models.