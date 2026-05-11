"""Sensor entities for OpenClash."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
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
    """Set up OpenClash sensors."""
    coordinator: OpenClashConfigCoordinator = hass.data[DOMAIN][entry.entry_id][
        DATA_COORDINATOR
    ]
    async_add_entities([OpenClashVersionSensor(coordinator, entry)])


class OpenClashVersionSensor(CoordinatorEntity[OpenClashConfigCoordinator], SensorEntity):
    """Sensor that displays the OpenClash version."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:information-outline"
    _attr_translation_key = "version"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator: OpenClashConfigCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_version"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "OpenClash",
            "model": "OpenClash Manager",
            "sw_version": coordinator.data.version if coordinator.data else None,
        }

    @property
    def native_value(self) -> str | None:
        """Return the version."""
        return self.coordinator.data.version if self.coordinator.data else None
