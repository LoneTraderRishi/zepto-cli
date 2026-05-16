"""Blinkit store implementation.

Note: Blinkit has strong anti-bot protection (CloudFront WAF).
If selectors fail, run with headless=False to inspect the page structure
and update the selectors below.
"""

from .base import AbstractGroceryBot

__all__ = ["BlinkitBot"]


class BlinkitBot(AbstractGroceryBot):
    """Drive blinkit.com to search groceries and add to cart.

    Usage:
        bot = BlinkitBot().start()
        bot.login("phone_number")
        products = bot.search("amul butter")
        bot.add_to_cart(0)
        bot.close()
    """

    BASE_URL = "https://www.blinkit.com"
    SEARCH_TEMPLATE = "https://www.blinkit.com/s?q={}"
    CART_URL = "https://www.blinkit.com/cart"

    # ── Selectors (Blinkit-specific) ─────────────────────────
    # Blinkit uses a different DOM structure than Zepto.
    # These are estimates — tune by inspecting the actual page.
    LOGIN_BTN = 'button:has-text("Login")'
    PHONE_INPUT = 'input[type="tel"], input[placeholder*="phone"], input[placeholder*="mobile"]'
    PRODUCT_CARD = 'a[class*="product"], div[class*="product"]'
    ADD_BTN_TEXT = "ADD"
    CART_BTN = 'div[class*="cart"], button[aria-label*="cart"], a[href*="/cart"]'
    CART_ITEM = 'div[class*="cart-item"], div[data-testid*="cart"]'

    def _parse_card(self, lines):
        """Blinkit product card layout is different from Zepto.
        Falls back to first-line name + first ₹ price heuristic."""
        try:
            aidx = lines.index(self.ADD_BTN_TEXT)
        except ValueError:
            return None

        try:
            # Common Blinkit card: name, quantity, price, MRP
            price = ""
            mrp = ""
            name = ""
            qty = ""
            for line in lines[aidx + 1:]:
                if line.startswith("₹"):
                    if not price:
                        price = line
                    elif not mrp:
                        mrp = line
                    else:
                        break
                elif not name:
                    name = line
                else:
                    qty = line

            if name.startswith('₹'):
                return None
            if not name or not price:
                return None
            return {"name": name, "price": price, "mrp": mrp, "quantity": qty}
        except (ValueError, IndexError):
            return None
