from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ZiggoModemApi, ZiggoModemApiError, ZiggoModemAuthError
from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ZiggoModemDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for Ziggo modem data."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: ZiggoModemApi,
        entry: ConfigEntry,
    ) -> None:
        self.entry = entry

        scan_interval = entry.options.get(
            CONF_SCAN_INTERVAL,
            DEFAULT_SCAN_INTERVAL,
        )

        super().__init__(
            hass,
            _LOGGER,
            name="ziggo_modem",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from modem unless paused."""
        entry_data = self.hass.data[DOMAIN][self.entry.entry_id]

        if entry_data.get("paused", False):
            _LOGGER.debug("Ziggo modem integration is paused; skipping update")
            return self.data if self.data is not None else {}

        try:
            return await self.api.async_get_data()
        except ZiggoModemAuthError as err:
            raise UpdateFailed(f"Authentication failed: {err}") from err
        except ZiggoModemApiError as err:
            raise UpdateFailed(f"API error: {err}") from err
