#!/bin/bash
# Kaizen — Restore last applied theme state on login
# Add to Hyprland autostart: exec-once = ~/.local/share/kaizen/bin/restore_state.sh

KAIZEN_BASE="$HOME/.local/share/kaizen"
STATE_FILE="$KAIZEN_BASE/state/current_theme"

if [ -f "$STATE_FILE" ]; then
    THEME=$(cat "$STATE_FILE")
    if [ -n "$THEME" ]; then
        # Re-apply theme silently (regenerates files + reloads apps)
        python3 -c "
import sys, os
sys.path.insert(0, '$KAIZEN_BASE')
from engine.theme_engine import ThemeEngine
engine = ThemeEngine('$KAIZEN_BASE')
engine.apply_theme('$THEME', silent=True)
" 2>/dev/null

        # Restore wallpaper if swww is available
        WALLPAPER_STATE="$KAIZEN_BASE/state/current_wallpaper"
        if [ -f "$WALLPAPER_STATE" ] && command -v awww-daemon &>/dev/null; then
            # Ensure daemon is running
            pgrep -x awww-daemon >/dev/null || awww-daemon &
            sleep 0.5
            awww img "$(cat "$WALLPAPER_STATE")" --transition-type fade --transition-duration 1
        fi
    fi
fi
