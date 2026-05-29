const state = { stats: null, page: 'home', raw: [] };

const titles = {
  home: ['Home', 'Distributed Eurovision voting with up to 20 Docker country datacenters.'],
  test: ['Start test', 'Choose votes, duration, datacenters and participating Eurovision countries.'],
  live: ['Live dashboard', 'Only the stats and charts update. The page itself does not reload.'],
  raw: ['Raw CSV votes', 'All incoming vote events stored by the central aggregator.'],
  datacenters: ['Datacenters', 'One Docker service per country/datacenter. Select only what you need for the demo.'],
  docker: ['Docker info', 'Commands and network explanation for the demo.'],
  presentation: ['Presentation text', 'Simple explanation you can say to the teacher.']
};

function fmt(n) { return Number(n || 0).toLocaleString('en-US'); }
function byId(id) { return document.getElementById(id); }
function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[c]));
}

function switchPage(page) {
  state.page = page;
  document.querySelectorAll('.page').forEach(el => el.classList.toggle('active', el.id === page));
  document.querySelectorAll('.nav').forEach(el => el.classList.toggle('active', el.dataset.page === page));
  byId('pageTitle').textContent = titles[page][0];
  byId('pageSubtitle').textContent = titles[page][1];
  updateUI();
  if (page === 'raw') fetchRawVotes();
}

document.querySelectorAll('.nav').forEach(btn => btn.addEventListener('click', () => switchPage(btn.dataset.page)));
document.querySelectorAll('[data-go]').forEach(btn => btn.addEventListener('click', () => switchPage(btn.dataset.go)));
byId('refreshBtn').addEventListener('click', fetchStats);
byId('refreshRawBtn').addEventListener('click', fetchRawVotes);
byId('startTestBtn').addEventListener('click', startTest);
byId('resetBtn').addEventListener('click', resetResults);
byId('selectAllSongs').addEventListener('click', () => setAllSongs(true));
byId('clearSongs').addEventListener('click', () => setAllSongs(false));
byId('selectAllDatacenters')?.addEventListener('click', () => setAllDatacenters(true));
byId('clearDatacenters')?.addEventListener('click', () => setAllDatacenters(false));

async function fetchStats() {
  try {
    const res = await fetch('/api/stats', { cache: 'no-store' });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    state.stats = await res.json();
    byId('connectionBadge').textContent = 'Connected';
    byId('connectionBadge').classList.add('ok');
    renderControlsOnce();
    updateUI();
  } catch (err) {
    byId('connectionBadge').textContent = 'Disconnected';
    byId('connectionBadge').classList.remove('ok');
  }
}

async function fetchRawVotes() {
  try {
    const res = await fetch('/api/raw-votes?limit=300', { cache: 'no-store' });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const payload = await res.json();
    state.raw = payload.rows || [];
    renderRawVotes();
  } catch (err) {
    byId('rawTable').innerHTML = `<tbody><tr><td>Could not load raw votes.</td></tr></tbody>`;
  }
}

function renderControlsOnce() {
  const s = state.stats;
  if (!s) return;

  const dcBox = byId('datacenterChecks');
  if (dcBox && !dcBox.dataset.rendered) {
    dcBox.innerHTML = (s.datacenters || []).map((dc, index) => `
      <label class="check-item">
        <input type="checkbox" name="datacenter" value="${escapeHtml(dc.datacenter)}" ${index < 3 ? 'checked' : ''} />
        <span><b>${escapeHtml(dc.country_code)} ${escapeHtml(dc.country)}</b><small>${escapeHtml(dc.datacenter)}</small></span>
      </label>
    `).join('');
    dcBox.dataset.rendered = '1';
  }

  const songBox = byId('songChecks');
  if (songBox && !songBox.dataset.rendered) {
    songBox.innerHTML = (s.available_songs || []).map(song => `
      <label class="check-item">
        <input type="checkbox" name="song" value="${song.song_id}" checked />
        <span><b>${escapeHtml(song.flag)} ${escapeHtml(song.country)}</b><small>song #${song.song_id}</small></span>
      </label>
    `).join('');
    songBox.dataset.rendered = '1';
  }
}

function selectedValues(name) {
  return [...document.querySelectorAll(`input[name="${name}"]:checked`)].map(x => x.value);
}

function setAllSongs(checked) {
  document.querySelectorAll('input[name="song"]').forEach(x => x.checked = checked);
}

function setAllDatacenters(checked) {
  document.querySelectorAll('input[name="datacenter"]').forEach(x => x.checked = checked);
}

async function startTest() {
  const totalVotes = Number(byId('testVotes').value || 0);
  const duration = Number(byId('testDuration').value || 0);
  const datacenters = selectedValues('datacenter');
  const songIds = selectedValues('song').map(Number);
  const msg = byId('testMessage');

  if (totalVotes < 10) {
    msg.textContent = 'Choose at least 10 votes.';
    msg.className = 'message error';
    return;
  }
  if (duration < 5) {
    msg.textContent = 'Choose at least 5 seconds.';
    msg.className = 'message error';
    return;
  }
  if (datacenters.length < 1) {
    msg.textContent = 'Select at least 1 datacenter.';
    msg.className = 'message error';
    return;
  }
  if (songIds.length < 2) {
    msg.textContent = 'Select at least 2 participating Eurovision countries/songs.';
    msg.className = 'message error';
    return;
  }

  msg.textContent = 'Starting test...';
  msg.className = 'message';
  try {
    const res = await fetch('/api/start-test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ total_votes: totalVotes, duration, datacenters, song_ids: songIds })
    });
    const payload = await res.json();
    if (!res.ok) throw new Error(payload.message || 'Could not start test');
    msg.textContent = `Test started: ${fmt(totalVotes)} votes over ${duration}s using ${datacenters.length} datacenter(s).`;
    msg.className = payload.errors?.length ? 'message warnmsg' : 'message okmsg';
    await fetchStats();
    switchPage('live');
  } catch (err) {
    msg.textContent = err.message;
    msg.className = 'message error';
  }
}

async function resetResults() {
  const msg = byId('testMessage');
  try {
    const res = await fetch('/api/reset', { method: 'POST' });
    if (!res.ok) throw new Error('Could not reset results');
    msg.textContent = 'Results and CSV files were reset.';
    msg.className = 'message okmsg';
    await fetchStats();
    await fetchRawVotes();
  } catch (err) {
    msg.textContent = err.message;
    msg.className = 'message error';
  }
}

function updateUI() {
  const s = state.stats;
  if (!s) return;
  const winner = s.winner ? `${s.winner.flag || ''} ${s.winner.country}` : '-';
  byId('homeTotal').textContent = fmt(s.total_votes);
  byId('homeActive').textContent = s.active_datacenters || 0;
  byId('homeWinner').textContent = winner;
  byId('homeUpdated').textContent = s.updated_at || '-';
  byId('totalVotes').textContent = fmt(s.total_votes);
  byId('activeDatacenters').textContent = s.active_datacenters || 0;
  byId('winner').textContent = winner;
  byId('updatedAt').textContent = s.updated_at || '-';
  renderRanking(s.global_results || []);
  renderDatacenters(s.datacenters || []);
  renderRecent(s.recent_events || []);
  drawBarChart(byId('dcChart'), (s.datacenters || []).filter(x => x.votes > 0 || state.page === 'datacenters').map(x => ({ label: x.country_code || x.datacenter.replace('dc-', ''), value: x.votes })));
  drawBarChart(byId('songChart'), (s.global_results || []).slice(0, 8).map(x => ({ label: x.country, value: x.total_votes })));
  if (state.page === 'raw') fetchRawVotes();
}

function renderRanking(rows) {
  const table = byId('rankingTable');
  table.innerHTML = `<thead><tr><th>Rank</th><th>Country</th><th>Song ID</th><th>Votes</th></tr></thead>` +
    `<tbody>${rows.slice(0, 12).map(r => `<tr><td>${r.rank}</td><td>${escapeHtml(r.flag || '')} ${escapeHtml(r.country)}</td><td>${r.song_id}</td><td>${fmt(r.total_votes)}</td></tr>`).join('')}</tbody>`;
}

function renderDatacenters(rows) {
  const table = byId('dcTable');
  table.innerHTML = `<thead><tr><th>Datacenter</th><th>Country</th><th>Container</th><th>Internal target</th><th>Votes</th><th>Local leader</th></tr></thead>` +
    `<tbody>${rows.map(r => `<tr><td>${escapeHtml(r.datacenter)}</td><td>${escapeHtml(r.country_code)} ${escapeHtml(r.country)}</td><td>${escapeHtml(r.container)}</td><td>central-aggregator:8501 → ${escapeHtml(r.datacenter)}:9000</td><td>${fmt(r.votes)}</td><td>${escapeHtml(r.top_flag || '')} ${escapeHtml(r.top_country)} (${fmt(r.top_votes)})</td></tr>`).join('')}</tbody>`;

  const max = Math.max(1, ...rows.map(r => r.votes || 0));
  byId('dcCards').innerHTML = rows.map(r => `
    <article class="card dc-mini">
      <span>${escapeHtml(r.datacenter)}</span>
      <strong>${escapeHtml(r.country_code)} ${escapeHtml(r.country)}</strong>
      <p>${escapeHtml(r.description)}</p>
      <p><b>Container:</b> ${escapeHtml(r.container)}</p>
      <p><b>Votes:</b> ${fmt(r.votes)}</p>
      <div class="progress"><div style="width:${Math.round((r.votes || 0) / max * 100)}%"></div></div>
    </article>
  `).join('');
}

function renderRecent(events) {
  const box = byId('recentEvents');
  if (!events.length) {
    box.innerHTML = '<p>No live events received yet. Go to Start test and launch a simulation.</p>';
    return;
  }

  box.innerHTML = events.map(e => `
    <div class="event">
      <small>${escapeHtml(e.timestamp?.split('T')[1] || '')}</small>
      <div>
        <b>${escapeHtml(e.from_country_code)} ${escapeHtml(e.from_country || '')}</b>
        vote via <b>${escapeHtml(e.datacenter)}</b>
        <span class="arrow">→</span>
        <b>${escapeHtml(e.flag || '')} ${escapeHtml(e.song_country)}</b>
        <br>
        <small>phone: ${escapeHtml(e.phone_number)} · song #${escapeHtml(e.song_id)}</small>
      </div>
      <small>#${escapeHtml(e.song_id)}</small>
    </div>
  `).join('');
}

function renderRawVotes() {
  const table = byId('rawTable');
  const rows = state.raw || [];

  if (!rows.length) {
    table.innerHTML = '<tbody><tr><td>No raw votes yet. Start a test first.</td></tr></tbody>';
    return;
  }

  table.innerHTML = `
    <thead>
      <tr>
        <th>event_id</th>
        <th>phone_number</th>
        <th>from</th>
        <th>datacenter</th>
        <th>voted_for</th>
        <th>timestamp</th>
      </tr>
    </thead>
    <tbody>
      ${rows.map(r => `
        <tr>
          <td>${escapeHtml(r.event_id)}</td>
          <td>${escapeHtml(r.phone_number)}</td>
          <td>${escapeHtml(r.from_country_code)} ${escapeHtml(r.from_country || '')}</td>
          <td>${escapeHtml(r.datacenter)}</td>
          <td>${escapeHtml(r.flag || '')} ${escapeHtml(r.song_country || ('song #' + r.song_id))}</td>
          <td>${escapeHtml(r.timestamp)}</td>
        </tr>
      `).join('')}
    </tbody>
  `;
}

function drawBarChart(canvas, data) {
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width * dpr;
  canvas.height = 320 * dpr;
  ctx.scale(dpr, dpr);

  const w = rect.width, h = 320;
  ctx.clearRect(0, 0, w, h);
  const pad = { left: 48, right: 16, top: 24, bottom: 56 };
  const chartW = w - pad.left - pad.right;
  const chartH = h - pad.top - pad.bottom;
  const max = Math.max(1, ...data.map(x => x.value || 0));

  ctx.strokeStyle = '#22304a';
  ctx.fillStyle = '#91a1b8';
  ctx.font = '12px Segoe UI, Arial';
  ctx.textAlign = 'left';
  for (let i = 0; i <= 4; i++) {
    const y = pad.top + chartH - (chartH * i / 4);
    ctx.beginPath(); ctx.moveTo(pad.left, y); ctx.lineTo(w - pad.right, y); ctx.stroke();
    ctx.fillText(fmt(Math.round(max * i / 4)), 4, y + 4);
  }

  const gap = 14;
  const barW = Math.max(18, (chartW - gap * (data.length - 1)) / Math.max(data.length, 1));
  data.forEach((item, i) => {
    const x = pad.left + i * (barW + gap);
    const barH = chartH * ((item.value || 0) / max);
    const y = pad.top + chartH - barH;
    const grad = ctx.createLinearGradient(0, y, 0, y + barH);
    grad.addColorStop(0, '#69d2ff');
    grad.addColorStop(1, '#8b5cf6');
    ctx.fillStyle = grad;
    roundRect(ctx, x, y, barW, barH, 8);
    ctx.fill();
    ctx.fillStyle = '#eef5ff';
    ctx.textAlign = 'center';
    ctx.fillText(fmt(item.value), x + barW / 2, Math.max(14, y - 6));
    ctx.save();
    ctx.translate(x + barW / 2, h - 16);
    ctx.rotate(-0.55);
    ctx.fillStyle = '#91a1b8';
    ctx.fillText(item.label, 0, 0);
    ctx.restore();
  });
}

function roundRect(ctx, x, y, width, height, radius) {
  const r = Math.min(radius, width / 2, height / 2);
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + width, y, x + width, y + height, r);
  ctx.arcTo(x + width, y + height, x, y + height, r);
  ctx.arcTo(x, y + height, x, y, r);
  ctx.arcTo(x, y, x + width, y, r);
  ctx.closePath();
}

fetchStats();
setInterval(fetchStats, 2000);
window.addEventListener('resize', updateUI);
