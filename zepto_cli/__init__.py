"""Initialization and backwards-compat re-exports."""

from .base import AbstractGroceryBot
from .zepto import ZeptoBot
from .blinkit import BlinkitBot
from .bot import ZeptoBot as ZeptoBotAlias, BlinkitBot as BlinkitBotAlias, __version__

__all__ = ["ZeptoBot", "BlinkitBot", "AbstractGroceryBot"]
__version__ = "0.2.1"
