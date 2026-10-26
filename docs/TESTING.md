# Hardware test reports

**English** · [Español](TESTING.es.md)

This project ships 95 images for 26 keyboards, but only **one unit** (K13 Pro ISO
RGB) has been tested on real hardware. Community reports are the only way to know
which models actually work, so reporting is deliberately a one-click flow.

## Report in 30 seconds

1. Click **[Report a hardware test](https://github.com/thementalcoding/keychron-pro-firmware/issues/new?template=hardware_test.yml)**
   (also linked from the README and from every model folder).
2. Pick your model, paste the firmware file name and its SHA-256, choose the
   result and press **Submit**.
3. That's it. The issue is public; you can add details later.

Get the SHA-256 of the file you flashed:

```bash
sha256sum firmware/<model>/<variant>/<file>.bin
# or, on Windows (PowerShell):
Get-FileHash .\<file>.bin -Algorithm SHA256
```

Do **not** paste MAC addresses, serial numbers, hostnames or personal paths.

## What happens after you submit

```
Issue form  ──►  label hardware-test
                     │
                     ├─ Result = Works      ──►  label tested-ok
                     └─ Result = Problems   ──►  label tested-problem
                                                      │
                              TESTED.md + tested.json rebuilt automatically
                                (published on the tested-index branch)
```

- Reporting is **not** a vote: a report is counted only if it includes the model,
  variant and SHA-256 of the binary.
- `tested-ok` means "this exact binary booted and was usable for at least a short
  session". It does not mean the model is fully validated.
- A maintainer may ask for details, or re-label an issue if the SHA does not match
  a published build.
- The badge and counters in the README are generated from `docs/tested.json` on
  the [`tested-index` branch](https://github.com/thementalcoding/keychron-pro-firmware/blob/tested-index/TESTED.md),
  which the [`tested-index`](../.github/workflows/tested-index.yml) workflow
  rebuilds from the labelled issues plus the maintainer's own test
  ([`docs/tested-seed.json`](tested-seed.json)). `main` stays protected: the
  generated files are published on their own branch, never pushed directly.

## Labels

| Label | Meaning |
|---|---|
| `hardware-test` | Any issue created from the test form |
| `tested-ok` | Binary flashed and keyboard usable |
| `tested-problem` | Binary flashed but something is wrong |
| `bug` | Firmware/tooling defect confirmed by a maintainer |

You can also browse the raw list:
[issues labelled `tested-ok`](https://github.com/thementalcoding/keychron-pro-firmware/issues?q=label%3Atested-ok).

## Good reports

A useful report includes:

- exact model, variant and PID (`lsusb | grep 3434`),
- the firmware **file name and SHA-256** (identifies the build),
- host OS and Bluetooth adapter (Linux: `lsusb`/`lspci`; macOS: About this Mac;
  Windows: Device Manager),
- whether it was tested over USB, Bluetooth or both,
- what you did (basic typing, VIA keymap edit, sleep/wake, reconnect, RGB),
- for problems: what happened, how often, and whether it also happens on stock
  firmware.

## For maintainers

Everything is automated; the only manual action is reviewing a report if its SHA
does not match a published build.

```bash
# Rebuild the index locally (needs gh auth with read access)
GITHUB_REPOSITORY=thementalcoding/keychron-pro-firmware \
  python3 tools/hardware_tests.py index

# Re-evaluate labels for one issue
GITHUB_REPOSITORY=thementalcoding/keychron-pro-firmware \
  python3 tools/hardware_tests.py label 123
```

The index workflow publishes the regenerated files to the `tested-index` branch
(force-pushed by the bot) because `main` is protected. The README badge and link
point there.
