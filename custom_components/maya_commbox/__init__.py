"""The CommBox MIO integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .const import DOMAIN, CONF_IP
from .hub import CommBoxHub
from .coordinator import CommBoxDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SWITCH, Platform.BINARY_SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up CommBox MIO from a config entry."""
    ip_address = entry.data[CONF_IP]
    hub = CommBoxHub(ip_address)
    
    device_info = await hub.get_device_info()
    
    coordinator = CommBoxDataUpdateCoordinator(hass, hub)
    coordinator.device_info = device_info
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def handle_pulse_output(call):
        """Handle the pulse service call."""
        # Generic handler for simple use case
        duration = call.data.get("duration", 1000)
        for entry_id, coord in hass.data[DOMAIN].items():
            await coord.hub.pulse_output(0, duration) 
    
    hass.services.async_register(DOMAIN, "pulse_output", handle_pulse_output)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
