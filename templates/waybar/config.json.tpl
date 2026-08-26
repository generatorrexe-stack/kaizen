[
    {
        "layer": "top",
        "position": "top",
        "height": 36,
        "spacing": 0,
        "margin-top": 8,
        "margin-left": 10,
        "margin-right": 10,

        "modules-left": ["group/left"],
        "modules-center": ["hyprland/workspaces"],
        "modules-right": ["group/right"],

        "group/left": {
            "orientation": "horizontal",
            "modules": [
                "custom/arch",
                "mpris",
                "hyprland/window"
            ]
        },

        "group/right": {
            "orientation": "horizontal",
            "modules": [
                "clock",
                "network",
                "memory",
                "cpu",
                "temperature",
                "wireplumber",
                "battery",
                "tray"
            ]
        },

        "custom/arch": {
            "format": "",
            "tooltip-format": "  Arch Linux",
            "on-click": "fuzzel"
        },

        "hyprland/workspaces": {
            "format": "{icon}",
            "all-outputs": true,
            "persistent-workspaces": {
                "*": 5
            },
            "format-icons": {
                "active": "",
                "default": "",
                "urgent": ""
            }
        },

        "hyprland/window": {
            "format": "   {title}",
            "max-length": 30,
            "all-outputs": true
        },

        "clock": {
            "format": "  {:%I:%M %p  %a %d %b}",
            "tooltip-format": "<big>{:%Y %B}</big>\n<tt>{calendar}</tt>",
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

        "mpris": {
            "format": "  {status_icon} {dynamic}",
            "status-icons": {
                "playing": "",
                "paused": "",
                "stopped": ""
            },
            "dynamic-len": 25,
            "on-click": "playerctl play-pause"
        },

        "network": {
            "format-wifi": "  {ipaddr}",
            "format-ethernet": "  {ipaddr}",
            "format-disconnected": "  Offline",
            "tooltip-format-wifi": "  {essid}\nIP: {ipaddr}/{cidr}",
            "tooltip-format-ethernet": "  Ethernet\nIP: {ipaddr}/{cidr}",
            "on-click": "kitty -e nmtui"
        },

        "memory": {
            "format": "  {percentage}%",
            "tooltip-format": "RAM: {used:0.1f} GB / {total:0.1f} GB"
        },

        "cpu": {
            "format": "  {usage}%",
            "interval": 2,
            "tooltip-format": "CPU: {usage}%"
        },

        "temperature": {
            "critical-threshold": 80,
            "format": "  {temperatureC}°C",
            "tooltip-format": "Temperatura: {temperatureC}°C"
        },

        "wireplumber": {
            "format": "  {volume}%",
            "format-muted": "  Muted",
            "on-click": "wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle",
            "tooltip-format": "Audio: {volume}%"
        },

        "battery": {
            "states": {
                "warning": 30,
                "critical": 15
            },
            "format": "{icon}  {capacity}%",
            "format-charging": "  {capacity}%",
            "format-plugged": "  {capacity}%",
            "format-icons": [
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                ""
            ]
        },

        "tray": {
            "icon-size": 16,
            "spacing": 10
        }
    }
]
