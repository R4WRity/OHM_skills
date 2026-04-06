#!/bin/bash
# Reset Wallpaper Bridge and Validate
# Usage: ./reset_and_validate.sh

echo "=== Wallpaper Bridge Reset & Validation ==="

# Kill existing bridge
pkill -f "bridge_server.py" 2>/dev/null
sleep 2

# Start bridge
cd projects/wallpapers/dataviz/retro-terminal
python bridge_server.py &
sleep 3

echo "Bridge restarted, running visual validation..."

# Run visual validation
cd ../../../..
python skills/diagnostics/scripts/visual_validate_wallpaper.py

echo ""
echo "=== Complete ==="
