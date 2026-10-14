from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ZiggoModemApi
from .const import (
    CONF_HOST,
    CONF_LANGUAGE,
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_VERBOSE_DIAGNOSTICS,
    DEFAULT_LANGUAGE,
    DEFAULT_VERBOSE_DIAGNOSTICS,
    PLATFORMS,
)
from .coordinator import ZiggoModemDataUpdateCoordinator
from .data import ZiggoModemConfigEntry, ZiggoModemRuntimeData


async def async_migrate_entry(
    hass: HomeAssistant,
    entry: ZiggoModemConfigEntry,
) -> bool:
    """Move connection details from legacy options into entry data."""
    if entry.version != 1:
        return False

    data = dict(entry.data)
    options = dict(entry.options)
    options.setdefault(CONF_LANGUAGE, data.pop(CONF_LANGUAGE, DEFAULT_LANGUAGE))
    for key in (CONF_HOST, CONF_USERNAME, CONF_PASSWORD):
        if key in options:
            data[key] = options.pop(key)

    hass.config_entries.async_update_entry(
        entry, data=data, options=options, version=2
    )
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ZiggoModemConfigEntry,
) -> bool:
    """Set up Ziggo modem from a config entry."""
    host = entry.data[CONF_HOST]
    username = entry.data.get(CONF_USERNAME, "")
    password = entry.data[CONF_PASSWORD]

    api = ZiggoModemApi(
        host=host,
        username=username,
        password=password,
        session=async_get_clientsession(hass, verify_ssl=False),
    )

    coordinator = ZiggoModemDataUpdateCoordinator(hass, api, entry)

    entry.runtime_data = ZiggoModemRuntimeData(
        api=api,
        coordinator=coordinator,
        verbose_diagnostics=entry.options.get(
            CONF_VERBOSE_DIAGNOSTICS,
            DEFAULT_VERBOSE_DIAGNOSTICS,
        ),
        language=entry.options.get(CONF_LANGUAGE, DEFAULT_LANGUAGE),
    )

    try:
        await coordinator.async_config_entry_first_refresh()
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except Exception:
        await api.async_close()
        raise
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ZiggoModemConfigEntry,
) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        await entry.runtime_data.api.async_close()

    return unload_ok
