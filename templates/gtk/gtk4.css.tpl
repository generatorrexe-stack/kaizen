/* Kaizen Template - GTK4 / Libadwaita / Nautilus Styling */
@define-color accent_bg_color {{accent}};
@define-color accent_fg_color {{bg}};
@define-color accent_color {{accent}};
@define-color window_bg_color {{bg}};
@define-color window_fg_color {{fg}};
@define-color view_bg_color {{bg_alt}};
@define-color view_fg_color {{fg}};
@define-color headerbar_bg_color {{bg_alt}};
@define-color headerbar_fg_color {{fg}};
@define-color headerbar_border_color {{accent}};
@define-color card_bg_color {{bg_alt}};
@define-color card_fg_color {{fg}};
@define-color popover_bg_color {{bg_alt}};
@define-color popover_fg_color {{fg}};
@define-color dialog_bg_color {{bg_alt}};
@define-color dialog_fg_color {{fg}};

/* GTK4 & Nautilus Specific Classes */
.nautilus-window, window.background {
    background-color: {{bg}};
    color: {{fg}};
}

headerbar {
    background-color: {{bg_alt}};
    color: {{fg}};
    border-bottom: 1px solid {{accent}};
}

.sidebar-pane, stack sidebar {
    background-color: {{bg_alt}};
    color: {{fg}};
}
