from dataclasses import dataclass


@dataclass(frozen=True)
class Season:
    source_league: str
    end_year: int
