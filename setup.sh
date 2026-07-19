#!/bin/bash
# Tuibro setup script - installs dependencies and Chromium for Android
set -e

echo "═══════════════════════════════════════"
echo "  Tuibro — TUI Browser Agent Setup"
echo "═══════════════════════════════════════"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "[1/3] Installing Python dependencies..."
if command -v pip3 &>/dev/null; then
    pip3 install --break-system-packages -r requirements.txt
elif command -v pip &>/dev/null; then
    pip install -r requirements.txt
else
    echo "Error: pip not found. Install python3-pip first."
    exit 1
fi

echo ""
echo "[2/3] Installing Playwright Chromium..."
python3 -m playwright install chromium
python3 -m playwright install-deps chromium 2>/dev/null || echo "(Some deps may already be installed)"

echo ""
echo "[3/3] Creating config directory..."
mkdir -p ~/.tuibro

echo ""
echo "═══════════════════════════════════════"
echo "  Setup complete!"
echo "═══════════════════════════════════════"
echo ""
echo "Quick start:"
echo "  1. Set your API key:"
echo "     export TUIBRO_OPENAI_API_KEY=sk-..."
echo "     or: python3 main.py --provider ollama (for local models)"
echo ""
echo "  2. Run Tuibro:"
echo "     python3 main.py"
echo ""
echo "  3. With a task:"
echo "     python3 main.py --task 'Search Google for Python tutorials'"
echo ""
echo "  4. Quick commands inside Tuibro:"
echo "     /google <query>  — Quick Google search"
echo "     /url <url>       — Navigate to URL"
echo "     Tab              — Switch panes"
echo "     F2               — Cycle providers"
echo "     F3               — Cycle models"
echo "     Ctrl+C           — Stop agent / Quit"
