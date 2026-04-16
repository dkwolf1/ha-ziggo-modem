from __future__ import annotations

from homeassistant.helpers.device_registry import (
    CONNECTION_NETWORK_MAC,
    DeviceInfo,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ZiggoModemDataUpdateCoordinator


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
        self._attr_has_entity_name = True

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for the Ziggo modem."""
        state = self.coordinator.data.get("state", {})
        cablemodem = state.get("cablemodem", {})

        serial = cablemodem.get("serialNumber")
        mac = cablemodem.get("macAddress")
        docsis = cablemodem.get("docsisVersion")

        identifiers = {
            (DOMAIN, serial or self._host),
        }

        connections = set()
        if mac:
            connections.add((CONNECTION_NETWORK_MAC, mac.lower()))

        sw_version = f"DOCSIS {docsis}" if docsis else None

        return DeviceInfo(
            identifiers=identifiers,
            connections=connections,
            name="Ziggo Modem",
            manufacturer="Sagemcom",
            model="SmartWifi modem",
            serial_number=serial,
            configuration_url=f"https://{self._host}",
            sw_version=sw_version,
        )
