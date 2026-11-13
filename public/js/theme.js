/* Light / dark theme. Loaded in <head> (before first paint) so there is no flash of the wrong theme.
   Default follows the device setting; the toggle remembers the person's choice. */
(function () {
  'use strict';
  var KEY = 'tickit_theme';
  var root = document.documentElement;
  var media = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;

  function saved() { try { var v = localStorage.getItem(KEY); return v === 'dark' || v === 'light' ? v : null; } catch (_) { return null; } }
  function current() { return saved() || (media && media.matches ? 'dark' : 'light'); }
  function apply(theme) {
    root.setAttribute('data-theme', theme);
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', theme === 'dark' ? '#0e0e0e' : '#ffffff');
    var btn = document.getElementById('themeToggle');
    if (btn) {
      btn.textContent = theme === 'dark' ? '\u2600' : '\u263E';   // sun / moon
      btn.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
      btn.title = btn.getAttribute('aria-label');
    }
  }

  apply(current());

  if (media && media.addEventListener) {
    media.addEventListener('change', function () { if (!saved()) apply(current()); });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var host = document.querySelector('.nav-right') || document.querySelector('.nav');
    if (!host) return;
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.id = 'themeToggle';
    btn.className = 'theme-toggle';
    btn.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem(KEY, next); } catch (_) { /* private mode: still switch for this visit */ }
      apply(next);
    });
    host.insertBefore(btn, host.firstChild);
    apply(root.getAttribute('data-theme') || current());
  });
})();
