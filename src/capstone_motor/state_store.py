from dataclasses import dataclass
from enum import Enum

try:
    from enum import StrEnum
except ImportError:
    class StrEnum(str, Enum):
        pass


class MotorOrder(StrEnum):
    FOLDING = "Folding"
    DEPLOYING = "Deploying"


class MotorStatus(StrEnum):
    DEAD = "DEAD"
    ERROR = "ERROR"
    WARN = "WARN"
    DEPLOYED = "DEPLOYED"
    DEPLOYING = "DEPLOYING"
    FOLDING = "FOLDING"
    FOLDED = "FOLDED"
    OK = "OK"
    STARTING = "STARTING"


@dataclass(slots=True)
class RuntimeState:
    motor_order: MotorOrder | str = MotorOrder.FOLDING
    motor_status: MotorStatus | str = MotorStatus.STARTING

    def __post_init__(self) -> None:
        self.motor_order = MotorOrder(self.motor_order)
        self.motor_status = MotorStatus(self.motor_status)
