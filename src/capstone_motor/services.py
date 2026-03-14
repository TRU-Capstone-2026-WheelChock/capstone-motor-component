from __future__ import annotations

import logging
from datetime import datetime

import msg_handler

from capstone_motor.motor_driver import MotorHardwareController
from capstone_motor.state_store import RuntimeStateStore


class MotorCommandService:
    def __init__(
        self,
        state_store: RuntimeStateStore,
        motor_controller: MotorHardwareController,
        logger: logging.Logger | None = None,
    ) -> None:
        self.state_store = state_store
        self.motor_controller = motor_controller
        self.logger = logger or logging.getLogger(__name__)

    async def process_command(self, message: msg_handler.MotorMessage) -> None:
        received_at = datetime.now()
        await self.state_store.record_received_command(message, received_at=received_at)

        try:
            applied_status = await self.motor_controller.apply_order(message.ordered_mode)
        except Exception as exc:
            await self.state_store.record_error(str(exc))
            raise

        await self.state_store.mark_applied_order(
            applied_mode=message.ordered_mode,
            motor_status=applied_status,
            applied_at=datetime.now(),
        )

    async def refresh_status_from_hardware(self) -> None:
        status = await self.motor_controller.read_status()
        await self.state_store.set_motor_status(status, updated_at=datetime.now())
