# Notas de implementación — auditoría K13 Pro (rama `k13-pro-audit`)

Repo: `firmware_qmk/wls_2025q1` · **Sin commits** (todo en working tree; snapshot = `k13-audit.patch`, `git diff`).
Builds: `qmk compile -kb keychron/k13_pro/<variante>/ -km default` tras cada WP; estados intermedios anotados abajo.
Tamaño línea `text` del .elf ansi/rgb: **baseline 57102 → final 57598** (+496; de esos ~+456 es el debounce de WP-202).

## WP-101 · Robustez parser UART — OK
- Ficheros: `keyboards/keychron/bluetooth/ckbt51.c` → `ckbt51_task()`.
- Qué cambia: el campo `len` del sub-header (3 bytes tras `0xAA 0x57`) se valida ahora en `buf[0] >= 3 && buf[0] <= 32`
  además del chequeo `~len`; fuera de cota se descartan los bytes consumidos y se resync (búsqueda de próximo `0xAA 0x57`).
  El `else // TODO: Error handle` del checksum pasa a contar frames corruptos con dprintf cada 16.
- Desviación: el SDD escribe el descarte como `len > 3+32`; sin embargo el bucle de payload lee **`len` bytes en `uint8_t buf[32]`**
  (el `len` del protocolo NO incluye el sub-header: es `evt(1)+data+cks(2)`), por lo que la cota segura real es 32; `33..35` desbordaría.
  Con `<=32` ningún frame legítimo real se pierde (GET_CONFIG rsp ≈25, OTA/ACK ≤28).
- Build: text 57126 (+24). OK.

## WP-103 · Timer de retransmisión FIFO — OK
- Ficheros: `ckbt51.c` → `ack_handler()`; `report_buffer.c`/`report_buffer.h` (excepción autorizada: setter nuevo).
- Qué cambia: en `ACK_FIFO_FULL_ERROR`, además de `report_buffer_set_retry(10)`, se llama al nuevo
  `report_buffer_reset_retry_timer()` → `retry_time_buffer = sync_timer_read32()` (la misma primitiva que ya usa
  `report_buffer_task()`). Así el reintento espera la ventana de backoff completa (7 ms) en vez de reenviar impulsivamente
  con el timestamp viejo. Semántica `sn`/dedupe intacta; `retry_time_buffer` sigue sin exponer en headers.
- Build: text 57142 (+16). OK.

## WP-104 · Protocolo HID muerto — OK (eliminación)
- Fichero: `bluetooth.c` → global `bluetooth_report_protocol` y `bluetooth_hid_set_protocol()`.
- Qué cambia: `grep -r` en todo el repo (excl. `.build`) confirma que la variable solo se escribía (nunca se leía, ni en
  headers; `keyboards/keychron/common/wireless/*` es una pila separada con su propio código, no la toca). Se elimina el
  global y la escritura muerta; la función queda como no-op con `(void)report_protocol` + comentario. El dispatch
  `EVT_HID_SET_PROTOCOL` se conserva (ningún producer en ckbt51.c hoy). NKRO (vía `keymap_config.nkro`) intacto.
- Build: text 57126 (−16 vs WP-103, código muerto fuera). OK.

## WP-102(a) · Flush del buffer al reconectar — OK
- Fichero: `bluetooth.c` → `bluetooth_event_queue_task()`, `case EVT_RECONNECTING`.
- Qué cambia: si el `report_buffer` no está vacío al recibir `EVT_RECONNECTING` del módulo, se vacía con el mismo helper
  que usa `EVT_DISCONNECTED` (`report_buffer_init()`, resetea cola + `retry` + timer), protegido por
  `#ifndef DISABLE_REPORT_BUFFER`. Evita el drenaje en ráfaga del backlog acumulado con el enlace caído. El resto del
  handler (indicador, `bluetooth_enter_reconnecting`) sin cambios.
- **No hecho: WP-102(b)** (post-LPM `CKBT51_CMD_READ_STATE_REG` en `lpm_stm32l432.c`): fuera de la lista de pasos asignada,
  depende de medir qué informa realmente el módulo tras wake desde STOP1 (validación solo en hardware). Queda para el coordinador.
- Build: text 57142 (+16). OK.

## WP-201 · Wake INT no-bloqueante — OK (OFF por defecto)
- Fichero: `ckbt51.c` → `ckbt51_send_cmd()`.
- Qué cambia: ruta rápida bajo `#ifdef CKBT51_FAST_WAKE` (no definido en ningún config del repo → default sin tocar):
  static `last_cmd_time` (`chVTGetSystemTime`); si el último comando salió hace < `CKBT51_FAST_WAKE_HOLD_MS` (default 50 ms,
  overrideable) se omite la secuencia de 3 toggles INT de ~1 ms pero el paquete se envía igual (el módulo solo apaga su
  UART tras 3 s de inactividad, `CKBT51_WAKE_WAIT_TIME`). Bifurcación `#else` conserva literal el código actual.
- Verificación extra: build temporal con `-DCKBT51_FAST_WAKE` (define añadido y **retirado** después) pasó: text 57206.
- Build default: text 57142 (idéntico al pre-WP-201 → comportamiento default sin cambios). OK.

## WP-202 · Debounce asimétrico — OK
- Fichero: `keyboards/keychron/k13_pro/rules.mk` (raíz del teclado, aplica a las 4 variantes; `keyboard.json` no se tocó).
- Qué cambia: `DEBOUNCE_TYPE = asym_eager_defer_pk` (vía canónica rules.mk; `builddefs/common_features.mk:679` usa `?=`
  → gana la asignación del teclado). `DEBOUNCE` sigue en su default 5. Presion eager (latencia menor), release defer.
- Verificación: las 4 variantes compilan limpias (ansi/rgb, ansi/white, iso/rgb, iso/white); los .elf enlazan el módulo
  nuevo (símbolos `malloc/free` presentes = `asym_eager_defer_pk`; `CH_CFG_USE_MEMCORE TRUE` del chconf común lo permite).
- Text final ansi/rgb: 57598 (≈+456 vs sym_defer_g). Trade-off de latencia real a medir en dispositivo (`medir_polling.py`, diferido al usuario).

## WP-203 · Tunables LPM — OK (ya overridables, solo doc)
- Comprobado: `RUN_MODE_PROCESS_TIME` ya tiene guarda `#ifndef` en `bluetooth/lpm.h:19` y `LOW_POWER_MODE` en
  `bluetooth/bluetooth.h:23` → no hacen falta guards; `lpm.h`/`lpm_stm32l432.c` no se tocaron.
- Fichero: `k13_pro/config.h` → 2 líneas de comentario dentro de `#ifdef KC_BLUETOOTH_ENABLE` documentando ambos overrides
  y el trade-off corriente ociosa/latencia de wake.
- Build final: comentario-only, sin cambio de código.

## Tamaño final (con todo aplicado)
| Variante | text | data | bss |
|---|---|---|---|
| ansi/rgb (baseline → final) | 57102 → 57598 | 1888 | 63648 |
| ansi/white | 49924 | 1872 | 63664 |
| iso/rgb | 57610 | 1892 | 63640 |
| iso/white | 49920 | 1876 | 63656 |

## Cosas NO hechas / fuera del repo
- **Commits: NO** (orden + sandbox); working tree limpio salvo los 6 ficheros del diff.
- **WP-102(b)**: ver arriba (requiere hardware).
- **Fix de entorno fuera del repo**: `tools/dfu-suffix` (clon python del post-proceso DFU) rechazaba el VID `0483` por usar
  `int(x, 0)` (prefijo octal). Cambiado a `int(x, 16)` → ahora los builds terminan con el sufijo DFU correcto y `qmk compile`
  sale 0. Nota: el `.bin` del baseline del verifier estaba **sin sufijo** (fallaba igual). Esto no forma parte del parche.

---

# Rework (ronda 2, tras VETOs del reviewer)

## WP-101 rework — OK
- `ckbt51.c` → `ckbt51_task()`: el buffer de payload pasa de `buf[32]` a `buf[PACKET_MAX_LEN]` (64, ckbt51.h:70) y la cota
  del campo len queda `3 ≤ len ≤ PACKET_MAX_LEN`. Se anula la cota 32 de la ronda 1: ahora NO se descartan tramas legítimas
  (rsp GET_MODULE_INFO = 1+37+2 = 42; OTA_RSP de hasta 61 bytes de datos).
- `ckbt51.c` → `ckbt51_dfu_tx()`: fix del desbordamiento real del PRIMER `memcpy` (`buf[RAW_EPSIZE=32]`, 7 bytes de header +
  data → overflow con data > 25, que ya pasaba la cota nueva). Ahora el primer paquete lleva `min(len,25)` y el resto sale en
  **bucle** de paquetes de continuación (`0x03` + hasta 31 bytes), extensión del `if (len > 25)` previo (para len ≤ 56 el
  resultado en el cable es idéntico al código original; para len > 56 evita el UB). Retirada la línea muerta
  `checksum += buf[i]` (nunca se enviaba y leía `buf[i]`, OOB by one cuando `i == 32`).
- Builds rework: ansi/rgb y iso/white OK.

## WP-202 rework — OK (revertido)
- `k13_pro/rules.mk`: eliminada la línea activa `DEBOUNCE_TYPE = asym_eager_defer_pk` → default `sym_defer_g` con DEBOUNCE=5.
  Motivo del VETO (aceptado): confirmación eager con 1 muestra sobre bus HC595 compartido (matrix.c) = riesgo de pulsaciones
  fantasma, que es la queja original del usuario. Quedan 2 líneas de comentario marcándolo como experimento opt-in a medir
  con `medir_polling.py` en hardware antes de activar.

## Tamaños tras rework (elf, línea text)
| Variante | pre-rework | post-rework |
|---|---|---|
| ansi/rgb | 57598 | **57166** |
| iso/white | 49920 | 48880 |

(−456 del revert asym; +24 del guard/ruta fast-wake y rework dfu_tx. `tools/dfu-suffix` ya corregido aparte — sufijo DFU
1.1a estándar verificado en el `.bin` nuevo: bcdDFU 0x011A, "UFD", bLength 0x10 — no tocado en esta ronda.)
Commits: NO. Parche regenerado: `patches/k13-audit.patch` (219 líneas, 6 ficheros, alcance igual).

---

# Ronda 2 (SDD §8) — polling BT + reconexión, todos los teclados

## WP-110 + WP-111(a) — OK (mecánico, uniforme)
- Qué cambia: en todos los bloques `module_param_t` de los drivers CKBT51/LKBT51: `.report_rate = 90` → `= 133` (WP-110) y
  `.reconnect_timeout = 5` → `= 60` (WP-111a). `connected_idle_timeout`, `pairing_*` y alineación intactos (sed anclado al nombre de campo).
- Ficheros tocados (27, 54 sustituciones; 2 bloques/teclado salvo excepciones):
  `k1_pro k2 k3 k4 k5 k6 k7 k8 k9 k10 k11 k12 k13 k14 k15 k17` + `q1 q2 q3 q4 q5 q6 q8 q10 q13 q14` (`<kb>/<kb>.c`, bloques
  `ckbt51_param_init` + `ckbt51_default_ack_handler`) y `common/wireless/keychron_wireless_common.c` (bloque `lkbt51_param_init`,
  mismo `module_param_t` 90|133; incluido por "cubre TODAS las ocurrencias" — pila de los `_max/version`, usarla no cambia K13).
  Excepciones: `q1_pro.c` = 3 bloques (149/218/246); `k5_pro.c` bloques en 229/244.
- CA verificada: `grep '.report_rate = 90'` = 0 hits; `'.reconnect_timeout = 5'` = 0 hits; 133/60 en los 54 sitios.
  Solo quedan los comentarios de struct en `ckbt51.h:118` / `lkbt51.h:91` (`/* 90 or 133 */`, sin tocar).
- **LKBT51 revertido por VETO (fuera de ámbito)**: `keychron_wireless_common.c` vuelve a 90/5 → 26 ficheros / 52 sustituciones; parche final = 33 ficheros.

## WP-111(b) — OK
- Fichero: `k13_pro/k13_pro.c` → `bluetooth_enter_disconnected_kb()` (`:217`): ventana `sync_timer_read32() < 1000` → `< 5000`
  + 1 línea de comentario (arranque lento del módulo: si pasa de la ventana, los parámetros no se aplican nunca → explicaría
  rate observado ≠ lo pedido). SOLO k13_pro.c; los demás teclados conservan su copia con 1000 (fuera de foco, §8).

## WP-107 — OK
- Fichero: `bluetooth/lpm.c` → `lpm_task()`: la condición de entrada a STOP1 exige ahora además
  `report_buffer_is_empty() && report_buffer_get_retry() == 0` (bajo `#ifndef DISABLE_REPORT_BUFFER`; hoy ningún teclado lo
  define → sin efecto sobre el gate) y `bt_event_queue_head == bt_event_queue_tail`.
- Cola de eventos: `bt_event_queue_head/tail` en bluetooth.c son globales NO-static → seguido la opción de menor superficie
  del §8 (extern directo en lpm.c, 2 líneas) en lugar de crear helper+header; `bluetooth.c`/`bluetooth.h` sin cambios por aquí.
  Añadido `#include "report_buffer.h"` a lpm.c. Conportamiento en reposo drenado: idéntico (gate solo bloquea con trabajo pendiente).

## WP-108 — OK
- Fichero: `bluetooth/bluetooth.c` → `bluetooth_connect()` (solo la base; `bluetooth_connect_ex` NO tocado): rate-limit 500 ms
  con `static uint32_t last_connect_time` + `sync_timer_elapsed32` (mismo patrón del fichero). Centinela 0 → la primera llamada
  pasa siempre; posterior comparación por elapsed → a prueba de wrap. Evita ráfaga de comandos connect (3 ms bloqueantes c/u)
  mientras el estado es DISCONNECTED/PARING.

## Builds ronda 2 (elf, línea text)
| Fichero build | pre-ronda2 | post-ronda2 |
|---|---|---|
| k13_pro ansi/rgb | 57166 | **57222** (+56) |
| k13_pro iso/rgb  | 57178 | **57234** (+56) |
| k14_pro ansi/rgb (spot-check §8, pila bluetooth + params WP-110) | n/b | 56862 OK |

- Spot-check fuera de K13: `keychron/k14_pro/ansi/rgb` compila limpio desde cero incremental con `bluetooth.mk` modificado.
- Sin incidencias preexistentes de build en los ficheros tocados. ansi/white e iso/white no re-validados en esta ronda (a criterio del verifier; lpm.c/bluetooth.c son comunes, el delta es idéntico que en ansi/rgb).
- Parche regenerado con rondas 1+2: `patches/k13-audit.patch` (975 líneas, 34 ficheros). Commits: NO.
- Validación diferida a hardware (usuario): `medir_polling.py -m tap` (suelo esperado ~7,5 ms con 133 Hz).
- format-text CI (espejo lint.yml, clang-format 22 --style=file): MODIFICÓ los 33 ficheros del diff; cambios whitespace-only (text/data/bss idénticos post-rebuild en las 5 variantes); rules.mk restaurado a 1f8f0cd (clang-format lo rompía, no es C); patch regenerado (1343 líneas, 33 ficheros). Sanity rebuild iso/rgb + k14_pro/ansi/rgb + repoblado 4 default: 6/6 exit 0.

## Commits (26/10/2026, rama k13-pro-audit, autorizados por el usuario; sin push)
- `10b7388` Grupo A — keyboards/keychron/bluetooth/ (bluetooth.c, ckbt51.c, lpm.c, report_buffer.c, report_buffer.h): "bluetooth: harden CKBT51 link handling (SDD WP-101/102a/103/104/107/108/201)"
- `6f5b50a` Grupo B — 25 keyboards/keychron/*_pro/*_pro.c (no k13_pro.c): "keychron: set CKBT51 report_rate=133 and reconnect_timeout=60s (SDD WP-110/111a)"
- `97e9727` Grupo C — keyboards/keychron/k13_pro/ (k13_pro.c, config.h, rules.mk): "k13_pro: widen param-init window to 5s, document LPM tunables, debounce opt-in note (SDD WP-111b/202/203)"
- Tras commitear: `git status --porcelain` vacío y `git diff HEAD --stat` vacío. `patches/k13-audit.patch` NO regenerado (snapshot pre-commit; incluye el format-text del verifier, funcionalmente idéntico a HEAD~3..HEAD).

Parche regenerado desde HEAD 1d66356 (incluye commit 4, 33 ficheros)
