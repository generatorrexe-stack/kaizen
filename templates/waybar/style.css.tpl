/* Kaizen Template - Waybar Styling (Based on User's Premium Glassmorphism Pill Layout) */
* {
    font-family: "JetBrainsMono Nerd Font";
    font-size: 13px;
    font-weight: 600;
    min-height: 0;
}

window#waybar {
    background: transparent;
    color: {{fg}};
}

/* GRUPOS */
#group-left,
#group-right {
    background: transparent;
}

/* ARCH LOGO */
#custom-arch {
    color: {{accent}};
    font-size: 21px;
    padding: 0 14px;
    margin-right: 6px;

    background: {{bg_alt}};
    border: 1px solid {{accent}};
    border-radius: 10px;
    box-shadow: 0 0 10px {{accent}};
}

#custom-arch:hover {
    color: {{accent2}};
    background: {{bg}};
    border-color: {{accent2}};
}

/* MPRIS */
#mpris {
    color: {{accent}};
    padding: 0 13px;
    margin-right: 6px;

    background: {{bg_alt}};
    border: 1px solid {{accent}};
    border-radius: 10px;
}

/* WINDOW */
#window {
    color: {{fg}};
    padding: 0 13px;

    background: {{bg_alt}};
    border: 1px solid {{accent2}};
    border-radius: 10px;
}

#window.empty {
    color: transparent;
}

/* WORKSPACES */
#workspaces {
    background: {{bg_alt}};
    border: 1px solid {{accent2}};
    border-radius: 10px;
    padding: 0 5px;
}

#workspaces button {
    color: {{fg_alt}};
    background: transparent;
    border: none;
    border-radius: 7px;
    padding: 0 9px;
    margin: 4px 2px;
}

#workspaces button.active {
    color: {{accent2}};
    background: {{bg}};
    border: 1px solid {{accent2}};
}

#workspaces button:hover {
    color: {{fg}};
    background: {{bg}};
}

#workspaces button.urgent {
    color: {{red}};
    background: {{bg}};
}

/* RIGHT MODULES */
#clock,
#network,
#memory,
#cpu,
#temperature,
#wireplumber,
#battery,
#tray {
    background: {{bg_alt}};
    border-radius: 10px;
    padding: 0 10px;
    margin-left: 5px;
}

#clock {
    color: {{cyan}};
    border: 1px solid {{cyan}};
}

#network {
    color: {{green}};
    border: 1px solid {{green}};
}

#memory {
    color: {{purple}};
    border: 1px solid {{purple}};
}

#cpu {
    color: {{yellow}};
    border: 1px solid {{yellow}};
}

#temperature {
    color: {{accent}};
    border: 1px solid {{accent}};
}

#wireplumber {
    color: {{accent2}};
    border: 1px solid {{accent2}};
}

#battery {
    color: {{green}};
    border: 1px solid {{green}};
}

#battery.warning {
    color: {{yellow}};
    border-color: {{yellow}};
}

#battery.critical {
    color: {{red}};
    border-color: {{red}};
}
