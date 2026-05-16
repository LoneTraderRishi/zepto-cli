"""🥬 Zepto CLI — Grocery bots for Zepto, Blinkit, and more.

Backwards-compatible re-exports.
Use `from zepto_cli import ZeptoBot` — still works.
"""

from .zepto import ZeptoBot
from .blinkit import BlinkitBot

# The original __version__ lives on the ZeptoBot class
__version__ = "0.2.0"
