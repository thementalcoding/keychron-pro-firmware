## Summary

<!-- What changes, and why. Link the issue/discussion if there is one. -->

## Testing

- Keyboard variant(s) and USB PID tested:
- Builds (check all that apply):
  - [ ] keychron/k13_pro ansi/rgb
  - [ ] keychron/k13_pro ansi/white
  - [ ] keychron/k13_pro iso/rgb (`-km default` and `-km via`)
  - [ ] keychron/k13_pro iso/white
  - [ ] keychron/k14_pro ansi/rgb (shared-code spot check)
- Tap test (`sudo python3 tools/medir_polling.py -m tap -t 10`):
  - before: __ ms floor / __ reports/s
  - after: __ ms floor / __ reports/s

## Checklist

- [ ] `python3 tools/verify_bins.py` passes
- [ ] `cd firmware && sha256sum -c SHA256SUMS` passes
- [ ] `firmware/SHA256SUMS` updated if binaries changed
- [ ] `patches/k13-audit.patch` regenerated if source changed
- [ ] No personal data (MACs, hostnames, user paths, LAN/tunnel IPs) — CI privacy guard is green
- [ ] README / docs updated for user-visible changes
- [ ] Contribution is licensed under GPL-2.0 (inbound = outbound)
