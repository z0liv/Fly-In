from pydantic import BaseModel, Field


class Drone(BaseModel):
    id: int = Field(ge=1)
    current_zone: str
    in_transit_connection: str | None = None
    target_restricted_zone: str | None = None
    turns_remaining: int = Field(default=0, ge=0)
    delivered: bool = False

    @property
    def is_in_transit(self) -> bool:
        return self.turns_remaining > 0

    def format_id(self) -> str:
        return f"D{self.id}"
