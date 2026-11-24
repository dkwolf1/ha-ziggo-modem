"""Tests for exposing the bundled dashboard card."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.ziggo_modem import async_setup


async def test_setup_registers_the_card_when_frontend_is_loaded():
    hass = MagicMock()
    hass.config.components = {"frontend"}
    hass.http.async_register_static_paths = AsyncMock()

    with (
        patch(
            "custom_components.ziggo_modem.async_get_integration",
            new=AsyncMock(return_value=SimpleNamespace(version="1.7.0")),
        ) as load_integration,
        patch("custom_components.ziggo_modem.frontend.add_extra_js_url") as add_module,
    ):
        assert await async_setup(hass, {})

    load_integration.assert_awaited_once_with(hass, "ziggo_modem")
    hass.http.async_register_static_paths.assert_awaited_once()
    [static_path] = hass.http.async_register_static_paths.await_args.args[0]
    assert static_path.url_path == "/ziggo_modem"
    assert not static_path.cache_headers
    www = Path(static_path.path)
    assert (www / "ziggo-modem-card.js").is_file()
    assert (www / "ziggo-modem-device.webp").is_file()
    add_module.assert_called_once_with(
        hass, "/ziggo_modem/ziggo-modem-card.js?v=1.7.0"
    )


async def test_setup_skips_the_card_without_frontend():
    hass = MagicMock()
    hass.config.components = set()

    with (
        patch("custom_components.ziggo_modem.async_get_integration") as load_integration,
        patch("custom_components.ziggo_modem.frontend.add_extra_js_url") as add_module,
    ):
        assert await async_setup(hass, {})

    load_integration.assert_not_called()
    hass.http.async_register_static_paths.assert_not_called()
    add_module.assert_not_called()
