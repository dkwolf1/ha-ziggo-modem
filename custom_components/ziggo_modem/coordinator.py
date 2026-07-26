from __future__ import annotations

from datetime import UTC, datetime, timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ZiggoModemApi, ZiggoModemApiError, ZiggoModemAuthError
from .const import (
    CONF_DOWNSTREAM_POWER_MAX,
    CONF_DOWNSTREAM_POWER_MIN,
    CONF_DOWNSTREAM_SNR_MIN,
    CONF_LANGUAGE,
    CONF_SCAN_INTERVAL,
    CONF_UPSTREAM_POWER_MAX,
    CONF_VERBOSE_DIAGNOSTICS,
    DEFAULT_DOWNSTREAM_POWER_MAX,
    DEFAULT_DOWNSTREAM_POWER_MIN,
    DEFAULT_DOWNSTREAM_SNR_MIN,
    DEFAULT_LANGUAGE,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_UPSTREAM_POWER_MAX,
    DOMAIN,
)
from .i18n import translate

_LOGGER = logging.getLogger(__name__)

HISTORY_STORAGE_VERSION = 1
HISTORY_DEFAULTS: dict[str, Any] = {
    "connection_interruptions": 0,
    "failed_updates": 0,
    "connection_available": None,
    "last_connection_interruption": None,
    "last_connection_recovery": None,
    "last_failed_update": None,
    "last_modem_restart": None,
}


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
        self._history = dict(HISTORY_DEFAULTS)
        self._history_store = Store[dict[str, Any]](
            hass,
            HISTORY_STORAGE_VERSION,
            f"{DOMAIN}.history.{entry.entry_id}",
        )

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
    def signal_thresholds(self) -> dict[str, float]:
        """Return the configured DOCSIS signal thresholds."""
        return {
            CONF_DOWNSTREAM_POWER_MIN: float(
                self.entry.options.get(
                    CONF_DOWNSTREAM_POWER_MIN,
                    DEFAULT_DOWNSTREAM_POWER_MIN,
                )
            ),
            CONF_DOWNSTREAM_POWER_MAX: float(
                self.entry.options.get(
                    CONF_DOWNSTREAM_POWER_MAX,
                    DEFAULT_DOWNSTREAM_POWER_MAX,
                )
            ),
            CONF_DOWNSTREAM_SNR_MIN: float(
                self.entry.options.get(
                    CONF_DOWNSTREAM_SNR_MIN,
                    DEFAULT_DOWNSTREAM_SNR_MIN,
                )
            ),
            CONF_UPSTREAM_POWER_MAX: float(
                self.entry.options.get(
                    CONF_UPSTREAM_POWER_MAX,
                    DEFAULT_UPSTREAM_POWER_MAX,
                )
            ),
        }

    @property
    def problem_history(self) -> dict[str, Any]:
        """Return a copy of the persistent problem history."""
        return dict(self._history)

    @property
    def connection_interruptions(self) -> int:
        """Return the number of detected connection interruptions."""
        return int(self._history["connection_interruptions"])

    @property
    def failed_updates(self) -> int:
        """Return the number of completely failed modem updates."""
        return int(self._history["failed_updates"])

    @property
    def last_modem_restart(self) -> datetime | None:
        """Return the estimated time of the last modem restart."""
        return self._history_datetime("last_modem_restart")

    @property
    def is_paused(self) -> bool:
        """Return whether the integration is currently paused."""
        entry_data = self.hass.data.get(DOMAIN, {}).get(self.entry.entry_id, {})
        return bool(entry_data.get("paused", False))

    @property
    def verbose_diagnostics(self) -> bool:
        """Return whether verbose diagnostic attributes are enabled."""
        entry_data = self.hass.data.get(DOMAIN, {}).get(self.entry.entry_id, {})
        return bool(entry_data.get(CONF_VERBOSE_DIAGNOSTICS, False))

    @property
    def language(self) -> str:
        """Return the configured integration language."""
        entry_data = self.hass.data.get(DOMAIN, {}).get(self.entry.entry_id, {})
        return entry_data.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)

    def translate(self, key: str) -> str:
        """Translate a key using the configured integration language."""
        return translate(self.language, key)

    @property
    def api_status(self) -> str:
        """Return a human-readable API status."""
        if self.is_paused:
            return self.translate("api_status.paused")

        if self._consecutive_failures == 0:
            return self.translate("api_status.ok")

        if self._consecutive_failures < self._max_failures:
            return self.translate("api_status.temporary_errors")

        return self.translate("api_status.unstable")

    async def _async_setup(self) -> None:
        """Load persistent history before the first coordinator update."""
        stored_history = await self._history_store.async_load()
        if not isinstance(stored_history, dict):
            return

        for key in HISTORY_DEFAULTS:
            if key in stored_history:
                self._history[key] = stored_history[key]

        for key in ("connection_interruptions", "failed_updates"):
            try:
                self._history[key] = max(0, int(self._history[key]))
            except (TypeError, ValueError):
                self._history[key] = 0

        if not isinstance(self._history["connection_available"], bool):
            self._history["connection_available"] = None

        for key in (
            "last_connection_interruption",
            "last_connection_recovery",
            "last_failed_update",
            "last_modem_restart",
        ):
            if not isinstance(self._history[key], str):
                self._history[key] = None

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from modem unless paused."""
        if self.is_paused:
            _LOGGER.debug("Ziggo modem integration is paused; skipping update")
            return self.data if self.data is not None else {}

        try:
            data = await self.api.async_get_data()
            now = datetime.now(UTC)
            self._endpoint_status = self.api.last_endpoint_status

            if self._endpoint_status and all(
                status == "failed" for status in self._endpoint_status.values()
            ):
                raise ZiggoModemApiError("All modem endpoints failed")

            self._consecutive_failures = 0
            self._last_successful_update = now
            await self._async_record_success(data, now)
            return data

        except ZiggoModemAuthError as err:
            await self._async_record_failed_update(connection_unavailable=False)
            raise UpdateFailed(f"Authentication failed: {err}") from err

        except ZiggoModemApiError as err:
            self._consecutive_failures += 1
            await self._async_record_failed_update()

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

    async def _async_record_success(
        self,
        data: dict[str, Any],
        now: datetime,
    ) -> None:
        """Record recovery and estimate the most recent modem restart."""
        changed = False
        connection_available = self._history["connection_available"]

        if connection_available is False:
            self._history["last_connection_recovery"] = now.isoformat()
            changed = True

        if connection_available is not True:
            self._history["connection_available"] = True
            changed = True

        uptime = data.get("state", {}).get("cablemodem", {}).get("upTime")
        try:
            uptime_seconds = float(uptime)
        except (TypeError, ValueError):
            uptime_seconds = -1

        if uptime_seconds >= 0:
            estimated_restart = now - timedelta(seconds=uptime_seconds)
            previous_restart = self._history_datetime("last_modem_restart")

            if (
                previous_restart is None
                or estimated_restart > previous_restart + timedelta(minutes=5)
            ):
                self._history["last_modem_restart"] = estimated_restart.isoformat()
                changed = True

        if changed:
            await self._history_store.async_save(self._history)

    async def _async_record_failed_update(
        self,
        *,
        connection_unavailable: bool = True,
    ) -> None:
        """Record a fully failed update and a new interruption transition."""
        now = datetime.now(UTC)
        self._history["failed_updates"] += 1
        self._history["last_failed_update"] = now.isoformat()

        if (
            connection_unavailable
            and self._history["connection_available"] is True
        ):
            self._history["connection_interruptions"] += 1
            self._history["last_connection_interruption"] = now.isoformat()

        if connection_unavailable:
            self._history["connection_available"] = False
        await self._history_store.async_save(self._history)

    def _history_datetime(self, key: str) -> datetime | None:
        """Return a stored ISO timestamp as a datetime."""
        value = self._history.get(key)
        if not isinstance(value, str):
            return None

        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
