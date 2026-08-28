from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import ZiggoModemApi
from .const import CONF_HOST, CONF_VERBOSE_DIAGNOSTICS
from .coordinator import ZiggoModemDataUpdateCoordinator
from .data import ZiggoModemConfigEntry
from .entity import ZiggoModemBaseEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ZiggoModemConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ziggo modem switches."""
    api = entry.runtime_data.api
    coordinator = entry.runtime_data.coordinator
    host: str = entry.options.get(CONF_HOST, entry.data[CONF_HOST])

    async_add_entities(
        [
            ZiggoModemPauseSwitch(
                coordinator,
                entry,
                host,
                api,
            ),
            ZiggoModemVerboseDiagnosticsSwitch(
                hass,
                coordinator,
                entry,
                host,
            ),
        ]
    )


class ZiggoModemPauseSwitch(ZiggoModemBaseEntity, SwitchEntity):
    """Switch to pause Ziggo modem polling and release session."""

    def __init__(
        self,
        coordinator: ZiggoModemDataUpdateCoordinator,
        entry: ZiggoModemConfigEntry,
        host: str,
        api: ZiggoModemApi,
    ) -> None:
        super().__init__(coordinator, entry.entry_id, host)
        self._entry = entry
        self._api = api
        self._translation_key = "switch.pause.name"
        self._attr_name = coordinator.translate("switch.pause.name")
        self._attr_unique_id = f"{entry.entry_id}_pause_integration"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def is_on(self) -> bool:
        """Return true if integration is paused."""
        return self._entry.runtime_data.paused

    async def async_turn_on(self, **kwargs) -> None:
        """Pause polling and release session."""
        self._entry.runtime_data.paused = True
        await self._api.async_release_session()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Resume polling."""
        self._entry.runtime_data.paused = False
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class ZiggoModemVerboseDiagnosticsSwitch(ZiggoModemBaseEntity, SwitchEntity):
    """Switch to show additional diagnostic attributes."""

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: ZiggoModemDataUpdateCoordinator,
        entry: ZiggoModemConfigEntry,
        host: str,
    ) -> None:
        super().__init__(coordinator, entry.entry_id, host)
        self.hass = hass
        self._entry = entry
        self._translation_key = "switch.verbose_diagnostics.name"
        self._attr_name = coordinator.translate("switch.verbose_diagnostics.name")
        self._attr_unique_id = f"{entry.entry_id}_verbose_diagnostics"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_icon = "mdi:text-box-search"

    @property
    def is_on(self) -> bool:
        """Return true if verbose diagnostics are enabled."""
        return self.coordinator.verbose_diagnostics

    async def async_turn_on(self, **kwargs) -> None:
        """Enable verbose diagnostics."""
        await self._set_verbose_diagnostics(True)

    async def async_turn_off(self, **kwargs) -> None:
        """Disable verbose diagnostics."""
        await self._set_verbose_diagnostics(False)

    async def _set_verbose_diagnostics(self, enabled: bool) -> None:
        self._entry.runtime_data.verbose_diagnostics = enabled

        self.hass.config_entries.async_update_entry(
            self._entry,
            options={
                **self._entry.options,
                CONF_VERBOSE_DIAGNOSTICS: enabled,
            },
        )

        self.async_write_ha_state()
        self.coordinator.async_update_listeners()
