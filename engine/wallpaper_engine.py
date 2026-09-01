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
        self.base_dir = base_dir or os.path.expanduser("~/.config/kaizen")
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

        # Ensure awww-daemon is running (use setsid to survive app close completely)
        check_cmd = "killall -q hyprpaper swaybg wbg; pgrep -x awww-daemon >/dev/null || (setsid awww-daemon >/dev/null 2>&1 & sleep 0.5)"
        subprocess.run(check_cmd, shell=True)

        # Trigger awww transition
        cmd = f"awww img '{image_path}' --transition-type {transition} --transition-step 90 --transition-fps 60"
        subprocess.run(cmd, shell=True)

        # Save state for restore_state.sh
        state_dir = os.path.join(self.base_dir, "state")
        os.makedirs(state_dir, exist_ok=True)
        with open(os.path.join(state_dir, "current_wallpaper"), "w") as f:
            f.write(os.path.abspath(image_path))

        print(f"🖼️ Wallpaper updated: {os.path.basename(image_path)}")

if __name__ == "__main__":
    engine = WallpaperEngine()
    print("Wallpapers found:", len(engine.list_wallpapers()))
