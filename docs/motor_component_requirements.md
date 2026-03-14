# Motor Component Requirements

## Background

This document summarizes the expected behavior of the motor-side component based on the current `capstone-center` implementation.

Reference files that informed this summary:

- `capstone-center/src/capstone_center/motor_sender_processor.py`
- `capstone-center/src/capstone_center/msg_recv_processor.py`
- `capstone-center/src/capstone_center/sensor_information_processor.py`
- `wheelchoke-system-communication-system/src/msg_handler/schemas.py`

## Confirmed Interface From Center

- `capstone-center` publishes `msg_handler.MotorMessage` to the motor endpoint.
- The motor command is event-driven when sensor-derived state changes.
- The same command is also re-sent periodically to tolerate PUB/SUB slow-joiner timing.
- The periodic resend interval comes from `motor.looptime`.
- `MotorMessage` includes:
  - `sender_id`
  - `timestamp`
  - `is_override_mode`
  - `ordered_mode`
- The center currently decides the motor order already.
- The motor component does not need to re-derive human presence.

## Confirmed Return Path To Center

- `capstone-center` receives heartbeats and generic status updates through the shared subscriber path used for component telemetry.
- The center-side receiver handles those as `msg_handler.SensorMessage`.
- For heartbeat-like traffic, the relevant payload type is `msg_handler.HeartBeatPayload`.
- A motor component heartbeat should therefore be sent as:
  - envelope: `msg_handler.SensorMessage`
  - `data_type`: `"heartbeat"`
  - payload: `msg_handler.HeartBeatPayload`

## Functional Requirements

- Subscribe to the motor command endpoint published by `capstone-center`.
- Accept `MotorMessage` messages and parse `ordered_mode`.
- Treat repeated commands as normal because `capstone-center` intentionally retries the latest command periodically.
- Keep track of the latest requested motor order and the latest known motor status.
- Execute the requested motion through a dedicated motor-control class.
- Send heartbeat messages periodically even when no new command arrives.
- Include the current motor status in heartbeat payloads so `capstone-center` can treat the motor like any other component.
- Preserve the incoming `is_override_mode` flag in local state for diagnostics and future policy hooks.
- Keep network transport, orchestration, and direct motor I/O separated.

## Non-Goals For This Component

- Recomputing whether a human is present.
- Deciding whether the motor should deploy or fold.
- Publishing display messages.
- Owning center-side timeout logic.

## Expected Runtime Flow

1. The command receiver subscribes to the center motor endpoint.
2. A `MotorMessage` arrives.
3. The component records the requested order in runtime state.
4. The command service asks the motor-control class to apply the order.
5. The motor-control class performs the direct hardware action.
6. The resulting status is written back into runtime state.
7. The heartbeat publisher periodically snapshots runtime state and sends `SensorMessage(data_type="heartbeat")` back to the center input endpoint.

## Design Constraints

- The class that directly drives GPIO, serial, CAN, or other motor hardware must be isolated in one place.
- Duplicate commands must be safe because periodic retries are part of the center contract.
- The component should remain async-friendly because the center side is async and PUB/SUB based.
- Future concrete hardware work should fit inside the motor-control class without forcing transport code to change.

## Proposed Module Split

- `config.py`
  - local component config loading and ZMQ option builders
- `models.py`
  - runtime dataclasses and heartbeat status helpers
- `state_store.py`
  - async-safe runtime state access
- `motor_driver.py`
  - the only class that should contain direct motor hardware code
- `services.py`
  - command application logic and state transitions
- `command_receiver.py`
  - subscribes to `MotorMessage`
- `heartbeat_publisher.py`
  - publishes periodic heartbeat/status messages
- `app.py`
  - wires the async tasks together
- `main.py`
  - entrypoint and dependency assembly

## Open Assumptions To Confirm Later

- Whether the motor heartbeat should use a dedicated sender ID like `motor-1` or a deployment-specific ID.
- The final mapping from motor state to numeric heartbeat status code.
- Whether direct motor actuation is GPIO, serial, CAN, or another hardware interface.
- Whether the motor component also needs to publish a one-shot status update immediately after command completion, in addition to the regular heartbeat.
