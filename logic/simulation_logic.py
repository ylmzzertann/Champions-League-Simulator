# logic/simulation_logic.py

import json
import random
from typing import List, Dict, Any
from models.team_models import DrawResult, LeagueStanding

# Bu fonksiyonlarda değişiklik yok
def load_squads():
    with open('data/squads.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_team_strengths(team_name, squads):
    squad = squads.get(team_name)
    if not squad: return {"attack": 75, "defense": 75}
    attackers = [p['power'] for p in squad if p['position'] in ['FV', 'OS']]
    defenders = [p['power'] for p in squad if p['position'] in ['DF', 'KL']]
    attack_strength = sum(attackers) / len(attackers) if attackers else 75
    defense_strength = sum(defenders) / len(defenders) if defenders else 75
    return {"attack": attack_strength, "defense": defense_strength}

def simulate_match(home_team_name, away_team_name, squads):
    home_strengths = get_team_strengths(home_team_name, squads)
    away_strengths = get_team_strengths(away_team_name, squads)
    home_attack_power = home_strengths['attack'] * 1.05
    home_goals = round(((home_attack_power / away_strengths['defense']) * random.uniform(0.7, 1.3)) + random.uniform(0, 1))
    away_goals = round(((away_strengths['attack'] / home_strengths['defense']) * random.uniform(0.7, 1.3)) + random.uniform(0, 1))
    return {"home_team": home_team_name, "away_team": away_team_name, "home_goals": int(home_goals), "away_goals": int(away_goals)}


# --- BU FONKSİYON NESNELERLE ÇALIŞACAK ŞEKİLDE DÜZELTİLDİ ---
def run_league_simulation(draw_results: List[DrawResult]) -> List[dict]:
    squads = load_squads()
    
    standings = {}
    for team_draw in draw_results:
        # DÜZELTME: Artık DrawResult nesnesiyle çalışıyoruz -> team_draw.team_name
        standings[team_draw.team_name] = {
            "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0
        }

    all_matches_to_play = []
    played_match_check = set()

    for team_draw in draw_results:
        # DÜZELTME: .team_name, .matches gibi nesne özelliklerini kullanıyoruz
        team_a_name = team_draw.team_name
        for match_info in team_draw.matches:
            # DÜZELTME: .opponent_name
            team_b_name = match_info.opponent_name
            
            match_tuple = tuple(sorted((team_a_name, team_b_name)))
            if match_tuple in played_match_check:
                continue
            
            # DÜZELTME: .location
            if match_info.location == 'home':
                all_matches_to_play.append({"home": team_a_name, "away": team_b_name})
            else:
                all_matches_to_play.append({"home": team_b_name, "away": team_a_name})
            
            played_match_check.add(match_tuple)

    for match_pair in all_matches_to_play:
        result = simulate_match(match_pair['home'], match_pair['away'], squads)
        home, away = result['home_team'], result['away_team']
        home_g, away_g = result['home_goals'], result['away_goals']

        standings[home]['goals_for'] += home_g
        standings[home]['goals_against'] += away_g
        standings[away]['goals_for'] += away_g
        standings[away]['goals_against'] += home_g

        if home_g > away_g:
            standings[home]['wins'] += 1; standings[away]['losses'] += 1
        elif away_g > home_g:
            standings[away]['wins'] += 1; standings[home]['losses'] += 1
        else:
            standings[home]['draws'] += 1; standings[away]['draws'] += 1

    final_standings = []
    for team_name, stats in standings.items():
        points = (stats['wins'] * 3) + (stats['draws'] * 1)
        goal_diff = stats['goals_for'] - stats['goals_against']
        final_standings.append({
            "team_name": team_name, "played": 8, "wins": stats['wins'], "draws": stats['draws'], 
            "losses": stats['losses'], "goals_for": stats['goals_for'], "goals_against": stats['goals_against'],
            "goal_difference": goal_diff, "points": points
        })

    final_standings.sort(key=lambda x: (x['points'], x['goal_difference'], x['goals_for']), reverse=True)
    
    for i, standing in enumerate(final_standings):
        standing['rank'] = i + 1
        
    return final_standings
def get_next_stage_teams(standings: List[LeagueStanding]) -> Dict[str, List[str]]:
    """
    Sıralı puan durumunu alır ve bir sonraki aşamaya geçen takımları belirler.
    """
    team_names = [s.team_name for s in standings]
    
    result = {
        "direct_to_round_of_16": team_names[0:8],
        "playoff_round": team_names[8:24],
        "eliminated": team_names[24:36]
    }
    return result