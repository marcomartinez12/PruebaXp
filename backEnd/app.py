from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from stats_fetcher import fetch_team_stats
from prediction_model import predict_winner
import os

# Inicializar FastAPI
app = FastAPI(
    title="Football Prediction API",
    description="API para predicción de partidos de fútbol con front-end estático servido por FastAPI",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas de front-end
BASE_DIR = os.path.dirname(__file__)
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, '../frontEnd'))

# Montar carpeta estática
app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, 'static')), name="static")

# Servir index.html
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(FRONTEND_DIR, 'index.html')
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="Front-end not found")
    return FileResponse(index_path)

# Endpoint de predicción
@app.post("/api/predict")
async def get_prediction(request: Request):
    data = await request.json()
    team1 = data.get('team1')
    team2 = data.get('team2')

    if not team1 or not team2:
        raise HTTPException(status_code=400, detail="Se requieren dos equipos")

    try:
        team1_stats = fetch_team_stats(team1)
        team2_stats = fetch_team_stats(team2)
        prediction = predict_winner(team1, team1_stats, team2, team2_stats)
        return JSONResponse(content=prediction)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check
@app.get("/health")
async def health_check():
    from datetime import datetime
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
