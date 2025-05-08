// DEBUG: comprobar que el script se carga
console.log('✔ main.js cargado ✅');

// Constantes
const API_URL = '/api/predict';    // Relativo al mismo origen
const ANIMATION_DELAY = 500;       // ms

// Elementos del DOM
const chatBox            = document.getElementById('chatBox');
const team1Input         = document.getElementById('team1');
const team2Input         = document.getElementById('team2');
const predictBtn         = document.getElementById('predictBtn');
const resultsContainer   = document.getElementById('resultsContainer');

const matchInfo          = document.getElementById('matchInfo');
const predTeam1Name      = document.getElementById('predTeam1Name');
const predTeam2Name      = document.getElementById('predTeam2Name');
const team1Prob          = document.getElementById('team1Prob');
const drawProb           = document.getElementById('drawProb');
const team2Prob          = document.getElementById('team2Prob');
const team1ProbFill      = document.getElementById('team1ProbFill');
const drawProbFill       = document.getElementById('drawProbFill');
const team2ProbFill      = document.getElementById('team2ProbFill');
const recommendationBox  = document.getElementById('recommendationBox');

const statsTeam1         = document.getElementById('statsTeam1');
const statsTeam2         = document.getElementById('statsTeam2');
const team1Form          = document.getElementById('team1Form');
const team2Form          = document.getElementById('team2Form');
const team1Goals         = document.getElementById('team1Goals');
const team2Goals         = document.getElementById('team2Goals');
const team1Possession    = document.getElementById('team1Possession');
const team2Possession    = document.getElementById('team2Possession');
const team1Corners       = document.getElementById('team1Corners');
const team2Corners       = document.getElementById('team2Corners');

// Verificación rápida
console.log('predictBtn encontrado:', predictBtn !== null);

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM listo, añadiendo listeners');
  predictBtn.addEventListener('click', () => {
    console.log('Click en Predecir');
    getPrediction();
  });
  team1Input.addEventListener('keypress', e => {
    if (e.key === 'Enter') {
      console.log('Enter en team1, salto a team2');
      team2Input.focus();
    }
  });
  team2Input.addEventListener('keypress', e => {
    if (e.key === 'Enter') {
      console.log('Enter en team2, lanzando getPrediction');
      getPrediction();
    }
  });
});

// Función para añadir mensajes al chat
function addMessage(text, isUser = false) {
  const div = document.createElement('div');
  div.classList.add('chat-message', isUser ? 'user' : 'bot');
  div.innerHTML = `<p>${text}</p>`;
  chatBox.append(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Llamada al API y manejo de la respuesta
async function getPrediction() {
  const team1 = team1Input.value.trim();
  const team2 = team2Input.value.trim();
  if (!team1 || !team2) {
    return alert('Por favor, ingresa ambos equipos');
  }

  addMessage(`${team1} vs ${team2}`, true);
  addMessage('Analizando estadísticas y calculando probabilidades...');

  predictBtn.disabled = true;
  predictBtn.textContent = 'Analizando...';

  try {
    const res = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ team1, team2 })
    });
    if (!res.ok) throw new Error('Error en la conexión con el servidor');

    const data = await res.json();
    displayResults(data, team1, team2);

    const { team1: t1, team2: t2, draw_probability } = data.prediction;
    const winner = t1.win_probability > t2.win_probability ? team1 : team2;
    const winProb = Math.max(t1.win_probability, t2.win_probability);

    if (winProb < 40) {
      addMessage(`Partido muy parejo: empate con ${draw_probability}% de probabilidad.`);
    } else {
      addMessage(`Predicción: ${winner} con ${winProb}% de probabilidades de ganar.`);
    }
    addMessage(data.recommendation);

  } catch (err) {
    console.error('Error:', err);
    addMessage('Lo siento, ocurrió un error. Intenta de nuevo.');
  } finally {
    predictBtn.disabled = false;
    predictBtn.textContent = 'Predecir';
  }
}

// Renderiza los resultados en pantalla
function displayResults(data, team1, team2) {
  predTeam1Name.textContent = team1;
  predTeam2Name.textContent = team2;
  statsTeam1.textContent = team1;
  statsTeam2.textContent = team2;
  matchInfo.textContent = `${team1} vs ${team2}`;

  setTimeout(() => {
    const { team1: t1, team2: t2, draw_probability } = data.prediction;
    team1Prob.textContent = `${t1.win_probability}%`;
    drawProb.textContent  = `${draw_probability}%`;
    team2Prob.textContent = `${t2.win_probability}%`;

    team1ProbFill.style.width = `${t1.win_probability}%`;
    drawProbFill.style.width  = `${draw_probability}%`;
    team2ProbFill.style.width = `${t2.win_probability}%`;

    recommendationBox.textContent = data.recommendation;
    updateStats(data.key_stats);
    resultsContainer.style.display = 'block';
    resultsContainer.scrollIntoView({ behavior: 'smooth' });
  }, ANIMATION_DELAY);
}

// Actualiza estadísticas clave
function updateStats({ team1, team2 }) {
  team1Form.textContent = formatForm(team1.form);
  team2Form.textContent = formatForm(team2.form);
  team1Goals.textContent = team1.goals_per_match.toFixed(1);
  team2Goals.textContent = team2.goals_per_match.toFixed(1);
  team1Possession.textContent = `${team1.possession}%`;
  team2Possession.textContent = `${team2.possession}%`;
  team1Corners.textContent = team1.corners_per_match.toFixed(1);
  team2Corners.textContent = team2.corners_per_match.toFixed(1);
}

// Convierte resultados W/D/L en símbolos
function formatForm(form = []) {
  if (!form.length) return 'N/A';
  return form.map(r => ({ W: '✓', D: '⟺', L: '✗' }[r] || r)).join(' ');
}
