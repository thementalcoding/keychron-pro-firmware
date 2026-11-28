# Project state (updated 2026-11-13)

Short snapshot for maintainers and AI agents. Rules and commands are in
[`../AGENTS.md`](../AGENTS.md); architecture and the code backlog are in
[`AI_CONTEXT.md`](AI_CONTEXT.md); per-finding status is in
[`CLAUDE_AUDIT.md`](CLAUDE_AUDIT.md); the past is in [`history/`](history/).

## Status

| | |
|---|---|
| Release | **v1.0.1** final, build `2026-11-03a`: 67 models / 231 images (26 CKBT51 Pro / 95 + 41 LKBT51 Max/Version / 136) |
| Source of truth | [`patches/final-v1.0.1.patch`](../patches/final-v1.0.1.patch) on Keychron `wls_2025q1` @ `c8b2b23` (= PR #529 branch) |
| Hardware-tested | **1 unit**, K13 Pro ISO RGB (`0x02D1`): flashed 2026-11-03, DFU and post-DFU enumeration OK |
| Field use | Same unit, about 10 days of daily Bluetooth use (to 2026-11-13): **no freezes and no key bursts**, which the stock firmware showed. Single unit |
| Polling | p10 6.99 ms, min 5.00 ms; module ceiling ~133 Hz |
| Reproducibility | All 231 images rebuild bit-identical with their embedded `QMK_BUILDDATE` |
| Upstream | [Keychron PR #529](https://github.com/Keychron/qmk_firmware/pull/529), head `2618f85`, 8 commits; awaiting maintainer review (its workflows need maintainer approval). `qmk test-c`, `qmk lint` (no new findings) and `qmk format-c` pass locally |

## Pending

1. Hardware reports for the other 230 images; LKBT51 has never been flashed.
2. Keychron review of PR #529.
3. Schematic/oscilloscope checks: q1_pro module reset pin polarity, `Q3-02`,
   `Q3-03`, `LK-08`.
4. Dependabot updates for GitHub Actions (review when convenient).

## Fixed decisions

- Reliability > latency > battery.
- Never modify the closed CKBT51/LKBT51 module firmware.
- Same version = same bytes; `firmware/` is generated.
- `tested: true` only with a real hardware report.
- Stay on `wls_2025q1`; Keychron's newer `2025q3` branch does not contain the
  CKBT51 Pro boards.
- Commits are authored as `TheMentalCoding`; upstream-bound code uses English
  comments, no internal references and commit subjects of 72 characters or fewer.
