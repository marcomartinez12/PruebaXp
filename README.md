# XplainBet

XplainBet es una plataforma de análisis de apuestas deportivas donde un chatbot utiliza modelos matemáticos para predecir los resultados de partidos basándose en estadísticas.

## Características

- Interfaz de chat intuitiva
- Análisis estadístico de equipos deportivos
- Predicciones basadas en datos como últimos 5 partidos, enfrentamientos directos, goles por partido, posesión y más
- Recomendaciones de apuestas
- Visualización gráfica de probabilidades

## Tecnologías

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (Flask)
- **APIs**: El sistema está preparado para integrarse con APIs de estadísticas deportivas

## Requisitos

### Backend
- Python 3.8+
- Flask
- Otras dependencias listadas en `backend/requirements.txt`

### Frontend
- Navegador web moderno

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tuusuario/xplainbet.git
cd xplainbet
```

2. Instalar dependencias del backend:
```bash
cd backend
pip install -r requirements.txt
```

3. Ejecutar el servidor:
```bash
python app.py
```

4. Abrir el archivo `frontend/templates/index.html` en un navegador o configurar un servidor web para servir los archivos frontend.

## Uso

1. Ingresa los nombres de dos equipos en los campos correspondientes
2. Haz clic en "Predecir"
3. El sistema analizará las estadísticas y mostrará las predicciones
4. Revisa las probabilidades y la recomendación de apuesta

## Estructura del Proyecto

```
xplainbet/
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   └── main.js
│   │   └── img/
│   │       ├── logo.svg
│   │       └── favicon.ico
│   └── templates/
│       └── index.html
├── backend/
│   ├── app.py
│   ├── prediction_model.py
│   ├── stats_fetcher.py
│   └── requirements.txt
├── .gitignore
└── README.md
```

## Futuras Mejoras

- Integración con APIs reales de estadísticas deportivas
- Soporte para más deportes y ligas
- Historial de predicciones
- Modelo de aprendizaje automático para mejorar las predicciones con el tiempo

## Licencia

MIT License