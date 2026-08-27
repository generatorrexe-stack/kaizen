import os
import sys
import threading

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


class KaizenWindow(Adw.ApplicationWindow if HAS_ADW else Gtk.ApplicationWindow):
    def __init__(self, app, base_dir):
        super().__init__(application=app)
        self.set_title("Kaizen Hub — Hyprland Customizer")
        self.set_default_size(980, 680)

        self.base_dir = base_dir
        self.theme_engine = ThemeEngine(base_dir)
        self.layout_engine = LayoutEngine(base_dir)
        self.wallpaper_engine = WallpaperEngine(base_dir)
        self.package_engine = PackageEngine(base_dir)
        self.matugen_adapter = MatugenAdapter(base_dir)

        self._load_css()
        self._build_ui()

    def _load_css(self):
        """Load custom CSS for the application."""
        css = b"""
        .sidebar {
            background-color: rgba(10, 14, 30, 0.95);
            border-right: 1px solid rgba(122, 162, 247, 0.3);
        }
        .sidebar-title {
            font-size: 22px;
            font-weight: 800;
            letter-spacing: 4px;
        }
        .theme-card {
            background: rgba(18, 24, 46, 0.85);
            border: 1px solid rgba(122, 162, 247, 0.25);
            border-radius: 12px;
            padding: 16px;
            transition: all 200ms ease;
        }
        .theme-card:hover {
            border-color: rgba(122, 162, 247, 0.6);
            background: rgba(24, 30, 52, 0.95);
        }
        .theme-card-active {
            border-color: rgba(0, 229, 255, 0.8);
            box-shadow: 0 0 12px rgba(0, 229, 255, 0.2);
        }
        .theme-name {
            font-size: 15px;
            font-weight: 700;
        }
        .theme-desc {
            font-size: 12px;
            opacity: 0.7;
        }
        .color-swatch {
            min-width: 24px;
            min-height: 24px;
            border-radius: 6px;
            border: 1px solid rgba(255, 255, 255, 0.15);
        }
        .apply-btn {
            background: rgba(122, 162, 247, 0.2);
            color: #7aa2f7;
            border: 1px solid rgba(122, 162, 247, 0.4);
            border-radius: 8px;
            padding: 6px 16px;
            font-weight: 600;
        }
        .apply-btn:hover {
            background: rgba(122, 162, 247, 0.35);
        }
        .apply-btn-active {
            background: rgba(0, 229, 255, 0.2);
            color: #00e5ff;
            border-color: rgba(0, 229, 255, 0.5);
        }
        .rollback-btn {
            background: rgba(247, 118, 142, 0.15);
            color: #f7768e;
            border: 1px solid rgba(247, 118, 142, 0.35);
            border-radius: 8px;
        }
        .section-header {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        .status-badge {
            font-size: 11px;
            padding: 2px 10px;
            border-radius: 12px;
            font-weight: 600;
        }
        .badge-installed {
            background: rgba(0, 255, 159, 0.15);
            color: #00ff9f;
        }
        .badge-missing {
            background: rgba(247, 118, 142, 0.15);
            color: #f7768e;
        }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _build_ui(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

        if HAS_ADW:
            # Use Adw.ToolbarView for proper Adw window
            toolbar = Adw.ToolbarView()
            header = Adw.HeaderBar()
            header.set_title_widget(Gtk.Label(label=""))  # Title in sidebar
            toolbar.add_top_bar(header)
            toolbar.set_content(main_box)
            self.set_content(toolbar)
        else:
            self.set_child(main_box)

        # === SIDEBAR ===
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        sidebar_box.set_size_request(210, -1)
        sidebar_box.add_css_class("sidebar")

        # Title
        title_label = Gtk.Label(label="🏯 KAIZEN")
        title_label.set_margin_top(20)
        title_label.set_margin_bottom(15)
        title_label.add_css_class("sidebar-title")
        sidebar_box.append(title_label)

        # Current theme indicator
        current = self.theme_engine.get_current_theme() or "none"
        self.current_label = Gtk.Label(label=f"▸ {current}")
        self.current_label.set_margin_bottom(15)
        self.current_label.set_opacity(0.6)
        sidebar_box.append(self.current_label)

        # Stack + StackSidebar
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(200)
        self.stack.set_hexpand(True)
        self.stack.set_vexpand(True)

        stack_sidebar = Gtk.StackSidebar()
        stack_sidebar.set_stack(self.stack)
        stack_sidebar.set_vexpand(True)
        sidebar_box.append(stack_sidebar)

        # Rollback button at bottom of sidebar
        rollback_btn = Gtk.Button(label="↩ Rollback")
        rollback_btn.add_css_class("rollback-btn")
        rollback_btn.set_margin_start(12)
        rollback_btn.set_margin_end(12)
        rollback_btn.set_margin_bottom(12)
        rollback_btn.connect("clicked", self._on_rollback)
        sidebar_box.append(rollback_btn)

        main_box.append(sidebar_box)
        main_box.append(self.stack)

        # Build tabs
        self._build_themes_tab()
        self._build_wallpapers_tab()
        self._build_layouts_tab()
        self._build_packages_tab()
        self._build_keybinds_tab()

    # ================================================================
    # THEMES TAB
    # ================================================================
    def _build_themes_tab(self):
        scroll = Gtk.ScrolledWindow()
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_margin_start(25)
        box.set_margin_end(25)
        box.set_margin_top(25)

        header = Gtk.Label(label="🎨 Galería de Temas")
        header.set_halign(Gtk.Align.START)
        header.add_css_class("section-header")
        box.append(header)

        grid = Gtk.FlowBox()
        grid.set_valign(Gtk.Align.START)
        grid.set_max_children_per_line(3)
        grid.set_min_children_per_line(2)
        grid.set_selection_mode(Gtk.SelectionMode.NONE)
        grid.set_homogeneous(True)
        grid.set_column_spacing(12)
        grid.set_row_spacing(12)

        current_theme = self.theme_engine.get_current_theme()
        themes = self.theme_engine.list_themes()
        self.theme_buttons = {}

        for t in themes:
            card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            card.add_css_class("theme-card")
            if t["id"] == current_theme:
                card.add_css_class("theme-card-active")

            # Theme name
            name = Gtk.Label(label=t["name"])
            name.add_css_class("theme-name")
            name.set_halign(Gtk.Align.START)
            card.append(name)

            # Description
            if t["description"]:
                desc = Gtk.Label(label=t["description"])
                desc.add_css_class("theme-desc")
                desc.set_halign(Gtk.Align.START)
                desc.set_wrap(True)
                desc.set_max_width_chars(30)
                card.append(desc)

            # Color swatches — real colored boxes
            swatch_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            swatch_box.set_halign(Gtk.Align.START)
            swatch_keys = ["bg", "fg", "accent", "accent2", "green", "purple", "red", "yellow"]
            for key in swatch_keys:
                color_hex = t["colors"].get(key, "#555555")
                swatch = Gtk.DrawingArea()
                swatch.set_size_request(26, 26)
                swatch.add_css_class("color-swatch")
                # Parse color and set draw function
                swatch.set_draw_func(self._make_swatch_draw(color_hex))
                swatch_box.append(swatch)
            card.append(swatch_box)

            # Apply button
            is_active = (t["id"] == current_theme)
            btn_label = "✓ Activo" if is_active else "Aplicar"
            apply_btn = Gtk.Button(label=btn_label)
            apply_btn.add_css_class("apply-btn")
            if is_active:
                apply_btn.add_css_class("apply-btn-active")
            apply_btn.connect("clicked", self._on_apply_theme, t["id"])
            self.theme_buttons[t["id"]] = (apply_btn, card)
            card.append(apply_btn)

            grid.append(card)

        box.append(grid)
        scroll.set_child(box)
        self.stack.add_titled(scroll, "themes", "🎨 Temas")

    def _make_swatch_draw(self, color_hex):
        """Create a draw function that paints a color swatch."""
        def draw_func(area, cr, width, height):
            # Parse hex color
            hex_clean = color_hex.lstrip("#")
            r = int(hex_clean[0:2], 16) / 255.0
            g = int(hex_clean[2:4], 16) / 255.0
            b = int(hex_clean[4:6], 16) / 255.0

            # Draw rounded rect
            radius = 6.0
            cr.new_sub_path()
            cr.arc(width - radius, radius, radius, -1.5708, 0)
            cr.arc(width - radius, height - radius, radius, 0, 1.5708)
            cr.arc(radius, height - radius, radius, 1.5708, 3.14159)
            cr.arc(radius, radius, radius, 3.14159, 4.71239)
            cr.close_path()
            cr.set_source_rgb(r, g, b)
            cr.fill()
        return draw_func

    def _on_apply_theme(self, btn, theme_id):
        """Apply theme in background thread with UI feedback."""
        btn.set_label("⏳ Aplicando...")
        btn.set_sensitive(False)

        def do_apply():
            try:
                self.theme_engine.apply_theme(theme_id, silent=True)
                GLib.idle_add(self._on_theme_applied, theme_id)
            except Exception as e:
                GLib.idle_add(self._show_toast, f"❌ Error: {e}")

        thread = threading.Thread(target=do_apply, daemon=True)
        thread.start()

    def _on_theme_applied(self, theme_id):
        """Update UI after theme is applied."""
        # Update all buttons
        for tid, (btn, card) in self.theme_buttons.items():
            if tid == theme_id:
                btn.set_label("✓ Activo")
                btn.add_css_class("apply-btn-active")
                card.add_css_class("theme-card-active")
            else:
                btn.set_label("Aplicar")
                btn.set_sensitive(True)
                try:
                    btn.remove_css_class("apply-btn-active")
                    card.remove_css_class("theme-card-active")
                except Exception:
                    pass

        # Update sidebar current label
        themes = self.theme_engine.list_themes()
        name = theme_id
        for t in themes:
            if t["id"] == theme_id:
                name = t["name"]
                break
        self.current_label.set_label(f"▸ {name}")
        self._show_toast(f"✅ Tema '{name}' aplicado")

    def _on_rollback(self, btn):
        """Rollback to previous backup."""
        try:
            self.theme_engine.rollback()
            current = self.theme_engine.get_current_theme() or "none"
            self.current_label.set_label(f"▸ {current}")
            self._show_toast(f"↩ Restaurado a: {current}")
        except Exception as e:
            self._show_toast(f"❌ Rollback error: {e}")

    def _show_toast(self, message):
        """Show a toast notification."""
        if HAS_ADW:
            toast = Adw.Toast(title=message)
            toast.set_timeout(3)
            # Find the toast overlay or just print
            print(message)
        else:
            print(message)

    # ================================================================
    # WALLPAPERS TAB
    # ================================================================
    def _build_wallpapers_tab(self):
        scroll = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_margin_start(25)
        box.set_margin_end(25)
        box.set_margin_top(25)

        header = Gtk.Label(label="🖼 Biblioteca de Wallpapers")
        header.set_halign(Gtk.Align.START)
        header.add_css_class("section-header")
        box.append(header)

        # Add wallpaper button
        add_btn = Gtk.Button(label="➕ Agregar Wallpaper")
        add_btn.add_css_class("apply-btn")
        add_btn.set_halign(Gtk.Align.START)
        add_btn.connect("clicked", self._on_add_wallpaper)
        box.append(add_btn)

        wallpapers = self.wallpaper_engine.list_wallpapers()
        grid = Gtk.FlowBox()
        grid.set_max_children_per_line(3)
        grid.set_selection_mode(Gtk.SelectionMode.NONE)
        grid.set_column_spacing(12)
        grid.set_row_spacing(12)

        for w in wallpapers:
            card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            card.add_css_class("theme-card")

            # Thumbnail
            if os.path.exists(w.get("thumbnail", "")):
                img = Gtk.Image.new_from_file(w["thumbnail"])
                img.set_size_request(280, 160)
                card.append(img)

            lbl = Gtk.Label(label=w["filename"])
            lbl.set_max_width_chars(25)
            lbl.set_ellipsize(3)  # PANGO_ELLIPSIZE_END
            card.append(lbl)

            btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            btn_set = Gtk.Button(label="Usar Fondo")
            btn_set.add_css_class("apply-btn")
            btn_set.connect("clicked", lambda b, wp=w["path"]: self.wallpaper_engine.set_wallpaper(wp))
            btn_box.append(btn_set)

            btn_gen = Gtk.Button(label="Auto-Tema")
            btn_gen.add_css_class("apply-btn")
            btn_gen.connect("clicked", lambda b, wp=w["path"]: self._generate_and_apply(wp))
            btn_box.append(btn_gen)

            card.append(btn_box)
            grid.append(card)

        box.append(grid)
        scroll.set_child(box)
        self.stack.add_titled(scroll, "wallpapers", "🖼 Fondos")

    def _on_add_wallpaper(self, btn):
        """Open file chooser to add wallpaper."""
        dialog = Gtk.FileDialog()
        filter_img = Gtk.FileFilter()
        filter_img.set_name("Images")
        filter_img.add_mime_type("image/jpeg")
        filter_img.add_mime_type("image/png")
        filter_img.add_mime_type("image/webp")
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(filter_img)
        dialog.set_filters(filters)
        dialog.open(self, None, self._on_wallpaper_chosen)

    def _on_wallpaper_chosen(self, dialog, result):
        try:
            file = dialog.open_finish(result)
            path = file.get_path()
            self.wallpaper_engine.add_wallpaper(path)
            self._show_toast(f"🖼 Wallpaper agregado: {os.path.basename(path)}")
        except Exception:
            pass  # User cancelled

    def _generate_and_apply(self, image_path):
        tname = self.matugen_adapter.generate_theme_from_image(image_path)
        self.theme_engine.apply_theme(tname)

    # ================================================================
    # LAYOUTS TAB
    # ================================================================
    def _build_layouts_tab(self):
        scroll = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_margin_start(25)
        box.set_margin_end(25)
        box.set_margin_top(25)

        header = Gtk.Label(label="📐 Posición de Waybar")
        header.set_halign(Gtk.Align.START)
        header.add_css_class("section-header")
        box.append(header)

        layouts = self.layout_engine.list_layouts()
        for l in layouts:
            btn = Gtk.Button(label=f"Aplicar Layout: {l['name']} ({l['position']})")
            btn.add_css_class("apply-btn")
            btn.connect("clicked", lambda b, lid=l["id"]: self.layout_engine.apply_layout(lid))
            box.append(btn)

        scroll.set_child(box)
        self.stack.add_titled(scroll, "layouts", "📐 Layouts")

    # ================================================================
    # PACKAGES TAB
    # ================================================================
    def _build_packages_tab(self):
        scroll = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_margin_start(25)
        box.set_margin_end(25)
        box.set_margin_top(25)

        header = Gtk.Label(label="📦 Catálogo de Aplicaciones")
        header.set_halign(Gtk.Align.START)
        header.add_css_class("section-header")
        box.append(header)

        catalog = self.package_engine.get_catalog()
        for cat, data in catalog.items():
            cat_lbl = Gtk.Label(label=f"<b>{cat}</b> — {data['description']}")
            cat_lbl.set_use_markup(True)
            cat_lbl.set_halign(Gtk.Align.START)
            cat_lbl.set_margin_top(10)
            box.append(cat_lbl)

            for app in data["apps"]:
                row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
                row.set_margin_start(15)

                app_lbl = Gtk.Label(label=f"{app['name']} ({app['pkg']})")
                app_lbl.set_hexpand(True)
                app_lbl.set_halign(Gtk.Align.START)
                row.append(app_lbl)

                if app["installed"]:
                    badge = Gtk.Label(label="✅ Instalado")
                    badge.add_css_class("status-badge")
                    badge.add_css_class("badge-installed")
                    row.append(badge)
                else:
                    btn = Gtk.Button(label="Instalar")
                    btn.add_css_class("apply-btn")
                    btn.connect("clicked", lambda b, p=app["pkg"], s=app["source"]: self.package_engine.install_package(p, s))
                    row.append(btn)

                box.append(row)

        scroll.set_child(box)
        self.stack.add_titled(scroll, "packages", "📦 Apps Store")

    # ================================================================
    # KEYBINDS TAB
    # ================================================================
    def _build_keybinds_tab(self):
        scroll = Gtk.ScrolledWindow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_margin_start(25)
        box.set_margin_end(25)
        box.set_margin_top(25)

        header = Gtk.Label(label="⌨ Atajos de Teclado (Hyprland)")
        header.set_halign(Gtk.Align.START)
        header.add_css_class("section-header")
        box.append(header)

        binds = [
            ("SUPER + T", "Abrir Terminal (Kitty)"),
            ("SUPER + Q", "Cerrar Ventana Activa"),
            ("SUPER + K", "🏯 Abrir Kaizen Hub"),
            ("SUPER + E", "Abrir Gestor de Archivos"),
            ("SUPER + R", "Lanzar Menú de Apps (Fuzzel)"),
            ("SUPER + F", "Pantalla Completa"),
            ("SUPER + V", "Alternar Flotante"),
            ("SUPER + O", "Toggle Floating + Center"),
            ("SUPER + SHIFT + P", "Captura de Pantalla (Hyprshot)"),
            ("SUPER + P", "Pseudo-tiling"),
            ("SUPER + J", "Toggle Split"),
            ("SUPER + 1..9", "Cambiar Workspace"),
            ("SUPER + SHIFT + 1..9", "Mover Ventana a Workspace"),
            ("SUPER + S", "Workspace Especial"),
        ]

        for keys, action in binds:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
            row.set_margin_start(10)
            row.set_margin_top(2)
            row.set_margin_bottom(2)

            k_lbl = Gtk.Label(label=f"<b>{keys}</b>")
            k_lbl.set_use_markup(True)
            k_lbl.set_size_request(200, -1)
            k_lbl.set_halign(Gtk.Align.START)

            a_lbl = Gtk.Label(label=action)
            a_lbl.set_halign(Gtk.Align.START)

            row.append(k_lbl)
            row.append(a_lbl)
            box.append(row)

        scroll.set_child(box)
        self.stack.add_titled(scroll, "keybinds", "⌨ Atajos")


class KaizenApp(Adw.Application if HAS_ADW else Gtk.Application):
    def __init__(self, base_dir):
        super().__init__(application_id="org.kaizen.hub")
        self.base_dir = base_dir

    def do_activate(self):
        win = KaizenWindow(self, self.base_dir)
        win.present()


def launch_gui(base_dir=None):
    if base_dir is None:
        base_dir = os.path.expanduser("~/.local/share/kaizen")
    app = KaizenApp(base_dir)
    app.run([])


if __name__ == "__main__":
    launch_gui()
