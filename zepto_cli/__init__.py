"""🥬 Zepto CLI — Order groceries from Zepto, Blinkit, or any quick-commerce store.

Usage:
    from zepto_cli import ZeptoBot, BlinkitBot

    # Zepto (default)
    bot = ZeptoBot().start()
    bot.login("phone")
    products = bot.search("milk")

    # Blinkit
    bot = BlinkitBot().start()
    bot.login("phone")
    products = bot.search("milk")
"""

from .bot import ZeptoBot, BlinkitBot, __version__

__all__ = ["ZeptoBot", "BlinkitBot", "__version__"]
