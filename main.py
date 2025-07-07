# main.py

from fastapi import FastAPI
from logic.draw_logic import create_full_fixture
from models.team_models import MatchWeek
from typing import List

app = FastAPI(
    title="Champions League Simulator API",
    description="Yeni format Şampiyonlar Ligi kura çekimi ve simülasyonu."
)

@app.get("/generate-fixture", response_model=List[MatchWeek], tags=["Fixture"])
def generate_new_fixture():
    """
    Önce lig aşaması kurasını çeker, ardından 8 haftalık tam fikstürü oluşturur.
    """
    full_fixture = create_full_fixture()
    return full_fixture

@app.get("/", tags=["Root"])
def read_root():
    """
    API'nin çalıştığını gösteren başlangıç mesajı.
    """
    return {"message": "Champions League Simulator API'sine hoş geldiniz! Fikstür oluşturmak için /docs adresine gidin."}