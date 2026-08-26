# Kaizen Auto-Generated Fish Prompt
# This file is sourced from ~/.config/fish/config.fish
# It redefines fish_prompt with Kaizen theme colors

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
