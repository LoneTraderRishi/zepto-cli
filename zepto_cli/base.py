"""Abstract base class for grocery store bots."""

import time
import os
import re
from abc import ABC, abstractmethod
from typing import Optional


class AbstractGroceryBot(ABC):
    """Base class for Playwright-powered grocery ordering bots.

    Subclasses must set:
        BASE_URL        — store homepage (e.g. "https://www.zepto.com")
        SEARCH_TEMPLATE — URL with {} placeholder for query
        CART_URL        — cart page URL
        LOGIN_BTN       — playwright locator for login button
        PHONE_INPUT     — locator for phone number input
        PRODUCT_CARD    — locator for product card links/anchors
        ADD_BTN_TEXT    — text on ADD button (e.g. "ADD" or "Add")
        CART_BTN        — locator for cart count button
        CART_ITEM       — locator for cart item containers
    """

    # ── Store-specific config (override in subclass) ──────────
    BASE_URL: str = ""
    SEARCH_TEMPLATE: str = ""
    CART_URL: str = ""
    LOGIN_BTN: str = ""
    PHONE_INPUT: str = ""
    PRODUCT_CARD: str = ""
    ADD_BTN_TEXT: str = "ADD"
    CART_BTN: str = ""
    CART_ITEM: str = ""

    def __init__(self, session_path: Optional[str] = None, headless: bool = True):
        self.session_path = session_path or f"/tmp/{self.__class__.__name__.lower()}_session.json"
        self.headless = headless
        self._pw = None
        self.browser = None
        self.context = None
        self.page = None
        self.logged_in = False

    # ── Lifecycle ────────────────────────────────────────────

    def start(self):
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.launch(headless=self.headless)
        kwargs = {
            "viewport": {"width": 1280, "height": 800},
            "locale": "en-IN",
            "timezone_id": "Asia/Kolkata",
            "geolocation": {"latitude": 19.0760, "longitude": 72.8777},
            "permissions": ["geolocation"],
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        }
        if os.path.exists(self.session_path):
            kwargs["storage_state"] = self.session_path
        self.context = self.browser.new_context(**kwargs)
        self.page = self.context.new_page()
        self.page.set_default_timeout(8000)
        return self

    def close(self):
        self.save_session()
        try:
            if self.browser:
                self.browser.close()
            if self._pw:
                self._pw.stop()
        except:
            pass

    def save_session(self):
        if self.context:
            try:
                self.context.storage_state(path=self.session_path)
            except:
                pass

    def _wait(self, s: float = 2):
        time.sleep(s)

    # ── Session ──────────────────────────────────────────────

    def ensure_session(self):
        """Check if saved session is valid. Does NOT attempt login."""
        self.go_home()
        try:
            if not self.page.locator(self.LOGIN_BTN).is_visible(timeout=3000):
                self.logged_in = True
                return True
        except:
            pass
        return False

    # ── Navigation ───────────────────────────────────────────

    def go_home(self):
        self.page.goto(self.BASE_URL, wait_until="load", timeout=15000)
        self._wait(2)

    # ── Location ─────────────────────────────────────────────

    def set_location(self, lat: float = 19.0760, lon: float = 72.8777):
        """Set delivery location. Default: Mumbai."""
        self.context.set_geolocation({"latitude": lat, "longitude": lon})
        self.go_home()
        try:
            self.page.click('button[aria-label="Select Location"]', timeout=3000)
            self._wait(0.5)
            self.page.click('text=Use My Current Location', timeout=3000)
            self._wait(2)
            self.page.keyboard.press("Escape")
            self._wait(0.5)
            return True
        except:
            return False

    # ── Login ────────────────────────────────────────────────

    def login(self, phone: str, otp: Optional[str] = None):
        """Login with phone + optional OTP.

        Returns:
            True        — already logged in or login successful
            "needs_otp" — OTP sent, waiting for user
            False       — failed
        """
        self.go_home()
        # Check saved session
        try:
            if not self.page.locator(self.LOGIN_BTN).is_visible(timeout=2000):
                self.logged_in = True
                return True
        except:
            pass

        # Full login flow
        try:
            self.page.click(self.LOGIN_BTN, timeout=3000)
            self._wait(1)
            self._fill_phone(phone)
            self._wait(0.3)
            self._click_continue()
            self._wait(2)
        except Exception as e:
            print(f"Login error: {e}")
            return False

        if otp is None:
            return "needs_otp"
        return self.enter_otp(otp)

    def _fill_phone(self, phone: str):
        """Override if store uses a different phone input selector."""
        self.page.fill(self.PHONE_INPUT, phone)

    def _click_continue(self):
        self.page.click('button:has-text("Continue")', timeout=3000)

    def enter_otp(self, otp):
        otp = str(otp)
        try:
            send_btn = self.page.locator('button:has-text("Send OTP")')
            if send_btn.is_visible(timeout=2000) and not send_btn.is_disabled():
                send_btn.click()
                self._wait(2)
        except:
            pass
        for i, d in enumerate(otp):
            try:
                self.page.locator('input[type="text"]').nth(i).fill(d)
            except:
                pass
        self._wait(2)
        body = self.page.inner_text("body")
        if "Login" not in body[:200]:
            self.logged_in = True
            self.save_session()
            return True
        return False

    # ── Search ───────────────────────────────────────────────

    def search(self, query: str):
        """Search products. Returns list of {name, price, mrp, quantity, store}."""
        url = self.SEARCH_TEMPLATE.format(query)
        self.page.goto(url, wait_until="load", timeout=15000)
        self._wait(3)
        return self._parse_search_results()

    def _parse_search_results(self):
        """Override for store-specific card parsing."""
        products = []
        cards = self.page.locator(self.PRODUCT_CARD)
        for i in range(min(cards.count(), 25)):
            try:
                text = cards.nth(i).inner_text()
                lines = [l.strip() for l in text.split('\n') if l.strip()]
                if self.ADD_BTN_TEXT not in lines:
                    continue
                item = self._parse_card(lines)
                if item:
                    item["store"] = self.__class__.__name__.replace("Bot", "").lower()
                    products.append(item)
            except:
                pass
        return products

    def _parse_card(self, lines: list):
        """Extract {name, price, mrp, quantity} from card text lines.
        Override if store layout differs from Zepto's pattern."""
        try:
            aidx = lines.index(self.ADD_BTN_TEXT)
            price = lines[aidx + 1]
            mrp = lines[aidx + 2]
            if aidx + 4 < len(lines) and lines[aidx + 4] == "OFF":
                name = lines[aidx + 5]
                qty = lines[aidx + 6] if aidx + 6 < len(lines) else ""
            else:
                name = lines[aidx + 3]
                qty = lines[aidx + 4] if aidx + 4 < len(lines) else ""
            if name.startswith('₹'):
                return None
            return {"name": name, "price": price, "mrp": mrp, "quantity": qty}
        except (ValueError, IndexError):
            return None

    # ── Cart ─────────────────────────────────────────────────

    def add_to_cart(self, index: int = 0):
        """Click the ADD button on the Nth product card."""
        self._wait(1)
        try:
            cards = self.page.locator(self.PRODUCT_CARD)
            if cards.count() > index:
                btn = cards.nth(index).locator(f'button:has-text("{self.ADD_BTN_TEXT}")')
                if btn.count() > 0:
                    btn.click()
                    self._wait(1)
                    return True
        except:
            pass
        return False

    def get_cart_count(self) -> int:
        """Read item count from the cart button."""
        try:
            text = self.page.locator(self.CART_BTN).first.inner_text()
            nums = re.findall(r'\d+', text)
            return int(nums[0]) if nums else 0
        except:
            return 0

    def get_cart_items(self):
        """Navigate to cart page and list items.
        Returns list of {name, quantity, price} or empty list."""
        try:
            self.page.goto(self.CART_URL, wait_until="load", timeout=15000)
            self._wait(3)
        except:
            pass
        return self._parse_cart_items()

    def _parse_cart_items(self):
        """Override for store-specific cart item parsing."""
        items = []
        try:
            cards = self.page.locator(self.CART_ITEM)
            if cards.count() == 0:
                cards = self.page.locator('div[class*="cart"] div[class*="item"]')
            if cards.count() == 0:
                cards = self.page.locator('div:has(> button)').filter(has_text="₹")
            for i in range(min(cards.count(), 50)):
                try:
                    text = cards.nth(i).inner_text()
                    lines = [l.strip() for l in text.split('\n') if l.strip()]
                    if not lines:
                        continue
                    name = lines[0]
                    price = ""
                    qty = ""
                    for line in lines[1:]:
                        if line.startswith("₹"):
                            price = line
                        elif line.isdigit() or "x" in line.lower():
                            qty = line
                    if name and price:
                        items.append({"name": name, "quantity": qty, "price": price})
                except:
                    pass
        except:
            pass
        return items
