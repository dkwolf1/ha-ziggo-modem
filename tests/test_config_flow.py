"""Tests for changing the modem address without replacing an entry."""

from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.config_entries import SOURCE_RECONFIGURE
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ziggo_modem.const import (
    CONF_HOST,
    CONF_PASSWORD,
    DOMAIN,
)


async def test_reconfigure_updates_existing_entry(hass):
    """A new address keeps the entry, options and entity IDs intact."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=2,
        unique_id="192.168.100.1",
        data={CONF_HOST: "192.168.100.1", CONF_PASSWORD: "secret"},
        options={"scan_interval": 90},
    )
    entry.add_to_hass(hass)
    api = MagicMock()
    api.async_login = AsyncMock()
    api.async_close = AsyncMock()

    with (
        patch(
            "custom_components.ziggo_modem.config_flow._create_api",
            return_value=api,
        ),
        patch.object(hass.config_entries, "async_reload", new_callable=AsyncMock),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_RECONFIGURE, "entry_id": entry.entry_id},
        )
        assert result["type"] is FlowResultType.FORM

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={CONF_HOST: "192.168.178.1"},
        )

    assert result["type"] is FlowResultType.ABORT
    assert entry.data[CONF_HOST] == "192.168.178.1"
    assert entry.unique_id == "192.168.178.1"
    assert entry.options == {"scan_interval": 90}
