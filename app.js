const DATA_SOURCES = {
  openfootball: 'https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json'
};

const state = {
  data: null,
  matches: [],
  selectedDate: null,
  search: '',
  activeTab: 'daily'
};


const TEAM_FLAG_MAP = {
  'argentina': 'AR', 'australia': 'AU', 'austria': 'AT', 'belgium': 'BE', 'bolivia': 'BO', 'brazil': 'BR',
  'cameroun': 'CM', 'cameroon': 'CM', 'canada': 'CA', 'chile': 'CL', 'china': 'CN', 'colombia': 'CO',
  'costa rica': 'CR', 'croatia': 'HR', 'czech republic': 'CZ', 'czechia': 'CZ', 'denmark': 'DK',
  'ecuador': 'EC', 'egypt': 'EG', 'england': 'GB-ENG', 'spain': 'ES', 'españa': 'ES', 'france': 'FR',
  'germany': 'DE', 'ghana': 'GH', 'greece': 'GR', 'honduras': 'HN', 'hungary': 'HU', 'india': 'IN',
  'iran': 'IR', 'ir iran': 'IR', 'iraq': 'IQ', 'ireland': 'IE', 'israel': 'IL', 'italy': 'IT',
  'ivory coast': 'CI', "cote d'ivoire": 'CI', 'japan': 'JP', 'korea republic': 'KR', 'south korea': 'KR',
  'mexico': 'MX', 'morocco': 'MA', 'netherlands': 'NL', 'new zealand': 'NZ', 'nigeria': 'NG',
  'north korea': 'KP', 'norway': 'NO', 'paraguay': 'PY', 'peru': 'PE', 'poland': 'PL', 'portugal': 'PT',
  'qatar': 'QA', 'romania': 'RO', 'saudi arabia': 'SA', 'scotland': 'GB-SCT', 'senegal': 'SN',
  'serbia': 'RS', 'slovakia': 'SK', 'slovenia': 'SI', 'south africa': 'ZA', 'sweden': 'SE',
  'switzerland': 'CH', 'tunisia': 'TN', 'turkey': 'TR', 'türkiye': 'TR', 'ukraine': 'UA',
  'united states': 'US', 'usa': 'US', 'uruguay': 'UY', 'venezuela': 'VE', 'wales': 'GB-WLS',
  'algeria': 'DZ', 'angola': 'AO', 'bosnia and herzegovina': 'BA', 'bosnia-herzegovina': 'BA',
  'burkina faso': 'BF', 'cape verde': 'CV', 'dr congo': 'CD', 'congo dr': 'CD', 'el salvador': 'SV',
  'finland': 'FI', 'georgia': 'GE', 'guatemala': 'GT', 'iceland': 'IS', 'jamaica': 'JM', 'jordan': 'JO',
  'mali': 'ML', 'oman': 'OM', 'panama': 'PA', 'republic of ireland': 'IE', 'russia': 'RU', 'syria': 'SY',
  'trinidad and tobago': 'TT', 'uae': 'AE', 'united arab emirates': 'AE', 'uzbekistan': 'UZ'
};

function toRegionalIndicatorFlag(code) {
  if (!code) return '🏳️';
  if (code === 'GB-ENG' || code === 'GB-SCT' || code === 'GB-WLS') return '🏴';
  if (code.length !== 2) return '🏳️';
  return code.toUpperCase().replace(/./g, char => String.fromCodePoint(127397 + char.charCodeAt(0)));
}

function teamCode(teamName) {
  const normalized = String(teamName || '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/&/g, 'and')
    .replace(/\./g, '')
    .replace(/\s+/g, ' ')
    .trim();
  return TEAM_FLAG_MAP[normalized] || null;
}

function teamFlag(teamName) {
  if (!teamName || /por definir|tbd|winner|runner-up/i.test(String(teamName))) return '🏳️';
  return toRegionalIndicatorFlag(teamCode(teamName));
}

function teamLabel(teamName) {
  const name = escapeHtml(teamName || 'Por definir');
  const flag = teamFlag(teamName);
  return `<span class="team-label"><span class="flag" aria-hidden="true">${flag}</span><span>${name}</span></span>`;
}

const els = {
  sourceStatus: document.getElementById('sourceStatus'),
  sourceSelect: document.getElementById('sourceSelect'),
  datePicker: document.getElementById('datePicker'),
  prevDay: document.getElementById('prevDay'),
  todayBtn: document.getElementById('todayBtn'),
  nextDay: document.getElementById('nextDay'),
  teamSearch: document.getElementById('teamSearch'),
  loadPastedJson: document.getElementById('loadPastedJson'),
  jsonPaste: document.getElementById('jsonPaste'),
  jsonFile: document.getElementById('jsonFile'),
  tabs: document.querySelectorAll('.tab'),
  panels: document.querySelectorAll('.tab-panel'),
  dailyTitle: document.getElementById('dailyTitle'),
  dailyCount: document.getElementById('dailyCount'),
  dayStatus: document.getElementById('dayStatus'),
  dailyMatches: document.getElementById('dailyMatches'),
  groupTables: document.getElementById('groupTables'),
  thirdsTable: document.getElementById('thirdsTable'),
  resultsByDay: document.getElementById('resultsByDay'),
  scorersTable: document.getElementById('scorersTable'),
  scorersCount: document.getElementById('scorersCount'),
  knockoutRounds: document.getElementById('knockoutRounds'),
  emptyTemplate: document.getElementById('emptyStateTemplate')
};

function setStatus(text, type = '') {
  els.sourceStatus.className = `status-card ${type}`.trim();
  els.sourceStatus.querySelector('span:last-child').textContent = text;
}

function todayMadridISO() {
  return madridParts(new Date()).date;
}

function madridParts(date) {
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Europe/Madrid',
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', hour12: false,
    timeZoneName: 'short'
  }).formatToParts(date).reduce((acc, part) => {
    acc[part.type] = part.value;
    return acc;
  }, {});
  return {
    date: `${parts.year}-${parts.month}-${parts.day}`,
    time: `${parts.hour}:${parts.minute}`,
    tz: parts.timeZoneName || 'España'
  };
}

function displayDateEs(isoDate) {
  const [y, m, d] = isoDate.split('-').map(Number);
  const date = new Date(Date.UTC(y, m - 1, d, 12, 0, 0));
  return new Intl.DateTimeFormat('es-ES', { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' }).format(date);
}

function addDaysISO(isoDate, days) {
  const [y, m, d] = isoDate.split('-').map(Number);
  const date = new Date(Date.UTC(y, m - 1, d + days, 12, 0, 0));
  return date.toISOString().slice(0, 10);
}

function parseSourceTime(match) {
  if (!match.date || !match.time) return null;
  const time = String(match.time).trim();
  const matchTime = time.match(/^(\d{1,2}):(\d{2})(?:\s*UTC\s*([+-]\d{1,2})(?::?(\d{2}))?)?/i);
  if (!matchTime) return null;

  const [year, month, day] = match.date.split('-').map(Number);
  const hour = Number(matchTime[1]);
  const minute = Number(matchTime[2]);
  const offsetHours = matchTime[3] ? Number(matchTime[3]) : 0;
  const offsetMinutes = matchTime[4] ? Number(matchTime[4]) * Math.sign(offsetHours || 1) : 0;
  const utcMillis = Date.UTC(year, month - 1, day, hour - offsetHours, minute - offsetMinutes, 0);
  return new Date(utcMillis);
}

function normalizeMatches(rawMatches = []) {
  return rawMatches.map((m, index) => {
    const utcDate = parseSourceTime(m);
    const madrid = utcDate ? madridParts(utcDate) : { date: m.date, time: m.time || '--:--', tz: 'España' };
    return {
      ...m,
      id: m.num || `${m.round || 'match'}-${index}`,
      _index: index,
      _utcDate: utcDate,
      _madridDate: madrid.date,
      _madridTime: madrid.time,
      _madridTz: madrid.tz,
      _isGroup: Boolean(m.group),
      _hasScore: Boolean(m.score && Array.isArray(m.score.ft))
    };
  }).sort((a, b) => (a._utcDate || 0) - (b._utcDate || 0));
}

async function loadDefaultData() {
  setStatus('Actualizando desde OpenFootball…');
  try {
    const response = await fetch(`${DATA_SOURCES.openfootball}?cacheBust=${Date.now()}`, { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    applyData(data, 'OpenFootball actualizado');
    localStorage.setItem('mundial2026-last-data', JSON.stringify(data));
  } catch (error) {
    const cached = localStorage.getItem('mundial2026-last-data');
    if (cached) {
      applyData(JSON.parse(cached), 'Usando última copia local', 'ok');
    } else {
      setStatus(`Error al cargar datos: ${error.message}`, 'err');
      renderAll();
    }
  }
}

function applyData(data, statusText = 'Datos cargados', statusType = 'ok') {
  if (!data || !Array.isArray(data.matches)) throw new Error('JSON no compatible: falta matches[]');
  state.data = data;
  state.matches = normalizeMatches(data.matches);
  setStatus(`${statusText} · ${state.matches.length} partidos`, statusType);
  renderAll();
}

function filteredMatches(matches = state.matches) {
  const q = state.search.trim().toLowerCase();
  if (!q) return matches;
  return matches.filter(m => [m.team1, m.team2, m.group, m.ground, m.round].some(v => String(v || '').toLowerCase().includes(q)));
}

function scoreText(match) {
  if (!match._hasScore) return '—';
  return `${match.score.ft[0]} - ${match.score.ft[1]}`;
}

function goalsText(match) {
  const g1 = Array.isArray(match.goals1) ? match.goals1 : [];
  const g2 = Array.isArray(match.goals2) ? match.goals2 : [];
  if (!g1.length && !g2.length) return '';
  const format = goal => `${escapeHtml(goal.name || 'Gol')} ${goal.minute ? `${goal.minute}'` : ''}${goal.penalty ? ' (p.)' : ''}`;
  const part1 = g1.length ? `<strong>${teamLabel(match.team1)}:</strong> ${g1.map(format).join(', ')}` : '';
  const part2 = g2.length ? `<strong>${teamLabel(match.team2)}:</strong> ${g2.map(format).join(', ')}` : '';
  return `<div class="goals">${[part1, part2].filter(Boolean).join('<br>')}</div>`;
}

function matchCard(match) {
  const resultClass = match._hasScore ? 'score' : 'score pending';
  return `<article class="match-card">
    <div>
      <div class="time">${escapeHtml(match._madridTime || '--:--')}</div>
      <span class="tz">${escapeHtml(match._madridTz || 'España')}</span>
    </div>
    <div>
      <div class="teams">${teamLabel(match.team1)} <span class="muted">vs</span> ${teamLabel(match.team2)}</div>
      <div class="meta">
        <span>${escapeHtml(match.round || '')}</span>
        ${match.group ? `<span>${escapeHtml(match.group)}</span>` : ''}
        ${match.num ? `<span>Partido ${escapeHtml(match.num)}</span>` : ''}
        <span>${escapeHtml(match.ground || '')}</span>
      </div>
      ${goalsText(match)}
    </div>
    <div class="${resultClass}">${scoreText(match)}</div>
  </article>`;
}

function renderDaily() {
  const date = state.selectedDate || todayMadridISO();
  const matches = filteredMatches().filter(m => m._madridDate === date);
  const finished = matches.filter(m => m._hasScore).length;
  const pending = matches.length - finished;
  els.dailyTitle.textContent = `Partidos del ${displayDateEs(date)}`;
  els.dailyCount.textContent = `${matches.length} partido${matches.length === 1 ? '' : 's'}`;
  if (els.dayStatus) els.dayStatus.textContent = `${finished} finalizado${finished === 1 ? '' : 's'} · ${pending} pendiente${pending === 1 ? '' : 's'}`;
  els.dailyMatches.innerHTML = matches.length ? matches.map(matchCard).join('') : emptyState();
}

function buildStandings() {
  const groups = new Map();
  state.matches.filter(m => m.group).forEach(match => {
    const group = match.group;
    if (!groups.has(group)) groups.set(group, new Map());
    const table = groups.get(group);
    [match.team1, match.team2].forEach(team => {
      if (!table.has(team)) table.set(team, { team, group, pj: 0, g: 0, e: 0, p: 0, gf: 0, gc: 0, dg: 0, pts: 0 });
    });
    if (match._hasScore) {
      const a = table.get(match.team1);
      const b = table.get(match.team2);
      const [gf1, gf2] = match.score.ft;
      a.pj += 1; b.pj += 1;
      a.gf += gf1; a.gc += gf2;
      b.gf += gf2; b.gc += gf1;
      if (gf1 > gf2) { a.g += 1; b.p += 1; a.pts += 3; }
      else if (gf1 < gf2) { b.g += 1; a.p += 1; b.pts += 3; }
      else { a.e += 1; b.e += 1; a.pts += 1; b.pts += 1; }
      a.dg = a.gf - a.gc;
      b.dg = b.gf - b.gc;
    }
  });

  return Array.from(groups.entries()).map(([group, table]) => ({
    group,
    rows: Array.from(table.values()).sort(sortRows)
  })).sort((a, b) => groupLetter(a.group).localeCompare(groupLetter(b.group)));
}

function groupLetter(groupName) {
  return String(groupName || '').replace(/Group\s+/i, '');
}

function sortRows(a, b) {
  return b.pts - a.pts || b.dg - a.dg || b.gf - a.gf || a.team.localeCompare(b.team, 'es');
}

function standingsTable(rows, markQualifiers = true) {
  return `<table>
    <thead><tr><th>Equipo</th><th class="num">PJ</th><th class="num">G</th><th class="num">E</th><th class="num">P</th><th class="num">GF</th><th class="num">GC</th><th class="num">DG</th><th class="num">Pts</th></tr></thead>
    <tbody>${rows.map((r, i) => `<tr class="${markQualifiers && i < 2 ? 'qualify' : markQualifiers && i === 2 ? 'third' : ''}"><td>${teamLabel(r.team)}</td><td class="num">${r.pj}</td><td class="num">${r.g}</td><td class="num">${r.e}</td><td class="num">${r.p}</td><td class="num">${r.gf}</td><td class="num">${r.gc}</td><td class="num">${r.dg}</td><td class="num"><strong>${r.pts}</strong></td></tr>`).join('')}</tbody>
  </table>`;
}

function renderGroups() {
  const groups = buildStandings();
  els.groupTables.innerHTML = groups.map(g => `<article class="group-card"><h3>${escapeHtml(g.group)}</h3>${standingsTable(g.rows)}</article>`).join('') || emptyState();
  const thirds = groups.map(g => g.rows[2]).filter(Boolean).sort(sortRows).map((r, idx) => ({ ...r, rank: idx + 1 }));
  els.thirdsTable.innerHTML = thirds.length ? `<table>
    <thead><tr><th>#</th><th>Equipo</th><th>Grupo</th><th class="num">PJ</th><th class="num">DG</th><th class="num">GF</th><th class="num">Pts</th><th>Estado</th></tr></thead>
    <tbody>${thirds.map(r => `<tr class="${r.rank <= 8 ? 'qualify' : ''}"><td>${r.rank}</td><td>${teamLabel(r.team)}</td><td>${escapeHtml(r.group)}</td><td class="num">${r.pj}</td><td class="num">${r.dg}</td><td class="num">${r.gf}</td><td class="num"><strong>${r.pts}</strong></td><td>${r.rank <= 8 ? 'Clasificaría' : 'Fuera'}</td></tr>`).join('')}</tbody>
  </table>` : emptyState();
}

function renderResults() {
  const played = filteredMatches().filter(m => m._hasScore);
  const byDay = groupBy(played, m => m._madridDate);
  const days = Object.keys(byDay).sort();
  els.resultsByDay.innerHTML = days.length ? days.map(day => `<section class="day-block"><header><h3>${displayDateEs(day)}</h3><span class="pill">${byDay[day].length} resultado${byDay[day].length === 1 ? '' : 's'}</span></header><div class="cards">${byDay[day].map(matchCard).join('')}</div></section>`).join('') : emptyState();
}

function renderScorers() {
  const scorers = new Map();
  state.matches.forEach(match => {
    [['goals1', match.team1], ['goals2', match.team2]].forEach(([key, team]) => {
      (Array.isArray(match[key]) ? match[key] : []).forEach(goal => {
        const name = goal.name || 'Desconocido';
        const id = `${name}|${team}`;
        const row = scorers.get(id) || { name, team, goals: 0, penalties: 0, matches: new Set() };
        row.goals += 1;
        if (goal.penalty) row.penalties += 1;
        row.matches.add(match.id);
        scorers.set(id, row);
      });
    });
  });
  const rows = Array.from(scorers.values()).sort((a, b) => b.goals - a.goals || a.name.localeCompare(b.name, 'es'));
  els.scorersCount.textContent = `${rows.length} jugador${rows.length === 1 ? '' : 'es'}`;
  els.scorersTable.innerHTML = rows.length ? `<table>
    <thead><tr><th>#</th><th>Jugador</th><th>Selección</th><th class="num">Goles</th><th class="num">Penaltis</th><th class="num">Partidos con gol</th></tr></thead>
    <tbody>${rows.map((r, i) => `<tr><td>${i + 1}</td><td>${escapeHtml(r.name)}</td><td>${teamLabel(r.team)}</td><td class="num"><strong>${r.goals}</strong></td><td class="num">${r.penalties}</td><td class="num">${r.matches.size}</td></tr>`).join('')}</tbody>
  </table>` : emptyState();
}

function renderKnockout() {
  const knockout = filteredMatches().filter(m => !m.group);
  const byRound = groupBy(knockout, m => m.round || 'Eliminatoria');
  const order = ['Round of 32', 'Round of 16', 'Quarter-final', 'Semi-final', 'Match for third place', 'Final'];
  const rounds = Object.keys(byRound).sort((a, b) => { const ia = order.indexOf(a); const ib = order.indexOf(b); return (ia === -1 ? 999 : ia) - (ib === -1 ? 999 : ib) || a.localeCompare(b, 'es'); });
  els.knockoutRounds.innerHTML = rounds.length ? rounds.map(round => `<article class="round-card"><h3>${translateRound(round)}</h3>${byRound[round].map(m => `<div class="match-card"><div><div class="time">${escapeHtml(m._madridTime)}</div><span class="tz">${escapeHtml(m._madridDate)}</span></div><div><div class="teams">${teamLabel(m.team1)} <span class="muted">vs</span> ${teamLabel(m.team2)}</div><div class="meta"><span>Partido ${escapeHtml(m.num || '')}</span><span>${escapeHtml(m.ground || '')}</span><span>${scoreText(m)}</span></div>${goalsText(m)}</div></div>`).join('')}</article>`).join('') : emptyState();
}

function translateRound(round) {
  return {
    'Round of 32': 'Dieciseisavos / Ronda de 32',
    'Round of 16': 'Octavos de final',
    'Quarter-final': 'Cuartos de final',
    'Semi-final': 'Semifinales',
    'Match for third place': 'Tercer y cuarto puesto',
    'Final': 'Final'
  }[round] || round;
}

function groupBy(array, fn) {
  return array.reduce((acc, item) => {
    const key = fn(item);
    (acc[key] ||= []).push(item);
    return acc;
  }, {});
}

function emptyState() {
  return els.emptyTemplate.innerHTML;
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[char]));
}

function renderAll() {
  renderDaily();
  renderGroups();
  renderResults();
  renderScorers();
  renderKnockout();
}

function setupEvents() {
  state.selectedDate = todayMadridISO();
  els.datePicker.value = state.selectedDate;

  els.datePicker.addEventListener('change', () => {
    state.selectedDate = els.datePicker.value || todayMadridISO();
    renderDaily();
  });
  els.prevDay.addEventListener('click', () => changeDay(-1));
  els.nextDay.addEventListener('click', () => changeDay(1));
  els.todayBtn.addEventListener('click', () => {
    state.selectedDate = todayMadridISO();
    els.datePicker.value = state.selectedDate;
    renderDaily();
  });
  els.teamSearch.addEventListener('input', () => {
    state.search = els.teamSearch.value;
    renderAll();
  });
  els.tabs.forEach(tab => tab.addEventListener('click', () => activateTab(tab.dataset.tab)));
  els.sourceSelect.addEventListener('change', () => {
    if (els.sourceSelect.value === 'openfootball') loadDefaultData();
    else setStatus('Modo manual: carga o pega un JSON', '');
  });
  els.loadPastedJson.addEventListener('click', () => {
    try {
      const data = JSON.parse(els.jsonPaste.value);
      applyData(data, 'JSON manual cargado');
      localStorage.setItem('mundial2026-last-data', JSON.stringify(data));
    } catch (error) {
      setStatus(`JSON inválido: ${error.message}`, 'err');
    }
  });
  els.jsonFile.addEventListener('change', async event => {
    const file = event.target.files?.[0];
    if (!file) return;
    try {
      const text = await file.text();
      const data = JSON.parse(text);
      applyData(data, `Archivo cargado: ${file.name}`);
      localStorage.setItem('mundial2026-last-data', JSON.stringify(data));
    } catch (error) {
      setStatus(`No se pudo cargar el archivo: ${error.message}`, 'err');
    }
  });
}

function changeDay(delta) {
  state.selectedDate = addDaysISO(state.selectedDate || todayMadridISO(), delta);
  els.datePicker.value = state.selectedDate;
  renderDaily();
}

function activateTab(tabName) {
  state.activeTab = tabName;
  els.tabs.forEach(t => t.classList.toggle('active', t.dataset.tab === tabName));
  els.panels.forEach(panel => panel.classList.toggle('active', panel.id === tabName));
}

setupEvents();
loadDefaultData();
