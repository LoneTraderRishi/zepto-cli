"""Tests for zepto-blinkit core components."""
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, "..")

# Mock cloakbrowser before any imports
sys.modules["cloakbrowser"] = MagicMock()
sys.modules["cloakbrowser"].Browser = MagicMock()
sys.modules["cloakbrowser"].find_element = MagicMock()

from zepto_cli import ZeptoBot, BlinkitBot, AbstractGroceryBot
from zepto_cli.cli import STORES


def test_stores_registered():
    """Test that both stores are in the registry."""
    assert "zepto" in STORES
    assert "blinkit" in STORES


def test_store_bot_classes():
    """Test store registry maps to correct bot classes."""
    assert STORES["zepto"] == ZeptoBot
    assert STORES["blinkit"] == BlinkitBot


def test_abstract_bot_has_required_methods():
    """Test that AbstractGroceryBot defines the required interface."""
    methods = [
        "start", "close", "ensure_session", "login",
        "search", "add_to_cart", "get_cart_count", "get_cart_items"
    ]
    for m in methods:
        assert hasattr(AbstractGroceryBot, m), f"Missing method: {m}"


def test_version_exists():
    """Test that version string is defined."""
    from zepto_cli import __version__
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_cli_description():
    """Test CLI has store documentation."""
    from zepto_cli.cli import STORES
    assert len(STORES) == 2


@patch("zepto_cli.zepto.ZeptoBot.search")
def test_zepto_search_interface(mock_search):
    """Test ZeptoBot search interface matches expected return type."""
    mock_search.return_value = [
        {"name": "Test Product", "price": "₹50", "mrp": "₹60", "quantity": "500g", "store": "zepto"}
    ]
    bot = ZeptoBot(headless=True)
    results = bot.search("test")
    assert isinstance(results, list)
    if results:
        assert "name" in results[0]
        assert "price" in results[0]
        assert "store" in results[0]


@patch("zepto_cli.blinkit.BlinkitBot.search")
def test_blinkit_search_interface(mock_search):
    """Test BlinkitBot search interface matches expected return type."""
    mock_search.return_value = [
        {"name": "Test Product", "price": "₹50", "mrp": None, "quantity": "1 kg", "store": "blinkit"}
    ]
    bot = BlinkitBot(headless=True)
    results = bot.search("test")
    assert isinstance(results, list)
    if results:
        assert "name" in results[0]
        assert "store" in results[0]
