# models/team_models.py

from pydantic import BaseModel, Field
from typing import List

# Bu modeller aynı kalıyor
class Match(BaseModel):
    opponent_name: str
    location: str

class DrawResult(BaseModel):
    team_name: str
    pot: int
    matches: List[Match]

class LeagueStanding(BaseModel):
    rank: int
    team_name: str
    played: int = 8
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int

# --- YENİ EKLENEN MODEL ---
# Lig aşaması sonrası durumu gösteren model
class NextStageResult(BaseModel):
    direct_to_round_of_16: List[str] = Field(..., description="Doğrudan Son 16'ya kalan ilk 8 takım")
    playoff_round: List[str] = Field(..., description="Play-off oynayacak olan 9-24 arası takımlar")
    eliminated: List[str] = Field(..., description="Turnuvadan elenen son 12 takım")