from pydantic import ValidationError
from .models import Zone, Connection, Map


class MapParserError(Exception):
    def __init__(self, line: int, message: str) -> None:
        super().__init__(f"Error in line {line}: {message}")


def unpack_metadata(raw_meta: str, l_index: int) -> dict[str, str]:
    raw_meta = raw_meta.strip()
    if not raw_meta:
        return {}

    if not (raw_meta.startswith("[") and raw_meta.endswith("]")):
        raise MapParserError(
            l_index, f"Malformed metadata (missing brackets): '{raw_meta}'.")

    inner = raw_meta[1:-1].strip()
    if not inner:
        return {}

    parsed: dict[str, str] = {}
    for token in inner.split():
        if "=" not in token:
            raise MapParserError(
                l_index,
                f"Invalid tag '{token}', expected 'key=value' syntax.")
        key, value = token.split("=", 1)
        if not key or not value:
            raise MapParserError(
                l_index, f"Key or value empty in '{token}'")
        if key in parsed:
            raise MapParserError(
                l_index, f"Duplicated tag '{key}' en metadata")
        parsed[key] = value
    return parsed


def parse_nb_drones(line: str, l_index: int) -> int:
    _, value = line.split(":")
    i_value = int(value)
    if i_value < 1:
        raise MapParserError(
            l_index, "nb_drones should be a positive integer greater than 0")
    return int(i_value)


def parse_zones(line: str, l_index: int) -> Zone:
    key, data = line.split(":")
    if "[" in data:
        name, x_str, y_str, metadata = data.strip().split(" ")
        d_meta = unpack_metadata(metadata, l_index)
        if key == "start_hub":
            zone = Zone(
                name=name, x=int(x_str), y=int(y_str),
                is_start=True, **d_meta)
        elif key == "end_hub":
            zone = Zone(
                name=name, x=int(x_str), y=int(y_str),
                is_end=True, **d_meta)
        else:
            zone = Zone(name=name, x=int(x_str), y=int(y_str), **d_meta)
        return zone
    else:
        name, x_str, y_str = data.strip().split(" ")
        if key == "start_hub":
            zone = Zone(name=name, x=int(x_str), y=int(y_str), is_start=True)
        elif key == "end_hub":
            zone = Zone(name=name, x=int(x_str), y=int(y_str), is_end=True)
        else:
            zone = Zone(name=name, x=int(x_str), y=int(y_str))
        return zone


def parse_connections(line: str, l_index: int) -> Connection:
    _, data = line.split(":")
    if "[" in data:
        zone_a, zone_b = data.split("-")
        zone_b, metadata = zone_b.strip().split(" ")
        d_meta = unpack_metadata(metadata, l_index)
        conn = Connection(
            zone_a=zone_a.strip(),
            zone_b=zone_b.strip(),
            **d_meta)
        return conn
    else:
        zone_a, zone_b = data.split("-")
        conn = Connection(zone_a=zone_a.strip(), zone_b=zone_b.strip())
        return conn


def parse_map(filename: str) -> Map:
    nb_drones: int | None = None
    zones: dict[str, Zone] = {}
    connections: list[Connection] = []
    try:
        with open(filename, "r") as file:
            for l_index, raw_line in enumerate(file, start=1):
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if nb_drones is None:
                    if not line.startswith("nb_drones:"):
                        msg = "The first line must define "
                        suffix = "'nb_drones: <positive int>'."
                        raise MapParserError(l_index, msg + suffix)
                    nb_drones = parse_nb_drones(line, l_index)
                    continue
                try:
                    if line.startswith(("start_hub:", "end_hub:", "hub:")):
                        zone = parse_zones(line, l_index)
                        if zone.name in zones:
                            raise MapParserError(
                                l_index,
                                f"Duplicated zone: '{zone.name}'.")
                        zones[zone.name] = zone
                    elif line.startswith("connection:"):
                        conn = parse_connections(line, l_index)
                        if (conn.zone_a not in zones
                                or conn.zone_b not in zones):
                            raise MapParserError(
                                l_index,
                                f"Connection '{conn.zone_a}-{conn.zone_b}'"
                                + "references an undefined zone.")
                        connections.append(conn)
                    else:
                        raise MapParserError(
                            l_index,
                            f"Unknown instruction: '{line}'.")
                except ValidationError as error:
                    raise MapParserError(
                        l_index, str(error.errors()[0]["msg"])) from error
    except OSError as error:
        raise MapParserError(0, f"Couldn't open the file: {error}")

    if nb_drones is None:
        raise MapParserError(
            0,
            "Empty file or it doesn't have nb_drones definition: '{s}'")
    try:
        return Map(nb_drones=nb_drones, zones=zones, connections=connections)
    except ValidationError as error:
        raise MapParserError(0, str(error.errors()[0]["msg"])) from error
