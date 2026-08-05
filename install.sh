#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Single sudo: run with `sudo ./install.sh` for one password prompt.
# Without it, the script self-sudoes each privileged step.
SUDO=""
if [ "$(id -u)" -ne 0 ]; then
    SUDO="sudo"
    echo "Tip: run 'sudo ./install.sh' for a single password prompt."
fi

# --- dependency check ---
TO_INSTALL=""
command -v fzf            >/dev/null 2>&1 || TO_INSTALL="$TO_INSTALL fzf"
python3 -c "import argcomplete" 2>/dev/null || TO_INSTALL="$TO_INSTALL python-argcomplete"
python3 -m pip --version  >/dev/null 2>&1 || TO_INSTALL="$TO_INSTALL python-pip"

if [ -n "$TO_INSTALL" ]; then
    echo "The following packages need to be installed:"
    echo "  pacman -S --needed$TO_INSTALL"
    read -p "Proceed with installation? (y/n): " ans
    case "$ans" in
        y|Y|yes|YES) $SUDO pacman -S --needed $TO_INSTALL ;;
        *) echo "Skipping dependency installation." ;;
    esac
fi

# --- launcher ---
$SUDO tee /usr/bin/trasher >/dev/null <<EOF
#!/usr/bin/env bash
export PYTHONPATH="$SCRIPT_DIR\${PYTHONPATH:+:\$PYTHONPATH}"
exec python3 -m trasher "\$@"
EOF
$SUDO chmod +x /usr/bin/trasher

echo "
   ████████╗██████╗  █████╗ ███████╗██╗  ██╗███████╗██████╗
   ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║  ██║██╔════╝██╔══██╗
      ██║   ██████╔╝███████║███████╗███████║█████╗  ██████╔╝
      ██║   ██╔══██╗██╔══██║╚════██║██╔══██║██╔══╝  ██╔══██╗
      ██║   ██║  ██║██║  ██║███████║██║  ██║███████╗██║  ██║
      ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝

installed succesfully!"
echo "Run 'trasher' to manage your trash"
echo "For tab completion (bash), add to ~/.bashrc:"
echo '  eval "$(register-python-argcomplete trasher)"'
