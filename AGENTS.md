# AGENTS.md — instructions for humans and AI agents

This repository publishes **unofficial community QMK firmware** for 67 Keychron
wireless products: 26 Pro keyboards built around the **CKBT51** UART module and
41 Max/Version keyboards built around the **LKBT51** SPI module, plus the audit,
patch series and tooling behind it.

If you are an AI agent (or a human) asked to analyse, fix or extend this project,
read this file first, then [`docs/STATE.md`](docs/STATE.md) and, if needed,
[`docs/AI_CONTEXT.md`](docs/AI_CONTEXT.md). The firmware source of truth is
[`patches/final-v1.0.1.patch`](patches/final-v1.0.1.patch) applied to Keychron
`wls_2025q1` @ `c8b2b23` (identical to the Keychron PR #529 branch); the
published binaries are generated artefacts. `docs/history/` is background only.

## Non-negotiable rules

1. **One tested unit.** Only the K13 Pro ISO RGB (`firmware/k13_pro/iso-rgb/…`)
   has been flashed on hardware. Never mark another image `tested: true` without
   a matching community report (labelled `tested-ok`) or your own unit test.
2. **Same version = same bytes.** A published version/tag is immutable. New
   content means a new version (`1.0.x-alpha.N` → `-beta.N` → stable).
3. **`firmware/` is generated.** Never hand-edit binaries, per-model READMEs,
   `manifest.json` or `SHA256SUMS`. Regenerate with
   `tools/gen_firmware_docs.py` and let the checks pass.
4. **Never touch the CKBT51/LKBT51 module.** Its firmware is closed and runs on
   a separate chip; this project only changes the keyboard MCU firmware.
   Module-side fixes come from Keychron's official updater.
5. **Reliability > latency > battery.** Prefer changes that prevent lost or
   duplicated keystrokes over micro-optimisations.
6. **Hardware-dependent changes are deferred, not guessed.** Anything that
   depends on the closed module's timing/semantics needs a hardware test and
   belongs in the backlog with a note (see `docs/AI_CONTEXT.md` §7).
7. **Scope discipline.** LKBT51 boards use a different SPI stack. The v1.0.1
   fixes are applied there, but no LKBT51 board has been flashed; keep that
   caveat in user-facing docs.
8. **Privacy.** No MAC addresses, serial numbers, hostnames, user paths or IPs in
   the tree, issues or logs. CI enforces `tools/check_sanitization.py`.
9. **Upstream is separate.** The Keychron PR lives in
   `thementalcoding/qmk_firmware` (branch `k13-pro-bt-fixes`). Never push
   firmware changes to `Keychron/qmk_firmware` directly.
10. **Report the truth.** The tested unit has run without freezes or key bursts
    in daily use since 2026-11-03, but that is one unit; do not claim the fix is
    confirmed for the range.

## Repository map

```
firmware/<model>/<variant>/<binary>.bin   generated images (231)
firmware/<model>/README.md                generated per-model notes
firmware/manifest.json                    generated index (67/231/1 tested)
SHA256SUMS                                generated checksums (repo root)
docs/                                     state, AI context, audit status, recovery, testing
docs/history/                             v1.0.0 audit, SDD and review records (background)
patches/final-v1.0.1.patch                source of truth for the MCU changes (= PR #529)
patches/claude-v1.0.1.patch               beta → final diff
patches/k13-audit.patch                   v1.0.0 patch, kept for reference
tests/host/                               parser tests (ASan/UBSan)
tools/                                    build, verify, report and flash helpers
.github/workflows/                        CI, upstream build check, test index
.github/ISSUE_TEMPLATE/hardware_test.yml  the "report a test" button
```

## Commands

```bash
# verify everything (what CI runs)
python3 tools/verify_bins.py
python3 tools/verify_manifest.py
sha256sum -c SHA256SUMS
python3 tools/check_sanitization.py
python3 tools/verify_repo.py
bash tests/host/run_host_tests.sh <patched qmk tree>

# rebuild the published tree after changing firmware
python3 tools/gen_firmware_docs.py \
  --builds <build-status dir> --qmk-root <qmk checkout> --out . \
  --tested k13_pro/iso/rgb --version X.Y.Z --build YYYY-MM-DDx

# compile the full matrix (231 variants)
source <repo>/tools/qmk_env.sh
qmk list-keyboards | grep -E '^keychron/[kqv][0-9]+_(pro|max|version_[0-9]+)/'
qmk compile -kb keychron/<model>/<variant> -km via
```

## Definition of done for a firmware change

1. Patch applies cleanly on `c8b2b23` (`git apply --check`); host tests pass.
2. All 231 variants compile (`via` keymap wherever it exists).
3. `verify_bins`, `verify_manifest` (67/231/1) and `sha256sum -c` pass.
4. QMK checks clean on the PR branch: `qmk format-c --core-only` (clang-format
   14), `qmk lint` (no new findings vs `c8b2b23`), `qmk test-c`.
5. Reviewer pass with concrete verdict; hardware-dependent items explicitly
   deferred with rationale.
6. Binaries regenerated, `manifest.json` / `SHA256SUMS` consistent, docs updated
   in **both** languages for user-visible changes.
7. Tested flags unchanged unless backed by a real report.

## Where to look next

| Question | File |
|---|---|
| Current status and pending work | [`docs/STATE.md`](docs/STATE.md) |
| Why does the firmware look like this? | [`docs/AI_CONTEXT.md`](docs/AI_CONTEXT.md), [`docs/CLAUDE_AUDIT.md`](docs/CLAUDE_AUDIT.md), [`docs/history/`](docs/history/README.md) |
| Which models/variants exist? | [`firmware/manifest.json`](firmware/manifest.json), [`docs/ckbt51_boards.csv`](docs/ckbt51_boards.csv) |
| What is still broken/deferred? | [`docs/AI_CONTEXT.md`](docs/AI_CONTEXT.md) §7 |
| How do reports and counters work? | [`docs/TESTING.md`](docs/TESTING.md), [`docs/SCHEMAS.md`](docs/SCHEMAS.md) |
| How to recover a keyboard? | [`docs/RECOVERY.md`](docs/RECOVERY.md) |
| Data formats | [`docs/SCHEMAS.md`](docs/SCHEMAS.md) |
