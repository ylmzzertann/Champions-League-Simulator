# main.py

from fastapi import FastAPI
from logic.draw_logic import create_draw
from models.team_models import DrawResult
from typing import List

app = FastAPI(
    title="Champions League Simulator API",
    description="Yeni format Şampiyonlar Ligi kura çekimi ve simülasyonu."
)

@app.get("/generate-draw", response_model=List[DrawResult], tags=["Draw"])
def generate_new_draw():
    """
    Yeni Şampiyonlar Ligi formatına göre 36 takım için 8'er maçlık
    lig aşaması kurasını çeker ve eşleşmeleri döndürür.
    """
    draw_results = create_draw()
    return draw_results


@app.get("/", tags=["Root"])
def read_root():
    """
    API'nin çalıştığını gösteren başlangıç mesajı.
    """
    return {"message": "Champions League Simulator API'sine hoş geldiniz! Kura çekimi için /docs adresine gidin."}