# Informe: cortes de teclado Keychron K13 Pro por Bluetooth

**Equipo:** host (Manjaro, kernel 6.12.108-1, bluetoothd 5.87)
**Fecha de análisis:** 30/09/2026, 14:40–15:00 CEST
**Ubicación:** ``

---

## 1. Problema

El teclado **Keychron K13 Pro**, conectado por **Bluetooth**, de vez en cuando
"se le va la perola" y **escribe muchas letras seguidas** (ráfaga de pulsaciones
repetidas). Ocurre esporádicamente; por cable no se ha notado.

## 2. Hardware implicado

| Componente | Detalle |
|---|---|
| Teclado | Keychron K13 Pro, BT HID v1.32, dirección `XX:XX:XX:XX:XX:XX` |
| Adaptador BT | **Intel AX210 Bluetooth** (USB interno, ID `8087:0032`), hci0 |
| Host BT | `XX:XX:XX:XX:XX:XX` |
| WiFi | Mismo chip AX210 (phy0/REDACTED) — **bloqueado por software y desconectado** (se usa Ethernet) |

## 3. Línea temporal del día del análisis (30/09/2026)

| Hora | Evento | Fuente |
|---|---|---|
| 04:36:29 | Carga del driver btusb; `hci0: FW download error recovery failed (-19)` (transitorio, recuperó) | kernel |
| 04:36:33 | Firmware Intel cargado OK: `ibt-0041-0041.sfi`, versión `202-5.26`, timestamp 2026.5 build 82122 | kernel |
| 04:36:38 | Teclado conecta por BT (instancia uhid `000A`) | kernel |
| **14:11:19** | **Reconexión silenciosa del teclado** (instancia uhid `000B`) — no hay ningún "disconnect" registrado justo antes | kernel |
| **14:42:05–14:42:31** | **Episodio de ráfaga de teclas.** Sin desconexión BT, sin error hci0, sin error de input. Solo 2 avisos cosméticos de KDE (`KKeyServer::xcbKeyPressEventToQt failed`) coincidiendo con la ráfaga | kernel/journal |

## 4. Diagnóstico

**Causa más probable: USB autosuspend del adaptador Intel AX210.**

- El adaptador BT tenía `power/control=auto` con retardo de 2 s
  (`usbcore.autosuspend=2` global en el kernel).
- Un enlace BT HID está la mayor parte del tiempo *inactivo* (no se escribe),
  por lo que el adaptador se suspendía a los 2 s de quietud. Al despertar a
  mitad de pulsación se producen micro-cortes de enlace: el informe HID se
  retransmite y llega en ráfaga → **letras repetidas**.
- **Coexistencia WiFi/BT descartada**: el WiFi del mismo chip está
  soft-blocked (`rfkill`) y sin usar; se navega por Ethernet.
- El `FW download error recovery failed (-19)` del arranque era transitorio y
  coherente con un chip en mal estado de energía, no con firmware antiguo.

**Firmware descartado como causa:** `linux-firmware-intel 20260810-2`
(actualizado el 23/08/2026) es ya la última versión del repo `core` de Manjaro;
`checkupdates` no devuelve nada pendiente. El firmware cargado en el arranque
(`Firmware Version: 202-5.26`, SHA1 verificado) corresponde a ese paquete.

## 5. Correcciones aplicadas (30/09/2026 14:58)

1. **Inmediata (runtime, sin reiniciar):**
   ```bash
   echo on | sudo tee /sys/bus/usb/devices/1-4/power/control
   ```
2. **Permanente (regla udev):** `/etc/udev/rules.d/90-ax210-bt-autosuspend.rules`
   ```
   # Desactiva el autosuspend USB del adaptador Intel AX210 Bluetooth (8087:0032)
   # Evita micro-cortes del enlace BT y ráfagas de teclas repetidas del teclado Keychron K13 Pro
   ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="8087", ATTR{idProduct}=="0032", TEST=="power/control", ATTR{power/control}="on"
   ```
   + `udevadm control --reload && udevadm trigger`

**Verificación:**

| Comprobación | Resultado |
|---|---|
| `cat /sys/bus/usb/devices/1-4/power/control` | `on` ✅ |
| Regla instalada y válida (`udevadm verify`) | Success ✅ |
| `udevadm test` simula el arranque | Matchea `v8087p0032` "AX210 Bluetooth" y escribiría `on` ✅ |

La regla matchea por ID de producto, por lo que funciona aunque cambie el
puerto USB del adaptador en un futuro.

## 6. Estado actual y plan de validación

- El teclado está conectado por **Bluetooth** (el cable solo alimenta; el
  interruptor del teclado no se cambió).
- **Validación:** usar el teclado por BT de forma normal unos días. El patrón
  era: ráfaga tras pausa corta (> 2 s de inactividad). Si desaparece, confirmado.
- **Si reaparece:** capturar el enlace en crudo con
  `sudo btmon -w /tmp/btsnoop.log` justo cuando ocurra, y considerar
  actualizar el firmware del propio Keychron K13 Pro (Keychron publica fixes
  de estabilidad BT).

## 7. Medición del polling rate

Script incluido: [`../tools/medir_polling.py`](../tools/medir_polling.py)

```bash
# opción A: con sudo (no requiere cambios permanentes)
sudo python3 tools/medir_polling.py

# opción B: permiso permanente sin sudo
sudo usermod -aG input user   # y relogin
python3 tools/medir_polling.py
```

**Concepto importante:** en un teclado el "polling rate" no se mide con la
cadencia de tecleo ni manteniendo una tecla (el auto-repeat lo genera el SO,
no el dispositivo: en el flujo crudo del teclado solo hay key-down/key-up).
El techo real lo fija el **intervalo de conexión del enlace**:

| Enlace | Intervalo típico | Techo de informes |
|---|---|---|
| Cable (USB) | 1–8 ms | 125–1000 Hz |
| Bluetooth | 7.5–15 ms | ~66–133 Hz |

El script actual (30/09/2026) agrupa las pulsaciones que llegan en el mismo
instante (lotes/coalescing) y estima el **intervalo de enlace** con el suelo
del espaciado entre lotes. Interpretación:

- Varias teclas dentro del mismo intervalo llegan juntas (gap ≈ 0 ms) — es lo
  normal y no un defecto.
- Si el intervalo estimado ronda 7.5–15 ms en BT, el enlace está sano.
- Si el intervalo estimado es muy superior (p. ej. >30 ms), el enlace está
  degradado (interferencias, ahorro de energía del teclado, etc.).

**Procedimiento:** teclear rápido con varias teclas simultáneas durante la
prueba, en modo BT y en modo cable, y comparar los intervalos estimados.

### Primer test (30/09/2026, versión antigua del script, modo BT)

- 189 pulsaciones en 6.97 s (27 teclas/s), 0 auto-repeats (confirmación de
  que el dispositivo no repite: el auto-repeat es del SO).
- Gap mínimo entre eventos: 0.01 ms → coalescing presente (varias teclas por
  informe), comportamiento normal en BT.
- El "43 Hz" de esa medición era la cadencia de tecleo del usuario, no el
  polling rate. Con el script actualizado se mide el intervalo de enlace.

### Resultados con el script actualizado (30/09/2026)

**Modo cable — 1000 Hz confirmados:**

- Descriptor USB (`lsusb -v`): `bcdUSB 2.00`, Full Speed (12 Mbps), endpoint
  del teclado con `bInterval 1` → el host sondea cada 1 ms.
- Tap test (`-m tap`, 230 taps de una tecla): **212 gaps de exactamente 1 ms**,
  224 gaps finos (1–7 ms). El firmware entrega informes cada 1 ms →
  **1000 Hz reales**, cumple la especificación anunciada.
- Nota: la primera estimación (125 Hz con tecleo libre, gap mínimo 8 ms) fue
  un artefacto del método: con tecleo multitecla las pulsaciones se agrupan
  en el mismo informe (coalescing) y las pausas humanas enmascaran el suelo.
  El tap test de una sola tecla es el método fiable.

**Modo Bluetooth — ~150 Hz (confirmado con tap test):**

- Análisis por lotes: 272 pulsaciones en 6.84 s, suelo de espaciado entre
  informes 6.64 ms → techo ~150 informes/s.
- Tap test (`-m tap`, 227 taps): pico dominante en **7 ms** (110 gaps) y picos
  secundarios en 10/13/17/20/23... ms = rejilla de cuantización del intervalo
  de conexión BT (~3.3 ms por paso, suelo 6.7 ms). Nada por debajo de ~6.5 ms:
  límite del protocolo Bluetooth, no un defecto.

| Modo | Rejilla de cuantización | Suelo | Polling rate |
|---|---|---|---|
| **Cable (USB)** | 1 ms | 1 ms | **1000 Hz** |
| **Bluetooth** | ~3.3 ms | ~6.7 ms | **~150 Hz** |

**Lectura:**

- El cable cumple los 1000 Hz anunciados: enlace USB perfecto.
- El BT rinde cerca del óptimo del protocolo; para escritura la diferencia es
  imperceptible (la pulsación humana dura ~50 ms, 7 veces el intervalo BT).
- El problema original (ráfagas de letras) no tenía relación con el polling
  rate: era el autosuspend del adaptador AX210, ya corregido.
- Nota: el `eventX` del teclado cambia al alternar BT/cable (reconexion por
  otro bus reasigna números); localizarlo con `--list` o
  `grep -A4 0003:3434 /proc/bus/input/devices`.

## 8. Referencias de comandos útiles

```bash
# estado de energía del adaptador
cat /sys/bus/usb/devices/1-4/power/control

# historial de conexiones del teclado (kernel)
journalctl -k | grep "0005:3434:02D1"

# logs de BT en vivo
journalctl -f | grep -i bluetooth
sudo btmon
```

---

## 9. Regresión detectada: 09/10/2026 ~15:10 CEST

**Síntoma:** ráfagas de teclas por BT ("se le iba la pinza"); el usuario terminó
conectando por cable a las 15:11:56.

**Evidencia recogida:**

| Comprobación | Valor actual | Esperado con la corrección |
|---|---|---|
| `/sys/bus/usb/devices/1-4/power/control` | **`auto`** ⚠️ | `on` |
| `power/autosuspend_delay_ms` | 2000 | — |
| `power/runtime_status` | **`suspended`** ⚠️ | activo |
| Regla udev `/etc/udev/rules.d/90-ax210-bt-autosuspend.rules` | existe, intacta | — |
| hwdb `60-autosuspend.hwdb` (systemd 261.2) | AX210 `8087:0032` **no** está listado | — |
| Actualizaciones bluez/systemd/kernel desde 30/09 | ninguna | — |

**Línea temporal de hoy (arranque 09/10 01:58:33):**

| Hora | Evento |
|---|---|
| 01:58:11 | Arranque limpio: firmware AX210 OK (`202-5.26`), sin errores hci0 |
| 01:58:33 | Teclado conecta por BT (uhid `000A`) |
| **12:09:32** | **Reconexión silenciosa BT** (uhid `000B`) — mismo patrón que el 30/09 |
| **15:11:40** | **Reconexión silenciosa BT** (uhid `000C`) tras el episodio de ráfagas |
| 15:11:56 | Usuario conecta el cable (USB `000D`–`000F`), luego reenumera (`0010`–`0012`) |

**Diagnóstico:** la corrección de 30/09 (regla udev) se ha **perdido**: el
adaptador está otra vez en `auto` + retardo 2 s y **suspendido en runtime**.
El patrón de micro-cortes/ráfagas es idéntico, lo que refuerza el diagnóstico
original (autosuspend del AX210). No hay proceso localizador claro: PPD
(`power-profiles-daemon`, activo pero inútil aquí — equipo sin batería) no
escribe `power/control` (verificado con `strings`), TLP inactivo, el hwdb de
systemd no marca el AX210 y no hubo re-enumeración USB que re-escribiera el
atributo. Sea cual sea el mecanismo, la regla udev (que solo actúa en el
evento `add`) no es suficiente.

**Corrección propuesta (definitiva, inmune a cualquier restauración del valor):**

1. Inmediata, sin reiniciar:
   ```bash
   echo on | sudo tee /sys/bus/usb/devices/1-4/power/control
   ```
2. Permanente por línea de arranque (desktop sin batería; desactiva el
   autosuspend USB a nivel del kernel — ningún demonio puede revertirlo):
   ```bash
   sudo nano /etc/default/grub   # en GRUB_CMDLINE_LINUX_DEFAULT añadir: usbcore.autosuspend=-1
   sudo grub-mkconfig -o /boot/grub/grub.cfg
   ```
3. Opcional: desactivar PPD en este equipo de escritorio:
   ```bash
   sudo systemctl mask power-profiles-daemon.service
   ```

**Verificación tras aplicar:** `cat /sys/bus/usb/devices/1-4/power/control`
(aunque siga en `auto`, con `usbcore.autosuspend=-1` el kernel no suspende),
monitorizar 2–3 días de uso BT. Si las ráfagas persisten **con autosuspend
desactivado**, siguiente hipótesis: firmware del propio Keychron K13 Pro o
interferencia RF; capturar con `sudo btmon -w /tmp/btsnoop.log` durante el
episodio.

---

## 10. Segunda regresión: 25/10/2026 — autosuspend DESCARTADO

**Síntoma:** ráfagas de teclas otra vez hoy (coinciden con reconexiones de las
12:19 y 15:35; a las 12:20 avisos `KKeyServer` y a las 15:35:59 fallo de
autenticación en el bloqueador de pantalla — ráfaga tecleando la contraseña).

**Estado actual del subsistema USB (arranque 24/10 18:16):**

| Comprobación | Valor | Conclusión |
|---|---|---|
| `/proc/cmdline` | contiene `usbcore.autosuspend=-1` | corrección definitiva **aplicada** ✅ |
| `1-4/power/autosuspend_delay_ms` | `-1000` (todos los dispositivos) | autosuspend globalmente desactivado |
| `1-4/power/runtime_suspended_time` | **0 ms** | el adaptador **nunca se ha suspendido** desde el arranque |
| `1-4/power/runtime_status` | `active` | sin cortes USB |
| reenumeraciones USB del adaptador | ninguna (device 3 desde el arranque) | estable |
| errores hci0 / kernel BT | ninguno | enlace limpio a nivel de host |
| suspend/resume del sistema | ninguno | descartado |
| WiFi AX210 (`phy0`) | soft-blocked | descartada coexistencia |
| actualizaciones bluez/kernel/firmware desde 09/10 | ninguna registrada | descarta regresión por paquete |

**Diagnóstico nuevo:** con el autosuspend del adaptador **verificado como
inactivo**, las ráfagas siguen produciéndose y van siempre precedidas de una
**reconexión Bluetooth de nivel de enlace** (nueva instancia uhid: `000A` en
el arranque, `000B` 12:19:06, `000C` 15:35:56). Es decir, el corte ocurre en
el **enlace BT radio** (teclado ↔ adaptador), no en el USB del adaptador. La
correa de eventos "pausa → microcorte → ráfaga" se explica ahora por:

1. **Hipótesis principal — firmware/ahorro de energía del propio Keychron K13
   Pro (BT HID v1.32):** el teclado entra en su sueño profundo y suelta el
   enlace; al reconectar reenvía en ráfaga los informes retenidos. Keychron
   publica fixes exactamente para esto. Ya se tiene descargado el utilitario
   `Keychron_Bt_Firmware_Upgrade_v0.14.exe` (visto en backups esta madrugada).
2. **Batería baja del teclado** (no se puede leer por BlueZ: no expone
   `BatteryPercentage`; comprobar el LED físico del teclado).
3. **Interferencia RF del entorno** (mismo sitio, mismo adaptador; único otro
   dispositivo emparejado: Redmi Buds 6, actualmente desconectado).

**Acciones recomendadas (orden):**

1. **Actualizar el firmware BT del Keychron K13 Pro** con el utilitario v0.14
   (Windows/Boot Camp) antes de nada: es la causa más probable restante.
2. **Instalar `bluez-utils`** (proporciona `btmon` y `bluetoothctl`, hoy NO
   instalados — el plan de captura del informe no era ejecutable):
   ```bash
   sudo pacman -S bluez-utils
   sudo btmon -w /tmp/btsnoop.log   # dejar corriendo hasta el próximo episodio
   ```
   En el log mirar el **motivo de desconexión**:
   - `Connection Timeout (0x08)` → pérdida de enlace por radio (interferencia
     o sueño agresivo del teclado).
   - `Remote User Terminated Connection (0x13)` → el teclado suelta el enlace
     a propósito → firmware del teclado confirmado.
3. Cargar completamente el teclado y observar si la frecuencia baja.
4. Si tras actualizar firmware persiste: probar otro adaptador BT o el
   receptor USB 2.4 GHz del K13 Pro (si el modelo lo incluye) para aislar el
   AX210.

**Nota:** no desinstalar la corrección `usbcore.autosuspend=-1`: sigue siendo
barata y evita una capa de problemas reales, pero **no era la causa** de las
ráfagas.

---

## 11. Auditoría del firmware (QMK) del K13 Pro — 25/10/2026

Código descargado en `firmware_qmk/` (sparse + blobless, solo
`keyboards/keychron`; el repo completo pesa 331 MB):

| Directorio | Rama | Último commit de `k13_pro` |
|---|---|---|
| `firmware_qmk/bluetooth_playground/` | `bluetooth_playground` | 03/12/2024 |
| `firmware_qmk/wls_2025q1/` | `wls_2025q1` | **05/09/2025** ← la más reciente |

**Hecho clave:** `bluetooth_playground` va **6337 commits por detrás** de la
línea actual; las correcciones BT de Keychron de 2025 están en `wls_2025q1`.
Además el K13 Pro **no existe** en `master` ni `2025q3` (Keychron nunca lo ha
fusionado a su rama principal).

### Arquitectura

STM32L432 (QMK/ChibiOS: matriz, RGB, glue) + **módulo CKBT51** (stack
Bluetooth, firmware **cerrado** sin fuente en el repo) comunicados por
**UART 460800 bps** con protocolo de comandos + ACK (`ckbt51.c`). La matriz
(6×17) se sondea por GPIO + registro de desplazamiento 74HC595 a ~1 kHz y
debounce 5 ms. Los informes HID salen hacia el módulo con un buffer propio.

### Hallazgos relevantes para las ráfagas

1. **Bug de doble envío en la rama vieja (ya corregido por Keychron en
   `wls_2025q1`):** en `bluetooth.c`, el camino rápido de
   `bluetooth_send_keyboard()` envía el informe directamente sin comprobar
   `report_buffer_get_retry() == 0`. Tras un `ACK_FIFO_FULL_ERROR` el STM32
   retransmite el informe retenido cada 7 ms (misma *sn*, deduplicada por el
   módulo); mientras, el bug permite que un informe nuevo salte por delante
   con la cola en estado inconsistente → informes duplicados/obsoletos en el
   enlace = **ráfagas de pulsaciones**. La versión 2025 unifica KB/NKRO por
   cola con la comprobación correcta y añade `send_string_task()`.
2. **Keychron conoce la familia de bugs de "wake":** comentario literal en
   `bluetooth_connect()`: *"Work around empty report after wakeup, which leads
   to reconnect/disconnected loop"*. Encaja con nuestro patrón (ráfaga tras
   pausa > 1–2 s + reconexión silenciosa).
3. **Carrera de sueño profundo (`lpm_stm32l432.c`):** tras 1 s sin actividad
   (`RUN_MODE_PROCESS_TIME=1000`) el STM32 entra en **PM_STOP1** (deep stop).
   Al despertar re-inicializa clocks/UART/timers, pero **los bytes UART que el
   módulo envió durante el sueño se pierden** ( overrun ): ACK e,
   importantísimo, el evento `EVT_DISCONNECTED`. La cola de informes
   (`REPORT_BUFFER_QUEUE_SIZE=512` ≈ 17 KB) **solo se vacía al recibir ese
   evento**; si se perdió, el STM32 sigue encolando como si estuviera
   conectado y, al restablecerse el enlace, el backlog (hasta 512 informes ≈
   256 caracteres) se drena a ~3 ms por informe → **ráfaga**.
4. **Robustez:** `ckbt51_task()` parsea paquetes con longitud de hasta 255
   bytes en un `uint8_t buf[32]` **sin comprobar el límite** → posible
   desbordamiento de pila con ruido/malformación en la UART.
5. **Latencia de envío:** cada comando UART hace un **busy-wait bloqueante de
   3 ms** (`CKBT51_WAKE_WAIT_TIME=3000`: pulsos INT 3×1 ms para despertar al
   módulo) dentro del bucle principal de QMK → el housekeeping (y el escaneo
   de matriz) se bloquea ~3 ms por informe. Techo MCU→módulo ~333 informes/s;
   irrelevante frente al techo radio de ~150 Hz ya medido.
6. **No hay margen real de mejora del polling rate desde este código:** el
   intervalo de conexión lo fijan el módulo CKBT51 (cerrado) y el host
   (Linux, rejilla ~7 ms medida). El cable ya da 1000 Hz verificados.

### Acciones derivadas (actualización del plan de la sección 10)

1. **Actualizar el firmware del teclado** (utilitario Keychron v0.14): lleva
   implícitas las correcciones tipo `wls_2025q1` (punto 1) y cambios en el
   módulo. Sigue siendo el paso principal.
2. Si se quiere **compilar el propio**: usar `wls_2025q1` **no**
   `bluetooth_playground`. Requiere materializar el repo completo (submódulos
   ChibiOS) y flashear por DFU (`bootloader: stm32-dfu`, `bootmagic: true`).
   Ajustes interesantes a probar en un build propio:
   - `RUN_MODE_PROCESS_TIME`: subirlo (p. ej. 3000–5000 ms) o cambiar
     `LOW_POWER_MODE` de `PM_STOP1` a `PM_SLEEP` para eliminar la carrera de
     wake (a costa de batería).
   - Añadir comprobación de longitud en `ckbt51_task()` (fix del buf[32]).
   - Vaciar `report_buffer` también en `EVT_RECONNECTING`, no solo en
     `EVT_DISCONNECTED` (defensa ante el evento perdido).
3. **Captura con `btmon`** (sección 10) sigue siendo imprescindible para
   saber quién corta el enlace: motivo `0x08`/`0x13` iniciado por el módulo →
   confirma punto 3; iniciado por el host → revisaría BlueZ/kernel.

---

## 12. Ejecución SDD multiagente sobre `wls_2025q1` (25/10/2026 21:00–22:00)

**Spec y roles:** `SDD_k13pro.md` (WP-000…900, gate §6). Roles definidos y
persistidos en `.kilo/agent/` (`orchestrator`, `implementer`, `reviewer`,
`tester`, `researcher`); esta sesión ejerció de orquestador con subagentes.

**Referencia externa (WP-000, ZMK):** la práctica clave —"al perder el enlace:
flush de estado + informe cero"— coincide con el fix WP-102a ya aplicado; los
parámetros de radio (intervalo/latencia) no son gobernalles desde el MCU
(CKBT51 cerrado). QMK mainline trae `asym_eager_defer_pk` (debounce asimétrico):
descartado por defecto tras VETO del reviewer (riesgo de pulsaciones fantasma
en el bus HC595 compartido de esta matriz), queda opt-in para medir.

**Parche:** `patches/k13-audit.patch` (219 líneas, 6 ficheros, todo bajo
`keyboards/keychron/`; **sin commitear**, working tree de la rama
`k13-pro-audit`). Notas por WP en `patches/notes.md`.

| WP | Cambio | Veredicto |
|---|---|---|
| 101 | Parser UART: cota de trama 3–64 con buf `PACKET_MAX_LEN` (evita desbordamiento Y descarte de tramas legítimas: MODULE_INFO len 42, OTA ≤ 61); `dfu_tx` troceado con bucle ≤ 25+31n | APROBADO (ronda 2) |
| 102a | `EVT_RECONNECTING` vacía la cola de informes pendiente (mitiga la ráfaga por evento perdido) | APROBADO |
| 103 | `ACK_FIFO_FULL` resetea el timer de reenvío (no reenvío impulsivo) | APROBADO |
| 104 | Eliminada variable muerta `bluetooth_report_protocol` (0 lecturas) | APROBADO |
| 201 | Ruta rápida de wake INT bajo `#ifdef CKBT51_FAST_WAKE` **OFF** por defecto (comportamiento idéntico; experimental para hardware) | APROBADO |
| 202 | `DEBOUNCE_TYPE` NO activado; comentado como experimento opt-in | APROBADO (revertido) |
| 203 | Tunables `RUN_MODE_PROCESS_TIME`/`LOW_POWER_MODE` documentados en `config.h` | APROBADO |

**BUILD-GATE: OK** — 4/4 variantes compiladas desde cero (`ansi/rgb` text
57166, `ansi/white` 48884, `iso/rgb` 57178, `iso/white` 48880; +64 B sobre el
baseline intacto 57102). Sufijos DFU 1.1a estándar en los 4 `.bin` (PAR
`0483:DF11`, default stm32-dfu de QMK; CRC sobre imagen+12 B — el clon
`tools/dfu-suffix` se corrigió tras el advisory del verifier, 4 CRCs
distintos, `-c` OK). `qmk lint`: 2 avisos preexistentes ajenos al parche.

**Pendientes (hardware, usuario):**
1. Decidir vía de actualización: **.exe Keychron v0.14** (cubre también el
   módulo CKBT51 — sigue siendo lo recomendado) **o** flashear estos `.bin`
   (solo MCU): DFU vía `qmk flash`/QMK Toolbox/`dfu-util -a 0 -s 0x08000000:leave
   -D <bin>` entrando en DFU (bootmagic: mantener la tecla Esc mientras se
   conecta el USB).
2. Con `bluez-utils` instalado: capturar `btmon` en el siguiente episodio
   (motivo 0x08/0x13) — discrimina teclado vs. host/interferencia.
3. Si persisten ráfagas tras parche: pruebas opt-in por orden —
   `RUN_MODE_PROCESS_TIME`↑ (o `LOW_POWER_MODE=PM_SLEEP`),
   `CKBT51_FAST_WAKE`, y medir polling/latencia con `tools/medir_polling.py`
   (tap test) antes/después.
4. WP-102(b) (estado del módulo post-wake) requiere medición real; no se
   implementó a ciegas.

---

## 13. Ronda 2 SDD: polling BT + teclas sueltas, todos los teclados (25/10 23:20–00:50)

**Hallazgo clave del scoping:** el driver CKBT51 expone `module_param_t` con
`report_rate` (90 | **133 Hz**), `reconnect_timeout` (segundos de reintentos
tras caída) y todos los Keychron del repo los fijaban a **90 Hz / 5 s**. Además
`ckbt51_param_init()` del K13 Pro solo se ejecutaba si el módulo arrancaba en
<1 s tras el boot del MCU: si no, **los parámetros no se aplicaban nunca**.

### Parches ronda 2 (todos APROBADOS por reviewer; BUILD-GATE OK 4/4 + k14_pro)

| WP | Cambio | Efecto esperado |
|---|---|---|
| 110 | `report_rate` 90→**133 Hz** en los 53 bloques CKBT51 (26 teclados) | +48 % informes/s por BT (techo documentado del módulo) |
| 111a | `reconnect_timeout` 5→**60 s** (mismos bloques) | el módulo reintenta solo 1 min tras caída → menos "reconexión al teclear" |
| 111b | Ventana de `ckbt51_param_init` 1 s→5 s (K13 Pro) | garantiza que los params se aplican aunque el módulo arranque lento |
| 107 | Gate LPM: no entrar en STOP1 con cola de informes/retry/eventos pendiente (compartido, todos) | elimina el drenaje de backlog tras pausa = ráfaga post-wake |
| 108 | Rate-limit 500 ms de `bluetooth_connect()` (compartido) | fin de la tormenta de comandos connect por pulsación con enlace caído |

Tamaños `text`: ansi/rgb **57222** · ansi/white **48940** · iso/rgb **57234** ·
iso/white **48936** · k14_pro/ansi/rgb **56862**. Patch acumulado (rondas 1+2):
`patches/k13-audit.patch`, 33 ficheros, todo bajo `keyboards/keychron/`, sin
commitear (rama `k13-pro-audit`).

**Nota LKBT51:** el módulo LKBT51 (pila SPI de otros modelos) se dejó con sus
valores de fábrica (90/5): semántica no verificada, VETO del reviewer.
**ISO ES:** las variantes `iso/*` están en el gate; la Ñ se configura en el
host con VIA (`via_json/k13_pro_iso_*.json`), no hay nada que cambiar en el
firmware.

### Herramientas nuevas
- `tools/bt_tune.sh` (invocar con `bash tools/bt_tune.sh …`):
  - `status` — autosuspend del adaptador, conexión BlueZ, (re)conexiones del boot.
  - `capture` — btmon a fichero para el próximo episodio (reason 0x08 = radio /
    0x13 = el teclado corta). Requiere `sudo pacman -S bluez-utils`.
  - `poll` — tap test con `tools/medir_polling.py -m tap`: antes/después de flashear.
- `tools/dfu-suffix` v4 — clon python conforme al tool real 0.11: **bcdDFU
  debe ser `0x0100`** en ficheros raw (el `0x011A` que escribía la v3 lo hacía
  pasar por contenedor DfuSe y dfu-util rechazaba el raw download con `-s`);
  bcdDevice `0xFFFF`, CRC `~crc32(imagen+12B)`. Bins re-sufijados y validados
  con `/usr/bin/dfu-suffix -c` (6/6); `flash_k13.sh` prechequea con el tool real.

### Cómo flashear (decisión del usuario)
1. **Recomendada:** updater oficial `Keychron_Bt_Firmware_Upgrade_v0.14.exe`
   (Windows) — actualiza MCU **y** módulo CKBT51. Nuestros parches NO sustituyen
   al firmware del módulo; si las ráfagas vienen del módulo, solo el .exe ayuda.
2. **Nuestro build (solo MCU):** entrar en DFU (mantener **Esc** mientras se
   conecta el USB-C, bootmagic) y:
   ```bash
   sudo dfu-util -a 0 -s 0x08000000:leave -D \
     firmware_qmk/wls_2025q1/.build/keychron_k13_pro_iso_rgb_default.bin
   ```
   (o QMK Toolbox / web flasher). Ojo: flashear el MCU **pisa** el firmware
   Keychron de esa mitad; el módulo sigue con el suyo.

### Validación pendiente (hardware)
0. **Baseline pre-flasheo (26/10 00:34, BT, tap test 10 s):** 150 taps, suelo
   **7 ms**, rejilla dominante 7/10/13/17/20 ms (paso ~3,3 ms) → ~143-150
   informes/s. Idéntico a la medición de septiembre ⇒ el enlace ya rinde por
   encima de los 90 Hz nominales que fija el firmware de fábrica — evidencia
   adicional de que `ckbt51_param_init` no se aplicaba (ventana <1 s, WP-111b)
   o de que `report_rate` no gobierna el intervalo real del enlace BR/EDR
   (lo negocian módulo y host). Expectativa tras flashear 133 Hz: suelo
   ~7-7,5 ms (mejora de polling neutra/marginal); el valor del patch está en
   la fiabilidad (WP-102a/107/108/111a), no en el throughput.
1. `bash tools/bt_tune.sh poll` ANTES de flashear (baseline) y DESPUÉS: el suelo
   de gaps debe moverse hacia ~7.5 ms si `report_rate=133` aplica.
2. Episodio de ráfagas → `bash tools/bt_tune.sh capture` y leer reason.
3. Uso normal 3 días por BT; comparar frecuencia de reconexiones
   (`bash tools/bt_tune.sh status`).
4. Experimentos opt-in si persisten problemas: `CKBT51_FAST_WAKE`,
   `RUN_MODE_PROCESS_TIME`↑ / `PM_SLEEP`, debounce `asym_eager_defer_pk`
   (todos documentados en SDD §3/§8; ninguno activo por defecto).

**Riesgo residual aceptado:** conmutar BT→USB→BT en <500 ms puede suprimir un
`connect` (rate-limit); se recupera solo al siguiente reintento (>500 ms).

---

## 14. Análisis final: tests CI de GitHub y riesgo de brick (26/10/2026)

### 14.1 Riesgo de brick: MUY BAJO (recuperación siempre disponible)

| Capa | Por qué no hay brick | Recuperación |
|---|---|---|
| **Bootloader** | `bootloader: stm32-dfu` = bootloader **ROM** del STM32L432 (system memory): físicamente no se puede sobreescribir con un flasheo de aplicación (`-s 0x08000000` solo toca la app) | siempre existe |
| **Entrada en DFU** | 2 vías: (a) bootmagic — mantener **Esc** al conectar; (b) **botón físico de reset bajo la barra espaciadora** (readme del K13 Pro: switch a Off → mantener Esc/reset → switch a Cable) | independiente de nuestro firmware |
| **Nuestro patch** | no toca NADA del arranque temprano: ni `matrix_init`, ni bootmagic, ni init USB, ni EEPROM; los cambios corren en housekeeping/eventos BT, después de que USB y DFU ya funcionan | — |
| **Flash** | STM32L432 = 256 KB; nuestro bin ≈ 59 KB (text+data, variante via similar) → margen enorme; si no cupiera, el link falla ANTES de generar bin (imposible flashear algo que desborde) | — |
| **RAM** | data+bss = 65536 B clavados (64 KB, todo estático, stack ChibiOS incluido) — el árbol de Keychron ya vive al límite; nuestro patch **no incrementa data/bss** (gate verificado), solo +56 B de código | — |
| **Flasheo interrumpido** | si se corta a mitad, el bootloader ROM sigue intacto: reentrar en DFU y repetir `dfu-util` | reset+Esc |
| **Variante errónea** (p. ej. bin `rgb` en placa `white`) | falla el init del driver LED ausente (I2C con timeouts, no cuelga); teclado sigue usable; no es brick | reflasar variante correcta |
| **Módulo CKBT51** (radio) | no lo flasheamos: solo `set_param` en runtime con valores documentados (90\|133 Hz; 2–254 s). Peor caso teórico: BT raro hasta factory-reset del teclado (re-ejecuta `ckbt51_param_init`) o reflash con el .exe oficial | factory reset / .exe v0.14 |
| **Escape universal** | el transporte **USB por cable es independiente del módulo BT**: aunque el lado BT quedara inutilizable, el teclado funciona y se reflasha por cable | siempre |

Conclusión: con bootloader ROM + botón de reset físico + patch que no toca el
arranque, el escenario "teclado muerto sin recuperación" no existe en la
práctica. El único riesgo real es funcional (BT raro), reversible por DFU.

### 14.2 Tests en GitHub que aplican a este cambio

CI del fork Keychron/qmk_firmware (20 workflows activos, heredados de QMK).
Para un PR que **solo toca `keyboards/**`** se disparan:

| Workflow | Qué valida | Aplica a nuestro patch |
|---|---|---|
| `lint.yml` "PR Lint keyboards" | `qmk lint` + `qmk info -l` por teclado cambiado; **`qmk format-text` debe dejar diff cero**; `qmk ci-validate-aliases` | **SÍ** — espejo local ejecutado (resultado abajo) |
| `unit_test.yml` | `qmk test-c` (googletest) | NO se dispara (paths: builddefs/quantum/platforms/tmk_core/tests/*.mk — no tocados) |
| `format.yml` | clang-format en drivers/quantum/platforms… | NO (paths fuera de keyboards/) |
| `ci_build_major_branch*` | build masivo en ramas mayores | NO (solo push a master/develop) |

Espejo local del gate real (lint.yml) sobre el working tree:

| Check CI | Resultado |
|---|---|
| `qmk format-text` (diff-cero) | APLICADO: clang-format retocó los 33 ficheros (whitespace-only, tamaños de binarios idénticos); rebuild sanity 6/6 OK; patch regenerado (1343 líneas) |
| `qmk lint` k13 ansi/rgb + iso/rgb | PASS — solo los 2–4 fallos PREEXISTENTES del fork (rules.mk vacío, keymap via, rgb.c sin header); ninguno nuevo |
| `qmk ci-validate-aliases` | SKIP — 746 fallos preexistentes del fork en teclados ajenos al patch; ninguno atribuible |
| `qmk test-c` (unit tests, no los dispara CI para keyboards/**) | **PASS — 77 suites, 0 fallos** |
| Artefacto via | `.build/keychron_k13_pro_iso_rgb_via.bin` — 61 736 B (text 59 822), flash usado 23,6 % de 256 KB |

### 14.3 VIA/usevia.app no conecta en Linux (resuelto)

Chromium detecta el teclado (3434:02d1, `/dev/hidraw10-12`) pero no puede
abrirlo: nodos `0600 root` y **sin regla udev** para el VID de Keychron.
Arreglo (una vez, con sudo):

```bash
sudo tee /etc/udev/rules.d/70-keychron-via.rules <<'EOF'
KERNEL=="hidraw*", SUBSYSTEM=="hidraw", ATTRS{idVendor}=="3434", TAG+="uaccess"
EOF
sudo udevadm control --reload-rules && sudo udevadm trigger --subsystem-match=hidraw
```

Reconectar el teclado y reintentar en usevia.app (o engine.keychron.com).
Verificación: `ls -l /dev/hidraw10` debe dar acceso al usuario.
Nota: con Keychron **Engine** (engine.keychron.com) conectó y exportó el
backup a la primera; en usevia.app hay que cargar a mano la definición
`via_json/k13_pro_iso_rgb.json` (pestaña Diseño) — Keychron no publica el
K13 Pro en la base remota de VIA.

---

## 15. Flasheo realizado con éxito (26/10/2026 ~01:00)

- **Bin flasheado:** `keychron_k13_pro_iso_rgb_via.bin` (61 736 B; raw
  61 720 + sufijo DFU 1.1a) vía `tools/flash_k13.sh` (dfu-util 0.11,
  bootloader ROM `0483:df11`, sin sudo gracias a `60-dfuse.rules`).
- **Incidencia resuelta:** primer intento rechazado con *"This is a DfuSe
  file, not meant for raw download"* — causa: el wrapper de sufijo escribía
  `bcdDFU=0x011A`, que dfu-util 0.11 interpreta como contenedor DfuSe
  (`main.c:438`/`dfuse.c:751`); el raw correcto es `0x0100`. Wrapper v4
  corregido; los 6 bins re-sufijados y validados con el `dfu-suffix` real
  (6/6, colas byte-idénticas al tool real). Ningún daño: el fallo fue en el
  parseo del fichero, antes de tocar flash.
- **Commits** (rama `k13-pro-audit`, sin push — autorizados por el usuario):
  | Hash | Contenido |
  |---|---|
  | `10b7388` | bluetooth/ (5 fich): WP-101/102a/103/104/107/108/201 |
  | `6f5b50a` | 25 teclados keychron: WP-110/111a (params CKBT51 133 Hz/60 s) |
  | `97e9727` | k13_pro/ (3 fich): WP-111b/202/203 |
  `git status` limpio; `patches/k13-audit.patch` = snapshot pre-commit.
  *Nota de revisión final:* los commits incluyen churn de `clang-format` en
  líneas ajenas a los WPs (firmas `uint8_t*`→`* `, alineaciones, macros DIP
  colapsadas; 13 ficheros de params afectados). Es inerte (whitespace, bins
  idénticos) y se conserva para no reescribir historia; si se propone PR
  upstream, conviene separarlo en un commit de formato aparte.
- **Config del usuario:** backup exportado desde Keychron Engine ANTES del
  flasheo; reimportado después (protocolo VIA v12 + LAYOUT_iso_91 idénticos).

### Validación post-flasheo (pendiente, usuario)
1. ✅ **Tap test post-flasheo (26/10 01:24):** 312 taps, suelo **5 ms**
   (141 gaps finos), techo **~200 informes/s** vs baseline pre-flasheo 7 ms /
   ~143 informes/s → **+40 % de polling confirmado**. La rejilla sigue en
   ~3,3 ms (7/10/13/17) pero el suelo bajó de 7→5 ms: el módulo ahora entrega
   por encima de los 150 Hz que medíamos antes — coherente con
   `report_rate=133` aplicado (WP-110/111b) más la negociación del host.
2. 2-3 días de uso BT normal: contar episodios de ráfagas/teclas sueltas.
3. Si aparece episodio: `bash tools/bt_tune.sh capture` → reason 0x08/0x13.
4. Experimentos opt-in si hicieran falta (SDD §8): `CKBT51_FAST_WAKE`,
   `RUN_MODE_PROCESS_TIME`, debounce asimétrico — cada uno requiere rebuild
   y medición.
5. Opcional: PR/ fork en GitHub si se quiere compartir los parches con
   Keychron (los commits están listos para cherry-pick).

---

## 16. PR público a Keychron (26/10/2026)

**https://github.com/Keychron/qmk_firmware/pull/529** — estado OPEN.

| Dato | Valor |
|---|---|
| Base | `wls_2025q1` (= rama que contiene el K13 Pro) |
| Head | `thementalcoding:k13-pro-bt-fixes` (fork creado) |
| Commits | `e14aa56` bluetooth/ · `b7d9962` params 25 teclados · `90f4d1d` k13_pro/ |
| Autor | TheMentalCoding `<312162298+thementalcoding@users.noreply.github.com>` |
| Formato | clang-format **19.1.7** (= contenedor CI), `format-text` diff cero |
| Descripción | `PR-529.md` (motivación, cambios, mediciones 7→5 ms, testing, limitaciones) |
| CI inicial | `triage` SUCCESS; lint/format pendientes de aprobación de workflows (primer PR del fork) |

La rama local de trabajo `k13-pro-audit` se conserva intacta como respaldo; el
PR usa una rama limpia (`k13-pro-bt-fixes`) reconstruida desde la base.

---

## 17. Publicación pública del proyecto (26/10/2026)

**Repo:** https://github.com/thementalcoding/keychron-k13-pro-firmware
(**público**, GPL-2.0, topics: qmk/keychron/k13-pro/firmware/bluetooth)

| Contenido | Detalle |
|---|---|
| `README.md` | Bilingüe (EN + inicio rápido ES): qué arregla, tabla de variantes por PID, flasheo DFU, backup/restore, recuperación, limitaciones, build from source, créditos |
| `firmware/` | 6 bins (K13 ISO/ANSI × RGB/white + `iso_rgb_via` recomendado + K14 spot) + `SHA256SUMS` |
| `docs/` | `AUDIT.md` (informe saneado), `SDD.md`, `PR-529.md` |
| `patches/` | `k13-audit.patch` + `notes.md` |
| `tools/` | `flash_k13.sh`, `bt_tune.sh`, `dfu-suffix`, `qmk_env.sh`, `medir_polling.py` (rutas relativas, ejecutables) |
| Release | **v1.0.0** con los 6 bins + checksums como assets descargables |

**Privacidad:** docs y scripts saneados — MACs, hostname, usuario y rutas
locales/IPs sustituidos (`grep` de verificación: 0 coincidencias). Los binarios
no contienen datos personales. Checksums publicados para verificación. Aviso de
"no oficial / úsalo bajo tu responsabilidad" y de recuperación ROM DFU incluido
en README.

---

## 18. CI y seguridad en GitHub (repo público)

**CI (verde):** workflow `checks` — obligatorio en `main` vía branch protection
(status `strict`). Verifica en cada push/PR:
- `tools/verify_bins.py`: sufijo DFU de los 6 bins (bcdDFU `0x0100`, "UFD",
  bLength, VID/PID `0483:DF11`, CRC `~crc32`) y tamaño < 256 KiB.
- `sha256sum -c SHA256SUMS` (raíz del repo).
- `bash -n`, **shellcheck** (0 warnings), `py_compile` de todos los scripts.
- **Guard de privacidad** (`tools/check_sanitization.py`): falla si reaparece
  una MAC, hostname, ruta `$HOME/...` o IP del entorno de origen.

**Build reproducible:** workflow `build` — `workflow_dispatch` + semanal +
tags. Clona Keychron `wls_2025q1` en el commit base pinneado `c8b2b23`
(submódulos chibios/contrib/printf/lufa), aplica `patches/k13-audit.patch`,
compila `iso/rgb:via` en el contenedor QMK fijado **por digest**, valida el
bin y lo publica como artifact. El schedule semanal actúa de **detector de
drift** upstream (si Keychron mueve el árbol, el `git apply` falla).

**Endurecimiento del repo:**
- Actions fijadas **por SHA** (checkout/setup-python/upload-artifact/
  scorecard/upload-sarif); contenedor por digest; `GITHUB_TOKEN` read-only;
  Actions restringidas a "selected"; `persist-credentials: false`.
- **Secret scanning + push protection** activos; **Dependabot alerts**;
  **private vulnerability reporting**; `SECURITY.md`.
- Branch protection en `main`: checks obligatorios, historial lineal, sin
  force-push ni borrado; borrado de ramas al mergear; wiki off, Discussions on.
- `CONTRIBUTING.md`, plantillas de issue/PR, labels (`bug`, `enhancement`,
  `good first issue`, `hardware-testing`, `upstream`), Dependabot semanal.

**Pendiente/opcional:** re-activar `scorecard.yml` cuando OpenSSF arregle su
error de gcr.io (workflow deshabilitado con comentario), mergear los PRs de
Dependabot (#1 innecesario tras desactivar scorecard; #2–#5 en verde),
attestations de artifacts + firma GPG de releases, CodeQL, CHANGELOG/semver y
job ligero "el patch aplica" filtrado por `patches/**`.
