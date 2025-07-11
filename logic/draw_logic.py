# logic/draw_logic.py

import json
import random
from models.team_models import Match, DrawResult
from typing import List, Dict, Any

def create_draw() -> List[DrawResult]:
    with open('data/teams.json', 'r', encoding='utf-8') as f:
        pots_data = json.load(f)

    all_teams: List[Dict[str, Any]] = []
    team_id_counter = 1
    for pot_num_str, teams_in_pot in pots_data.items():
        pot_num = int(pot_num_str.split(' ')[1])
        for team_info in teams_in_pot:
            all_teams.append({
                "id": team_id_counter, "name": team_info["name"], "country": team_info["country"],
                "pot": pot_num, "opponents": []
            })
            team_id_counter += 1

    attempt_count = 0
    while True:
        attempt_count += 1
        if attempt_count > 1 and attempt_count % 20000 == 0:
            print(f"Kura denemesi #{attempt_count}...")

        is_draw_possible = True
        for team in all_teams: team["opponents"] = []
        random.shuffle(all_teams)

        for team in all_teams:
            if not is_draw_possible: break
            opponents_needed_from_pot = {p: 2 for p in range(1, 5)}
            for opp in team["opponents"]: opponents_needed_from_pot[opp['pot']] -= 1
            for pot_to_draw_from in sorted(range(1, 5), key=lambda k: random.random()):
                if not is_draw_possible: break
                needed = opponents_needed_from_pot[pot_to_draw_from]
                if needed <= 0: continue
                candidates = [
                    opp for opp in all_teams
                    if opp['id'] != team['id'] and opp['pot'] == pot_to_draw_from and
                       team['country'] != opp['country'] and opp not in team['opponents'] and
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
            print(f"BAŞARILI KURA BULUNDU! ({attempt_count}. denemede)")
            break
            
    final_draw = []
    for team in sorted(all_teams, key=lambda x: x['id']):
        matches = []
        opponents_by_pot = {p: [] for p in range(1, 5)}
        for opp in team['opponents']: opponents_by_pot[opp['pot']].append(opp)
        for opponents_in_pot in opponents_by_pot.values():
            if opponents_in_pot:
                random.shuffle(opponents_in_pot)
                matches.append(Match(opponent_name=opponents_in_pot[0]['name'], location='home'))
                if len(opponents_in_pot) > 1:
                    matches.append(Match(opponent_name=opponents_in_pot[1]['name'], location='away'))
    
        final_draw.append(DrawResult(
            team_name=team['name'], pot=team['pot'],
            matches=sorted(matches, key=lambda x: x.location, reverse=True)
        ))
    return final_draw