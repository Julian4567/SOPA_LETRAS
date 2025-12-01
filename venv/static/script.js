// static/script.js
const socket = io();
let grid = [];
let words = [];
let size = 12;
let selecting = [];
let foundWords = new Set();
let timerInterval = null;
let startTime = null;

function log(msg) {
  const l = document.getElementById('log');
  l.innerText = msg;
}

function startTimer() {
  startTime = Date.now();
  const timerSpan = document.getElementById('timer');
  if (timerInterval) clearInterval(timerInterval);
  timerInterval = setInterval(() => {
    const elapsed = Date.now() - startTime;
    const s = Math.floor(elapsed/1000);
    const mm = String(Math.floor(s/60)).padStart(2,'0');
    const ss = String(s%60).padStart(2,'0');
    timerSpan.innerText = `${mm}:${ss}`;
  }, 250);
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

function renderBoard() {
  const boardDiv = document.getElementById('board');
  boardDiv.innerHTML = '';
  const table = document.createElement('table');
  table.className = 'grid';
  for (let r=0; r<size; r++) {
    const tr = document.createElement('tr');
    for (let c=0; c<size; c++) {
      const td = document.createElement('td');
      td.dataset.r = r;
      td.dataset.c = c;
      td.innerText = grid[r][c];
      td.onclick = onCellClick;
      tr.appendChild(td);
    }
    table.appendChild(tr);
  }
  boardDiv.appendChild(table);
  renderWords();
}

function renderWords() {
  const wl = document.getElementById('words_list');
  wl.innerHTML = '<h3>Palabras</h3>';
  const ul = document.createElement('ul');
  words.forEach(w => {
    const li = document.createElement('li');
    li.id = 'word_'+w;
    li.innerText = w + (foundWords.has(w) ? ' ✔' : '');
    ul.appendChild(li);
  });
  wl.appendChild(ul);
}

function onCellClick(e) {
  const r = Number(this.dataset.r);
  const c = Number(this.dataset.c);
  const key = `${r},${c}`;
  // toggle selection
  const idx = selecting.findIndex(p => p[0]===r && p[1]===c);
  if (idx >= 0) {
    selecting.splice(idx,1);
    this.classList.remove('selected');
  } else {
    selecting.push([r,c]);
    this.classList.add('selected');
  }
}

function submitSelectionAsWord() {
  if (selecting.length === 0) return;
  // build word from selection in the order selected
  const w = selecting.map(p => grid[p[0]][p[1]]).join('');
  // send to server
  socket.emit('submit_word', {word: w, coords: selecting});
}

document.getElementById('start_btn').onclick = () => {
  const words_input = document.getElementById('words_input').value;
  const size_input = Number(document.getElementById('size_input').value) || 12;
  size = size_input;
  const raw = words_input.split(',').map(x=>x.trim()).filter(x=>x.length>0);
  words = raw.map(x => x.toUpperCase());
  socket.emit('start_game', {words: words, size: size});
  startTimer();
  foundWords.clear();
};

document.getElementById('solve_btn').onclick = () => {
  socket.emit('request_solve');
};

document.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    submitSelectionAsWord();
  }
  if (e.key === 'Escape') {
    // clear selection visually
    selecting = [];
    document.querySelectorAll('.selected').forEach(el => el.classList.remove('selected'));
  }
});

// socket handlers
socket.on('board', (data) => {
  grid = data.grid;
  words = data.words;
  size = grid.length;
  renderBoard();
  log('Tablero recibido. Selecciona letras y presiona Enter para enviar palabra.');
});

socket.on('word_result', (data) => {
  if (data.ok) {
    foundWords.add(data.word);
    renderWords();
    // clear selection and mark selected cells as found
    selecting.forEach(p => {
      const selector = `td[data-r="${p[0]}"][data-c="${p[1]}"]`;
      const el = document.querySelector(selector);
      if (el) el.classList.add('found');
    });
    selecting = [];
  } else {
    log(data.msg || 'Palabra incorrecta');
    // keep selection so user can adjust
  }
});

socket.on('solve_result', (data) => {
  if (!data.ok) {
    log(data.msg || 'No hay solución');
    return;
  }
  const positions = data.positions;
  // highlight solution on board
  // clear earlier highlights
  document.querySelectorAll('td').forEach(td => {
    td.classList.remove('solution');
  });
  Object.values(positions).forEach(coordList => {
    coordList.forEach(pair => {
      const r = pair[0], c = pair[1];
      const el = document.querySelector(`td[data-r="${r}"][data-c="${c}"]`);
      if (el) el.classList.add('solution');
    });
  });
  log('Solución mostrada (resaltada).');
  stopTimer();
});
