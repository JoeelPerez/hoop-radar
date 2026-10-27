from dataclasses import dataclass


@dataclass(frozen=True)
class StatLine:
    source_league: str
    match_id: str
    player_id: str
    club_id: str
    minutes_played: float | None = None
    points: int | None = None
    rebounds: int | None = None
    assists: int | None = None
    steals: int | None = None
    blocks: int | None = None
    turnovers: int | None = None
    personal_fouls: int | None = None
    field_goals_made: int | None = None
    field_goals_attempted: int | None = None
    three_points_made: int | None = None
    three_points_attempted: int | None = None
    free_throws_made: int | None = None
    free_throws_attempted: int | None = None
