# Test multitecla de polling rate — v0.0.1

Test autónomo para Linux que estima el espaciado entre informes del teclado por
Bluetooth o USB. No necesita paquetes de terceros.

## Qué mide

El script lee eventos `EV_KEY` crudos de `/dev/input/eventX`. Los eventos que
llegan en la misma lectura se tratan como un único informe HID; los huecos entre
esas lecturas estiman el intervalo del enlace.

Es una herramienta de observación, no un analizador USB. El módulo CKBT51/LKBT51
es cerrado y no expone su polling rate real.

## Requisitos

- Linux (x86_64) con dispositivos de entrada `evdev`.
- Python 3.10 o superior.
- Permiso de lectura sobre `/dev/input/eventX`: usa `sudo` o añade tu usuario al
  grupo `input`.
- Un teclado conectado por cable o Bluetooth.

## Listar dispositivos

```bash
sudo python3 tools/polling_multikey_v0.0.1.py --list
```

Busca una línea como:

```text
/dev/input/event19  Keychron K13 Pro Keyboard  <-- Keychron
```

No uses el dispositivo `... Mouse` ni `... Consumer Control` para este test.

## Ejecutar

```bash
sudo python3 tools/polling_multikey_v0.0.1.py -t 10 -d /dev/input/event19
```

Durante todo el test, **pulsa varias teclas a la vez** (3-5 teclas en acordes o
rolls rápidos) y suéltalas rápido. No uses auto-repeat. La carga multitecla hace
visible el agrupamiento de informes.

Guarda el resultado para un PR o issue:

```bash
sudo python3 tools/polling_multikey_v0.0.1.py -t 10 --json polling.json
```

Pruebas internas sin teclado:

```bash
python3 tools/polling_multikey_v0.0.1.py --self-test
```

## Interpretación

| Observación | Significado |
|---|---|
| p10 ≈ 1-2 ms | Enlace USB a ~1000 Hz |
| p10 ≈ 7-8 ms | Bluetooth en el techo del módulo (~133 Hz) |
| p10 ≈ 9-16 ms | Bluetooth limitado a ~90-125 Hz |
| Huecos en múltiplos exactos de 8 ms | Tope de 125 Hz |
| Huecos grandes e irregulares | Domina tu cadencia; repite más rápido |

Ejemplo del K13 Pro ISO RGB del mantenedor (Bluetooth):

```text
Pulsaciones             : 298  (33/s de media = tu cadencia)
Duración efectiva       : 9.10 s
Informes (lotes)        : 292  -> 32 informes/s
Pulsaciones agrupadas   : 6 lotes con >1 tecla
Espaciado mínimo entre informes (suelo del enlace):
   p10 de gaps <150ms  :    6.99 ms
   mínimo              :     5.00 ms
>> INTERVALO de enlace estimado: ~7.0 ms (techo ~143 informes/s) <<
```

El techo nominal del módulo es 133 Hz (~7,5 ms). La cifra de 143/s es la
estimación heurística e incluye ruido de planificación; no es un enlace de
1000 Hz.

## Protocolo antes/después

1. Ejecuta el test con el firmware de fábrica, por Bluetooth, mismo host y mismo
   dispositivo.
2. Flashea la v1.0.1 final.
3. Repite el test con el mismo patrón multitecla.
4. Reporta `p10`, mínimo e informes/s estimados en el issue de hardware.

Los hallazgos principales del proyecto están documentados en
[CLAUDE_AUDIT.md](CLAUDE_AUDIT.md).
