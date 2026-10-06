#!/bin/bash

echo "====================================================="
echo "             Linux System Cleanup Utility            "
echo "====================================================="

# Prompt the user as requested
read -p "Are you sure you want to clean large bloat files and app caches? (y/n): " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Operation cancelled. Exiting..."
    exit 0
fi

echo -e "\n[1/4] Clearing user application caches (~/.cache/)..."
# Safely removes contents of the cache folder without deleting the folder itself
rm -rf ~/.cache/* 2>/dev/null
echo "User app caches cleaned."

echo -e "\n[2/4] Clearing system package manager caches..."
# Detects the package manager and cleans its cache (requires sudo password)
if command -v apt-get >/dev/null; then
    sudo apt-get clean
    echo "APT cache cleaned."
elif command -v dnf >/dev/null; then
    sudo dnf clean all
    echo "DNF cache cleaned."
elif command -v pacman >/dev/null; then
    sudo pacman -Sc --noconfirm
    echo "Pacman cache cleaned."
else
    echo "Supported package manager (APT, DNF, Pacman) not found. Skipping."
fi

echo -e "\n[3/4] Removing common bloat (old logs, tmp files, core dumps)..."
# Deletes old log files (>7 days), temporary files, and crash dumps in the home directory
find ~/.local/share -type f -name "*.log" -mtime +7 -delete 2>/dev/null
find ~/.cache -type f -name "*.tmp" -delete 2>/dev/null
find ~ -type f -name "core" -delete 2>/dev/null
echo "Common bloat removed."

echo -e "\n[4/4] Searching for large files (>500MB)..."
echo "You will be prompted individually for any massive files found in your home directory."
echo "Type 'y' to delete or 'n' to keep."
echo "-----------------------------------------------------"
# Finds files larger than 500MB and uses 'rm -i' to ask for confirmation before deleting each one
find ~ -type f -size +500M -exec rm -i {} \;

echo -e "\n====================================================="
echo "                  Cleanup Complete!                  "
echo "====================================================="
