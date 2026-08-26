import os
import subprocess
import tomllib

class PackageEngine:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.expanduser("~/.config/kaizen")
        self.packages_dir = os.path.join(self.base_dir, "packages")
        self.categories_dir = os.path.join(self.packages_dir, "categories")

    def is_installed(self, pkg_name):
        try:
            res = subprocess.run(f"pacman -Qq '{pkg_name}' 2>/dev/null", shell=True, stdout=subprocess.PIPE)
            return res.returncode == 0
        except Exception:
            return False

    def get_catalog(self):
        catalog = {}
        if not os.path.exists(self.categories_dir):
            return catalog

        for f in os.listdir(self.categories_dir):
            if f.endswith(".toml"):
                cat_path = os.path.join(self.categories_dir, f)
                try:
                    with open(cat_path, "rb") as cf:
                        data = tomllib.load(cf)
                        cat_title = data.get("category", f[:-5])
                        apps = data.get("app", [])
                        
                        # Enrich apps with live installation status
                        for app in apps:
                            app["installed"] = self.is_installed(app.get("pkg", ""))

                        catalog[cat_title] = {
                            "description": data.get("description", ""),
                            "apps": apps
                        }
                except Exception as e:
                    print(f"Error loading category {f}: {e}")
        return catalog

    def install_package(self, pkg_name, source="pacman"):
        if source == "pacman":
            cmd = f"pkexec pacman -S --noconfirm {pkg_name}"
        else: # AUR
            cmd = f"yay -S --noconfirm {pkg_name}"
        
        print(f"📦 Installing {pkg_name} via {source}...")
        res = subprocess.run(cmd, shell=True)
        return res.returncode == 0

    def remove_package(self, pkg_name):
        cmd = f"pkexec pacman -Rns --noconfirm {pkg_name}"
        print(f"🗑️ Removing {pkg_name}...")
        res = subprocess.run(cmd, shell=True)
        return res.returncode == 0

if __name__ == "__main__":
    engine = PackageEngine()
    catalog = engine.get_catalog()
    for cat, data in catalog.items():
        print(f"Category: {cat} ({len(data['apps'])} apps)")
