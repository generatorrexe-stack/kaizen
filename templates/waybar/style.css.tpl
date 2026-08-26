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

#group-left,
#group-right {
    background: transparent;
}

#custom-arch {
    color: {{accent}};
    font-size: 21px;
    padding: 0 14px;
    margin-right: 6px;
    background: rgba(8, 8, 18, 0.94);
    border: 1px solid {{accent}};
    border-radius: 10px;
    box-shadow: 0 0 10px {{accent}};
}

#custom-arch:hover {
    color: {{accent}};
    background: rgba(255, 45, 85, 0.12);
    border-color: {{accent}};
}

#mpris {
    color: {{accent}};
    padding: 0 13px;
    margin-right: 6px;
    background: rgba(8, 8, 18, 0.94);
    border: 1px solid {{accent}};
    border-radius: 10px;
}

#window {
    color: {{fg}};
    padding: 0 13px;
    background: rgba(8, 8, 18, 0.94);
    border: 1px solid {{blue}};
    border-radius: 10px;
}

#window.empty {
    color: transparent;
}

#workspaces {
    background: rgba(8, 8, 18, 0.94);
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
    background: rgba(0, 229, 255, 0.13);
    border: 1px solid {{accent2}};
}

#workspaces button:hover {
    color: #ffffff;
    background: rgba(0, 229, 255, 0.08);
}

#workspaces button.urgent {
    color: {{accent}};
    background: rgba(255, 45, 85, 0.15);
}

#clock,
#network,
#memory,
#cpu,
#temperature,
#wireplumber,
#battery,
#tray {
    background: rgba(8, 8, 18, 0.94);
    border-radius: 10px;
    padding: 0 10px;
    margin-left: 5px;
}

#clock {
    color: {{accent2}};
    border: 1px solid {{accent2}};
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
    color: {{blue}};
    border: 1px solid {{blue}};
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
    color: {{accent}};
    border-color: {{accent}};
}
