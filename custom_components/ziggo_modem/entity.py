from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from homeassistant.helpers.device_registry import (
    CONNECTION_NETWORK_MAC,
    DeviceInfo,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ZiggoModemDataUpdateCoordinator


def _first_text(
    sources: Sequence[Mapping[str, Any]],
    keys: Sequence[str],
) -> str | None:
    """Return the first non-empty device information value."""
    for source in sources:
        for key in keys:
            value = source.get(key)
            if value is not None and str(value).strip():
                return str(value).strip()
    return None


def _device_info_sources(data: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    state = data.get("state")
    update = data.get("softwareupdate")
    sources = []
    if isinstance(state, Mapping):
        sources.extend(state.get(key) for key in ("cablemodem", "system", "device"))
    if isinstance(update, Mapping):
        sources.append(update.get("softwareUpdate"))
    return tuple(source for source in sources if isinstance(source, Mapping))


def modem_docsis_version(data: Mapping[str, Any]) -> str | None:
    """Return the version explicitly reported by the modem, when available."""
    for source in _device_info_sources(data):
        version = source.get("docsisVersion")
        match = re.fullmatch(
            r"(?:DOCSIS\s*)?([0-9]+(?:\.[0-9]+)*)", str(version).strip(), re.IGNORECASE
        )
        if match:
            return match[1]
    return None


class ZiggoModemBaseEntity(CoordinatorEntity[ZiggoModemDataUpdateCoordinator]):
    """Base entity for Ziggo modem entities."""

    def __init__(
        self,
        coordinator: ZiggoModemDataUpdateCoordinator,
        entry_id: str,
        host: str,
    ) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._host = host
        self._translation_key: str | None = None
        self._attr_has_entity_name = True

    @property
    def name(self) -> str | None:
        """Return the translated entity name."""
        if self._translation_key:
            return self.coordinator.translate(self._translation_key)
        return getattr(self, "_attr_name", None)

    @property
    def available(self) -> bool:
        """Return whether the coordinator and required endpoints are available."""
        description = getattr(self, "entity_description", None)
        required_endpoints = getattr(description, "required_endpoints", frozenset())
        return super().available and self.coordinator.endpoints_available(
            required_endpoints
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for the Ziggo modem."""
        data = self.coordinator.data or {}
        sources = _device_info_sources(data)

        manufacturer = _first_text(
            sources,
            ("manufacturer", "manufacturerName", "vendor", "vendorName"),
        ) or "Sagemcom"
        model = _first_text(
            sources,
            ("modelName", "model", "productName", "productClass", "deviceModel"),
        )
        serial = _first_text(sources, ("serialNumber", "serial", "serialNo"))
        mac = _first_text(sources, ("macAddress", "mac", "cmMacAddress"))
        firmware = _first_text(
            sources,
            (
                "firmwareVersion",
                "softwareVersion",
                "currentVersion",
                "currentSoftwareVersion",
            ),
        )
        hardware = _first_text(
            sources,
            ("hardwareVersion", "hardwareRevision", "hwVersion"),
        )
        if not model:
            model = "SmartWifi modem"
            if docsis := modem_docsis_version(data):
                model = f"{model} (DOCSIS {docsis})"

        identifiers = {
            (DOMAIN, serial or self._host),
        }

        connections = set()
        if mac:
            connections.add((CONNECTION_NETWORK_MAC, mac.lower()))

        return DeviceInfo(
            identifiers=identifiers,
            connections=connections,
            name="Ziggo Modem",
            manufacturer=manufacturer,
            model=model,
            serial_number=serial,
            configuration_url=f"https://{self._host}",
            sw_version=firmware,
            hw_version=hardware,
        )
