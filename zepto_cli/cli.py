#!/usr/bin/env python3
"""
Zepto CLI — Order groceries from Zepto from your terminal.

Usage:
    zepto login                # One-time OTP login
    zepto search "amul milk"   # Search products
    zepto add 0                # Add item at index 0 to cart
    zepto cart                 # Show cart
    zepto order "bread, eggs, milk"  # Full flow: search + add all
"""
import sys, os, argparse, json
from .bot import ZeptoBot, __version__


def cmd_login(args):
    bot = ZeptoBot().start()
    phone = args.phone or input("📱 Phone number: ")
    result = bot.login(phone)
    if result is True:
        print("✅ Already logged in (session active)")
    elif result == "needs_otp":
        otp = input("🔑 OTP sent to your phone. Enter OTP: ")
        if bot.enter_otp(otp):
            print("✅ Logged in!")
        else:
            print("❌ Login failed")
    bot.close()


def cmd_search(args):
    bot = ZeptoBot().start()
    if not bot.ensure_session():
        print("❌ No saved session. Run `zepto login` first.")
        bot.close()
        return
    products = bot.search(args.query)
    if not products:
        print("❌ No products found")
        bot.close()
        return
    print(f"\n🔍 Results for \"{args.query}\":")
    for i, p in enumerate(products[:args.limit]):
        mrp_str = f" (MRP {p['mrp']})" if p['mrp'] else ""
        print(f"  [{i}] {p['name'][:40]:40s} | {p['price']:6s}{mrp_str} | {p['quantity'][:20]}")
    bot.close()


def cmd_add(args):
    bot = ZeptoBot().start()
    if not bot.ensure_session():
        print("❌ No saved session. Run `zepto login` first.")
        bot.close()
        return
    if args.search:
        # Search first, then add
        products = bot.search(args.search)
        if not products:
            print("❌ No products found")
            bot.close()
            return
        print(f"Searching \"{args.search}\"...")
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
    bot = ZeptoBot().start()
    if not bot.ensure_session():
        print("❌ No saved session. Run `zepto login` first.")
        bot.close()
        return
    count = bot.get_cart_count()
    print(f"🛒 Cart: {count} item{'s' if count != 1 else ''}")
    if count > 0:
        print("Open https://www.zepto.com in your browser to see details.")
    bot.close()


def cmd_order(args):
    """One-shot: login, add items, show cart result."""
    bot = ZeptoBot().start()
    if not bot.ensure_session():
        print("❌ No saved session. Run `zepto login` first.")
        bot.close()
        return
    items = [i.strip() for i in args.items.split(",") if i.strip()]
    print(f"🛒 Ordering: {', '.join(items)}")
    for item in items:
        products = bot.search(item)
        if products:
            p = products[0]
            bot.add_to_cart(0)
            print(f"  ✅ {p['name'][:30]:30s} | {p['price']}")
        else:
            print(f"  ❌ No results for \"{item}\"")
    print(f"\n📦 Cart total: {bot.get_cart_count()} items")
    bot.close()


def main():
    parser = argparse.ArgumentParser(
        description="🥬 Zepto CLI — Order groceries from your terminal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  zepto login                         # Login with OTP
  zepto search "amul butter"          # Search products
  zepto search "milk" --limit 5       # Show first 5 results
  zepto add --search "eggs"           # Search + add to cart
  zepto order "bread, eggs, milk"     # Full order flow
  zepto cart                          # Check cart
        """
    )
    parser.add_argument("--version", action="version", version=f"zepto-cli v{__version__}")

    sub = parser.add_subparsers(dest="command")

    # login
    p_login = sub.add_parser("login", help="One-time OTP login")
    p_login.add_argument("--phone", help="Phone number")

    # search
    p_search = sub.add_parser("search", help="Search products")
    p_search.add_argument("query", help="Product to search")
    p_search.add_argument("--limit", type=int, default=10, help="Max results")

    # add
    p_add = sub.add_parser("add", help="Add item to cart")
    p_add.add_argument("--index", type=int, default=0, help="Product card index")
    p_add.add_argument("--search", help="Search then add")

    # cart
    sub.add_parser("cart", help="Show cart count")

    # order
    p_order = sub.add_parser("order", help="One-shot: search and add multiple items")
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
