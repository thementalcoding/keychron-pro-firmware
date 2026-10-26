# AGENTS.md — instructions for humans and AI agents

This repository publishes **unofficial community QMK firmware** for 26 Keychron
Pro wireless keyboards built around the **CKBT51** Bluetooth module, plus the
audit, patch series and tooling behind it.

If you are an AI agent (or a human) asked to analyse, fix or extend this project,
read this file first, then [`docs/AI_CONTEXT.md`](docs/AI_CONTEXT.md). The
firmware source of truth is [`patches/k13-audit.patch`](patches/k13-audit.patch)
applied to Keychron `wls_2025q1` @ `c8b2b23`; the published binaries are
generated artefacts.

## Non-negotiable rules

1. **One tested unit.** Only the K13 Pro ISO RGB (`firmware/k13_pro/iso-rgb/…`)
   has been flashed on hardware. Never mark another image `tested: true` without
   a matching community report (labelled `tested-ok`) or your own unit test.
2. **Same version = same bytes.** A published version/tag is immutable. New
   content means a new version (`1.0.x-alpha.N` → `-beta.N` → stable).
3. **`firmware/` is generated.** Never hand-edit binaries, per-model READMEs,
   `manifest.json` or `SHA256SUMS`. Regenerate with
   `tools/gen_firmware_docs.py` and let the checks pass.
4. **Never touch the CKBT51 module.** Its firmware is closed and lives in a
   separate MCU; this project only changes the STM32L432 firmware. Module-side
   fixes are Keychron's official updater.
5. **Reliability > latency > battery.** Prefer changes that prevent lost or
   duplicated keystrokes over micro-optimisations.
6. **Hardware-dependent changes are deferred, not guessed.** Anything that
   depends on the closed module's timing/semantics needs a hardware test and
   belongs in the backlog with a note (see `docs/AI_CONTEXT.md` §7).
7. **Scope discipline.** Do not modify LKBT51 boards (`common/wireless/*` with
   the SPI stack); they are a different, unverified protocol.
8. **Privacy.** No MAC addresses, serial numbers, hostnames, user paths or IPs in
   the tree, issues or logs. CI enforces `tools/check_sanitization.py`.
9. **Upstream is separate.** The Keychron PR lives in
   `thementalcoding/qmk_firmware` (branch `k13-pro-bt-fixes`). Never push
   firmware changes to `Keychron/qmk_firmware` directly.
10. **Report the truth.** The original symptom (bursts of repeated keys) is not
    yet confirmed fixed long-term; keep that caveat in user-facing docs.

## Repository map

```
firmware/<model>/<variant>/<binary>.bin   generated images (95)
firmware/<model>/README.md                generated per-model notes
firmware/manifest.json                    generated index (26/95/1)
SHA256SUMS                                generated checksums (repo root)
docs/                                     audit, SDD, recovery, testing, AI context
patches/k13-audit.patch                   source of truth for the MCU changes
patches/notes*.md                         design notes per round/review
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

# rebuild the published tree after changing firmware
python3 tools/gen_firmware_docs.py \
  --builds <build-status dir> --qmk-root <qmk checkout> --out . \
  --tested k13_pro/iso/rgb --version X.Y.Z --build YYYY-MM-DDx

# compile the full matrix (95 variants)
source <repo>/tools/qmk_env.sh
qmk list-keyboards | grep '^keychron/\(k\|q\).*_pro/'
qmk compile -kb keychron/<model>/<variant> -km via
```

## Definition of done for a firmware change

1. Patch applies cleanly on `c8b2b23` (`git apply --check`).
2. All 95 variants compile (`via` keymap wherever it exists).
3. `verify_bins`, `verify_manifest` (26/95/1) and `sha256sum -c` pass.
4. clang-format 19.1.7 clean on touched files.
5. Reviewer pass with concrete verdict; hardware-dependent items explicitly
   deferred with rationale.
6. Binaries regenerated, `manifest.json` / `SHA256SUMS` consistent, docs updated
   in **both** languages for user-visible changes.
7. Tested flags unchanged unless backed by a real report.

## Where to look next

| Question | File |
|---|---|
| Why does the firmware look like this? | [`docs/AI_CONTEXT.md`](docs/AI_CONTEXT.md), [`docs/AUDIT.md`](docs/AUDIT.md), [`docs/SDD.md`](docs/SDD.md) |
| Which models/variants exist? | [`firmware/manifest.json`](firmware/manifest.json), [`docs/ckbt51_boards.csv`](docs/ckbt51_boards.csv) |
| What is still broken/deferred? | [`docs/AI_CONTEXT.md`](docs/AI_CONTEXT.md) §7, [`docs/PER_BOARD_REVIEW.md`](docs/PER_BOARD_REVIEW.md) |
| How do reports and counters work? | [`docs/TESTING.md`](docs/TESTING.md), [`docs/SCHEMAS.md`](docs/SCHEMAS.md) |
| How to recover a keyboard? | [`docs/RECOVERY.md`](docs/RECOVERY.md) |
| Data formats | [`docs/SCHEMAS.md`](docs/SCHEMAS.md) |
