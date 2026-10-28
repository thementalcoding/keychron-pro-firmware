# AI context — architecture, invariants and backlog

This document is written so an AI agent (or a new maintainer) can understand the
project without re-reading the whole audit. It is deliberately factual and
points to the authoritative files. `AGENTS.md` has the hard rules; this file has
the *why* and the *what*.

## 1. What this project is

- **Hardware**: 26 Keychron *Pro* wireless keyboards (K1–K17 Pro, Q1–Q14 Pro),
  all STM32L432 MCU + **CKBT51** Bluetooth BR/EDR module over UART (460800 baud).
  The module runs **closed firmware**; the MCU runs QMK.
- **Goal**: remove Bluetooth link defects that produce **bursts of repeated
  keystrokes** and silent reconnects, and raise the report rate from 90 Hz to the
  module's documented maximum (133 Hz).
- **Baseline**: Keychron `qmk_firmware`, branch `wls_2025q1`, commit `c8b2b23`.
- **Distribution**: source patch + prebuilt binaries (95 images, 26 models) in
  this repository; upstream proposal in Keychron PR #529.

## 2. Firmware change set (source of truth)

`patches/k13-audit.patch` (33 files, all under `keyboards/keychron/`) contains:

**Shared link layer** (`keyboards/keychron/bluetooth/`)

- `ckbt51.c`
  - UART frame parser bounded: RX buffer `PACKET_MAX_LEN` (64), length accepted
    only in `3..64`; legitimate 42-byte module-info and 42–61-byte OTA frames are
    no longer dropped.
  - `ckbt51_dfu_tx`: first USB packet chunked to `RAW_EPSIZE` (25 data bytes),
    continuation frames `0x03` + ≤31 bytes in a loop; no silent truncation.
- `bluetooth.c`
  - Report buffer is flushed on `EVT_RECONNECTING` as well as disconnect. This is
    the **primary burst fix**: after a lost disconnect event, a stale report
    backlog used to be replayed on reconnect.
  - Event queue overflow policy and retry-timer reset on module FIFO-full ACK
    (no resend storm).
  - `bluetooth_connect()` rate-limited to one attempt per 500 ms (sentinel 0 =
    immediate first connect).
- `report_buffer.c/.h`, `config.h`: supporting state/knobs.
- `lpm.c`: never enter STOP1 while reports, retries or events are pending.

**Per-board init** (26 × `*/​*_pro.c`)

- `ckbt51_param_init()`: `report_rate` 90 → **133**, `reconnect_timeout` 5 → **60 s**.
- The old `sync_timer_read32() < 1000` (and k13_pro's 5000) uptime guard is
  **removed**, so parameters are applied on the first Bluetooth init regardless
  of boot timing. `firstDisconnect && get_port == TRANSPORT_BLUETOOTH`.

**Board-specific fixes (v1.0.0)**

- `q6_pro.c`: removed `ckbt51_factory_reset()` from `case KC_TASK` (Fn+F3 on all
  q6 keymaps wiped pairing/parameters).
- `q1_pro.c`: `STR(PRODUCT)` → `PRODUCT` for the advertised Bluetooth name
  (`:143` dead path and `:212`).

**Explicitly untouched**

- `common/wireless/*` (LKBT51 SPI stack) — different protocol, out of scope.
- Closed CKBT51 module firmware.
- Optional `CKBT51_FAST_WAKE` stays off by default.

## 3. Published artefacts

`firmware/` is **generated**, never hand-edited:

- one folder per model, one subfolder per variant (`iso-rgb`, `ansi-white`, …),
  containing `<keyboard>_<variant>_<keymap>.bin`;
- keymap is `via` for every variant in this release (all 95 have one), so VIA /
  Keychron Engine keeps working;
- `manifest.json` and root `SHA256SUMS` are produced by
  `tools/gen_firmware_docs.py` from a build report (`build-status.json`).

See `docs/SCHEMAS.md` for the exact shapes.

## 4. Verification stack

| Layer | Tool | What it proves |
|---|---|---|
| Binary | `tools/verify_bins.py` | DFU 1.1a suffix (`bcdDFU 0x0100`, `UFD`, len 16, CRC), VID/PID `0483:DF11`, size ≤ 256 KiB |
| Tree | `tools/verify_manifest.py` | every manifest entry exists with matching size/hash, no orphan bins, totals, SHA256SUMS consistency, ≥1 tested |
| Privacy | `tools/check_sanitization.py` | no MACs/hostnames/paths/IPs |
| Docs/tests | `tools/verify_repo.py` | README↔manifest consistency, local links, seed hashes, summary rows |
| Build | `.github/workflows/build.yml` | patch applies on `c8b2b23` and K13 + spot-check compile |
| Upstream | Keychron PR #529 | human review by Keychron maintainers |

Measured on the only hardware-tested unit (K13 Pro ISO RGB, Linux 6.12, AX210):
minimum inter-report gap **7 → 5 ms**, ceiling **~143 → ~200 reports/s**.
Bursts: after several days of daily Bluetooth use, no episodes and typing feels
markedly better; **single unit, so not confirmed long-term**.

## 5. Test-report pipeline

```
issue form (hardware_test.yml)
   -> label hardware-test
   -> tools/hardware_tests.py classify -> tested-ok | tested-problem
   -> regenerate TESTED.md + docs/tested.json
   -> push to the `tested-index` branch (main stays protected)
   -> README badge (shields endpoint) reads the branch's JSON
```

Only reports with model + variant + 64-hex SHA-256 are counted. The maintainer
seed (`docs/tested-seed.json`) is merged in. `tested: true` in the manifest must
correspond to a real report/unit test.

## 6. Design decisions and their reasons

| Decision | Reason |
|---|---|
| Flush queue on `EVT_RECONNECTING`, not just disconnect | Root cause of burst replays; disconnect events can be lost |
| 500 ms connect rate limit | Stops reconnect storms from slider/power toggles; one lost attempt in <500 ms toggles is documented |
| LPM gate on pending work | STOP1 with a pending UART transaction dropped reports |
| `report_rate` 133 Hz | Documented module maximum; measured +40 % ceiling |
| `reconnect_timeout` 60 s | 5 s gave up during normal host sleep/resume |
| Parameters on first BT init, no uptime window | Slow module boot / late switch to BT left factory defaults |
| Untested images still published, clearly marked | Whole range benefits, but testing is community-driven; warnings everywhere |
| Index on `tested-index` branch | `main` is protected; avoids giving the bot write bypass |
| One upstream PR for 26 models | Shared code; per-model PRs would duplicate hunks and be rejected |

## 7. Backlog — analysed, not implemented

Hardware-dependent items must be validated on a unit before shipping.

| ID | Item | Where | Risk | Notes |
|---|---|---|---|---|
| R3-02 | One-shot flag for `param_init` instead of uptime window | `*_pro.c` | Low | Window already removed; flag would re-send on later reconnects |
| R3-03 | Clear `bat_empty` when voltage recovers | `bluetooth/battery.c` | Low | LEDs stuck until USB otherwise |
| R3-04 | Debounce the Cable/BT mode pin | `*_pro.c` | Low | Slider bounce triggers multiple transport switches |
| R3-05 | Event-queue overflow policy | `bluetooth/bluetooth.c` | Low | Dropping oldest may lose DISCONNECTED/RECONNECTING |
| R3-06 | `CKBT51_FAST_WAKE` on + measure | `bluetooth/ckbt51.c` | Medium | ~3 ms per command; needs HW |
| R3-07 | `usb_remote_wakeup()` timeout | `bluetooth/transport.c` | Medium | Host may ignore remote wake |
| R3-08 | `reinit_led_drvier()` busy-wait 100 ms | `bluetooth/transport.c` | Low | Freezes scan/UART on transport change |
| R3-09 | `HC595_delay(1)` ≈12.5 ns < 20 ns spec | board `matrix.c` | Low | Harden to 2–3 nops |
| R3-10 | 17th column shift on `uint16_t` | `k13_pro/matrix.c` | Low | Phantom column after boot/wake |
| R3-11 | Battery measure interval 3 s | `bluetooth/battery.h` | Low | Each measure = blocking UART |
| R3-12 | `rtcGetTime` every loop | `bluetooth/rtc_timer.c` | None | Gate with timer |
| R3-14 | Re-sync state with module after wake | `bluetooth/ckbt51.c` | Medium | Needs vendor register semantics |
| PB-03 | q1_pro `CKBT51_RESET_PIN` (A9) LOW at boot | `q1_pro.c/config.h` | Unknown | Polarity unconfirmed; **hardware test only** |
| PB-06 | k11_pro backlight timeout 30 s vs 600 s | `k11_pro` | Low | Vendor choice; leave |
| PB-05 | q3_pro `_se` LED overlay rearmed on wake | `q3_pro/matrix.c` | Low | 3 s repeat per wake; leave |

Full detail: `docs/PER_BOARD_REVIEW.md`, `docs/AUDIT.md`, `docs/SDD.md`.

## 8. Known limitations

- Single-unit hardware validation (K13 Pro ISO RGB only).
- BT → USB → BT toggles under 500 ms can suppress one connect attempt.
- Module parameters are sent on the first BT init after power-on, not per reconnect.
- Some variants have no `via` keymap upstream (none in this release).
- Radio-level issues (interference, adapter power saving) are outside this firmware.

## 9. How to extend (for an AI agent)

1. Read `AGENTS.md` rules; check `git status` is clean.
2. Change **source**, not `firmware/`.
3. Fix one concern per commit; keep upstream style; clang-format 19.1.7.
4. Rebuild affected variants + the K13/K14/Q1 spot checks; if a release is
   intended, rebuild all 95.
5. Regenerate `firmware/manifest.json`, `SHA256SUMS`, per-model READMEs with
   `gen_firmware_docs.py`; run all verifiers.
6. Update `docs/AI_CONTEXT.md` §7 if you implement or add a backlog item.
7. Hardware-dependent? Stop, write it in the backlog with the test procedure.
8. Open a PR against **this** repository (not Keychron) unless the change is
   upstream-ready and the maintainer asked for an upstream PR.

## 10. Glossary

- **CKBT51**: Keychron Bluetooth BR/EDR module (closed firmware, UART control).
- **LKBT51**: different Keychron wireless stack (SPI); out of scope.
- **VIA**: keymap protocol used by VIA and Keychron Engine.
- **DFU**: STM32 ROM bootloader at `0483:DF11`; cannot be erased.
- **HC595**: shift-register column driver on most Pro boards; microsecond-scale
  timing and glitch sensitivity.
- **LPM/STOP1**: low-power MCU state; entering it with pending work loses reports.
