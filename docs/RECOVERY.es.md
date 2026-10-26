# Guía de recuperación — qué hacer si un flasheo sale mal

[English](RECOVERY.md) · **Español**

El dato más importante: **el bootloader ROM (DFU) del STM32L432 vive en memoria de
solo lectura y no se puede borrar flasheando firmware.** Hagas lo que hagas, o se
interrumpa como se interrumpa el flasheo, el teclado siempre se puede volver a
poner en modo DFU y reflashear. No existe un camino software hacia un brick
permanente.

Dicho esto, un flasheo malo puede dejar el teclado con aspecto de muerto. Sigue
esta guía en orden.

---

## 1. Identifica qué ha pasado

| Síntoma | Causa más probable | Ir a |
|---|---|---|
| No enumera nada (ningún dispositivo USB) | Imagen mala/incompleta, variante equivocada, flasheo interrumpido | [§2](#2-entrar-en-dfu-manualmente) |
| Enumera, pero no funcionan las teclas | Variante equivocada, keymap/EEPROM corruptos | [§2](#2-entrar-en-dfu-manualmente) → reflashear |
| Las teclas van, pero el layout/retroiluminación está mal | Variante equivocada (otro layout o retroiluminación) | [§6](#6-variante-equivocada) |
| USB va, Bluetooth no | Módulo sin inicializar, firmware del módulo, radio | [§7](#7-problemas-solo-de-bluetooth) |
| Se queda en DFU/bootloader tras flashear | El flasheo falló antes del paso `:leave` | [§2](#2-entrar-en-dfu-manualmente) → reflashear |
| Errores de `dfu-util` (`LIBUSB_ERROR_ACCESS`, no hay dispositivo) | Permisos, cable, puerto, hub | [§3](#3-problemas-de-dfu-util-y-drivers) |

## 2. Entrar en DFU manualmente

Hazlo **con el teclado desenchufado**:

1. Pon el interruptor en **Off** (posición central en la mayoría de modelos).
2. Mantén **Esc** (la tecla de arriba a la izquierda).
3. Sin soltar Esc, pasa el interruptor a **Cable** y enchufa el USB.
4. Mantén Esc ~2 segundos y suelta.

El teclado debe aparecer como:

```
0483:df11 STMicroelectronics STM32 BOOTLOADER
```

Compruébalo con `lsusb` (Linux/macOS) o el Administrador de dispositivos / QMK
Toolbox (Windows).

**Si tu modelo tiene botón de reset** (bajo la barra espaciadora en muchos Pro),
puedes mantenerlo mientras enchufas, o pulsarlo dos veces rápido.

**Si no funciona**, prueba en este orden:

1. Otro cable USB (de datos, no solo de carga).
2. Otro puerto — preferiblemente **USB-A 2.0** directo al equipo, sin hub, sin
   dock, sin adaptador USB-C.
3. Off → espera 5 s → Esc → Cable otra vez.
4. Mantén **Esc + reset** a la vez mientras enchufas.
5. En portátiles, desenchufa el cargador (algunas tomas de tierra interfieren en
   la detección DFU).

Una vez en DFU, reflashea la imagen correcta:

```bash
sudo dfu-util -d 0483:df11 -a 0 -s 0x08000000:leave -D \
  firmware/<modelo>/<variante>/<fichero>.bin
```

`-s 0x08000000:leave` escribe la imagen al inicio de la flash y reinicia después.
`dfu-util` debe terminar con `File downloaded successfully` y
`Transitioning to dfuMANIFEST state`.

## 3. Problemas de `dfu-util` y drivers

### Regla udev en Linux

Si ves `LIBUSB_ERROR_ACCESS`, `Cannot open DFU device 0483:df11` o necesitas
`sudo` siempre:

```bash
sudo tee /etc/udev/rules.d/60-stm32-dfu.rules >/dev/null <<'EOF'
SUBSYSTEM=="usb", ATTR{idVendor}=="0483", ATTR{idProduct}=="df11", MODE="0666", TAG+="uaccess"
EOF
sudo udevadm control --reload-rules && sudo udevadm trigger
```

Desenchufa y vuelve a entrar en DFU. Esta regla es independiente de la de VIA de
Keychron (`3434:*`), que solo aplica al teclado en modo normal.

### "No DFU capable USB device found"

- Confirma que `lsusb` muestra `0483:df11`; si muestra `3434:02d1` (u otro PID),
  el teclado ha arrancado normal: no estás en DFU.
- Si no aparece nada, el MCU puede estar ejecutando una imagen rota; repite §2 con
  otro cable/puerto. El bootloader ROM se ejecuta antes que cualquier firmware,
  así que siempre es alcanzable con el MCU alimentado.
- En Windows, instala el driver WinUSB con [Zadig](https://zadig.akeo.ie/) para
  `STM32 BOOTLOADER`, o usa QMK Toolbox, que lo gestiona.

### macOS

No hace falta driver. `brew install dfu-util`. Si no aparece, mira
`system_profiler SPUSBDataType` buscando `STM32 BOOTLOADER`.

## 4. Verifica la imagen antes de flashear

Una causa sorprendentemente habitual de "flasheo malo" es una descarga truncada o
equivocada:

```bash
sha256sum -c SHA256SUMS                 # debe imprimir OK para tu fichero
python3 tools/verify_bins.py <fichero.bin>  # sufijo DFU, VID/PID, CRC, tamaño
```

Un fichero que falla el CRC o el tamaño no arrancará bien. Vuelve a descargarlo.

## 5. Interrupciones del flasheo / corte de luz

Si se desconecta el cable a mitad, el MCU puede quedar con una imagen a medias y
no enumerar como teclado. Tiene arreglo: el bootloader ROM sigue intacto. Vuelve
a entrar en DFU (§2) y flashea otra vez. No te pongas a apagar y encender en
bucle; vuelve a DFU.

## 6. Variante equivocada

Señales típicas: el teclado funciona pero hay teclas cambiadas o que faltan, la
retroiluminación hace cosas raras, o VIA muestra un layout distinto.

1. Identifica tu PID en modo cable normal: `lsusb | grep 3434`.
2. Búscalo en la tabla de modelos / `firmware/manifest.json`.
3. Entra en DFU y flashea la imagen de ese PID exacto.
4. Restaura tu JSON de keymap en VIA / Keychron Engine.

Flashear otro layout no es destructivo: el MCU es el mismo y al bootloader le da
igual qué variante escribas.

## 7. Problemas solo de Bluetooth

Si el USB va pero el Bluetooth no:

1. Asegúrate de que la batería tiene carga y el interruptor está en **BT**, no en
   Cable.
2. Re-empareja: borra el teclado de la lista Bluetooth del host, luego mantén la
   combinación de emparejamiento (normalmente **Fn + 1/2/3** durante 3 s) y
   empareja de nuevo.
3. Reflashea el firmware una vez (un arranque limpio reenvía los parámetros del
   módulo en el primer init de Bluetooth).
4. Si el módulo no responde en absoluto (no empareja, no hay LED), el problema
   puede ser el **firmware del módulo CKBT51**. Ese firmware es cerrado y solo se
   actualiza con la herramienta oficial de Keychron
   (`Keychron_Bt_Firmware_Upgrade_v0.14.exe`, Windows). **Esa herramienta
   sobrescribe el firmware del MCU**, así que después hay que volver a flashear la
   build de este proyecto.
5. Las causas de radio (interferencias, ahorro de energía del adaptador) quedan
   fuera de este firmware. En Linux, comprueba que el adaptador no entra en
   autosuspend (`usbcore.autosuspend=-1`, o una regla udev para el adaptador) y
   mira `btmon` para ver si la desconexión es `0x08` (radio/timeout) o `0x13`
   (remota/usuario).

## 8. Restaurar el firmware de fábrica

Si quieres volver al firmware de Keychron:

1. Descarga el firmware oficial de tu modelo/variante exacto de Keychron (o usa la
   actualización de firmware de Keychron Engine).
2. Entra en DFU como en §2.
3. Flashea el `.bin` oficial con el mismo comando `dfu-util`, o usa Keychron
   Engine / QMK Toolbox.

Tu keymap vive en la EEPROM y normalmente sobrevive; aun así, conserva el JSON que
exportaste antes de flashear.

## 9. Limpiar la EEPROM (último recurso para keymaps raros)

Si el teclado funciona pero se comporta como si las teclas estuvieran
remapeadas tras restaurar el firmware de fábrica, limpia la EEPROM:

- En VIA: **Settings → Reset EEPROM** (si el firmware habla VIA), o
- Flashea una imagen `default` (sin VIA) una vez — QMK inicializa una EEPROM
  limpia — y luego reflashea la imagen que quieras, o
- Usa el botón **Clear EEPROM** de QMK Toolbox (en STM32 flashea una imagen
  pequeña de reset).

## 10. ¿Sigue atascado?

Abre un issue con:

- modelo exacto + PID (`lsusb`),
- nombre del binario y SHA-256,
- salida completa de `dfu-util`,
- si `0483:df11` aparece alguna vez en `lsusb`,
- SO y cable/puerto usados.

**No** incluyas direcciones MAC, nombres de equipo ni rutas personales.

**Recordatorio:** en el peor caso, el bootloader ROM sigue funcionando. Un teclado
que "no hace nada" es casi siempre un teclado al que hay que entrar en DFU
correctamente con un cable bueno.
