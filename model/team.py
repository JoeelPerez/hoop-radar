from dataclasses import dataclass


@dataclass(frozen=True)
class Team:
    source_league: str
    id: str
    name: str
