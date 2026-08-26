import os
import json
import subprocess

class LayoutEngine:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.expanduser("~/.config/kaizen")
        self.layouts_dir = os.path.join(self.base_dir, "layouts")
        self.waybar_config = os.path.expanduser("~/.config/waybar/config")

    def list_layouts(self):
        layouts = []
        if not os.path.exists(self.layouts_dir):
            return layouts
        for f in os.listdir(self.layouts_dir):
            if f.endswith(".json"):
                layout_path = os.path.join(self.layouts_dir, f)
                try:
                    with open(layout_path, "r", encoding="utf-8") as lf:
                        data = json.load(lf)
                        layouts.append({
                            "id": f[:-5],
                            "name": data.get("name", f[:-5]),
                            "position": data.get("position", "top"),
                            "path": layout_path
                        })
                except Exception as e:
                    print(f"Error loading layout {f}: {e}")
        return layouts

    def apply_layout(self, layout_id):
        layout_path = os.path.join(self.layouts_dir, f"{layout_id}.json")
        if not os.path.exists(layout_path):
            raise FileNotFoundError(f"Layout '{layout_id}' not found")

        with open(layout_path, "r", encoding="utf-8") as lf:
            layout_data = json.load(lf)

        if not os.path.exists(self.waybar_config):
            print(f"Waybar config not found at {self.waybar_config}")
            return

        with open(self.waybar_config, "r", encoding="utf-8") as wf:
            wb_data = json.load(wf)

        # Update position and margins in main Waybar config
        target = wb_data[0] if isinstance(wb_data, list) else wb_data
        target["position"] = layout_data.get("position", "top")
        if "height" in layout_data:
            target["height"] = layout_data["height"]
        if "width" in layout_data:
            target["width"] = layout_data["width"]
        elif "width" in target:
            del target["width"]

        margin_keys = ["margin-top", "margin-bottom", "margin-left", "margin-right"]
        for mk in margin_keys:
            if mk in layout_data:
                target[mk] = layout_data[mk]

        with open(self.waybar_config, "w", encoding="utf-8") as wf:
            json.dump(wb_data, wf, indent=4)

        # Reload Waybar
        subprocess.Popen("killall -9 waybar 2>/dev/null; waybar &", shell=True)
        print(f"✅ Layout '{layout_id}' applied to Waybar!")

if __name__ == "__main__":
    engine = LayoutEngine()
    print("Available layouts:", [l["id"] for l in engine.list_layouts()])
