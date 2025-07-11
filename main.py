# main.py

from fastapi import FastAPI, Body
from typing import List
from logic.draw_logic import create_draw
from logic.simulation_logic import run_league_simulation, get_next_stage_teams
from models.team_models import DrawResult, LeagueStanding, NextStageResult

app = FastAPI(
    title="Champions League Simulator - Adım Adım",
    description="Şampiyonlar Ligi simülasyonunu adım adım çalıştırın."
)

# --- ADIM 1: KURA ÇEKİMİ ---
@app.get("/generate-draw", 
         response_model=List[DrawResult], 
         tags=["Adım 1: Kura Çekimi"],
         summary="1. Adım: 36 takım için 8'er rakip belirle.")
def generate_new_draw():
    """
    Tüm takımlar için 8'er rakip ve ev/deplasman durumlarını belirleyen
    lig aşaması kurasını çeker. Bir sonraki adıma geçmek için bu adımın
    çıktısını kopyalayın.
    """
    return create_draw()

# --- ADIM 2: MAÇ SİMÜLASYONU VE PUAN DURUMU ---
@app.post("/run-simulation", 
          response_model=List[LeagueStanding], 
          tags=["Adım 2 & 3: Simülasyon ve Puan Durumu"],
          summary="2. Adım: Eşleşmeleri simüle et ve puan durumunu al.")
def run_simulation(draw_results: List[DrawResult] = Body(...)):
    """
    1. Adım'dan alınan kura sonuçlarını kullanarak tüm maçları simüle eder
    ve sıralı nihai puan durumunu oluşturur. Bir sonraki adıma geçmek için
    bu adımın çıktısını kopyalayın.
    """
    return run_league_simulation(draw_results)

# --- ADIM 3: ÜST TUR ANALİZİ ---
@app.post("/determine-next-stage", 
          response_model=NextStageResult, 
          tags=["Adım 4: Üst Tur Analizi"],
          summary="3. Adım: Puan durumuna göre üst tura çıkanları belirle.")
def determine_next_stage(standings: List[LeagueStanding] = Body(...)):
    """
    2. Adım'dan alınan puan durumuna göre doğrudan Son 16'ya kalanları,
    play-off oynayacakları ve elenenleri gruplandırır.
    """
    return get_next_stage_teams(standings)

@app.get("/", tags=["Başlangıç"])
def read_root():
    return {"message": "Adım adım simülasyon için /docs adresine gidin."}