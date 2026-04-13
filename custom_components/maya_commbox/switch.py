"""Switch platform for CommBox MIO."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NUM_RELAYS
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
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        # Output mapping in the 32-element list: Out 1 is at index 31, etc.
        outputs = self.coordinator.data.get("outputs", [])
        api_index = 32 - self._num_outputs + self._address
        if api_index < len(outputs):
            return outputs[api_index] == 1
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        if await self.coordinator.hub.set_output(self._address, 1, self._num_outputs):
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        if await self.coordinator.hub.set_output(self._address, 0, self._num_outputs):
            await self.coordinator.async_request_refresh()
