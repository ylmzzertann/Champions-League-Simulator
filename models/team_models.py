# models/team_models.py

from pydantic import BaseModel
from typing import List

# Bir takımın yapacağı tek bir maçı temsil eden model
class Match(BaseModel):
    opponent_name: str
    location: str # 'home' ya da 'away'


# API'den dönecek olan kura sonucunu temsil eden model
class DrawResult(BaseModel):
    team_name: str
    pot: int
    matches: List[Match]