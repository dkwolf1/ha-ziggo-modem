"""Test fixtures for the Ziggo Modem integration."""

import pytest

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def enable_integration(enable_custom_integrations):
    """Allow Home Assistant to load this custom integration in tests."""
