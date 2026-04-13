"""Binary sensor platform for CommBox MIO."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NUM_INPUTS
from .coordinator import CommBoxDataUpdateCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the CommBox binary sensors."""
    coordinator: CommBoxDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    num_inputs = coordinator.device_info.get("num_inputs", 4)

    sensors = []
    for i in range(num_inputs):
        sensors.append(CommBoxInput(coordinator, i))

    async_add_entities(sensors)

class CommBoxInput(CoordinatorEntity, BinarySensorEntity):
    """Representation of a CommBox Input."""

    def __init__(self, coordinator: CommBoxDataUpdateCoordinator, address: int) -> None:
        """Initialize the input."""
        super().__init__(coordinator)
        self._address = address
        self._num_inputs = coordinator.device_info.get("num_inputs", 4)
        self._attr_name = f"CommBox Input {address + 1}"
        self._attr_unique_id = f"{coordinator.hub.ip_address}_input_{address}"

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        # Input mapping in the 32-element list: In 1 is at index 31, etc.
        inputs = self.coordinator.data.get("inputs", [])
        api_index = 32 - self._num_inputs + self._address
        if api_index < len(inputs):
            return inputs[api_index] == 1
        return None
