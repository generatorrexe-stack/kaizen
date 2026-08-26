/* Kaizen Template - SwayNC Notification Center Styling */
* {
    font-family: "JetBrainsMono Nerd Font", sans-serif;
    border-radius: 10px;
}

.notification-row {
    outline: none;
}

.notification {
    background: {{bg_alt}};
    border: 1px solid {{accent}};
    color: {{fg}};
    box-shadow: 0 0 10px {{accent}};
}

.notification-content {
    background: transparent;
    padding: 10px;
}

.close-button {
    background: {{red}};
    color: {{bg}};
}

.widget-title {
    color: {{accent2}};
    font-size: 1.2rem;
    font-weight: bold;
}

.widget-dnd {
    background: {{bg}};
    border: 1px solid {{accent2}};
    color: {{fg}};
}
