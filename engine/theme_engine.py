"""Kaizen Theme Engine — Core palette parser, template renderer, auto-backup, rollback."""
import os
import re
import sys
import time
import shutil
import subprocess
import tomllib


class ThemeEngine:
    """Loads TOML palettes, renders templates, manages backups and state."""

    # All known color variable names. Templates MUST only use these.
    KNOWN_VARS = {
        "bg", "bg_alt", "fg", "fg_alt", "accent", "accent2",
        "red", "green", "yellow", "blue", "purple", "cyan", "magenta", "border",
        # Raw (no #) variants are auto-generated
    }

    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.expanduser("~/.local/share/kaizen")
        self.themes_dir = os.path.join(self.base_dir, "themes")
        self.templates_dir = os.path.join(self.base_dir, "templates")
        self.generated_dir = os.path.join(self.base_dir, "generated")
        self.state_dir = os.path.join(self.base_dir, "state")
        self.backup_dir = os.path.expanduser("~/.config/kaizen-backups/auto")
        os.makedirs(self.generated_dir, exist_ok=True)
        os.makedirs(self.state_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)

    # ------------------------------------------------------------------
    # Theme listing
    # ------------------------------------------------------------------
    def list_themes(self):
        themes = []
        if not os.path.exists(self.themes_dir):
            return themes
        for f in sorted(os.listdir(self.themes_dir)):
            if f.endswith(".toml"):
                theme_path = os.path.join(self.themes_dir, f)
                try:
                    data = self._load_toml(theme_path)
                    meta = data.get("meta", {})
                    colors = data.get("colors", {})
                    themes.append({
                        "id": f[:-5],
                        "name": meta.get("name", f[:-5]),
                        "description": meta.get("description", ""),
                        "author": meta.get("author", ""),
                        "colors": colors,
                        "path": theme_path,
                    })
                except Exception as e:
                    print(f"⚠ Error loading theme {f}: {e}", file=sys.stderr)
        return themes

    # ------------------------------------------------------------------
    # TOML loading with validation
    # ------------------------------------------------------------------
    def _load_toml(self, path):
        """Load and validate a TOML file. Raises on parse error."""
        with open(path, "rb") as f:
            try:
                return tomllib.load(f)
            except tomllib.TOMLDecodeError as e:
                raise ValueError(f"TOML parse error in {path}: {e}") from e

    # ------------------------------------------------------------------
    # Apply theme — the main entry point
    # ------------------------------------------------------------------
    def apply_theme(self, theme_id, silent=False):
        theme_file = os.path.join(self.themes_dir, f"{theme_id}.toml")
        if not os.path.exists(theme_file):
            avail = [f[:-5] for f in os.listdir(self.themes_dir) if f.endswith(".toml")]
            raise FileNotFoundError(
                f"Theme '{theme_id}' not found.\nAvailable: {', '.join(avail)}"
            )

        # 1. Validate TOML first — fail BEFORE touching anything
        theme_data = self._load_toml(theme_file)
        colors = theme_data.get("colors", {})
        if not colors:
            raise ValueError(f"Theme '{theme_id}' has no [colors] section")

        # 2. Build context
        context = self._build_context(colors)

        # 3. Auto-backup current live configs
        self._auto_backup()

        # 4. Render all templates
        errors = self._render_all_templates(context)
        if errors:
            msg = "Template rendering failed:\n" + "\n".join(errors)
            raise RuntimeError(msg)

        # 5. Create symlinks to live config locations
        self._create_symlinks()

        # 6. Save state
        self._save_state("current_theme", theme_id)
        self._append_history(theme_id)

        # 7. Reload applications
        self._reload_applications()

        if not silent:
            name = theme_data.get("meta", {}).get("name", theme_id)
            print(f"✅ Theme '{name}' ({theme_id}) applied successfully!")

    # ------------------------------------------------------------------
    # Build template context from color dict
    # ------------------------------------------------------------------
    def _build_context(self, colors):
        context = {}
        for k, v in colors.items():
            context[k] = v
            context[f"{k}_raw"] = v.lstrip("#")

        # Ensure all known vars have values (fallback to prevent crashes)
        for var in self.KNOWN_VARS:
            if var not in context:
                context[var] = colors.get("fg", "#ffffff")
                context[f"{var}_raw"] = context[var].lstrip("#")
        return context

    # ------------------------------------------------------------------
    # Render all templates — with strict placeholder validation
    # ------------------------------------------------------------------
    def _render_all_templates(self, context):
        """Render every .tpl file in templates/. Returns list of errors."""
        render_map = {
            "waybar/style.css.tpl": "waybar-style.css",
            "waybar/config.json.tpl": "waybar-config.json",
            "kitty/theme.conf.tpl": "kitty-theme.conf",
            "hyprlock/hyprlock.conf.tpl": "hyprlock.conf",
            "fuzzel/fuzzel.ini.tpl": "fuzzel.ini",
            "gtk/gtk3.css.tpl": "gtk3.css",
            "gtk/gtk4.css.tpl": "gtk4.css",
            "hyprland/colors.conf.tpl": "hyprland-colors.conf",
            "hyprland/kaizen-colors.lua.tpl": "kaizen-colors.lua",
            "swaync/style.css.tpl": "swaync-style.css",
            "btop/kaizen.theme.tpl": "btop-kaizen.theme",
            "starship/starship.toml.tpl": "starship.toml",
            "sddm/theme.conf.tpl": "sddm-theme.conf",
            "sddm/Main.qml.tpl": "sddm-Main.qml",
            "fish/kaizen-prompt.fish.tpl": "kaizen-prompt.fish",
            "cava/config.tpl": "cava-config",
        }

        errors = []
        for tpl_rel, gen_name in render_map.items():
            tpl_path = os.path.join(self.templates_dir, tpl_rel)
            if not os.path.exists(tpl_path):
                continue  # Skip optional templates

            with open(tpl_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Replace all {{key}} placeholders
            for key, val in context.items():
                content = content.replace("{{" + key + "}}", str(val))

            # STRICT VALIDATION: check for any unreplaced {{...}}
            remaining = re.findall(r"\{\{(\w+)\}\}", content)
            if remaining:
                errors.append(
                    f"  {tpl_rel}: unreplaced placeholders: {', '.join(set(remaining))}"
                )
                continue  # Don't write broken output

            out_path = os.path.join(self.generated_dir, gen_name)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(content)

        return errors

    # ------------------------------------------------------------------
    # Auto-backup — save current live configs before overwriting
    # ------------------------------------------------------------------
    def _auto_backup(self):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, timestamp)
        os.makedirs(backup_path, exist_ok=True)

        home = os.path.expanduser("~")
        files_to_backup = [
            (".config/waybar/style.css", "waybar-style.css"),
            (".config/waybar/config", "waybar-config"),
            (".config/kitty/theme.conf", "kitty-theme.conf"),
            (".config/fuzzel/fuzzel.ini", "fuzzel.ini"),
            (".config/hypr/hyprlock.conf", "hyprlock.conf"),
            (".config/gtk-3.0/gtk.css", "gtk3.css"),
            (".config/gtk-4.0/gtk.css", "gtk4.css"),
            (".config/fish/kaizen-prompt.fish", "kaizen-prompt.fish"),
            (".config/cava/config", "cava-config"),
            (".config/hypr/kaizen-colors.conf", "hyprland-colors.conf"),
            (".config/hypr/kaizen-colors.lua", "kaizen-colors.lua"),
            (".config/btop/themes/kaizen.theme", "btop-kaizen.theme"),
            (".config/swaync/style.css", "swaync-style.css"),
            (".config/starship.toml", "starship.toml"),
        ]

        for src_rel, dst_name in files_to_backup:
            src = os.path.join(home, src_rel)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(backup_path, dst_name))

        # Save which theme was active
        current = self._read_state("current_theme")
        if current:
            with open(os.path.join(backup_path, "theme_id"), "w") as f:
                f.write(current)

        # Prune old backups — keep only last 20
        all_backups = sorted(os.listdir(self.backup_dir))
        while len(all_backups) > 20:
            oldest = all_backups.pop(0)
            shutil.rmtree(os.path.join(self.backup_dir, oldest), ignore_errors=True)

    # ------------------------------------------------------------------
    # Rollback — restore from latest auto-backup
    # ------------------------------------------------------------------
    def rollback(self):
        all_backups = sorted(os.listdir(self.backup_dir))
        if not all_backups:
            print("❌ No backups found to rollback to.")
            return False

        latest = os.path.join(self.backup_dir, all_backups[-1])
        home = os.path.expanduser("~")

        restore_map = {
            "waybar-style.css": ".config/waybar/style.css",
            "waybar-config": ".config/waybar/config",
            "kitty-theme.conf": ".config/kitty/theme.conf",
            "fuzzel.ini": ".config/fuzzel/fuzzel.ini",
            "hyprlock.conf": ".config/hypr/hyprlock.conf",
            "gtk3.css": ".config/gtk-3.0/gtk.css",
            "gtk4.css": ".config/gtk-4.0/gtk.css",
            "kaizen-prompt.fish": ".config/fish/kaizen-prompt.fish",
        }

        restored = []
        for backup_name, dst_rel in restore_map.items():
            src = os.path.join(latest, backup_name)
            dst = os.path.join(home, dst_rel)
            if os.path.exists(src):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                restored.append(dst_rel)

        # Restore theme state
        theme_file = os.path.join(latest, "theme_id")
        if os.path.exists(theme_file):
            with open(theme_file, "r") as f:
                old_theme = f.read().strip()
            self._save_state("current_theme", old_theme)

        self._reload_applications()
        print(f"✅ Rolled back to backup {all_backups[-1]}")
        print(f"   Restored: {', '.join(restored)}")
        return True

    # ------------------------------------------------------------------
    # Apply previous theme (from history)
    # ------------------------------------------------------------------
    def apply_previous(self):
        history_file = os.path.join(self.state_dir, "history")
        if not os.path.exists(history_file):
            print("❌ No theme history found.")
            return
        with open(history_file, "r") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        if len(lines) < 2:
            print("❌ Not enough history to go back.")
            return
        previous = lines[-2]
        print(f"↩ Applying previous theme: {previous}")
        self.apply_theme(previous)

    # ------------------------------------------------------------------
    # Symlinks from generated/ to live config locations
    # ------------------------------------------------------------------
    def _create_symlinks(self):
        home = os.path.expanduser("~")
        links = [
            ("waybar-style.css", ".config/waybar/style.css"),
            ("waybar-config.json", ".config/waybar/config"),
            ("kitty-theme.conf", ".config/kitty/theme.conf"),
            ("kitty-theme.conf", ".config/kitty/current-theme.conf"),
            ("fuzzel.ini", ".config/fuzzel/fuzzel.ini"),
            ("hyprlock.conf", ".config/hypr/hyprlock.conf"),
            ("gtk3.css", ".config/gtk-3.0/gtk.css"),
            ("gtk4.css", ".config/gtk-4.0/gtk.css"),
            ("kaizen-prompt.fish", ".config/fish/kaizen-prompt.fish"),
            ("cava-config", ".config/cava/config"),
            ("hyprland-colors.conf", ".config/hypr/kaizen-colors.conf"),
            ("kaizen-colors.lua", ".config/hypr/kaizen-colors.lua"),
            ("btop-kaizen.theme", ".config/btop/themes/kaizen.theme"),
            ("swaync-style.css", ".config/swaync/style.css"),
            ("starship.toml", ".config/starship.toml"),
        ]

        for gen_name, dst_rel in links:
            src = os.path.join(self.generated_dir, gen_name)
            dst = os.path.join(home, dst_rel)
            if os.path.exists(src):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                # Remove existing file/symlink
                if os.path.islink(dst) or os.path.exists(dst):
                    os.remove(dst)
                try:
                    os.symlink(src, dst)
                except OSError:
                    shutil.copy2(src, dst)

        # SDDM requires root — deploy via privileged script
        self._deploy_sddm()

    # ------------------------------------------------------------------
    # Deploy SDDM theme (requires root via pkexec)
    # ------------------------------------------------------------------
    def _deploy_sddm(self):
        """Copy generated SDDM Main.qml to /usr/share/sddm/themes/corners/ via pkexec."""
        gen_qml = os.path.join(self.generated_dir, "sddm-Main.qml")
        gen_conf = os.path.join(self.generated_dir, "sddm-theme.conf")
        script = os.path.join(self.base_dir, "bin", "kaizen-sddm-deploy.sh")

        if not os.path.exists(gen_qml):
            return  # No SDDM template rendered

        # Create the deploy script if it doesn't exist
        if not os.path.exists(script):
            os.makedirs(os.path.dirname(script), exist_ok=True)
            with open(script, "w") as f:
                f.write("#!/bin/bash\n")
                f.write('# Kaizen SDDM Deploy — copies themed QML + components to SDDM theme dir\n')
                f.write('THEME_DIR="/usr/share/sddm/themes/corners"\n')
                f.write('GEN_DIR="$1"\n')
                f.write('TPL_DIR="$2"\n')
                f.write('\n')
                f.write('cp "$GEN_DIR/sddm-Main.qml" "$THEME_DIR/Main.qml" || exit 1\n')
                f.write('if [ -f "$GEN_DIR/sddm-theme.conf" ]; then\n')
                f.write('  cp "$GEN_DIR/sddm-theme.conf" "$THEME_DIR/theme.conf"\n')
                f.write('fi\n')
                f.write('# Copy components\n')
                f.write('if [ -d "$TPL_DIR/sddm/components" ]; then\n')
                f.write('  cp -r "$TPL_DIR/sddm/components/"* "$THEME_DIR/components/"\n')
                f.write('fi\n')
                f.write('echo "SDDM theme deployed successfully."\n')
            os.chmod(script, 0o755)

        tpl_dir = self.templates_dir
        # Only attempt pkexec if a polkit agent is running (GUI auth dialog)
        # Without it, pkexec falls back to terminal auth which blocks
        try:
            agent_check = subprocess.run(
                ["pgrep", "-f", "polkit-.*agent"],
                capture_output=True, timeout=3
            )
            if agent_check.returncode != 0:
                print("  ⚠  SDDM deploy skipped (no polkit agent running — deploy manually with: sudo kaizen-sddm-deploy.sh)")
                return
        except Exception:
            pass

        try:
            result = subprocess.run(
                ["pkexec", script, self.generated_dir, tpl_dir],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                print("  ✅ SDDM theme deployed (via pkexec)")
            else:
                print(f"  ⚠  SDDM deploy skipped (pkexec returned {result.returncode})")
        except FileNotFoundError:
            print("  ⚠  SDDM deploy skipped (pkexec not found)")
        except subprocess.TimeoutExpired:
            print("  ⚠  SDDM deploy skipped (timeout — polkit dialog not answered)")
        except Exception as e:
            print(f"  ⚠  SDDM deploy skipped ({e})")

    # ------------------------------------------------------------------
    # Reload applications after theme change
    # ------------------------------------------------------------------
    def _reload_applications(self):
        cmds = [
            # Waybar: try SIGUSR2 for hot-reload first, fallback to restart
            "killall -SIGUSR2 waybar 2>/dev/null || (killall waybar 2>/dev/null; sleep 0.3; waybar &)",
            "hyprctl reload 2>/dev/null",
            "swaync-client -R 2>/dev/null",
            "killall -USR1 kitty 2>/dev/null",
            "kitty @ set-colors -a -a ~/.config/kitty/theme.conf 2>/dev/null",
            "gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark' 2>/dev/null",
            "gsettings set org.gnome.desktop.interface gtk-theme 'Adwaita-dark' 2>/dev/null",
        ]
        for cmd in cmds:
            try:
                subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # State persistence
    # ------------------------------------------------------------------
    def _save_state(self, key, value):
        path = os.path.join(self.state_dir, key)
        with open(path, "w") as f:
            f.write(value)

    def _read_state(self, key):
        path = os.path.join(self.state_dir, key)
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read().strip()
        return None

    def _append_history(self, theme_id):
        history_file = os.path.join(self.state_dir, "history")
        lines = []
        if os.path.exists(history_file):
            with open(history_file, "r") as f:
                lines = [l.strip() for l in f.readlines() if l.strip()]
        lines.append(theme_id)
        # Keep last 50
        lines = lines[-50:]
        with open(history_file, "w") as f:
            f.write("\n".join(lines) + "\n")

    def get_current_theme(self):
        return self._read_state("current_theme")


if __name__ == "__main__":
    engine = ThemeEngine()
    themes = engine.list_themes()
    print("Available themes:", [t["id"] for t in themes])
