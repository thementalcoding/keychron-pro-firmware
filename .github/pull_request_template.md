## Summary

<!-- What changes, and why. Link the issue/discussion if there is one. -->

> Main project areas: CKBT51/LKBT51 Bluetooth link reliability, post-DFU USB
> enumeration, report-queue flushes, OTA bounds, encoder/matrix timing, and the
> documented Claude audit findings in `docs/CLAUDE_AUDIT.md`.

## Testing

- Keyboard variant(s) and USB PID tested:
- Builds (check all that apply):
  - [ ] keychron/k13_pro ansi/rgb
  - [ ] keychron/k13_pro ansi/white
  - [ ] keychron/k13_pro iso/rgb (`-km default` and `-km via`)
  - [ ] keychron/k13_pro iso/white
  - [ ] keychron/k14_pro ansi/rgb (shared-code spot check)
- Multikey polling test v0.0.1 (`sudo python3 tools/polling_multikey_v0.0.1.py -t 10 -d /dev/input/eventX`):
  - before: __ ms p10 / __ reports/s est.
  - after: __ ms p10 / __ reports/s est.
  - link: USB / Bluetooth
- Optional tap test (`sudo python3 tools/medir_polling.py -m tap -t 10`):
  - before: __ ms floor
  - after: __ ms floor

## Checklist

- [ ] `python3 tools/verify_bins.py` passes
- [ ] `sha256sum -c SHA256SUMS` passes
- [ ] `firmware/manifest.json` updated if binaries changed
- [ ] `patches/final-v1.0.1.patch` regenerated if source changed
- [ ] `python3 -m unittest discover -s tests` passes
- [ ] No personal data (MACs, hostnames, user paths, LAN/tunnel IPs) — CI privacy guard is green
- [ ] README / docs updated for user-visible changes
- [ ] Contribution is licensed under GPL-2.0 (inbound = outbound)
