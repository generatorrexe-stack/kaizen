# Kaizen Auto-Generated Fish Prompt
# This file is sourced from ~/.config/fish/config.fish

# 1. Global Kaizen Colors for Kitty Banner in config.fish
set -g KAIZEN_BORDE (set_color {{accent_raw}})
set -g KAIZEN_TITULO (set_color {{accent2_raw}})
set -g KAIZEN_BERRY (set_color {{purple_raw}})
set -g KAIZEN_TEAL (set_color {{green_raw}})
set -g KAIZEN_LIMA (set_color {{yellow_raw}})
set -g KAIZEN_AZUL (set_color {{blue_raw}})
set -g KAIZEN_MAGENTA (set_color {{accent_raw}})

# 2. Fish Syntax Highlighting Colors
set -U fish_color_normal {{fg_raw}}
set -U fish_color_command {{accent2_raw}}
set -U fish_color_quote {{green_raw}}
set -U fish_color_redirection {{purple_raw}}
set -U fish_color_end {{accent_raw}}
set -U fish_color_error {{red_raw}}
set -U fish_color_param {{blue_raw}}
set -U fish_color_comment {{fg_alt_raw}}
set -U fish_color_match {{cyan_raw}}
set -U fish_color_selection --background={{bg_alt_raw}}
set -U fish_color_search_match --background={{bg_alt_raw}}
set -U fish_color_operator {{yellow_raw}}
set -U fish_color_escape {{magenta_raw}}
set -U fish_color_autosuggestion {{fg_alt_raw}}

# 3. Prompt Function
function fish_prompt
    set_color {{accent_raw}}
    echo -n "╭─"

    set_color {{accent2_raw}}
    echo -n " "

    set_color {{purple_raw}}
    echo -n "$USER"

    set_color {{accent_raw}}
    echo -n "@"

    set_color {{accent2_raw}}
    echo -n "$hostname"

    set_color {{accent_raw}}
    echo -n " ─ "

    set_color {{accent2_raw}}
    echo -n " "

    set_color {{purple_raw}}
    echo -n (basename $PWD)

    echo ""

    set_color {{accent_raw}}
    echo -n "╰─❯ "

    set_color normal
end
