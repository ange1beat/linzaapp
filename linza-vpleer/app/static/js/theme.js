// ── Theme ──
function toggleTheme() {
  const html = document.documentElement;
  const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  localStorage.setItem('linza-theme', next);
  const btn = document.getElementById('themeToggle');
  if (btn) btn.textContent = next === 'dark' ? '\u263E' : '\u2600';
}
(function initTheme() {
  const params = new URLSearchParams(window.location.search);
  const qTheme = params.get('theme');
  let initial;
  if (qTheme === 'light' || qTheme === 'dark') {
    initial = qTheme;
    localStorage.setItem('linza-theme', initial);
  } else {
    initial = localStorage.getItem('linza-theme')
      || (matchMedia('(prefers-color-scheme:light)').matches ? 'light' : 'dark');
  }
  document.documentElement.setAttribute('data-theme', initial);
  const btn = document.getElementById('themeToggle');
  if (btn) btn.textContent = initial === 'dark' ? '\u263E' : '\u2600';
})();
