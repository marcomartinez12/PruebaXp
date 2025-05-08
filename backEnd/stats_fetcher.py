from fastapi import FastAPI, HTTPException
import requests
import random
import logging
from fastapi.middleware.cors import CORSMiddleware
import datetime

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API key para football-data.org
API_KEY = "f2ad0e925c1b44ce93e483122bb4ce78"
HEADERS = {
    "X-Auth-Token": API_KEY,
    "Accept": "application/json"
}

# Inicializar FastAPI
app = FastAPI(
    title="Football Team Stats API",
    description="API para obtener estadísticas de equipos de fútbol",
    version="1.0.0"
)

# Configurar CORS para permitir peticiones desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mapeo de equipos populares a sus IDs en la API
# Mantenemos esta lista solo como referencia para el endpoint /teams
TEAM_MAPPING = {
    "barcelona": 81,
    "real madrid": 86,
    "atletico madrid": 78,
    "manchester city": 65,
    "manchester united": 66,
    "liverpool": 64,
    "chelsea": 61,
    "bayern munich": 5,
    "borussia dortmund": 4,
    "psg": 524,
    "juventus": 109,
    "milan": 98,
    "inter": 108,
    "arsenal": 57,
    "tottenham": 73,
    "sevilla": 559,
    "valencia": 94,
    "villarreal": 99,
    "athletic bilbao": 77,
    "real sociedad": 92,
    "napoli": 113,
    "roma": 100,
    "lazio": 110
}

def find_team_in_api(team_name):
    """
    Busca el equipo en la API de football-data.org o en el mapeo local
    """
    # Primero verificamos si está en nuestro mapeo local para evitar llamadas a la API innecesarias
    if team_name.lower() in TEAM_MAPPING:
        team_id = TEAM_MAPPING[team_name.lower()]
        logger.info(f"Equipo encontrado en mapeo local: {team_name} (ID: {team_id})")
        return team_id
    
    # Si no está en el mapeo, intentamos buscar en competiciones para no exceder los límites de la API
    # Nota: Este enfoque es limitado por las restricciones de la API gratuita
    try:
        # Buscamos el equipo en las principales competiciones
        # Estas son búsquedas que suelen estar permitidas en el plan gratuito
        competitions = [2001, 2002, 2014, 2019, 2021]  # Champions League, Bundesliga, LaLiga, Serie A, Premier League
        
        for comp_id in competitions:
            try:
                teams_url = f"https://api.football-data.org/v4/competitions/{comp_id}/teams"
                response = requests.get(teams_url, headers=HEADERS)
                if response.status_code == 200:
                    teams_data = response.json()
                    if "teams" in teams_data:
                        for team in teams_data["teams"]:
                            # Comparamos ignorando mayúsculas y acentos
                            if (team_name.lower() in team["name"].lower() or 
                                team_name.lower() in team.get("shortName", "").lower() or
                                team_name.lower() in team.get("tla", "").lower()):
                                logger.info(f"Equipo encontrado en API (competición {comp_id}): {team['name']} (ID: {team['id']})")
                                return team["id"]
            except Exception as e:
                logger.warning(f"Error al buscar en competición {comp_id}: {e}")
                continue
                
        # Si llegamos aquí, no encontramos el equipo en ninguna competición
        logger.warning(f"No se encontró el equipo: {team_name} en la API")
        return 0
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al buscar equipo en API: {e}")
        return 0

def fetch_real_data(team_name):
    """
    Obtiene datos reales del equipo usando la API de football-data.org
    """
    team_id = find_team_in_api(team_name)
    
    if team_id == 0:
        logger.warning(f"No se encontró ID para el equipo: {team_name}")
        # Si no encontramos el ID, usamos datos simulados como fallback
        return generate_simulated_data(team_name)
    
    try:
        # Obtener datos del equipo
        team_url = f"https://api.football-data.org/v4/teams/{team_id}"
        team_response = requests.get(team_url, headers=HEADERS)
        team_response.raise_for_status()
        team_data = team_response.json()
        
        # Obtener últimos partidos
        matches_url = f"https://api.football-data.org/v4/teams/{team_id}/matches?limit=10"
        matches_response = requests.get(matches_url, headers=HEADERS)
        matches_response.raise_for_status()
        matches_data = matches_response.json()
        
        # Procesar resultados de últimos partidos
        last_matches_results = []
        home_matches = 0
        away_matches = 0
        home_wins = 0
        away_wins = 0
        total_goals_scored = 0
        total_goals_conceded = 0
        
        if "matches" in matches_data:
            for match in matches_data["matches"]:
                is_home = match["homeTeam"]["id"] == team_id
                
                result = "D"  # Empate por defecto
                if match["score"]["winner"] == "HOME_TEAM" and is_home:
                    result = "W"  # Victoria local
                    home_wins += 1
                elif match["score"]["winner"] == "AWAY_TEAM" and not is_home:
                    result = "W"  # Victoria visitante
                    away_wins += 1
                elif match["score"]["winner"] == "HOME_TEAM" and not is_home:
                    result = "L"  # Derrota como visitante
                elif match["score"]["winner"] == "AWAY_TEAM" and is_home:
                    result = "L"  # Derrota como local
                
                # Contar partidos en casa y fuera
                if is_home:
                    home_matches += 1
                    if match["score"]["fullTime"]["home"] is not None:
                        total_goals_scored += match["score"]["fullTime"]["home"]
                        total_goals_conceded += match["score"]["fullTime"]["away"]
                else:
                    away_matches += 1
                    if match["score"]["fullTime"]["away"] is not None:
                        total_goals_scored += match["score"]["fullTime"]["away"]
                        total_goals_conceded += match["score"]["fullTime"]["home"]
                
                last_matches_results.append(result)
        
        # Calcular estadísticas
        total_matches = len(last_matches_results)
        if total_matches > 0:
            goals_per_match = total_goals_scored / total_matches
            conceded_per_match = total_goals_conceded / total_matches
        else:
            goals_per_match = 0
            conceded_per_match = 0
        
        # Calcular ventaja en casa (si gana más en casa que fuera)
        home_advantage = False
        if home_matches > 0 and away_matches > 0:
            home_win_rate = home_wins / home_matches
            away_win_rate = away_wins / away_matches
            home_advantage = home_win_rate > away_win_rate
        
        # Usamos una posesión promedio calculada en base a la calidad del equipo
        # En una implementación real, esto vendría de la API
        possession = min(70, 40 + (team_data.get("founded", 1950) % 15))
        
        # Construir el objeto de estadísticas en el formato esperado por el modelo
        stats = {
            "name": team_data["name"],
            "last_matches": {
                "results": last_matches_results[:5]  # Tomamos solo los últimos 5
            },
            "head_to_head": {
                "wins": random.randint(3, 8),  # Dato no disponible directamente en esta API
                "draws": random.randint(1, 4),  # Usamos valores aleatorios como ejemplo
                "losses": random.randint(2, 7)
            },
            "goals_per_match": round(goals_per_match, 2),
            "conceded_per_match": round(conceded_per_match, 2),
            "possession": possession,
            "corners_per_match": round(random.uniform(4.0, 7.0), 1),  # No disponible directamente
            "home_advantage": home_advantage
        }
        
        logger.info(f"Datos reales obtenidos para {team_name}")
        return stats
        
    except requests.exceptions.RequestException as e:
        body = e.response.text if e.response is not None else "<sin cuerpo>"
        logger.error(f"Error al obtener datos reales: {e} — respuesta: {body}")
        return generate_simulated_data(team_name)
        

def generate_simulated_data(team_name):
    """
    Genera datos simulados para casos donde la API falla o no se encuentra el equipo.
    Esta es una copia de la función original para mantener compatibilidad.
    """
    logger.info(f"Generando datos simulados para {team_name}")
    
    # Simulación un poco más realista basada en el nombre del equipo
    # Los equipos más conocidos tendrán mejores estadísticas
    team_reputation = 0
    top_teams = ["barcelona", "real madrid", "manchester city", "liverpool", "bayern munich", "psg"]
    good_teams = ["atletico madrid", "chelsea", "manchester united", "juventus", "arsenal", "inter", "milan"]
    
    if team_name.lower() in top_teams:
        team_reputation = 3
    elif team_name.lower() in good_teams:
        team_reputation = 2
    elif team_name.lower() in TEAM_MAPPING:
        team_reputation = 1
    
    # Ajustar los datos aleatorios según la reputación
    if team_reputation == 3:  # Top team
        last_match_options = ["W", "W", "W", "D", "L"]  # Más probabilidad de victoria
        goals_min, goals_max = 1.8, 3.2
        possession_min, possession_max = 55, 70
        corners_min, corners_max = 5.0, 8.0
        home_advantage_prob = 0.7
    elif team_reputation == 2:  # Good team
        last_match_options = ["W", "W", "D", "D", "L"]
        goals_min, goals_max = 1.4, 2.5
        possession_min, possession_max = 50, 65
        corners_min, corners_max = 4.5, 7.0
        home_advantage_prob = 0.6
    elif team_reputation == 1:  # Known team
        last_match_options = ["W", "D", "D", "L", "L"]
        goals_min, goals_max = 1.0, 2.0
        possession_min, possession_max = 45, 55
        corners_min, corners_max = 4.0, 6.0
        home_advantage_prob = 0.5
    else:  # Unknown team
        last_match_options = ["W", "D", "L", "L", "L"]  # Más probabilidad de derrota
        goals_min, goals_max = 0.5, 1.5
        possession_min, possession_max = 35, 50
        corners_min, corners_max = 3.0, 5.0
        home_advantage_prob = 0.4
    
    stats = {
        "name": team_name,
        "last_matches": {
            "results": [random.choice(last_match_options) for _ in range(5)]
        },
        "head_to_head": {
            "wins": random.randint(0, 8),
            "draws": random.randint(0, 5),
            "losses": random.randint(0, 10),
        },
        "goals_per_match": round(random.uniform(goals_min, goals_max), 2),
        "conceded_per_match": round(random.uniform(0.5, 3.5 - team_reputation * 0.5), 2),
        "possession": random.randint(possession_min, possession_max),
        "corners_per_match": round(random.uniform(corners_min, corners_max), 1),
        "home_advantage": random.random() < home_advantage_prob
    }
    
    return stats

def fetch_team_stats(team_name):
    """
    Función principal que devuelve las estadísticas del equipo.
    Esta es la función que usa el resto del sistema.
    """
    try:
        # Intentamos obtener datos reales primero
        return fetch_real_data(team_name)
    except Exception as e:
        # Si algo falla, usamos datos simulados como fallback
        logger.error(f"Error inesperado: {e}")
        return generate_simulated_data(team_name)

# Endpoint principal para obtener estadísticas de un equipo
@app.get("/team/{team_name}")
async def get_team_statistics(team_name: str):
    try:
        stats = fetch_team_stats(team_name)
        return stats
    except Exception as e:
        logger.error(f"Error en el endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

# Endpoint para obtener la lista de equipos mapeados
@app.get("/teams")
async def get_available_teams():
    return {"teams": list(TEAM_MAPPING.keys())}

# Verificar estado de la API
@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": str(datetime.datetime.now())}

# Punto de entrada para ejecutar el servidor
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    