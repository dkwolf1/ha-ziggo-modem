"""Runtime data types for the Ziggo Modem integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry

from .const import DEFAULT_LANGUAGE

if TYPE_CHECKING:
    from .api import ZiggoModemApi
    from .coordinator import ZiggoModemDataUpdateCoordinator


@dataclass
class ZiggoModemRuntimeData:
    """Runtime data for a loaded Ziggo Modem config entry."""

    api: ZiggoModemApi
    coordinator: ZiggoModemDataUpdateCoordinator
    paused: bool = False
    verbose_diagnostics: bool = False
    language: str = DEFAULT_LANGUAGE


type ZiggoModemConfigEntry = ConfigEntry[ZiggoModemRuntimeData]
