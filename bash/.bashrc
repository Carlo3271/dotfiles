export PATH="$HOME/.npm-global/bin:$PATH"
#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

alias ls='ls --color=auto'
alias grep='grep --color=auto'

case ":$PATH:" in
  *":$HOME/.local/bin:"*) ;;
  *) PATH="$HOME/.local/bin:$PATH" ;;
esac

if [[ -z "${XP_WEBCORE_SPLASH_SHOWN:-}" && "${TERM:-}" != dumb ]]; then
  export XP_WEBCORE_SPLASH_SHOWN=1
  command -v xp-webcore-terminal >/dev/null 2>&1 && xp-webcore-terminal || true
fi

PS1='\[\033[38;2;118;255;83m\]C:\\Documents and Settings\\\u\[\033[38;2;146;203;255m\]\\\W\[\033[0m\]> '


# Added by Antigravity CLI installer
export PATH="/home/carlo/.local/bin:$PATH"
