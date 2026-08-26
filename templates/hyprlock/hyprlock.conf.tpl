# Kaizen Template - Hyprlock Config
background {
    monitor =
    path = screenshot
    blur_passes = 3
    blur_size = 8
    color = {{bg}}
}

input-field {
    monitor =
    size = 250, 50
    outline_thickness = 3
    dots_size = 0.2
    dots_spacing = 0.6
    dots_center = true
    outer_color = {{accent}}
    inner_color = {{bg_alt}}
    font_color = {{fg}}
    fade_on_empty = false
    placeholder_text = <span foreground="{{fg_alt}}">enter passphrase...</span>
    hide_input = false
    check_color = {{yellow}}
    fail_color = {{red}}
    fail_text = <i>$FAIL <b>($ATTEMPTS)</b></i>
    position = 0, -20
    halign = center
    valign = center
}

label {
    monitor =
    text = $TIME
    color = {{accent}}
    font_size = 64
    font_family = JetBrainsMono Nerd Font
    position = 0, 80
    halign = center
    valign = center
}
