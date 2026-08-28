from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import ZiggoModemApi
from .const import CONF_HOST
from .coordinator import ZiggoModemDataUpdateCoordinator
from .data import ZiggoModemConfigEntry
from .entity import ZiggoModemBaseEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ZiggoModemConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ziggo modem buttons."""
    api = entry.runtime_data.api
    coordinator = entry.runtime_data.coordinator
    host = entry.options.get(CONF_HOST, entry.data[CONF_HOST])

    async_add_entities(
        [
            ZiggoModemReleaseSessionButton(
                coordinator,
                entry.entry_id,
                host,
                api,
            ),
            ZiggoModemRebootButton(
                coordinator,
                entry.entry_id,
                host,
                api,
            ),
        ]
    )


class ZiggoModemReleaseSessionButton(ZiggoModemBaseEntity, ButtonEntity):
    """Button to release the active modem session."""

    def __init__(
        self,
        coordinator: ZiggoModemDataUpdateCoordinator,
        entry_id: str,
        host: str,
        api: ZiggoModemApi,
    ) -> None:
        super().__init__(coordinator, entry_id, host)
        self._api = api
        self._translation_key = "button.release_session.name"
        self._attr_name = coordinator.translate("button.release_session.name")
        self._attr_unique_id = f"{entry_id}_release_session"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_icon = "mdi:connection"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._api.async_release_session()
        await self.coordinator.async_request_refresh()


class ZiggoModemRebootButton(ZiggoModemBaseEntity, ButtonEntity):
    """Button to reboot the modem."""

    def __init__(
        self,
        coordinator: ZiggoModemDataUpdateCoordinator,
        entry_id: str,
        host: str,
        api: ZiggoModemApi,
    ) -> None:
        super().__init__(coordinator, entry_id, host)
        self._api = api
        self._translation_key = "button.reboot.name"
        self._attr_name = coordinator.translate("button.reboot.name")
        self._attr_unique_id = f"{entry_id}_reboot"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_icon = "mdi:restart"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._api.async_reboot()
