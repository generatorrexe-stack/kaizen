* {
    font-family: "JetBrainsMono Nerd Font";
    font-size: 13px;
    font-weight: 600;
    min-width: 0;
    min-height: 0;
}

window#waybar {
    background: transparent;
    color: {{fg}};
}

#group-top {
    background: transparent;
    margin-bottom: 4px;
}

#custom-arch {
    color: {{accent}};
    font-size: 20px;
    padding: 8px 0;
    margin-bottom: 6px;
    background: alpha({{bg_alt}}, 0.94);
    border: 1px solid {{accent}};
    border-radius: 12px;
    box-shadow: 0 0 10px {{accent}};
    transition: all 0.2s ease;
}

#custom-arch:hover {
    color: #ffffff;
    background: alpha({{accent}}, 0.25);
    border-color: {{accent}};
    box-shadow: 0 0 14px {{accent}};
}

#mpris {
    color: {{accent}};
    font-size: 14px;
    padding: 8px 0;
    margin-bottom: 4px;
    background: alpha({{bg_alt}}, 0.94);
    border: 1px solid {{accent}};
    border-radius: 10px;
    transition: all 0.2s ease;
}

#mpris:hover {
    background: alpha({{accent}}, 0.20);
}

#workspaces {
    background: alpha({{bg_alt}}, 0.94);
    border: 1px solid {{accent2}};
    border-radius: 12px;
    padding: 6px 0;
    margin: 4px 0;
    box-shadow: 0 0 8px alpha({{accent2}}, 0.15);
}

#workspaces button {
    color: {{fg_alt}};
    background: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 6px 0;
    margin: 3px 5px;
    font-size: 14px;
    transition: all 0.2s ease;
}

#workspaces button.active {
    color: {{accent2}};
    background: alpha({{accent2}}, 0.16);
    border: 1px solid {{accent2}};
    box-shadow: 0 0 8px alpha({{accent2}}, 0.35);
}

#workspaces button:hover {
    color: #ffffff;
    background: alpha({{accent2}}, 0.10);
}

#workspaces button.urgent {
    color: {{accent}};
    background: alpha({{accent}}, 0.20);
    border: 1px solid {{accent}};
}

#group-bottom,
.modules-right {
    background: alpha({{bg_alt}}, 0.94);
    border: 1px solid {{accent2}};
    border-radius: 12px;
    padding: 8px 0;
    margin-top: 4px;
    box-shadow: 0 0 8px alpha({{accent2}}, 0.15);
}

#wireplumber,
#network,
#memory,
#cpu,
#temperature,
#battery,
#tray {
    background: transparent;
    border: none;
    border-radius: 6px;
    padding: 6px 0;
    margin: 1px 4px;
    font-size: 15px;
    transition: all 0.2s ease;
}

#wireplumber:hover,
#network:hover,
#memory:hover,
#cpu:hover,
#temperature:hover,
#battery:hover {
    background: alpha({{fg}}, 0.08);
}

#wireplumber {
    color: {{blue}};
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

#battery {
    color: {{green}};
}

#battery.warning {
    color: {{yellow}};
}

#battery.critical {
    color: {{accent}};
}

#clock {
    color: {{accent2}};
    font-size: 12px;
    font-weight: 800;
    padding: 8px 0 4px 0;
    margin: 6px 4px 0 4px;
    border-top: 1px solid alpha({{border}}, 0.25);
}

#tray {
    padding: 4px 0;
}
