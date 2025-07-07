# models/team_models.py

from pydantic import BaseModel
from typing import List

# Bir haftadaki tek bir maçı temsil eder
class FixtureMatch(BaseModel):
    home_team: str
    away_team: str

# Bir maç haftasını temsil eder
class MatchWeek(BaseModel):
    week: int
    matches: List[FixtureMatch]