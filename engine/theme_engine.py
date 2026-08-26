import os
import sys
import subprocess
import shutil
import tomllib  # Python 3.11+ standard library tomllib

class ThemeEngine:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.expanduser("~/.config/kaizen")
        self.themes_dir = os.path.join(self.base_dir, "themes")
        self.templates_dir = os.path.join(self.base_dir, "templates")
        self.generated_dir = os.path.join(self.base_dir, "generated")
        os.makedirs(self.generated_dir, exist_ok=True)

    def list_themes(self):
        themes = []
        if not os.path.exists(self.themes_dir):
            return themes
        for f in os.listdir(self.themes_dir):
            if f.endswith(".toml"):
                theme_path = os.path.join(self.themes_dir, f)
                try:
                    with open(theme_path, "rb") as tf:
                        data = tomllib.load(tf)
                        meta = data.get("meta", {})
                        colors = data.get("colors", {})
                        themes.append({
                            "id": f[:-5],
                            "name": meta.get("name", f[:-5]),
                            "description": meta.get("description", ""),
                            "colors": colors,
                            "path": theme_path
                        })
                except Exception as e:
                    print(f"Error loading theme {f}: {e}")
        return themes

    def apply_theme(self, theme_id):
        theme_file = os.path.join(self.themes_dir, f"{theme_id}.toml")
        if not os.path.exists(theme_file):
            raise FileNotFoundError(f"Theme '{theme_id}' not found in {self.themes_dir}")

        with open(theme_file, "rb") as tf:
            theme_data = tomllib.load(tf)

        colors = theme_data.get("colors", {})
        
        # Prepare context variables for templating
        context = {}
        for k, v in colors.items():
            context[k] = v
            # Raw hex without '#' for Fuzzel/Hyprland
            context[f"{k}_raw"] = v.lstrip("#")

        # Fallback values
        default_colors = ["bg", "bg_alt", "fg", "fg_alt", "accent", "accent2", "red", "green", "yellow", "blue", "purple", "cyan", "border"]
        for col in default_colors:
            if col not in context:
                context[col] = "#ffffff"
                context[f"{col}_raw"] = "ffffff"

        # Template compilation map (template_subpath -> output_generated_filename)
        render_map = {
            os.path.join("waybar", "style.css.tpl"): "waybar-style.css",
            os.path.join("kitty", "theme.conf.tpl"): "kitty-theme.conf",
            os.path.join("hyprlock", "hyprlock.conf.tpl"): "hyprlock.conf",
            os.path.join("fuzzel", "fuzzel.ini.tpl"): "fuzzel.ini",
            os.path.join("gtk", "gtk3.css.tpl"): "gtk3.css",
            os.path.join("gtk", "gtk4.css.tpl"): "gtk4.css",
            os.path.join("hyprland", "colors.conf.tpl"): "hyprland-colors.lua",
            os.path.join("swaync", "style.css.tpl"): "swaync-style.css",
            os.path.join("btop", "kaizen.theme.tpl"): "btop-kaizen.theme",
            os.path.join("starship", "starship.toml.tpl"): "starship.toml",
            os.path.join("sddm", "theme.conf.tpl"): "sddm-theme.conf",
        }

        for tpl_rel, gen_name in render_map.items():
            tpl_path = os.path.join(self.templates_dir, tpl_rel)
            if os.path.exists(tpl_path):
                with open(tpl_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Replace placeholders {{key}}
                for key, val in context.items():
                    content = content.replace(f"{{{{{key}}}}}", str(val))

                out_path = os.path.join(self.generated_dir, gen_name)
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(content)

        # Apply symlinks to system dotfile locations safely
        self._create_symlinks()

        # Execute reload signals
        self._reload_applications()

        # Update active state file
        state_file = os.path.join(self.base_dir, "config", "kaizen.toml")
        print(f"✅ Theme '{theme_id}' successfully applied!")

    def _create_symlinks(self):
        home = os.path.expanduser("~")
        links = [
            (os.path.join(self.generated_dir, "waybar-style.css"), os.path.join(home, ".config", "waybar", "style.css")),
            (os.path.join(self.generated_dir, "kitty-theme.conf"), os.path.join(home, ".config", "kitty", "theme.conf")),
            (os.path.join(self.generated_dir, "fuzzel.ini"), os.path.join(home, ".config", "fuzzel", "fuzzel.ini")),
            (os.path.join(self.generated_dir, "gtk3.css"), os.path.join(home, ".config", "gtk-3.0", "gtk.css")),
            (os.path.join(self.generated_dir, "gtk4.css"), os.path.join(home, ".config", "gtk-4.0", "gtk.css")),
        ]

        for src, dst in links:
            if os.path.exists(src):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                if os.path.islink(dst) or os.path.exists(dst):
                    try:
                        os.remove(dst)
                    except Exception:
                        pass
                try:
                    os.symlink(src, dst)
                except Exception as e:
                    # Fallback to copy if symlink creation fails
                    shutil.copy2(src, dst)

    def _reload_applications(self):
        cmds = [
            "killall -9 waybar 2>/dev/null; waybar &",
            "hyprctl reload 2>/dev/null",
            "swaync-client -R 2>/dev/null",
            "killall -USR1 kitty 2>/dev/null",
        ]
        for cmd in cmds:
            try:
                subprocess.Popen(cmd, shell=True)
            except Exception:
                pass

if __name__ == "__main__":
    engine = ThemeEngine()
    themes = engine.list_themes()
    print("Available themes:", [t["id"] for t in themes])
    if themes:
        engine.apply_theme(themes[0]["id"])
