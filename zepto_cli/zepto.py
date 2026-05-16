"""Zepto store implementation."""

from .base import AbstractGroceryBot

__all__ = ["ZeptoBot"]


class ZeptoBot(AbstractGroceryBot):
    """Drive zepto.com to search groceries and add to cart.

    Usage:
        bot = ZeptoBot().start()
        bot.login("phone_number")
        products = bot.search("amul butter")
        bot.add_to_cart(0)
        print(bot.get_cart_count())
        bot.close()
    """

    BASE_URL = "https://www.zepto.com"
    SEARCH_TEMPLATE = "https://www.zepto.com/search?query={}"
    CART_URL = "https://www.zepto.com/cart"

    # ── Selectors (Zepto-specific) ───────────────────────────
    LOGIN_BTN = 'button[aria-label="login"]'
    PHONE_INPUT = 'input[type="tel"]'
    PRODUCT_CARD = 'a.B4vNQ'
    ADD_BTN_TEXT = "ADD"
    CART_BTN = '[data-testid="cart-btn"]'
    CART_ITEM = '[data-testid="cart-item"]'
