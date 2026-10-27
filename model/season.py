from dataclasses import dataclass


@dataclass(frozen=True)
class Season:
    source_league: str
    year: int
