#!/usr/bin/env bash
# flash_k13.sh — Flashea el Keychron K13 Pro (ISO RGB, keymap via) con el firmware auditado.
# Uso:  bash tools/flash_k13.sh [bin]        (flasheo completo)
#       bash tools/flash_k13.sh --check [bin] (solo prechequeos, no flashea)
#       K13_BIN=/ruta/al/bin bash tools/flash_k13.sh
set -u
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BIN="${K13_BIN:-${REPO_ROOT}/.build/keychron_k13_pro_iso_rgb_via.bin}"
CHECK=0
for arg in "$@"; do
    if [ "$arg" = "--check" ]; then
        CHECK=1
    else
        BIN="$arg"
    fi
done
SUF="$(dirname "$0")/dfu-suffix"
VID_PID="0483:df11"
ADDR="0x08000000:leave"

die() { echo "ERROR: $*" >&2; exit 1; }

# --- Prechequeos ---
[ -f "$BIN" ] || die "bin no encontrado: $BIN"
command -v dfu-util >/dev/null 2>&1 || die "dfu-util no instalado (sudo pacman -S dfu-util)"
if [ -x /usr/bin/dfu-suffix ]; then
    /usr/bin/dfu-suffix -c "$BIN" >/dev/null 2>&1 || die "sufijo DFU inválido en el bin (dfu-suffix real)"
else
    [ -x "$SUF" ] || die "wrapper dfu-suffix no encontrado: $SUF"
    "$SUF" -c -a "$BIN" >/dev/null 2>&1 || die "sufijo DFU inválido en el bin (wrapper)"
fi
echo "OK: bin $(stat -c %s "$BIN") bytes, sufijo DFU válido."

if [ "$CHECK" = 1 ]; then
    echo "CHECK MODE: prechequeos correctos (no se ha flasheado nada)."
    exit 0
fi

# --- Espera del bootloader ---
echo ""
echo ">>> PON AHORA el teclado en DFU: switch a Off → MANTÉN Esc → switch a Cable."
echo ">>> Esperando bootloader [${VID_PID}] hasta 60 s..."
found=0
for i in $(seq 60); do
    if dfu-util -l 2>/dev/null | grep -q "$VID_PID"; then
        echo ">>> Bootloader DFU detectado (t=${i}s)."
        found=1
        break
    fi
    sleep 1
done
[ "$found" = 1 ] || die "No se detectó el bootloader en 60 s. Repite: Off → mantener Esc → Cable, y relanza."

# --- Flasheo ---
echo ">>> Flasheando (no toques nada)..."
dfu-util -d "$VID_PID" -a 0 -s "$ADDR" -D "$BIN" || die "falló el flasheo (si fue un error de permisos, relanza con sudo)"
sleep 2

echo ""
echo "=== FLASHEO COMPLETADO: el teclado reinicia con el firmware nuevo ==="
echo "Siguientes pasos:"
echo "  1) Pon el switch en BT (o Cable, como uses)."
echo "  2) Keychron Engine / VIA → LOAD de tu backup JSON (la config se borró con el flasheo)."
echo "  3) Compara polling (desde la raíz del repo):  sudo python3 tools/medir_polling.py -m tap -t 10"
echo "  4) Si algo fuera mal: el bootloader ROM sigue intacto — repite este script con el bin"
echo "     original de Keychron (Engine) o reflashea; no hay brick posible (ver docs/AUDIT.md)."
