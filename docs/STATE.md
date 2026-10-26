# Project state — v1.0.0 (2026-10-26)

Snapshot for resuming work. User-facing docs live in the README; this file is for
maintainers and AI agents.

## Status

| | |
|---|---|
| Release | **v1.0.0**, tag `3a13cec`, 28 assets (26 model ZIPs + manifest + SHA256SUMS) |
| Repository | https://github.com/thementalcoding/keychron-pro-firmware |
| Release URL | https://github.com/thementalcoding/keychron-pro-firmware/releases/tag/v1.0.0 |
| Upstream PR | https://github.com/Keychron/qmk_firmware/pull/529 — OPEN, MERGEABLE, 6 commits, 33 files |
| Fork | branch `k13-pro-bt-fixes`, head includes `5c5e03f` (q6) and `36dd12e` (q1) |
| Range | 26 CKBT51 models, 95 variants, all `via` |
| Hardware-tested | **1 unit** (K13 Pro ISO RGB) |
| Burst symptom | measured improvement (7→5 ms, ~143→~200 reports/s); long-term confirmation pending |

## Repository history (main)

```
release: v1.0.0 — 26 CKBT51 models, 95 images, bilingual docs, recovery and hardware-test index
chore: drop Python caches and disable scorecard workflow (upstream gcr.io outage)
fix(patch): include final q1_pro name fix and q6_pro factory-reset removal
```

- `v1.0.0` → `3a13cec`.
- `tested-index` branch is generated (`TESTED.md`, `docs/tested.json`).
- `main` protection: `checks` required (strict), linear history, no force-push,
  no deletions, PR not mandatory.
- Scorecard workflow manually disabled (external gcr.io outage).

## Done

- Range audit: 26 CKBT51 boards / 95 variants (LKBT51 analysed, out of scope).
- Link fixes: bounded UART parser, queue flush on `EVT_RECONNECTING`, FIFO-full
  backoff, LPM gate, connect rate limit.
- `report_rate` 90→133 Hz, `reconnect_timeout` 5→60 s on all 26 `*_pro.c`,
  applied on first Bluetooth init (uptime windows removed).
- Per-board review: q6_pro accidental factory reset on Fn+F3 fixed; q1_pro
  quoted Bluetooth name fixed; q1 A9, k11 timeout, q3 overlay deferred to HW.
- 95/95 builds, DFU/CRC/size checks, manifest 26/95/1, checksums.
- Public repo rebuilt (3 commits), organised by model, README/RECOVERY/TESTING
  in EN+ES, issue form, automatic test index and badge.
- Release v1.0.0 with per-model ZIPs; one ZIP verified end to end.
- PR #529 updated to 26 models, 2 extra commits pushed, comment added.

## Pending

1. **Test review**: verify the `Build (QMK)` run triggered by tag `v1.0.0`,
   validate all 28 assets and the 95 binaries, propose test improvements.
2. **Commit AI documentation** (`AGENTS.md`, `docs/AI_CONTEXT.md`,
   `docs/SCHEMAS.md`, `llms.txt`, `.github/copilot-instructions.md`,
   `tools/verify_repo.py`) and add `verify_repo.py` to CI.
3. Apply the test improvements that come out of the review.
4. Wait for Keychron workflow approval + human review on PR #529.
5. Field validation (2–3 days of normal Bluetooth use); if bursts reappear, run
   `tools/bt_tune.sh capture` and check the disconnect reason.
6. Hardware backlog (§ below). Do not touch without a unit.

## Backlog (analysed, not implemented)

R3-02 one-shot param flag · R3-03 clear `bat_empty` · R3-04 debounce mode pin ·
R3-05 event-queue overflow policy · R3-06 `CKBT51_FAST_WAKE` (+measure) ·
R3-07 `usb_remote_wakeup` timeout · R3-08 `reinit_led_drvier` busy-wait ·
R3-09 `HC595_delay` ≥20 ns · R3-10 17th column · R3-11 battery interval ·
R3-12 `rtcGetTime` · R3-14 post-wake state resync.
Board-specific: q1_pro A9 reset-pin polarity · k11_pro 30 s backlight timeout ·
q3_pro `_se` LED overlay on wake.
Details: `docs/PER_BOARD_REVIEW.md`, `docs/AI_CONTEXT.md` §7.

## Fixed decisions

- Reliability > latency > battery.
- Never touch LKBT51 (`common/wireless/`) or the closed CKBT51 module firmware.
- One upstream PR for 26 models (shared code); split only if Keychron asks.
- `firmware/` is generated; same version = same bytes.
- Test index lives on `tested-index`; `main` stays protected.
- `tested: true` requires a real report or maintainer unit test.

## Risks

- Single-unit validation; 94 images never flashed.
- Burst fix not confirmed long-term.
- BT → USB → BT under 500 ms can drop one connect attempt.
- Upstream PR may be rejected or require changes.
- Scorecard disabled due to an external outage.

## Resume commands

```bash
python3 tools/verify_bins.py
python3 tools/verify_manifest.py
python3 tools/verify_repo.py
sha256sum -c SHA256SUMS
python3 tools/check_sanitization.py

# rebuild published tree
python3 tools/gen_firmware_docs.py \
  --builds <build-status> --qmk-root <qmk checkout> --out . \
  --tested k13_pro/iso/rgb --version 1.0.0 --build 2026-10-26c

# upstream
gh pr view 529 -R Keychron/qmk_firmware --json state,title,headRefOid,mergeable,commits
```
