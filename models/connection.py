from pydantic import (BaseModel, Field, model_validator)


class Connection(BaseModel):
    zone_a: str
    zone_b: str
    max_link_capacity: int = Field(default=1, ge=1)

    @model_validator(mode="after")
    def validate_distinct_zones(self) -> "Connection":
        if self.zone_a == self.zone_b:
            raise ValueError("Zones cannot be connected to themselves.")
        return self

    @property
    def canonical_id(self) -> tuple[str, str]:
        return (min(self.zone_a, self.zone_b), max(self.zone_a, self.zone_b))

    def format_output(self, target_zone: str) -> str:
        origin = self.zone_b if target_zone == self.zone_a else self.zone_a
        return f"{origin}-{target_zone}"
