#!/bin/bash
# Kaizen SDDM Deploy — copies themed QML + components to SDDM theme dir
THEME_DIR="/usr/share/sddm/themes/corners"
GEN_DIR="$1"
TPL_DIR="$2"

cp "$GEN_DIR/sddm-Main.qml" "$THEME_DIR/Main.qml" || exit 1
if [ -f "$GEN_DIR/sddm-theme.conf" ]; then
  cp "$GEN_DIR/sddm-theme.conf" "$THEME_DIR/theme.conf"
fi
# Copy components
if [ -d "$TPL_DIR/sddm/components" ]; then
  cp -r "$TPL_DIR/sddm/components/"* "$THEME_DIR/components/"
fi
echo "SDDM theme deployed successfully."
