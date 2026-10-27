from dataclasses import dataclass


@dataclass(frozen=True)
class Club:
    source_league: str
    id: str
    name: str
