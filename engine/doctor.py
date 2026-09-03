"""Kaizen Doctor — System diagnostics and health checker."""
import os
import shutil
import subprocess
import tomllib
import re
from engine.accessibility import find_low_contrast_pairs
from engine.theme_schema import CURRENT_THEME_SCHEMA_VERSION, migrate_theme_data


def run_doctor(base_dir):
    """Run comprehensive diagnostics on Kaizen installation."""
    print("🏯 Kaizen Doctor — Running diagnostics...\n")
    issues = []
    warnings = []
    ok_count = 0

    # 1. Check system dependencies
    print("━━━ System Dependencies ━━━")
    deps = {
        "waybar": "Waybar status bar",
        "hyprctl": "Hyprland compositor",
        "kitty": "Kitty terminal",
        "fuzzel": "Fuzzel launcher",
        "awww": "awww wallpaper daemon (animated transitions)",
        "matugen": "Matugen color extractor (optional)",
        "pkexec": "Polkit agent (privilege escalation)",
        "magick": "ImageMagick (thumbnail generation)",
    }
    for cmd, desc in deps.items():
        path = shutil.which(cmd)
        if path:
            print(f"  ✅ {cmd}: {path}")
            ok_count += 1
        elif cmd in ("matugen",):
            print(f"  ⚠  {cmd}: not found — {desc}")
            warnings.append(f"{cmd} not installed ({desc})")
        else:
            print(f"  ❌ {cmd}: NOT FOUND — {desc}")
            issues.append(f"{cmd} not installed ({desc})")

    # 2. Check Python dependencies
    print("\n━━━ Python Dependencies ━━━")
    py_deps = [
        ("gi", "PyGObject (GTK4 bindings)", True),
        ("tomllib", "TOML parser", True),
        ("PIL", "Pillow (image processing)", False),
    ]
    for mod, desc, required in py_deps:
        try:
            __import__(mod)
            print(f"  ✅ {mod}: available")
            ok_count += 1
        except ImportError:
            if required:
                print(f"  ❌ {mod}: NOT FOUND — {desc}")
                issues.append(f"Python module {mod} missing ({desc})")
            else:
                print(f"  ⚠  {mod}: not found — {desc} (optional)")
                warnings.append(f"Python module {mod} missing ({desc})")

    # 3. Check GTK4/Adwaita
    try:
        import gi
        gi.require_version('Gtk', '4.0')
        from gi.repository import Gtk
        print(f"  ✅ GTK4: available")
        ok_count += 1
        try:
            gi.require_version('Adw', '1')
            from gi.repository import Adw
            print(f"  ✅ Libadwaita: available")
            ok_count += 1
        except Exception:
            print(f"  ⚠  Libadwaita: not available (GUI will use plain GTK4)")
            warnings.append("Libadwaita not available")
    except Exception:
        print(f"  ❌ GTK4: NOT AVAILABLE")
        issues.append("GTK4 Python bindings not available")

    # 4. Check directory structure
    print("\n━━━ Directory Structure ━━━")
    dirs = [
        "themes", "templates", "generated", "state",
        "layouts", "packages", "wallpapers/library", "wallpapers/thumbnails",
    ]
    for d in dirs:
        full = os.path.join(base_dir, d)
        if os.path.isdir(full):
            print(f"  ✅ {d}/")
            ok_count += 1
        else:
            print(f"  ❌ {d}/ — MISSING")
            issues.append(f"Directory {d}/ missing")

    # 5. Validate all theme TOML files
    print("\n━━━ Theme Validation ━━━")
    themes_dir = os.path.join(base_dir, "themes")
    if os.path.isdir(themes_dir):
        for f in sorted(os.listdir(themes_dir)):
            if f.endswith(".toml"):
                path = os.path.join(themes_dir, f)
                try:
                    with open(path, "rb") as tf:
                        data = tomllib.load(tf)
                    data, schema_notices = migrate_theme_data(data, f)
                    for notice in schema_notices:
                        print(f"  ⚠  {notice}")
                        warnings.append(notice)
                    colors = data.get("colors", {})
                    if not colors:
                        print(f"  ⚠  {f}: no [colors] section")
                        warnings.append(f"Theme {f} has no colors")
                    else:
                        missing = [v for v in ("bg", "fg", "accent") if v not in colors]
                        if missing:
                            print(f"  ⚠  {f}: missing colors: {', '.join(missing)}")
                            warnings.append(f"Theme {f} missing: {', '.join(missing)}")
                        else:
                            try:
                                c_warns = find_low_contrast_pairs(colors)
                                if c_warns:
                                    for w in c_warns:
                                        print(f"  ⚠  {f}: WCAG AA contrast warning — {w}")
                                        warnings.append(f"Theme {f}: low contrast {w}")
                                else:
                                    print(f"  ✅ {f}: valid ({len(colors)} colors, good contrast)")
                                    ok_count += 1
                            except Exception as e:
                                print(f"  ⚠  {f}: error calculating contrast: {e}")
                except Exception as e:
                    print(f"  ❌ {f}: PARSE ERROR — {e}")
                    issues.append(f"Theme {f} has parse error: {e}")

    # 6. Check template placeholders
    print("\n━━━ Template Validation ━━━")
    templates_dir = os.path.join(base_dir, "templates")
    if os.path.isdir(templates_dir):
        for root, _, files in os.walk(templates_dir):
            for f in files:
                if f.endswith(".tpl"):
                    path = os.path.join(root, f)
                    rel = os.path.relpath(path, templates_dir)
                    with open(path, "r", encoding="utf-8") as tf:
                        content = tf.read()
                    placeholders = set(re.findall(r"\{\{(\w+)\}\}", content))
                    known_all = set()
                    for v in ("bg", "bg_alt", "fg", "fg_alt", "accent", "accent2",
                              "red", "green", "yellow", "blue", "purple", "cyan", "magenta", "border", "outer_gap", "wallpaper_path", "sddm_wallpaper_asset"):
                        known_all.add(v)
                        known_all.add(f"{v}_raw")
                    unknown = placeholders - known_all
                    if unknown:
                        print(f"  ⚠  {rel}: unknown placeholders: {', '.join(unknown)}")
                        warnings.append(f"Template {rel} has unknown vars: {', '.join(unknown)}")
                    else:
                        print(f"  ✅ {rel}: {len(placeholders)} placeholders, all valid")
                        ok_count += 1

    # 7. Check symlinks
    print("\n━━━ Symlink Status ━━━")
    home = os.path.expanduser("~")
    gen_dir = os.path.join(base_dir, "generated")
    symlinks = [
        (".config/waybar/style.css", "waybar-style.css"),
        (".config/kitty/theme.conf", "kitty-theme.conf"),
        (".config/fuzzel/fuzzel.ini", "fuzzel.ini"),
    ]
    for dst_rel, gen_name in symlinks:
        dst = os.path.join(home, dst_rel)
        expected_target = os.path.join(gen_dir, gen_name)
        if os.path.islink(dst):
            actual = os.readlink(dst)
            if actual == expected_target:
                print(f"  ✅ {dst_rel} → {gen_name}")
                ok_count += 1
            else:
                print(f"  ⚠  {dst_rel} → {actual} (expected {expected_target})")
                warnings.append(f"Symlink {dst_rel} points to wrong target")
        elif os.path.exists(dst):
            print(f"  ⚠  {dst_rel}: regular file (not managed by Kaizen yet)")
            warnings.append(f"{dst_rel} is a regular file, not a Kaizen symlink")
        else:
            print(f"  ❌ {dst_rel}: does not exist")
            issues.append(f"{dst_rel} missing")

    # 8. Check state
    print("\n━━━ State ━━━")
    current_theme = None
    theme_file = os.path.join(base_dir, "state", "current_theme")
    if os.path.exists(theme_file):
        with open(theme_file, "r") as f:
            current_theme = f.read().strip()
        print(f"  ✅ Active theme: {current_theme}")
        ok_count += 1
    else:
        print(f"  ⚠  No active theme set")
        warnings.append("No active theme in state/current_theme")

    # 9. Validate Presets
    print("\n━━━ Preset Validation ━━━")
    try:
        from engine.preset_engine import PresetEngine
        preset_engine = PresetEngine(base_dir)
        presets = preset_engine.list_presets()
        if presets:
            for p in presets:
                errs, warns = preset_engine.validate_preset(p)
                if not errs and not warns:
                    print(f"  ✅ {p['id']}: valid")
                    ok_count += 1
                else:
                    for e in errs:
                        print(f"  ❌ {p['id']}: {e}")
                        issues.append(f"Preset {p['id']}: {e}")
                    for w in warns:
                        print(f"  ⚠  {p['id']}: {w}")
                        warnings.append(f"Preset {p['id']}: {w}")
        else:
            print("  ℹ  No presets found")
    except Exception as e:
        print(f"  ❌ Failed to validate presets: {e}")
        issues.append(f"Failed to validate presets: {e}")

    # Summary
    print(f"\n{'='*50}")
    print(f"  ✅ {ok_count} checks passed")
    if warnings:
        print(f"  ⚠  {len(warnings)} warnings")
    if issues:
        print(f"  ❌ {len(issues)} issues")
        print(f"\nIssues to fix:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
    else:
        print(f"\n  🎉 Kaizen is healthy!")
    print()
