"""Switch entities for HomeKit-friendly OpenClash config switching."""

from __future__ import annotations

from hashlib import sha1
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA_COORDINATOR, DOMAIN
from .coordinator import OpenClashConfigCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenClash switch entities."""
    coordinator: OpenClashConfigCoordinator = hass.data[DOMAIN][entry.entry_id][
        DATA_COORDINATOR
    ]
    
    async_add_entities([OpenClashEnableSwitch(coordinator, entry)])

    known_options: set[str] = set()

    @callback
    def _add_missing_switches() -> None:
        if not coordinator.data:
            return

        new_options = [
            option for option in coordinator.data.options if option not in known_options
        ]
        if not new_options:
            return

        known_options.update(new_options)
        async_add_entities(
            [OpenClashConfigSwitch(coordinator, entry, option) for option in new_options]
        )

    _add_missing_switches()
    entry.async_on_unload(coordinator.async_add_listener(_add_missing_switches))


class OpenClashEnableSwitch(CoordinatorEntity[OpenClashConfigCoordinator], SwitchEntity):
    """Switch that enables or disables OpenClash globally."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:shield-check"
    _attr_translation_key = "enable"

    def __init__(
        self,
        coordinator: OpenClashConfigCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_enable"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "OpenClash",
            "model": "OpenClash Manager",
            "sw_version": coordinator.data.version if coordinator.data else None,
        }

    @property
    def is_on(self) -> bool:
        """Return true if OpenClash is enabled."""
        return self.coordinator.data.enabled if self.coordinator.data else False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable OpenClash."""
        await self.hass.async_add_executor_job(
            self.coordinator.client.set_enabled, True
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable OpenClash."""
        await self.hass.async_add_executor_job(
            self.coordinator.client.set_enabled, False
        )
        await self.coordinator.async_request_refresh()


class OpenClashConfigSwitch(CoordinatorEntity[OpenClashConfigCoordinator], SwitchEntity):
    """Switch that turns on one OpenClash config."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: OpenClashConfigCoordinator,
        entry: ConfigEntry,
        option: str,
    ) -> None:
        """Initialize the config switch."""
        super().__init__(coordinator)
        self._option = option
        # Strip extension for a cleaner name
        display_name = option
        for ext in (".yaml", ".yml"):
            if display_name.lower().endswith(ext):
                display_name = display_name[: -len(ext)]
        self._attr_name = display_name
        option_hash = sha1(option.encode("utf-8")).hexdigest()
        self._attr_unique_id = f"{entry.entry_id}_config_{option_hash}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "OpenClash",
            "model": "OpenClash Manager",
            "sw_version": coordinator.data.version if coordinator.data else None,
        }

    @property
    def is_on(self) -> bool:
        """Return true if this config is active."""
        return bool(self.coordinator.data and self.coordinator.data.current == self._option)

    @property
    def icon(self) -> str:
        """Return an icon that highlights the active config."""
        return "mdi:check-circle-outline" if self.is_on else "mdi:file-document-outline"

    @property
    def available(self) -> bool:
        """Return true if this config still exists on the router."""
        return bool(
            super().available
            and self.coordinator.data
            and self._option in self.coordinator.data.options
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Switch OpenClash to this config."""
        if self.is_on:
            return

        await self.hass.async_add_executor_job(
            self.coordinator.client.switch_config,
            self._option,
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Ignore turn-off requests because one OpenClash config must stay active."""
        await self.coordinator.async_request_refresh()
