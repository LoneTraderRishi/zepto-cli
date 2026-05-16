#!/usr/bin/env bash
# zepto-cli demo — run this to see the bot in action
# Requires: pip install zepto-cli && playwright install chromium
# First run: run `zepto login` to set up your session

set -e

echo "🥬 Zepto CLI Demo"
echo "================="
echo ""

# Check if session exists
if [ ! -f /tmp/zepto_session.json ]; then
    echo "❌ No saved session found."
    echo "👉 Run 'zepto login' first to authenticate."
    echo ""
    exit 1
fi

echo "🔍 Searching for 'amul butter'..."
zepto search "amul butter" --limit 5
echo ""

echo "🔍 Searching for 'brown bread'..."
zepto search "brown bread" --limit 3
echo ""

echo "🛒 Placing order..."
zepto order "amul butter, brown bread, eggs"
echo ""

echo "📦 Final cart:"
zepto cart
echo ""
echo "✅ Demo complete!"
