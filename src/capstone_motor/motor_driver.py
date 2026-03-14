from __future__ import annotations

import logging

import msg_handler


class MotorHardwareController:
    """Place all direct motor hardware code in this class."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.logger = logger or logging.getLogger(__name__)

    async def initialize(self) -> None:
        """Reserve GPIO, serial, CAN, or any other hardware resources here."""

    async def apply_order(
        self,
        ordered_mode: msg_handler.MotorState,
    ) -> msg_handler.MotorState:
        if ordered_mode == msg_handler.MotorState.DEPLOYING:
            return await self.deploy()
        if ordered_mode == msg_handler.MotorState.FOLDING:
            return await self.fold()
        raise ValueError(f"Unsupported motor order: {ordered_mode}")

    async def deploy(self) -> msg_handler.MotorState:
        raise NotImplementedError("Add direct deploy control code here.")

    async def fold(self) -> msg_handler.MotorState:
        raise NotImplementedError("Add direct fold control code here.")

    async def read_status(self) -> msg_handler.MotorState:
        raise NotImplementedError("Add direct motor status read code here.")

    async def stop(self) -> None:
        """Release hardware resources or stop the motor safely here."""
