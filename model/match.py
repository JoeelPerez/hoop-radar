from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Match:
    source_league: str
    id: str
    season_end_year: int
    home_team_id: str
    away_team_id: str
    played: bool
    competition_phase: str | None = None
    scheduled_at: datetime | None = None
    home_score: int | None = None
    away_score: int | None = None
