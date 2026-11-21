"""Test fixtures for the Ziggo Modem integration."""

import pytest

from tests.ha_compat import HAS_OFFICIAL_TEST_PLUGIN

if not HAS_OFFICIAL_TEST_PLUGIN:
    pytest_plugins = ("pytest_homeassistant_custom_component",)

    @pytest.fixture(autouse=True)
    def enable_integration(enable_custom_integrations):
        """Allow the legacy test plugin to load this custom integration."""
