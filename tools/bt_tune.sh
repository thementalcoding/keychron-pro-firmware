#!/usr/bin/env bash
# bt_tune.sh — utilidades host para el Keychron K13 Pro por Bluetooth (informe §10-13)
# Uso: bt_tune.sh {status|capture|poll}
set -u
KB_MAC="XX:XX:XX:XX:XX:XX"   # Keychron K13 Pro
LOGDIR="/tmp"

need_bluez_utils() {
    if ! command -v btmon >/dev/null 2>&1; then
        echo "Falta bluez-utils (btmon/bluetoothctl). Instala con:"
        echo "  sudo pacman -S bluez-utils"
        exit 1
    fi
}

case "${1:-status}" in
status)
    echo "== Autosuspend adaptador (debe ser delay -1000 / no suspendido) =="
    for d in /sys/bus/usb/devices/*/; do
        if grep -qs 8087 "${d}idVendor" 2>/dev/null; then
            echo "  $(basename "$d"): control=$(cat "${d}power/control") status=$(cat "${d}power/runtime_status") suspended_ms=$(cat "${d}power/runtime_suspended_time")"
        fi
    done
    echo "== Teclado conectado =="
    busctl --system get-property org.bluez "/org/bluez/hci0/dev_${KB_MAC//:/_}" org.bluez.Device1 Connected 2>/dev/null || echo "  no aparece en BlueZ (¿emparejado?)"
    echo "== Eventos uhid del teclado (hoy) =="
    journalctl -b -k --no-pager 2>/dev/null | grep -c "Keychron K13 Pro" | xargs -I{} echo "  {} (re)conexiones este arranque"
    ;;
capture)
    need_bluez_utils
    TS="$(date +%Y%m%d-%H%M%S)"
    LOG="${LOGDIR}/btsnoop-${TS}.log"
    echo "Capturando enlace BT en ${LOG} — reproduce el episodio de ráfagas y pulsa Ctrl+C."
    echo "Después: btmon -r ${LOG} | grep -B2 -A2 -iE 'disconnect|reason' | less"
    echo "Claves: reason 0x08 (Connection Timeout) = radio/interferencia; 0x13 (Remote User Terminated) = el teclado cortó (firmware/sueño)."
    exec sudo btmon -w "${LOG}"
    ;;
poll)
    # Tap test: mide el suelo real del enlace BT (ver informe §7). Con report_rate=133
    # el suelo esperado baja de ~11 ms a ~7.5 ms.
    cd "$(dirname "$0")/.." || exit 1
    echo "Modo tap: pulsa UNA tecla ~200 veces rápido (compara BT vs cable)."
    exec sudo python3 tools/medir_polling.py -m tap
    ;;
*)
    echo "Uso: $0 {status|capture|poll}"
    exit 1
    ;;
esac
