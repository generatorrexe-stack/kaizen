import os
import shutil
import subprocess

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

class WallpaperEngine:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.expanduser("~/.local/share/kaizen")
        self.library_dir = os.path.join(self.base_dir, "wallpapers", "library")
        self.thumbnails_dir = os.path.join(self.base_dir, "wallpapers", "thumbnails")
        os.makedirs(self.library_dir, exist_ok=True)
        os.makedirs(self.thumbnails_dir, exist_ok=True)

    def list_wallpapers(self):
        wallpapers = []
        valid_exts = (".jpg", ".jpeg", ".png", ".webp", ".gif")
        if not os.path.exists(self.library_dir):
            return wallpapers

        for f in os.listdir(self.library_dir):
            if f.lower().endswith(valid_exts):
                full_path = os.path.join(self.library_dir, f)
                thumb_path = self.get_or_create_thumbnail(full_path, f)
                wallpapers.append({
                    "filename": f,
                    "path": full_path,
                    "thumbnail": thumb_path
                })
        return wallpapers

    def get_or_create_thumbnail(self, image_path, filename):
        thumb_name = f"thumb_{os.path.splitext(filename)[0]}.png"
        thumb_path = os.path.join(self.thumbnails_dir, thumb_name)
        
        if os.path.exists(thumb_path):
            return thumb_path

        try:
            if HAS_PIL:
                with Image.open(image_path) as img:
                    img.thumbnail((320, 180))
                    img.save(thumb_path, "PNG")
                    return thumb_path
            else:
                # Fallback to ImageMagick convert if PIL is missing
                cmd = f"convert '{image_path}' -resize 320x180 '{thumb_path}' 2>/dev/null"
                subprocess.run(cmd, shell=True, check=False)
                if os.path.exists(thumb_path):
                    return thumb_path
        except Exception as e:
            print(f"Thumbnail generation error for {filename}: {e}")

        return image_path

    def add_wallpaper(self, source_path):
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source file '{source_path}' does not exist")

        filename = os.path.basename(source_path)
        dest_path = os.path.join(self.library_dir, filename)
        shutil.copy2(source_path, dest_path)
        self.get_or_create_thumbnail(dest_path, filename)
        return dest_path

    def set_wallpaper(self, image_path, transition="wipe"):
        if not os.path.exists(image_path):
            # Check if filename only was passed
            rel_path = os.path.join(self.library_dir, image_path)
            if os.path.exists(rel_path):
                image_path = rel_path
            else:
                raise FileNotFoundError(f"Wallpaper not found at '{image_path}'")

        image_path = os.path.abspath(image_path)
        previous_path = self._read_current_wallpaper()
        hyprlock_path = os.path.join(self.base_dir, "generated", "hyprlock.conf")
        previous_hyprlock = None
        if os.path.exists(hyprlock_path):
            with open(hyprlock_path, "rb") as previous_file:
                previous_hyprlock = previous_file.read()

        # Ensure awww-daemon is running (use setsid to survive app close completely)
        check_cmd = "killall -q hyprpaper swaybg wbg; pgrep -x awww-daemon >/dev/null || (setsid awww-daemon >/dev/null 2>&1 & sleep 0.5)"
        subprocess.run(check_cmd, shell=True)

        # Trigger awww transition
        cmd = f"awww img '{image_path}' --transition-type {transition} --transition-step 90 --transition-fps 60"
        subprocess.run(cmd, shell=True)

        self._write_current_wallpaper(image_path)
        try:
            from engine.theme_engine import ThemeEngine
            sync = ThemeEngine(self.base_dir).sync_wallpaper(image_path)
        except Exception as exc:
            rollback_errors = []
            if previous_path:
                self._write_current_wallpaper(previous_path)
                if os.path.isfile(previous_path):
                    result = subprocess.run(["awww", "img", previous_path, "--transition-type", transition,
                                             "--transition-step", "90", "--transition-fps", "60"], check=False)
                    if result.returncode != 0:
                        rollback_errors.append("desktop wallpaper")
                else:
                    rollback_errors.append("previous wallpaper file is missing")
            if previous_hyprlock is not None:
                with open(hyprlock_path, "wb") as rollback_file:
                    rollback_file.write(previous_hyprlock)
                try:
                    ThemeEngine(self.base_dir)._link_generated("hyprlock.conf", ".config/hypr/hyprlock.conf")
                except Exception as rollback_error:
                    rollback_errors.append(f"Hyprlock: {rollback_error}")
            if rollback_errors:
                raise RuntimeError(
                    "Wallpaper synchronization failed and automatic rollback also failed; review Kaizen state/config manually. "
                    f"Rollback failures: {', '.join(rollback_errors)}. Original error: {exc}"
                ) from exc
            raise RuntimeError(
                "Wallpaper changed on the desktop but lockscreen/SDDM synchronization failed; "
                f"state was rolled back. Original error: {exc}"
            ) from exc

        status = "deployed" if sync["sddm_deployed"] else "generated; deploy pending"
        print(f"🖼️ Wallpaper updated: {os.path.basename(image_path)}")
        print(f"  🔒 Hyprlock: {sync['lockscreen_path']}")
        print(f"  🖥️ SDDM: {sync['sddm_path']} ({status})")
        return sync

    def _read_current_wallpaper(self):
        path = os.path.join(self.base_dir, "state", "current_wallpaper")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as state_file:
                return state_file.read().strip()
        return ""

    def _write_current_wallpaper(self, image_path):
        state_dir = os.path.join(self.base_dir, "state")
        os.makedirs(state_dir, exist_ok=True)
        with open(os.path.join(state_dir, "current_wallpaper"), "w", encoding="utf-8") as state_file:
            state_file.write(image_path.rstrip("\n") + "\n")

if __name__ == "__main__":
    engine = WallpaperEngine()
    print("Wallpapers found:", len(engine.list_wallpapers()))
