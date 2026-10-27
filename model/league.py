from dataclasses import dataclass


@dataclass(frozen=True)
class League:
    id: str
    name: str
