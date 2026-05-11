"""Button entities for OpenClash actions."""

from __future__ import annotations

from typing import Any

from homeassistant.components.button import ButtonEntity
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
    """Set up OpenClash buttons."""
    coordinator: OpenClashConfigCoordinator = hass.data[DOMAIN][entry.entry_id][
        DATA_COORDINATOR
    ]
    async_add_entities(
        [
            OpenClashUpdateSubscriptionsButton(coordinator, entry),
            OpenClashUpdateCoresButton(coordinator, entry),
            OpenClashRestartButton(coordinator, entry),
        ]
    )


class OpenClashButton(CoordinatorEntity[OpenClashConfigCoordinator], ButtonEntity):
    """Base button for OpenClash actions."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: OpenClashConfigCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "OpenClash",
            "model": "OpenClash Manager",
            "sw_version": coordinator.data.version if coordinator.data else None,
            "configuration_url": f"http://{entry.data[CONF_HOST]}/cgi-bin/luci/admin/services/openclash",
        }


class OpenClashUpdateSubscriptionsButton(OpenClashButton):
    """Button to update OpenClash subscriptions."""

    _attr_translation_key = "update_subscriptions"

    def __init__(
        self,
        coordinator: OpenClashConfigCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_update_subscriptions"
        self._attr_icon = "mdi:update"

    async def async_press(self) -> None:
        """Trigger update subscriptions."""
        await self.hass.async_add_executor_job(
            self.coordinator.client.update_subscriptions
        )
        await self.coordinator.async_request_refresh()


class OpenClashUpdateCoresButton(OpenClashButton):
    """Button to update OpenClash cores."""

    _attr_translation_key = "update_cores"

    def __init__(
        self,
        coordinator: OpenClashConfigCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_update_cores"
        self._attr_icon = "mdi:cpu-64-bit"

    async def async_press(self) -> None:
        """Trigger update cores."""
        await self.hass.async_add_executor_job(
            self.coordinator.client.update_cores
        )
        await self.coordinator.async_request_refresh()


class OpenClashRestartButton(OpenClashButton):
    """Button to restart OpenClash."""

    _attr_translation_key = "restart"

    def __init__(
        self,
        coordinator: OpenClashConfigCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_restart"
        self._attr_icon = "mdi:restart"

    async def async_press(self) -> None:
        """Trigger OpenClash restart."""
        await self.hass.async_add_executor_job(
            self.coordinator.client.restart_openclash
        )
        await self.coordinator.async_request_refresh()
