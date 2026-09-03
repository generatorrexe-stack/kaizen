"""Kaizen Preset Engine — Save, list, delete, and apply named configuration snapshots."""
import os
import sys
import time
import tomllib
from engine.accessibility import find_low_contrast_pairs


class PresetEngine:
    """Manages named presets that bundle theme + wallpaper + layout + GTK settings."""

    CURRENT_SCHEMA_VERSION = 1

    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.expanduser("~/.local/share/kaizen")
        self.presets_dir = os.path.join(self.base_dir, "presets")
        self.state_dir = os.path.join(self.base_dir, "state")
        self.themes_dir = os.path.join(self.base_dir, "themes")
        self.layouts_dir = os.path.join(self.base_dir, "layouts")
        os.makedirs(self.presets_dir, exist_ok=True)

    # ------------------------------------------------------------------
    # List all saved presets
    # ------------------------------------------------------------------
    def list_presets(self):
        """Return a list of dicts with metadata for each saved preset."""
        presets = []
        for f in sorted(os.listdir(self.presets_dir)):
            if f.endswith(".toml"):
                path = os.path.join(self.presets_dir, f)
                try:
                    data = self._load_toml(path)
                    presets.append({
                        "id": f[:-5],
                        "name": data.get("name", f[:-5]),
                        "description": data.get("description", ""),
                        "created_at": data.get("created_at", ""),
                        "schema_version": data.get("schema_version", 0),
                        "preset": data.get("preset", {}),
                        "path": path,
                    })
                except Exception as e:
                    print(f"⚠ Error loading preset {f}: {e}", file=sys.stderr)
        return presets

    # ------------------------------------------------------------------
    # Save current state as a named preset
    # ------------------------------------------------------------------
    def save_preset(self, name, description="", overwrite=False):
        """Snapshot the current active state into a preset TOML file.

        Args:
            name: Preset identifier (used as filename, sanitized).
            description: Optional human-readable description.
            overwrite: If False and the preset already exists, raises FileExistsError.

        Returns:
            The absolute path of the saved preset file.
        """
        preset_id = self._sanitize_name(name)
        preset_path = os.path.join(self.presets_dir, f"{preset_id}.toml")

        if os.path.exists(preset_path) and not overwrite:
            raise FileExistsError(
                f"A preset with slug '{preset_id}' already exists at {preset_path}.\n"
                f"(Your name '{name}' maps to the same file as an existing preset.)\n"
                f"Use --overwrite or confirm to replace it."
            )

        # Read current state from every engine's persisted state
        theme_id = self._read_state("current_theme") or ""
        layout_id = self._read_state("current_layout") or "top"
        wallpaper_path = self._read_state("current_wallpaper") or ""

        # Read icon/cursor from what is ACTUALLY applied right now (generated settings.ini),
        # NOT from the theme TOML source — because the user could have changed these
        # independently in the future, and the preset must snapshot reality.
        icon_theme, cursor_theme, cursor_size = self._read_applied_gtk_settings()
        # Fallback to theme TOML only if settings.ini doesn't exist yet
        if icon_theme == "Adwaita" and cursor_theme == "Adwaita" and cursor_size == 24:
            t_icon, t_cursor, t_size = self._read_gtk_settings_from_theme(theme_id)
            # Only use theme values if they're non-default (i.e., actually customized)
            if t_icon != "Adwaita" or t_cursor != "Adwaita" or t_size != 24:
                icon_theme, cursor_theme, cursor_size = t_icon, t_cursor, t_size

        created_at = time.strftime("%Y-%m-%dT%H:%M:%S")

        # Build TOML content manually to preserve formatting and comments
        lines = [
            f'schema_version = {self.CURRENT_SCHEMA_VERSION}',
            f'name = "{self._escape_toml(name)}"',
        ]
        if description:
            lines.append(f'description = "{self._escape_toml(description)}"')
        lines.append(f'created_at = "{created_at}"')
        lines.append("")
        lines.append("[preset]")
        lines.append(f'theme_id = "{self._escape_toml(theme_id)}"')
        lines.append(f'wallpaper_path = "{self._escape_toml(wallpaper_path)}"')
        lines.append(f'layout_id = "{self._escape_toml(layout_id)}"')
        lines.append(f'icon_theme = "{self._escape_toml(icon_theme)}"')
        lines.append(f'cursor_theme = "{self._escape_toml(cursor_theme)}"')
        lines.append(f'cursor_size = {cursor_size}')
        lines.append("")

        with open(preset_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return preset_path

    # ------------------------------------------------------------------
    # Delete a preset
    # ------------------------------------------------------------------
    def delete_preset(self, name):
        """Remove a preset file. Returns True if deleted, raises if not found."""
        preset_id = self._sanitize_name(name)
        preset_path = os.path.join(self.presets_dir, f"{preset_id}.toml")
        if not os.path.exists(preset_path):
            raise FileNotFoundError(f"Preset '{preset_id}' not found.")
        os.remove(preset_path)
        return True

    # ------------------------------------------------------------------
    # Load and validate a single preset
    # ------------------------------------------------------------------
    def load_preset(self, name):
        """Load a preset TOML and return its data dict. Raises if not found."""
        preset_id = self._sanitize_name(name)
        preset_path = os.path.join(self.presets_dir, f"{preset_id}.toml")
        if not os.path.exists(preset_path):
            raise FileNotFoundError(
                f"Preset '{preset_id}' not found.\n"
                f"Available: {', '.join(p['id'] for p in self.list_presets())}"
            )
        return self._load_toml(preset_path)

    # ------------------------------------------------------------------
    # Validate that all resources referenced by a preset still exist
    # ------------------------------------------------------------------
    def validate_preset(self, preset_data):
        """Check that theme, layout, and wallpaper referenced in a preset exist.

        Returns a tuple of (errors, warnings) lists. Empty errors means valid.
        """
        errors = []
        warnings = []
        p = preset_data.get("preset", {})

        theme_id = p.get("theme_id", "")
        if theme_id:
            found = False
            theme_file = os.path.join(self.themes_dir, f"{theme_id}.toml")
            if os.path.exists(theme_file):
                found = True
            else:
                # Walk subdirs like ThemeEngine does
                for root, _, files in os.walk(self.themes_dir):
                    if f"{theme_id}.toml" in files:
                        found = True
                        theme_file = os.path.join(root, f"{theme_id}.toml")
                        break
            if not found:
                errors.append(f"Theme '{theme_id}' not found in {self.themes_dir}")

        layout_id = p.get("layout_id", "")
        if layout_id:
            layout_file = os.path.join(self.layouts_dir, f"{layout_id}.json")
            if not os.path.exists(layout_file):
                errors.append(f"Layout '{layout_id}' not found in {self.layouts_dir}")

        wallpaper_path = p.get("wallpaper_path", "")
        if wallpaper_path and not os.path.exists(wallpaper_path):
            errors.append(f"Wallpaper not found at '{wallpaper_path}'")

        # Presets inherit their palette from the referenced theme, so validate the
        # same WCAG text/background pairs used by `kaizen doctor`.
        if theme_id and 'found' in locals() and found:
            try:
                data = self._load_toml(theme_file)
                colors = data.get("colors", {})
                for warning in find_low_contrast_pairs(colors):
                    warnings.append(f"WCAG AA contrast warning — {warning}")
            except ValueError as exc:
                warnings.append(f"Could not calculate theme contrast: {exc}")

        return errors, warnings

    # ------------------------------------------------------------------
    # Apply a preset (orchestrates existing engines, no reimplementation)
    # ------------------------------------------------------------------
    def apply_preset(self, name, overrides=None):
        """Apply a saved preset by orchestrating ThemeEngine, WallpaperEngine, LayoutEngine.

        Args:
            name: Preset id or name.
            overrides: Optional dict with keys theme_id, wallpaper_path, layout_id
                       to override for this execution only (does NOT modify saved file).

        Raises on validation failure (missing resources).
        All overrides pass through the same validate_preset check as the saved values.
        """
        preset_data = self.load_preset(name)
        p = dict(preset_data.get("preset", {}))

        # Apply runtime overrides (don't touch the saved file)
        if overrides:
            for key in ("theme_id", "wallpaper_path", "layout_id",
                        "icon_theme", "cursor_theme", "cursor_size"):
                if key in overrides and overrides[key] is not None:
                    p[key] = overrides[key]

        # Validate ALL references (including overrides) before touching anything
        validate_data = {"preset": p}
        errors, warnings_list = self.validate_preset(validate_data)
        if errors:
            raise RuntimeError(
                "Preset validation failed — aborting to prevent partial application:\n"
                + "\n".join(f"  ❌ {e}" for e in errors)
            )
        for w in warnings_list:
            print(f"  ⚠  Warning: {w}")

        # Import engines here to avoid circular imports at module level
        from engine.theme_engine import ThemeEngine
        from engine.wallpaper_engine import WallpaperEngine
        from engine.layout_engine import LayoutEngine

        # Snapshot current state BEFORE any mutation, so we can rollback on partial failure.
        # ThemeEngine._auto_backup covers config files; we also save layout/wallpaper state.
        prev_layout = self._read_state("current_layout") or "top"
        prev_theme = self._read_state("current_theme") or ""
        prev_wallpaper = self._read_state("current_wallpaper") or ""

        try:
            # 1. Set layout state FIRST so ThemeEngine renders the right Waybar orientation
            layout_id = p.get("layout_id", "")
            if layout_id:
                self._save_state("current_layout", layout_id)

            # 2. Apply theme (this does backup, render, symlink, reload — full pipeline)
            theme_id = p.get("theme_id", "")
            if theme_id:
                te = ThemeEngine(self.base_dir)
                te.apply_theme(
                    theme_id, silent=True,
                    hook_context={"operation": "preset_apply", "preset_id": name},
                )

            # 3. Apply wallpaper AFTER theme (daemon needs to be ready)
            wallpaper_path = p.get("wallpaper_path", "")
            if wallpaper_path and os.path.exists(wallpaper_path):
                we = WallpaperEngine(self.base_dir)
                we.set_wallpaper(wallpaper_path)

        except Exception as e:
            # Full Operation Rollback: state files AND live configs
            print(f"⚠ Preset application failed mid-way: {e}", file=sys.stderr)
            print("  ↩ Rolling back state and configs to pre-preset values...", file=sys.stderr)
            
            rollback_failed = False
            try:
                # Rollback live configs if ThemeEngine created a backup
                te_fallback = ThemeEngine(self.base_dir)
                te_fallback.rollback()
            except Exception as rollback_err:
                print(f"  ❌ Config rollback also failed: {rollback_err}", file=sys.stderr)
                rollback_failed = True

            # Rollback state pointers
            if prev_layout:
                self._save_state("current_layout", prev_layout)
            if prev_theme:
                self._save_state("current_theme", prev_theme)
            if prev_wallpaper:
                self._save_state("current_wallpaper", prev_wallpaper)
                # Re-apply previous wallpaper visually
                try:
                    we_fallback = WallpaperEngine(self.base_dir)
                    we_fallback.set_wallpaper(prev_wallpaper)
                except Exception as wp_err:
                    print(f"  ❌ Wallpaper rollback failed: {wp_err}", file=sys.stderr)
                    rollback_failed = True

            if rollback_failed:
                raise RuntimeError(
                    f"Preset '{name}' failed, AND automatic rollback ALSO failed.\n"
                    f"Tu sistema podría estar en un estado parcialmente aplicado.\n"
                    f"Revisa ~/.local/share/kaizen/backups/ manualmente para restaurar.\n"
                    f"Original error: {e}"
                ) from e
            else:
                raise RuntimeError(
                    f"Preset '{name}' failed and was completely rolled back.\n"
                    f"Original error: {e}"
                ) from e

        preset_name = preset_data.get("name", name)
        print(f"✅ Preset '{preset_name}' applied successfully!")

    # ------------------------------------------------------------------
    # State persistence (local to preset engine)
    # ------------------------------------------------------------------
    def _save_state(self, key, value):
        os.makedirs(self.state_dir, exist_ok=True)
        path = os.path.join(self.state_dir, key)
        with open(path, "w") as f:
            f.write(value.rstrip("\n") + "\n")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _read_state(self, key):
        path = os.path.join(self.state_dir, key)
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read().strip()
        return None

    def _read_applied_gtk_settings(self):
        """Read icon/cursor/size from the ACTUALLY generated settings.ini (what's live now).

        This is the source of truth for what the user sees right now,
        regardless of whether it came from a theme TOML or a future independent change.
        """
        icon_theme = "Adwaita"
        cursor_theme = "Adwaita"
        cursor_size = 24

        generated_dir = os.path.join(self.base_dir, "generated")
        for ini_name in ("gtk3-settings.ini", "gtk4-settings.ini"):
            ini_path = os.path.join(generated_dir, ini_name)
            if os.path.exists(ini_path):
                try:
                    with open(ini_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    for line in content.splitlines():
                        line = line.strip()
                        if line.startswith("gtk-icon-theme-name="):
                            icon_theme = line.split("=", 1)[1].strip()
                        elif line.startswith("gtk-cursor-theme-name="):
                            cursor_theme = line.split("=", 1)[1].strip()
                        elif line.startswith("gtk-cursor-theme-size="):
                            try:
                                cursor_size = int(line.split("=", 1)[1].strip())
                            except ValueError:
                                pass
                    break  # Found and parsed one, that's enough
                except Exception:
                    pass

        return icon_theme, cursor_theme, cursor_size

    def _read_gtk_settings_from_theme(self, theme_id):
        """Fallback: extract icon/cursor settings from the theme's TOML source."""
        icon_theme = "Adwaita"
        cursor_theme = "Adwaita"
        cursor_size = 24

        if not theme_id:
            return icon_theme, cursor_theme, cursor_size

        theme_file = os.path.join(self.themes_dir, f"{theme_id}.toml")
        if not os.path.exists(theme_file):
            for root, _, files in os.walk(self.themes_dir):
                if f"{theme_id}.toml" in files:
                    theme_file = os.path.join(root, f"{theme_id}.toml")
                    break

        if os.path.exists(theme_file):
            try:
                data = self._load_toml(theme_file)
                icons = data.get("icons", {})
                cursor = data.get("cursor", {})
                icon_theme = icons.get("icon_theme", icon_theme)
                cursor_theme = cursor.get("cursor_theme", cursor_theme)
                cursor_size = cursor.get("cursor_size", cursor_size)
            except Exception:
                pass

        return icon_theme, cursor_theme, cursor_size

    def _load_toml(self, path):
        with open(path, "rb") as f:
            try:
                return tomllib.load(f)
            except tomllib.TOMLDecodeError as e:
                raise ValueError(f"TOML parse error in {path}: {e}") from e

    @staticmethod
    def _sanitize_name(name):
        """Convert a human name to a safe filename id."""
        return name.strip().lower().replace(" ", "-").replace("/", "-").replace("\\", "-")

    @staticmethod
    def _escape_toml(value):
        """Escape special characters for TOML string values."""
        return str(value).replace("\\", "\\\\").replace('"', '\\"')


if __name__ == "__main__":
    engine = PresetEngine()
    presets = engine.list_presets()
    print(f"Saved presets: {[p['id'] for p in presets]}")
