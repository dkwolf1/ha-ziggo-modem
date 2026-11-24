from __future__ import annotations

from pathlib import Path

from homeassistant.components import frontend
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType
from homeassistant.loader import async_get_integration

from .api import ZiggoModemApi
from .const import (
    CONF_HOST,
    CONF_LANGUAGE,
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_VERBOSE_DIAGNOSTICS,
    DEFAULT_LANGUAGE,
    DEFAULT_VERBOSE_DIAGNOSTICS,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import ZiggoModemDataUpdateCoordinator
from .data import ZiggoModemConfigEntry, ZiggoModemRuntimeData

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, _config: ConfigType) -> bool:
    """Publish the bundled dashboard card once for this integration."""
    if frontend.DOMAIN not in hass.config.components:
        return True

    integration = await async_get_integration(hass, DOMAIN)
    url_path = f"/{DOMAIN}"
    await hass.http.async_register_static_paths(
        [StaticPathConfig(url_path, str(Path(__file__).parent / "www"), False)]
    )
    frontend.add_extra_js_url(
        hass, f"{url_path}/ziggo-modem-card.js?v={integration.version}"
    )
    return True


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
