#!/usr/bin/env python3
"""Verify the DFU-suffixed firmware binaries shipped in firmware/.

Checks per file:
  * size fits the STM32L432 flash (256 KiB)
  * 16-byte DFU suffix: bcdDevice/pid/vid, bcdDFU == 0x0100 (raw, not DfuSe),
    "UFD" signature, bLength == 0x10, CRC == ~crc32(all bytes except CRC)
  * VID/PID == 0x0483:0xDF11 (STM32 ROM DFU)

If firmware/ contains no binaries the check passes with a warning (the tree can
legitimately be between releases); a malformed binary always fails.

Usage:
    python3 tools/verify_bins.py [file ...]   # default: firmware/**/*.bin (recursive)
"""
import binascii
import glob
import os
import struct
import sys

FLASH_LIMIT = 256 * 1024
EXPECT_VID = 0x0483
EXPECT_PID = 0xDF11


def check(path: str) -> list[str]:
    errors = []
    size = os.path.getsize(path)
    if size > FLASH_LIMIT:
        errors.append(f"size {size} > {FLASH_LIMIT}")
    if size < 17:
        return errors + ["file too small"]

    with open(path, "rb") as fh:
        data = fh.read()

    suffix = data[-16:]
    _bcd_dev, pid, vid, bcd_dfu = struct.unpack("<HHHH", suffix[0:8])
    signature = suffix[8:11]
    length = suffix[11]
    stored_crc = struct.unpack("<I", suffix[12:16])[0]
    calc_crc = (~binascii.crc32(data[:-4])) & 0xFFFFFFFF

    if signature != b"UFD":
        errors.append(f"missing UFD signature (got {signature!r})")
    if length != 0x10:
        errors.append(f"bLength {length:#04x} != 0x10")
    if bcd_dfu != 0x0100:
        errors.append(f"bcdDFU {bcd_dfu:#06x} != 0x0100 (DfuSe marker!)")
    if (vid, pid) != (EXPECT_VID, EXPECT_PID):
        errors.append(f"VID:PID {vid:04X}:{pid:04X} != {EXPECT_VID:04X}:{EXPECT_PID:04X}")
    if stored_crc != calc_crc:
        errors.append(f"CRC {stored_crc:#010x} != {calc_crc:#010x}")
    return errors


def main() -> int:
    files = sys.argv[1:]
    if not files:
        files = sorted(glob.glob("firmware/**/*.bin", recursive=True))
        if not files:
            print("WARNING: no binaries present in firmware/ — skipping binary checks")
            return 0

    failed = 0
    print(f"{'file':<64} {'size':>7}  result")
    for path in files:
        errors = check(path)
        status = "OK" if not errors else "FAIL: " + "; ".join(errors)
        label = os.path.relpath(path, "firmware") if path.startswith("firmware" + os.sep) else os.path.basename(path)
        print(f"{label:<64} {os.path.getsize(path):>7}  {status}")
        failed += bool(errors)
    print(f"\n{len(files) - failed}/{len(files)} binaries valid")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
