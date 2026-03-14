from __future__ import annotations

import asyncio
import logging
from typing import Protocol

import msg_handler

from capstone_motor.config import MotorComponentConfig
from capstone_motor.state_store import RuntimeStateStore


class _AsyncHeartbeatPublisher(Protocol):
    async def send(self, msg: msg_handler.SensorMessage) -> None: ...


class HeartbeatPublisher:
    def __init__(
        self,
        component_config: MotorComponentConfig,
        state_store: RuntimeStateStore,
        pub_opt: msg_handler.ZmqPubOptions,
        logger: logging.Logger | None = None,
    ) -> None:
        self.component_config = component_config
        self.state_store = state_store
        self.pub_opt = pub_opt
        self.logger = logger or logging.getLogger(__name__)

    async def build_message(self) -> msg_handler.SensorMessage:
        snapshot = await self.state_store.snapshot()
        return msg_handler.SensorMessage(
            sender_id=self.component_config.component_id,
            sender_name=self.component_config.component_name,
            data_type=msg_handler.GenericMessageDatatype.HEARTBEAT,
            payload=snapshot.build_heartbeat_payload(),
        )

    async def publish_once(self, publisher: _AsyncHeartbeatPublisher) -> None:
        message = await self.build_message()
        await publisher.send(message)
        await self.state_store.mark_heartbeat_sent(sent_at=message.timestamp)

    async def run(self) -> None:
        async with msg_handler.get_async_publisher(self.pub_opt) as publisher:
            self.logger.info("heartbeat publisher is UP")
            while True:
                await self.publish_once(publisher)
                await asyncio.sleep(self.component_config.heartbeat.interval_sec)
