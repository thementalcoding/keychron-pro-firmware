# Auditoría de gama — teclados Keychron con CKBT51 / LKBT51

Fecha: 2026-10-26 · Repo: `firmware_qmk/wls_2025q1` · Rama `k13-pro-bt-fixes` (HEAD `90f4d1d`, parches K13 ya aplicados) · Solo lectura.

## Resumen ejecutivo

- 67 teclados de producto en `keyboards/keychron/`: **26 con CKBT51** (familia K/Q Pro, 95 variantes de build) y **41 con LKBT51 vía SPI** (`common/wireless`, sufijo `_max`/`_version_N`). No hay teclados solo-cable en esta gama.
- El parche compartido de `keyboards/keychron/bluetooth/` (parser UART acotado, flush en `EVT_RECONNECTING`, retry timer, gate LPM, rate-limit connect, FAST_WAKE opt-in) **beneficia a los 26 CKBT51**; los 41 LKBT51 usan otra pila (`common/wireless`) y **no reciben ninguno** de esos arreglos.
- Parámetros: **26/26 CKBT51 con `report_rate=133` y `reconnect_timeout=60`** (2 bloques por teclado; q1_pro 3). `connected_idle_timeout=7200`, `pairing_timeout=180`, `pairing_mode=0` intactos en todos.
- **P0 — 25 de 26 CKBT51 siguen con la ventana de init `< 1000 ms`** (solo k13_pro tiene `< 5000`): si el módulo tarda en arrancar, los params 133/60 no se aplican nunca. Es el mismo bug que corregimos en el K13.
- Sin hallazgos en los otros riesgos buscados: 0 teclados con `DEBOUNCE_TYPE` eager/asym activo, 0 con `CKBT51_FAST_WAKE`, 0 con overrides LPM, y **0 casos de HC595 con >16 columnas sobre `uint16_t`** (los anchos 17–21 usan `uint32_t` o selección bit a bit).
- La pila LKBT51 conserva 90 Hz/5 s (intencionado, fuera de alcance) y mantiene dos defectos análogos a los que arreglamos: sin flush al reconectar y `memcpy` sin acotar en su `dfu_tx`.

---

## Tabla 1 — Inventario y clasificación (CKBT51)

VID común `0x3434` en toda la gama. `matrix`: implementación propia (`<board>/matrix.c`) o compartida (`common/matrix.c`, `custom_lite`, tipo elegido por `HC595_END_INDEX`). Debounce: todos `sym_defer_g` (default de `builddefs/common_features.mk:679`). LPM: ninguno sobreescribe `LOW_POWER_MODE`/`RUN_MODE_PROCESS_TIME` → default `PM_STOP1` / 1000 ms (`bluetooth/bluetooth.h:23`, `bluetooth/lpm.h:19`).

| Teclado | Variantes | VID / PID | Matrix | Debounce | Fichero params |
|---|---|---|---|---|---|
| k1_pro | 4 | 3434 / 0210-0214 | HC595 propio (uint16, 1 directa, 16 shift) | sym_defer_g | k1_pro.c |
| k2_pro | 6 | 3434 / 0220-0225 | HC595 propio (uint16, 16 cols) | sym_defer_g | k2_pro.c |
| k3_pro | 6 | 3434 / 0230-0235 | HC595 propio (uint16, 1 directa) | sym_defer_g | k3_pro.c |
| k4_pro | 4 | 3434 / 0240-0244 | HC595 propio (uint16, 2 directas, 16 shift) | sym_defer_g | k4_pro.c |
| k5_pro | 6 | 3434 / 0250-0255 | HC595 propio (**uint32**, 21 cols) | sym_defer_g | k5_pro.c |
| k6_pro | 5 | 3434 / 0260-0264 | HC595 propio (uint16, 15 cols) | sym_defer_g | k6_pro.c |
| k7_pro | 4 | 3434 / 0270-0274 | HC595 propio (uint16, 1 directa) | sym_defer_g | k7_pro.c |
| k8_pro | 6 | 3434 / 0280-0285 | HC595 propio (uint16, 1 directa + caso borde) | sym_defer_g | k8_pro.c |
| k9_pro | 6 | 3434 / 0290-0295 | HC595 propio (uint16, selección 1 bit) | sym_defer_g | k9_pro.c |
| k10_pro | 6 | 3434 / 02A0-02A5 | HC595 propio (**uint32**, 21 cols) | sym_defer_g | k10_pro.c |
| k11_pro | 4 | 3434 / 02B0-02B9 | HC595 propio (uint16, 16 cols) | sym_defer_g | k11_pro.c |
| k12_pro | 2 | 3434 / 02C0-02C3 | HC595 propio (uint16, 14 cols) | sym_defer_g | k12_pro.c |
| k13_pro | 4 | 3434 / 02D0-02D4 | HC595 propio (uint16, selección 1 bit, 17 cols) | sym_defer_g (+opt-in comentado) | k13_pro.c |
| k14_pro | 2 | 3434 / 02E0-02E3 | HC595 propio (uint16, 16 cols) | sym_defer_g | k14_pro.c |
| k15_pro | 2 | 3434 / 02F6-02F9 | HC595 compartido (END=15 → uint16, 16 cols) | sym_defer_g | k15_pro.c |
| k17_pro | 4 | 3434 / 0206-020A | HC595 propio (SIZE_T, END=19 → uint32) | sym_defer_g | k17_pro.c |
| q1_pro | 3 | 3434 / 0610,0611,A612 | HC595 propio (uint16, 16 cols) | sym_defer_g | q1_pro.c (3 bloques) |
| q2_pro | 2 | 3434 / 0620-0621 | HC595 propio (uint16, 16 cols) | sym_defer_g | q2_pro.c |
| q3_pro | 5 | 3434 / 0630-0634 | HC595 propio (**uint32**, 16/18 cols) | sym_defer_g | q3_pro.c |
| q4_pro | 2 | 3434 / 0640-0641 | HC595 compartido (END=13, 14 cols) | sym_defer_g | q4_pro.c |
| q5_pro | 2 | 3434 / 0650-0651 | HC595 compartido (END=19 → uint32, 20 cols) | sym_defer_g | q5_pro.c |
| q6_pro | 2 | 3434 / 0660-0661 | HC595 compartido (END=20 → uint32, 21 cols) | sym_defer_g | q6_pro.c |
| q8_pro | 2 | 3434 / 0680-0681 | HC595 compartido (END=14, 15 cols) | sym_defer_g | q8_pro.c |
| q10_pro | 2 | 3434 / 06A0-06A1 | HC595 compartido (END=15, 16 cols) | sym_defer_g | q10_pro.c |
| q13_pro | 2 | 3434 / 06D0-06D1 | HC595 compartido (END=18 → uint32, 19 cols) | sym_defer_g | q13_pro.c |
| q14_pro | 2 | 3434 / 06E0-06E1 | HC595 compartido (END=18 → uint32, 19 cols) | sym_defer_g | q14_pro.c |

**LKBT51 (41)**, pila `common/wireless` (SPI, `lkbt51.c`), matrix por pines directos (sin HC595), debounce default, params en `common/wireless/keychron_wireless_common.c:87-97` (90 Hz/5 s):
`k0_max · k10_max · k10_version_2 · k11_max · k13_max · k15_max · k17_max · k1_max · k1_version_6 · k2_max · k2_version_3 · k3_max · k3_version_3 · k4_version_3 · k5_max · k5_version_2 · k7_max · k8_max · k8_version_2 · q0_max · q10_max · q12_max · q13_max · q14_max · q15_max · q1_max · q2_max · q3_max · q5_max · q60_max · q65_max · q6_max · q8_max · v10_max · v1_max · v2_max · v3_max · v4_max · v5_max · v6_max · v8_max`

## Tabla 2 — Parámetros y ventana de init (CKBT51)

Leyenda: ✅ correcto · ❌ bug de ventana (`<1000`).

| Teclado | rate | reconnect | idle | pairing t/mode | bloques | ventana init | |
|---|---|---|---|---|---|---|---|
| k1_pro | 133 | 60 | 7200 | 180 / 0 | 2 | 1000 | ❌ |
| k2_pro | 133 | 60 | 7200 | 180 / 0 | 2 | 1000 | ❌ |
| k3_pro | 133 | 60 | 7200 | 180 / 0 | 2 | 1000 | ❌ |
| k4_pro | 133 | 60 | 7200 | 180 / 0 | 2 | 1000 | ❌ |
| k5_pro | 133 | 60 | 7200 | 180 / 0 | 2 | 1000 | ❌ |
| k6_pro | 133 | 60 | 7200 | 180 / 0 | 2 | 1000 | ❌ |
| k7_pro | 133 | 60 | 7200 | 180 / 0 | 2 | 1000 | ❌ |
| k8_pro | 133 | 60 | 7200 | 180 / 0 | 2 | 1000 | ❌ |
| k9_pro | 133 | 60 | 7200 | 180 / 0 | 2 | 1000 | ❌ |
| k10_pro | 133 | 60 | 7200 | 180 / 0 | 2 | 1000 | ❌ |
| k11_pro | 133 | 60 | 7200 | 180 / 0 | 2 | 1000 | ❌ |
| k12_pro | 133 | 60 | 7200 | 180 / 0 | 2 | 1000 | ❌ |
| **k13_pro** | 133 | 60 | 7200 | 180 / 0 | 2 | **5000** | ✅ |
| k14_pro | 133 | 60 | 7200 | 180 / 0 | 2 | 1000 | ❌ |
| k15_pro | 133 | 60 | 7200 | 180 / 0 | 2 | 1000 | ❌ |
| k17_pro | 133 | 60 | 7200 | 180 / 0 | 2 | 1000 | ❌ |
| q1_pro | 133 | 60 | 7200 | 180 / 0 | **3** | 1000 | ❌ |
| q2_pro | 133 | 60 | 7200 | 180 / 0 | 2 | 1000 | ❌ |
| q3_pro | 133 | 60 | 7200 | 180 / 0 | 2 | 1000 | ❌ |
| q4_pro | 133 | 60 | 7200 | 180 / 0 | 2 | 1000 | ❌ |
| q5_pro | 133 | 60 | 7200 | 180 / 0 | 2 | 1000 | ❌ |
| q6_pro | 133 | 60 | 7200 | 180 / 0 | 2 | 1000 | ❌ |
| q8_pro | 133 | 60 | 7200 | 180 / 0 | 2 | 1000 | ❌ |
| q10_pro | 133 | 60 | 7200 | 180 / 0 | 2 | 1000 | ❌ |
| q13_pro | 133 | 60 | 7200 | 180 / 0 | 2 | 1000 | ❌ |
| q14_pro | 133 | 60 | 7200 | 180 / 0 | 2 | 1000 | ❌ |

Sin valores raros: no hay bloques con 90/5 en CKBT51 ni diferencias de idle/pairing. El 90/5 que queda en el árbol está solo en LKBT51 (`common/wireless/keychron_wireless_common.c:90-91`), decisión ya tomada.

## Tabla 3 — Riesgos análogos

| Riesgo | Resultado | Detalle |
|---|---|---|
| HC595 con shift `uint16_t` y >16 columnas (col. 17 en primer scan) | **0 afectados** | k1 (16 shift + 1 directa), k4 (16 shift + 2), k8 (16 + caso borde), k13/k9 (selección bit a bit) caben; k5/k10/q3 usan `uint32_t`; k17/q5/q6/q13/q14 usan `common/matrix.c` con `SIZE_T` derivado de `HC595_END_INDEX` (19-20 → uint32). Todas las `matrix_init_custom` llaman `unselect_cols()` |
| `DEBOUNCE_TYPE` eager/asym | **0 activos** | Solo k13_pro tiene la línea comentada como opt-in (`k13_pro/rules.mk:5-6`); resto default `sym_defer_g` |
| `CKBT51_FAST_WAKE` | **0 activos** | Único `#ifdef` en `bluetooth/ckbt51.c:159`; ningún `-D` en config/rules |
| `LOW_POWER_MODE` / `RUN_MODE_PROCESS_TIME` propios | **0 en CKBT51** | Defaults compartidos; solo `k0_max` (LKBT51) define `LOW_POWER_MODE PM_STOP1` en su pila |
| `HC595_delay(1)` (≈12,5 ns) | Aplica a 18 teclados CKBT51 | `k13_pro/matrix.c:54` y copias por teclado; el 74HC595 pide ≥20 ns. Riesgo de glitch/ghosting, ya documentado para K13 |
| Pila LKBT51: flush al reconectar | **Falta** | `common/wireless/wireless.c:475-477` (`EVT_RECONNECTING`) no vacía `report_buffer` (análogo a WP-102a) |
| Pila LKBT51: `dfu_tx` sin acotar | **Falta** | `common/wireless/lkbt51.c:637-649`: 7 B de cabecera + `memcpy(len)` en `buf[RAW_EPSIZE=32]` (análogo a WP-101b) |
| Pila LKBT51: parser | No aplica | SPI maestro con `expect_len` fijo (22/64), sin parser de flujo UART |
| Otros workarounds | Nada llamativo | 1-3 `wait_ms()` por teclado en rutas de reset/switch de host; sin bucles de wake propios |

## Acciones priorizadas

**P0 — bug de ventana de init (25 teclados, 1 línea cada uno)**: cambiar `sync_timer_read32() < 1000` → `< 5000` en `bluetooth_enter_disconnected_kb`:
k1_pro.c:228 · k2_pro.c:205 · k3_pro.c:210 · k4_pro.c:205 · k5_pro.c:260 · k6_pro.c:202 · k7_pro.c:221 · k8_pro.c:231 · k9_pro.c:217 · k10_pro.c:237 · k11_pro.c:236 · k12_pro.c:221 · k14_pro.c:219 · k15_pro.c:253 · k17_pro.c:257 · q1_pro.c:233 · q2_pro.c:222 · q3_pro.c:232 · q4_pro.c:207 · q5_pro.c:224 · q6_pro.c:245 · q8_pro.c:225 · q10_pro.c:237 · q13_pro.c:238 · q14_pro.c:224

**P1 — verificación tras el P0**: en 2-3 teclados (p. ej. k14_pro, k15_pro, q1_pro) confirmar con tap test que el suelo baja a ~5 ms (params aplicados de verdad). Requiere hardware. Solo tiene sentido después del P0: con 1 s de ventana la medición puede dar 7 ms y parecer que 133 Hz "no funciona".

**P1 — decisión de alcance sobre LKBT51 (41 teclados)**: o se declara explícitamente fuera de alcance en el informe, o se abre un WP aparte para portar (a) flush en `EVT_RECONNECTING` (`wireless.c:475`), (b) acotado de `lkbt51_dfu_tx` (`lkbt51.c:637`). No tocar 90/5 sin medición: es otro módulo.

**P2 — endurecer `HC595_delay`** (`k13_pro/matrix.c:54` y copias): subir a 2-3 nop exige medir ghosting en hardware; solo si aparecen pulsaciones fantasma.

**No aplica**: LKBT51/params (módulo distinto, cerrado, sin datos); teclados solo-cable (no existen en esta gama); debounce eager (descartado por riesgo 595).

## Anexo

- `docs/ckbt51_boards.csv` — 67 filas: `teclado;variantes;pila;rate;reconnect;ventana_ms;hc595;debounce`.

## Metodología y límites

Datos extraídos de `rules.mk`/`info.json`/`keyboard.json`, bloques `module_param_t` de cada `<board>.c`, y `matrix.c` (propio o `common/matrix.c`). El número de columnas sale de `matrix_pins.cols` de los JSON; en k9_pro/q3_pro (sin `matrix_pins` en root) se dedujo del estilo de selección del `matrix.c`. No se ha compilado ni flasheado nada: todo lo que depende del módulo (aplicación real de 133 Hz/60 s, ghosting) queda pendiente de hardware.
