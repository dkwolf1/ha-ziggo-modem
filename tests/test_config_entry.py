"""Tests for config entry migration and coordinator startup."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ziggo_modem import async_migrate_entry
from custom_components.ziggo_modem.api import ZiggoModemApiError
from custom_components.ziggo_modem.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
    DOMAIN,
)
from custom_components.ziggo_modem.coordinator import ZiggoModemDataUpdateCoordinator


async def test_migration_preserves_effective_connection_settings(hass):
    """Legacy options take precedence and move to entry data."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=1,
        data={
            CONF_HOST: "192.168.100.1",
            CONF_PASSWORD: "old",
            "language": "en",
        },
        options={
            CONF_HOST: "192.168.178.1",
            CONF_USERNAME: "admin",
            CONF_PASSWORD: "new",
            "scan_interval": 90,
        },
    )
    entry.add_to_hass(hass)

    assert await async_migrate_entry(hass, entry)
    assert entry.version == 2
    assert entry.data[CONF_HOST] == "192.168.178.1"
    assert entry.data[CONF_USERNAME] == "admin"
    assert entry.data[CONF_PASSWORD] == "new"
    assert entry.options == {"scan_interval": 90, "language": "en"}


async def test_first_complete_failure_does_not_create_empty_data(hass):
    """A modem that never answered must fail its first refresh."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "192.168.178.1", CONF_PASSWORD: "secret"},
    )
    entry.add_to_hass(hass)
    entry.runtime_data = MagicMock(paused=False)
    api = MagicMock(host="192.168.178.1")
    api.async_get_data = AsyncMock(side_effect=ZiggoModemApiError("offline"))
    coordinator = ZiggoModemDataUpdateCoordinator(hass, api, entry)

    with patch.object(coordinator._history_store, "async_save", new_callable=AsyncMock):
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()

    assert coordinator.data is None
    assert coordinator.consecutive_failures == 1


async def test_temporary_failure_uses_previous_data_then_becomes_unavailable(hass):
    """Existing readings survive two failures, but not a sustained outage."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "192.168.178.1", CONF_PASSWORD: "secret"},
    )
    entry.add_to_hass(hass)
    entry.runtime_data = MagicMock(paused=False)
    api = MagicMock(host="192.168.178.1")
    api.async_get_data = AsyncMock(side_effect=ZiggoModemApiError("offline"))
    coordinator = ZiggoModemDataUpdateCoordinator(hass, api, entry)
    previous = {"state": {"cablemodem": {"upTime": 42}}}
    coordinator.data = previous

    with patch.object(coordinator._history_store, "async_save", new_callable=AsyncMock):
        assert await coordinator._async_update_data() is previous
        assert await coordinator._async_update_data() is previous
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()

    assert coordinator.consecutive_failures == 3
