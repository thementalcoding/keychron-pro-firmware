#!/usr/bin/env python3
"""Multikey polling-rate test for Keychron (and other) keyboards. v0.0.1.

This is a standalone Linux test. It reads raw `EV_KEY` events from
`/dev/input/eventX`, groups events that arrived in the same read (the same HID
report), and estimates the spacing between reports while you type with several
keys at once.

The result is an estimate, not a USB bus analyzer. A closed Bluetooth module
does not expose its true polling rate; the tool only observes what the kernel
delivers.

Usage:
    sudo python3 tools/polling_multikey_v0.0.1.py --list
    sudo python3 tools/polling_multikey_v0.0.1.py -t 10
    sudo python3 tools/polling_multikey_v0.0.1.py -t 10 -d /dev/input/event19
    sudo python3 tools/polling_multikey_v0.0.1.py -t 10 --json resultado.json
    python3 tools/polling_multikey_v0.0.1.py --self-test
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import select
import statistics
import struct
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone

VERSION = "0.0.1"
PROC_DEVICES = "/proc/bus/input/devices"
EVENT_FMT = struct.Struct("llHHi")  # struct input_event on 64-bit Linux (24 bytes)
EV_KEY = 0x01
EVIOCGNAME = (2 << 30) | (256 << 16) | (0x45 << 8) | 6  # _IOR('E', 0x06, 256)
MAX_GAP_S = 0.150


@dataclass
class Event:
    t: float      # monotonic read time shared by every event in one report
    code: int
    value: int    # 1 = key-down, 0 = key-up


def parse_devices(path: str = PROC_DEVICES) -> list[tuple[str, str]]:
    devices: list[tuple[str, str]] = []
    name: str | None = None
    try:
        with open(path, encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.rstrip("\n")
                if line.startswith("N: Name="):
                    name = line.split('"', 2)[1]
                elif line.startswith("H: Handlers=") and name:
                    for token in line.split("=", 1)[1].split():
                        if token.startswith("event"):
                            devices.append((name, "/dev/input/" + token))
    except OSError as exc:
        raise SystemExit(f"no se puede leer {path}: {exc}") from exc
    return devices


def list_devices(devices: list[tuple[str, str]]) -> None:
    for name, path in devices:
        marker = "  <-- Keychron" if "Keychron" in name else ""
        print(f"{path}  {name}{marker}")


def choose_device(devices: list[tuple[str, str]], explicit: str | None) -> str:
    if explicit:
        return explicit

    keyboards = [(n, d) for n, d in devices if "keyboard" in n.lower()]
    keychrons = [(n, d) for n, d in keyboards if "keychron" in n.lower()]
    if len(keychrons) == 1:
        print(f"Dispositivo autodetectado: {keychrons[0][0]}  [{keychrons[0][1]}]")
        return keychrons[0][1]
    if len(keyboards) == 1:
        print(f"Dispositivo autodetectado: {keyboards[0][0]}  [{keyboards[0][1]}]")
        return keyboards[0][1]

    print("Varios teclados encontrados:")
    for index, (name, path) in enumerate(devices):
        print(f"  [{index}] {name}  ({path})")
    try:
        chosen = int(input("Elige un dispositivo: "))
        return devices[chosen][1]
    except (ValueError, IndexError, EOFError):
        raise SystemExit("selección inválida")


def capture(device: str, seconds: int) -> list[Event]:
    try:
        fd = os.open(device, os.O_RDONLY | os.O_NONBLOCK)
    except PermissionError:
        raise SystemExit(
            "sin permiso para leer " + device + ". Usa sudo o ejecuta:\n"
            "  sudo usermod -aG input $USER   (y vuelve a iniciar sesión)"
        )
    except OSError as exc:
        raise SystemExit(f"no se puede abrir {device}: {exc}") from exc

    try:
        name = fcntl_name(fd)
    except OSError:
        name = device

    print(f"\nDispositivo: {name}  [{device}]")
    print(f"Durante {seconds}s: TECLEA RAPIDO CON VARIAS TECLAS A LA VEZ.")
    print("Mantén 3-5 teclas en juego (acordes/rolls) y suelta rapido. No uses auto-repeat.\n")

    events: list[Event] = []
    poller = select.poll()
    poller.register(fd, select.POLLIN)
    finish = time.monotonic() + seconds
    next_status = time.monotonic()

    while time.monotonic() < finish:
        remaining = finish - time.monotonic()
        if time.monotonic() >= next_status:
            print(f"  ... {max(0, int(remaining))}s restantes, {sum(e.value == 1 for e in events)} pulsaciones", end="\r")
            sys.stdout.flush()
            next_status += 1.0
        if not poller.poll(max(1, int(min(0.5, remaining) * 1000))):
            continue
        try:
            raw = os.read(fd, EVENT_FMT.size * 64)
        except BlockingIOError:
            continue
        read_time = time.monotonic()
        for offset in range(0, len(raw) - EVENT_FMT.size + 1, EVENT_FMT.size):
            _, _, kind, code, value = EVENT_FMT.unpack_from(raw, offset)
            if kind == EV_KEY and value in (0, 1):
                events.append(Event(read_time, code, value))

    os.close(fd)
    print()
    return events


def fcntl_name(fd: int) -> str:
    import fcntl

    raw = fcntl.ioctl(fd, EVIOCGNAME, b"\0" * 256)
    return raw.split(b"\0", 1)[0].decode(errors="replace")


def analyze(events: list[Event]) -> dict:
    downs = [event for event in events if event.value == 1]
    if len(downs) < 10:
        return dict(version=VERSION, status="insufficient", reason="muy pocas pulsaciones capturadas", downs=len(downs))

    batches: list[list[Event]] = []
    current = [downs[0]]
    for event in downs[1:]:
        if event.t == current[-1].t:
            current.append(event)
        else:
            batches.append(current)
            current = [event]
    batches.append(current)

    gaps = sorted(
        later[0].t - earlier[0].t
        for earlier, later in zip(batches, batches[1:])
        if 0 < later[0].t - earlier[0].t < MAX_GAP_S
    )
    if len(gaps) < 5:
        return dict(version=VERSION, status="insufficient", reason="muy pocos informes distintos", downs=len(downs), batches=len(batches))

    floor_sample = gaps[: max(5, len(gaps) // 10)]
    floor = statistics.median(floor_sample)
    duration = events[-1].t - events[0].t
    coalesced = sum(1 for batch in batches if len(batch) > 1)

    if floor <= 0.002:
        classification = "usb_1000hz"
        explanation = "huecos de ~1 ms: enlace USB a 1000 Hz"
    elif floor <= 0.009:
        classification = "bluetooth_133hz"
        explanation = "huecos de ~7-8 ms: Bluetooth en el maximo del modulo (~133 Hz)"
    elif floor <= 0.017:
        classification = "bluetooth_90_125hz"
        explanation = "huecos de ~9-16 ms: Bluetooth limitado a 90-125 Hz"
    else:
        classification = "inconclusive"
        explanation = "los huecos son mayores que el enlace: domina la cadencia humana"

    return dict(
        version=VERSION,
        status="ok",
        classification=classification,
        explanation=explanation,
        downs=len(downs),
        batches=len(batches),
        coalesced=coalesced,
        duration_s=round(duration, 3),
        floor_ms=round(floor * 1000, 2),
        min_ms=round(gaps[0] * 1000, 2),
        estimated_reports_s=round(1 / floor) if floor else 0,
        cadence_s=round(len(downs) / duration, 1) if duration else 0,
        histogram_top=dict(collections.Counter(round(gap * 1000) for gap in gaps).most_common(8)),
    )


def print_result(result: dict) -> None:
    print("======== RESULTADO MULTITE CLA v" + VERSION + " ========")
    if result["status"] != "ok":
        print("Test no concluyente:", result.get("reason", "sin datos"))
        return
    print(f"Pulsaciones             : {result['downs']}  ({result['cadence_s']}/s = tu cadencia)")
    print(f"Duración efectiva       : {result['duration_s']:.2f} s")
    print(f"Informes (lotes)        : {result['batches']}  -> {result['estimated_reports_s']} informes/s estimados")
    print(f"Pulsaciones agrupadas   : {result['coalesced']} lotes con >1 tecla")
    print("Espaciado entre informes:")
    print(f"   p10                   : {result['floor_ms']:7.2f} ms")
    print(f"   mínimo                : {result['min_ms']:7.2f} ms")
    print(f">> {result['explanation']} <<")
    print("\nReferencia: CKBT51 cerrado, maximo documentado 133 Hz (~7,5 ms).")
    print("Multiplos exactos de 8 ms sugieren un tope de 125 Hz; valores de 1-2 ms, USB 1000 Hz.")


def self_test() -> int:
    def synth(interval_s: float, batches: int = 120, per_batch: int = 3) -> list[Event]:
        events: list[Event] = []
        for index in range(batches):
            stamp = 1000.0 + index * interval_s
            for key in range(per_batch):
                events.append(Event(stamp, 4 + key, 1))
                events.append(Event(stamp + 0.050, 4 + key, 0))
        return events

    cases = [
        (0.0075, "bluetooth_133hz"),
        (0.0010, "usb_1000hz"),
        (0.0125, "bluetooth_90_125hz"),
    ]
    for interval, expected in cases:
        result = analyze(synth(interval))
        if result["status"] != "ok" or result["classification"] != expected:
            print(f"FAIL: intervalo {interval * 1000:.1f} ms -> {result}")
            return 1
        print(f"OK: {interval * 1000:.1f} ms -> {result['classification']} ({result['floor_ms']} ms)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Test multitecla de polling rate (v" + VERSION + ").")
    parser.add_argument("-d", "--device", help="ruta del event device, p. ej. /dev/input/event19")
    parser.add_argument("-t", "--tiempo", type=int, default=10, help="segundos de medicion (defecto: 10)")
    parser.add_argument("--list", action="store_true", help="listar dispositivos de entrada")
    parser.add_argument("--json", dest="json_path", help="guardar el resultado en JSON")
    parser.add_argument("--self-test", action="store_true", help="ejecutar pruebas internas sin teclado")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    devices = parse_devices()
    if args.list:
        list_devices(devices)
        return 0

    result = analyze(capture(choose_device(devices, args.device), args.tiempo))
    result["timestamp"] = datetime.now(timezone.utc).isoformat()
    print_result(result)

    if args.json_path:
        with open(args.json_path, "w", encoding="utf-8") as handle:
            json.dump(result, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        print(f"\nResultado guardado en {args.json_path}")

    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
