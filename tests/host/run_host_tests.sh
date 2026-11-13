#!/usr/bin/env bash
# Host-side parser tests for the CKBT51/LKBT51 links (no hardware needed).
#
# usage: tests/host/run_host_tests.sh <path to a patched Keychron QMK tree>
#
# Extracts ckbt51_task() and lkbt51_read()/lkbt51_task() from the tree, builds
# them against a fake UART/SPI transport with AddressSanitizer and UBSan, and
# fails on any sanitizer report or unexpected event count.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
tree="$(cd "${1:?usage: $0 <qmk tree>}" && pwd)"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

python3 "$here/extract.py" "$tree" "$work"
cflags=(-g -O1 -fno-omit-frame-pointer "-fsanitize=address,undefined" -fno-sanitize-recover=all -w -I "$work")
wake='(void)0'   # the unpatched parser has no reset hook
grep -q 'void ckbt51_parser_reset(void)' "$work/ck.inc" && wake='ckbt51_parser_reset()'
cc "${cflags[@]}" -DINC='"ck.inc"' -DWAKE_RESET="$wake" "$here/ck_harness.c" -o "$work/ck"
cc "${cflags[@]}" -DINC='"lk.inc"' "$here/lk_harness.c" -o "$work/lk"

fail=0
run() {
    local bin=$1 case=$2 out
    if ! out=$(ASAN_OPTIONS=detect_leaks=0 "$work/$bin" "$case" 2>&1); then
        echo "FAIL $bin $case: sanitizer or crash"; echo "$out" | tail -20; fail=1; return
    fi
    local got want
    got=$(sed -n 's/.*\(events\|packets\)=\([0-9]*\) expected=.*/\2/p' <<<"$out")
    want=$(sed -n 's/.*expected=\([0-9]*\).*/\1/p' <<<"$out")
    if [[ -z "$got" || "$got" != "$want" ]]; then
        echo "FAIL $out"; fail=1
    else
        echo "ok   $out"
    fi
}
for t in 1 2 3 4 5 6; do run ck "$t"; done
for t in 1 2 3; do run lk "$t"; done
exit $fail
