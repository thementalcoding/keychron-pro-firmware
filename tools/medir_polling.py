#!/usr/bin/env python3
"""Mide el polling rate efectivo del Keychron K13 Pro (o cualquier teclado).

Lee eventos crudos de /dev/input/eventX y calcula estadísticas de
intervalos entre eventos de tecla mientras mantienes una tecla pulsada
(o tecleas rápido).

Uso:
    sudo python3 medir_polling.py                # autodetecta el Keychron
    sudo python3 medir_polling.py --list         # lista teclados disponibles
    sudo python3 medir_polling.py -d /dev/input/event20 -t 10
    python3 medir_polling.py                     # si estás en el grupo input
"""

import argparse
import fcntl
import os
import select
import statistics
import struct
import sys
import time

PROC_DEVICES = "/proc/bus/input/devices"
EVENT_FMT = struct.Struct("llHHi")  # struct input_event en x86_64 (24 bytes)
EV_KEY = 0x01
EVIOCGNAME = (2 << 30) | (256 << 16) | (0x45 << 8) | 6  # _IOR('E', 0x06, 256)


def listar_teclados(filtro=""):
    """Devuelve [(nombre, event_dev)] parseando /proc/bus/input/devices."""
    resultado = []
    nombre = None
    with open(PROC_DEVICES, encoding="utf-8") as f:
        for linea in f:
            linea = linea.rstrip("\n")
            if linea.startswith("N: Name="):
                nombre = linea.split('"')[1]
            elif linea.startswith("H: Handlers=") and nombre:
                handlers = linea.split("=", 1)[1].split()
                ev = next((h for h in handlers if h.startswith("event")), None)
                if ev:
                    resultado.append((nombre, f"/dev/input/{ev}"))
                nombre = None
    if filtro:
        resultado = [(n, d) for n, d in resultado if filtro.lower() in n.lower()]
    return resultado


def elegir_dispositivo():
    candidatos = listar_teclados("Keychron")
    teclados = [(n, d) for n, d in listar_teclados("key") if "Keychron" in n] or candidatos
    if not teclados:
        teclados = candidatos or listar_teclados()
    if not teclados:
        sys.exit("No se encontró ningún dispositivo de teclado.")
    if len(teclados) > 1:
        solo_teclas = [(n, d) for n, d in teclados if "keyboard" in n.lower()]
        if solo_teclas:
            teclados = solo_teclas
    if len(teclados) == 1:
        return teclados[0]
    print("Varios teclados encontrados:")
    for i, (n, d) in enumerate(teclados):
        print(f"  [{i}] {n}  ({d})")
    idx = int(input("Elige [0]: ") or 0)
    return teclados[idx]


def nombre_dispositivo(fd):
    try:
        bruto = fcntl.ioctl(fd, EVIOCGNAME, b"\0" * 256)
        return bruto.split(b"\0")[0].decode(errors="replace")
    except OSError:
        return "desconocido"


def medir(dev_path, segundos):
    try:
        fd = os.open(dev_path, os.O_RDONLY | os.O_NONBLOCK)
    except PermissionError:
        sys.exit("Sin permiso para leer " + dev_path + ". Ejecuta con sudo o añádete al grupo input:\n"
                 "  sudo usermod -aG input $USER  (y vuelve a iniciar sesión)")
    except FileNotFoundError:
        sys.exit(f"No existe {dev_path}")

    print(f"\nDispositivo: {nombre_dispositivo(fd)}  [{dev_path}]")
    print(f"Medición durante {segundos}s: TECLEA RÁPIDO con varias teclas a la vez")
    print("(cuantas más teclas pulsadas en el mismo instante, mejor se mide el enlace)...\n")

    marcas = []        # timestamps de key-down
    pares = []         # (down, up) por tecla, para latencia
    teclas_abajo = {}
    pulsaciones = 0
    fin = time.monotonic() + segundos
    fd_num = fd
    poller = select.poll()
    poller.register(fd_num, select.POLLIN)

    ultimo_aviso = time.monotonic()
    while time.monotonic() < fin:
        restante = fin - time.monotonic()
        if time.monotonic() - ultimo_aviso >= 1.0:
            print(f"  ... {int(restante)}s restantes, {len(marcas)} pulsaciones", end="\r", flush=True)
            ultimo_aviso = time.monotonic()
        if not poller.poll(min(0.5, max(0.0, restante) * 1000)):
            continue
        datos = os.read(fd_num, EVENT_FMT.size * 64)
        ahora = time.monotonic()
        for offset in range(0, len(datos) - EVENT_FMT.size + 1, EVENT_FMT.size):
            _, _, tipo, codigo, valor = EVENT_FMT.unpack_from(datos, offset)
            if tipo != EV_KEY or valor == 2:
                continue  # ignorar auto-repeats (no existen a nivel dispositivo)
            if valor == 1:
                teclas_abajo[codigo] = ahora
                marcas.append(ahora)
                pulsaciones += 1
            elif valor == 0:
                inicio = teclas_abajo.pop(codigo, None)
                if inicio is not None:
                    pares.append(inicio - ahora)  # duración de la pulsación (negativo)

    os.close(fd_num)
    print()

    if len(marcas) < 6:
        print("Muy pocos eventos capturados. Teclea rápido durante toda la prueba.")
        return

    # --- Análisis por LOTES (batching) -----------------------------------
    # Eventos separados <1.5ms llegaron en el mismo informe/intervalo de
    # conexión. El espaciado entre lotes muestrea el intervalo real del enlace.
    lotes, actual = [], [marcas[0]]
    for t in marcas[1:]:
        if t - actual[-1] < 0.0015:
            actual.append(t)
        else:
            lotes.append(actual)
            actual = [t]
    lotes.append(actual)
    inicio_lotes = [lote[0] for lote in lotes]
    gap_lotes = [b - a for a, b in zip(inicio_lotes, inicio_lotes[1:])]
    # solo gaps "sostenidos" (<150ms): muestrean el intervalo del enlace
    gap_cortos = sorted(g for g in gap_lotes if 0 < g < 0.150)
    suelo = gap_cortos[:max(5, len(gap_cortos) // 10)] if gap_cortos else []

    agrupados = sum(1 for lote in lotes if len(lote) > 1)
    duracion_total = marcas[-1] - marcas[0]
    hz_pulsaciones = pulsaciones / duracion_total if duracion_total > 0 else 0

    print("════════ RESULTADO ══════")
    print(f"Pulsaciones             : {pulsaciones}  ({hz_pulsaciones:.0f}/s de media = tu cadencia)")
    print(f"Duración efectiva       : {duracion_total:.2f} s")
    print(f"Informes (lotes)       : {len(lotes)}  -> {len(lotes)/duracion_total:.0f} informes/s")
    print(f"Pulsaciones agrupadas   : {agrupados} lotes con >1 tecla (coalescing)")
    if suelo:
        suelo_med = statistics.median(suelo)
        print(f"Espaciado mínimo entre informes (suelo del enlace):")
        print(f"   p10 de gaps <150ms  : {suelo_med*1000:7.2f} ms")
        print(f"   mínimo              : {min(gap_cortos)*1000:7.2f} ms")
        print(f"   >> INTERVALO de enlace estimado: ~{suelo_med*1000:.1f} ms "
              f"(techo ~{1/suelo_med:.0f} informes/s) <<")
    if pares:
        duraciones = [-x for x in pares]
        print(f"Duración de pulsaciones : mediana {statistics.median(duraciones)*1000:.1f} ms "
              f"(granularidad del muestreo del enlace)")
    print()
    print("Nota: en un teclado el 'polling rate' no es la cadencia de tecleo;")
    print("el techo real lo fija el intervalo de conexión del enlace (BT ~7.5-15ms,")
    print("cable 1-8ms). Si el intervalo estimado ronda esos valores, el enlace va bien.")


def test_tap(dev_path, segundos):
    """Taps rápidos de UNA tecla: revela la rejilla de cuantización del enlace.

    A 125 Hz los gaps/duraciones caen en múltiplos de 8ms;
    a 1000 Hz aparecen valores finos de 1-7ms.
    """
    try:
        fd = os.open(dev_path, os.O_RDONLY | os.O_NONBLOCK)
    except PermissionError:
        sys.exit("Sin permiso para leer " + dev_path + ". Ejecuta con sudo.")
    print(f"\nDispositivo: {nombre_dispositivo(fd)}  [{dev_path}]")
    print(f"Durante {segundos}s: TAPA UNA SOLA TECLA (sube-baja) lo más rápido que puedas.\n")

    eventos = []  # (t, codigo, valor)
    fin = time.monotonic() + segundos
    poller = select.poll()
    poller.register(fd, select.POLLIN)
    while time.monotonic() < fin:
        if not poller.poll(500):
            continue
        datos = os.read(fd, EVENT_FMT.size * 64)
        ahora = time.monotonic()
        for offset in range(0, len(datos) - EVENT_FMT.size + 1, EVENT_FMT.size):
            _, _, tipo, codigo, valor = EVENT_FMT.unpack_from(datos, offset)
            if tipo == EV_KEY and valor in (0, 1):
                eventos.append((ahora, codigo, valor))
    os.close(fd)

    downs = sum(1 for e in eventos if e[2] == 1)
    if downs < 10:
        print("Muy pocos taps. Repite la prueba tapando más rápido.")
        return

    gaps = [b[0] - a[0] for a, b in zip(eventos, eventos[1:])
            if b[0] - a[0] < 0.120 and b[0] - a[0] > 0.0002]
    ms = sorted(round(g * 1000) for g in gaps)

    import collections
    frecuencias = collections.Counter(ms)

    # Análisis de rejilla: ¿caen en múltiplos de 8ms o hay valores finos 1-7ms?
    finos = [g for g in ms if 1 <= g <= 7]
    mult8 = [g for g in ms if g >= 8 and g % 8 == 0]
    otros = [g for g in ms if g >= 8 and g % 8 != 0]

    print("════════ RESULTADO TAP TEST ══════")
    print(f"Taps (key-down)     : {downs}")
    print(f"Gaps analizados     : {len(ms)}")
    print(f"\nHistograma de gaps (ms -> nº):")
    for valor, cuenta in sorted(frecuencias.items()):
        if cuenta >= 2:
            print(f"   {valor:4d} ms : {'█' * min(50, cuenta)} {cuenta}")
    print(f"\nGaps finos (1-7 ms)        : {len(finos)}")
    print(f"Gaps en múltiplos de 8 ms  : {len(mult8)}")
    print(f"Gaps otros                 : {len(otros)}")

    # Clasificación del enlace a partir de la rejilla observada
    if len(finos) > len(mult8) * 2:
        suelo = min(ms) if ms else 0
        print(f"\n>> Enlace rápido: gaps de 1-{suelo if suelo>1 else 7} ms presentes.")
        if suelo <= 1:
            print("   Pico dominante en 1 ms -> polling 1000 Hz (USB). <<")
        else:
            print(f"   Suelo ~{suelo} ms -> techo ~{1000/suelo:.0f} informes/s (intervalo BT). <<")
    elif len(mult8) > len(finos):
        print("\n>> Los gaps caen en múltiplos de 8 ms: firmware entrega cada 8 ms")
        print("   (125 Hz efectivos) aunque el endpoint permita 1000 Hz. <<")
    else:
        print("\n>> Resultado mixto: repite la prueba tapando más rápido para aclarar. <<")



def main():
    ap = argparse.ArgumentParser(description="Mide el polling rate de un teclado por sus eventos de input.")
    ap.add_argument("-d", "--device", help="ruta del event device (p.ej. /dev/input/event20)")
    ap.add_argument("-t", "--tiempo", type=int, default=8, help="segundos de medición (defecto: 8)")
    ap.add_argument("--list", action="store_true", help="listar teclados y salir")
    ap.add_argument("-m", "--modo", choices=["tecleo", "tap"], default="tecleo",
                    help="tecleo: análisis por lotes; tap: rejilla de cuantización con taps de una tecla")
    args = ap.parse_args()

    if args.list:
        for n, d in listar_teclados():
            marca = "  <-- Keychron" if "Keychron" in n else ""
            print(f"{d}  {n}{marca}")
        return

    dev = args.device or elegir_dispositivo()[1]
    if args.modo == "tap":
        test_tap(dev, args.tiempo)
    else:
        medir(dev, args.tiempo)


if __name__ == "__main__":
    main()
