#!/usr/bin/env bash
set -Eeuo pipefail

HOME_DIR="${HOME:-$(getent passwd "$(id -un)" 2>/dev/null | cut -d: -f6)}"
TARGET_DIR="${1:-$HOME_DIR}"
readonly TARGET_DIR

if [[ ! -d "$TARGET_DIR" ]]; then
    echo "Error: '$TARGET_DIR' is not a directory." >&2
    exit 1
fi

if [[ "$TARGET_DIR" != "$HOME_DIR" ]]; then
    echo "Cleaning only '$TARGET_DIR' is not allowed unless it is your home directory." >&2
    exit 1
fi

if [[ "${EUID:-$(id -u)}" -eq 0 ]]; then
    echo "Error: run this script as a normal user; package manager commands may require sudo." >&2
    exit 1
fi

echo "====================================================="
echo "              Linux Cleanup Utility                  "
echo "====================================================="
echo "Target: $TARGET_DIR"
read -r -p "Delete cache files, old logs, and temporary files? [y/N]: " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Operation cancelled."
    exit 0
fi

cleanup_cache() {
    local cache_dir="$1"
    if [[ -d "$cache_dir" ]]; then
        find "$cache_dir" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
    fi
}

cleanup_cache "$HOME_DIR/.cache"

for package_manager in apt-get dnf pacman; do
    if command -v "$package_manager" >/dev/null 2>&1; then
        echo "Package manager cache cleanup is not performed automatically. Run the package manager's cleanup command with sudo when appropriate."
        break
    fi
done

find "$HOME_DIR/.local/share" -type f -name "*.log" -mtime +7 -delete 2>/dev/null || true
find "$HOME_DIR/.cache" -type f -name "*.tmp" -delete 2>/dev/null || true
find "$HOME_DIR" -type f -name "core" -delete 2>/dev/null || true
find "$HOME_DIR" -type f -size +500M -print -exec rm -i {} +

echo "Cleanup complete. Review the deleted files above carefully."
