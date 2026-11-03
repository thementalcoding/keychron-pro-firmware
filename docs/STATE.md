# Project state — v1.0.1 final (2026-11-03)

Snapshot for resuming work. User-facing docs live in the README; this file is for
maintainers and AI agents.

## Status

| | |
|---|---|
| Release | **v1.0.1** final, 67 models / 231 images (26 CKBT51 Pro + 41 LKBT51 Max/Version) |
| Previous release | **v1.0.1-beta**, Teclado2, build `2026-11-02a`, 26 CKBT51 / 95 images |
| Repository | https://github.com/thementalcoding/keychron-pro-firmware |
| Upstream baseline | `Keychron/qmk_firmware` `wls_2025q1` @ `c8b2b23` |
| Hardware-tested | **1 unit** (K13 Pro ISO RGB), validated against the previous beta bytes |
| Final images | All marked `tested: false`; revalidation required |
| Audit inputs | `Teclado5/reports/` (Claude); these files are read-only and were not modified |

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

## Validation

- Manifest: **67 models / 231 images / 0 tested**.
- `tools/verify_all.py`: all sizes, SHA-256 and DFU suffixes valid (WB32 raw
  images intentionally have no DFU suffix).
- `tools/verify_manifest.py`, `tools/verify_bins.py`, `tools/verify_repo.py` and
  `sha256sum -c SHA256SUMS` pass.
- No hardware flashing was performed in this phase.

## Pending

1. Flash and validate the final K13 ISO RGB image (or a per-model image) on a
   physical unit.
2. Run the host parser harness against the final tree.
3. Upstream PR #529: human review and workflow approval.
4. Hardware backlog remains for timing/regression checks.

## Fixed decisions

- Reliability > latency > battery.
- Never modify the closed CKBT51 or LKBT51 module firmware.
- `firmware/` is generated; same version = same bytes.
- `tested: true` requires a real hardware report or maintainer unit test.
- The previous v1.0.1 is labelled `v1.0.1-beta`; the new release is v1.0.1.

## Resume commands

```bash
python3 tools/verify_all.py
python3 tools/verify_bins.py
python3 tools/verify_manifest.py
python3 tools/verify_repo.py
sha256sum -c SHA256SUMS
python3 tools/check_sanitization.py

# compile the full matrix (231 variants)
source <repo>/tools/qmk_env.sh
python3 tools/build_all.py --jobs 6

# package release assets
python3 tools/make_release_assets.py --out <assets> --version 1.0.1
```