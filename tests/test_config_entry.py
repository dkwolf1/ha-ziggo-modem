"""Tests for config entry migration and coordinator startup."""

from datetime import UTC, datetime, timedelta
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
from custom_components.ziggo_modem.coordinator import (
    STALE_DATA_GRACE,
    ZiggoModemDataUpdateCoordinator,
)


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

    with (
        patch.object(coordinator._history_store, "async_save", new_callable=AsyncMock),
        pytest.raises(UpdateFailed),
    ):
        await coordinator._async_update_data()

    assert coordinator.data is None
    assert coordinator.consecutive_failures == 1


async def test_temporary_failure_uses_previous_data_until_grace_expires(hass):
    """A complete outage uses cached readings for at most ten minutes."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "192.168.178.1", CONF_PASSWORD: "secret"},
    )
    entry.add_to_hass(hass)
    entry.runtime_data = MagicMock(paused=False)
    api = MagicMock(host="192.168.178.1")
    coordinator = ZiggoModemDataUpdateCoordinator(hass, api, entry)
    previous = {"state": {"cablemodem": {"upTime": 42}}}
    api.last_endpoint_status = {"state": "ok"}
    api.async_get_data = AsyncMock(return_value=previous)

    with patch.object(coordinator._history_store, "async_save", new_callable=AsyncMock):
        coordinator.data = await coordinator._async_update_data()
        api.async_get_data = AsyncMock(side_effect=ZiggoModemApiError("offline"))
        for _ in range(3):
            assert await coordinator._async_update_data() is previous
        coordinator._last_successful_update = datetime.now(UTC) - STALE_DATA_GRACE
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()

    assert coordinator.consecutive_failures == 4


async def test_partial_endpoint_failure_keeps_cached_reading_briefly(hass):
    """One missing endpoint should not flicker after a successful reading."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "192.168.178.1", CONF_PASSWORD: "secret"},
    )
    entry.add_to_hass(hass)
    entry.runtime_data = MagicMock(paused=False)
    api = MagicMock(host="192.168.178.1")
    coordinator = ZiggoModemDataUpdateCoordinator(hass, api, entry)
    readings = {"state": {"cablemodem": {"upTime": 42}}, "downstream": {"value": 1}}

    async def fetch_data():
        return {
            "state": readings["state"],
            "downstream": (
                readings["downstream"]
                if api.last_endpoint_status["downstream"] == "ok"
                else {}
            ),
        }

    api.async_get_data = AsyncMock(side_effect=fetch_data)

    with patch.object(coordinator._history_store, "async_save", new_callable=AsyncMock):
        api.last_endpoint_status = {"state": "ok", "downstream": "ok"}
        coordinator.data = await coordinator._async_update_data()

        api.last_endpoint_status = {"state": "ok", "downstream": "failed"}
        for _ in range(2):
            coordinator.data = await coordinator._async_update_data()
            assert coordinator.data["downstream"] == readings["downstream"]
            assert coordinator.endpoints_available({"downstream"})

        coordinator.data = await coordinator._async_update_data()
        assert coordinator.endpoints_available({"downstream"})
        assert coordinator.endpoints_available({"state"})

        coordinator._last_endpoint_success["downstream"] = datetime.now(UTC) - (
            STALE_DATA_GRACE + timedelta(seconds=1)
        )
        assert not coordinator.endpoints_available({"downstream"})

        api.last_endpoint_status = {"state": "ok", "downstream": "ok"}
        coordinator.data = await coordinator._async_update_data()
        assert coordinator.endpoints_available({"downstream"})


async def test_complete_failure_keeps_cached_endpoints_until_grace_expires(hass):
    """Repeated total failures remain available only while data is fresh."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "192.168.178.1", CONF_PASSWORD: "secret"},
    )
    entry.add_to_hass(hass)
    entry.runtime_data = MagicMock(paused=False)
    api = MagicMock(host="192.168.178.1")
    coordinator = ZiggoModemDataUpdateCoordinator(hass, api, entry)
    readings = {"state": {"cablemodem": {"upTime": 42}}}
    api.async_get_data = AsyncMock(return_value=dict(readings))

    with patch.object(coordinator._history_store, "async_save", new_callable=AsyncMock):
        api.last_endpoint_status = {"state": "ok"}
        coordinator.data = await coordinator._async_update_data()

        api.last_endpoint_status = {"state": "failed"}
        api.async_get_data = AsyncMock(return_value={"state": {}})
        for _ in range(3):
            assert await coordinator._async_update_data() == readings
            assert coordinator.endpoints_available({"state"})

        coordinator._last_endpoint_success["state"] = datetime.now(UTC) - (
            STALE_DATA_GRACE + timedelta(seconds=1)
        )
        coordinator._last_successful_update = datetime.now(UTC) - STALE_DATA_GRACE
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()
        assert not coordinator.endpoints_available({"state"})
