# Firmware para Keychron inalámbricos (CKBT51 / LKBT51) — builds QMK de la comunidad

[![CI](https://github.com/thementalcoding/keychron-pro-firmware/actions/workflows/ci.yml/badge.svg)](https://github.com/thementalcoding/keychron-pro-firmware/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/thementalcoding/keychron-pro-firmware?include_prereleases&sort=semver)](https://github.com/thementalcoding/keychron-pro-firmware/releases)
[![Probado en hardware](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fthementalcoding%2Fkeychron-pro-firmware%2Ftested-index%2Fdocs%2Ftested.json)](https://github.com/thementalcoding/keychron-pro-firmware/blob/tested-index/TESTED.md)
[![Licencia: GPL-2.0](https://img.shields.io/badge/license-GPL--2.0-blue.svg)](LICENSE)

[English](README.md) · **Español**

Firmware QMK no oficial, compilado por la comunidad, para **67 productos Keychron
inalámbricos**: **26 modelos Pro con módulo UART CKBT51** y **41 modelos Max /
Version con módulo SPI LKBT51**, basado en la rama `wls_2025q1` oficial de
Keychron.

Estas builds corrigen una familia de defectos del enlace Bluetooth que provocan
**ráfagas de teclas repetidas** y reconexiones silenciosas. En CKBT51 también
suben la tasa de informes de 90 Hz (de fábrica) al máximo documentado del módulo:
**133 Hz**; los arreglos de LKBT51 son defensivos y aún no se han validado en
hardware.

Síntomas que corrige: **key chatter, doble escritura y ráfagas de teclas
repetidas** por Bluetooth, además de reconexiones silenciosas y una tasa de
informes baja.

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
| ⚠️ **Compilado y verificado automáticamente, nunca flasheado** | El resto de modelos y variantes (230 imágenes) |

Todos los binarios salen del mismo código parcheado, pasan los controles de
sufijo DFU/CRC/tamaño en CI y se publican con su SHA-256. **No se ha probado
ninguna otra unidad**, así que considera esas imágenes *sin probar* hasta que un
reporte de la comunidad diga lo contrario.

**Estado de campo (13-11-2026):** la unidad probada lleva unos 10 días con la
v1.0.1 final en uso diario por Bluetooth sin cuelgues ni ráfagas, que sí ocurrían
con el firmware de fábrica. Sigue siendo una sola unidad, así que la corrección
no está confirmada para el resto de la gama.

¿Lo has flasheado? **[Repórtalo en 30 segundos →](https://github.com/thementalcoding/keychron-pro-firmware/issues/new?template=hardware_test.yml)**
Los contadores de esta página se actualizan solos con esos reportes
([cómo funciona](docs/TESTING.es.md)). La tabla generada vive en la
[rama `tested-index`](https://github.com/thementalcoding/keychron-pro-firmware/blob/tested-index/TESTED.md).

<!-- BEGIN TESTED -->
**1 reporte verificado · 1 modelo** (unidad del mantenedor, K13 Pro ISO RGB, v1.0.1 final, enumeración post-DFU OK 2026-11-03). Tabla en vivo: [tested-index](https://github.com/thementalcoding/keychron-pro-firmware/blob/tested-index/TESTED.md).
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
6. **Mide el enlace**: ejecuta el [test multitecla de polling v0.0.1](docs/POLLING_TEST.es.md).

## Descargas

Las imágenes están agrupadas por modelo. Cada carpeta de modelo tiene un README
con sus PIDs, variantes y notas por fichero.

<!-- BEGIN MODELS -->
| Modelo | Variantes | USB PIDs | Imágenes | Probado en hardware |
|---|---|---|---|---|
| [K0 Max](firmware/k0_max/README.md) | 1 | `0x0A06` | 1 | no |
| [K10 Max](firmware/k10_max/README.md) | 4 | `0x0AA0`, `0x0AA3`, `0x0AA1`, `0x0AA4` | 4 | no |
| [K10 Pro](firmware/k10_pro/README.md) | 6 | `0x02A0`, `0x02A3`, `0x02A1`, `0x02A4`, `0x02A2`, `0x02A5` | 6 | no |
| [K10 Version 2](firmware/k10_version_2/README.md) | 6 | `0x0DA0`, `0x0DA3`, `0x0DA1`, `0x0DA4`, `0x0DA2`, `0x0DA5` | 6 | no |
| [K11 Max](firmware/k11_max/README.md) | 6 | `0x0AB3`, `0x0AB9`, `0x0AB4`, `0x0ABA`, `0x0AB5`, `0x0ABB` | 6 | no |
| [K11 Pro](firmware/k11_pro/README.md) | 4 | `0x02B0`, `0x02B3`, `0x02B6`, `0x02B9` | 4 | no |
| [K12 Pro](firmware/k12_pro/README.md) | 2 | `0x02C0`, `0x02C3` | 2 | no |
| [K13 Max](firmware/k13_max/README.md) | 4 | `0x0AD0`, `0x0AD3`, `0x0AD1`, `0x0AD4` | 4 | no |
| [K13 Pro](firmware/k13_pro/README.md) | 4 | `0x02D0`, `0x02D3`, `0x02D1`, `0x02D4` | 4 | ✅ ISO RGB |
| [K14 Pro](firmware/k14_pro/README.md) | 2 | `0x02E0`, `0x02E3` | 2 | no |
| [K15 Max](firmware/k15_max/README.md) | 4 | `0x0AF0`, `0x0AF3`, `0x0AF1`, `0x0AF4` | 4 | no |
| [K15 Pro](firmware/k15_pro/README.md) | 2 | `0x02F6`, `0x02F9` | 2 | no |
| [K17 Max](firmware/k17_max/README.md) | 6 | `0x0A00`, `0x0A03`, `0x0A01`, `0x0A04`, `0x0A02`, `0x0A05` | 6 | no |
| [K17 Pro](firmware/k17_pro/README.md) | 4 | `0x0206`, `0x0209`, `0x0207`, `0x020A` | 4 | no |
| [K1 Max](firmware/k1_max/README.md) | 6 | `0x0A10`, `0x0A13`, `0x0A11`, `0x0A14`, `0x0A12`, `0x0A15` | 6 | no |
| [K1 Pro](firmware/k1_pro/README.md) | 4 | `0x0210`, `0x0213`, `0x0211`, `0x0214` | 4 | no |
| [K1 Version 6](firmware/k1_version_6/README.md) | 6 | `0x0D10`, `0x0D13`, `0x0D11`, `0x0D14`, `0x0D12`, `0x0D15` | 6 | no |
| [K2 Max](firmware/k2_max/README.md) | 6 | `0x0A20`, `0x0A23`, `0x0A21`, `0x0A24`, `0x0A22`, `0x0A25` | 6 | no |
| [K2 Pro](firmware/k2_pro/README.md) | 6 | `0x0220`, `0x0223`, `0x0221`, `0x0224`, `0x0222`, `0x0225` | 6 | no |
| [K2 Version 3](firmware/k2_version_3/README.md) | 6 | `0x0D20`, `0x0D23`, `0x0D21`, `0x0D24`, `0x0D22`, `0x0D25` | 6 | no |
| [K3 Max](firmware/k3_max/README.md) | 6 | `0x0A30`, `0x0A33`, `0x0A31`, `0x0A34`, `0x0A32`, `0x0A35` | 6 | no |
| [K3 Pro](firmware/k3_pro/README.md) | 6 | `0x0230`, `0x0233`, `0x0231`, `0x0234`, `0x0232`, `0x0235` | 6 | no |
| [K3 Version 3](firmware/k3_version_3/README.md) | 6 | `0x0D30`, `0x0D33`, `0x0D31`, `0x0D34`, `0x0D32`, `0x0D35` | 6 | no |
| [K4 Pro](firmware/k4_pro/README.md) | 4 | `0x0240`, `0x0243`, `0x0241`, `0x0244` | 4 | no |
| [K4 Version 3](firmware/k4_version_3/README.md) | 6 | `0x0D40`, `0x0D43`, `0x0D41`, `0x0D44`, `0x0D42`, `0x0D45` | 6 | no |
| [K5 Max](firmware/k5_max/README.md) | 4 | `0x0A50`, `0x0A53`, `0x0A51`, `0x0A54` | 4 | no |
| [K5 Pro](firmware/k5_pro/README.md) | 6 | `0x0250`, `0x0253`, `0x0251`, `0x0254`, `0x0252`, `0x0255` | 6 | no |
| [K5 Version 2](firmware/k5_version_2/README.md) | 6 | `0x0D50`, `0x0D53`, `0x0D51`, `0x0D54`, `0x0D52`, `0x0D55` | 6 | no |
| [K6 Pro](firmware/k6_pro/README.md) | 5 | `0x0260`, `0x0263`, `0x0261`, `0x0264`, `0x0262` | 5 | no |
| [K7 Max](firmware/k7_max/README.md) | 6 | `0x0A70`, `0x0A73`, `0x0A71`, `0x0A74`, `0x0A72`, `0x0A75` | 6 | no |
| [K7 Pro](firmware/k7_pro/README.md) | 4 | `0x0270`, `0x0273`, `0x0271`, `0x0274` | 4 | no |
| [K8 Max](firmware/k8_max/README.md) | 6 | `0x0A80`, `0x0A83`, `0x0A81`, `0x0A84`, `0x0A82`, `0x0A85` | 6 | no |
| [K8 Pro](firmware/k8_pro/README.md) | 6 | `0x0280`, `0x0283`, `0x0281`, `0x0284`, `0x0282`, `0x0285` | 6 | no |
| [K8 Version 2](firmware/k8_version_2/README.md) | 6 | `0x0D80`, `0x0D83`, `0x0D81`, `0x0D84`, `0x0D82`, `0x0D85` | 6 | no |
| [K9 Pro](firmware/k9_pro/README.md) | 6 | `0x0290`, `0x0293`, `0x0291`, `0x0294`, `0x0292`, `0x0295` | 6 | no |
| [Q0 Max](firmware/q0_max/README.md) | 1 | `0x0800` | 1 | no |
| [Q10 Max](firmware/q10_max/README.md) | 2 | `0x08A0`, `0x08A1` | 2 | no |
| [Q10 Pro](firmware/q10_pro/README.md) | 2 | `0x06A0`, `0x06A1` | 2 | no |
| [Q12 Max](firmware/q12_max/README.md) | 1 | `0x08C3` | 1 | no |
| [Q13 Max](firmware/q13_max/README.md) | 1 | `0x08D0` | 1 | no |
| [Q13 Pro](firmware/q13_pro/README.md) | 2 | `0x06D0`, `0x06D1` | 2 | no |
| [Q14 Max](firmware/q14_max/README.md) | 1 | `0x08E0` | 1 | no |
| [Q14 Pro](firmware/q14_pro/README.md) | 2 | `0x06E0`, `0x06E1` | 2 | no |
| [Q15 Max](firmware/q15_max/README.md) | 1 | `0x08F0` | 1 | no |
| [Q1 Max](firmware/q1_max/README.md) | 3 | `0x0810`, `0x0811`, `0x0812` | 3 | no |
| [Q1 Pro](firmware/q1_pro/README.md) | 3 | `0x0610`, `0x0611`, `0xA612` | 3 | no |
| [Q2 Max](firmware/q2_max/README.md) | 2 | `0x0820`, `0x0821` | 2 | no |
| [Q2 Pro](firmware/q2_pro/README.md) | 2 | `0x0620`, `0x0621` | 2 | no |
| [Q3 Max](firmware/q3_max/README.md) | 2 | `0x0830`, `0x0831` | 2 | no |
| [Q3 Pro](firmware/q3_pro/README.md) | 5 | `0x0633`, `0x0630`, `0x0634`, `0x0631`, `0x0632` | 5 | no |
| [Q4 Pro](firmware/q4_pro/README.md) | 2 | `0x0640`, `0x0641` | 2 | no |
| [Q5 Max](firmware/q5_max/README.md) | 2 | `0x0850`, `0x0851` | 2 | no |
| [Q5 Pro](firmware/q5_pro/README.md) | 2 | `0x0650`, `0x0651` | 2 | no |
| [Q60 Max](firmware/q60_max/README.md) | 1 | `0x08C0` | 1 | no |
| [Q65 Max](firmware/q65_max/README.md) | 1 | `0x08B0` | 1 | no |
| [Q6 Max](firmware/q6_max/README.md) | 2 | `0x0860`, `0x0861` | 2 | no |
| [Q6 Pro](firmware/q6_pro/README.md) | 2 | `0x0660`, `0x0661` | 2 | no |
| [Q8 Max](firmware/q8_max/README.md) | 1 | `0x0880` | 1 | no |
| [Q8 Pro](firmware/q8_pro/README.md) | 2 | `0x0680`, `0x0681` | 2 | no |
| [V10 Max](firmware/v10_max/README.md) | 1 | `0x09A0` | 1 | no |
| [V1 Max](firmware/v1_max/README.md) | 3 | `0x0913`, `0x0914`, `0x0915` | 3 | no |
| [V2 Max](firmware/v2_max/README.md) | 2 | `0x0920`, `0x0921` | 2 | no |
| [V3 Max](firmware/v3_max/README.md) | 2 | `0x0933`, `0x0934` | 2 | no |
| [V4 Max](firmware/v4_max/README.md) | 1 | `0x0940` | 1 | no |
| [V5 Max](firmware/v5_max/README.md) | 2 | `0x0950`, `0x0951` | 2 | no |
| [V6 Max](firmware/v6_max/README.md) | 2 | `0x0960`, `0x0961` | 2 | no |
| [V8 Max](firmware/v8_max/README.md) | 1 | `0x0980` | 1 | no |
<!-- END MODELS -->

Índice legible por máquina con tamaños, SHA-256, PIDs y estado de prueba:
[`firmware/manifest.json`](firmware/manifest.json).

> **`_via` vs `_default`:** las imágenes `_via` conservan el protocolo de keymap
> de VIA / Keychron Engine. Las `_default` no hablan VIA: úsalas solo si no usas
> VIA. Si una variante no tiene imagen `_via`, ese keymap no existe upstream.

## Qué cambia

**Robustez del enlace Bluetooth** (código CKBT51 compartido — beneficia a los 26 modelos Pro)

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

**Familia LKBT51 SPI** (41 modelos Max / Version)

- `lkbt51_read()` queda acotado al buffer de paquete de 64 bytes.
- El parser `0xAA 0x57` valida `len >= 3`, mantiene el paquete dentro de `buf[]`
  y ya no se bloquea permanentemente con una cabecera fuera de rango.
- El TX de OTA se trocea y el RX rechaza payloads más cortos que el sub-header.
- La cola de informes se vacía al reconectar, cambiar de host y suspender; los
  informes consumer esperan si hay un reintento pendiente.
- La inicialización del encoder se mueve después del manejo EXTI de los pines de
  modo al despertar.

**Detalles por modelo** en la carpeta de cada modelo.

## Resultado medido

Keychron K13 Pro ISO RGB, Linux 6.12, Intel AX210, Bluetooth. Test de pulsación,
una tecla, 10 s (`tools/medir_polling.py -m tap`):

| Métrica | De fábrica (90 Hz) | Este firmware (133 Hz) |
|---|---|---|
| Techo del módulo | 90 Hz | **133 Hz** |
| Suelo de un tap de una tecla | ~7,5 ms | ~7,5 ms |

La cifra anterior de “5 ms / ~200 informes/s” era una medición multi-tecla y
queda retirada: un tap de una tecla está limitado a ~7,5 ms / 133 Hz por el
módulo cerrado.

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
  hardware; el resto solo está compilado y verificado estáticamente. Las 41
  imágenes LKBT51 nunca se han flasheado.
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
# QMK CLI, arm-none-eabi-gcc 12–14; clang-format 14 (CI de QMK) para ficheros del core
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
- `v1.0.1-beta` (build **2026-11-02a**, histórica): 26 modelos CKBT51, 95
  imágenes; la beta local anterior con P1–P5.
- `v1.0.1` (build **2026-11-03a**): 67 modelos, 231 imágenes; parches de la
  auditoría de Claude más la espera USB P5. La v1.0.1 anterior pasa a
  `v1.0.1-beta`.
- Próximos arreglos: `1.0.x-alpha.N` (validación en una unidad) → `-beta.N` (más
  reportes de hardware) → estable.
- Las notas de cada release indican el commit base upstream.

## Créditos y licencia

- Basado en [Keychron/qmk_firmware](https://github.com/Keychron/qmk_firmware)
  (`wls_2025q1`) — QMK Firmware y ChibiOS son GPL-2.0.
- Todos los cambios de este repositorio se publican bajo **GPL-2.0** (ver
  [LICENSE](LICENSE)).
- Estado de la auditoría: [`docs/CLAUDE_AUDIT.md`](docs/CLAUDE_AUDIT.md);
  auditorías y notas de diseño anteriores: [`docs/history/`](docs/history/README.md).
