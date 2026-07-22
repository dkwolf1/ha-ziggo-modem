from __future__ import annotations

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
    def device_info(self) -> DeviceInfo:
        """Return device info for the Ziggo modem."""
        data = self.coordinator.data or {}
        state = data.get("state", {})
        cablemodem = state.get("cablemodem", {})
        system = state.get("system", {})
        device = state.get("device", {})
        software_update = data.get("softwareupdate", {}).get("softwareUpdate", {})

        sources = tuple(
            source
            for source in (cablemodem, system, device, software_update)
            if isinstance(source, Mapping)
        )

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
        docsis = _first_text(sources, ("docsisVersion",))

        if not model:
            model = "SmartWifi modem"
            if docsis:
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
