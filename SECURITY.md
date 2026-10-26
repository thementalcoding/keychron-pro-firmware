# Security Policy

## Supported versions

| Version | Supported          |
|---------|--------------------|
| v1.0.x  | :white_check_mark: |

Only the firmware binaries published in this repository (`v1.0.0` and later
`v1.0.x` builds) and the scripts in `tools/` are in scope.

## Reporting a vulnerability

**Please do not open a public issue for security problems.**

Use GitHub's private vulnerability reporting: open the **Security** tab of this
repository and click **Report a vulnerability**. This opens a private advisory
visible only to the maintainers, and it is the only supported contact channel
(there is no security email address for this project).

Please include the affected version and the SHA-256 of the binary, your host
environment (OS/kernel, toolchain), reproduction steps, and the impact you
expect.

## Scope

In scope:

- The MCU firmware changes in `patches/k13-audit.patch` (Bluetooth link
  handling, report queue, low-power gating, report rate).
- The `tools/` scripts: flashing helper, DFU suffix wrapper, polling
  measurement.
- Repository infrastructure and the published binaries.

Out of scope (not treated as vulnerabilities here):

- The **CKBT51 Bluetooth module firmware**: it is closed and cannot be modified
  by this project (see README, "Known limitations").
- **Bricking** concerns: the STM32 ROM bootloader cannot be overwritten and DFU
  recovery is always available (see README, "Flashing").
- Behaviour documented as a known limitation in the README, for example
  switching BT → USB → BT in under 500 ms, or module parameters being applied
  at the first Bluetooth init per boot.
- Issues in upstream QMK firmware or Keychron's own tree that are not
  introduced by this patch set — please report those upstream.

## What the published artifacts contain

The `.bin` files are plain MCU flash images with a standard DFU 1.1a suffix.
They contain no keys, credentials, or personal data. This repository is
published from a sanitized private working tree: MAC addresses, hostnames, user
paths and LAN/tunnel addresses are removed, and the CI job
`tools/check_sanitization.py` fails the build if any of those patterns reappear.

## Disclosure policy

We follow coordinated disclosure with a **90-day** deadline: we acknowledge a
report within 7 days, aim to ship a fix or mitigation within 90 days, and
publish an advisory once a fixed release is available (or at the end of the
90-day window, whichever comes first). Credit is given in the advisory unless
you ask otherwise.
