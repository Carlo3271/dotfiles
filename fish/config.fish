source /usr/share/cachyos-fish-config/cachyos-config.fish

# XP/webcore prompt styling to match the God$mack terminal palette.
set -g pure_symbol_prompt "C:\\>"
set -g pure_symbol_reverse_prompt "<\\C"
set -g pure_color_primary 92cbff
set -g pure_color_success 76ff53
set -g pure_color_warning fff066
set -g pure_color_danger ff6b8a
set -g pure_color_mute 5b79bd
set -g pure_color_current_directory pure_color_primary
set -g pure_color_prompt_on_success pure_color_success
set -g pure_color_prompt_on_error pure_color_danger
set -g pure_color_git_branch pure_color_mute
set -g pure_color_git_dirty pure_color_warning

function fish_greeting
    fastfetch
end

function sigil --description 'Show the God$mack XP-webcore terminal sigil'
    env XP_WEBCORE_SPLASH_CLEAR=0 xp-webcore-terminal
end

function godsmack --description 'Show the God$mack XP-webcore terminal sigil'
    sigil
end

function mascot --description 'Compatibility alias for the God$mack terminal sigil'
    sigil
end


# Added by Antigravity CLI installer
set -gx PATH "/home/carlo/.local/bin" $PATH

# Hermes Agent command
fish_add_path "$HOME/.local/bin"
