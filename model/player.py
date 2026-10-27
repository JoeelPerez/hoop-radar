from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Player:
    source_league: str
    id: str
    name: str
    birth_date: date | None = None
    nationality: str | None = None
