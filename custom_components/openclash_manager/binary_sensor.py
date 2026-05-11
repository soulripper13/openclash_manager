"""Binary sensor entities for OpenClash."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
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
    _attr_translation_key = "status"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator: OpenClashConfigCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_status"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "OpenClash",
            "model": "OpenClash Manager",
            "sw_version": coordinator.data.version if coordinator.data else None,
            "configuration_url": f"http://{entry.data[CONF_HOST]}/cgi-bin/luci/admin/services/openclash",
        }

    @property
    def is_on(self) -> bool:
        """Return true if OpenClash is running."""
        return self.coordinator.data.is_running if self.coordinator.data else False
