import os
import json
import subprocess
from engine.theme_schema import CURRENT_THEME_SCHEMA_VERSION

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

class MatugenAdapter:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.expanduser("~/.local/share/kaizen")
        self.themes_dir = os.path.join(self.base_dir, "themes")

    def generate_theme_from_image(self, image_path, theme_name=None):
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at {image_path}")

        base_name = os.path.splitext(os.path.basename(image_path))[0]
        if not theme_name:
            theme_name = f"auto-{base_name.lower().replace(' ', '-')}"

        colors = self._extract_colors(image_path)

        theme_content = f"""schema_version = {CURRENT_THEME_SCHEMA_VERSION}

[meta]
name = "Auto: {base_name.title()}"
author = "Kaizen Auto-Matugen"
description = "Auto-generated color palette from wallpaper: {base_name}"

[colors]
bg       = "{colors.get('bg', '#0f141d')}"
bg_alt   = "{colors.get('bg_alt', '#1a202c')}"
fg       = "{colors.get('fg', '#e2e8f0')}"
fg_alt   = "{colors.get('fg_alt', '#94a3b8')}"
accent   = "{colors.get('accent', '#38bdf8')}"
accent2  = "{colors.get('accent2', '#818cf8')}"
red      = "{colors.get('red', '#f87171')}"
green    = "{colors.get('green', '#4ade80')}"
yellow   = "{colors.get('yellow', '#facc15')}"
blue     = "{colors.get('blue', '#60a5fa')}"
purple   = "{colors.get('purple', '#c084fc')}"
cyan     = "{colors.get('cyan', '#22d3ee')}"
border   = "{colors.get('accent', '#38bdf8')}"

[icons]
icon_theme = "Adwaita"

[cursor]
cursor_theme = "Adwaita"
cursor_size = 24

[font]
font_name = "Cantarell 11"

[gtk]
prefer_dark_theme = "1"
"""

        target_file = os.path.join(self.themes_dir, f"{theme_name}.toml")
        with open(target_file, "w", encoding="utf-8") as tf:
            tf.write(theme_content)

        print(f"✨ Auto-generated theme '{theme_name}' saved to {target_file}")
        return theme_name

    def _extract_colors(self, image_path):
        # Try matugen CLI first if installed
        try:
            res = subprocess.run(f"matugen image '{image_path}' --json hex 2>/dev/null", shell=True, stdout=subprocess.PIPE, text=True)
            if res.returncode == 0 and res.stdout.strip():
                m_data = json.loads(res.stdout)
                m_colors = m_data.get("colors", {}).get("dark", {})
                if m_colors:
                    return {
                        "bg": m_colors.get("surface", "#0f141d"),
                        "bg_alt": m_colors.get("surface_container", "#1a202c"),
                        "fg": m_colors.get("on_surface", "#e2e8f0"),
                        "fg_alt": m_colors.get("on_surface_variant", "#94a3b8"),
                        "accent": m_colors.get("primary", "#38bdf8"),
                        "accent2": m_colors.get("secondary", "#818cf8"),
                        "red": m_colors.get("error", "#f87171"),
                        "green": "#4ade80",
                        "yellow": "#facc15",
                        "blue": m_colors.get("tertiary", "#60a5fa"),
                        "purple": "#c084fc",
                        "cyan": "#22d3ee",
                    }
        except Exception:
            pass

        # Fallback color sampling via PIL
        if HAS_PIL:
            try:
                with Image.open(image_path) as img:
                    img = img.resize((50, 50))
                    result = img.convert('P', palette=Image.ADAPTIVE, colors=5)
                    palette = result.getpalette()
                    color_counts = sorted(result.getcolors(), reverse=True)
                    
                    colors_hex = []
                    for count, index in color_counts[:5]:
                        r, g, b = palette[index*3:index*3+3]
                        colors_hex.append(f"#{r:02x}{g:02x}{b:02x}")
                    
                    if len(colors_hex) >= 3:
                        return {
                            "bg": "#0d1117",
                            "bg_alt": colors_hex[0],
                            "fg": "#f0f6fc",
                            "fg_alt": "#8b949e",
                            "accent": colors_hex[1],
                            "accent2": colors_hex[2],
                            "red": "#ff5555",
                            "green": "#50fa7b",
                            "yellow": "#f1fa8c",
                            "blue": colors_hex[1],
                            "purple": colors_hex[2],
                            "cyan": "#8be9fd",
                        }
            except Exception:
                pass

        # Default fallback palette
        return {
            "bg": "#0f141d", "bg_alt": "#1a202c", "fg": "#e2e8f0", "fg_alt": "#94a3b8",
            "accent": "#ff2d95", "accent2": "#00e5ff", "red": "#f87171", "green": "#4ade80",
            "yellow": "#facc15", "blue": "#60a5fa", "purple": "#c084fc", "cyan": "#22d3ee"
        }

if __name__ == "__main__":
    adapter = MatugenAdapter()
    print("Matugen adapter ready.")
