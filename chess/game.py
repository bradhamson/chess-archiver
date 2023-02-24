from dataclasses import dataclass
from uuid import UUID

@dataclass
class Player:
    player_id: str
    user_name: str
    rating: int
    result: str

@dataclass
class Game:
    game_id: str
    url: str
    pgn_data: str
    white: Player
    black: Player
    time_control: str
    length_ms: int
