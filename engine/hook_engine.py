"""Best-effort hooks shared by theme, preset, and package operations."""
import os
import subprocess
import time


class HookRunner:
    """Run Kaizen hooks without allowing hook failures to stop an operation."""

    PHASES = {"pre_apply", "post_apply"}

    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.hooks_dir = os.path.join(base_dir, "hooks")
        self.themes_dir = os.path.join(base_dir, "themes")
        self.log_path = os.path.join(base_dir, "state", "hooks.log")

    def run_apply_phase(self, phase, theme_id, previous_theme_id="", operation="theme_apply", extra=None):
        """Run global then per-theme hooks for one apply phase.

        Returns a result per discovered hook. Failures are recorded and printed,
        but are intentionally never raised to the caller.
        """
        if phase not in self.PHASES:
            raise ValueError(f"Unsupported hook phase: {phase}")

        global_hook = ("global", os.path.join(self.hooks_dir, f"{phase}.sh"))
        theme_hook = ("theme", os.path.join(self.themes_dir, theme_id, "hooks", f"{phase}.sh"))
        hooks = [global_hook, theme_hook] if phase == "pre_apply" and theme_id else [global_hook]
        if phase == "post_apply" and theme_id:
            hooks = [theme_hook, global_hook]

        environment = os.environ.copy()
        for key, value in (extra or {}).items():
            environment[f"KAIZEN_{key.upper()}"] = str(value)
        environment.update({
            "KAIZEN_BASE_DIR": self.base_dir,
            "KAIZEN_THEME_ID": theme_id or "",
            "KAIZEN_PREVIOUS_THEME_ID": previous_theme_id or "",
            "KAIZEN_HOOK_PHASE": phase,
            "KAIZEN_OPERATION": operation,
        })

        results = []
        for scope, hook_path in hooks:
            if not os.path.exists(hook_path):
                continue
            if not os.path.isfile(hook_path):
                self._record(phase, scope, hook_path, "skipped", "not a regular file")
                continue

            executable = os.access(hook_path, os.X_OK)
            command = [hook_path] if executable else ["/bin/bash", hook_path]
            try:
                result = subprocess.run(
                    command, cwd=self.base_dir, env=environment, text=True,
                    capture_output=True, timeout=30,
                )
                status = "ok" if result.returncode == 0 else "failed"
                details = self._details(result.stdout, result.stderr, result.returncode)
                if not executable:
                    details = "hook found but not executable (+x); ran with /bin/bash; " + details
            except subprocess.TimeoutExpired:
                status, details = "failed", "timed out after 30 seconds"
            except OSError as exc:
                status, details = "failed", f"could not run hook: {exc}"

            self._record(phase, scope, hook_path, status, details)
            results.append({"scope": scope, "path": hook_path, "status": status, "details": details})
        return results

    def run_script(self, hook_path, operation, extra=None):
        """Run one declared app hook with the same best-effort logging semantics."""
        environment = os.environ.copy()
        for key, value in (extra or {}).items():
            environment[f"KAIZEN_{key.upper()}"] = str(value)
        environment.update({
            "KAIZEN_BASE_DIR": self.base_dir,
            "KAIZEN_OPERATION": operation,
            "KAIZEN_HOOK_PHASE": operation,
        })
        if not os.path.isfile(hook_path):
            self._record(operation, "app", hook_path, "failed", "hook not found or not a regular file")
            return {"status": "failed", "details": "hook not found or not a regular file"}
        executable = os.access(hook_path, os.X_OK)
        command = [hook_path] if executable else ["/bin/bash", hook_path]
        try:
            result = subprocess.run(command, cwd=self.base_dir, env=environment, text=True, capture_output=True, timeout=30)
            status = "ok" if result.returncode == 0 else "failed"
            details = self._details(result.stdout, result.stderr, result.returncode)
            if not executable:
                details = "hook found but not executable (+x); ran with /bin/bash; " + details
        except subprocess.TimeoutExpired:
            status, details = "failed", "timed out after 30 seconds"
        except OSError as exc:
            status, details = "failed", f"could not run hook: {exc}"
        self._record(operation, "app", hook_path, status, details)
        return {"status": status, "details": details}

    @staticmethod
    def _details(stdout, stderr, returncode):
        output = "\n".join(part.strip() for part in (stdout, stderr) if part and part.strip())
        return f"exit={returncode}" + (f"; {output}" if output else "")

    def _record(self, phase, scope, hook_path, status, details):
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
        line = f"{timestamp} phase={phase} scope={scope} status={status} hook={hook_path} {details}"
        with open(self.log_path, "a", encoding="utf-8") as log_file:
            log_file.write(line + "\n")
        marker = "✅" if status == "ok" else "⚠"
        print(f"  {marker} Hook {scope}/{phase}: {details}")
