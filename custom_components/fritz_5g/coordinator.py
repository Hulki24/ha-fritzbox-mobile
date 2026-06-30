"""Coordinator for HA FRITZ!Box Mobile."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import Fritz5GApi
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class Fritz5GCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator for FRITZ!Box Mobile."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        """Initialize coordinator."""

        self.config_entry = entry

        self.api = Fritz5GApi(
            host=entry.data["host"],
            username=entry.data["username"],
            password=entry.data["password"],
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(
                seconds=DEFAULT_SCAN_INTERVAL
            ),
        )

    async def _async_update_data(self) -> dict:
        """Update data."""

        try:
            data = await self.hass.async_add_executor_job(
                self.api.get_data
            )

            
            _LOGGER.debug("Coordinator update: %s", data)

            return data

        except Exception as err:
            raise UpdateFailed(str(err)) from err