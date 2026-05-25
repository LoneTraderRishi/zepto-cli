<div align="center">
  <h1>🥬 Zepto Blinkit</h1>
  <p><strong>Your AI agent's grocery arm — search, manage, and order from Zepto & Blinkit (India only)</strong></p>
  <p>
    <a href="#features"><img src="https://img.shields.io/github/stars/LoneTraderRishi/zepto-blinkit?style=social" alt="Stars"></a>
    <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python">
    <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="MIT">
    <img src="https://img.shields.io/github/actions/workflow/status/LoneTraderRishi/zepto-blinkit/ci.yml?style=for-the-badge" alt="CI">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen?style=for-the-badge" alt="PRs Welcome">
  </p>
  <p>
    <a href="#features">Features</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#agent-integration">Agent Integration</a> •
    <a href="#api">API</a>
  </p>
  <br>
</div>

Give your AI agent the power to search **Zepto** or **Blinkit**, manage your cart, and keep your kitchen stocked — all from a text message, a cron job, or a skill. Same CLI, same API, one `--store` flag to switch.

Uses **CloakBrowser** under the hood — a stealth Chromium binary with 57 C++ patch levels that passes bot detection. One-time OTP login, persistent sessions per store. No API keys needed — your agent drives the store like a human.

> ⚠️ **India only.** Zepto and Blinkit only deliver in Indian cities. Does NOT work outside India.
> ⚠️ **Payment is manual** — the bot gets your cart ready and you tap Pay on your phone. UPI PIN / Bank OTP can't be automated.

---

## 🧠 What This Is

This isn't just a CLI. It's an **AI-managed grocery inventory system** — a tool your agent uses to handle your household essentials across **both Zepto and Blinkit**.

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

- 🏪 **Dual-store** — Zepto and Blinkit supported, same API for both
- 🔍 **Search** any product — name, price, MRP, quantity
- 🛒 **Add to cart** and manage what's inside
- 📋 **List cart items** — see everything waiting to be checked out
- 🤖 **Agent-native** — `pip install zepto-blinkit`, one import in any skill
- 🔐 **One-time OTP login** — session persists for days per store
- 📍 **Auto-location** via geolocation (Mumbai default)
- 🧾 **CLI-native** — pipe, script, cron everything
- 📦 **Inventory-aware** — track what's in your cart, plan what's low

---

## 🎥 Demo

![Demo](screenshots/demo.gif)

---

## 🚀 Quick Start

```bash
# Install
pip install zepto-blinkit

# Login (one-time per store)
zepto login                              # Zepto (default)
zepto login --store blinkit              # Blinkit (separate session)
zb login                                 # Shorthand

# Search
zepto search "amul butter"               # Zepto
zepto search "amul butter" --store blinkit  # Blinkit

# Order multiple things
zepto order "brown bread, amul milk, eggs"  # Zepto
zb order "brown bread, amul milk" --store blinkit  # Blinkit shorthand

# Check cart
zepto cart --list                              # Zepto
zepto cart --store blinkit --list              # Blinkit
```

---

## 🤖 Agent Integration

```python
from zepto_cli import ZeptoBot, BlinkitBot

# Zepto
bot = ZeptoBot().start()
bot.ensure_session()
products = bot.search("amul butter")
bot.add_to_cart(0)
bot.close()

# Blinkit — same API, just different class
bot = BlinkitBot().start()
bot.ensure_session()
products = bot.search("banana")
bot.add_to_cart(0)
bot.close()
```

### CLI Reference

```
zepto login [--phone NUMBER] [--store STORE]
zepto search <query> [--limit N] [--store STORE]
zepto add [--search <query>] [--index N] [--store STORE]
zepto cart [-l/--list] [--store STORE]
zepto order "<item1>, <item2>, ..." [--store STORE]

Shorthand: replace `zepto` with `zb`
```

### Bot API

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

---

## ⚙️ How It Works

1. **CloakBrowser** launches a stealth Chromium (57 C++ patches, bypasses bot detection)
2. Sets geolocation to Mumbai (override with `set_location()`)
3. Login sends an OTP — you enter it once per store
4. Cookies persist to `~/.<store>_session.json` — reused by your agent automatically
5. `search()` navigates to the store's search page and parses product cards
6. `add_to_cart()` clicks the ADD button on the target card
7. `get_cart_items()` reads the cart page to show current inventory
8. `--store` flag selects which store to use — same API, different selectors

---

## 🛡️ Limitations

- **No auto-payment** — requires UPI PIN / Bank OTP
- **Blinkit WAF** — Blinkit has stronger anti-bot protection
- **Selector fragility** — store CSS class names change on deploy
- **Rate limited** — CloudFront returns 429 if you search too fast (~5s between calls)
- **India only** — Zepto and Blinkit only deliver in Indian cities

---

## 🧪 Tests

```bash
pip install pytest pytest-asyncio httpx
python -m pytest tests/ -v
```

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](.github/CONTRIBUTING.md).

- **New stores** — subclass `AbstractGroceryBot`, add to `STORES` registry
- **Selector updates** — product cards change HTML structure sometimes
- **New features** — checkout flow, order history, multi-location

---

## 🏗️ Project Structure

```
zepto-blinkit/
├── zepto_cli/
│   ├── __init__.py     # Package exports (ZeptoBot, BlinkitBot)
│   ├── base.py         # AbstractGroceryBot base class
│   ├── zepto.py        # ZeptoBot implementation
│   ├── blinkit.py      # BlinkitBot implementation
│   ├── bot.py          # Backwards-compat re-exports
│   └── cli.py          # CLI with --store flag
├── tests/
│   ├── __init__.py
│   └── test_core.py
├── scripts/demo.sh
├── .github/            # CI, issue templates, etc.
├── pyproject.toml
└── README.md
```

## 📄 License

MIT
