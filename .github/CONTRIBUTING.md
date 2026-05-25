# Contributing to zepto-blinkit

## Development Setup
```bash
git clone https://github.com/LoneTraderRishi/zepto-blinkit.git
cd zepto-blinkit
pip install -e .
pip install pytest pytest-asyncio httpx
```

## Adding a New Store
1. Subclass `AbstractGroceryBot` in a new file
2. Add selectors for the store's product cards, cart page, and login flow
3. Register in `zepto_cli/cli.py` `STORES` dict
4. Test with the actual store

## Code Style
- Python: PEP 8
- Selector fallbacks: prefer text content parsing over fragile class names
