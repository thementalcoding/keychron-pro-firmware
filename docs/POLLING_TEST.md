# Multikey polling-rate test — v0.0.1

Standalone Linux test to estimate the spacing between keyboard reports over
Bluetooth or USB. No third-party packages are required.

## What it measures

The script reads raw `EV_KEY` events from `/dev/input/eventX`. Events read in the
same system call are treated as one HID report; the gaps between those reports
estimate the link interval.

This is an observation tool, not a USB analyzer. The CKBT51/LKBT51 module is
closed and does not expose a true polling-rate register.

## Requirements

- Linux (x86_64) with `evdev` input devices.
- Python 3.10 or newer.
- Read permission on `/dev/input/eventX`: use `sudo` or add your user to the
  `input` group.
- A keyboard connected by cable or Bluetooth.

## List devices

```bash
sudo python3 tools/polling_multikey_v0.0.1.py --list
```

Look for a line such as:

```text
/dev/input/event19  Keychron K13 Pro Keyboard  <-- Keychron
```

Do not use the `... Mouse` or `... Consumer Control` device for this test.

## Run

```bash
sudo python3 tools/polling_multikey_v0.0.1.py -t 10 -d /dev/input/event19
```

During the whole test, **press several keys at the same time** (3-5 keys in
chords or fast rolls) and release them quickly. Do not use auto-repeat. A
multikey workload makes the report batching visible.

Save the result for a PR or issue:

```bash
sudo python3 tools/polling_multikey_v0.0.1.py -t 10 --json polling.json
```

Run the internal checks without a keyboard:

```bash
python3 tools/polling_multikey_v0.0.1.py --self-test
```

## Reading the result

| Observation | Meaning |
|---|---|
| p10 ≈ 1-2 ms | USB link running at ~1000 Hz |
| p10 ≈ 7-8 ms | Bluetooth at the module ceiling (~133 Hz) |
| p10 ≈ 9-16 ms | Bluetooth limited to ~90-125 Hz |
| Gaps in exact multiples of 8 ms | 125 Hz cap |
| Larger, irregular gaps | Human cadence dominates; repeat faster |

Example from the maintainer K13 Pro ISO RGB (Bluetooth):

```text
Pulsaciones             : 298  (33/s de media = tu cadencia)
Duración efectiva       : 9.10 s
Informes (lotes)        : 292  -> 32 informes/s
Pulsaciones agrupadas   : 6 lotes con >1 tecla
Espaciado mínimo entre informes (suelo del enlace):
   p10 de gaps <150ms  :    6.99 ms
   mínimo              :    5.00 ms
>> INTERVALO de enlace estimado: ~7.0 ms (techo ~143 informes/s) <<
```

The nominal module ceiling is 133 Hz (~7.5 ms). The 143/s figure is the
heuristic estimate and includes scheduling noise; it is not a 1000 Hz link.

## Before/after protocol

1. Run the test on the stock firmware, over Bluetooth, same host, same device.
2. Flash v1.0.1 final.
3. Run the same test again with the same multikey pattern.
4. Report `p10`, minimum, and estimated reports/s in the hardware-test issue.

The project's main reliability findings are documented in
[CLAUDE_AUDIT.md](CLAUDE_AUDIT.md).
