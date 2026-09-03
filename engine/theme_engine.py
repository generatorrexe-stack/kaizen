"""Kaizen Theme Engine — Core palette parser, template renderer, auto-backup, rollback."""
import os
import re
import sys
import json
import time
import shutil
import subprocess
import tomllib
from engine.hook_engine import HookRunner
from engine.theme_schema import migrate_theme_data


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
        self.hook_runner = HookRunner(self.base_dir)
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
        for root, _, files in os.walk(self.themes_dir):
            for f in sorted(files):
                if f.endswith(".toml"):
                    theme_path = os.path.join(root, f)
                    try:
                        data = self._load_toml(theme_path)
                        meta = data.get("meta", {})
                        colors = data.get("colors", {})
                        cat = meta.get("category")
                        if not cat:
                            rel_dir = os.path.relpath(root, self.themes_dir)
                            cat = rel_dir if rel_dir != "." else "Otros"
                        themes.append({
                            "id": f[:-5],
                            "name": meta.get("name", f[:-5]),
                            "description": meta.get("description", ""),
                            "author": meta.get("author", ""),
                            "category": cat,
                            "colors": colors,
                            "path": theme_path,
                        })
                    except Exception as e:
                        print(f"⚠ Error loading theme {f}: {e}", file=sys.stderr)
        return themes

    # ------------------------------------------------------------------
    # Layout inspection
    # ------------------------------------------------------------------
    def get_current_layout(self):
        return self._read_state("current_layout") or "top"

    def get_layout_info(self, layout_id):
        layouts_dir = os.path.join(self.base_dir, "layouts")
        layout_file = os.path.join(layouts_dir, f"{layout_id}.json")
        if os.path.exists(layout_file):
            try:
                with open(layout_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("orientation", "horizontal"), data
            except Exception:
                pass
        if layout_id in ("left", "right"):
            return "vertical", {"position": layout_id, "width": 48}
        return "horizontal", {"position": layout_id, "height": 36}

    # ------------------------------------------------------------------
    # TOML loading with validation
    # ------------------------------------------------------------------
    def _load_toml(self, path):
        """Load and migrate a TOML theme. Raises on parse/schema errors."""
        with open(path, "rb") as f:
            try:
                data = tomllib.load(f)
            except tomllib.TOMLDecodeError as e:
                raise ValueError(f"TOML parse error in {path}: {e}") from e
        data, notices = migrate_theme_data(data, path)
        for notice in notices:
            print(f"⚠ {notice}", file=sys.stderr)
        return data

    # ------------------------------------------------------------------
    # Apply theme — the main entry point
    # ------------------------------------------------------------------
    def apply_theme(self, theme_id, silent=False, dry_run=False, hook_context=None):
        """Render a theme and optionally apply it to the running desktop.

        A dry run writes its output under ``generated/preview/<theme-id>/``.  It
        deliberately does not overwrite the live generated files, because those
        can already be the targets of Kaizen-managed symlinks.
        """
        theme_file = os.path.join(self.themes_dir, f"{theme_id}.toml")
        if not os.path.exists(theme_file):
            found = None
            for root, _, files in os.walk(self.themes_dir):
                if f"{theme_id}.toml" in files:
                    found = os.path.join(root, f"{theme_id}.toml")
                    break
            if found:
                theme_file = found
            else:
                avail = [t["id"] for t in self.list_themes()]
                raise FileNotFoundError(
                    f"Theme '{theme_id}' not found.\nAvailable: {', '.join(avail)}"
                )

        # 1. Validate TOML first — fail BEFORE touching anything
        theme_data = self._load_toml(theme_file)
        colors = theme_data.get("colors", {})
        if not colors:
            raise ValueError(f"Theme '{theme_id}' has no [colors] section")

        icons = theme_data.get("icons", {})
        cursor = theme_data.get("cursor", {})
        font = theme_data.get("font", {})
        gtk = theme_data.get("gtk", {})

        # 2. Build context
        context = self._build_context(colors, icons, cursor, font, gtk)

        # 3. Render all templates.  Preview output is isolated from the live
        # generated files, so an existing symlink cannot make a dry run visible.
        output_dir = self.generated_dir
        if dry_run:
            output_dir = os.path.join(self.generated_dir, "preview", theme_id)

        if dry_run:
            errors, rendered_files = self._render_all_templates(context, output_dir)
            if errors:
                msg = "Template rendering failed:\n" + "\n".join(errors)
                raise RuntimeError(msg)
            result = {
                "theme_id": theme_id,
                "name": theme_data.get("meta", {}).get("name", theme_id),
                "context": context,
                "output_dir": output_dir,
                "rendered_files": rendered_files,
            }
            if not silent:
                print(f"🔎 Preview for '{result['name']}' rendered to {output_dir}")
                print("   No symlinks, backup, state changes, or application reloads were made.")
            return result

        previous_theme_id = self.get_current_theme() or ""
        hook_context = dict(hook_context or {})
        operation = hook_context.pop("operation", "theme_apply")
        self.hook_runner.run_apply_phase(
            "pre_apply", theme_id, previous_theme_id, operation, hook_context,
        )
        try:
            # Preserve live configuration before writing the normal generated output:
            # those files may be the targets of existing managed symlinks.
            self._auto_backup()
            errors, _ = self._render_all_templates(context, output_dir)
            if errors:
                msg = "Template rendering failed:\n" + "\n".join(errors)
                raise RuntimeError(msg)

            # 4. Create symlinks to live config locations
            self._create_symlinks()

            # 6. Save state
            self._save_state("current_theme", theme_id)
            self._append_history(theme_id)

            # 7. Reload applications
            self._reload_applications(context)
        finally:
            self.hook_runner.run_apply_phase(
                "post_apply", theme_id, previous_theme_id, operation, hook_context,
            )

        if not silent:
            name = theme_data.get("meta", {}).get("name", theme_id)
            print(f"✅ Theme '{name}' ({theme_id}) applied successfully!")

    def preview_theme(self, theme_id):
        """Render and return a non-invasive preview for a theme."""
        return self.apply_theme(theme_id, silent=True, dry_run=True)

    # ------------------------------------------------------------------
    # Build template context from color dict
    # ------------------------------------------------------------------
    def _build_context(self, colors, icons=None, cursor=None, font=None, gtk=None):
        icons = icons or {}
        cursor = cursor or {}
        font = font or {}
        gtk = gtk or {}
        
        context = {}
        for k, v in colors.items():
            context[k] = v
            context[f"{k}_raw"] = v.lstrip("#")

        # Ensure all known vars have values (fallback to prevent crashes)
        for var in self.KNOWN_VARS:
            if var not in context:
                context[var] = colors.get("fg", "#ffffff")
                context[f"{var}_raw"] = context[var].lstrip("#")
                
        context["icon_theme"] = icons.get("icon_theme", "Adwaita")
        context["cursor_theme"] = cursor.get("cursor_theme", "Adwaita")
        context["cursor_size"] = cursor.get("cursor_size", 24)
        context["font_name"] = font.get("font_name", "Cantarell 11")
        context["wallpaper_path"] = self._read_state("current_wallpaper") or ""
        context["sddm_wallpaper_asset"] = "kaizen-wallpaper"
        
        raw_prefer_dark = gtk.get("prefer_dark_theme", "1")
        if isinstance(raw_prefer_dark, bool):
            context["prefer_dark_theme"] = "1" if raw_prefer_dark else "0"
        elif str(raw_prefer_dark).lower() in ("0", "false", "no"):
            context["prefer_dark_theme"] = "0"
        else:
            context["prefer_dark_theme"] = "1"

        # Explicit user theme takes priority. Only fallback to Adwaita / Adwaita-dark if not defined.
        user_gtk_theme = gtk.get("gtk_theme") or gtk.get("theme") or gtk.get("name")
        if user_gtk_theme:
            context["gtk_theme"] = user_gtk_theme
        else:
            context["gtk_theme"] = "Adwaita-dark" if context["prefer_dark_theme"] == "1" else "Adwaita"
        
        return context

    def sync_wallpaper(self, desktop_path, lockscreen_path=None, sddm_path=None, deploy=True):
        """Render lockscreen/SDDM wallpaper artifacts for the active theme.

        The SDDM image is copied into generated/ first; deploy remains restricted
        to the existing Polkit route in ``_deploy_sddm``.
        """
        theme_id = self.get_current_theme()
        if not theme_id:
            raise RuntimeError("Cannot sync wallpaper: no active theme")
        theme_path = os.path.join(self.themes_dir, f"{theme_id}.toml")
        theme = self._load_toml(theme_path)
        wallpaper = theme.get("wallpaper", {})
        lockscreen_path = lockscreen_path or wallpaper.get("lockscreen_path") or desktop_path
        sddm_path = sddm_path or wallpaper.get("sddm_path") or desktop_path
        for label, path in (("lockscreen", lockscreen_path), ("SDDM", sddm_path)):
            if not os.path.isfile(path):
                raise FileNotFoundError(f"{label} wallpaper not found: {path}")

        context = self._build_context(
            theme.get("colors", {}), theme.get("icons", {}), theme.get("cursor", {}),
            theme.get("font", {}), theme.get("gtk", {}),
        )
        context["wallpaper_path"] = os.path.abspath(lockscreen_path)
        suffix = os.path.splitext(sddm_path)[1].lower() or ".img"
        asset_name = f"kaizen-wallpaper{suffix}"
        context["sddm_wallpaper_asset"] = asset_name
        asset_path = os.path.join(self.generated_dir, asset_name)
        shutil.copy2(sddm_path, asset_path)
        errors, _ = self._render_all_templates(context, self.generated_dir)
        if errors:
            raise RuntimeError("Wallpaper template rendering failed:\n" + "\n".join(errors))
        self._link_generated("hyprlock.conf", ".config/hypr/hyprlock.conf")
        deployed = self._deploy_sddm() if deploy else None
        if deploy and not deployed:
            raise RuntimeError("SDDM deploy failed after Hyprlock was updated")
        return {"lockscreen_path": context["wallpaper_path"], "sddm_path": sddm_path,
                "sddm_asset": asset_path, "sddm_deployed": deployed}

    # ------------------------------------------------------------------
    # Render all templates — with strict placeholder validation
    # ------------------------------------------------------------------
    def _render_all_templates(self, context, output_dir=None):
        """Render every template file and return ``(errors, rendered_paths)``."""
        output_dir = output_dir or self.generated_dir
        os.makedirs(output_dir, exist_ok=True)
        current_layout = self.get_current_layout()
        orientation, layout_data = self.get_layout_info(current_layout)
        outer_gap = int(layout_data.get("outer_gap", 8))
        context = {**context, "outer_gap": outer_gap}

        # Select specialized Waybar templates based on layout orientation
        if orientation == "vertical":
            waybar_tpl = "waybar/config-vertical.json.tpl"
            waybar_style_tpl = "waybar/style-vertical.css.tpl"
        else:
            waybar_tpl = "waybar/config-horizontal.json.tpl"
            waybar_style_tpl = "waybar/style-horizontal.css.tpl"

        # Fallback to default templates if specific orientation ones are missing
        if not os.path.exists(os.path.join(self.templates_dir, waybar_tpl)):
            waybar_tpl = "waybar/config.json.tpl"
        if not os.path.exists(os.path.join(self.templates_dir, waybar_style_tpl)):
            waybar_style_tpl = "waybar/style.css.tpl"

        render_map = {
            waybar_style_tpl: "waybar-style.css",
            waybar_tpl: "waybar-config.json",
            "kitty/theme.conf.tpl": "kitty-theme.conf",
            "hyprlock/hyprlock.conf.tpl": "hyprlock.conf",
            "fuzzel/fuzzel.ini.tpl": "fuzzel.ini",
            "gtk/gtk3.css.tpl": "gtk3.css",
            "gtk/gtk4.css.tpl": "gtk4.css",
            "gtk/gtk3-settings.ini.tpl": "gtk3-settings.ini",
            "gtk/gtk4-settings.ini.tpl": "gtk4-settings.ini",
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
        rendered_files = []
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

            # Apply geometry and margin overrides for Waybar config
            if gen_name == "waybar-config.json" and layout_data:
                try:
                    wb_data = json.loads(content)
                    target = wb_data[0] if isinstance(wb_data, list) else wb_data
                    if "position" in layout_data:
                        target["position"] = layout_data["position"]
                    if "height" in layout_data:
                        target["height"] = layout_data["height"]
                    elif "height" in target and orientation == "vertical":
                        del target["height"]

                    if "width" in layout_data:
                        target["width"] = layout_data["width"]
                    elif "width" in target and orientation == "horizontal":
                        del target["width"]

                    # A single layout-owned outer gap governs Hyprland and every
                    # Waybar edge, eliminating the former 10px/8px mismatch.
                    for mk in ["margin-top", "margin-bottom", "margin-left", "margin-right"]:
                        target[mk] = outer_gap
                    content = json.dumps(wb_data, indent=4)
                except Exception as e:
                    print(f"Warning: could not adjust waybar geometry: {e}", file=sys.stderr)

            out_path = os.path.join(output_dir, gen_name)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(content)
            rendered_files.append(out_path)

        return errors, rendered_files

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
            (".config/gtk-3.0/settings.ini", "gtk3-settings.ini"),
            (".config/gtk-4.0/settings.ini", "gtk4-settings.ini"),
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

        # Save which theme and layout were active
        current_theme = self._read_state("current_theme")
        if current_theme:
            with open(os.path.join(backup_path, "theme_id"), "w") as f:
                f.write(current_theme)

        current_layout = self._read_state("current_layout")
        if current_layout:
            with open(os.path.join(backup_path, "layout_id"), "w") as f:
                f.write(current_layout)

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
            "gtk3-settings.ini": ".config/gtk-3.0/settings.ini",
            "gtk4-settings.ini": ".config/gtk-4.0/settings.ini",
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

        # Restore theme and layout state
        theme_file = os.path.join(latest, "theme_id")
        if os.path.exists(theme_file):
            with open(theme_file, "r") as f:
                old_theme = f.read().strip()
            self._save_state("current_theme", old_theme)

        layout_file = os.path.join(latest, "layout_id")
        if os.path.exists(layout_file):
            with open(layout_file, "r") as f:
                old_layout = f.read().strip()
            self._save_state("current_layout", old_layout)

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
            ("gtk3-settings.ini", ".config/gtk-3.0/settings.ini"),
            ("gtk4-settings.ini", ".config/gtk-4.0/settings.ini"),
            ("kaizen-prompt.fish", ".config/fish/kaizen-prompt.fish"),
            ("cava-config", ".config/cava/config"),
            ("hyprland-colors.conf", ".config/hypr/kaizen-colors.conf"),
            ("kaizen-colors.lua", ".config/hypr/kaizen-colors.lua"),
            ("btop-kaizen.theme", ".config/btop/themes/kaizen.theme"),
            ("swaync-style.css", ".config/swaync/style.css"),
            ("starship.toml", ".config/starship.toml"),
        ]

        for gen_name, dst_rel in links:
            self._link_generated(gen_name, dst_rel)

        # SDDM requires root — deploy via privileged script
        self._deploy_sddm()

    def _link_generated(self, gen_name, dst_rel):
        src = os.path.join(self.generated_dir, gen_name)
        dst = os.path.join(os.path.expanduser("~"), dst_rel)
        if os.path.exists(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if os.path.islink(dst) or os.path.exists(dst):
                os.remove(dst)
            try:
                os.symlink(src, dst)
            except OSError:
                shutil.copy2(src, dst)

    # ------------------------------------------------------------------
    # Deploy SDDM theme through its dedicated Polkit action
    # ------------------------------------------------------------------
    def _deploy_sddm(self):
        """Copy generated SDDM files through Kaizen's scoped Polkit helper."""
        gen_qml = os.path.join(self.generated_dir, "sddm-Main.qml")
        gen_conf = os.path.join(self.generated_dir, "sddm-theme.conf")

        if not os.path.exists(gen_qml):
            return False

        helper = "/usr/lib/kaizen/kaizen-privileged"
        if not os.path.exists(helper):
            print("  ⚠ SDDM deploy skipped: install Kaizen's Polkit helper first")
            return False

        tpl_dir = self.templates_dir
        try:
            agent_check = subprocess.run(
                ["pgrep", "-f", "polkit-.*agent"],
                capture_output=True, timeout=3
            )
            if agent_check.returncode != 0:
                print("  ⚠ SDDM deploy skipped: no Polkit authentication agent")
                return False
        except Exception:
            pass

        try:
            result = subprocess.run(
                ["pkexec", "--disable-internal-agent", "--action-id",
                 "io.github.kaizen.sddm.deploy", helper, "sddm-deploy",
                 self.generated_dir, tpl_dir],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                print("  ✅ SDDM theme deployed (via Kaizen Polkit action)")
                return True
            print(f"  ⚠ SDDM deploy failed: {result.stderr.strip() or result.stdout.strip()}")
        except Exception as exc:
            print(f"  ⚠ SDDM deploy failed: {exc}")
        return False

    # ------------------------------------------------------------------
    # Reload applications after theme change
    # ------------------------------------------------------------------
    def _reload_applications(self, context=None):
        context = context or {}
        icon_theme = context.get("icon_theme", "Adwaita")
        cursor_theme = context.get("cursor_theme", "Adwaita")
        font_name = context.get("font_name", "Cantarell 11")
        prefer_dark = context.get("prefer_dark_theme", "1")
        gtk_theme_val = context.get("gtk_theme", "Adwaita-dark")

        cmds = [
            # Waybar: try SIGUSR2 for hot-reload first, fallback to restart
            "killall -SIGUSR2 waybar 2>/dev/null || (killall waybar 2>/dev/null; sleep 0.3; waybar &)",
            "hyprctl reload 2>/dev/null",
            "swaync-client -R 2>/dev/null",
            "killall -USR1 kitty 2>/dev/null",
            "kitty @ set-colors -a -a ~/.config/kitty/theme.conf 2>/dev/null",
            f"gsettings set org.gnome.desktop.interface color-scheme \"{'prefer-dark' if str(prefer_dark) == '1' else 'default'}\" 2>/dev/null",
            f"gsettings set org.gnome.desktop.interface gtk-theme '{gtk_theme_val}' 2>/dev/null",
            f"gsettings set org.gnome.desktop.interface icon-theme '{icon_theme}' 2>/dev/null",
            f"gsettings set org.gnome.desktop.interface cursor-theme '{cursor_theme}' 2>/dev/null",
            f"gsettings set org.gnome.desktop.interface font-name '{font_name}' 2>/dev/null",
            "command -v thunar >/dev/null 2>&1 && if hyprctl clients -j 2>/dev/null | grep -q '\"class\": \"thunar\"'; then killall -q thunar; thunar >/dev/null 2>&1 & else killall -q thunar; thunar --daemon >/dev/null 2>&1 & fi",
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
            f.write(value.rstrip("\n") + "\n")

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
    print("Current layout:", engine.get_current_layout())
