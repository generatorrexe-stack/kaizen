# Kaizen Template - Starship Shell Prompt Palette
format = """
$username\
$hostname\
$directory\
$git_branch\
$git_status\
$c\
$rust\
$golang\
$nodejs\
$python\
$docker_context\
$line_break\
$character"""

[character]
success_symbol = "[❯]({{accent}})"
error_symbol = "[❯]({{red}})"

[directory]
style = "bold {{accent2}}"
format = "[$path]($style) "

[git_branch]
symbol = "󰘬 "
style = "bold {{purple}}"
format = "on [$symbol$branch]($style) "

[username]
style_user = "bold {{accent}}"
show_always = false

[hostname]
style = "bold {{yellow}}"
