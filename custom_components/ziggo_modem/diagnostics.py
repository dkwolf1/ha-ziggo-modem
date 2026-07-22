"""Diagnostics support for the Ziggo Modem integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, DOMAIN
from .coordinator import ZiggoModemDataUpdateCoordinator

TO_REDACT = {
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
    "accessToken",
    "authorization",
    "bssid",
    "cmMacAddress",
    "hostName",
    "hostname",
    "ip",
    "ipAddress",
    "ipv4Address",
    "ipv6Address",
    "mac",
    "macAddress",
    "serial",
    "serialNo",
    "serialNumber",
    "ssid",
    "token",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return redacted diagnostics for a config entry."""
    entry_data = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
    coordinator: ZiggoModemDataUpdateCoordinator | None = entry_data.get(
        "coordinator"
    )

    diagnostics: dict[str, Any] = {
        "entry": {
            "version": entry.version,
            "minor_version": entry.minor_version,
            "data": async_redact_data(dict(entry.data), TO_REDACT),
            "options": async_redact_data(dict(entry.options), TO_REDACT),
        },
        "runtime": {
            "loaded": coordinator is not None,
        },
    }

    if coordinator is None:
        return diagnostics

    last_successful_update = coordinator.last_successful_update
    last_exception = coordinator.last_exception

    diagnostics["runtime"].update(
        {
            "last_update_success": coordinator.last_update_success,
            "last_exception_type": (
                type(last_exception).__name__ if last_exception else None
            ),
            "last_successful_update": (
                last_successful_update.isoformat()
                if last_successful_update is not None
                else None
            ),
            "consecutive_failures": coordinator.consecutive_failures,
            "max_failures": coordinator.max_failures,
            "update_interval_seconds": coordinator.update_interval_seconds,
            "endpoint_status": coordinator.endpoint_status,
            "paused": coordinator.is_paused,
            "verbose_diagnostics": coordinator.verbose_diagnostics,
            "language": coordinator.language,
        }
    )
    diagnostics["modem_data"] = async_redact_data(
        coordinator.data or {},
        TO_REDACT,
    )

    return diagnostics
