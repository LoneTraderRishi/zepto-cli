<div align="center">
  <h1>🥬 Zepto CLI</h1>
  <p><strong>Your AI agent's grocery arm — search, manage, and order household essentials from Zepto (India only).</strong></p>
  <p>
    <a href="#features"><img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fapi.github.com%2Frepos%2FLoneTraderRishi%2Fzepto-cli&query=stargazers_count&style=for-the-badge&logo=github&label=stars&color=yellow" alt="Stars"></a>
    <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python">
    <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="MIT">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen?style=for-the-badge" alt="PRs Welcome">
  </p>
  <br>
</div>

Give your AI agent the power to search Zepto, manage your cart, and keep your kitchen stocked — all from a text message, a cron job, or a skill.

Uses **Playwright** under the hood. One-time OTP login, persistent sessions. No API keys needed — your agent drives Zepto like a human.

> ⚠️ **India only.** Zepto delivers in 20+ Indian cities. Does NOT work outside India.
> ⚠️ **Payment is manual** — the bot gets your cart ready and you tap Pay on your phone. Zepto requires UPI PIN / Bank OTP which can't be automated.

---

## 🧠 What This Is

This isn't just a CLI. It's an **AI-managed grocery inventory system** — a tool your agent uses to handle your household essentials.

**How it works with your AI agent:**

1. You tell your agent "I'm running out of milk"
2. Your agent searches Zepto, finds the best option, adds it to your cart
3. Checks current cart inventory
4. Schedules recurring orders ("order milk every Monday at 9 AM")
5. You tap Pay in the app when ready

All through Hermes Agent, OpenClaw, Claude Code, or any Python-capable agent.

---

## ✨ Features

- 🔍 **Search** any product — name, price, MRP, quantity at a glance
- 🛒 **Add to cart** and manage what's inside
- 📋 **List cart items** — see everything waiting to be checked out
- 🤖 **Agent-native** — `pip install zepto-cli`, one import in any skill
- 🔐 **One-time OTP login** — session persists for days
- 📍 **Auto-location** via geolocation (Mumbai default)
- 🧾 **CLI-native** — pipe, script, cron everything
- 📦 **Inventory-aware** — track what's in your cart, plan what's low

## 🚀 Human Quick Start

```bash
# 1. Install
pip install zepto-cli

# 2. Install browser driver
playwright install chromium

# 3. Login (one-time)
zepto login
# → Enter your phone number
# → Check SMS for OTP
# → Enter OTP
# ✅ Session saved for next time

# 4. Search products
zepto search "amul butter"

# 5. See your cart
zepto cart --list

# 6. Order multiple things at once
zepto order "brown bread, amul milk, eggs"
```

---

## 🤖 Agent Integration

Zepto CLI is designed as a **tool your agent calls**. One import, no ceremony.

### Hermes Agent (primary target)

Add it as a dependency, then use in any skill:

```python
# In a Hermes Agent skill:
from zepto_cli import ZeptoBot

def check_and_order(items: list[str]) -> str:
    """AI grocery manager — search, add, and report cart status."""
    bot = ZeptoBot().start()
    bot.ensure_session()

    # Check current cart first
    current = bot.get_cart_items()
    cart_report = f"🛒 Already in cart: {len(current)} items" if current else "🛒 Cart is empty"

    # Add requested items
    results = []
    for item in items:
        products = bot.search(item)
        if products:
            bot.add_to_cart(0)
            results.append(f"✅ {products[0]['name']} — {products[0]['price']}")
        else:
            results.append(f"❌ No results for '{item}'")

    # Final inventory
    total = bot.get_cart_count()
    bot.close()
    return "\n".join([cart_report] + results + [f"\n📦 Cart: {total} items"])
```

**Skill config** (`~/.hermes/skills/grocery/skill.md`):
```yaml
---
name: grocery
description: Household grocery management — search, stock, and order from Zepto
tools:
  - zepto-cli
---

Lets your agent manage kitchen inventory. Just say "add milk to the cart"
and it searches, finds the right product, and adds it.
```

**Cron — auto-reorder essentials:**
```yaml
# ~/.hermes/cron/groceries.yaml
name: Weekly grocery run
schedule: "0 9 * * 1"  # Every Monday 9 AM
prompt: >
  Check what's in my kitchen inventory and order weekly essentials:
  amul milk 1L, brown bread, eggs 12 pack, curd 500g
```

One message to Hermes: *"I'm running low on eggs and milk"* → bot searches, adds, tells you what's in cart.

### OpenClaw

As a standard Python package, OpenClaw can invoke it:

```python
# In any OpenClaw agent or extension:
from zepto_cli import ZeptoBot

bot = ZeptoBot().start()
bot.ensure_session()
products = bot.search("banana")
bot.add_to_cart(0)
bot.close()
```

Or from any shell step in an OpenClaw workflow:
```bash
zepto order "eggs, bread, milk"
```

### Any Python agent

```python
from zepto_cli import ZeptoBot
# Works with Claude Code, Codex, OpenCode, LangChain, CrewAI, etc.
```

---

## 📋 What Your Agent Can Do

| Action | Example | Agent Command |
|--------|---------|---------------|
| 🔍 **Search inventory** | "Is amul butter available?" | `zepto search "amul butter"` |
| 🛒 **Add to cart** | "Add milk to my cart" | `zepto add --search "milk"` |
| 📦 **Check cart** | "What's in my cart?" | `zepto cart --list` |
| 📝 **Order multiple** | "Restock the kitchen" | `zepto order "milk, eggs, bread, butter"` |
| 🔄 **Auto-refill** | "Order milk every Monday" | (via cron) |

## 🧩 API Reference

### `ZeptoBot`

| Method | Returns | Description |
|--------|---------|-------------|
| `.start()` | self | Launches browser + loads saved session |
| `.close()` | — | Saves session + closes browser |
| `.ensure_session()` | `True` / `False` | Check saved session |
| `.login(phone, otp=None)` | `True` / `"needs_otp"` / `False` | OTP login |
| `.enter_otp(otp)` | `True` / `False` | Enter 6-digit OTP |
| `.set_location(lat, lon)` | `True` / `False` | Change delivery area |
| `.search(query)` | `list[dict]` | Search → `[{name, price, mrp, quantity}]` |
| `.add_to_cart(index=0)` | `True` / `False` | Click ADD on Nth card |
| `.get_cart_count()` | `int` | Items in cart |
| `.get_cart_items()` | `list[dict]` | Cart details → `[{name, quantity, price}]` |
| `.go_home()` | — | Navigate to zepto.com |

### CLI

```
zepto login [--phone NUMBER]          One-time OTP login
zepto search <query> [--limit N]      Search products
zepto add [--search <query>] [--index N]  Add to cart
zepto cart [-l/--list]                Show cart count (--list for items)
zepto order "<item1>, <item2>, ..."   Full search + add flow
```

### Example: check cart contents

```bash
zepto cart
# 🛒 Cart: 3 items

zepto cart --list
# 🛒 Cart: 3 items
#
#   • Amul Taaza Milk 500 ml     ₹34
#   • Eggoz Farm Fresh Eggs      ₹76
#   • Britannia Whole Wheat Bread ₹54
```

---

## ⚙️ How It Works

1. **Playwright** launches a headless Chromium browser
2. Sets geolocation to Mumbai (override with `set_location()`)
3. Login sends an OTP — you enter it once
4. Cookies persist to `~/.zepto_session.json` — reused by your agent automatically
5. `search()` navigates to `zepto.com/search?query=...` and parses product cards
6. `add_to_cart()` clicks the ADD button on the target card
7. `get_cart_items()` reads the cart page to show current inventory

## 🛡️ Limitations

- **No auto-payment** — Zepto requires UPI PIN / Bank OTP
- **Selector fragility** — Zepto's CSS class names are hashed and change on deploy. The bot reads card text content as fallback
- **Rate limited** — CloudFront returns 429 if you search too fast (wait ~5s between calls)
- **India only** — Zepto only delivers in Indian cities

## 🏗️ Project Structure

```
zepto-cli/
├── zepto_cli/
│   ├── __init__.py     # Package init
│   ├── bot.py          # Core ZeptoBot class
│   └── cli.py          # CLI entry point (argparse)
├── scripts/demo.sh     # Session-aware demo
├── pyproject.toml      # Build config
└── README.md
```

## 🤝 Contributing

PRs welcome! The bot needs ongoing maintenance as Zepto updates their frontend. Key areas:

- **Selector updates** — if product cards change their HTML structure
- **New features** — checkout flow, order history, multi-location, multi-store
- **Stealth improvements** — better anti-detection for CloudFront

## ⚖️ Disclaimer

This project is **for educational purposes**. Zepto doesn't have a public API — this tool drives their public website like a human would using a browser. Use responsibly and in accordance with Zepto's terms of service.

## 📄 License

MIT
