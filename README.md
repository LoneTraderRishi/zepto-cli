<div align="center">
  <h1>🥬 Zepto CLI</h1>
  <p><strong>Your AI agent's grocery arm — search, manage, and order household essentials from Zepto, Blinkit, or any quick-commerce store (India only).</strong></p>
  <p>
    <a href="#features"><img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fapi.github.com%2Frepos%2FLoneTraderRishi%2Fzepto-cli&query=stargazers_count&style=for-the-badge&logo=github&label=stars&color=yellow" alt="Stars"></a>
    <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python">
    <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="MIT">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen?style=for-the-badge" alt="PRs Welcome">
  </p>
  <br>
</div>

Give your AI agent the power to search Zepto or Blinkit, manage your cart, and keep your kitchen stocked — all from a text message, a cron job, or a skill.

Uses **CloakBrowser** under the hood — a stealth Chromium binary with 57 C++ patch levels that passes bot detection. One-time OTP login, persistent sessions per store. No API keys needed — your agent drives the store like a human.

> ⚠️ **India only.** Zepto and Blinkit only deliver in Indian cities. Does NOT work outside India.
> ⚠️ **Payment is manual** — the bot gets your cart ready and you tap Pay on your phone. UPI PIN / Bank OTP can't be automated.

---

## 🧠 What This Is

This isn't just a CLI. It's an **AI-managed grocery inventory system** — a tool your agent uses to handle your household essentials across stores.

**How it works with your AI agent:**

1. You tell your agent "I'm running out of milk"
2. Your agent searches your preferred store, finds the best option, adds it to your cart
3. Checks current cart inventory
4. Schedules recurring orders ("order milk every Monday at 9 AM")
5. Can compare across stores — Zepto vs Blinkit
6. You tap Pay in the app when ready

All through Hermes Agent, OpenClaw, Claude Code, or any Python-capable agent.

---

## ✨ Features

- 🏪 **Multi-store** — Zepto and Blinkit supported, same API for both
- 🔍 **Search** any product — name, price, MRP, quantity at a glance
- 🛒 **Add to cart** and manage what's inside
- 📋 **List cart items** — see everything waiting to be checked out
- 🤖 **Agent-native** — `pip install zepto-cli`, one import in any skill
- 🔐 **One-time OTP login** — session persists for days per store
- 📍 **Auto-location** via geolocation (Mumbai default)
- 🧾 **CLI-native** — pipe, script, cron everything
- 📦 **Inventory-aware** — track what's in your cart, plan what's low

## 🚀 Human Quick Start

```bash
# Default: install with CloakBrowser (stealth Chromium, auto-downloads binary)
pip install zepto-cli

# Alternative: use raw Playwright instead (if CloakBrowser has issues)
pip install zepto-cli[playwright]
playwright install chromium

# 2. Login (one-time per store)
zepto login                          # Zepto (default) — auto-downloads stealth Chromium
zepto login --store blinkit          # Blinkit (separate session)

# 4. Search products
zepto search "amul butter"                    # Zepto
zepto search "amul butter" --store blinkit     # Blinkit

# 5. See your cart
zepto cart --list                              # Zepto cart
zepto cart --store blinkit --list              # Blinkit cart

# 6. Order multiple things at once
zepto order "brown bread, amul milk, eggs"              # Zepto
zepto order "brown bread, amul milk" --store blinkit     # Blinkit
```

---

## 🤖 Agent Integration

Zepto CLI is designed as a **tool your agent calls** — one import, any store, zero ceremony.

### Hermes Agent (primary target)

Add it as a dependency, then use in any skill:

```python
# In a Hermes Agent skill — works with any store
from zepto_cli import ZeptoBot, BlinkitBot

def check_and_order(items: list[str], store: str = "zepto") -> str:
    """AI grocery manager — search, add, and report cart status.
    
    Args:
        items: List of items to order
        store: "zepto" or "blinkit"
    """
    BotClass = {"zepto": ZeptoBot, "blinkit": BlinkitBot}.get(store, ZeptoBot)
    bot = BotClass().start()
    bot.ensure_session()

    # Check current cart first
    current = bot.get_cart_items()
    cart_report = f"🛒 {store.title()} already has {len(current)} items" if current else f"🛒 {store.title()} cart is empty"

    # Add requested items
    results = []
    for item in items:
        products = bot.search(item)
        if products:
            bot.add_to_cart(0)
            results.append(f"✅ {products[0]['name']} — {products[0]['price']}")
        else:
            results.append(f"❌ No results for '{item}'")

    total = bot.get_cart_count()
    bot.close()
    return "\n".join([cart_report] + results + [f"\n📦 {store.title()} Cart: {total} items"])
```

**Skill config** (`~/.hermes/skills/grocery/skill.md`):
```yaml
---
name: grocery
description: Household grocery management across Zepto and Blinkit
tools:
  - zepto-cli
---

Lets your agent manage kitchen inventory. Supports:
  - "add milk to zepto cart"
  - "check what's in blinkit"
  - "order weekly essentials"
```

**Cron — auto-reorder essentials:**
```bash
# Zepto — every Monday
zepto order "amul milk 1L, brown bread, eggs 12 pack" --store zepto

# Blinkit — every Thursday
zepto order "curd, paneer, bananas" --store blinkit
```

One message to Hermes: *"I'm running low on eggs"* → bot checks both stores, adds to whichever has stock, tells you what's in cart.

### OpenClaw

```python
from zepto_cli import ZeptoBot, BlinkitBot

# Zepto
bot = ZeptoBot().start()
bot.ensure_session()
bot.search("banana")

# Blinkit
bot = BlinkitBot().start()
bot.ensure_session()
bot.search("banana")
```

Or from a shell step:
```bash
zepto order "eggs, bread, milk" --store blinkit
```

### Any Python agent

```python
from zepto_cli import ZeptoBot, BlinkitBot
# Works with Claude Code, Codex, OpenCode, LangChain, CrewAI, etc.
```

---

## 📋 What Your Agent Can Do

| Action | Example | Agent Command |
|--------|---------|---------------|
| 🔍 **Search Zepto** | "Is amul butter available?" | `zepto search "amul butter"` |
| 🔍 **Search Blinkit** | "Is it on Blinkit?" | `zepto search "amul butter" --store blinkit` |
| 🛒 **Add to cart** | "Add milk to Zepto" | `zepto add --search "milk"` |
| 📦 **Check Zepto cart** | "What's in my Zepto cart?" | `zepto cart --list` |
| 📦 **Check Blinkit cart** | "What's in Blinkit?" | `zepto cart --store blinkit --list` |
| 📝 **Order multiple** | "Restock the kitchen (Zepto)" | `zepto order "milk, eggs, bread, butter"` |
| 🔄 **Auto-refill** | "Order milk every Monday" | (via cron with --store flag) |

---

## 🧩 API Reference

### Bot Classes

```python
from zepto_cli import ZeptoBot, BlinkitBot
```

Both share the same API (`AbstractGroceryBot`):

| Method | Returns | Description |
|--------|---------|-------------|
| `.start()` | self | Launches browser + loads saved session |
| `.close()` | — | Saves session + closes browser |
| `.ensure_session()` | `True` / `False` | Check saved session |
| `.login(phone, otp=None)` | `True` / `"needs_otp"` / `False` | OTP login |
| `.enter_otp(otp)` | `True` / `False` | Enter 6-digit OTP |
| `.set_location(lat, lon)` | `True` / `False` | Change delivery area |
| `.search(query)` | `list[dict]` | Search → `[{name, price, mrp, quantity, store}]` |
| `.add_to_cart(index=0)` | `True` / `False` | Click ADD on Nth card |
| `.get_cart_count()` | `int` | Items in cart |
| `.get_cart_items()` | `list[dict]` | Cart details → `[{name, quantity, price}]` |
| `.go_home()` | — | Navigate to store homepage |

### CLI

```
zepto login [--phone NUMBER] [--store STORE]      One-time OTP login
zepto search <query> [--limit N] [--store STORE]  Search products
zepto add [--search <query>] [--index N] [--store STORE]  Add to cart
zepto cart [-l/--list] [--store STORE]            Show cart count (--list for items)
zepto order "<item1>, <item2>, ..." [--store STORE]  Full search + add flow
```

Stores: `zepto` (default), `blinkit`

### Example: check cart contents

```bash
zepto cart --list
# 🛒 Zepto Cart: 3 items
#   • Amul Taaza Milk 500 ml     ₹34
#   • Eggoz Farm Fresh Eggs      ₹76
#   • Britannia Whole Wheat Bread ₹54

zepto cart --store blinkit --list
# 🛒 Blinkit Cart: 2 items
#   • Amul Butter                ₹55
#   • Brown Bread                ₹48
```

---

## ⚙️ How It Works

1. **CloakBrowser** launches a stealth Chromium (57 C++ patches, bypasses bot detection)
2. Sets geolocation to Mumbai (override with `set_location()`)
3. Login sends an OTP — you enter it once per store
4. Cookies persist to `~/.<store>_session.json` — reused by your agent automatically
5. `search()` navigates to the store's search page and parses product cards
6. `add_to_cart()` clicks the ADD button on the target card
7. `get_cart_items()` reads the cart page to show current inventory
8. **--store flag** selects which store to use — same API, different selectors

## 🛡️ Limitations

- **No auto-payment** — requires UPI PIN / Bank OTP
- **Blinkit WAF** — Blinkit has stronger anti-bot protection. If selectors fail, run with `headless=False` to inspect and tune
- **Selector fragility** — store CSS class names change on deploy. The bot reads card text content as fallback
- **Rate limited** — CloudFront returns 429 if you search too fast (wait ~5s between calls)
- **India only** — Zepto and Blinkit only deliver in Indian cities

## 🏗️ Project Structure

```
zepto-cli/
├── zepto_cli/
│   ├── __init__.py     # Package exports (ZeptoBot, BlinkitBot)
│   ├── base.py         # AbstractGroceryBot base class
│   ├── zepto.py        # ZeptoBot implementation
│   ├── blinkit.py      # BlinkitBot implementation
│   ├── bot.py          # Backwards-compat re-exports
│   └── cli.py          # CLI with --store flag
├── scripts/demo.sh
├── pyproject.toml
└── README.md
```

## 🤝 Contributing

PRs welcome! New stores, better selectors, new features:

- **Add a new store** — subclass `AbstractGroceryBot`, set selectors, add to `STORES` registry
- **Selector updates** — if product cards change their HTML structure
- **New features** — checkout flow, order history, multi-location, payment flow hints
- **Stealth improvements** — better anti-detection for CloudFront / WAF

## ⚖️ Disclaimer

This project is **for educational purposes**. These tools drive public websites like a human would using a browser. Use responsibly and in accordance with each store's terms of service.

## 📄 License

MIT
