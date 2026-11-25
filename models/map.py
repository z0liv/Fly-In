from models import Zone, ZoneType, Connection
from pydantic import (BaseModel, Field, model_validator)


class Map(BaseModel):
    nb_drones: int = Field(ge=1)
    zones: dict[str, Zone] = Field(default_factory = dict)
    connections: list[Connection] = Field(default_factory=list)
    start_zone: str = ""
    end_zone: str = ""
    adjacency: dict[str, list[Connection]] = Field(default_factory=dict, exclude=True)

    @model_validator(mode="after")
    def build_and_validate_graph(self) -> "Map":
        starts = [z.name for z in self.zones.values() if z.is_start]
        ends = [z.name for z in self.zones.values() if z.is_end]

        if len(starts) != 1:
            raise ValueError(f"It should be only one start_hub (found: {len(starts)})")
        if len(ends) != 1:
            raise ValueError(f"It should be only one end_hub (found: {len(starts)})")

        self.start_zone = starts[0]
        self.end_zone = ends[0]

        self.adjacency = {zone_name: [] for zone_name in self.zones}
        seen_connections: set[tuple[str, str]] = set()

        for conn in self.connections:
            if conn.zone_a not in self.zones or conn.zone_b not in self.zones:
                raise ValueError(f"Connection to an unexistent zone: {conn.zone_a}-{conn.zone_b}")

        cid = conn.canonical_id
        if cid in seen_connections:
            raise ValueError(f"Duplicated connection: {conn.zone_a}-{conn.zone_b}")
        seen_connections.add(cid)

        self.adjacency[conn.zone_a].append(conn)
        self.adjacency[conn.zone_b].append(conn)
        
        return self

    def get_neighbors(self, zone_name: str) -> list[tuple[Zone, Connection]]:
        neighbors: list[tuple[Zone, Connection]] = []
        for conn in self.adjacency.get(zone_name, []):
            target_name = conn.zone_b if conn.zone_a == zone_name else conn.zone_a
            target_zone = self.zones[target_name]
            if target_zone.zone_type != ZoneType.BLOCKED:
                neighbors.append((target_zone, conn))
        return neighbors
