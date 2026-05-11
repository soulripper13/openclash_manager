"""Coordinator for the OpenClash Config Switcher integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import OpenClashClient, OpenClashConnectionConfig, OpenClashError, OpenClashState
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class OpenClashConfigCoordinator(DataUpdateCoordinator[OpenClashState]):
    """Coordinator that keeps OpenClash config options in memory."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.client = OpenClashClient(OpenClashConnectionConfig.from_config_entry(entry))
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),
        )

    async def _async_update_data(self) -> OpenClashState:
        """Fetch state from OpenClash."""
        try:
            return await self.hass.async_add_executor_job(self.client.get_state)
        except OpenClashError as err:
            raise UpdateFailed(str(err)) from err
