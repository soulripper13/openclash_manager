"""Lovelace card setup for OpenClash Config Switcher."""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace import DOMAIN as LOVELACE_DOMAIN
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_call_later

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

CARD_VERSION = "0.3.4"
CARD_FILENAME = "openclash-config-card.js"
CARD_URL_BASE = f"/{DOMAIN}/{CARD_FILENAME}"
WWW_PATH = Path(__file__).parent / "www"


async def async_setup_card(hass: HomeAssistant) -> None:
    """Serve and register the OpenClash Lovelace card."""
    static_marker = f"{DOMAIN}_static_path_registered"
    if not hass.data.get(static_marker):
        await hass.http.async_register_static_paths(
            [StaticPathConfig(f"/{DOMAIN}", str(WWW_PATH), False)]
        )
        hass.data[static_marker] = True

    frontend_marker = f"{DOMAIN}_frontend_card_registered_{CARD_VERSION}"
    if not hass.data.get(frontend_marker):
        add_extra_js_url(hass, f"{CARD_URL_BASE}?v={CARD_VERSION}")
        hass.data[frontend_marker] = True

    await async_register_card_resource(hass)


async def async_register_card_resource(hass: HomeAssistant) -> None:
    """Register the card as a Lovelace module resource when Lovelace is ready."""
    lovelace = hass.data.get(LOVELACE_DOMAIN)
    if not lovelace or not getattr(lovelace, "resources", None):
        _schedule_retry(hass)
        return

    resources = lovelace.resources
    if not resources.loaded:
        _schedule_retry(hass)
        return

    full_url = f"{CARD_URL_BASE}?v={CARD_VERSION}"
    existing = None
    for resource in resources.async_items():
        if resource["url"].split("?")[0] == CARD_URL_BASE:
            existing = resource
            break

    try:
        if existing:
            if existing["url"] != full_url:
                await resources.async_update_item(
                    existing["id"], {"res_type": "module", "url": full_url}
                )
        else:
            await resources.async_create_item({"res_type": "module", "url": full_url})
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning("Could not register OpenClash Lovelace card: %s", err)


def _schedule_retry(hass: HomeAssistant) -> None:
    """Try resource registration again after Lovelace finishes loading."""

    @callback
    def _retry(_now) -> None:
        hass.async_create_task(async_register_card_resource(hass))

    async_call_later(hass, 5, _retry)
