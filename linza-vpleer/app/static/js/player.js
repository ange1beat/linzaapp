/* global filename — injected by inline <script> in player.html */
const video = document.getElementById('video');
const overlay = document.getElementById('videoOverlay');
const playBtn = document.getElementById('playPauseBtn');

/** Ключи sources/a/b.mp4 → .../sources/a/b.mp4 (без %2F в одном сегменте — стабильнее за прокси). */
function encodePathSegments(key) {
  if (!key) return '';
  return String(key).split('/').map(encodeURIComponent).join('/');
}
const pathEnc = encodePathSegments(filename);

// ── Glass overlay play/pause + seek controls ──
function togglePlay() {
  if (video.paused) { video.play(); } else { video.pause(); }
}

function seekRelative(seconds) {
  video.currentTime = Math.max(0, Math.min(video.duration || 0, video.currentTime + seconds));
}

function updatePlayPauseIcon() {
  if (!playBtn) return;
  const iconPlay = playBtn.querySelector('.icon-play');
  const iconPause = playBtn.querySelector('.icon-pause');
  if (video.paused) {
    iconPlay.style.display = '';
    iconPause.style.display = 'none';
  } else {
    iconPlay.style.display = 'none';
    iconPause.style.display = '';
  }
}

video.addEventListener('play', updatePlayPauseIcon);
video.addEventListener('pause', updatePlayPauseIcon);
video.addEventListener('click', togglePlay);

// Auto-hide overlay while playing
let overlayTimer;
function showOverlay() {
  if (overlay) { overlay.classList.remove('hidden'); overlay.classList.add('show'); }
  clearTimeout(overlayTimer);
  if (!video.paused) {
    overlayTimer = setTimeout(() => {
      if (overlay && !video.paused) { overlay.classList.add('hidden'); overlay.classList.remove('show'); }
    }, 2500);
  }
}
if (overlay) {
  const container = video.closest('.player-container');
  if (container) {
    container.addEventListener('mousemove', showOverlay);
    container.addEventListener('mouseleave', () => {
      if (!video.paused && overlay) { overlay.classList.add('hidden'); overlay.classList.remove('show'); }
    });
  }
}

// ── Speed controls ──
function setSpeed(rate) {
  video.playbackRate = rate;
  document.querySelectorAll('.speed-controls button').forEach(b => {
    b.classList.toggle('active', parseFloat(b.textContent) === rate);
  });
}

// ── Metadata ──
fetch('/api/vpleer/metadata/' + pathEnc)
  .then(r => { if (!r.ok) throw new Error('metadata'); return r.json(); })
  .then(m => {
    const meta = document.getElementById('meta');
    meta.innerHTML = `
      <div class="row"><span class="label">Формат:</span> ${m.format}</div>
      <div class="row"><span class="label">Длительность:</span> ${m.duration_formatted}</div>
      <div class="row"><span class="label">Размер:</span> ${(m.size / 1048576).toFixed(1)} МБ</div>
      <div class="row"><span class="label">Видео:</span> ${m.video?.codec} ${m.video?.width}x${m.video?.height} @ ${m.video?.fps} fps</div>
      <div class="row"><span class="label">Аудио:</span> ${m.audio?.codec} ${m.audio?.sample_rate} Hz</div>
      <div class="row"><span class="label">Битрейт:</span> ${(m.bit_rate / 1000).toFixed(0)} kbps</div>
    `;
  })
  .catch(() => {
    document.getElementById('meta').textContent = 'Не удалось загрузить метаданные';
  });

// ── B5: Playback strategy (progressive vs HLS transcode) ──
let hlsInstance = null;
fetch('/api/vpleer/playback-info/' + pathEnc)
  .then(r => { if (!r.ok) throw new Error('playback-info'); return r.json(); })
  .then(info => {
    document.getElementById('formatBadge').textContent = info.format_label || '';
    if (info.strategy === 'progressive') {
      video.src = info.stream_url;
    } else if (info.strategy === 'transcode') {
      // Показать overlay
      const overlay = document.getElementById('transcodeOverlay');
      overlay.classList.add('visible');
      if (info.warnings && info.warnings.length) {
        document.getElementById('transcodeWarnings').textContent = info.warnings.join(' ');
      }
      if (typeof Hls !== 'undefined' && Hls.isSupported()) {
        hlsInstance = new Hls({ maxBufferLength: 30, maxMaxBufferLength: 60 });
        hlsInstance.loadSource(info.hls_url);
        hlsInstance.attachMedia(video);
        hlsInstance.on(Hls.Events.MANIFEST_PARSED, () => {
          overlay.classList.remove('visible');
        });
        hlsInstance.on(Hls.Events.ERROR, (event, data) => {
          if (data.fatal) {
            document.getElementById('transcodeLabel').textContent = 'Ошибка транскодирования';
            overlay.classList.add('visible');
          }
        });
      } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        // Safari native HLS
        video.src = info.hls_url;
        video.addEventListener('loadedmetadata', () => { overlay.classList.remove('visible'); });
      } else {
        document.getElementById('transcodeLabel').textContent = 'Формат не поддерживается';
      }
    } else {
      video.src = info.stream_url;
    }
  })
  .catch(() => {
    // Fallback: progressive stream
    video.src = '/api/vpleer/stream/' + pathEnc;
  });

// MOV fallback: если progressive не сработал — попробовать HLS
video.addEventListener('error', () => {
  if (!hlsInstance && typeof Hls !== 'undefined' && Hls.isSupported()) {
    const hlsUrl = '/api/vpleer/hls/' + pathEnc + '/playlist.m3u8';
    hlsInstance = new Hls({ maxBufferLength: 30, maxMaxBufferLength: 60 });
    hlsInstance.loadSource(hlsUrl);
    hlsInstance.attachMedia(video);
  }
});

// ── A2+C2: Timeline & Detection state ──
const timelineEl = document.getElementById('timeline');
const trackVideo = document.getElementById('trackVideo');
const trackAudio = document.getElementById('trackAudio');
let videoDuration = 0;
let markersData = [];
let currentDetIdx = -1;

function syncDurationAndUrlTimeline() {
  if (video.readyState < 1) return;
  videoDuration = video.duration || 0;
  loadTimeline();
}
video.addEventListener('loadedmetadata', syncDurationAndUrlTimeline);
/* Уже в кэше: loadedmetadata мог произойти до навешивания слушателя */
if (video.readyState >= 1) syncDurationAndUrlTimeline();

timelineEl.addEventListener('click', (e) => {
  if (videoDuration > 0) {
    const track = e.target.closest('.timeline-track');
    const ref = track || trackVideo;
    const rect = ref.getBoundingClientRect();
    video.currentTime = ((e.clientX - rect.left) / rect.width) * videoDuration;
  }
});

// ── Time helpers ──
function parseTime(t) {
  if (typeof t === 'number') return t;
  if (!t) return 0;
  const p = String(t).split(':');
  if (p.length === 3) return parseFloat(p[0])*3600 + parseFloat(p[1])*60 + parseFloat(p[2]);
  if (p.length === 2) return parseFloat(p[0])*60 + parseFloat(p[1]);
  return parseFloat(t) || 0;
}
function formatTimecode(sec) {
  const n = typeof sec === 'number' ? sec : parseFloat(sec);
  if (!Number.isFinite(n)) return '00:00:00.000';
  const h = Math.floor(n / 3600);
  const m = Math.floor((n % 3600) / 60);
  const s = n % 60;
  return String(h).padStart(2,'0') + ':' + String(m).padStart(2,'0') + ':' + s.toFixed(3).padStart(6,'0');
}

// ── A8: Unified data flow ──
/** Декодирование base64(JSON в UTF-8) — зеркало encodeUtf8Base64 в Linza VideoPlayer. */
function decodeUtf8Base64(b64) {
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return new TextDecoder().decode(bytes);
}

function loadTimeline() {
  const params = new URLSearchParams(window.location.search);
  const det = params.get('detections');
  if (!det) return;
  let detections;
  try {
    detections = JSON.parse(decodeUtf8Base64(det));
  } catch {
    try {
      detections = JSON.parse(atob(det));
    } catch {
      try {
        detections = JSON.parse(decodeURIComponent(det));
      } catch {
        console.warn('[VPleer] loadTimeline: не удалось разобрать ?detections=');
        return;
      }
    }
  }
  /* Не затирать данные из ds:/postMessage: в URL часто попадает не массив или [] из-за порчи query */
  if (!Array.isArray(detections)) {
    console.warn('[VPleer] loadTimeline: ?detections= не JSON-массив, пропуск', typeof detections);
    return;
  }
  if (detections.length === 0) return;
  fetchAndApply(detections);
}

function clientSideMarkers(detections) {
  if (!Array.isArray(detections)) return [];
  return detections.map(function (d, i) {
    var st = d.start_time != null ? d.start_time : d.startSeconds;
    var et = d.end_time != null ? d.end_time : d.endSeconds;
    var src = d.source || (d.modality ? d.modality.toLowerCase() : '');
    if (!src && typeof d.type === 'string') {
      var tl = d.type.toLowerCase();
      if (tl === 'audio' || tl === 'video') src = tl;
    }
    if (!src) src = 'both';
    /* video-ai-filter: type = модальность; subclass = код нарушения */
    var sub = d.subclass != null && String(d.subclass).trim() !== '' ? String(d.subclass).trim() : '';
    if (!sub && typeof d.type === 'string' && d.type.toLowerCase() !== 'audio' && d.type.toLowerCase() !== 'video') {
      sub = d.type;
    }
    return {
      id: d.id || ('det_' + i),
      subclass: sub,
      category: '16+',
      color: '#ffc107',
      start_time: st != null ? st : 0,
      end_time: et != null ? et : 0,
      confidence: d.confidence,
      source: src,
    };
  });
}

function fetchAndApply(detections) {
  if (!Array.isArray(detections)) {
    console.warn('[VPleer] fetchAndApply: ожидался массив детекций, игнор (не очищаем панель)', detections);
    return;
  }
  /* Всегда POST: JSON с кириллицей в quote/reason раздувает GET ?detections= и ломается на лимите URL прокси. */
  var req = fetch('/api/vpleer/timeline', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename: filename, detections: detections }),
  });
  req
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(function (data) {
      var m = data.markers || [];
      if (m.length === 0 && detections.length > 0) {
        console.warn('[VPleer] timeline вернул пустой markers при непустых detections — клиентский fallback');
        applyDetections(clientSideMarkers(detections));
        return;
      }
      applyDetections(m);
    })
    .catch(function (err) {
      console.warn('[VPleer] timeline API failed, applying client-side fallback', err);
      applyDetections(clientSideMarkers(detections));
    });
}

// ── C4: Group overlapping detections ──
function groupByOverlap(markers) {
  if (!markers.length) return [];
  const sorted = [...markers].sort((a, b) => a._startSec - b._startSec);
  const groups = [];
  let cur = { items: [sorted[0]], start: sorted[0]._startSec, end: sorted[0]._endSec };
  for (let i = 1; i < sorted.length; i++) {
    if (sorted[i]._startSec < cur.end) {
      cur.items.push(sorted[i]);
      cur.end = Math.max(cur.end, sorted[i]._endSec);
    } else {
      groups.push(cur);
      cur = { items: [sorted[i]], start: sorted[i]._startSec, end: sorted[i]._endSec };
    }
  }
  groups.push(cur);
  return groups;
}

let groupsData = [];

function applyDetections(markers) {
  /* Сброс фильтров: иначе после buildFilterChips() чипы новые, а activeFilters старый — карточки скрыты (display:none), маркеры на шкале без учёта status остаются яркими. */
  activeFilters.category.clear();
  activeFilters.source.clear();
  activeFilters.status.clear();
  activeFilters.minConf = 0;
  const confSlider = document.getElementById('confSlider');
  if (confSlider) {
    confSlider.value = 0;
    const cv = document.getElementById('confValue');
    if (cv) cv.textContent = '0';
  }

  markersData = markers.map((m, i) => {
    const idNorm = m.id != null && m.id !== '' ? String(m.id) : ('det_' + i);
    const startRaw = m.start_time != null ? m.start_time : m.startSeconds;
    const endRaw = m.end_time != null ? m.end_time : m.endSeconds;
    return {
      ...m,
      id: idNorm,
      _startSec: (() => {
        const t = parseTime(startRaw);
        return Number.isFinite(t) ? t : 0;
      })(),
      _endSec: (() => {
        const t = parseTime(endRaw);
        return Number.isFinite(t) ? t : 0;
      })(),
      _els: [],
      _card: null,
    };
  });
  groupsData = groupByOverlap(markersData);
  // Restore review states before rendering
  const store = getReviewStore();
  markersData.forEach(m => { m._review = store[m.id] || null; });
  currentDetIdx = -1;
  /* Счётчик и навигация до отрисовки: если renderDetectionPanel бросит, шкала уже могла обновиться — не оставляем «0» */
  const countEl = document.getElementById('detectionCount');
  if (countEl) countEl.textContent = String(markers.length);
  updateNavButtons();
  try {
    renderMarkers(markersData);
    renderDetectionPanel(groupsData);
    applyReviewStates();
  } catch (err) {
    console.error('[VPleer] applyDetections: отрисовка', err);
    const list = document.getElementById('detectionList');
    if (list) {
      const msg = String(err && err.message ? err.message : err).replace(/</g, '');
      list.innerHTML =
        '<div class="no-detections">Не удалось отрисовать список детекций.<br><small>' + msg + '</small></div>';
    }
  }
  try {
    buildFilterChips();
    applyFilters();
    updateStatBar();
  } catch (err) {
    console.error('[VPleer] applyDetections: фильтры/стат.', err);
  }
}

// ── A2+C2: Render timeline markers on dual tracks ──
function renderMarkers(markers) {
  // Clear only markers, keep track labels
  trackVideo.querySelectorAll('.marker').forEach(el => el.remove());
  trackAudio.querySelectorAll('.marker').forEach(el => el.remove());
  if (!videoDuration || !markers.length) return;
  markers.forEach((m, i) => {
    const src = (m.source || 'both').toLowerCase();
    const targets = src === 'video' ? [trackVideo]
      : src === 'audio' ? [trackAudio]
      : [trackVideo, trackAudio];
    const leftPct = (m._startSec / videoDuration * 100) + '%';
    const widthPct = Math.max((m._endSec - m._startSec) / videoDuration * 100, 0.5) + '%';
    m._els = [];
    targets.forEach(track => {
      const div = document.createElement('div');
      div.className = 'marker';
      div.style.left = leftPct;
      div.style.width = widthPct;
      div.style.background = m.color || '#ffc107';
      div.onclick = (e) => { e.stopPropagation(); video.currentTime = m._startSec; video.play(); };
      div.addEventListener('mouseenter', () => {
        const tip = document.createElement('div');
        tip.className = 'marker-tooltip';
        tip.textContent = (m.subclass || '') + ' (' + (m.category || '') + ') '
          + Math.round((m.confidence || 0) * 100) + '% | '
          + formatTimecode(m._startSec) + ' — ' + formatTimecode(m._endSec);
        div.appendChild(tip);
      });
      div.addEventListener('mouseleave', () => {
        const tip = div.querySelector('.marker-tooltip');
        if (tip) tip.remove();
      });
      m._els.push(div);
      track.appendChild(div);
    });
  });
}

// ── A3+C4: Render detection panel (grouped) ──
function srcIcon(source) {
  const s = (source || 'both').toLowerCase();
  return s === 'video' ? String.fromCodePoint(0x1F3AC)
    : s === 'audio' ? String.fromCodePoint(0x1F50A) : '\u25C9';
}

function renderDetectionPanel(groups) {
  const list = document.getElementById('detectionList');
  if (!list) {
    console.error('[VPleer] #detectionList не найден в DOM');
    return;
  }
  if (!groups.length) {
    list.innerHTML = '<div class="no-detections">Нет загруженных детекций.<br><small>Данные приходят из Linza (postMessage или ?detections=)</small></div>';
    return;
  }
  list.innerHTML = '';
  groups.forEach((g, gi) => {
    if (g.items.length === 1) {
      // Single detection — original card style
      const m = g.items[0];
      const card = document.createElement('div');
      card.className = 'detection-card';
      card.id = 'group-card-' + gi;
      card.style.borderLeftColor = m.color || '#ffc107';
      const reclassed = m._review && m._review.status === 'reclassified' && m._review.new_subclass;
      card.innerHTML =
        '<div class="det-time">' + formatTimecode(m._startSec) + ' — ' + formatTimecode(m._endSec)
        + '<span class="review-status-icon"></span></div>'
        + '<div class="det-info">'
        + '<span class="det-source" title="' + (m.source || 'both') + '">' + srcIcon(m.source) + '</span>'
        + '<span class="det-subclass">' + (m.subclass || '') + (reclassed ? ' \u2192 ' + m._review.new_subclass : '') + '</span>'
        + '<span class="det-category" style="background:' + (m.color || '#ffc107') + '">' + (m.category || '') + '</span>'
        + '<span class="det-confidence">' + Math.round((m.confidence || 0) * 100) + '%</span>'
        + '</div>'
        + '<div class="det-actions">'
        + '<button class="review-btn" onclick="event.stopPropagation();playGroupFragment(' + gi + ')" title="Фрагмент">' + SVG.play + '</button>'
        + (m.id ? buildReviewButtons(m.id, !!m._review) : '')
        + '<a href="/api/vpleer/fragment?filename=' + encodeURIComponent(filename)
          + '&start=' + g.start + '&end=' + g.end
          + '" target="_blank" class="review-btn" style="text-decoration:none" '
          + 'onclick="event.stopPropagation()" title="Скачать">' + SVG.download + '</a>'
        + '</div>';
      card.onclick = () => { video.currentTime = g.start; video.play(); currentDetIdx = gi; updateNavButtons(); };
      g.items.forEach(m => { m._card = card; });
      list.appendChild(card);
    } else {
      // Grouped card — multiple overlapping detections
      const colors = [...new Set(g.items.map(m => m.color || '#ffc107'))];
      const grad = colors.length > 1
        ? 'linear-gradient(90deg,' + colors.join(',') + ')'
        : colors[0];
      const card = document.createElement('div');
      card.className = 'group-card';
      card.id = 'group-card-' + gi;
      let html = '<div class="group-border" style="background:' + grad + '"></div>'
        + '<div class="group-header">'
        + '<div class="det-time">' + formatTimecode(g.start) + ' — ' + formatTimecode(g.end) + '</div>'
        + '<span class="group-count">' + g.items.length + '</span>'
        + '</div>';
      g.items.forEach(m => {
        const rc = m._review && m._review.status === 'reclassified' && m._review.new_subclass;
        html += '<div class="group-det" data-det-id="' + (m.id || '') + '">'
          + '<span class="det-source" title="' + (m.source || 'both') + '">' + srcIcon(m.source) + '</span>'
          + '<span class="det-subclass">' + (m.subclass || '') + (rc ? ' \u2192 ' + m._review.new_subclass : '') + '</span>'
          + '<span class="det-category" style="background:' + (m.color || '#ffc107') + '">' + (m.category || '') + '</span>'
          + '<span class="det-confidence">' + Math.round((m.confidence || 0) * 100) + '%</span>'
          + (m.id ? buildReviewButtons(m.id, !!m._review) : '')
          + '</div>';
      });
      html += '<div class="group-actions">'
        + '<button class="review-btn" onclick="event.stopPropagation();playGroupFragment(' + gi + ')" title="Фрагмент">' + SVG.play + '</button>'
        + '<a href="/api/vpleer/fragment?filename=' + encodeURIComponent(filename)
          + '&start=' + g.start + '&end=' + g.end
          + '" target="_blank" class="review-btn" style="text-decoration:none" '
          + 'onclick="event.stopPropagation()" title="Скачать">' + SVG.download + '</a>'
        + '</div>';
      card.innerHTML = html;
      card.onclick = () => { video.currentTime = g.start; video.play(); currentDetIdx = gi; updateNavButtons(); };
      g.items.forEach(m => { m._card = card; });
      list.appendChild(card);
    }
  });
}

// ── A4: Active detection highlight ──
let lastActiveSet = '';
video.addEventListener('timeupdate', () => {
  const t = video.currentTime;
  let activeIds = '';
  markersData.forEach((m, i) => {
    const isActive = t >= m._startSec && t <= m._endSec;
    if (m._card) m._card.classList.toggle('active', isActive);
    if (m._els) m._els.forEach(el => el.classList.toggle('active', isActive));
    if (isActive) activeIds += i + ',';
  });
  // Auto-scroll to first active group card
  if (activeIds && activeIds !== lastActiveSet) {
    for (let gi = 0; gi < groupsData.length; gi++) {
      if (groupsData[gi].items.some(m => t >= m._startSec && t <= m._endSec)) {
        const card = document.getElementById('group-card-' + gi);
        if (card) card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        break;
      }
    }
  }
  lastActiveSet = activeIds;
  // A7: Fragment mode enforcement
  if (fragmentMode) {
    if (t >= fragmentMode.end) {
      if (document.getElementById('fragmentLoop').checked) {
        video.currentTime = fragmentMode.start;
      } else {
        video.pause();
        stopFragment();
      }
    }
  }
});

// ── A5+C4: Prev/Next navigation (by groups) ──
document.getElementById('btnNext').onclick = () => {
  const t = video.currentTime;
  for (let i = 0; i < groupsData.length; i++) {
    if (groupsData[i].start > t + 0.1) {
      video.currentTime = groupsData[i].start;
      video.play();
      currentDetIdx = i;
      updateNavButtons();
      const card = document.getElementById('group-card-' + i);
      if (card) card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      return;
    }
  }
};
document.getElementById('btnPrev').onclick = () => {
  const t = video.currentTime;
  for (let i = groupsData.length - 1; i >= 0; i--) {
    if (groupsData[i].start < t - 0.5) {
      video.currentTime = groupsData[i].start;
      video.play();
      currentDetIdx = i;
      updateNavButtons();
      const card = document.getElementById('group-card-' + i);
      if (card) card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      return;
    }
  }
};
function updateNavButtons() {
  const n = groupsData.length;
  document.getElementById('btnPrev').disabled = n === 0;
  document.getElementById('btnNext').disabled = n === 0;
  document.getElementById('navPosition').textContent =
    n > 0 ? (currentDetIdx >= 0 ? (currentDetIdx + 1) : '\u2014') + ' / ' + n : '0 / 0';
}

// A5: Hotkeys
document.addEventListener('keydown', (e) => {
  if (e.target.tagName === 'TEXTAREA' || e.target.tagName === 'INPUT') return;
  if (e.key === '[') document.getElementById('btnPrev').click();
  if (e.key === ']') document.getElementById('btnNext').click();
});

// ── A7+C4: Fragment playback ──
let fragmentMode = null;
function playFragment(idx) {
  const m = markersData[idx];
  if (!m) return;
  fragmentMode = { start: m._startSec, end: m._endSec };
  video.currentTime = m._startSec;
  video.play();
  const ind = document.getElementById('fragmentIndicator');
  ind.classList.add('visible');
  document.getElementById('fragmentLabel').textContent =
    'Фрагмент: ' + formatTimecode(m._startSec) + ' — ' + formatTimecode(m._endSec);
}
function playGroupFragment(gi) {
  const g = groupsData[gi];
  if (!g) return;
  fragmentMode = { start: g.start, end: g.end };
  video.currentTime = g.start;
  video.play();
  const ind = document.getElementById('fragmentIndicator');
  ind.classList.add('visible');
  document.getElementById('fragmentLabel').textContent =
    'Фрагмент: ' + formatTimecode(g.start) + ' — ' + formatTimecode(g.end);
}
function stopFragment() {
  fragmentMode = null;
  document.getElementById('fragmentIndicator').classList.remove('visible');
}

// ── C5: Review feedback (SVG icons, undo, batch) ──
const SUBCLASSES = ['NUDE','ALCOHOL','SMOKING','VIOLENCE','DRUGS','OBSCENE','TERROR',
  'WEAPON','BLOOD','GAMBLING','SELF_HARM','EXTREMISM','CHILD_ABUSE','HATE_SPEECH',
  'PORNOGRAPHY','PROFANITY','HARASSMENT','SUICIDE','DANGEROUS_ACTS','DECEPTION','OTHER'];

const SVG = {
  check: '<svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor"><path d="M13.854 3.646a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 10.293l6.646-6.647a.5.5 0 0 1 .708 0z"/></svg>',
  x: '<svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor"><path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/></svg>',
  reclass: '<svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor"><path fill-rule="evenodd" d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2v1z"/><path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466z"/></svg>',
  undo: '<svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor"><path fill-rule="evenodd" d="M8 3a5 5 0 1 1-4.546 2.914.5.5 0 0 0-.908-.417A6 6 0 1 0 8 2v1z"/><path d="M8 4.466V.534a.25.25 0 0 0-.41-.192L5.23 2.308c-.12.1-.12.284 0 .384l2.36 1.966A.25.25 0 0 0 8 4.466z"/></svg>',
  play: '<svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor"><path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"/></svg>',
  download: '<svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor"><path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/><path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"/></svg>',
  checkCircle: '<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/></svg>',
  xCircle: '<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"/></svg>',
  arrowRepeat: '<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M11.534 7h3.932a.25.25 0 0 1 .192.41l-1.966 2.36a.25.25 0 0 1-.384 0l-1.966-2.36a.25.25 0 0 1 .192-.41zm-11 2h3.932a.25.25 0 0 0 .192-.41L2.692 6.23a.25.25 0 0 0-.384 0L.342 8.59A.25.25 0 0 0 .534 9z"/><path fill-rule="evenodd" d="M8 3c-1.552 0-2.94.707-3.857 1.818a.5.5 0 1 1-.771-.636A6.002 6.002 0 0 1 13.917 7H12.9A5.002 5.002 0 0 0 8 3zM3.1 9a5.002 5.002 0 0 0 8.757 2.182.5.5 0 1 1 .771.636A6.002 6.002 0 0 1 2.083 9H3.1z"/></svg>',
};

function getReviewStore() {
  try { return JSON.parse(localStorage.getItem('linza-reviews-' + filename) || '{}'); }
  catch { return {}; }
}
function saveReviewStore(store) {
  localStorage.setItem('linza-reviews-' + filename, JSON.stringify(store));
}

function setReview(detId, status, newSubclass) {
  const store = getReviewStore();
  if (status === null) {
    delete store[detId];
  } else {
    store[detId] = { status: status, new_subclass: newSubclass || null };
  }
  saveReviewStore(store);
  renderDetectionPanel(groupsData);
  applyReviewStates();
  updateStatBar();
}

function applyReviewStates() {
  const store = getReviewStore();
  markersData.forEach(m => { m._review = store[m.id] || null; });
  groupsData.forEach((g, gi) => {
    const card = document.getElementById('group-card-' + gi);
    if (!card) return;
    card.classList.remove('review-confirmed','review-rejected','review-reclassified');
    if (g.items.length === 1) {
      const r = g.items[0]._review;
      if (r) {
        card.classList.add('review-' + r.status);
        const icon = card.querySelector('.review-status-icon');
        if (icon) {
          icon.className = 'review-status-icon st-' + r.status;
          icon.innerHTML = r.status === 'confirmed' ? SVG.checkCircle
            : r.status === 'rejected' ? SVG.xCircle : SVG.arrowRepeat;
        }
      } else {
        const icon = card.querySelector('.review-status-icon');
        if (icon) { icon.className = 'review-status-icon'; icon.innerHTML = ''; }
      }
    }
    g.items.forEach(m => {
      const row = card.querySelector('[data-det-id="' + m.id + '"]');
      if (!row) return;
      row.classList.remove('review-confirmed','review-rejected','review-reclassified');
      if (m._review) row.classList.add('review-' + m._review.status);
    });
  });
  const hasUnreviewed = markersData.some(m => m.id && !m._review);
  const btnAll = document.getElementById('btnConfirmAll');
  if (btnAll) btnAll.style.display = markersData.length > 0 && hasUnreviewed ? '' : 'none';
  updateStatBar();
}

/** Экранирование для id внутри onclick="...setReview('…')" (не использовать \\'' — ломает строку в JS). */
function jsQuoteForInlineHandler(s) {
  return String(s).replace(/\\/g, '\\\\').replace(/'/g, '\\\'');
}

function buildReviewButtons(detId, reviewed) {
  const q = jsQuoteForInlineHandler(detId);
  if (reviewed) {
    return '<button class="review-btn btn-undo" data-det-id="' + detId + '" onclick="event.stopPropagation();setReview(\'' + q + '\',null)" title="\u041e\u0442\u043c\u0435\u043d\u0438\u0442\u044c">' + SVG.undo + '</button>';
  }
  return '<button class="review-btn btn-confirm" data-det-id="' + detId + '" onclick="event.stopPropagation();setReview(\'' + q + '\',\'confirmed\')" title="\u041f\u043e\u0434\u0442\u0432\u0435\u0440\u0434\u0438\u0442\u044c (Y)">' + SVG.check + '</button>'
    + '<button class="review-btn btn-reject" data-det-id="' + detId + '" onclick="event.stopPropagation();setReview(\'' + q + '\',\'rejected\')" title="\u041e\u0442\u043a\u043b\u043e\u043d\u0438\u0442\u044c (N)">' + SVG.x + '</button>'
    + '<button class="review-btn btn-reclass" data-det-id="' + detId + '" onclick="event.stopPropagation();showReclass(\'' + q + '\',this)" title="\u041f\u0435\u0440\u0435\u043a\u043b\u0430\u0441\u0441\u0438\u0444\u0438\u0446\u0438\u0440\u043e\u0432\u0430\u0442\u044c (R)">' + SVG.reclass + '</button>';
}

function showReclass(detId, btnEl) {
  const current = markersData.find(m => m.id === detId);
  const opts = SUBCLASSES.filter(s => s !== (current ? current.subclass : '')).map(s =>
    '<option value="' + s + '">' + s + '</option>').join('');
  const btn = btnEl || document.querySelector('.btn-reclass[data-det-id="' + detId + '"]');
  if (!btn) return;
  const sel = document.createElement('select');
  sel.className = 'reclass-select';
  sel.innerHTML = '<option value="">\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435...</option>' + opts;
  sel.onchange = () => {
    if (sel.value) setReview(detId, 'reclassified', sel.value);
  };
  sel.onclick = (e) => e.stopPropagation();
  btn.replaceWith(sel);
  sel.focus();
}

function confirmAllVisible() {
  const store = getReviewStore();
  markersData.forEach(m => {
    if (m.id && !store[m.id]) store[m.id] = { status: 'confirmed', new_subclass: null };
  });
  saveReviewStore(store);
  renderDetectionPanel(groupsData);
  applyReviewStates();
}

// C5: Keyboard shortcuts for review (works on groups too)
document.addEventListener('keydown', (e) => {
  if (e.target.tagName === 'TEXTAREA' || e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;
  if (currentDetIdx < 0 || currentDetIdx >= groupsData.length) return;
  const g = groupsData[currentDetIdx];
  if (!g) return;
  const ids = g.items.filter(m => m.id).map(m => m.id);
  if (!ids.length) return;
  if (e.key === 'y' || e.key === 'Y') ids.forEach(id => setReview(id, 'confirmed'));
  if (e.key === 'n' || e.key === 'N') ids.forEach(id => setReview(id, 'rejected'));
  if (e.key === 'r' || e.key === 'R') { if (g.items.length === 1) showReclass(ids[0]); }
});

// ── C6: Filter & Sort ──
const activeFilters = { category: new Set(), source: new Set(), status: new Set(), minConf: 0 };
let currentSort = 'time';

document.getElementById('filterToggle').onclick = () => {
  const body = document.getElementById('filterBody');
  body.style.display = body.style.display === 'none' ? '' : 'none';
};

document.getElementById('sortSelect').onchange = (e) => {
  currentSort = e.target.value;
  resortAndRender();
};

document.getElementById('confSlider').oninput = (e) => {
  activeFilters.minConf = parseInt(e.target.value);
  document.getElementById('confValue').textContent = e.target.value;
  applyFilters();
};

function buildFilterChips() {
  const cats = [...new Set(markersData.map(m => m.category).filter(Boolean))];
  const srcs = [...new Set(markersData.map(m => (m.source || 'both').toLowerCase()))];
  const statuses = [{'key':'pending','label':'\u25FB Без ответа'},{'key':'confirmed','label':'\u2713 Подтв.'},{'key':'rejected','label':'\u2717 Отклон.'},{'key':'reclassified','label':'\u21BB Перекл.'}];

  const catEl = document.getElementById('filterCategory');
  const srcEl = document.getElementById('filterSource');
  const stEl = document.getElementById('filterStatus');
  if (!catEl || !srcEl || !stEl) {
    console.warn('[VPleer] контейнеры фильтров не найдены');
    return;
  }
  catEl.innerHTML = cats.map(c => '<span class="filter-chip" data-filter="category" data-value="' + c + '">' + c + '</span>').join('');

  srcEl.innerHTML = srcs.map(s => {
    const icon = s === 'video' ? String.fromCodePoint(0x1F3AC) : s === 'audio' ? String.fromCodePoint(0x1F50A) : '\u25C9';
    return '<span class="filter-chip" data-filter="source" data-value="' + s + '">' + icon + ' ' + s + '</span>';
  }).join('');

  stEl.innerHTML = statuses.map(s => '<span class="filter-chip" data-filter="status" data-value="' + s.key + '">' + s.label + '</span>').join('');

  document.querySelectorAll('.filter-chip').forEach(chip => {
    const f = chip.dataset.filter;
    const v = chip.dataset.value;
    if (activeFilters[f] && activeFilters[f].has(v)) chip.classList.add('active');
    chip.onclick = (e) => {
      e.stopPropagation();
      const f2 = chip.dataset.filter;
      const v2 = chip.dataset.value;
      if (activeFilters[f2].has(v2)) { activeFilters[f2].delete(v2); chip.classList.remove('active'); }
      else { activeFilters[f2].add(v2); chip.classList.add('active'); }
      applyFilters();
    };
  });
}

function applyFilters() {
  const store = getReviewStore();
  let visibleCount = 0;
  groupsData.forEach((g, gi) => {
    const card = document.getElementById('group-card-' + gi);
    if (!card) return;
    const match = g.items.some(m => {
      if (activeFilters.category.size && !activeFilters.category.has(m.category)) return false;
      if (activeFilters.source.size && !activeFilters.source.has((m.source || 'both').toLowerCase())) return false;
      if (activeFilters.status.size) {
        const st = store[m.id] ? store[m.id].status : 'pending';
        if (!activeFilters.status.has(st)) return false;
      }
      if (activeFilters.minConf > 0 && (m.confidence || 0) * 100 < activeFilters.minConf) return false;
      return true;
    });
    card.classList.toggle('filtered-out', !match);
    if (match) visibleCount++;
  });

  // Opacity on timeline markers — те же правила, что и для списка (включая статус ревью)
  markersData.forEach(m => {
    const st = store[m.id] ? store[m.id].status : 'pending';
    const matchM = (!activeFilters.category.size || activeFilters.category.has(m.category))
      && (!activeFilters.source.size || activeFilters.source.has((m.source || 'both').toLowerCase()))
      && (!activeFilters.status.size || activeFilters.status.has(st))
      && (activeFilters.minConf <= 0 || (m.confidence || 0) * 100 >= activeFilters.minConf);
    if (m._els) m._els.forEach(el => { el.style.opacity = matchM ? '' : '0.12'; });
  });

  updateFilterTags();
  const total = groupsData.length;
  const countEl = document.getElementById('filterCount');
  const hasFilter = activeFilters.category.size || activeFilters.source.size || activeFilters.status.size || activeFilters.minConf > 0;
  countEl.textContent = hasFilter ? visibleCount + ' / ' + total + ' групп' : '';
  document.getElementById('filterReset').style.display = hasFilter ? '' : 'none';
}

function updateFilterTags() {
  const tags = [];
  activeFilters.category.forEach(v => tags.push(v));
  activeFilters.source.forEach(v => tags.push(v));
  activeFilters.status.forEach(v => tags.push(v));
  if (activeFilters.minConf > 0) tags.push('\u2265' + activeFilters.minConf + '%');
  document.getElementById('filterTags').innerHTML = tags.map(t => '<span class="filter-tag">' + t + '</span>').join('');
}

function resetFilters() {
  activeFilters.category.clear();
  activeFilters.source.clear();
  activeFilters.status.clear();
  activeFilters.minConf = 0;
  document.getElementById('confSlider').value = 0;
  document.getElementById('confValue').textContent = '0';
  document.querySelectorAll('.filter-chip.active').forEach(c => c.classList.remove('active'));
  applyFilters();
}

// ── C7: Stat bar ──
function updateStatBar() {
  const bar = document.getElementById('statBar');
  if (!markersData.length) { bar.style.display = 'none'; return; }
  bar.style.display = '';
  const store = getReviewStore();
  const cats = {};
  const stats = { pending: 0, confirmed: 0, rejected: 0, reclassified: 0 };
  markersData.forEach(m => {
    const cat = m.category || '16+';
    cats[cat] = (cats[cat] || 0) + 1;
    const st = store[m.id] ? store[m.id].status : 'pending';
    stats[st] = (stats[st] || 0) + 1;
  });
  const catColors = {'prohibited':'var(--cat-prohibited)','18+':'var(--cat-18)','16+':'var(--cat-16)'};
  const stIcons = {'pending':'\u25FB','confirmed':'\u2713','rejected':'\u2717','reclassified':'\u21BB'};
  const stColors = {'pending':'var(--text-muted)','confirmed':'var(--feedback-confirm)','rejected':'var(--feedback-reject)','reclassified':'var(--feedback-reclass)'};
  const stLabels = {'pending':'без ответа','confirmed':'подтв.','rejected':'отклон.','reclassified':'перекл.'};
  let html = '';
  ['prohibited', '18+', '16+'].forEach(cat => {
    const n = cats[cat];
    if (!n) return;
    html += '<span class="stat-item" data-stat-filter="category:' + cat + '">'
      + '<span class="stat-dot" style="background:' + (catColors[cat] || 'var(--cat-16)') + '"></span>'
      + '<span class="stat-value">' + n + '</span> ' + cat + '</span>';
  });
  Object.entries(stats).forEach(([st, n]) => {
    if (n === 0) return;
    html += '<span class="stat-item" data-stat-filter="status:' + st + '" style="color:' + stColors[st] + '">'
      + stIcons[st] + ' <span class="stat-value">' + n + '</span> ' + stLabels[st] + '</span>';
  });
  bar.innerHTML = html;
  bar.querySelectorAll('.stat-item').forEach(item => {
    item.onclick = () => {
      const [type, value] = item.dataset.statFilter.split(':');
      resetFilters();
      activeFilters[type].add(value);
      const chip = document.querySelector('.filter-chip[data-filter="' + type + '"][data-value="' + value + '"]');
      if (chip) chip.classList.add('active');
      applyFilters();
    };
  });
}

function resortAndRender() {
  const severityOrder = {'prohibited': 0, '18+': 1, '16+': 2};
  const sorted = [...markersData];
  if (currentSort === 'severity') {
    sorted.sort((a, b) => (severityOrder[a.category] ?? 3) - (severityOrder[b.category] ?? 3) || a._startSec - b._startSec);
  } else if (currentSort === 'confidence') {
    sorted.sort((a, b) => (b.confidence || 0) - (a.confidence || 0));
  } else {
    sorted.sort((a, b) => a._startSec - b._startSec);
  }
  groupsData = groupByOverlap(sorted);
  const store = getReviewStore();
  markersData.forEach(m => { m._review = store[m.id] || null; });
  renderDetectionPanel(groupsData);
  applyReviewStates();
  buildFilterChips();
  applyFilters();
}

window.addEventListener('message', (ev) => {
  const d = ev.data;
  if (!d || d.type !== 'linza-detections') return;
  if (d.theme === 'light' || d.theme === 'dark') {
    document.documentElement.setAttribute('data-theme', d.theme);
    localStorage.setItem('linza-theme', d.theme);
    const btn = document.getElementById('themeToggle');
    if (btn) btn.textContent = d.theme === 'dark' ? '\u263E' : '\u2600';
  }
  if (Array.isArray(d.detections) && d.detections.length) {
    fetchAndApply(d.detections);
  }
});

/** Родительский Linza открывает плеер в iframe: sessionStorage у фрейма отделён от родителя, postMessage мог уйти до этого listener — сигнал «готов». */
(function notifyLinzaParentReady() {
  try {
    if (window.parent && window.parent !== window) {
      window.parent.postMessage({ type: 'linza-vpleer-ready' }, '*');
    }
  } catch (_) { /* ignore */ }
})();

(function bootstrapSessionDetections() {
  const ds = new URLSearchParams(window.location.search).get('ds');
  if (!ds) return;
  try {
    const raw = sessionStorage.getItem('linza-vpleer-ds:' + ds);
    if (!raw) return;
    const o = JSON.parse(raw);
    if (o.theme === 'light' || o.theme === 'dark') {
      document.documentElement.setAttribute('data-theme', o.theme);
      localStorage.setItem('linza-theme', o.theme);
      const btn = document.getElementById('themeToggle');
      if (btn) btn.textContent = o.theme === 'dark' ? '\u263E' : '\u2600';
    }
    if (Array.isArray(o.detections) && o.detections.length) {
      fetchAndApply(o.detections);
    }
  } catch (_) { /* ignore */ }
})();

// C8: beforeunload warning if there are unsaved reviews
window.addEventListener('beforeunload', (e) => {
  const store = getReviewStore();
  if (Object.keys(store).length > 0) {
    e.preventDefault();
  }
});
