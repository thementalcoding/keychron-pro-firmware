# AI context — architecture, invariants and backlog

For an AI agent or new maintainer. `AGENTS.md` has the hard rules, `STATE.md`
the current status, `CLAUDE_AUDIT.md` the per-finding status. This file has the
*what* and the *why*. Older process records are in `history/`.

## 1. What this project is

- **Hardware:** 67 Keychron wireless products. 26 *Pro* boards (K1–K17 Pro,
  Q1–Q14 Pro) use an STM32L432 plus the **CKBT51** Bluetooth module over UART
  (460800 baud). 41 *Max*/*Version* boards use the **LKBT51** module over SPI.
  Both modules run **closed firmware**; the MCU runs QMK.
- **Goal:** remove link defects that caused **bursts of repeated keystrokes**,
  freezes and silent reconnects, and raise the CKBT51 report rate from 90 Hz to
  the module maximum (133 Hz).
- **Baseline:** Keychron `qmk_firmware`, branch `wls_2025q1`, commit `c8b2b23`.
- **Distribution:** source patch plus 231 prebuilt images in this repository;
  upstream proposal in Keychron PR #529.

## 2. Firmware change set

Source of truth: `patches/final-v1.0.1.patch`, the diff from `c8b2b23` to the
PR #529 branch (59 files). Per-ID detail: `CLAUDE_AUDIT.md`.

**CKBT51** (`keyboards/keychron/bluetooth/` + per-board files)

- UART parser bounded (length `3..64`), incomplete-frame timeout and
  `ckbt51_rx_idle()`; OTA TX chunked and RX length-checked.
- Report queue flushed on `EVT_RECONNECTING` and on host change: the **primary
  burst fix** (a stale backlog was replayed after a lost disconnect event).
- LPM: never enter STOP1 with a half-parsed frame, pending reports, retries or
  events.
- Retry guards for NKRO/consumer; PIN keys sent directly while pairing;
  `bluetooth_connect()` rate-limited to one attempt per 500 ms; pairing timer
  work moved out of the ISR.
- `ckbt51_param_init()`: `report_rate` 90 → **133**, `reconnect_timeout` 5 →
  **60 s**, applied on the first Bluetooth init (no uptime window).
- Board fixes: K13 16-bit shift register output, HC595 DS→SHCP setup delay, Q3
  column mask, q6_pro Fn+F3 factory reset removed, q1_pro BT name quoting and
  reset-pin level (polarity unconfirmed).

**LKBT51** (`keyboards/keychron/common/wireless/`)

- `lkbt51_read()` bounded (was 68 bytes into 64-byte buffers), `0xAA 0x57`
  parser validated, OTA TX chunked / RX bounded, queue flush on
  reconnect/host/suspend, consumer retry guard, encoder wake ordering.

**Core hooks** (opt-in; only the Keychron wireless makefiles enable them)

- `USB_ENUMERATION_WAIT_MS=500` (`tmk_core/protocol/chibios/chibios.c`): fixes
  the first USB enumeration after DFU (`-71`). Hardware-confirmed on K13 Pro.
- `ENCODER_QUADRATURE_ATOMIC_READ` (`drivers/encoder/encoder_quadrature.c`):
  the encoder pins are also read from a pin ISR.

Not touched: the closed module firmware. `CKBT51_FAST_WAKE` stays off.

## 3. Published artefacts

`firmware/` is **generated** (`tools/gen_firmware_docs.py`): one folder per
model, one subfolder per variant, `<keyboard>_<variant>_via.bin`, plus
`manifest.json` and root `SHA256SUMS`. Shapes: `SCHEMAS.md`. QMK embeds
`QMK_BUILDDATE` (VIA EEPROM magic; LKBT51 also the full time), so a rebuild only
matches bit for bit when built with the original timestamp.

## 4. Verification stack

| Layer | Tool | What it proves |
|---|---|---|
| Binary | `tools/verify_bins.py` | DFU 1.1a suffix, CRC, VID/PID `0483:DF11`, size; WB32 raw images exempt |
| Tree | `tools/verify_manifest.py` | manifest ↔ files ↔ `SHA256SUMS`, totals 67/231, ≥1 tested |
| Privacy | `tools/check_sanitization.py` | no MACs/hostnames/paths/IPs |
| Docs | `tools/verify_repo.py` | README ↔ manifest, local links, seed hashes |
| Build | `.github/workflows/build.yml` | patch applies on `c8b2b23`; K13 + spot-check compile |
| Parser | `tests/host/run_host_tests.sh` | CKBT51/LKBT51 parsers under ASan/UBSan: 9/9 patched, 8/9 fail on `c8b2b23` |
| Polling tool | `tests/test_polling_multikey.py` | parser and batching logic |
| Upstream | `qmk test-c`, `qmk lint`, `qmk format-c` (clang-format 14) on the PR branch | what Keychron's PR workflows will run once approved |

Field evidence (single unit, K13 Pro ISO RGB, v1.0.1 final): about 10 days of
daily Bluetooth use to 2026-11-13 with no freezes or bursts. Polling p10
~7 ms, consistent with the 133 Hz module ceiling. The old "5 ms / ~200
reports/s" figure was a multi-key artefact and is withdrawn.

## 5. Test-report pipeline

```
issue form (hardware_test.yml) -> label hardware-test
  -> tools/hardware_tests.py classify -> tested-ok | tested-problem
  -> TESTED.md + docs/tested.json on branch `tested-index` (main stays protected)
  -> README badge (shields endpoint)
```

Only reports with model + variant + 64-hex SHA-256 count. `docs/tested-seed.json`
holds the maintainer unit.

## 6. Design decisions

| Decision | Reason |
|---|---|
| Flush queue on `EVT_RECONNECTING`, not only on disconnect | Root cause of burst replays; disconnect events can be lost |
| 500 ms connect rate limit | Stops reconnect storms; a BT→USB→BT toggle under 500 ms can lose one attempt |
| LPM gate on pending work | STOP1 with a pending UART transaction dropped reports |
| 133 Hz / 60 s reconnect | Module maximum; 5 s gave up during normal host sleep |
| Parameters on first BT init | Slow module boot left factory defaults |
| Core changes behind opt-in macros | Keeps QMK's other boards and unit tests unchanged |
| Untested images published, clearly marked | Whole range benefits; testing is community-driven |
| One upstream PR | Shared code; per-model PRs would duplicate hunks |

## 7. Backlog — analysed, not implemented

Hardware-dependent items need a unit before shipping. Per-board detail:
`history/PER_BOARD_REVIEW.md`.

| ID | Item | Where | Risk | Notes |
|---|---|---|---|---|
| Q1-02 | q1_pro module reset pin (A9) level | `q1_pro` | Unknown | Now released high; polarity unconfirmed, **hardware/schematic only** |
| Q3-02 | Q3 16-column map uses a 19-bit layout | `q3_pro` | Low | Needs schematic |
| Q3-03 | Q3 EXTI4 shared between encoder and row | `q3_pro` | Low | Needs hardware |
| LK-08 | k0_max mode-pin EXTI shares row lines | `k0_max` | Low | Needs hardware |
| R3-03 | Clear `bat_empty` when voltage recovers | `bluetooth/battery.c` | Low | LEDs stuck until USB otherwise |
| R3-04 | Debounce the Cable/BT mode pin | `*_pro.c` | Low | Slider bounce → several transport switches |
| R3-05 | Event-queue overflow policy | `bluetooth/bluetooth.c` | Low | Dropping oldest may lose DISCONNECTED/RECONNECTING |
| R3-06 | `CKBT51_FAST_WAKE` on + measure | `bluetooth/ckbt51.c` | Medium | ~3 ms per command; needs HW |
| R3-07 | `usb_remote_wakeup()` timeout | `bluetooth/transport.c` | Medium | Host may ignore remote wake |
| R3-08 | `reinit_led_drvier()` busy-waits 100 ms | `bluetooth/transport.c` | Low | Freezes scan/UART on transport change |
| R3-11 | Battery measured every 3 s | `bluetooth/battery.h` | Low | Each measure is a blocking UART exchange |
| R3-12 | `rtcGetTime` every loop | `bluetooth/rtc_timer.c` | None | Gate with a timer |
| R3-14 | Re-sync state with module after wake | `bluetooth/ckbt51.c` | Medium | Needs vendor register semantics |
| PB-05 | q3_pro `_se` LED overlay rearmed on wake | `q3_pro/matrix.c` | Low | Vendor behaviour; leave |
| PB-06 | k11_pro backlight timeout 30 s vs 600 s | `k11_pro` | Low | Vendor choice; leave |

Done since v1.0.0 (removed from this list): R3-02 (uptime window), R3-09
(HC595 setup, MTX-02), R3-10 (17th column shift, MTX-01), PB-03 (q1 reset pin,
now Q1-02).

## 8. Known limitations

- Single-unit hardware validation (K13 Pro ISO RGB).
- Module parameters are sent on the first BT init after power-on, not per
  reconnect.
- Radio-level issues (interference, adapter power saving) are outside this
  firmware.

## 9. How to extend

1. Read `AGENTS.md`; `git status` clean.
2. Change source (the PR branch), never `firmware/`. One concern per commit.
3. Run the upstream checks (§4) and the host tests.
4. Rebuild: affected variants for review, all 231 for a release (new version).
5. Regenerate `firmware/`, `manifest.json`, `SHA256SUMS` and
   `patches/final-v1.0.1.patch` (or the new version's patch); run all verifiers.
6. Hardware-dependent? Do not guess: add it to §7 with a test procedure.
