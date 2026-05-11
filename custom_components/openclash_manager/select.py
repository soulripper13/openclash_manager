"""Select entity for OpenClash config switching."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA_COORDINATOR, DOMAIN
from .coordinator import OpenClashConfigCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenClash select entities."""
    coordinator: OpenClashConfigCoordinator = hass.data[DOMAIN][entry.entry_id][
        DATA_COORDINATOR
    ]
    async_add_entities(
        [
            OpenClashConfigSelect(coordinator, entry),
            OpenClashOperationModeSelect(coordinator, entry),
        ]
    )


class OpenClashConfigSelect(CoordinatorEntity[OpenClashConfigCoordinator], SelectEntity):
    """Select entity that switches the active OpenClash config."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:file-swap-outline"
    _attr_translation_key = "config"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: OpenClashConfigCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_config"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "OpenClash",
            "model": "OpenClash Manager",
            "sw_version": coordinator.data.version if coordinator.data else None,
        }

    @property
    def current_option(self) -> str | None:
        """Return the currently selected config."""
        return self.coordinator.data.current if self.coordinator.data else None

    @property
    def options(self) -> list[str]:
        """Return available config files."""
        if not self.coordinator.data:
            return []
        return list(self.coordinator.data.options)

    async def async_select_option(self, option: str) -> None:
        """Switch OpenClash to the selected config."""
        if option == self.current_option:
            return

        await self.hass.async_add_executor_job(self.coordinator.client.switch_config, option)
        await self.coordinator.async_request_refresh()


class OpenClashOperationModeSelect(
    CoordinatorEntity[OpenClashConfigCoordinator], SelectEntity
):
    """Select entity that switches the OpenClash operation mode."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:router-wireless-settings"
    _attr_translation_key = "operation_mode"
    _attr_options = ["rule", "global", "direct"]
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: OpenClashConfigCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_name = "Operation Mode"
        self._attr_unique_id = f"{entry.entry_id}_operation_mode"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "OpenClash",
            "model": "OpenClash Manager",
            "sw_version": coordinator.data.version if coordinator.data else None,
        }

    @property
    def current_option(self) -> str | None:
        """Return the current operation mode."""
        if not self.coordinator.data or not self.coordinator.data.operation_mode:
            return None
        mode = self.coordinator.data.operation_mode.lower()
        if mode in self._attr_options:
            return mode
        return None

    async def async_select_option(self, option: str) -> None:
        """Switch OpenClash to the selected operation mode."""
        if option == self.current_option:
            return

        await self.hass.async_add_executor_job(
            self.coordinator.client.set_operation_mode, option
        )
        await self.coordinator.async_request_refresh()
