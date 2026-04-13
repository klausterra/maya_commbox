"""DataUpdateCoordinator for CommBox MIO."""
from datetime import timedelta
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

class CommBoxDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching status data from CommBox device."""

    def __init__(self, hass, hub):
        """Initialize."""
        self.hub = hub
        self.device_info = {}
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self):
        """Fetch data from hub."""
        data = await self.hub.get_io_status()
        if data is None:
            raise UpdateFailed("Error communicating with CommBox MIO")
        return data
