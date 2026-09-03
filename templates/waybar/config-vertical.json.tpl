[
    {
        "layer": "top",
        "position": "left",
        "width": 48,
        "spacing": 0,
        "margin-top": {{outer_gap}},
        "margin-bottom": {{outer_gap}},
        "margin-left": {{outer_gap}},
        "margin-right": 0,

        "modules-left": ["group/top"],
        "modules-center": ["hyprland/workspaces"],
        "modules-right": ["group/bottom", "tray"],

        "group/top": {
            "orientation": "vertical",
            "modules": [
                "custom/arch",
                "mpris"
            ]
        },

        "group/bottom": {
            "orientation": "vertical",
            "modules": [
                "wireplumber",
                "network",
                "memory",
                "cpu",
                "temperature",
                "battery",
                "clock"
            ]
        },

        "custom/arch": {
            "format": "󰣇",
            "tooltip-format": "󰣇  Arch Linux\nClic: Lanzador Fuzzel",
            "on-click": "fuzzel"
        },

        "mpris": {
            "format": "󰎆",
            "format-paused": "󰏤",
            "format-stopped": "󰓛",
            "tooltip-format": "󰎆  {title} - {artist}\nClic: Play/Pausa\nScroll: Cambiar canción",
            "on-click": "playerctl play-pause",
            "on-scroll-up": "playerctl next",
            "on-scroll-down": "playerctl previous"
        },

        "hyprland/workspaces": {
            "format": "{icon}",
            "all-outputs": true,
            "persistent-workspaces": {
                "*": 5
            },
            "format-icons": {
                "active": "󰮯",
                "default": "󰊠",
                "urgent": "󰀨"
            }
        },

        "clock": {
            "format": "{:%H\n%M}",
            "tooltip-format": "<tt>{calendar}</tt>",
            "calendar": {
                "mode": "month",
                "weeks-pos": "right",
                "format": {
                    "months": "<span color='{{accent2}}'><b>{}</b></span>",
                    "days": "<span color='{{fg}}'>{}</span>",
                    "weekdays": "<span color='{{accent}}'><b>{}</b></span>",
                    "today": "<span color='{{green}}'><b><u>{}</u></b></span>"
                }
            }
        },

        "wireplumber": {
            "format": "{icon}",
            "format-muted": "󰝟",
            "format-icons": ["󰕿", "󰖀", "󰕾"],
            "tooltip-format": "Audio: {volume}%\nScroll: Ajustar volumen\nClic: Silenciar",
            "on-click": "wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle",
            "on-scroll-up": "wpctl set-volume @DEFAULT_AUDIO_SINK@ 2%+",
            "on-scroll-down": "wpctl set-volume @DEFAULT_AUDIO_SINK@ 2%-"
        },

        "network": {
            "format-wifi": "󰤨",
            "format-ethernet": "󰈀",
            "format-disconnected": "󰤭",
            "tooltip-format-wifi": "WiFi: {essid}\nIP: {ipaddr}\nSeñal: {signalStrength}%",
            "tooltip-format-ethernet": "Ethernet\nIP: {ipaddr}",
            "on-click": "kitty -e nmtui"
        },

        "memory": {
            "format": "󰍛",
            "tooltip-format": "RAM: {used:0.1f} GB / {total:0.1f} GB ({percentage}%)",
            "on-click": "kitty -e btop"
        },

        "cpu": {
            "format": "󰻠",
            "interval": 2,
            "tooltip-format": "CPU: {usage}%",
            "on-click": "kitty -e btop"
        },

        "temperature": {
            "critical-threshold": 80,
            "format": "󰔏",
            "tooltip-format": "Temperatura: {temperatureC}°C"
        },

        "battery": {
            "states": {
                "warning": 30,
                "critical": 15
            },
            "format": "{icon}",
            "format-charging": "󰂄",
            "format-plugged": "󰚥",
            "tooltip-format": "Batería: {capacity}%\nEstado: {timeTo}",
            "format-icons": [
                "󰂎",
                "󰁺",
                "󰁻",
                "󰁼",
                "󰁽",
                "󰁾",
                "󰁿",
                "󰂀",
                "󰂁",
                "󰂂",
                "󰁹"
            ]
        },

        "tray": {
            "icon-size": 16,
            "spacing": 8
        }
    }
]
