# Dotfiles — Windows XP / Webcore Rice

**DE:** XFCE 4  
**WM:** xfwm4 + WinTC Luna shell  
**Theme:** Luna-Webcore / WhiteSur-Dark / Windows XP Linux style (Blue)  
**Bar:** polybar  
**Launcher:** rofi  
**Terminal:** alacritty + xfce4-terminal  
**Shell:** fish + bash + zsh  
**Compositor:** picom  

## What's in here

| Dir | What |
|-----|------|
| `bash/` | .bashrc, .bash_profile, .bash_logout |
| `zsh/` | .zshrc |
| `fish/` | fish config, functions, conf.d |
| `alacritty/` | terminal colors, fonts, opacity |
| `xfce4/` | xfconf XML + terminalrc + desktop icons |
| `polybar/` | panel config + launch script |
| `rofi/` | app launcher config |
| `picom/` | compositor config |
| `fastfetch/` | sysinfo logo + config |
| `neofetch/` | sysinfo config |
| `btop/` | system monitor config |
| `micro/` | editor settings + catppuccin theme |
| `autostart/` | XDG autostart .desktop files |
| `systemd/user/` | hermes-gateway user service |
| `scripts/` | xp-webcore-terminal, wintc-rice-layout, low-latency-session, screenshot-copy, etc. |
| `themes/` | Luna-Webcore, WhiteSur-Dark |
| `webcore-rice/` | reactive widgets, fetch/music scripts |

## Install

```bash
git clone https://github.com/<you>/dotfiles.git ~/.dotfiles
cd ~/.dotfiles
./install.sh
```

Requires: `stow` (from `pacman -S stow` or equivalent).

The script symlinks every directory into `$HOME`, backing up any existing conflicting files to `~/.dotfiles-backup/`.

## Missing but needed

These are installed via package manager, not tracked here:
- **WhiteSur icon theme** (`yay -S whitesur-icon-theme` or copy from `/usr/share/icons`)
- **Mojave-CT icons** (`yay -S mojave-ct-icon-theme`)
- **Tahoma / Lucida Console fonts** (`ttf-ms-fonts`, `ttf-lucida-console`, or Windows fonts)
- **Luna theme** (included here as custom xfwm4 theme)
- **Noto Sans / MesloLGS Nerd Font / Noto Color Emoji** for polybar

## Credits

XP Luna aesthetic inspired by the Windows XP Luna theme.  
God$mack//404 terminal sigil by carlo.
