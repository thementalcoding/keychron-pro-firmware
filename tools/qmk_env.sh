# shellcheck shell=bash
# Generic QMK build environment for this firmware.
# Edit the paths below to match your local install, then:  source tools/qmk_env.sh
#
# The three variables are intentionally left commented out so that sourcing this
# file never clobbers an existing environment. Uncomment/adjust as needed.
#
# export PATH="$HOME/qmk/tools/arm-gnu-toolchain/bin:$PATH"   # arm-none-eabi-gcc 12/13/14
# export QMK="$HOME/.venv-qmk/bin/qmk"                        # QMK CLI (python venv)
# export QMK_FIRMWARE="$HOME/qmk_firmware"                    # QMK fork checkout (wls_2025q1 branch)
#
# Build example (from the QMK checkout):
#   qmk compile -kb keychron/k13_pro/iso/rgb -km via
