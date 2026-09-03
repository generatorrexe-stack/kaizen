import os
import subprocess
import tomllib
from engine.hook_engine import HookRunner

class PackageEngine:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.expanduser("~/.local/share/kaizen")
        self.packages_dir = os.path.join(self.base_dir, "packages")
        self.privileged_helper = "/usr/lib/kaizen/kaizen-privileged"
        self.yay_auth_helper = "/usr/lib/kaizen/kaizen-yay-auth"
        self.hook_runner = HookRunner(self.base_dir)

    def _run_hooks(self, phase, operation, package_name):
        theme_id = ""
        theme_state = os.path.join(self.base_dir, "state", "current_theme")
        if os.path.exists(theme_state):
            with open(theme_state, "r", encoding="utf-8") as state_file:
                theme_id = state_file.read().strip()
        return self.hook_runner.run_apply_phase(
            phase, theme_id, theme_id, operation, {"package_name": package_name},
        )

    def is_installed(self, pkg_name):
        try:
            res = subprocess.run(["pacman", "-Qq", pkg_name], capture_output=True)
            return res.returncode == 0
        except Exception:
            return False

    def get_catalog(self):
        catalog = {}
        for f in sorted(os.listdir(self.packages_dir)):
            if not f.endswith(".toml") or f == "catalog.toml":
                continue
            with open(os.path.join(self.packages_dir, f), "rb") as cf:
                data = tomllib.load(cf)
            apps = []
            for app in data.get("apps", []):
                app = dict(app)
                app["installed"] = self.is_installed(app["package"])
                apps.append(app)
            catalog[f[:-5]] = {**data["category"], "apps": apps}
        return catalog

    def get_app(self, app_id):
        for category in self.get_catalog().values():
            for app in category["apps"]:
                if app["id"] == app_id:
                    return app
        raise KeyError(f"Unknown catalog app: {app_id}")

    @staticmethod
    def _emit(progress, stage, detail=""):
        if progress:
            progress(stage, detail)

    def resolve_dependencies(self, app):
        return [p for p in dict.fromkeys([app["package"], *app.get("depends", [])]) if not self.is_installed(p)]

    def _run_declared_hook(self, app, field, operation):
        hook = app.get(field)
        if not hook:
            return True
        path = os.path.realpath(os.path.join(self.base_dir, hook))
        root = os.path.realpath(os.path.join(self.base_dir, "hooks"))
        if not path.startswith(root + os.sep):
            return False
        return self.hook_runner.run_script(path, operation, {"app_id": app["id"], "package_name": app["package"]})["status"] == "ok"

    def install_app(self, app_id, progress=None):
        app = self.get_app(app_id)
        self._emit(progress, "resolving", "Resolving dependencies")
        packages = self.resolve_dependencies(app)
        if packages:
            command = (["yay", "--sudo", self.yay_auth_helper, "-S", "--needed", "--noconfirm", *packages]
                       if app.get("aur") else
                       ["pkexec", "--disable-internal-agent", "--action-id", "io.github.kaizen.package.install", self.privileged_helper, "package-install", *packages])
            self._emit(progress, "downloading", ", ".join(packages))
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in process.stdout:
                self._emit(progress, "downloading" if "download" in line.lower() else "installing", line.rstrip())
            if process.wait() != 0:
                self._emit(progress, "failed", "Package transaction failed; configuration was skipped")
                return False
        self._emit(progress, "configuring", "Running post-install configuration")
        if app.get("requires_service"):
            command = ["pkexec", "--disable-internal-agent", "--action-id", "io.github.kaizen.package.configure", self.privileged_helper, "service-enable-now", app["requires_service"]]
            if subprocess.run(command).returncode != 0:
                self._emit(progress, "failed", f"Could not enable {app['requires_service']}")
                return False
        if not self._run_declared_hook(app, "post_install_hook", "post_install"):
            self._emit(progress, "failed", "Post-install hook failed")
            return False
        self._emit(progress, "ready", f"{app['name']} is ready")
        return True

    def install_package(self, pkg_name, source="pacman"):
        if source == "pacman":
            cmd = ["pkexec", "--disable-internal-agent", "--action-id",
                   "io.github.kaizen.package.install", self.privileged_helper,
                   "package-install", pkg_name]
        else: # AUR builds remain unprivileged; yay delegates only pacman to Polkit.
            cmd = ["yay", "--sudo", self.yay_auth_helper, "-S", "--noconfirm", pkg_name]
        
        print(f"📦 Installing {pkg_name} via {source}...")
        self._run_hooks("pre_apply", "package_install", pkg_name)
        try:
            res = subprocess.run(cmd)
        finally:
            self._run_hooks("post_apply", "package_install", pkg_name)
        return res.returncode == 0

    def remove_package(self, pkg_name, source="pacman"):
        if source == "aur":
            cmd = ["yay", "--sudo", self.yay_auth_helper, "-Rns", "--noconfirm", pkg_name]
        else:
            cmd = ["pkexec", "--disable-internal-agent", "--action-id",
                   "io.github.kaizen.package.remove", self.privileged_helper,
                   "package-remove", pkg_name]
        print(f"🗑️ Removing {pkg_name}...")
        self._run_hooks("pre_apply", "package_remove", pkg_name)
        try:
            res = subprocess.run(cmd)
        finally:
            self._run_hooks("post_apply", "package_remove", pkg_name)
        return res.returncode == 0

if __name__ == "__main__":
    engine = PackageEngine()
    catalog = engine.get_catalog()
    for cat, data in catalog.items():
        print(f"Category: {cat} ({len(data['apps'])} apps)")
