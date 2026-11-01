#!/usr/bin/env bash
set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${HOME}"

echo "==> Installing dotfiles from $DOTFILES_DIR"
echo "==> Target: $TARGET"

DEFAULT_PACKAGES="bash zsh fish alacritty polybar rofi picom fastfetch neofetch btop micro xfce4 gtk-3.0 autostart systemd local themes webcore-rice"
packages="${1:-$DEFAULT_PACKAGES}"

# Prefer GNU Stow if available
if command -v stow >/dev/null 2>&1; then
    echo "==> Using GNU Stow"
    cd "$DOTFILES_DIR"
    for pkg in $packages; do
        [[ -d "$pkg" ]] || { echo "    [SKIP] $pkg"; continue; }
        echo "    [STOW] $pkg"
        stow -v -R -t "$TARGET" "$pkg"
    done
    echo "==> Done."
    exit 0
fi

# Fallback: manual symlink method
echo "==> GNU Stow not found, using manual symlinks"
BACKUP_DIR="$TARGET/.dotfiles-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

for pkg in $packages; do
    src="$DOTFILES_DIR/$pkg"
    [[ -d "$src" ]] || { echo "    [SKIP] $pkg"; continue; }

    echo "    [STOW] $pkg"
    cd "$src"

    while IFS= read -r -d '' item; do
        rel="${item#./}"
        dest="$TARGET/$rel"

        # Skip if already correctly linked
        if [[ -L "$dest" ]]; then
            current_target="$(readlink "$dest")"
            if [[ "$current_target" == "$(pwd)/$item" ]]; then
                continue
            fi
        fi

        # Back up existing file/dir/symlink (but not our own symlinks)
        if [[ -e "$dest" || -L "$dest" ]]; then
            # Skip paths that resolve inside the dotfiles repo
            real_dest="$(realpath -m "$dest" 2>/dev/null || echo "$dest")"
            if [[ "$real_dest" == "$DOTFILES_DIR"* ]]; then
                continue
            fi
            echo "      BACKUP: ~${rel}"
            mkdir -p "$BACKUP_DIR/$(dirname "$rel")"
            mv "$dest" "$BACKUP_DIR/$rel"
        fi

        mkdir -p "$(dirname "$dest")"
        ln -s "$(pwd)/$item" "$dest"
    done < <(find . -mindepth 1 -print0)

    cd "$DOTFILES_DIR"
done

echo "==> Done. Restart your session or run 'xfce4-panel -r' to reload panel."
