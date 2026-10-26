# Firmware para Keychron Pro inalámbricos (CKBT51) — builds QMK de la comunidad

[![CI](https://github.com/thementalcoding/keychron-pro-firmware/actions/workflows/ci.yml/badge.svg)](https://github.com/thementalcoding/keychron-pro-firmware/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/thementalcoding/keychron-pro-firmware?include_prereleases&sort=semver)](https://github.com/thementalcoding/keychron-pro-firmware/releases)
[![Probado en hardware](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fthementalcoding%2Fkeychron-pro-firmware%2Ftested-index%2Fdocs%2Ftested.json)](https://github.com/thementalcoding/keychron-pro-firmware/blob/tested-index/TESTED.md)
[![Licencia: GPL-2.0](https://img.shields.io/badge/license-GPL--2.0-blue.svg)](LICENSE)

[English](README.md) · **Español**

Firmware QMK no oficial, compilado por la comunidad, para **26 teclados Keychron
Pro inalámbricos** (STM32L432 + módulo Bluetooth **CKBT51**), basado en la rama
`wls_2025q1` oficial de Keychron.

Estas builds corrigen una familia de defectos del enlace Bluetooth que provocan
**ráfagas de teclas repetidas** y reconexiones silenciosas, y suben la tasa de
informes Bluetooth de 90 Hz (de fábrica) al máximo documentado del módulo:
**133 Hz**.

> ⚠️ **No oficial.** Sin relación con Keychron. Flashear es responsabilidad tuya.
> Un brick es prácticamente imposible: el **bootloader ROM del STM32 no se puede
> sobrescribir**, así que siempre se puede volver al modo DFU
> (ver [Recuperación](docs/RECOVERY.es.md)).

**Propuesta upstream:** [Keychron/qmk_firmware#529](https://github.com/Keychron/qmk_firmware/pull/529)

---

## Estado de las pruebas en hardware

| | |
|---|---|
| ✅ **Probado en hardware real** | **1 unidad**: Keychron K13 Pro **ISO RGB** (`0x02D1`) |
| ⚠️ **Compilado y verificado automáticamente, nunca flasheado** | El resto de modelos y variantes (94 imágenes) |

Todos los binarios salen del mismo código parcheado, pasan los controles de
sufijo DFU/CRC/tamaño en CI y se publican con su SHA-256. **No se ha probado
ninguna otra unidad**, así que considera esas imágenes *sin probar* hasta que un
reporte de la comunidad diga lo contrario.

El síntoma original (ráfagas de teclas repetidas) **aún no está confirmado como
resuelto** a largo plazo: en la unidad probada los resultados preliminares son
buenos (+40 % de polling, sin episodios), pero solo han pasado unos días de uso.

¿Lo has flasheado? **[Repórtalo en 30 segundos →](https://github.com/thementalcoding/keychron-pro-firmware/issues/new?template=hardware_test.yml)**
Los contadores de esta página se actualizan solos con esos reportes
([cómo funciona](docs/TESTING.es.md)). La tabla generada vive en la
[rama `tested-index`](https://github.com/thementalcoding/keychron-pro-firmware/blob/tested-index/TESTED.md).

<!-- BEGIN TESTED -->
**1 reporte verificado · 1 modelo** (unidad del mantenedor, K13 Pro ISO RGB). Tabla en vivo: [tested-index](https://github.com/thementalcoding/keychron-pro-firmware/blob/tested-index/TESTED.md).
<!-- END TESTED -->

---

## Inicio rápido

1. **Identifica tu variante exacta** (PID) en modo cable:
   ```bash
   lsusb | grep -i 3434
   ```
   Búscalo en la tabla de abajo. Flashear la variante equivocada tiene arreglo,
   pero el teclado se comportará raro (layout/retroiluminación) hasta que flashes
   la correcta.
2. **Copia de seguridad de tu keymap**: Keychron Engine (engine.keychron.com) o
   VIA → exportar el JSON.
3. **Verifica la descarga** antes de flashear:
   ```bash
   sha256sum -c SHA256SUMS
   ```
4. **Flashea**: ver [Flasheo](#flasheo) (Linux, macOS, Windows).
5. **Restaura tu keymap** y [reporta el resultado](https://github.com/thementalcoding/keychron-pro-firmware/issues/new?template=hardware_test.yml).

## Descargas

Las imágenes están agrupadas por modelo. Cada carpeta de modelo tiene un README
con sus PIDs, variantes y notas por fichero.

<!-- BEGIN MODELS -->
| Model | Variants | USB PIDs | Images | Hardware-tested |
|---|---|---|---|---|
| [K1 Pro](firmware/k1_pro/README.md) | 4 | `0x0210`, `0x0211`, `0x0213`, `0x0214` | 4 | — (untested) |
| [K2 Pro](firmware/k2_pro/README.md) | 6 | `0x0220`, `0x0221`, `0x0222`, `0x0223`, `0x0224`, `0x0225` | 6 | — (untested) |
| [K3 Pro](firmware/k3_pro/README.md) | 6 | `0x0230`, `0x0231`, `0x0232`, `0x0233`, `0x0234`, `0x0235` | 6 | — (untested) |
| [K4 Pro](firmware/k4_pro/README.md) | 4 | `0x0240`, `0x0241`, `0x0243`, `0x0244` | 4 | — (untested) |
| [K5 Pro](firmware/k5_pro/README.md) | 6 | `0x0250`, `0x0251`, `0x0252`, `0x0253`, `0x0254`, `0x0255` | 6 | — (untested) |
| [K6 Pro](firmware/k6_pro/README.md) | 5 | `0x0260`, `0x0261`, `0x0262`, `0x0263`, `0x0264` | 5 | — (untested) |
| [K7 Pro](firmware/k7_pro/README.md) | 4 | `0x0270`, `0x0271`, `0x0273`, `0x0274` | 4 | — (untested) |
| [K8 Pro](firmware/k8_pro/README.md) | 6 | `0x0280`, `0x0281`, `0x0282`, `0x0283`, `0x0284`, `0x0285` | 6 | — (untested) |
| [K9 Pro](firmware/k9_pro/README.md) | 6 | `0x0290`, `0x0291`, `0x0292`, `0x0293`, `0x0294`, `0x0295` | 6 | — (untested) |
| [K10 Pro](firmware/k10_pro/README.md) | 6 | `0x02A0`, `0x02A1`, `0x02A2`, `0x02A3`, `0x02A4`, `0x02A5` | 6 | — (untested) |
| [K11 Pro](firmware/k11_pro/README.md) | 4 | `0x02B0`, `0x02B3`, `0x02B6`, `0x02B9` | 4 | — (untested) |
| [K12 Pro](firmware/k12_pro/README.md) | 2 | `0x02C0`, `0x02C3` | 2 | — (untested) |
| [K13 Pro](firmware/k13_pro/README.md) | 4 | `0x02D0`, `0x02D1`, `0x02D3`, `0x02D4` | 4 | ✅ ISO/RGB |
| [K14 Pro](firmware/k14_pro/README.md) | 2 | `0x02E0`, `0x02E3` | 2 | — (untested) |
| [K15 Pro](firmware/k15_pro/README.md) | 2 | `0x02F6`, `0x02F9` | 2 | — (untested) |
| [K17 Pro](firmware/k17_pro/README.md) | 4 | `0x0206`, `0x0207`, `0x0209`, `0x020A` | 4 | — (untested) |
| [Q1 Pro](firmware/q1_pro/README.md) | 3 | `0x0610`, `0x0611`, `0xA612` | 3 | — (untested) |
| [Q2 Pro](firmware/q2_pro/README.md) | 2 | `0x0620`, `0x0621` | 2 | — (untested) |
| [Q3 Pro](firmware/q3_pro/README.md) | 5 | `0x0630`, `0x0631`, `0x0632`, `0x0633`, `0x0634` | 5 | — (untested) |
| [Q4 Pro](firmware/q4_pro/README.md) | 2 | `0x0640`, `0x0641` | 2 | — (untested) |
| [Q5 Pro](firmware/q5_pro/README.md) | 2 | `0x0650`, `0x0651` | 2 | — (untested) |
| [Q6 Pro](firmware/q6_pro/README.md) | 2 | `0x0660`, `0x0661` | 2 | — (untested) |
| [Q8 Pro](firmware/q8_pro/README.md) | 2 | `0x0680`, `0x0681` | 2 | — (untested) |
| [Q10 Pro](firmware/q10_pro/README.md) | 2 | `0x06A0`, `0x06A1` | 2 | — (untested) |
| [Q13 Pro](firmware/q13_pro/README.md) | 2 | `0x06D0`, `0x06D1` | 2 | — (untested) |
| [Q14 Pro](firmware/q14_pro/README.md) | 2 | `0x06E0`, `0x06E1` | 2 | — (untested) |

Every image is built from the same patched source. Only the rows marked ✅ have been flashed on hardware; the rest are untested builds.
<!-- END MODELS -->

Índice legible por máquina con tamaños, SHA-256, PIDs y estado de prueba:
[`firmware/manifest.json`](firmware/manifest.json).

> **`_via` vs `_default`:** las imágenes `_via` conservan el protocolo de keymap
> de VIA / Keychron Engine. Las `_default` no hablan VIA: úsalas solo si no usas
> VIA. Si una variante no tiene imagen `_via`, ese keymap no existe upstream.

## Qué cambia

**Robustez del enlace Bluetooth** (código compartido — beneficia a los 26 modelos)

- Parser de tramas UART acotado (buffer de 64 bytes; sin desbordes y sin
  descartar tramas legítimas de 42–61 bytes del módulo).
- La cola de informes se vacía también en `EVT_RECONNECTING`, no solo al
  desconectar. Esto elimina el mecanismo principal de las ráfagas: la reproducción
  de una cola obsoleta tras perderse el evento de desconexión.
- Reset del temporizador de reintento ante ACK de FIFO llena (sin tormenta de
  reenvíos).
- Puerta de bajo consumo: nunca se entra en STOP1 con informes, reintentos o
  eventos pendientes.
- `bluetooth_connect()` limitado a un intento cada 500 ms.
- `CKBT51_FAST_WAKE` opcional (desactivado por defecto) para saltar la secuencia
  de despertar de 3 ms cuando el módulo ya está despierto.

**Parámetros del módulo** (todos los modelos CKBT51)

- `report_rate`: 90 → **133 Hz**
- `reconnect_timeout`: 5 s → **60 s**
- Se aplican en el **primer init de Bluetooth**, independientemente del momento
  del arranque (las ventanas de 1 s — y de 5 s en k13_pro — han desaparecido).

**Detalles por modelo** en la carpeta de cada modelo.

## Resultado medido

Keychron K13 Pro ISO RGB, Linux 6.12, Intel AX210, Bluetooth. Test de pulsación,
una tecla, 10 s (`tools/medir_polling.py -m tap`):

| Métrica | De fábrica (90 Hz) | Este firmware (133 Hz) |
|---|---|---|
| Hueco mínimo entre informes | 7 ms | **5 ms** |
| Techo de informes estimado | ~143 informes/s | **~200 informes/s** |

## Flasheo

Necesitas `dfu-util` (Linux/macOS) o QMK Toolbox (Windows). En Linux/macOS no
hay driver que instalar; en Windows hace falta el driver WinUSB (QMK Toolbox lo
instala).

### Entrar en DFU (todos los modelos)

1. Apaga el teclado (**Off**).
2. Mantén **Esc**.
3. Pasa a **Cable** sin soltar Esc (o mantén el botón de reset bajo la barra
   espaciadora, si tu modelo lo tiene).
4. Suelta. `lsusb` debe mostrar `0483:df11 STMicroelectronics STM32 BOOTLOADER`.

### Linux

```bash
sudo dfu-util -d 0483:df11 -a 0 -s 0x08000000:leave -D \
  firmware/k13_pro/iso-rgb/keychron_k13_pro_iso_rgb_via.bin
```

Si aparece `LIBUSB_ERROR_ACCESS`, añade la regla udev de
[`docs/RECOVERY.es.md`](docs/RECOVERY.es.md#regla-udev-en-linux).

### macOS

```bash
brew install dfu-util
dfu-util -d 0483:df11 -a 0 -s 0x08000000:leave -D firmware/<modelo>/<variante>/<fichero>.bin
```

### Windows

Usa [QMK Toolbox](https://qmk.fm/toolbox): selecciona el `.bin`, activa
"STM32 DFU", conecta el teclado en modo DFU y pulsa **Flash**. Keychron Engine
también sirve para restaurar el firmware de fábrica, no para estas builds.

El teclado reinicia con el firmware nuevo. Restaura tu JSON de keymap.

## Si algo sale mal

Lee **[docs/RECOVERY.es.md](docs/RECOVERY.es.md)** (English:
[RECOVERY.md](docs/RECOVERY.md)). Resumen:

- El bootloader ROM nunca se borra: **vuelve a entrar en DFU y flashea otra vez**.
- Variante equivocada / sin teclas / sin retroiluminación → flashea la imagen del
  PID correcto.
- No se detecta en DFU → prueba otro cable/puerto (USB 2.0, sin hub), apaga →
  mantén Esc → Cable de nuevo.
- Bluetooth muerto pero USB funciona → reflashea; si persiste, el firmware del
  módulo CKBT51 puede necesitar el actualizador oficial de Keychron (ver
  limitaciones).
- Último recurso: restaurar el firmware de fábrica con Keychron Engine.

## Limitaciones conocidas

- **Validación de una sola unidad.** Solo el K13 Pro ISO RGB se ha flasheado en
  hardware; el resto solo está compilado y verificado estáticamente.
- Cambiar BT → USB → BT en menos de 500 ms puede suprimir un intento de conexión
  (una pulsación puede retrasarse hasta el siguiente reintento).
- Los parámetros del módulo se envían en el primer init de Bluetooth tras el
  encendido; no se reenvían en cada reconexión.
- Este proyecto solo cambia el **STM32 (MCU)**. El módulo de radio CKBT51 lleva
  firmware cerrado; para arreglos del módulo usa el actualizador oficial de
  Keychron (`Keychron_Bt_Firmware_Upgrade_v0.14.exe`). Ese actualizador
  sobrescribe el firmware del MCU: vuelve a flashear esta build después.
- Algunas variantes no tienen keymap `via` upstream; sus imágenes son solo
  `_default`.

## Verificar una descarga

```bash
sha256sum -c SHA256SUMS
python3 tools/verify_bins.py            # sufijo DFU, VID/PID, CRC, tamaño
python3 tools/verify_manifest.py        # coherencia manifest ↔ ficheros
```

## Compilar desde el código

```bash
git clone https://github.com/thementalcoding/qmk_firmware.git
cd qmk_firmware && git checkout k13-pro-bt-fixes
# QMK CLI, arm-none-eabi-gcc 12–14; clang-format 19.x para paridad con CI
qmk compile -kb keychron/k13_pro/iso/rgb -km via
```

La serie de parches se aplica sobre un checkout limpio de
`Keychron/qmk_firmware` en `c8b2b23` (`wls_2025q1`); ver [`patches/`](patches/)
y [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Estructura del repositorio

```
firmware/<modelo>/<variante>/<binario>.bin   # una carpeta por modelo y variante
firmware/manifest.json                       # índice legible por máquina
SHA256SUMS                                   # checksums de todos los binarios
docs/                                        # auditoría, SDD, recuperación, pruebas
patches/                                     # serie de parches upstream
tools/                                       # scripts de flasheo/verificación/medición
```

El índice de pruebas generado vive en la rama `tested-index`
(`TESTED.md` + `docs/tested.json`), para que `main` siga protegida y revisada.

Las carpetas de modelo usan el nombre upstream en minúsculas (`k13_pro`,
`q6_pro`, …). Las de variante usan guiones (`iso-rgb`, `ansi-white`).

## Versionado

[SemVer](https://semver.org/). **El mismo número de versión significa los mismos
bytes** — una release nunca se re-sube con contenido distinto.

- `v1.0.0` (build **2026-10-26c**): primera release de toda la gama, 26 modelos,
  95 imágenes. Una unidad probada en hardware (K13 Pro ISO RGB).
- Próximos arreglos: `1.0.x-alpha.N` (validación en una unidad) → `-beta.N` (más
  reportes de hardware) → estable.
- Las notas de cada release indican el commit base upstream.

## Créditos y licencia

- Basado en [Keychron/qmk_firmware](https://github.com/Keychron/qmk_firmware)
  (`wls_2025q1`) — QMK Firmware y ChibiOS son GPL-2.0.
- Todos los cambios de este repositorio se publican bajo **GPL-2.0** (ver
  [LICENSE](LICENSE)).
- Auditoría y notas de diseño: [`docs/AUDIT.md`](docs/AUDIT.md),
  [`docs/SDD.md`](docs/SDD.md), [`docs/GAMA_AUDIT.md`](docs/GAMA_AUDIT.md).
