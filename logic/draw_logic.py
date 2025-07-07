# logic/draw_logic.py

import json
import random
import time
from models.team_models import FixtureMatch, MatchWeek
from typing import List, Dict, Any, Set

# --- YENİ VE GARANTİLİ FİKSTÜR OLUŞTURMA BÖLÜMÜ ---

# logic/draw_logic.py dosyasındaki fonksiyon

def solve_fixture_recursive(
    matches_to_place: List[FixtureMatch],
    fixture: Dict[int, List[FixtureMatch]],
    team_schedules: Dict[str, Set[int]]
) -> bool:
    
    # --- BU SATIRI EKLE ---
    # Her 1000 denemede bir veya belirli sayıda maç kaldığında bilgi ver
    if len(matches_to_place) % 10 == 0: # Her 10 maç yerleştirildiğinde bir mesaj yazdır
        print(f"Fikstürde yerleştirilecek {len(matches_to_place)} maç kaldı...")
    # ----------------------

    if not matches_to_place:
        return True

    # ... fonksiyonun geri kalanı aynı ...
    # Yerleştirilecek ilk maçı al, geri kalanları ayır.
    match_to_place = matches_to_place[0]
    remaining_matches = matches_to_place[1:]
    
    home_team = match_to_place.home_team
    away_team = match_to_place.away_team

    # Bu maçı 1'den 8'e kadar olan haftalara yerleştirmeyi dene
    for week_num in range(1, 9):
        # Kısıtları kontrol et:
        # 1. Bu hafta dolu mu? (18 maç)
        if len(fixture[week_num]) >= 18:
            continue
        # 2. Ev sahibi takım bu hafta zaten oynuyor mu?
        if week_num in team_schedules[home_team]:
            continue
        # 3. Deplasman takımı bu hafta zaten oynuyor mu?
        if week_num in team_schedules[away_team]:
            continue

        # Tüm kontrollerden geçtiyse, maçı bu haftaya yerleştir.
        fixture[week_num].append(match_to_place)
        team_schedules[home_team].add(week_num)
        team_schedules[away_team].add(week_num)

        # Geri kalan maçları yerleştirmek için fonksiyonu tekrar çağır.
        if solve_fixture_recursive(remaining_matches, fixture, team_schedules):
            return True  # Eğer başarılı olursa, çözüm bulundu demektir.

        # EĞER BURAYA GELDİYSEK, YUKARIDAKİ YERLEŞTİRME BİR ÇIKMAZA YOL AÇTI DEMEKTİR.
        # Bu yüzden yaptığımız değişikliği geri almalıyız (Backtrack).
        fixture[week_num].remove(match_to_place)
        team_schedules[home_team].remove(week_num)
        team_schedules[away_team].remove(week_num)

    # Eğer döngü bitti ve maç hiçbir haftaya yerleştirilemediyse, bu yol yanlıştır.
    return False

def generate_fixture(draw_results: list, all_team_names: List[str]) -> List[MatchWeek]:
    print("Fikstür oluşturma işlemi başlıyor (Sistematik Yöntem)...")
    all_matches_to_schedule = []
    added_matches_check = set()

    for result in draw_results:
        team_name = result['team_name']
        for match_info in result['matches']:
            opponent_name = match_info['opponent_name']
            match_tuple = tuple(sorted((team_name, opponent_name)))
            if match_tuple in added_matches_check:
                continue
            if match_info['location'] == 'home':
                all_matches_to_schedule.append(FixtureMatch(home_team=team_name, away_team=opponent_name))
            else:
                all_matches_to_schedule.append(FixtureMatch(home_team=opponent_name, away_team=team_name))
            added_matches_check.add(match_tuple)

    random.shuffle(all_matches_to_schedule)

    # Çözücü için başlangıç yapılarını hazırla
    fixture_dict: Dict[int, List[FixtureMatch]] = {i: [] for i in range(1, 9)}
    team_schedules: Dict[str, Set[int]] = {name: set() for name in all_team_names}

    # Çözücüyü başlat
    success = solve_fixture_recursive(all_matches_to_schedule, fixture_dict, team_schedules)

    if not success:
        print("UYARI: Fikstür oluşturulamadı! Bu mantıksal bir hatayı gösterir.")
        return []

    # Sözlük formatındaki fikstürü, API'nin istediği liste formatına çevir
    final_fixture = [MatchWeek(week=w, matches=m) for w, m in fixture_dict.items()]
    print("Fikstür başarıyla ve eksiksiz oluşturuldu!")
    return final_fixture

# --- KURA ÇEKME BÖLÜMÜ (DEĞİŞİKLİK YOK) ---
def create_full_fixture() -> List[MatchWeek]:
    with open('data/teams.json', 'r', encoding='utf-8') as f:
        pots_data = json.load(f)

    all_teams: List[Dict[str, Any]] = []
    all_team_names = []
    team_id_counter = 1
    for pot_num_str, teams_in_pot in pots_data.items():
        pot_num = int(pot_num_str.split(' ')[1])
        for team_info in teams_in_pot:
            all_teams.append({
                "id": team_id_counter,
                "name": team_info["name"],
                "country": team_info["country"],
                "pot": pot_num,
                "opponents": []
            })
            all_team_names.append(team_info["name"])
            team_id_counter += 1

    # ... (Kura çekme `while` döngüsü burada başlıyor, önceki kodla aynı) ...
    attempt_count = 0
    start_time = time.time()
    while True:
        attempt_count += 1
        print(f"Kura denemesi #{attempt_count} başlıyor...")
        is_draw_possible = True
        for team in all_teams:
            team["opponents"] = []
        random.shuffle(all_teams)
        for team in all_teams:
            if not is_draw_possible: break
            opponents_needed_from_pot = {p: 2 for p in range(1, 5)}
            for opp in team["opponents"]:
                opponents_needed_from_pot[opp['pot']] -= 1
            for pot_to_draw_from in sorted(range(1, 5), key=lambda k: random.random()):
                if not is_draw_possible: break
                needed = opponents_needed_from_pot[pot_to_draw_from]
                if needed <= 0: continue
                candidates = [
                    opp for opp in all_teams
                    if opp['id'] != team['id'] and
                       opp['pot'] == pot_to_draw_from and
                       team['country'] != opp['country'] and
                       opp not in team['opponents'] and
                       len(opp['opponents']) < 8
                ]
                for _ in range(needed):
                    if not candidates:
                        is_draw_possible = False
                        break
                    best_candidate = min(candidates, key=lambda c: len(c['opponents']))
                    team['opponents'].append(best_candidate)
                    best_candidate['opponents'].append(team)
                    candidates.remove(best_candidate)
        if is_draw_possible and all(len(t['opponents']) == 8 for t in all_teams):
            print("-" * 30)
            print(f"BAŞARILI KURA BULUNDU! ({attempt_count}. denemede)")
            break
            
    # KURA BİTTİ, FİKSTÜR İÇİN VERİ HAZIRLA
    draw_results_for_fixture = []
    for team in sorted(all_teams, key=lambda x: x['id']):
        matches = []
        opponents_by_pot = {p: [] for p in range(1, 5)}
        for opp in team['opponents']:
            opponents_by_pot[opp['pot']].append(opp)
        for opponents_in_pot in opponents_by_pot.values():
            if opponents_in_pot:
                random.shuffle(opponents_in_pot)
                matches.append({'opponent_name': opponents_in_pot[0]['name'], 'location': 'home'})
                if len(opponents_in_pot) > 1:
                    matches.append({'opponent_name': opponents_in_pot[1]['name'], 'location': 'away'})
        draw_results_for_fixture.append({
            "team_name": team['name'],
            "pot": team['pot'],
            "matches": matches
        })

    # YENİ VE GARANTİLİ FİKSTÜR FONKSİYONUNU ÇAĞIR
    final_fixture = generate_fixture(draw_results_for_fixture, all_team_names)
    return final_fixture