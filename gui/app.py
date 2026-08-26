import os
import sys

# Ensure parent path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from engine.theme_engine import ThemeEngine
from engine.layout_engine import LayoutEngine
from engine.wallpaper_engine import WallpaperEngine
from engine.package_engine import PackageEngine
from engine.matugen_adapter import MatugenAdapter

import gi
gi.require_version('Gtk', '4.0')
try:
    gi.require_version('Adw', '1')
    from gi.repository import Adw
    HAS_ADW = True
except Exception:
    HAS_ADW = False

from gi.repository import Gtk, Gdk, GLib, Gio

class KaizenWindow(Gtk.ApplicationWindow if not HAS_ADW else Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("Kaizen Hub — Hyprland Customizer")
        self.set_default_size(950, 650)

        self.theme_engine = ThemeEngine(parent_dir)
        self.layout_engine = LayoutEngine(parent_dir)
        self.wallpaper_engine = WallpaperEngine(parent_dir)
        self.package_engine = PackageEngine(parent_dir)
        self.matugen_adapter = MatugenAdapter(parent_dir)

        self._build_ui()

    def _build_ui(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.set_child(main_box)

        # Sidebar StackSwitcher
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        sidebar_box.set_size_request(200, -1)
        sidebar_box.add_css_class("sidebar")
        
        title_label = Gtk.Label(label="🏯 KAIZEN")
        title_label.set_margin_top(15)
        title_label.set_margin_bottom(10)
        title_label.add_css_class("title-1")
        sidebar_box.append(title_label)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)

        stack_switcher = Gtk.StackSidebar()
        stack_switcher.set_stack(self.stack)
        sidebar_box.append(stack_switcher)

        main_box.append(sidebar_box)
        main_box.append(self.stack)

        # Build Tabs
        self._build_themes_tab()
        self._build_wallpapers_tab()
        self._build_layouts_tab()
        self._build_packages_tab()
        self._build_keybinds_tab()

    def _build_themes_tab(self):
        scroll = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_margin_start(20)
        box.set_margin_end(20)
        box.set_margin_top(20)

        header = Gtk.Label(label="🎨 Galería de Temas")
        header.set_halign(Gtk.Align.START)
        header.add_css_class("title-2")
        box.append(header)

        grid = Gtk.FlowBox()
        grid.set_valign(Gtk.Align.START)
        grid.set_max_children_per_line(3)
        grid.set_selection_mode(Gtk.SelectionMode.NONE)

        themes = self.theme_engine.list_themes()
        for t in themes:
            card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            card.set_margin_start(8)
            card.set_margin_end(8)
            card.set_margin_top(8)
            card.set_margin_bottom(8)
            card.set_size_request(220, 140)

            name = Gtk.Label(label=t["name"])
            name.add_css_class("heading")
            card.append(name)

            desc = Gtk.Label(label=t["description"])
            desc.set_wrap(True)
            card.append(desc)

            # Color palette preview swatches
            swatch_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
            swatch_box.set_halign(Gtk.Align.CENTER)
            cols = [t["colors"].get("bg", "#000"), t["colors"].get("accent", "#fff"), t["colors"].get("accent2", "#aaa"), t["colors"].get("green", "#0f0")]
            for c in cols:
                swatch = Gtk.Label(label="   ")
                # Add basic styling hint
                swatch_box.append(swatch)
            card.append(swatch_box)

            apply_btn = Gtk.Button(label="Aplicar Tema")
            apply_btn.connect("clicked", lambda b, tid=t["id"]: self.theme_engine.apply_theme(tid))
            card.append(apply_btn)

            grid.append(card)

        box.append(grid)
        scroll.set_child(box)
        self.stack.add_titled(scroll, "themes", "🎨 Temas")

    def _build_wallpapers_tab(self):
        scroll = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_margin_start(20)
        box.set_margin_end(20)
        box.set_margin_top(20)

        header = Gtk.Label(label="🖼 Biblioteca de Wallpapers")
        header.set_halign(Gtk.Align.START)
        header.add_css_class("title-2")
        box.append(header)

        wallpapers = self.wallpaper_engine.list_wallpapers()
        grid = Gtk.FlowBox()
        grid.set_max_children_per_line(3)
        grid.set_selection_mode(Gtk.SelectionMode.NONE)

        for w in wallpapers:
            card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            card.set_margin_start(8)
            card.set_margin_end(8)
            card.set_margin_top(8)

            lbl = Gtk.Label(label=w["filename"])
            card.append(lbl)

            btn_set = Gtk.Button(label="Establecer Fondo")
            btn_set.connect("clicked", lambda b, wp=w["path"]: self.wallpaper_engine.set_wallpaper(wp))
            card.append(btn_set)

            btn_gen = Gtk.Button(label="Auto-Generar Tema")
            btn_gen.connect("clicked", lambda b, wp=w["path"]: self._generate_and_apply(wp))
            card.append(btn_gen)

            grid.append(card)

        box.append(grid)
        scroll.set_child(box)
        self.stack.add_titled(scroll, "wallpapers", "🖼 Fondos")

    def _generate_and_apply(self, image_path):
        tname = self.matugen_adapter.generate_theme_from_image(image_path)
        self.theme_engine.apply_theme(tname)

    def _build_layouts_tab(self):
        scroll = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_margin_start(20)
        box.set_margin_top(20)

        header = Gtk.Label(label="📐 Posición de Waybar")
        header.set_halign(Gtk.Align.START)
        header.add_css_class("title-2")
        box.append(header)

        layouts = self.layout_engine.list_layouts()
        for l in layouts:
            btn = Gtk.Button(label=f"Aplicar Layout: {l['name']} ({l['position']})")
            btn.connect("clicked", lambda b, lid=l["id"]: self.layout_engine.apply_layout(lid))
            box.append(btn)

        scroll.set_child(box)
        self.stack.add_titled(scroll, "layouts", "📐 Layouts")

    def _build_packages_tab(self):
        scroll = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_margin_start(20)
        box.set_margin_top(20)

        header = Gtk.Label(label="📦 Catálogo de Aplicaciones")
        header.set_halign(Gtk.Align.START)
        header.add_css_class("title-2")
        box.append(header)

        catalog = self.package_engine.get_catalog()
        for cat, data in catalog.items():
            cat_lbl = Gtk.Label(label=f"<b>{cat}</b> - {data['description']}")
            cat_lbl.set_use_markup(True)
            cat_lbl.set_halign(Gtk.Align.START)
            box.append(cat_lbl)

            for app in data["apps"]:
                row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                row.set_margin_start(15)
                
                app_lbl = Gtk.Label(label=f"{app['name']} ({app['pkg']})")
                row.append(app_lbl)

                status_str = "✅ Instalado" if app["installed"] else "Instalar"
                btn = Gtk.Button(label=status_str)
                if not app["installed"]:
                    btn.connect("clicked", lambda b, p=app["pkg"], s=app["source"]: self.package_engine.install_package(p, s))
                row.append(btn)
                box.append(row)

        scroll.set_child(box)
        self.stack.add_titled(scroll, "packages", "📦 Apps Store")

    def _build_keybinds_tab(self):
        scroll = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_margin_start(20)
        box.set_margin_top(20)

        header = Gtk.Label(label="⌨ Atajos de Teclado (Hyprland)")
        header.set_halign(Gtk.Align.START)
        header.add_css_class("title-2")
        box.append(header)

        binds = [
            ("SUPER + Q", "Abrir Terminal (Kitty)"),
            ("SUPER + C", "Cerrar Ventana Activa"),
            ("SUPER + M", "Salir de Hyprland"),
            ("SUPER + E", "Abrir Gestor de Archivos (Thunar/Nautilus)"),
            ("SUPER + V", "Alternar Estado Flotante"),
            ("SUPER + R", "Lanzar Menú de Apps (Fuzzel)"),
            ("SUPER + P", "Conmutar Pseudo-tiling"),
            ("SUPER + J", "Conmutar Split Window"),
            ("SUPER + 1..9", "Cambiar de Workspace (1 al 9)"),
            ("SUPER + SHIFT + 1..9", "Mover Ventana a Workspace"),
        ]

        for keys, action in binds:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
            k_lbl = Gtk.Label(label=f"<b>{keys}</b>")
            k_lbl.set_use_markup(True)
            k_lbl.set_size_request(150, -1)
            a_lbl = Gtk.Label(label=action)
            row.append(k_lbl)
            row.append(a_lbl)
            box.append(row)

        scroll.set_child(box)
        self.stack.add_titled(scroll, "keybinds", "⌨ Atajos")

class KaizenApp(Gtk.Application if not HAS_ADW else Adw.Application):
    def __init__(self):
        super().__init__(application_id="org.kaizen.hub")

    def do_activate(self):
        win = KaizenWindow(self)
        win.present()

def launch_gui():
    app = KaizenApp()
    app.run(sys.argv)

if __name__ == "__main__":
    launch_gui()
