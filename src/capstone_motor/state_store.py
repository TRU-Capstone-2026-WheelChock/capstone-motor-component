from __future__ import annotations

import asyncio
from copy import deepcopy
from datetime import datetime

import msg_handler

from capstone_motor.models import CommandRecord, RuntimeState


class RuntimeStateStore:
    def __init__(self, initial_state: RuntimeState | None = None) -> None:
        self._state = initial_state or RuntimeState()
        self._lock = asyncio.Lock()

    async def snapshot(self) -> RuntimeState:
        async with self._lock:
            return deepcopy(self._state)

    async def record_received_command(
        self,
        message: msg_handler.MotorMessage,
        *,
        received_at: datetime | None = None,
    ) -> None:
        now = received_at or datetime.now()
        async with self._lock:
            self._state.desired_mode = message.ordered_mode
            self._state.is_override_mode = message.is_override_mode
            self._state.last_command = CommandRecord(
                ordered_mode=message.ordered_mode,
                is_override_mode=message.is_override_mode,
                received_at=now,
            )
            self._state.last_command_at = now

    async def mark_applied_order(
        self,
        *,
        applied_mode: msg_handler.MotorState,
        motor_status: msg_handler.MotorState,
        applied_at: datetime | None = None,
    ) -> None:
        now = applied_at or datetime.now()
        async with self._lock:
            self._state.applied_mode = applied_mode
            self._state.motor_status = motor_status
            self._state.last_applied_at = now
            self._state.last_error = None

    async def set_motor_status(
        self,
        motor_status: msg_handler.MotorState,
        *,
        updated_at: datetime | None = None,
    ) -> None:
        now = updated_at or datetime.now()
        async with self._lock:
            self._state.motor_status = motor_status
            self._state.last_applied_at = now

    async def mark_heartbeat_sent(self, *, sent_at: datetime | None = None) -> None:
        now = sent_at or datetime.now()
        async with self._lock:
            self._state.last_heartbeat_at = now

    async def record_error(
        self,
        error_message: str,
        *,
        failed_status: msg_handler.MotorState = msg_handler.MotorState.ERROR,
    ) -> None:
        async with self._lock:
            self._state.motor_status = failed_status
            self._state.last_error = error_message
