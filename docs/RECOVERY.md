# Recovery guide — what to do if a flash goes wrong

**English** · [Español](RECOVERY.es.md)

The single most important fact: **the STM32L432 ROM bootloader (DFU) lives in
read-only memory and cannot be erased by flashing firmware.** No matter what you
flash, or how badly the flash is interrupted, the keyboard can always be put back
into DFU mode and reflashed. There is no software path to a permanent brick.

That said, a bad flash can leave the keyboard in a state where it looks dead.
Work through this guide in order.

---

## 1. Identify what happened

| Symptom | Most likely cause | Go to |
|---|---|---|
| Keyboard does not enumerate at all (no USB device) | Bad/incomplete image, wrong variant, interrupted flash | [§2](#2-enter-dfu-manually) |
| Enumerates, but no keys work | Wrong variant, corrupted keymap/EEPROM | [§2](#2-enter-dfu-manually) → reflash |
| Keys work but layout/backlight is wrong | Wrong variant (different layout or backlight) | [§6](#6-wrong-variant-flashed) |
| USB works, Bluetooth does not | Module not initialised, module firmware, RF issue | [§7](#7-bluetooth-only-problems) |
| Stuck in DFU / bootloader after flash | Flash failed before the `:leave` step | [§2](#2-enter-dfu-manually) → reflash |
| `dfu-util` errors (`LIBUSB_ERROR_ACCESS`, no device) | Permissions, cable, port, hub | [§3](#3-dfu-utildriver-problems) |

## 2. Enter DFU manually

Do this **with the keyboard unplugged**:

1. Set the power switch to **Off** (middle position on most models).
2. Hold **Esc** (the top-left key).
3. While holding Esc, move the switch to **Cable** and plug the USB cable in.
4. Keep Esc held for ~2 seconds, then release.

The keyboard should now enumerate as:

```
0483:df11 STMicroelectronics STM32 BOOTLOADER
```

Check with `lsusb` (Linux/macOS) or Device Manager / QMK Toolbox (Windows).

**If your model has a reset button** (under the spacebar on many Pro models),
you can instead hold that button while plugging in, or press it twice quickly.

**If that does not work**, try in this order:

1. Another USB cable (data cable, not charge-only).
2. Another port — prefer a **USB-A 2.0** port directly on the computer, no hub,
   no dock, no USB-C adapter.
3. Switch Off → wait 5 s → hold Esc → Cable again.
4. Hold **Esc + reset** together while plugging in.
5. On laptops, unplug the charger (some grounds interfere with DFU detection).

Once in DFU, reflash the correct image:

```bash
sudo dfu-util -d 0483:df11 -a 0 -s 0x08000000:leave -D \
  firmware/<model>/<variant>/<file>.bin
```

`-s 0x08000000:leave` writes the image at the start of flash and reboots
afterwards. `dfu-util` should end with `File downloaded successfully` and
`Transitioning to dfuMANIFEST state`.

## 3. `dfu-util`/driver problems

### Linux udev rule

If you see `LIBUSB_ERROR_ACCESS`, `Cannot open DFU device 0483:df11` or need
`sudo` every time:

```bash
sudo tee /etc/udev/rules.d/60-stm32-dfu.rules >/dev/null <<'EOF'
SUBSYSTEM=="usb", ATTR{idVendor}=="0483", ATTR{idProduct}=="df11", MODE="0666", TAG+="uaccess"
EOF
sudo udevadm control --reload-rules && sudo udevadm trigger
```

Unplug and re-enter DFU. This rule is independent of the Keychron VIA rule
(`3434:*`), which is only for the keyboard in normal mode.

### "No DFU capable USB device found"

- Confirm `lsusb` shows `0483:df11`; if it shows `3434:02d1` (or another PID),
  the keyboard booted normally — you are not in DFU mode.
- If nothing appears at all, the MCU may be running a broken image; retry §2 with
  a different cable/port. The ROM bootloader runs before any firmware, so it is
  always reachable when the MCU has power.
- On Windows, install the WinUSB driver with [Zadig](https://zadig.akeo.ie/) for
  `STM32 BOOTLOADER`, or just use QMK Toolbox, which handles it.

### macOS

No driver needed. `brew install dfu-util`. If the device is not listed, check
`system_profiler SPUSBDataType` for `STM32 BOOTLOADER`.

## 4. Verify the image before flashing

A surprisingly common cause of "bad flash" is a truncated or wrong download:

```bash
sha256sum -c SHA256SUMS                 # must print OK for your file
python3 tools/verify_bins.py <file.bin> # DFU suffix, VID/PID, CRC, size
```

A file that fails CRC or size will not boot correctly. Re-download it.

## 5. Flash interrupts / power loss

If the cable is unplugged mid-flash, the MCU may be left with a partially written
image and will not enumerate as a keyboard. This is recoverable: the ROM
bootloader is still intact. Re-enter DFU (§2) and flash again. Do not repeatedly
power-cycle; just go back to DFU.

## 6. Wrong variant flashed

Typical signs: the keyboard works but keys are swapped/missing, the backlight
behaves oddly, or VIA shows the wrong layout.

1. Identify your PID in normal cable mode: `lsusb | grep 3434`.
2. Match it in the model table / `firmware/manifest.json`.
3. Enter DFU and flash the image for that exact PID.
4. Restore your keymap JSON in VIA / Keychron Engine.

Flashing a different layout is not destructive: the MCU is the same and the
bootloader does not care which variant you write.

## 7. Bluetooth-only problems

If USB works but Bluetooth does not:

1. Make sure the battery is charged and the switch is in **BT**, not Cable.
2. Re-pair: remove the keyboard from the host's Bluetooth list, then hold the
   pairing combo (usually **Fn + 1/2/3** for 3 s) and pair again.
3. Reflash the firmware once (a clean boot re-sends the module parameters on the
   first Bluetooth init).
4. If the module does not respond at all (no pairing, no LED), the **CKBT51
   module firmware** may be the problem. That firmware is closed and is updated
   only with Keychron's official tool
   (`Keychron_Bt_Firmware_Upgrade_v0.14.exe`, Windows). **That tool overwrites
   the MCU firmware**, so after running it you must reflash this project's build.
5. Radio-level causes (interference, adapter power saving) are outside this
   firmware. On Linux, verify the adapter is not autosuspending
   (`usbcore.autosuspend=-1`, or a udev rule for the Bluetooth adapter) and check
   `btmon` for disconnect reason `0x08` (radio/timeout) vs `0x13` (remote/user).

## 8. Restore stock firmware

If you want to go back to Keychron's firmware:

1. Download the official firmware for your exact model/variant from Keychron (or
   use Keychron Engine's firmware update).
2. Enter DFU as in §2.
3. Flash the official `.bin` with the same `dfu-util` command, or use Keychron
   Engine / QMK Toolbox.

Your keymap lives in EEPROM and usually survives; still, keep the JSON export you
made before flashing.

## 9. Clear the EEPROM (last resort for weird keymaps)

If the keyboard works but behaves as if keys are remapped after restoring stock
firmware, clear the EEPROM:

- In VIA: **Settings → Reset EEPROM** (if the firmware speaks VIA), or
- Flash a `default` (non-VIA) image once — QMK initialises a fresh EEPROM — then
  reflash the image you want, or
- Use QMK Toolbox's **Clear EEPROM** button (STM32: it flashes a small reset
  image).

## 10. Still stuck?

Open an issue with:

- exact model + PID (`lsusb`),
- binary name and SHA-256,
- what `dfu-util` prints (full output),
- whether `0483:df11` ever appears in `lsusb`,
- OS and cable/port used.

Do **not** include MAC addresses, hostnames or personal paths.

**Reminder:** in the worst case, the ROM bootloader still works. A keyboard that
"does nothing" is almost always a keyboard that needs DFU mode entered correctly
with a good cable.
