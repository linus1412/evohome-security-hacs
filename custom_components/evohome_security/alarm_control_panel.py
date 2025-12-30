"""Alarm control panel platform for Honeywell Evohome Security."""

from __future__ import annotations

import logging

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
)
from homeassistant.components.alarm_control_panel.const import AlarmControlPanelState
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import EvohomeSecurityCoordinator
from .evohome_security_async import ArmStatus

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up alarm control panel from config entry."""
    coordinator: EvohomeSecurityCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        [EvohomeSecurityPanel(coordinator, config_entry)],
        True,
    )


class EvohomeSecurityPanel(
    CoordinatorEntity[EvohomeSecurityCoordinator], AlarmControlPanelEntity
):
    """Representation of Evohome Security alarm panel."""

    _attr_code_arm_required = False
    _attr_name = "Evohome Security"
    _attr_supported_features = (
        AlarmControlPanelEntityFeature.ARM_AWAY
        | AlarmControlPanelEntityFeature.ARM_HOME
    )

    def __init__(
        self,
        coordinator: EvohomeSecurityCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the alarm panel."""
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._attr_unique_id = f"{DOMAIN}_panel"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "evohome_security")},
            name="Evohome Security",
            manufacturer="Honeywell",
            model="Total Connect Security",
        )

    @property
    def state(self) -> AlarmControlPanelState | None:
        """Return the state of the alarm panel."""
        if not self.coordinator.data:
            return None

        status = self.coordinator.data.get("status")
        if status == ArmStatus.ARMED_AWAY:
            return AlarmControlPanelState.ARMED_AWAY
        if status == ArmStatus.ARMED_HOME:
            return AlarmControlPanelState.ARMED_HOME
        if status == ArmStatus.DISARMED:
            return AlarmControlPanelState.DISARMED

        return None

    async def async_alarm_arm_away(self, code: str | None = None) -> None:
        """Arm away."""
        await self.coordinator.async_arm_away()

    async def async_alarm_arm_home(self, code: str | None = None) -> None:
        """Arm home."""
        await self.coordinator.async_arm_home()

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        """Disarm."""
        await self.coordinator.async_disarm()
