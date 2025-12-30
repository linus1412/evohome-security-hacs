"""Data update coordinator for Evohome Security."""

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .evohome_security_async import EvohomeSecurityClient

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(seconds=30)


class EvohomeSecurityCoordinator(DataUpdateCoordinator):
    """Coordinator for Evohome Security data updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        username: str,
        password: str,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        self.username = username
        self.password = password

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
            config_entry=config_entry,
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from the API."""
        client = EvohomeSecurityClient(self.username, self.password)

        try:
            async with client:
                await client.authenticate()
                status = await client.get_status()
                return {"status": status}
        except Exception as err:
            raise UpdateFailed(
                f"Error communicating with Evohome Security: {err}"
            ) from err

    async def async_arm_away(self) -> None:
        """Arm the system (away mode)."""
        client = EvohomeSecurityClient(self.username, self.password)

        try:
            async with client:
                await client.authenticate()
                await client.arm_total()
                await self.async_refresh()
        except Exception as err:
            _LOGGER.error("Error arming system: %s", err)
            raise

    async def async_arm_home(self) -> None:
        """Arm the system (home mode)."""
        client = EvohomeSecurityClient(self.username, self.password)

        try:
            async with client:
                await client.authenticate()
                await client.arm_partial()
                await self.async_refresh()
        except Exception as err:
            _LOGGER.error("Error arming system: %s", err)
            raise

    async def async_disarm(self) -> None:
        """Disarm the system."""
        client = EvohomeSecurityClient(self.username, self.password)

        try:
            async with client:
                await client.authenticate()
                await client.disarm()
                await self.async_refresh()
        except Exception as err:
            _LOGGER.error("Error disarming system: %s", err)
            raise

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
