#!/usr/bin/env python3
"""Extract the CKBT51/LKBT51 parser code from a QMK tree for the host harness.

usage: extract.py <qmk tree> <out dir>
"""
import sys
from pathlib import Path

root, out = Path(sys.argv[1]), Path(sys.argv[2])
src = (root / "keyboards/keychron/bluetooth/ckbt51.c").read_text()
pre = ""
if "#ifndef CKBT51_RX_FRAME_TIMEOUT_MS" in src:
    pre = src[src.index("#ifndef CKBT51_RX_FRAME_TIMEOUT_MS"):src.index("void ckbt51_init(")]
state = ""
if "void ckbt51_parser_reset(void) {" in src:
    reset = src.index("void ckbt51_parser_reset(void) {")
    state = src[src.rindex("static bool", 0, reset):src.index("void ckbt51_task(void) {")]
(out / "ck.inc").write_text(pre + "\n" + state + "\n" + src[src.index("void ckbt51_task(void) {"):])

lk = (root / "keyboards/keychron/common/wireless/lkbt51.c").read_text()
read = lk[lk.index("void lkbt51_read(uint8_t* payload, uint8_t len) {"):lk.index("void lkbt51_send_keyboard(")]
(out / "lk.inc").write_text(read + "\n" + lk[lk.index("void lkbt51_task(void) {"):])
