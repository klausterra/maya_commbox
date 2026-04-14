"""Switch platform for Maya Commbox."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import CommBoxDataUpdateCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the CommBox switches."""
    coordinator: CommBoxDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    num_outputs = coordinator.device_info.get("num_outputs", 4)

    switches = []
    for i in range(num_outputs):
        switches.append(CommBoxRelay(coordinator, i))

    async_add_entities(switches)

    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        "pulse_output",
        {
            vol.Required("duration", default=1000): cv.positive_int,
        },
        "async_pulse_output",
    )

class CommBoxRelay(CoordinatorEntity, SwitchEntity):
    """Representation of a CommBox Relay."""

    def __init__(self, coordinator: CommBoxDataUpdateCoordinator, address: int) -> None:
        """Initialize the relay."""
        super().__init__(coordinator)
        self._address = address
        self._num_outputs = coordinator.device_info.get("num_outputs", 4)
        self._attr_name = f"CommBox Relay {address + 1}"
        self._attr_unique_id = f"{coordinator.hub.ip_address}_relay_{address}"

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.hub.ip_address)},
            "name": f"Maya Commbox ({self.coordinator.hub.ip_address})",
            "manufacturer": "Hiperenge / Maya Home",
            "model": self.coordinator.device_info.get("model", "Modular I/O"),
            "sw_version": self.coordinator.device_info.get("firmware"),
            "configuration_url": "https://www.mayahome.ia.br",
        }

    @property
    def is_on(self):
        """Return true if switch is on."""
        if not self.coordinator.data:
            return False
        # MIOv3 Logic: Relays are typically in the outputs["state"] array.
        # Index 31 is Output 1, 30 is Output 2, etc.
        try:
            return self.coordinator.data["outputs"]["state"][31 - self._address] == 1
        except (KeyError, IndexError):
            return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        if await self.coordinator.hub.set_output(self._address, 1, self._num_outputs):
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        if await self.coordinator.hub.set_output(self._address, 0, self._num_outputs):
            await self.coordinator.async_request_refresh()

    async def async_pulse_output(self, duration: int) -> None:
        """Pulse the relay for a duration."""
        if await self.coordinator.hub.pulse_output(self._address, duration, self._num_outputs):
            await self.coordinator.async_request_refresh()
