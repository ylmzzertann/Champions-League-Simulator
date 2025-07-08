# logic/draw_logic.py

import json
import random
import time
from models.team_models import Match

def create_draw():
    # Takım verilerini JSON dosyasından yükle
    with open('data/teams.json', 'r', encoding='utf-8') as f:
        pots_data = json.load(f)

    # Veriyi işlemek için daha esnek olan dictionary listesi oluştur
    all_teams = []
    team_id_counter = 1
    for pot_num_str, teams_in_pot in pots_data.items():
        pot_num = int(pot_num_str.split(' ')[1])
        for team_info in teams_in_pot:
            all_teams.append({
                "id": team_id_counter,
                "name": team_info["name"],
                "country": team_info["country"],
                "pot": pot_num,
                "opponents": [] # Her denemede sıfırlanacak geçici rakip listesi
            })
            team_id_counter += 1

    attempt_count = 0
    start_time = time.time()

    # Başarılı bir kura bulunana kadar denemeye devam et
    while True:
        attempt_count += 1
        print(f"Kura denemesi #{attempt_count} başlıyor...")

        # Her denemede tüm takımların rakip listesini sıfırla
        is_draw_possible = True
        for team in all_teams:
            team["opponents"] = []
        
        # Takımları rastgele bir sırayla eşleştirmek, kilitlenme olasılığını azaltır
        random.shuffle(all_teams)

        for team in all_teams:
            # Bu takım için her torbadan 2 rakip bulmaya çalış
            # Zaten atanmış rakipleri sayarak başla
            opponents_needed_from_pot = {p: 2 for p in range(1, 5)}
            for opp in team["opponents"]:
                opponents_needed_from_pot[opp['pot']] -= 1
            
            # Tüm torbaları gezerek rakip ara
            for pot_to_draw_from in sorted(range(1, 5), key=lambda k: random.random()):
                
                needed = opponents_needed_from_pot[pot_to_draw_from]
                if needed <= 0:
                    continue

                # Geçerli adayları bul
                candidates = [
                    opp for opp in all_teams
                    if opp['id'] != team['id'] and                         # Kendisiyle oynamasın
                       opp['pot'] == pot_to_draw_from and                 # Hedef torbada olsun
                       team['country'] != opp['country'] and              # Aynı ülkeden olmasın
                       opp not in team['opponents'] and                   # Zaten rakip olarak eklenmemiş olsun
                       len(opp['opponents']) < 8                          # Rakibin fikstürü dolmamış olsun
                ]
                
                # Bu torbadan gereken sayıda rakip ekle
                for _ in range(needed):
                    if not candidates:
                        is_draw_possible = False
                        break
                    
                    # En uygun adayı seç (en az rakibi olanı seçmek iyi bir strateji olabilir)
                    best_candidate = min(candidates, key=lambda c: len(c['opponents']))
                    
                    team['opponents'].append(best_candidate)
                    best_candidate['opponents'].append(team)
                    candidates.remove(best_candidate) # Adaylar arasından çıkar
            
            if not is_draw_possible:
                break
        
        # Tüm takımların 8 rakibi var mı kontrol et
        if is_draw_possible and all(len(t['opponents']) == 8 for t in all_teams):
            print("-" * 30)
            print(f"BAŞARILI KURA BULUNDU! ({attempt_count}. denemede)")
            print(f"İşlem {time.time() - start_time:.2f} saniye sürdü.")
            print("-" * 30)
            break # Ana while döngüsünü sonlandır
        
    # Başarılı kurayı işleyip sonuca çevirr
    final_draw = []
    for team in sorted(all_teams, key=lambda x: x['id']):
        matches = []
        opponents_by_pot = {p: [] for p in range(1, 5)}
        for opp in team['opponents']:
            opponents_by_pot[opp['pot']].append(opp)
        
        for pot_num, opponents_in_pot in opponents_by_pot.items():
            if opponents_in_pot:
                random.shuffle(opponents_in_pot)
                matches.append(Match(opponent_name=opponents_in_pot[0]['name'], location='home'))
                if len(opponents_in_pot) > 1:
                    matches.append(Match(opponent_name=opponents_in_pot[1]['name'], location='away'))
    
        final_draw.append({
            "team_name": team['name'],
            "pot": team['pot'],
            "matches": sorted(matches, key=lambda x: x.location, reverse=True)
        })

    return final_draw