function fastfetch --wraps fastfetch --description 'Clear the typed command before showing Fastfetch'
    if status is-interactive
        printf '\e[2J\e[3J\e[H'
    end

    command fastfetch $argv
end
