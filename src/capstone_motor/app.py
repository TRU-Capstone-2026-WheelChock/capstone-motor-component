from __future__ import annotations

import asyncio
import logging

from capstone_motor.command_receiver import MotorCommandReceiver
from capstone_motor.heartbeat_publisher import HeartbeatPublisher
from capstone_motor.motor_driver import MotorHardwareController


class MotorComponentApp:
    def __init__(
        self,
        command_receiver: MotorCommandReceiver,
        heartbeat_publisher: HeartbeatPublisher,
        motor_controller: MotorHardwareController,
        logger: logging.Logger | None = None,
    ) -> None:
        self.command_receiver = command_receiver
        self.heartbeat_publisher = heartbeat_publisher
        self.motor_controller = motor_controller
        self.logger = logger or logging.getLogger(__name__)

    async def run(self) -> None:
        await self.motor_controller.initialize()
        try:
            async with asyncio.TaskGroup() as task_group:
                task_group.create_task(
                    self.command_receiver.run(),
                    name="motor-command-receiver",
                )
                task_group.create_task(
                    self.heartbeat_publisher.run(),
                    name="motor-heartbeat-publisher",
                )
        finally:
            await self.motor_controller.stop()
