# Revisión profunda por teclado — 26 CKBT51 antes de v1.0.0

Fecha: 2026-10-26 · Repo: Keychron `qmk_firmware` (`wls_2025q1`) · Rama `k13-pro-bt-fixes`, HEAD `1d66356`
Alcance: 26 boards CKBT51; solo lectura (no se modificó el repo). LKBT51 fuera de alcance.

## 1. Hallazgos nuevos por placa

| board | fichero:línea | hallazgo (1 línea) | sev | ¿seguro sin HW? | ¿R3-xx? |
|---|---|---|---|---|---|
| q6_pro | `q6_pro/q6_pro.c:92-95` | `KC_TASK` llama `ckbt51_factory_reset()` en cada pulsación; el keymap default usa Fn+Task → borra pairing/params del módulo | alta | sí | no |
| q1_pro | `q1_pro/q1_pro.c:163-164` y `:191-193` | `CKBT51_RESET_PIN` (A9) se deja LOW en boot y solo sube tras un factory-reset que termina HIGH; la polaridad es internamente incoherente | alta | no | no |
| q1_pro | `q1_pro/q1_pro.c:212` | `ckbt51_set_local_name(STR(PRODUCT))` publica el nombre BT con comillas literales (`"Keychron Q1 Pro"`); las 25 hermanas usan `PRODUCT` | baja | sí | no |
| q3_pro (_se) | `q3_pro/matrix.c:218` | `unselect_cols()` rearma `power_on_indicator_timer_buffer` en cada `matrix_init`; cada wake desde STOP1 repite el overlay LED de 3 s (solo ansi/iso/jis_encoder_se) | baja | sí | no |
| k11_pro | `k11_pro/config.h:64` | `CONNECTED_BACKLIGHT_DISABLE_TIMEOUT 30` vs 600 s en las otras 25; valor atípico a confirmar | baja | no (intención) | no |
| varias (16) | `k1,k5,k7,k8,k11,k12,k14,k15,k17,k1,q4,q5,q6,q8,q10,q13,q14` `.c` (`wait_ms(10)` ×2) | 20 ms bloqueantes en `ckbt51_param_init` dentro del event queue (primer BT / factory reset); el ACK 0x45 ya reenvía `set_param` | baja | no (validar UART/ACK) | no |
| q1_pro, q2_pro, k10_pro | `*/matrix.c` (no compilado) | `rules.mk` incluye `common/common.mk`; el `matrix.c` propio queda muerto y diverge (k10: 24 bits vs 20 del driver activo) | baja | sí | no |

Notas de alcance de la tabla:
- q3_pro: solo afecta a las 3 variantes `_se` (18 columnas), que son las que compilan `q3_pro/matrix.c`; las variantes de 16 columnas usan `common/matrix.c`.
- La fila "varias (16)" es un patrón compartido, no 16 fallos independientes. q1 aporta además un `own_bt_param_init()` muerto con `wait_ms` y `STR(PRODUCT)`.
- k13_pro no tiene hallazgos nuevos: sus dos riesgos conocidos son R3-09 (`HC595_delay(1)` ≈12,5 ns) y R3-10 (17ª columna en `unselect_cols`).

## 2. Placas limpias

Limpieza estricta (sin hallazgos propios ni notas compartidas): **k2_pro, k3_pro, k4_pro, k6_pro, k9_pro, k13_pro**.

Limpieza respecto a fallos propios, pero con la nota compartida PB-06 (`wait_ms(10)` en param-init): **k1_pro, k5_pro, k7_pro, k8_pro, k12_pro, k14_pro, k15_pro, k17_pro, q4_pro, q5_pro, q8_pro, q10_pro, q13_pro, q14_pro**.

k10_pro y q2_pro solo tienen el `matrix.c` muerto (PB-07, mantenimiento); q1_pro queda excluida por PB-02/PB-03.

## 3. Veredicto WP → APROBADO/VETO

| WP | veredicto | motivo (1 línea) | cambios solicitados (mínimos, sin código) |
|---|---|---|---|
| PB-01 q6 factory reset en Task | **APROBADO** | Pérdida de pairing/params con una tecla de uso normal; no depende de HW | Retirar la llamada de `case KC_TASK` (dejar el fallthrough a Win+Tab como las hermanas); si se quiere conservar, moverla a `ENABLE_FACTORY_TEST` y a una combinación que no esté en el keymap default |
| PB-02 q1 reset A9 | **VETO** | No se puede decidir polaridad sin esquema/HW; init LOW y pulso LOW→HIGH son incompatibles entre sí | Medir A9 y la línea de reset del módulo; si es activo-bajo, subirla a HIGH en init y dejar el pulso LOW→HIGH solo en factory reset; si A9 no es reset, retirar macro/usos |
| PB-03 q1 nombre BT | **APROBADO** | Cambio estático y verificable; el nombre se publica con comillas | Sustituir `STR(PRODUCT)` por `PRODUCT` en la función activa (`:212`) y, por coherencia, en la muerta (`:143`) |
| PB-04 q3 overlay LED al despertar | **APROBADO** | Solo afecta a `_se`; consume bus 595 y puede pisar el indicador 3 s tras cada wake | Rearmar `power_on_indicator_timer_buffer` solo en boot (no en `unselect_cols`/`matrix_init`), o eliminar el overlay si el estado LED ya se restaura en cada `select_col` |
| PB-05 k11 timeout 30 s | **VETO** | Puede ser decisión de producto (batería/panel), no un typo demostrable | Confirmar con el responsable; si es copia de k10/k12, alinear a 600 s |
| PB-06 waits 10 ms en param-init | **VETO** | Quitarlos sin medir puede perder `set_name`/`set_param` en módulos lentos; son redundantes pero no inocuos de validar | No tocar en v1.0.0; documentar y, si se optimiza, sustituir por secuencia no bloqueante basada en el ACK 0x45 |
| PB-07 `matrix.c` muerto (q1/q2/k10) | **APROBADO** | No afecta al binario actual; evita que un futuro cambio de `rules.mk` active un driver divergente | Borrar los `matrix.c` no compilados o documentar explícitamente que el driver activo es `common/matrix.c`; no cambiar `rules.mk` |
| PB-08 parche/notas vs HEAD | **VETO** | `patches/k13-audit.patch` no incluye el commit `1d66356` (26 hunks de ventana init); `notes.md` sigue diciendo que solo k13 cambia y lista 3 commits | Regenerar el parche desde `c8b2b23..HEAD` y actualizar `notes.md` con el 4º commit, el alcance real (26 boards) y el hash nuevo; reconstruir al menos una variante por grupo |

## 4. Top-5 si hay que tocar algo antes de v1.0.0

1. **q6_pro (PB-01, alta).** Es el único fallo funcional directo y reproducible: Fn+Task borra el pairing. Riesgo de arreglo: nulo (una llamada); riesgo de no arreglarlo: soporte/pérdida de configuración.
2. **Artefactos de release (PB-08, alta).** El parche público y las notas no describen el árbol que se va a publicar (`1d66356`). Riesgo: el usuario/CI flashea o audita un diff distinto del binario. Regenerar parche/notas es mecánico.
3. **q1_pro reset A9 (PB-02, alta/media).** Si A9 es el reset activo-bajo, q1 arranca con el módulo en reset; si es activo-alto, el factory-reset lo deja asserted. Requiere HW; no cambiar a ciegas.
4. **q1_pro nombre BT (PB-03, baja).** Arreglo de una línea; evita un nombre con comillas en el emparejamiento.
5. **q3_pro `_se` overlay LED (PB-04, baja) / k11 timeout (PB-05, baja).** Ambas son de bajo impacto; la de q3 es segura de corregir en código, la de k11 solo tras confirmar intención.

## 5. Método

- Ficheros leídos: 26 `<board>.c`, 26 `config.h`, 26 `rules.mk`, 18 `matrix.c` (15 activos, 3 muertos), `halconf.h`/`mcuconf.h` cuando aplica, y la pila compartida `keyboards/keychron/bluetooth/` (`ckbt51.c/.h`, `bluetooth.c`, `report_buffer.c/.h`, `transport.c`, `lpm.c`, `lpm_stm32l432.c`, `battery.c`, `rtc_timer.c`, `indicator` solo por llamadas). `common/wireless/` solo para descartar LKBT51.
- Patrones/greps principales: `wait_ms|delay|chThdSleep`, `while (`/busy-wait, `MATRIX_ROWS|MATRIX_COLS`, `HC595_(START|END|OFFSET|STCP|SHCP|DS)`, `uint8_t|uint16_t|uint32_t data`, `DEBOUNCE_TYPE`, `CKBT51_FAST_WAKE`, `LOW_POWER_MODE|RUN_MODE_PROCESS_TIME`, `USB_BT_MODE_SELECT_PIN`, `CKBT51_RESET_PIN`, `battery_calculte_voltage|2246`, `report_rate|reconnect_timeout`, `ckbt51_[a-z_]+\(`, `STR(PRODUCT)`, `factory_timer|bt_factory_reset`, `process_record_kb` (llamadas inesperadas), `suspend_wakeup_init_kb`.
- Cruces: dimensión efectiva de columnas por variante desde `info.json`/`keyboard.json` (26 boards, 95 variantes de build), ancho de tipo vs `HC595_END_INDEX`, y comparación normalizada (`sed` + `diff -u`) de hermanas (k13/k14, k10/k11, k1/k5, q5/q6/q8, q10/q13/q14, q13/q14).
- Comprobaciones estáticas: conflicto de pines macro↔encoder/HC595, `rules.mk` vs `common/common.mk` (driver de matrix realmente compilado), y `patches/k13-audit.patch` vs `git diff c8b2b23..HEAD`.
- Límites: sin compilación ni hardware en esta revisión. Todo lo que depende de polaridad del reset, tiempos del módulo, ghosting del 595 o del bus UART queda marcado como "no seguro sin HW".

---

## 6. Deep dive v1.0.0 (solo lectura)

Comparativa adicional usada abajo: árbol de referencia del vendor (`keyboards/keychron/`, mismo día). No se modificó ningún fichero de firmware.

### 6.1 q6_pro — `ckbt51_factory_reset()` en `KC_TASK`

**Contexto exacto** (`q6_pro/q6_pro.c:88-99`):

```c
        case KC_TASK:
            if (record->event.pressed) {
                ckbt51_factory_reset();
            }
        case KC_FILE:
        case KC_SNAP:
        case KC_CTANA:
            if (record->event.pressed) {
                for (uint8_t i = 0; i < key_comb_list[keycode - KC_TASK].len; i++)
                    register_code(key_comb_list[keycode - KC_TASK].keycode[i]);
```

El `case KC_TASK` cae por fallthrough al bloque de `KC_FILE/KC_SNAP/KC_CTANA`, así que además de resetear el módulo envía Win+Tab.

**Keymaps que lo alcanzan** (los 4 de q6_pro):
- `q6_pro/ansi_encoder/keymaps/default/keymap.c:50` → capa `[WIN_FN]`, fila 0 columna 3.
- `q6_pro/ansi_encoder/keymaps/via/keymap.c:50` → ídem.
- `q6_pro/iso_encoder/keymaps/default/keymap.c:50` → ídem.
- `q6_pro/iso_encoder/keymaps/via/keymap.c:50` → ídem.

En `WIN_BASE` la fila 0 columna 3 es `KC_F3` y `MO(WIN_FN)` está en la fila inferior; por tanto el atajo real es **Fn+F3 en modo Windows**. En `MAC_FN` esa posición es `_______` (transparente) y cae a `KC_MCTL`, así que en modo Mac no se dispara. `KC_TASK` está declarado en `q6_pro/q6_pro.h:38` dentro del bloque `QK_KB_0/SAFE_RANGE`.

**Qué hace `ckbt51_factory_reset()`** (`bluetooth/ckbt51.c:398-404`): envía `CKBT51_CMD_FACTORY_RESET = 0x71` con `ack_enable=false`. Es el mismo comando que usa el factory reset intencional del firmware (`bluetooth/factory_test.c:53`: `FN|J|Z`, 3 s; `:103-104`), que además hace `eeconfig_init()` y pone `bt_factory_reset=true`. En el repo no hay una especificación local del 0x71; por nombre y por ser el paso final del reset de fábrica, restaura la configuración del módulo (emparejamientos y parámetros), no es un simple “clear bond”. La llamada de q6 **no** pone `bt_factory_reset`, así que no se re-aplican nombre/133/60; el enlace BT puede caer y hay que re-emparejar. USB sigue funcionando, no es un brick; sí deja el BT inutilizable hasta re-emparejar/reconfigurar.

**Evidencia de que es una edición local y no intencionada:** el hermano de referencia (`keychron/q6_pro/q6_pro.c:93-99` en el árbol del vendor) tiene el mismo `case KC_TASK` **sin** las dos líneas del reset. El diff entre ambos muestra exactamente la adición de `if (pressed) { ckbt51_factory_reset(); }`.

**Otros `*_pro.c` con `case KC_TASK`:** los 26 lo tienen; solo q6 añade la llamada. Fichero:línea del `case` (todos contienen únicamente el bloque compartido de Win+Tab): k1:92, k2:87, k3:87, k4:87, k5:109, k6:87, k7:94, k8:92, k9:92, k10:102, k11:90, k12:92, k13:93, k14:92, k15:106, k17:106, q1:85, q2:89, q3:93, q4:89, q5:89, **q6:92**, q8:89, q10:103, q13:103, q14:89. Los keymaps de las 26 placas mapean `KC_TASK` en alguna capa Fn (100% de los `.c` de keymaps revisados), por lo que si la llamada estuviera en otra placa también sería alcanzable; no lo está.

**Veredicto: CORREGIR antes de v1.0.0.** Parche mínimo: borrar las líneas 93-95 (`if (pressed) { ckbt51_factory_reset(); }`) y dejar el fallthrough como en playground/hermanas. No hace falta inventar combo alternativo: el reset intencional ya existe en Fn+J+Z durante 3 s. Riesgo: prácticamente nulo; como único efecto se pierde un atajo oculto no documentado. No requiere hardware. Rebuild: **q6_pro ansi_encoder e iso_encoder, keymaps default y via (4 builds)**.

### 6.2 q1_pro — `CKBT51_RESET_PIN` (A9)

**Definición y escrituras (todas):**
- `q1_pro/config.h:29`: `#define CKBT51_RESET_PIN A9`.
- `q1_pro/q1_pro.c:163-164`: `gpio_set_pin_output_push_pull(A9); gpio_write_pin_low(A9);` (boot, único sitio que lo deja bajo).
- `q1_pro/q1_pro.c:191-193`: `palWriteLine(CKBT51_RESET_PIN, PAL_LOW); wait_ms(5); palWriteLine(CKBT51_RESET_PIN, PAL_HIGH);` (factory reset, termina en HIGH).
- No hay más escrituras de A9 ni apagado/encendido que lo toque (`grep` de `A9`/`CKBT51_RESET_PIN` en q1_pro).

**Polaridad según el código:** las 25 hermanas usan HIGH como reposo y un pulso LOW de 5 ms como reset (p. ej. q2_pro `:149-150` y `:180-182`; k10_pro `:154-155` y `:181-183`). Eso implica **reset activo-bajo**. q1 hace lo contrario en boot (LOW) y su pulso de factory reset termina en HIGH.

Consecuencia si A9 está conectado al reset del módulo:
- Interpretación activo-bajo: q1 arranca con el módulo en reset; el primer factory reset lo libera al final (HIGH), pero el comando 0x71 enviado durante el pulso no se recibiría. Explicaría “módulo muerto hasta el primer factory reset”.
- Interpretación activo-alta: el boot es normal, pero el factory reset deja A9 en HIGH = reset asserted permanente.
- En ambos casos la secuencia es internamente incoherente. Si A9 no está conectado al reset en q1, ambas son inocuas.

**¿Comparte esquema con q2/k10?** q1, q2 y k10 comparten la asignación `CKBT51_RESET_PIN A9` (y q1/q2 también `INT A5`, `BLUETOOTH_INT A6`, `MODE C15`, `POWER B1`); k10 solo cambia `MODE` a A10. q2 y k10 inicializan A9 en HIGH; el patrón LOW inicial es **exclusivo de q1**. No se puede confirmar el esquema físico desde el repo, pero la asignación común hace sospechoso el estado inicial distinto. El mismo LOW está también en el árbol de referencia del vendor, así que no lo introdujo este parche.

**Veredicto: DOCUMENTAR / no corregir a ciegas en v1.0.0.** Parche mínimo si se confirma activo-bajo: cambiar el boot a `gpio_write_pin_high(A9)` (una línea) y mantener el pulso LOW→HIGH del factory reset. Si se confirma que A9 no es reset, retirar el bloque de init y la macro. Riesgo sin hardware: alto (si A9 es un enable activo-bajo, ponerlo HIGH puede dejar el módulo sin alimentación; si es reset activo-bajo, el cambio es el correcto). Rebuild si se toca: **q1_pro ansi_knob/iso_knob/jis_encoder, default y via (6 builds)**.

### 6.3 q1_pro — `STR(PRODUCT)` en el nombre Bluetooth

Línea activa: `q1_pro/q1_pro.c:212` → `ckbt51_set_local_name(STR(PRODUCT));` (la copia muerta de `own_bt_param_init` está en `:143`).

`PRODUCT` lo genera QMK desde `info.json` como cadena C: `"Keychron Q1 Pro"`. `STR`/`XSTR` (`quantum/util.h:10-11`) stringifica el literal expandido:

```c
#define STR(s) XSTR(s)
#define XSTR(s) #s
#define PRODUCT "Keychron Q1 Pro"
STR(PRODUCT)  →  "\"Keychron Q1 Pro\""
```

El `strlen` enviado es 17 (15 del nombre + 2 comillas). El nombre que anuncia el módulo incluye las comillas; el resto de las 25 placas usa `ckbt51_set_local_name(PRODUCT)`.

**Veredicto: CORREGIR (baja).** Parche mínimo: `ckbt51_set_local_name(PRODUCT);` en `:212` y, por coherencia, en `:143`. Riesgo nulo (solo cambia el string). Rebuild si q1 entra en el release: **6 builds de q1_pro** (ansi_knob/iso_knob/jis_encoder × default/via). No bloquea K13.

### 6.4 k11_pro — `CONNECTED_BACKLIGHT_DISABLE_TIMEOUT`

`k11_pro/config.h:64`: `30`; las otras 25 placas: `600` (el `DISCONNECTED` sí coincide en 40). Está dentro del bloque `#if defined(RGB_MATRIX_ENABLE) || defined(LED_MATRIX_ENABLE)`, sin comentario que explique el valor. El mismo `30` existe en el árbol de referencia del vendor (`k11_pro/config.h:64`), por lo que **no es una divergencia introducida por este parche** y probablemente es una decisión del vendor para el K11 (perfil bajo/batería). No hay evidencia en repo de copy-paste accidental.

**Veredicto: DOCUMENTAR / DESCARTAR para v1.0.0.** No cambiar sin confirmación de producto. Si se decidiera alinear a 600, sería un cambio de una línea y rebuild de **k11_pro ansi/rgb, ansi/white, ansi_encoder/rgb, ansi_encoder/white (4 builds)**; riesgo funcional bajo, pero cambia autonomía/experiencia.

### 6.5 q3_pro `_se` — overlay LED en cada `matrix_init`

Cadena confirmada:
- `q3_pro/matrix.c:218` (dentro de `unselect_cols`) → `power_on_indicator_timer_buffer = sync_timer_read32() | 1;`.
- `q3_pro/matrix.c:265-276`: `matrix_init_custom()` llama `unselect_cols()`.
- `bluetooth/lpm_stm32l432.c:257`: tras despertar de STOP1, `enter_power_mode()` llama `matrix_init()`; con `CUSTOM_MATRIX=lite`, `quantum/matrix_common.c` invoca `matrix_init_custom()`.

Por tanto **sí**: cada wake rearma el overlay de 3 s y `select_col()` vuelve a ignorar `indicator_config`/Caps durante ese tiempo (`q3_pro/matrix.c:95-150`). Solo aplica a las 3 variantes `_se` (`ansi_encoder_se`, `iso_encoder_se`, `jis_encoder_se`); las de 16 columnas usan `common/matrix.c`. El mismo código está en el árbol de referencia del vendor (`q3_pro/matrix.c:218`), así que es preexistente y podría ser intencional (restaurar LEDs tras wake); no hay evidencia de que cause un fallo funcional.

**Veredicto: DOCUMENTAR / no tocar en v1.0.0 sin HW.** Si se corrige, el parche mínimo es rearmar `power_on_indicator_timer_buffer` solo en el primer init (flag `static bool` de boot) y no en cada `matrix_init`, o eliminar el overlay si el estado LED ya se reescribe en cada `select_col`. Riesgo: bajo en código, pero puede cambiar la animación/indicadores al despertar. Rebuild: **3 variantes `_se` de q3_pro, default y via (6 builds)**.

### 6.6 Otros puntos (para cierre de v1.0.0)

| punto | veredicto v1.0.0 | acción |
|---|---|---|
| `patches/k13-audit.patch` vs HEAD `1d66356` | **CORREGIR (bloqueante de artefacto)** | Regenerar desde `c8b2b23..HEAD` (1343→1593 líneas, 26 hunks de ventana init) y actualizar `notes.md` (4º commit, 26 boards); no es cambio de código |
| q1/q2/k10 `matrix.c` no compilado | **DESCARTAR para v1.0.0** | Solo limpieza futura; no tocar `rules.mk` antes del release |
| `wait_ms(10)`×2 en `ckbt51_param_init` (16 placas) | **DOCUMENTAR** | No quitar sin medir UART/ACK; no es bloqueante |
| q1 reset A9 | **DOCUMENTAR + HW** | No cambiar a ciegas; ver 6.2 |
| q1 `STR(PRODUCT)` | **CORREGIR si q1 entra en el release** | Una línea; ver 6.3 |
| q6 factory reset | **CORREGIR (bloqueante si q6 está en el PR/release)** | Ver 6.1 |
| k11 timeout / q3 overlay | **DOCUMENTAR** | Valores/precedentes del vendor; no bloquean |

**Conclusión de deep dive:** de los hallazgos funcionales, solo **q6_pro** merece corrección de código antes de publicar (una llamada, sin HW, 4 builds). **q1 `STR(PRODUCT)`** es un arreglo trivial si q1 se publica. **q1 A9** requiere hardware y no debe tocarse a ciegas. **k11 y q3** quedan documentados como comportamiento preexistente del vendor. El **parche/notas stale** sigue siendo el bloqueante de artefacto: el código de HEAD y el patch entregable no coinciden.

## Review final fixes (2026-10-26, HEAD `1d66356` + 2 ficheros)

Alcance: solo los dos cambios del working tree (`q6_pro.c`, `q1_pro.c`), el parche `k13-audit.patch` y los 5 bins q6/q1. Solo lectura.

| WP | veredicto | motivo (1 línea) | cambio solicitado (mínimo, sin código) |
|---|---|---|---|
| FIX q6 `KC_TASK` | **APROBADO** | El bloque queda idéntico a k2_pro/k3_pro: `KC_TASK` cae al handler común y solo desaparece `ckbt51_factory_reset()`; sin código muerto, sin variable sin usar y log de build sin warnings | Ninguno |
| FIX q1 nombre BT `:212` | **APROBADO** | `PRODUCT` = `"Keychron Q1 Pro"` (15 B + cmd = 16 B; `PACKET_MAX_LEN` 64, `RAW_EPSIZE` 32) y los bins contienen el nombre sin comillas | Ninguno |
| FIX q1 copia muerta `:143` | **VETO** | `own_bt_param_init()` conserva `ckbt51_set_local_name(STR(PRODUCT))`: es el mismo error y PB-03 pedía corregir `:212` **y** `:143`; no se compila (`BLUETOOTH_ENABLE` no definido) pero queda en fuente/parche | Cambiar `:143` a `PRODUCT` o borrar la función muerta; regenerar `k13-audit.patch` y notas; **no rebuild** (no entra en el binario) |
| Working tree | **APROBADO** | `git status --short` = solo `q1_pro.c` y `q6_pro.c`; `git diff --stat` = 1 inserción / 4 borrados | Ninguno |
| Patch `k13-audit.patch` | **VETO** | 33 diffs, 0 fuera de `keyboards/keychron/`, 4 commits (`c8b2b23..HEAD`), q6 sin la llamada y q1 `:212` con `PRODUCT`; **falta** el hunk de `:143` | Incluir el fix de `:143` al regenerar el parche/notas |
| Bins q6/q1 (5) | **APROBADO** | sha256 = manifest (`de481940…`, `c066fa3a…`, `94bd96da…`, `2f50002d…`, `0caa64cd…`), 62.144–62.984 B > 20 KB y `dfu-suffix -c` real exit 0 (PAR 0483:DF11); mtime 16:25:59 > fuentes 16:25:28 | Ninguno |
| Fn+F3 / tecla muerta | **APROBADO (sí es aceptable)** | Antes: factory reset + Win+Tab; ahora: solo Win+Tab (Vista de tareas). No aparece tecla muerta nueva y el resto de `key_comb_list` no cambia | Documentar Fn+F3 = Vista de tareas en release notes |

**Veredicto final: VETO** (único y de artefacto, no de binario): completar PB-03 en `q1_pro.c:143` y regenerar el parche. Los 5 bins publicados son válidos tal cual; al ser código no compilado, no exige recompilar ni cambia sus sha256.

**Re-review (VETO resuelto) — 2026-10-26:** `git diff` muestra `:143` y `:212` con `PRODUCT` (2+/2− en q1; q6 0/3); `STR(PRODUCT)` solo queda en 8 líneas comentadas del baseline; parche con 33 ficheros, 0 fuera de `keyboards/keychron/`, ambos fixes q1 + retirada q6 y `git apply --check` sobre `c8b2b23` rc=0; 2/5 bins muestreados con sha256 = manifest y tamaños 62.144–62.984 B. **Veredicto final: APROBADO — v1.0.0 publicable.**
