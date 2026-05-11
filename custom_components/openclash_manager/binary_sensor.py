"""Binary sensor entities for OpenClash."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA_COORDINATOR, DOMAIN
from .coordinator import OpenClashConfigCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenClash binary sensors."""
    coordinator: OpenClashConfigCoordinator = hass.data[DOMAIN][entry.entry_id][
        DATA_COORDINATOR
    ]
    async_add_entities([OpenClashRunningSensor(coordinator, entry)])


class OpenClashRunningSensor(
    CoordinatorEntity[OpenClashConfigCoordinator], BinarySensorEntity
):
    """Binary sensor that tracks if OpenClash is running."""

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.RUNNING

    def __init__(
        self,
        coordinator: OpenClashConfigCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Status"
        self._attr_unique_id = f"{entry.entry_id}_status"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "OpenClash",
        }

    @property
    def is_on(self) -> bool:
        """Return true if OpenClash is running."""
        return self.coordinator.data.is_running if self.coordinator.data else False

    @property
    def available(self) -> bool:
        """Return true if coordinator has data."""
        return self.coordinator.last_update_success and self.coordinator.data is not None
