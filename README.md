<div align="center">
  <h1>🥬 Zepto CLI</h1>
  <p><strong>Order groceries from Zepto — from your terminal, your scripts, or your AI agent.</strong></p>
  <p>
    <a href="#features"><img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fapi.github.com%2Frepos%2FLoneTraderRishi%2Fzepto-cli&query=stargazers_count&style=for-the-badge&logo=github&label=stars&color=yellow" alt="Stars"></a>
    <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python">
    <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="MIT">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen?style=for-the-badge" alt="PRs Welcome">
  </p>
  <br>
</div>

A Python CLI + library that drives **zepto.com** to search groceries, check prices, and add them to your cart — from your terminal, or imported directly into any AI agent workflow.

Uses **Playwright** under the hood. One-time OTP login, persistent sessions.

> ⚠️ **Payment is manual** — the bot gets your cart ready and you tap Pay on your phone. Zepto requires UPI PIN / Bank OTP which can't be automated.

---

## ✨ Features

- 🔍 **Search** any product — see price, MRP, and quantity
- 🛒 **Add to cart** with one command
- 🔐 **One-time OTP login** — session persists for days
- 📍 **Auto-location** via geolocation (Mumbai default)
- 🧾 **CLI-native** — pipe, script, cron everything
- 🤖 **Agent-native** — `pip install` and import from Hermes Agent, OpenClaw, browser-use, or any Python-based AI workflow

## 🚀 Quick Start

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

# 5. Add to cart
zepto add --search "eggs"

# 6. Order multiple items at once
zepto order "brown bread, amul milk, eggs"
```

---

## 🤖 Agent Integration

Zepto CLI is a `pip install`-able Python package. Any agent framework that can run Python can use it — either via the CLI (`subprocess`) or by importing `ZeptoBot` directly.

### Hermes Agent

Add `zepto-cli` to your Hermes Agent's config, then use it as a tool in any skill:

```python
# In a Hermes Agent skill (.py block):
from zepto_cli import ZeptoBot

def order_groceries(items: list[str]) -> str:
    """Search and add each item to your Zepto cart."""
    bot = ZeptoBot().start()
    bot.ensure_session()
    results = []
    for item in items:
        products = bot.search(item)
        if products:
            bot.add_to_cart(0)
            results.append(f"✅ {products[0]['name']} — {products[0]['price']}")
        else:
            results.append(f"❌ No results for '{item}'")
    count = bot.get_cart_count()
    bot.close()
    results.append(f"\n📦 Cart: {count} items — pay in the Zepto app!")
    return "\n".join(results)
```

Skill config (`~/.hermes/skills/zepto/skill.md`):
```yaml
---
name: zepto
description: Order groceries from Zepto
tools:
  - zepto-cli
---

Provides ZeptoBot for searching and ordering groceries.
```

### OpenClaw

Zepto CLI is a standard Python package — OpenClaw can invoke it via any of its supported methods:

**As a CLI command** — just `zepto search "milk"` from any OpenClaw agent or task:
```bash
# In any OpenClaw agent config or step:
# Simply call the CLI:
zepto order "eggs, bread, milk"
```

**As a Python import** — use `ZeptoBot` from an OpenClaw extension:
```python
# In any OpenClaw Python extension or agent:
from zepto_cli import ZeptoBot

bot = ZeptoBot().start()
bot.ensure_session()
```

**Via subprocess** — non-Python agents can call the CLI and parse output.

### browser-use

```python
from zepto_cli import ZeptoBot

bot = ZeptoBot().start()
bot.ensure_session()
products = bot.search("banana")
if products:
    bot.add_to_cart(0)
bot.close()
```

### Any Python agent

Same pattern — `pip install zepto-cli`, `from zepto_cli import ZeptoBot`. Works with Claude Code, Codex, OpenCode, LangChain, CrewAI, or any framework that can call Python functions.

---

## 📦 Examples

### Compare prices
```bash
for item in "amul butter" "nandini butter" "mother dairy butter"; do
    echo "=== $item ==="
    zepto search "$item" --limit 3
done
```

### Weekly grocery run
```bash
zepto order "brown bread, whole wheat bread, amul milk 1L, eggs 12, apple 1kg, banana, curd, paneer"
```

### From a cron job
```bash
# Daily 9 AM: order milk and bread
0 9 * * * zepto order "amul milk 1L, brown bread"
```

---

## 🧩 API Reference

### `ZeptoBot`

| Method | Returns | Description |
|--------|---------|-------------|
| `.start()` | self | Launches browser + loads saved session |
| `.close()` | — | Saves session + closes browser |
| `.ensure_session()` | `True` / `False` | Check saved session, don't attempt login |
| `.login(phone, otp=None)` | `True` / `"needs_otp"` / `False` | OTP login flow |
| `.enter_otp(otp)` | `True` / `False` | Enter 6-digit OTP |
| `.set_location(lat, lon)` | `True` / `False` | Change delivery area |
| `.search(query)` | `list[dict]` | Search products → `[{name, price, mrp, quantity}]` |
| `.add_to_cart(index=0)` | `True` / `False` | Click ADD on Nth card |
| `.get_cart_count()` | `int` | Items in cart |
| `.go_home()` | — | Navigate to zepto.com |

### CLI

```
zepto login [--phone NUMBER]          One-time OTP login
zepto search <query> [--limit N]      Search products
zepto add [--search <query>] [--index N]  Add to cart
zepto cart                            Show cart count
zepto order "<item1>, <item2>, ..."   Full search + add flow
```

---

## ⚙️ How It Works

1. **Playwright** launches a headless Chromium browser
2. Sets geolocation to Mumbai (override with `set_location()`)
3. Login sends an OTP — you enter it once
4. Cookies persist to `~/.zepto_session.json` — reused automatically
5. `search()` navigates to `zepto.com/search?query=...` and parses product cards
6. `add_to_cart()` clicks the ADD button on the target card

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
├── pyproject.toml      # Build config
└── README.md
```

## 🤝 Contributing

PRs welcome! The bot needs ongoing maintenance as Zepto updates their frontend. Key areas:

- **Selector updates** — if product cards change their HTML structure
- **New features** — checkout flow, order history, multi-location
- **Stealth improvements** — better anti-detection for CloudFront

## ⚖️ Disclaimer

This project is **for educational purposes**. Zepto doesn't have a public API — this tool drives their public website like a human would using a browser. Use responsibly and in accordance with Zepto's terms of service.

## 📄 License

MIT
