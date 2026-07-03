from __future__ import annotations

from datetime import UTC, datetime, timedelta
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
        self.api = api

        self._consecutive_failures = 0
        self._max_failures = 3
        self._last_successful_update: datetime | None = None
        self._endpoint_status: dict[str, str] = {}

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

    @property
    def consecutive_failures(self) -> int:
        """Return the number of consecutive update failures."""
        return self._consecutive_failures

    @property
    def max_failures(self) -> int:
        """Return the maximum tolerated consecutive update failures."""
        return self._max_failures

    @property
    def update_interval_seconds(self) -> int | None:
        """Return the configured update interval in seconds."""
        if self.update_interval is None:
            return None
        return int(self.update_interval.total_seconds())

    @property
    def last_successful_update(self) -> datetime | None:
        """Return when data was last fetched successfully."""
        return self._last_successful_update

    @property
    def endpoint_status(self) -> dict[str, str]:
        """Return the status of the most recent endpoint fetch."""
        return self._endpoint_status

    @property
    def is_paused(self) -> bool:
        """Return whether the integration is currently paused."""
        entry_data = self.hass.data.get(DOMAIN, {}).get(self.entry.entry_id, {})
        return bool(entry_data.get("paused", False))

    @property
    def verbose_diagnostics(self) -> bool:
        """Return whether verbose diagnostic attributes are enabled."""
        entry_data = self.hass.data.get(DOMAIN, {}).get(self.entry.entry_id, {})
        return bool(entry_data.get("verbose_diagnostics", False))

    @property
    def api_status(self) -> str:
        """Return a human-readable API status."""
        if self.is_paused:
            return "Gepauzeerd"

        if self._consecutive_failures == 0:
            return "OK"

        if self._consecutive_failures < self._max_failures:
            return "Tijdelijke fouten"

        return "Instabiel"

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from modem unless paused."""
        if self.is_paused:
            _LOGGER.debug("Ziggo modem integration is paused; skipping update")
            return self.data if self.data is not None else {}

        try:
            data = await self.api.async_get_data()
            self._consecutive_failures = 0
            self._last_successful_update = datetime.now(UTC)
            self._endpoint_status = self.api.last_endpoint_status
            return data

        except ZiggoModemAuthError as err:
            raise UpdateFailed(f"Authentication failed: {err}") from err

        except ZiggoModemApiError as err:
            self._consecutive_failures += 1

            _LOGGER.warning(
                "Ziggo modem fetch failed for %s (%s/%s): %s",
                self.api.host,
                self._consecutive_failures,
                self._max_failures,
                err,
            )

            if self._consecutive_failures < self._max_failures:
                _LOGGER.debug("Using last known data due to temporary failure")
                return self.data if self.data is not None else {}

            raise UpdateFailed(
                f"API error after {self._max_failures} retries: {err}"
            ) from err
