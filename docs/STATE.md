# Project state — v1.0.1 final (updated 2026-11-13)

Snapshot for resuming work. User-facing docs live in the README; this file is for
maintainers, collaborators and AI agents.

## Status

| | |
|---|---|
| Release | **v1.0.1** final, 67 models / 231 images (26 CKBT51 Pro + 41 LKBT51 Max/Version) |
| Previous release | **v1.0.1-beta** (historical folder, removed), build `2026-11-02a`, 26 CKBT51 / 95 images |
| Repository | https://github.com/thementalcoding/keychron-pro-firmware |
| Upstream baseline | `Keychron/qmk_firmware` `wls_2025q1` @ `c8b2b23` |
| Public release | https://github.com/thementalcoding/keychron-pro-firmware/releases/tag/v1.0.1 |
| Hardware-tested | **1 unit** (K13 Pro ISO RGB, PID `0x02D1`), v1.0.1 final, DFU + post-DFU enumeration OK 2026-11-03 |
| Polling test | p10 **6.99 ms**, minimum **5.00 ms**, estimate **~143 reports/s**; consistent with the closed module ceiling of **~133 Hz** |
| Manifest | **67 models / 231 images / 1 tested** |
| Audit inputs | `reports/` (Claude); read-only, not modified |
| Upstream PR | https://github.com/Keychron/qmk_firmware/pull/529 (8 commits, 59 files, head `2618f85`); no maintainer review yet, Keychron's workflows await approval |

## What is applied in v1.0.1 final

- CKBT51: bounded UART parser, incomplete-frame timeout, `ckbt51_rx_idle()` LPM
  gate, OTA RX length validation, report-queue flush on reconnect and host change,
  retry guards for NKRO/consumer, PIN-key direct send, connect rate limit on
  activity, pairing timer moved out of ISR, K13 16-bit shift register output,
  HC595 DS setup delay, Q3 column mask fix, encoder atomicity, q1 reset-pin
  polarity, and P5 USB enumeration wait.
- LKBT51: bounded `lkbt51_read()`, safe `0xAA 0x57` parser, chunked OTA TX, OTA
  RX length validation, queue flush on reconnect/host/suspend, consumer retry
  guard, encoder wake ordering, and the P5 USB enumeration wait.
- Core hooks, opt-in and enabled only by the Keychron wireless makefiles:
  `USB_ENUMERATION_WAIT_MS` (ChibiOS USB init) and
  `ENCODER_QUADRATURE_ATOMIC_READ` (encoder driver). Until 2026-11-13 the encoder
  change was unconditional and broke QMK's encoder unit tests.

Findings and per-ID status: [`CLAUDE_AUDIT.md`](CLAUDE_AUDIT.md).

## Validation

- 231/231 builds, 0 warnings.
- `tools/verify_all.py` (from the project root): sizes, SHA-256 and DFU suffixes
  valid; WB32 raw images intentionally have no DFU suffix.
- `tools/verify_bins.py`, `tools/verify_manifest.py`, `tools/verify_repo.py`,
  `sha256sum -c SHA256SUMS` and `tools/check_sanitization.py` pass.
- K13 Pro ISO RGB flashed; DFU correct, post-DFU enumeration confirmed and keymap
  restored. No other model has been flashed.
- Polling test: p10 6.99 ms, min 5.00 ms; 143/s is the heuristic estimate, not a
  1000 Hz link.
- Host parser tests (`tests/host/`, ASan/UBSan): 9/9 on the patched tree; the
  Keychron base fails 8/9. Run in CI with the polling unit tests.
- PR #529 branch, checked locally on 2026-11-13: `qmk test-c` passes, `qmk lint`
  reports nothing beyond the findings already present on `c8b2b23`, and
  `qmk format-c --core-only` (clang-format 14) requires no changes.
- Reproducibility: QMK embeds `QMK_BUILDDATE` (VIA EEPROM magic; LKBT51 images
  embed the full date and time). Rebuilt with each image's timestamp, all 231
  published images are bit-identical. A plain rebuild changes every SHA-256.

## Pending

1. Hardware validation for the other 230 images; LKBT51 has never been flashed.
2. Field test of the Bluetooth symptoms (chatter, reconnect) over several days.
3. `Q3-02`, `Q3-03` and `LK-08` need schematic/oscilloscope confirmation.
4. Upstream PR #529: Keychron review (maintainer must approve the PR workflows).
5. Dependabot PRs for GitHub Actions remain open (#2 and #3 asked to recreate after the history rewrite); review/merge when convenient.

## Fixed decisions

- Reliability > latency > battery.
- Never modify the closed CKBT51 or LKBT51 module firmware.
- `firmware/` is generated; same version = same bytes.
- `tested: true` requires a real hardware report or maintainer unit test.
- The previous v1.0.1 is labelled `v1.0.1-beta`; the new release is v1.0.1.
- Historical folders were consolidated into the current tree; only
  `Teclado4_obsoleto_2026-11-02` and its audit ZIP remain as archives.

## Resume commands

From the project root (the tree that contains `firmware_qmk/`, `builds_v1.0.1/`,
`tools/` and `release/`):

```bash
python3 tools/build_all.py --skip-build   # refresh manifest without rebuilding
python3 tools/verify_all.py               # 67 models / 231 images
python3 tools/sync_release.py             # refresh release/firmware + README tables
python3 release/tools/verify_manifest.py
python3 release/tools/verify_bins.py
python3 release/tools/verify_repo.py
sha256sum -c release/SHA256SUMS
python3 release/tools/check_sanitization.py
```

Full rebuild (231 variants; needs the bundled toolchain and `.venv-qmk`):

```bash
python3 tools/build_all.py --jobs 6
```

Release assets:

```bash
python3 release/tools/make_release_assets.py --out assets_v1.0.1 --version 1.0.1
```

Polling test:

```bash
sudo python3 release/tools/polling_multikey_v0.0.1.py --list
sudo python3 release/tools/polling_multikey_v0.0.1.py -t 10 -d /dev/input/eventX
```

## Notes for the next agent

- Do not rewrite `reports/`; it is the Claude audit source of truth.
- Check `docs/CLAUDE_AUDIT.md` before proposing a patch: some findings are already
  fixed by v1.0.0/v1.0.1-beta.
- The local source tree is a git repo (`base: v1.0.1 beta`, `v1.0.1 final`,
  `v1.0.1: upstream-review cleanups`) and is identical to the PR #529 branch;
  keep both in sync and regenerate `patches/final-v1.0.1.patch` after a change.
- Commit as `TheMentalCoding <312162298+thementalcoding@users.noreply.github.com>`.
  The history of `main` and the `v1.0.1` tag were rewritten on 2026-11-13 for
  authorship only (same content); `main` is protected against force pushes.
- Code that goes upstream: English comments, no internal references (audit
  names, work-package IDs, release versions, local scripts), commit subjects of
  72 characters or fewer.
- The release tree is a clone of the public repo; commit/push only after the
  verifiers pass.
