#!/usr/bin/env python3
"""
Zepto CLI — Order groceries from your terminal.

Usage:
    zepto login                        # One-time OTP login
    zepto search "amul milk"           # Search products
    zepto add 0                        # Add item at index 0 to cart
    zepto cart                         # Show cart
    zepto order "bread, eggs, milk"    # Full flow: search + add all

Stores:
    zepto (default)  → zepto.com
    blinkit          → blinkit.com
"""
import sys, argparse
from .bot import ZeptoBot, BlinkitBot, __version__

# ── Store registry ────────────────────────────────────────────
STORES = {
    "zepto": ZeptoBot,
    "blinkit": BlinkitBot,
}

def _resolve_bot(store_name: str, headless: bool = True):
    """Return an instance of the correct bot class for the given store name."""
    cls = STORES.get(store_name)
    if cls is None:
        available = ", ".join(STORES.keys())
        print(f"❌ Unknown store '{store_name}'. Available: {available}")
        sys.exit(1)
    return cls(headless=headless).start()


def cmd_login(args):
    bot = _resolve_bot(args.store)
    phone = args.phone or input("📱 Phone number: ")
    result = bot.login(phone)
    if result is True:
        print(f"✅ Already logged in ({args.store}, session active)")
    elif result == "needs_otp":
        otp = input("🔑 OTP sent to your phone. Enter OTP: ")
        if bot.enter_otp(otp):
            print(f"✅ Logged in ({args.store})!")
        else:
            print("❌ Login failed")
    else:
        print("❌ Login failed")
    bot.close()


def cmd_search(args):
    bot = _resolve_bot(args.store)
    if not bot.ensure_session():
        print(f"❌ No saved session for {args.store}. Run `zepto login --store {args.store}` first.")
        bot.close()
        return
    products = bot.search(args.query)
    if not products:
        print("❌ No products found")
        bot.close()
        return
    print(f"\n🔍 {args.store.title()} — Results for \"{args.query}\":")
    for i, p in enumerate(products[:args.limit]):
        mrp_str = f" (MRP {p['mrp']})" if p['mrp'] else ""
        print(f"  [{i}] {p['name'][:40]:40s} | {p['price']:6s}{mrp_str} | {p['quantity'][:20]}")
    bot.close()


def cmd_add(args):
    bot = _resolve_bot(args.store)
    if not bot.ensure_session():
        print(f"❌ No saved session for {args.store}. Run `zepto login --store {args.store}` first.")
        bot.close()
        return
    if args.search:
        products = bot.search(args.search)
        if not products:
            print("❌ No products found")
            bot.close()
            return
        print(f"Searching \"{args.search}\" on {args.store.title()}...")
        for i, p in enumerate(products[:5]):
            print(f"  [{i}] {p['name'][:35]:35s} | {p['price']}")
        idx = int(input(f"Which index to add? [0]: ") or "0")
        bot.add_to_cart(index=idx)
        print(f"✅ Added to cart! Cart count: {bot.get_cart_count()}")
    else:
        idx = args.index or 0
        bot.add_to_cart(index=idx)
        print(f"✅ Added to cart! Cart count: {bot.get_cart_count()}")
    bot.close()


def cmd_cart(args):
    bot = _resolve_bot(args.store)
    if not bot.ensure_session():
        print(f"❌ No saved session for {args.store}. Run `zepto login --store {args.store}` first.")
        bot.close()
        return
    count = bot.get_cart_count()
    store_label = args.store.title()
    print(f"🛒 {store_label} Cart: {count} item{'s' if count != 1 else ''}")

    if args.list:
        if count == 0:
            print("   (empty cart)")
        else:
            items = bot.get_cart_items()
            if items:
                print()
                for item in items:
                    line = f"   • {item['name']}"
                    if item.get('quantity'):
                        line += f"  ×{item['quantity']}"
                    if item.get('price'):
                        line += f"  {item['price']}"
                    print(line)
            else:
                print(f"   (could not parse items — open {args.store}.com to see details)")
    elif count > 0 and not args.list:
        print(f"   Use `zepto cart --list` to see items")

    bot.close()


def cmd_order(args):
    """One-shot: check session, search + add each item, report."""
    bot = _resolve_bot(args.store)
    if not bot.ensure_session():
        print(f"❌ No saved session for {args.store}. Run `zepto login --store {args.store}` first.")
        bot.close()
        return
    items = [i.strip() for i in args.items.split(",") if i.strip()]
    store_label = args.store.title()
    print(f"🛒 {store_label} — Ordering: {', '.join(items)}")
    for item in items:
        products = bot.search(item)
        if products:
            p = products[0]
            bot.add_to_cart(0)
            print(f"  ✅ {p['name'][:30]:30s} | {p['price']}")
        else:
            print(f"  ❌ No results for \"{item}\"")
    print(f"\n📦 {store_label} Cart total: {bot.get_cart_count()} items")
    bot.close()


def main():
    # Shared args: --store added to every subparser via parent
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("--store", choices=list(STORES.keys()), default="zepto",
                        help="Which store to use (default: zepto)")

    parser = argparse.ArgumentParser(
        description="🥬 Zepto CLI — Order groceries from your terminal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  zepto login                              # Login to Zepto
  zepto login --store blinkit              # Login to Blinkit
  zepto search "amul butter"               # Search Zepto
  zepto search "milk" --store blinkit       # Search Blinkit
  zepto add --search "eggs"                # Search + add on Zepto
  zepto order "bread, eggs, milk"          # Order from Zepto
  zepto order "milk" --store blinkit       # Order from Blinkit
  zepto cart --list                        # List cart items (Zepto)
  zepto cart --store blinkit --list        # List cart items (Blinkit)
        """
    )
    parser.add_argument("--version", action="version", version=f"zepto-cli v{__version__}")

    sub = parser.add_subparsers(dest="command")

    # login
    p_login = sub.add_parser("login", parents=[parent], help="One-time OTP login")
    p_login.add_argument("--phone", help="Phone number")

    # search
    p_search = sub.add_parser("search", parents=[parent], help="Search products")
    p_search.add_argument("query", help="Product to search")
    p_search.add_argument("--limit", type=int, default=10, help="Max results")

    # add
    p_add = sub.add_parser("add", parents=[parent], help="Add item to cart")
    p_add.add_argument("--index", type=int, default=0, help="Product card index")
    p_add.add_argument("--search", help="Search then add")

    # cart
    p_cart = sub.add_parser("cart", parents=[parent], help="Show cart count / items")
    p_cart.add_argument("--list", "-l", action="store_true", help="List all items in cart")

    # order
    p_order = sub.add_parser("order", parents=[parent], help="One-shot: search and add multiple items")
    p_order.add_argument("items", help="Comma-separated items (e.g. 'bread, eggs, milk')")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    commands = {
        "login": cmd_login,
        "search": cmd_search,
        "add": cmd_add,
        "cart": cmd_cart,
        "order": cmd_order,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
