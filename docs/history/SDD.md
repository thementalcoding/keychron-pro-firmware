# SDD — Auditoría y mejora firmware Keychron K13 Pro (rama `wls_2025q1`)

**Rev:** 2.2 · **Fecha:** 26/10/2026 · **Estado:** CERRADO — BUILD-GATE OK, CI-espejo OK, commiteado (`10b7388`/`6f5b50a`/`97e9727`) y FLASHEADO en el teclado del usuario; validación post-flasheo en informe §15

## 0. Objetivo
Mejorar fiabilidad (ráfagas de teclas / microcortes BT), latencia y robustez del
firmware STM32 del K13 Pro con parches mínimos, compilables y revisables.
El radio (CKBT51, firmware cerrado) NO es modificable: solo su lado host QMK.

## 1. Base de trabajo
- Repo: `firmware_qmk/wls_2025q1/` (QMK fork Keychron, árbol completo materializado
  + submódulos chibios/chibios-contrib/printf).
- Rama de trabajo: `k13-pro-audit` (1 commit por WP).
- Alcance de edición: **solo `keyboards/keychron/**`**. Toques fuera → permiso del coordinador.
- Entorno build (VERIFICADO, baseline `.bin` OK): `source tools/qmk_env.sh`
  → `.venv-qmk/bin/qmk compile -kb keychron/k13_pro/ansi/rgb -km default`
  (variantes: `ansi/{rgb,white}`, `iso/{rgb,white}`; dfu-suffix es un wrapper python en `tools/`).

## 2. Roles y flujo
| Rol | Misión | Salida |
|---|---|---|
| Coordinador | asigna WPs, integra, decide bloqueos | tabla de estado, informe §12 |
| Researcher | WP-000 referencias externas | ≤15 bullets, sin código |
| Implementer | parches WP-1xx/2xx | commits + resumen 5 líneas por WP en board |
| Reviewer | revisa `git show` de cada commit | INFO (aprobado) o VETO con motivo |
| Verifier | builds y estáticos | RESULT PASS/FAIL por WP y variante |

Tablero: mensajes cortos (ID de WP + commit + veredicto). **Nunca pegar diffs grandes.**
Orden: Implementer WP → Reviewer → Verifier → siguiente WP. P0 pueden paralelizarse
entre sí (archivos solapados: WP-102 toca bluetooth.c y lpm_stm32l432.c; WP-101/103/104
tocan ckbt51.c/bluetooth.c — el implementador las hace en serie para evitar conflictos).

## 3. Work Packages

### WP-000 · Referencias (researcher, P2, sin código)
Analizar **ZMK firmware** (github.com/zmkfirmware/zmk) — debounce, parámetros de
conexión BLE, gestión de energía — y QMK mainline `asym_eager_defer_pk`.
Entregable: ≤15 bullets "práctica → ¿aplicable al K13? → WP destino".

### WP-101 · P0 Robustez parser UART (`bluetooth/ckbt51.c: ckbt51_task`)
- Falta cota: `len` válido hasta 255 → `buf[32]` desborda la pila. Añadir
  `if (len > 3+32) → descartar y resync`. Contador de checksum-error con `dprintf`.
- CA: sin copia fuera de cota; resync tras paquete corrupto; build pasa.

### WP-102 · P0 Sincronizar buffer de informes con el enlace (`bluetooth/bluetooth.c`, `bluetooth/lpm_stm32l432.c`)
Problema: la cola de informes solo se vacía en `EVT_DISCONNECTED`. Si ese evento
se pierde (UART overrun tras wake desde STOP1), el STM32 sigue encolando con el
enlace caído y drena el backlog en ráfaga al reconectar.
- (a) Vaciar `report_buffer` también al entrar en `EVT_RECONNECTING`.
- (b) Tras wake de LPM (`lpm_wakeup`), pedir estado del módulo
  (`CKBT51_CMD_READ_STATE_REG`) y si informa link-down, transicionar a desconectado.
- CA: no existe camino "link caído → encolado" sin flush; no romper el retry legítimo.

### WP-103 · P1 Timer de retransmisión FIFO (`bluetooth/ckbt51.c: ack_handler`)
En `ACK_FIFO_FULL_ERROR` → `set_retry(10)` sin resetear `retry_time_buffer` →
reenvío inmediato/impulsivo. Resetear el timer al fijar retry.
- CA: diff mínimo; revisión de semántica sn (dedupe por módulo intacta).

### WP-104 · P2 Protocolo HID muerto (`bluetooth/bluetooth.c: bluetooth_hid_set_protocol`)
Ignora el parámetro y fija `false` siempre; `bluetooth_report_protocol` quedó
obsoleto tras la refactor 2025. Decidir (reviewer): eliminar la variable muerta o
propagar boot-vs-report protocol.
- CA: sin escrituras huérfanas; NKRO/6KRO sin regresión.

### WP-201 · P2 Wake INT no bloqueante (`bluetooth/ckbt51.c: ckbt51_send_cmd`)
Hoy: busy-wait 3 ms ANTES de CADA comando (pulsos INT 3×1 ms).
Mejora: evitar la secuencia de wake si hubo actividad reciente con el módulo
(último TX/RX < N ms), N conservador (p. ej. 50 ms). NO cambiar el protocolo.
- CA: ráfagas de informes sin esperar 3 ms por informe; enlace sigue despierto
  correctamente en reposo largo (verificación manual pos-flasheo).

### WP-202 · P2 Debounce específico BT (`k13_pro/rules.mk` o `keyboard.json`)
Probar `DEBOUNCE_TYPE = asym_eager_defer_pk` (eager + asimétrico por tecla;
reducción de latencia sin dobles). Mantener DEBOUNCE=5.
- CA: 4 variantes buildan; documentar trade-off; decisión final requiere medición
  en dispositivo (diferida al usuario, `tools/medir_polling.py`).

### WP-203 · P1 Tunables LPM (`bluetooth/lpm.h`, `k13_pro/config.h`)
Exponer `RUN_MODE_PROCESS_TIME` (hoy 1000 ms) y `LOW_POWER_MODE` (PM_STOP1) como
overrides por config.h con guardas `#ifndef` (sin cambiar defaults).
- CA: build idéntico por defecto; doc 3 líneas del trade-off batería/latencia.

### WP-300 · Verificación (continua, verifier)
- Baseline ANTES de parches: compilar `keyboards/keychron/k13_pro/ansi/rgb`,
  `ansi/white`, `iso/rgb`, `iso/white` (solo vía default) + `qmk lint`.
- Repetir tras cada commit aprobado. Cualquier fallo → VETO al WP.
- Estáticos: grep de cotas (WP-101), `git diff --stat` (alcance), sin tabs nuevos.

### WP-900 · Cierre (coordinador)
Integrar → `informe_bluetooth_keychron.md` §12: parches aplicados/rechazados,
instrucciones de flasheo DFU y plan de validación en hardware.

## 4. Plan de pruebas (resumen)
| Nivel | Método | Quién |
|---|---|---|
| Estático | revisión diff por commit | Reviewer |
| Build | 4 variantes + lint | Verifier |
| Lógico | host-tests QMK si existen para el módulo tocado | Verifier (best-effort) |
| Hardware | flash DFU + 3 días BT + tap test | **Usuario (diferido)** |

No hay simulación del enlace radio: todo lo relativo al módulo CKBT51 se valida
solo en hardware. Ningún WP depende de flashear para aceptarse (build+review).

## 5. Restricciones
- GPL2; conservar cabeceras; no reformatar ni renombrar fuera del WP.
- Máx. ~40 líneas de cambio por WP (excepciones: WP-102).
- Cero toques en `lib/` (ChibiOS). Cambios en `quantum/` prohibidos salvo orden escrita.
- No instalar/pedir nada fuera del venv y el toolchain ya indicados.

## 6. Definición de hecho
P0 y P1 aprobados e integrados; P2 aprobados o aplazados con motivo escrito;
4 variantes compilando limpias; informe §12 redactado; pendientes de hardware
enumerados en el informe con pasos concretos para el usuario.

## 7. Referencias externas (WP-000 completado, research ZMK main)
Aplicadas en el parche: regla de oro en pérdida de enlace (flush + informe cero
al reconectar → WP-102a/`clear_keyboard`), cola acotada (cota de trama → WP-101),
parser sin tocar estado desde callback (single-thread: OK en QMK housekeeping),
debounce asimétrico solo opt-in tras VETO reviewer (ghosting con bus HC595).
Diferidas a hardware (medir con `tools/medir_polling.py`/btmon): PM de dos niveles al
estilo ZMK (idle 30 s → deep sleep 15 min con gate VBUS; nuestro default es
STOP1 a 1 s — subir `RUN_MODE_PROCESS_TIME` si la carrera de wake persiste),
presupuesto de latencia radio (intervalo 7,5–15 ms + latency → peor caso ~0,5 s
de entrega; detección de caída ~4 s — es la ventana real de la ráfaga),
coalescing de escritura EEPROM (desgaste flash). No aplicable: params BLE y
re-advertising (la radio la gobierna CKBT51, cerrado).

## 8. Ronda 2 (25/10 23:20) — polling BT + teclas sueltas, todos los teclados

Contexto nuevo (scoping coordinador): el driver expone `module_param_t` con
`report_rate` (90|133 Hz), `reconnect_timeout` (2–254 s, 0xFF ilimitado) y
`connected_idle_timeout`; **todos** los teclados CKBT51 del repo fijan
`report_rate=90` y `reconnect_timeout=5`, y `ckbt51_param_init()` solo corre si
el módulo arranca en <1 s. Usuario: K13 Pro **ISO ES**; mejoras → todo el árbol
keychron. Ámbito extra permitido: `keyboards/keychron/*/*.c` (bloques de
parámetros) y `bluetooth/lpm.c`.

### WP-110 · P0 Polling BT: `report_rate` 90 → 133
En TODOS los `ckbt51_set_param` del árbol keychron (mecánico, uniforme).
CA: 0 hits de `report_rate.*= 90`; 133 en todos los bloques; K13 iso+ansi buildan.
Validación real: `tools/medir_polling.py -m tap` en hardware (suelo esperado ~7,5 ms).

### WP-111 · P0 Reconexión y ventana de init
(a) `reconnect_timeout` 5 → 60 s en los mismos bloques (fiabilidad > batería,
regla 4 del orquestador; el módulo deja de reintentar a los 5 s = patrón de
"reconexión silenciosa al teclear").
(b) Ventana de `ckbt51_param_init` en `bluetooth_enter_disconnected_kb` del
K13 Pro: `sync_timer_read32() < 1000` → `< 5000` (si el módulo tarda, hoy los
parámetros NO se aplican nunca → explicarían rate observado ≠ 90). Solo k13_pro.c
(los demás teclados tienen su propia copia; NO tocar: fuera de foco usuario).
CA: grep confirma; build iso/rgb OK.

### WP-107 · P1 Gate LPM: no dormir con trabajo pendiente
`lpm_task()` (compartido, todos los teclados): añadir a la condición
`report_buffer_is_empty() && !report_buffer_get_retry()` y cola de eventos BT
vacía (helper nuevo `bluetooth_event_queue_is_empty()` si hace falta, o inline
con las vars ya file-scope en bluetooth.c — elegir la de menor superficie).
CA: no se entra en STOP1 con informes/retry/eventos pendientes; sin cambio
cuando todo está drenado (comportamiento default idéntico en reposo).

### WP-108 · P1 Rate-limit `bluetooth_connect()`
Hoy cada informe con enlace caído lanza un comando connect (3 ms bloqueantes +
churn del módulo). Mínimo 500 ms entre comandos connect (sync_timer), solo en
`bluetooth_connect()` base (NO en `connect_ex` con host_idx explícito de los
teclados multi-host). CA: primer connect inmediato (timer=0); posteriores
espaciados; sin impacto en pairing.

### WP-H1 · Coordinador (no firmware)
`tools/bt_tune.sh`: wrapper btmon + guía tap-test antes/después + chequeo
bluez-utils. Informe §13 con tabla polling esperado (90→133 Hz) y pendientes.

### Fuera de ronda 2 (documentado)
- `connected_idle_timeout=7200` ya es largo: no tocar.
- `if` anidado duplicado en `bluetooth_pre_task` de k13_pro.c: cosmético, se deja.
- Ñ/ISO-ES: el layout físico ya existe (iso/*) y el mapa ES se configura en el
  host (VIA/`via_json/k13_pro_iso_*.json`); no hay cambio de firmware posible.
- Gate tester: 4 variantes K13 + spot-check de OTRO teclado con bloque de
  params (p. ej. k15_pro o k14_pro, la variante que exista) para validar que el
  cambio mecánico compila fuera del K13.

## 9. Cierre y continuidad
- Rondas 1+2 entregadas, revisadas, verificadas (BUILD-GATE OK + CI-espejo) y
  **flasheadas** en hardware con resultado medido (+40 % polling). Informe §15.
- PR upstream: Keychron/qmk_firmware#529 (rama `k13-pro-bt-fixes`, base
  `wls_2025q1`). Repo público con binarios: ver informe §17.
- **Pendientes y ronda 3** (14 candidatos priorizados, con riesgo y necesidad de
  hardware): `docs/BACKLOG.md` en la raíz del proyecto. Retomar por ahí.

