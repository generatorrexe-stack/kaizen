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

#group-left {
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

.modules-right {
    background: rgba(8, 8, 18, 0.94);
    border: 1px solid {{accent2}};
    border-radius: 10px;
    margin-left: 5px;
    padding: 0 5px;
}

#clock,
#network,
#memory,
#cpu,
#temperature,
#wireplumber,
#battery,
#tray {
    background: transparent;
    border: none;
    border-radius: 0;
    padding: 0 5px;
    margin: 0;
}

#clock {
    color: {{accent2}};
}

#network {
    color: {{green}};
}

#memory {
    color: {{purple}};
}

#cpu {
    color: {{yellow}};
}

#temperature {
    color: {{accent}};
}

#wireplumber {
    color: {{blue}};
}

#battery {
    color: {{green}};
}

#battery.warning {
    color: {{yellow}};
}

#battery.critical {
    color: {{accent}};
}
