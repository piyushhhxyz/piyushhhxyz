#!/usr/bin/env bash
# Regenerate assets/ascii_art.txt from assets/avatar.png.
# These flags are tuned for the current avatar - re-tune if you swap the photo.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tools/make_ascii.py assets/avatar.png \
  --invert --ramp block --cols 44 --aspect 1.85 \
  --crop 0.22,0.15,0.84,0.80 \
  --vignette 0.50,0.48,0.47,0.55,0.05 \
  --contrast 1.35 --gamma 0.9 --ink 0.12 \
  > assets/ascii_art.txt
echo "wrote assets/ascii_art.txt ($(wc -l < assets/ascii_art.txt) rows)"
