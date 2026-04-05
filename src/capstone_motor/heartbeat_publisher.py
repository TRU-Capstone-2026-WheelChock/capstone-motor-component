from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
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
        refresh_status: Callable[[], Awaitable[None]] | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.component_config = component_config
        self.state_store = state_store
        self.pub_opt = pub_opt
        self.refresh_status = refresh_status
        self.logger = logger or logging.getLogger(__name__)
        self.seq_no = 0
        self._last_logged_status: int | None = None

    async def build_message(self) -> msg_handler.SensorMessage:
        if self.refresh_status is not None:
            await self.refresh_status()
        snapshot = await self.state_store.snapshot()
        self.seq_no +=1
        return msg_handler.SensorMessage(
            sender_id=self.component_config.component_id,
            sender_name=self.component_config.component_name,
            data_type=msg_handler.GenericMessageDatatype.HEARTBEAT,
            payload=snapshot.build_heartbeat_payload(),
            sequence_no=self.seq_no
        )

    async def publish_once(self, publisher: _AsyncHeartbeatPublisher) -> None:
        message = await self.build_message()
        self._log_message(message)
        await publisher.send(message)

    def _log_message(self, message: msg_handler.SensorMessage) -> None:
        payload = message.payload
        self.logger.debug(
            "heartbeat send seq=%d sender=%s status=%s status_code=%d",
            message.sequence_no,
            message.sender_id,
            payload.status,
            payload.status_code,
        )
        if payload.status != self._last_logged_status:
            self.logger.info(
                "heartbeat status changed: status=%s status_code=%d (seq=%d)",
                payload.status,
                payload.status_code,
                message.sequence_no,
            )
            self._last_logged_status = payload.status

    async def run(self) -> None:
        async with msg_handler.get_async_publisher(self.pub_opt) as publisher:
            self.logger.info("heartbeat publisher is UP")
            while True:
                await self.publish_once(publisher)
                await asyncio.sleep(self.component_config.heartbeat.interval_sec)
