# GitHub Copilot instructions

Read [`AGENTS.md`](../AGENTS.md) and [`docs/AI_CONTEXT.md`](../docs/AI_CONTEXT.md)
before suggesting changes.

Key points:

- `firmware/` is **generated** (`tools/gen_firmware_docs.py`); never edit binaries,
  `manifest.json`, `SHA256SUMS` or per-model READMEs by hand.
- Only the K13 Pro ISO RGB has been hardware-tested. Never set `tested: true`
  without a real report (`tested-ok`) or maintainer unit test.
- Same version = same bytes. New content requires a new version.
- The CKBT51 module firmware is closed: do not attempt to patch it here.
- Reliability > latency > battery. Hardware-dependent changes go to the backlog.
- Verify with `tools/verify_bins.py`, `tools/verify_manifest.py`,
  `sha256sum -c SHA256SUMS`, `tools/check_sanitization.py` and, after adding docs,
  `tools/verify_repo.py`.
- Do not add personal data (MACs, hostnames, paths, IPs) anywhere; CI checks it.
