#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

chmod +x "$SCRIPT_DIR/main.py"

sudo ln -sf "$SCRIPT_DIR/main.py" /usr/local/bin/trasher

echo "Trasher installed succesfully!"
echo "Run 'trasher' to manage your trash"
