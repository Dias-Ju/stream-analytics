
const BASE = 'http://localhost:5000';
const RECADOS_KEY = 'streamanalytics_recados';

function fmt(s, n = 20) {
  return s ? (s.length > n ? s.substring(0, n) + '…' : s) : '—';
}

function timeAgo(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  const diff = Math.floor((Date.now() - d) / 1000);
  if (isNaN(diff)) return '';
  if (diff < 60) return `${diff}s`;
  if (diff < 3600) return `${Math.floor(diff / 60)}min`;
  return `${Math.floor(diff / 3600)}h`;
}

async function carregarResumo() {
  try {
    const r = await fetch(`${BASE}/resumo`);
    const d = await r.json();
    document.getElementById('total').textContent = d.total_geral ?? '—';
    document.getElementById('sucessos').textContent = d.streams_validos ?? '—';
    document.getElementById('erros').textContent = d.streams_suspeitos ?? '—';
    document.getElementById('taxa').textContent =
      d.taxa_falha != null ? d.taxa_falha + '%' : '—';
  } catch {
    ['total', 'sucessos', 'erros', 'taxa'].forEach(
      id => (document.getElementById(id).textContent = '—')
    );
  }
}

async function carregarMusicas() {
  try {
    const r = await fetch(`${BASE}/ranking/musicas`);
    const lista = await r.json();
    const el = document.getElementById('nokia-list');
    if (!lista.length) {
      el.innerHTML = '<div class="screen-empty">sem dados</div>';
      return;
    }
    el.innerHTML = lista.slice(0, 5).map((m, i) => `
      <div class="screen-item ${i === 0 ? 'screen-item--active' : ''}"
           style="animation-delay:${i * 0.08}s">
        <span class="screen-num">${i + 1}</span>
        <span class="screen-name">${fmt(m.musica, 14)}</span>
      </div>
    `).join('');
  } catch { }
}

async function carregarArtistas() {
  try {
    const r = await fetch(`${BASE}/ranking/artistas`);
    const lista = await r.json();
    const el = document.getElementById('lista-artistas');
    if (!lista.length) {
      el.innerHTML = '<div class="empty-state">sem dados ainda</div>';
      return;
    }
    const max = lista[0]?.total || 1;
    el.innerHTML = lista.slice(0, 5).map((a, i) => `
      <div class="rank-item" style="animation-delay:${i * 0.07}s">
        <span class="rank-num ${i < 3 ? 'rank-num--top' : ''}">${i + 1}</span>
        <div class="rank-info">
          <span class="rank-name">${a.artista}</span>
          <span class="rank-sub">${a.total} reproduções</span>
        </div>
        <div class="rank-bar-wrap">
          <div class="rank-bar" style="width:${Math.round((a.total / max) * 100)}%"></div>
        </div>
        <span class="rank-count">${a.total}</span>
      </div>
    `).join('');
  } catch {
    document.getElementById('lista-artistas').innerHTML =
      '<div class="empty-state">api offline</div>';
  }
}

async function carregarPlataformas() {
  try {
    const r = await fetch(`${BASE}/ranking/plataformas`);
    const lista = await r.json();
    const el = document.getElementById('lista-plataformas');
    if (!lista.length) {
      el.innerHTML = '<div class="empty-state">sem dados ainda</div>';
      return;
    }
    el.innerHTML = lista.map((p, i) => `
      <div class="platform-pill" style="animation-delay:${i * 0.07}s">
        <span class="platform-name">${p.plataforma}</span>
        <span class="platform-count">${p.total}</span>
      </div>
    `).join('');
  } catch { }
}

async function carregarStreams() {
  try {
    const r = await fetch(`${BASE}/streams`);
    const lista = await r.json();
    const el = document.getElementById('lista-sucesso');
    if (!lista.length) {
      el.innerHTML = '<div class="empty-state">nenhum stream ainda</div>';
      return;
    }
    el.innerHTML = lista.map(s => `
      <div class="feed-item">
        <span class="feed-icon">♪</span>
        <div class="feed-body">
          <span class="feed-title">${fmt(s.musica)}</span>
          <span class="feed-meta">${s.artista} · ${s.usuario} · ${s.plataforma} · ${s.duracao}s</span>
        </div>
        <span class="feed-time">${timeAgo(s.data_processamento)}</span>
      </div>
    `).join('');
  } catch {
    document.getElementById('lista-sucesso').innerHTML =
      '<div class="empty-state">api offline</div>';
  }
}

async function carregarErros() {
  try {
    const r = await fetch(`${BASE}/erros`);
    const lista = await r.json();
    const el = document.getElementById('lista-erros');
    if (!lista.length) {
      el.innerHTML = '<div class="empty-state">nenhum erro ainda</div>';
      return;
    }
    el.innerHTML = lista.map(e => `
      <div class="feed-item feed-item--dlq">
        <span class="feed-icon">⚠</span>
        <div class="feed-body">
          <span class="feed-title">${e.stream_id}</span>
          <span class="feed-meta">${fmt(e.erro, 30)} · ${e.tentativas} tentativas</span>
        </div>
        <span class="feed-time">${timeAgo(e.data_erro)}</span>
      </div>
    `).join('');
  } catch {
    document.getElementById('lista-erros').innerHTML =
      '<div class="empty-state">api offline</div>';
  }
}

function carregarRecados() {
  const dados = JSON.parse(localStorage.getItem(RECADOS_KEY) || '[]');
  const el = document.getElementById('recados-lista');
  if (!dados.length) {
    el.innerHTML = '<div class="empty-state">nenhum recado ainda</div>';
    return;
  }
  el.innerHTML = dados.slice().reverse().map(r => `
    <div class="chat-msg">
      <span class="chat-msg-texto">${r.texto}</span>
      <span class="chat-msg-data">${r.data}</span>
    </div>
  `).join('');
  el.scrollTop = el.scrollHeight;
}

function salvarRecado() {
  const input = document.getElementById('recado-input');
  const texto = input.value.trim();
  if (!texto) return;
  const dados = JSON.parse(localStorage.getItem(RECADOS_KEY) || '[]');
  const agora = new Date();
  dados.push({
    texto,
    data: agora.toLocaleDateString('pt-BR', {
      day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit'
    })
  });
  if (dados.length > 20) dados.shift();
  localStorage.setItem(RECADOS_KEY, JSON.stringify(dados));
  input.value = '';
  carregarRecados();
}

document.getElementById('recado-input').addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    salvarRecado();
  }
});

async function carregar() {

  const btn = document.getElementById("btn-refresh");

  if (btn) {
    btn.classList.add("loading");
  }

  await Promise.all([
    carregarResumo(),
    carregarMusicas(),
    carregarArtistas(),
    carregarPlataformas(),
    carregarStreams(),
    carregarErros(),
  ]);

  if (btn) {
    btn.classList.remove("loading");
  }

}
async function carregarEvolucao() {
  try {
    const r = await fetch(`${BASE}/evolucao`);
    const lista = await r.json();

    const labels = lista.map(d => d.minuto);
    const dados = lista.map(d => d.total);

    const ctx = document.getElementById('grafico-evolucao').getContext('2d');

    if (window.graficoEvolucao) {
      window.graficoEvolucao.data.labels = labels;
      window.graficoEvolucao.data.datasets[0].data = dados;
      window.graficoEvolucao.update();
    } else {
      window.graficoEvolucao = new Chart(ctx, {
        type: 'line',
        data: {
          labels,
          datasets: [{
            label: 'streams por minuto',
            data: dados,
            borderColor: '#7FB9B9',
            backgroundColor: 'rgba(127,185,185,0.1)',
            borderWidth: 2,
            pointBackgroundColor: '#D463A1',
            pointRadius: 4,
            tension: 0.4,
            fill: true
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                font: { family: 'DM Mono' },
                color: '#7a6062'
              },
              grid: { color: 'rgba(85,67,69,0.08)' }
            },
            x: {
              ticks: {
                font: { family: 'DM Mono' },
                color: '#7a6062'
              },
              grid: { display: false }
            }
          }
        }
      });
    }
  } catch { }
}

async function carregar() {
  await Promise.all([
    carregarResumo(),
    carregarMusicas(),
    carregarArtistas(),
    carregarPlataformas(),
    carregarStreams(),
    carregarErros(),
    carregarEvolucao(),
    carregarRankingPeriodo(periodoAtivo),
  ]);
}

let periodoAtivo = 'hoje';

async function carregarRankingPeriodo(periodo) {
  try {
    const r = await fetch(`${BASE}/ranking/artistas/${periodo}`);
    const lista = await r.json();
    const el = document.getElementById('lista-periodo');
    if (!lista.length) {
      el.innerHTML = '<div class="empty-state">sem dados ainda</div>';
      return;
    }
    const max = lista[0]?.total || 1;
    el.innerHTML = lista.map((a, i) => `
      <div class="rank-item">
        <span class="rank-num ${i < 3 ? 'rank-num--top' : ''}">${i + 1}</span>
        <div class="rank-info">
          <span class="rank-name">${a.artista}</span>
          <span class="rank-sub">${a.total} reproduções</span>
        </div>
        <div class="rank-bar-wrap">
          <div class="rank-bar" style="width:${Math.round((a.total / max) * 100)}%"></div>
        </div>
        <span class="rank-count">${a.total}</span>
      </div>
    `).join('');
  } catch {
    document.getElementById('lista-periodo').innerHTML =
      '<div class="empty-state">api offline</div>';
  }
}

function mudarPeriodo(periodo) {
  periodoAtivo = periodo;
  document.querySelectorAll('.periodo-btn').forEach(btn => {
    btn.classList.toggle('active', btn.textContent.toLowerCase() === periodo);
  });
  carregarRankingPeriodo(periodo);
}

carregar();
carregarRecados();
setInterval(carregar, 10000);