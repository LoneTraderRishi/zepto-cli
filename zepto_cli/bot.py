"""
ZeptoBot — Playwright-powered grocery ordering agent for Zepto.
Supports persistent sessions, OTP login, product search, and cart management.
"""
import time, os, re

__version__ = "0.1.0"


class ZeptoBot:
    """Drive zepto.com to search groceries and add to cart.

    Usage:
        bot = ZeptoBot().start()
        bot.login("phone_number")  # or bot.login("phone", "otp")
        products = bot.search("amul butter")
        bot.add_to_cart(0)
        print(bot.get_cart_count())
        bot.close()
    """

    def __init__(self, session_path="/tmp/zepto_session.json", headless=True):
        self.session_path = session_path
        self.headless = headless
        self._pw = None
        self.browser = None
        self.context = None
        self.page = None
        self.logged_in = False

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

    def ensure_session(self):
        """Check if a valid saved session exists. Returns True if already logged in, False otherwise.
        Does NOT attempt login — use this in non-login commands to avoid the fake-phone hack."""
        self.go_home()
        try:
            if not self.page.locator('button[aria-label="login"]').is_visible(timeout=3000):
                self.logged_in = True
                return True
        except:
            pass
        return False

    def _wait(self, s=2):
        time.sleep(s)

    # ── Navigation ──────────────────────────────────────────

    def go_home(self):
        self.page.goto("https://www.zepto.com", wait_until="load", timeout=15000)
        self._wait(2)

    # ── Location ────────────────────────────────────────────

    def set_location(self, lat=19.0760, lon=72.8777):
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

    # ── Login ───────────────────────────────────────────────

    def login(self, phone, otp=None):
        """Login with phone + optional OTP.
        
        Returns:
            True        — already logged in or login successful
            "needs_otp" — OTP sent, waiting for user to provide it
            False       — failed
        """
        self.go_home()
        # Check saved session
        try:
            if not self.page.locator('button[aria-label="login"]').is_visible(timeout=2000):
                self.logged_in = True
                return True
        except:
            pass

        # Full login flow
        try:
            self.page.click('button[aria-label="login"]', timeout=3000)
            self._wait(1)
            self.page.fill('input[type="tel"]', phone)
            self._wait(0.3)
            self.page.click('button:has-text("Continue")', timeout=3000)
            self._wait(2)
        except Exception as e:
            print(f"Login error: {e}")
            return False

        if otp is None:
            return "needs_otp"
        return self.enter_otp(otp)

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

    # ── Search ──────────────────────────────────────────────

    def search(self, query):
        """Search products. Returns list of {name, price, mrp, quantity}."""
        self.page.goto(f"https://www.zepto.com/search?query={query}", wait_until="load", timeout=15000)
        self._wait(3)
        products = []
        cards = self.page.locator('a.B4vNQ')
        for i in range(min(cards.count(), 25)):
            try:
                text = cards.nth(i).inner_text()
                lines = [l.strip() for l in text.split('\n') if l.strip()]
                if "ADD" not in lines:
                    continue
                aidx = lines.index("ADD")
                price = lines[aidx + 1]
                mrp = lines[aidx + 2]
                if aidx + 4 < len(lines) and lines[aidx + 4] == "OFF":
                    name = lines[aidx + 5]
                    qty = lines[aidx + 6] if aidx + 6 < len(lines) else ""
                else:
                    name = lines[aidx + 3]
                    qty = lines[aidx + 4] if aidx + 4 < len(lines) else ""
                if name.startswith('₹'):
                    continue
                products.append({"name": name, "price": price, "mrp": mrp, "quantity": qty})
            except:
                pass
        return products

    # ── Cart ────────────────────────────────────────────────

    def add_to_cart(self, index=0):
        """Click ADD on the Nth product card."""
        self._wait(1)
        try:
            cards = self.page.locator('a.B4vNQ')
            if cards.count() > index:
                btn = cards.nth(index).locator('button:has-text("ADD")')
                if btn.count() > 0:
                    btn.click()
                    self._wait(1)
                    return True
        except:
            pass
        return False

    def get_cart_count(self):
        try:
            text = self.page.locator('[data-testid="cart-btn"]').first.inner_text()
            nums = re.findall(r'\d+', text)
            return int(nums[0]) if nums else 0
        except:
            return 0

    def get_cart_items(self):
        """Navigate to the cart page and list all items.
        Returns list of {name, quantity, price, total} or empty list."""
        try:
            self.page.goto("https://www.zepto.com/cart", wait_until="load", timeout=15000)
            self._wait(3)
        except:
            pass

        items = []
        # Try parsing item cards on the cart page
        try:
            cards = self.page.locator('[data-testid="cart-item"]')
            if cards.count() == 0:
                # Fallback: try generic item containers
                cards = self.page.locator('div[class*="cart"] div[class*="item"]')
            if cards.count() == 0:
                # Last resort: grab all visible product-like rows
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
