/* Kaizen Template - GTK3 & Nautilus Dynamic Styling */
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

/* Base GTK3 Override Rules */
window, .background {
    background-color: {{bg}};
    color: {{fg}};
}

headerbar {
    background-color: {{bg_alt}};
    color: {{fg}};
    border-bottom: 1px solid {{accent}};
}

.sidebar, stack sidebar {
    background-color: {{bg_alt}};
    color: {{fg}};
}

button.suggested-action {
    background-color: {{accent}};
    color: {{bg}};
}
