#!/bin/bash
# Kaizen SDDM Deploy — invoked only by the installed Kaizen Polkit helper.
THEME_DIR="/usr/share/sddm/themes/corners"
GEN_DIR="$1"
TPL_DIR="$2"

die() { echo "kaizen-sddm-deploy: $*" >&2; exit 2; }
require_file_within_dir() {
  file_real="$(realpath -e "$1")" || die "missing source file: $1"
  dir_real="$(realpath -e "$2")" || die "missing source directory: $2"
  [ -f "$file_real" ] || die "source is not a regular file: $1"
  case "$file_real" in
    "$dir_real"/*) printf '%s\n' "$file_real" ;;
    *) die "source escapes generated directory: $1" ;;
  esac
}

MAIN_QML="$(require_file_within_dir "$GEN_DIR/sddm-Main.qml" "$GEN_DIR")"
cp "$MAIN_QML" "$THEME_DIR/Main.qml" || exit 1
if [ -e "$GEN_DIR/sddm-theme.conf" ]; then
  THEME_CONF="$(require_file_within_dir "$GEN_DIR/sddm-theme.conf" "$GEN_DIR")"
  cp "$THEME_CONF" "$THEME_DIR/theme.conf"
fi
for WALLPAPER in "$GEN_DIR"/kaizen-wallpaper.*; do
  [ -e "$WALLPAPER" ] || continue
  WALLPAPER_REAL="$(require_file_within_dir "$WALLPAPER" "$GEN_DIR")"
  cp "$WALLPAPER_REAL" "$THEME_DIR/$(basename "$WALLPAPER_REAL")"
done
# Copy only canonical, regular QML component files.  `find -P` never follows a
# component symlink to a file outside the trusted templates tree.
if [ -d "$TPL_DIR/sddm/components" ]; then
  COMPONENTS_DIR="$(realpath -e "$TPL_DIR/sddm/components")" || die "missing components directory"
  TPL_REAL="$(realpath -e "$TPL_DIR")" || die "missing templates directory"
  case "$COMPONENTS_DIR" in
    "$TPL_REAL"/*) ;;
    *) die "components directory escapes templates" ;;
  esac
  mkdir -p "$THEME_DIR/components"
  find -P "$COMPONENTS_DIR" -maxdepth 1 -type f -name '*.qml' -exec cp -- {} "$THEME_DIR/components/" \;
fi
echo "SDDM theme deployed successfully."
