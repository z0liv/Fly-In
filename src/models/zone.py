from enum import Enum
from pydantic import (BaseModel, Field, field_validator, ConfigDict)


class ZoneType(Enum):
    NORMAL = "normal"
    RESTRICTED = "restricted"
    PRIORITY = "priority"
    BLOCKED = "blocked"

    @property
    def move_cost(self) -> int:
        if self == ZoneType.RESTRICTED:
            return 2
        if self == ZoneType.BLOCKED:
            raise ValueError("Cannot calculate cost to a blocked zone")
        return 1


class Zone(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    x: int
    y: int
    type: ZoneType = ZoneType.NORMAL
    color: str | None = None
    max_drones: int = Field(default=1, ge=1)
    is_start: bool = False
    is_end: bool = False

    @field_validator("name")
    @classmethod
    def validate_name(cls, n: str) -> str:
        if not n or "-" in n or " " in n:
            suffix: str = "Can't contain dashes or whitespaces"
            raise ValueError(f"Invalid zone name: '{n}'." + suffix)
        return n

    @property
    def effective_capacity(self) -> float:
        if self.is_start or self.is_end:
            return float("inf")
        return float(self.max_drones)
