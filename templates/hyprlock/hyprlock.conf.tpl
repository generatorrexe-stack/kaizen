$accent = rgb({{accent_raw}})
$accent2 = rgb({{accent2_raw}})
$accent3 = rgb({{purple_raw}})
$bg = rgb({{bg_raw}})
$text = rgb({{fg_raw}})
$fail = rgb({{red_raw}})

general {
  hide_cursor = true
}

background {
  monitor =
  path = {{wallpaper_path}}
  blur_passes = 4
  blur_size = 6
  noise = 0.02
  color = $bg
}

# ===== TOP LEFT: ARCH + SYSTEM STATUS =====
label {
  monitor =
  text = 
  color = $accent
  font_size = 24
  font_family = JetBrainsMono Nerd Font
  position = 30, -25
  halign = left
  valign = top
}
label {
  monitor =
  text = cmd[update:10000] echo "$(hostname) ▸ UPTIME $(uptime -p | sed 's/up //')"
  color = $text
  font_size = 13
  font_family = JetBrainsMono Nerd Font
  position = 65, -30
  halign = left
  valign = top
}

# ===== TOP RIGHT: KEYBOARD LAYOUT =====
label {
  monitor =
  text =  $LAYOUT
  color = $text
  font_size = 13
  font_family = JetBrainsMono Nerd Font
  position = -30, -30
  halign = right
  valign = top
}

# ===== DATE (arriba de la hora) =====
label {
  monitor =
  text = cmd[update:43200000] date +"%A · %d %B %Y" | tr 'a-z' 'A-Z'
  color = $accent2
  font_size = 20
  font_family = JetBrainsMono Nerd Font Bold
  position = 0, 280
  halign = center
  valign = center
}

# ===== TIME (grande) =====
label {
  monitor =
  text = $TIME
  color = $accent
  font_size = 130
  font_family = JetBrainsMono Nerd Font Bold
  position = 0, 180
  halign = center
  valign = center
}

# ===== AVATAR =====
image {
  monitor =
  path = /home/wonyoung/Documents/banners/foto123-circle.png
  size = 170, 170
  border_size = 5
  border_color = $accent
  rounding = -1
  position = 0, 0
  halign = center
  valign = center
}

# ===== USERNAME =====
label {
  monitor =
  text = $USER
  color = $text
  font_size = 24
  font_family = JetBrainsMono Nerd Font Bold
  position = 0, -110
  halign = center
  valign = center
}

# ===== INPUT FIELD =====
input-field {
  monitor =
  size = 340, 56
  outline_thickness = 3
  rounding = 28
  dots_size = 0.25
  dots_spacing = 0.3
  dots_center = true
  outer_color = $accent
  inner_color = rgba({{bg_raw}}b3)
  font_color = $accent2
  fade_on_empty = false
  placeholder_text = <span foreground="#{{accent_raw}}"> password</span>
  hide_input = false
  check_color = $accent2
  fail_color = $fail
  fail_text = <i>DENIED · $FAIL ($ATTEMPTS)</i>
  capslock_color = $fail
  position = 0, -175
  halign = center
  valign = center
}

# ===== PHRASE =====
label {
  monitor =
  text = ✦ THE WINNER TAKES IT ALL ✦
  color = $accent3
  font_size = 13
  font_family = JetBrainsMono Nerd Font
  position = 0, -230
  halign = center
  valign = center
}

# ===== BOTTOM LEFT: BATTERY + LOCATION =====
label {
  monitor =
  text = cmd[update:10000] echo "🔋 $(cat /sys/class/power_supply/BAT0/capacity)%"
  color = $accent2
  font_size = 17
  font_family = JetBrainsMono Nerd Font Bold
  position = 45, 65
  halign = left
  valign = bottom
}
label {
  monitor =
  text = cmd[update:600000] echo "📍 $(cat /tmp/sddm-location.txt 2>/dev/null || echo 'Unknown')"
  color = $text
  font_size = 15
  font_family = JetBrainsMono Nerd Font
  position = 45, 40
  halign = left
  valign = bottom
}

# ===== BOTTOM RIGHT: MUSIC =====
label {
  monitor =
  text = ▂▅▇▅▂
  color = $accent
  font_size = 16
  font_family = JetBrainsMono Nerd Font Bold
  position = -45, 65
  halign = right
  valign = bottom
}
label {
  monitor =
  text = cmd[update:3000] echo "$(cat /tmp/sddm-music.txt 2>/dev/null || echo 'Not playing')"
  color = $text
  font_size = 14
  font_family = JetBrainsMono Nerd Font
  position = -45, 40
  halign = right
  valign = bottom
}

# ===== BOTTOM CENTER: WARNING =====
label {
  monitor =
  text = ▓▓▓ SYSTEM LOCKED ▓▓▓
  color = $accent
  font_size = 12
  font_family = JetBrainsMono Nerd Font Bold
  position = 0, 10
  halign = center
  valign = bottom
}
