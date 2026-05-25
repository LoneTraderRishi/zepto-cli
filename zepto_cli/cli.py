#!/usr/bin/env python3
"""
Zepto CLI — Order groceries from your terminal.

Supports Zepto and Blinkit via the --store flag.

Usage:
    zepto login                        # One-time OTP login (Zepto)
    zepto login --store blinkit        # One-time OTP login (Blinkit)
    zepto search "amul milk"           # Search Zepto
    zepto search "amul milk" --store blinkit  # Search Blinkit
    zepto order "bread, eggs, milk"    # Full flow: search + add all (Zepto)
    zepto order "milk" --store blinkit # Full flow: search + add (Blinkit)

Shorthand:
    zb login                           # Same as `zepto login`
    zb order "milk" --store blinkit    # Same as `zepto order ...`

Stores:
    zepto (default)  → zepto.com
    blinkit          → blinkit.com
"""
import sys, argparse
from .bot import ZeptoBot, BlinkitBot, __version__

# ── Store registry ────────────────────────────────────────────
STORES = {
    "zepto": ZeptoBot,
    "blinkit": BlinkitBot,
}
