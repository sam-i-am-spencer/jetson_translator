#!/usr/bin/env bash
# Install udev rule for persistent ALSA card names by USB port.
#
# Cards are identified by the physical USB port they're plugged into:
#   Port 2.4 -> ALSA name: translator_en  (English card)
#   Port 2.3 -> ALSA name: translator_zh  (Chinese card)
#
# This means you can swap the card in port 2.3 for any USB audio device
# and it will automatically be named translator_zh — no config changes needed.
#
# After running this script, replug both USB sound cards (or reboot) for
# the names to take effect. Verify with: cat /proc/asound/cards
set -euo pipefail

RULES_FILE="/etc/udev/rules.d/99-translator-audio.rules"

sudo tee "$RULES_FILE" << 'EOF'
# Jetson Translator - persistent ALSA names by USB port
# English card: port 2.4 -> plughw:translator_en,0
SUBSYSTEM=="sound", KERNEL=="card*", KERNELS=="1-2.4", ATTR{id}="translator_en"
# Chinese card: port 2.3 -> plughw:translator_zh,0
# Swap the card in this port freely - name stays stable
SUBSYSTEM=="sound", KERNEL=="card*", KERNELS=="1-2.3", ATTR{id}="translator_zh"
EOF

sudo udevadm control --reload-rules

echo "Rule installed at $RULES_FILE"
echo "Replug both USB sound cards (or reboot) to apply."
echo "Verify with: cat /proc/asound/cards"
