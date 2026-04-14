"""Binary sensor platform for Maya Commbox."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
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
        """Return true if the binary sensor is on."""
        if not self.coordinator.data:
            return False
        # MIOv3 Logic: Inputs follow same inverted pattern as outputs (Input 1 = idx 31).
        try:
            return self.coordinator.data["inputs"]["state"][31 - self._address] == 1
        except (KeyError, IndexError):
            return False
