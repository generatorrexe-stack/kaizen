import os
import json
import subprocess

class LayoutEngine:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.expanduser("~/.local/share/kaizen")
        self.layouts_dir = os.path.join(self.base_dir, "layouts")
        self.state_dir = os.path.join(self.base_dir, "state")
        os.makedirs(self.state_dir, exist_ok=True)

    def list_layouts(self):
        layouts = []
        if not os.path.exists(self.layouts_dir):
            return layouts
        for f in sorted(os.listdir(self.layouts_dir)):
            if f.endswith(".json"):
                layout_path = os.path.join(self.layouts_dir, f)
                try:
                    with open(layout_path, "r", encoding="utf-8") as lf:
                        data = json.load(lf)
                        layouts.append({
                            "id": f[:-5],
                            "name": data.get("name", f[:-5]),
                            "position": data.get("position", "top"),
                            "orientation": data.get("orientation", "horizontal"),
                            "path": layout_path
                        })
                except Exception as e:
                    print(f"Error loading layout {f}: {e}")
        return layouts

    def get_current_layout(self):
        layout_file = os.path.join(self.state_dir, "current_layout")
        if os.path.exists(layout_file):
            with open(layout_file, "r") as f:
                return f.read().strip()
        return "top"

    def apply_layout(self, layout_id):
        layout_path = os.path.join(self.layouts_dir, f"{layout_id}.json")
        if not os.path.exists(layout_path):
            raise FileNotFoundError(f"Layout '{layout_id}' not found")

        with open(layout_path, "r", encoding="utf-8") as lf:
            layout_data = json.load(lf)

        # 1. Save active layout state
        with open(os.path.join(self.state_dir, "current_layout"), "w") as f:
            f.write(layout_id.rstrip("\n") + "\n")

        # 2. Re-render Waybar templates via ThemeEngine with specialized architecture
        from engine.theme_engine import ThemeEngine
        t_engine = ThemeEngine(self.base_dir)
        current_theme = t_engine.get_current_theme() or "cyberpunk-neon"
        t_engine.apply_theme(current_theme, silent=True)

        orientation = layout_data.get("orientation", "horizontal")
        name = layout_data.get("name", layout_id)
        print(f"✅ Layout '{name}' ({layout_id}, {orientation}) aplicado con éxito a Waybar!")

if __name__ == "__main__":
    engine = LayoutEngine()
    print("Available layouts:", [l["id"] for l in engine.list_layouts()])
