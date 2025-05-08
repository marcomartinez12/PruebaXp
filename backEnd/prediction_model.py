import numpy as np


def predict_winner(team1_name, team1_stats, team2_name, team2_stats):
    """
    Modelo de predicción basado en estadísticas de los equipos.
    Devuelve las probabilidades de victoria para cada equipo.
    """
    
    # Calcular puntuación para cada equipo
    team1_score = calculate_team_score(team1_stats)
    team2_score = calculate_team_score(team2_stats)
    
    # Normalizar y convertir a probabilidades
    total_score = team1_score + team2_score
    if total_score == 0:
        # Evitar división por cero: repartir equitativamente
        team1_prob = team2_prob = 45.0
        draw_prob = 10.0
    else:
        team1_prob = round((team1_score / total_score) * 100, 1)
        team2_prob = round((team2_score / total_score) * 100, 1)
        draw_prob = round(100 - team1_prob - team2_prob, 1)
    
    # Asegurar que el empate tenga un valor mínimo
    if draw_prob < 10:
        draw_prob = 10.0
        factor = (100 - draw_prob) / (team1_prob + team2_prob)
        team1_prob = round(team1_prob * factor, 1)
        team2_prob = round(team2_prob * factor, 1)
    
    return {
        "prediction": {
            "team1": {"name": team1_name, "win_probability": team1_prob},
            "team2": {"name": team2_name, "win_probability": team2_prob},
            "draw_probability": draw_prob
        },
        "key_stats": {
            "team1": extract_key_stats(team1_stats),
            "team2": extract_key_stats(team2_stats)
        },
        "recommendation": get_betting_recommendation(
            team1_name, team1_prob, team2_name, team2_prob, draw_prob
        )
    }


def calculate_team_score(stats):
    """
    Calcula una puntuación basada en las estadísticas del equipo.
    """
    score = 0
    
    # Últimos 5 partidos: stats["last_matches"]["results"] es lista de 'W','D','L'
    results = stats.get("last_matches", {}).get("results", [])
    for result in results:
        if result == "W":
            score += 3
        elif result == "D":
            score += 1
    
    # Goles por partido
    score += stats.get("goals_per_match", 0) * 2
    
    # Posesión
    score += stats.get("possession", 0) * 0.05
    
    # Córners por partido
    score += stats.get("corners_per_match", 0) * 0.2
    
    # Ventaja de local
    if stats.get("home_advantage", False):
        score *= 1.1
    
    return score


def extract_key_stats(stats):
    """
    Extrae estadísticas clave para mostrar en la interfaz.
    """
    return {
        "form": stats.get("last_matches", {}).get("results", []),
        "goals_per_match": stats.get("goals_per_match", 0),
        "possession": stats.get("possession", 0),
        "corners_per_match": stats.get("corners_per_match", 0)
    }


def get_betting_recommendation(team1_name, team1_prob, team2_name, team2_prob, draw_prob):
    """
    Genera una recomendación de apuesta basada en las probabilidades.
    """
    threshold = 60  # Umbral para considerar una apuesta segura
    
    if team1_prob > threshold:
        return f"Apuesta recomendada: Victoria de {team1_name}"
    elif team2_prob > threshold:
        return f"Apuesta recomendada: Victoria de {team2_name}"
    elif draw_prob > 30:
        return "Apuesta recomendada: Empate"
    else:
        return "Partido muy equilibrado, se recomienda precaución al apostar"
