/* Kaizen Template - GTK3 & Thunar Dynamic Styling */

/* Standard GTK3 Symbolic Colors for Classic Apps (Thunar, etc.) */
@define-color theme_bg_color {{bg}};
@define-color theme_fg_color {{fg}};
@define-color theme_base_color {{bg_alt}};
@define-color theme_text_color {{fg}};
@define-color theme_selected_bg_color {{accent}};
@define-color theme_selected_fg_color {{bg}};
@define-color theme_unfocused_bg_color {{bg}};
@define-color theme_unfocused_fg_color {{fg_alt}};
@define-color theme_unfocused_base_color {{bg_alt}};
@define-color theme_unfocused_text_color {{fg_alt}};
@define-color theme_unfocused_selected_bg_color {{accent}};
@define-color theme_unfocused_selected_fg_color {{bg}};

@define-color borders {{border}};
@define-color unfocused_borders {{bg_alt}};

/* Libadwaita / Modern GTK3 compatibility */
@define-color accent_bg_color {{accent}};
@define-color accent_fg_color {{bg}};
@define-color accent_color {{accent}};
@define-color window_bg_color {{bg}};
@define-color window_fg_color {{fg}};
@define-color view_bg_color {{bg_alt}};
@define-color view_fg_color {{fg}};
@define-color headerbar_bg_color {{bg_alt}};
@define-color headerbar_fg_color {{fg}};
@define-color headerbar_border_color {{border}};
@define-color card_bg_color {{bg_alt}};
@define-color card_fg_color {{fg}};

/* Base GTK3 Override Rules */
window, .background {
    background-color: @theme_bg_color;
    color: @theme_fg_color;
}

headerbar, toolbar {
    background-color: @headerbar_bg_color;
    color: @headerbar_fg_color;
    border-bottom: 1px solid @borders;
}

/* Views, IconViews and TreeViews (Thunar file pane) */
view, iconview, treeview, textview, .view {
    background-color: @theme_base_color;
    color: @theme_text_color;
}

view:selected, iconview:selected, treeview:selected, .view:selected {
    background-color: @theme_selected_bg_color;
    color: @theme_selected_fg_color;
}

/* Sidebars and Paned widgets */
.sidebar, stack sidebar, paned separator {
    background-color: @theme_bg_color;
    color: @theme_fg_color;
}

/* Specific Thunar window classes */
.thunar, thunar-window, ThunarWindow {
    background-color: @theme_bg_color;
    color: @theme_fg_color;
}

.thunar .sidebar, ThunarWindow .sidebar {
    background-color: @theme_bg_color;
    color: @theme_fg_color;
}

.thunar .view, ThunarWindow .view {
    background-color: @theme_base_color;
    color: @theme_text_color;
}

button.suggested-action {
    background-color: @accent_bg_color;
    color: @accent_fg_color;
}
