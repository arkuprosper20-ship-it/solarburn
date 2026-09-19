/* ============================================================================
 * SuryaDrishti — ui-shell.js
 * ----------------------------------------------------------------------------
 * Shared application chrome injected into every dashboard page:
 *   • top navigation with 3D / 2D / overview view switching
 *   • boot splash that hides as soon as the page is interactive
 *   • toast notification stack (window.SDUI.toast / SDUI.alert)
 *   • alert-level watcher that raises toasts on CRITICAL / ELEVATED
 *   • keyboard shortcut overlay
 *   • presentation "focus mode" that hides the chrome
 *
 * Kept separate from dashboard.js on purpose: dashboard.js owns telemetry and
 * rendering, this file owns navigation. No jQuery, no build step, no deps.
 * ========================================================================== */
(function () {
  'use strict';

  var STORE = {
    view:  'sd.view',
    focus: 'sd.focus',
    toast: 'sd.alertToasts'
  };

  var REPO = 'https://github.com/arkuprosper20-ship-it/solarburn';

  var UI = {};
  window.SDUI = UI;

  /* ---------------------------------------------------------------- utils - */
  function el(tag, cls, html) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html != null) n.innerHTML = html;
    return n;
  }
  function store(key, val) {
    try {
      if (val === undefined) return window.localStorage.getItem(key);
      window.localStorage.setItem(key, val);
      return val;
    } catch (e) { return null; }
  }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function reducedMotion() {
    return !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  }

  /* ----------------------------------------------------------- page id --- */
  function detectPage() {
    var p = (location.pathname || '').toLowerCase();
    if (p.indexOf('dashboard_2d') !== -1) return '2d';
    if (p.indexOf('dashboard') !== -1) return '3d';
    return 'home';
  }

  var PAGE = detectPage();

  var VIEWS = [
    { id: 'home', label: 'Overview',        href: './index.html',         icon: '◈' },
    { id: '3d',   label: '3D Command Deck', href: './dashboard.html',     icon: '🌐' },
    { id: '2d',   label: '2D Analytics',    href: './dashboard_2d.html',  icon: '📊' }
  ];

  var EXTERNAL = [
    { label: 'Streamlit ML Console', href: 'http://localhost:8501', icon: '🧠', title: 'Local Streamlit scientific dashboard (port 8501)' },
    { label: 'Source',               href: REPO,                    icon: '⌥', title: 'Repository' }
  ];
  /* ------------------------------------------------------------ toasts --- */
  var toastWrap = null;
  function toastHost() {
    if (!toastWrap) {
      toastWrap = el('div', 'sd-toast-wrap');
      toastWrap.setAttribute('role', 'region');
      toastWrap.setAttribute('aria-live', 'polite');
      toastWrap.setAttribute('aria-label', 'Notifications');
      document.body.appendChild(toastWrap);
    }
    return toastWrap;
  }

  UI.toast = function (message, kind, ttl) {
    var host = toastHost();
    var icon = { ok: '✓', warn: '⚠', err: '✕', info: '◈' }[kind] || '◈';
    var node = el('div', 'sd-toast sd-toast-' + (kind || 'info'),
      '<span class="sd-toast-ico">' + icon + '</span>' +
      '<span class="sd-toast-msg">' + esc(message) + '</span>' +
      '<button class="sd-toast-x" type="button" aria-label="Dismiss">×</button>');
    host.appendChild(node);
    var kill = function () {
      node.classList.add('sd-toast-out');
      window.setTimeout(function () {
        if (node.parentNode) node.parentNode.removeChild(node);
      }, reducedMotion() ? 0 : 260);
    };
    node.querySelector('.sd-toast-x').addEventListener('click', kill);
    window.setTimeout(kill, ttl || 5200);
    return node;
  };
  UI.alert = function (m, k) { return UI.toast(m, k || 'warn', 9000); };

  /* --------------------------------------------------------- chrome ------- */
  UI.setFocusMode = function (on) {
    document.body.classList.toggle('sd-focus', !!on);
    store(STORE.focus, on ? '1' : '0');
    var btn = document.getElementById('sd-focus-btn');
    if (btn) {
      btn.classList.toggle('sd-on', !!on);
      btn.title = on ? 'Show navigation (F) [currently hidden]' : 'Focus mode — hide navigation (F)';
    }
  };
  UI.toggleFocusMode = function () {
    return UI.setFocusMode(!document.body.classList.contains('sd-focus'));
  };

  function buildNav() {
    var host = document.getElementById('sd-shell');
    if (!host) return;

    var online = navigator.onLine !== false;
    var bar = el('div', 'sd-nav');
    bar.innerHTML =
      '<div class="sd-nav-l">' +
        '<a class="sd-brand" href="./index.html" title="SuryaDrishti home">' +
          '<img class="sd-logo" src="./favicon.svg" alt="" width="28" height="28">' +
          '<span class="sd-brand-txt">' +
            '<span class="sd-brand-nm">SURYA<span class="sd-brand-ac">DRISHTI</span></span>' +
            '<span class="sd-brand-sub">Aditya-L1 · Solar Flare Intelligence</span>' +
          '</span>' +
        '</a>' +
      '</div>' +
      '<nav class="sd-nav-c" aria-label="Dashboard views">' +
        VIEWS.map(function (v) {
          return '<a class="sd-vtab' + (v.id === PAGE ? ' sd-active' : '') + '"' +
            (v.id === PAGE ? ' aria-current="page"' : '') +
            ' href="' + v.href + '"><span class="sd-vico">' + v.icon + '</span>' +
            '<span class="sd-vlbl">' + esc(v.label) + '</span></a>';
        }).join('') +
      '</nav>' +
      '<div class="sd-nav-r">' +
        '<span class="sd-pill" id="sd-net-pill" title="Network status">' +
          '<span class="sd-pdot' + (online ? ' sd-live' : ' sd-off') + '"></span>' +
          '<span class="sd-ptxt">' + (online ? 'ONLINE' : 'OFFLINE') + '</span>' +
        '</span>' +
        '<div class="sd-extra">' +
          EXTERNAL.map(function (x) {
            return '<a class="sd-xbtn" href="' + x.href + '" title="' + esc(x.title || x.label) + '"' +
              (x.href.indexOf('http') === 0 ? ' target="_blank" rel="noopener"' : '') + '>' +
              '<span>' + x.icon + '</span><span class="sd-xlbl">' + esc(x.label) + '</span></a>';
          }).join('') +
        '</div>' +
        '<button class="sd-icon" id="sd-focus-btn" type="button" title="Focus mode — hide navigation (F)" aria-label="Toggle focus mode">⛶</button>' +
        '<button class="sd-icon" id="sd-keys-btn" type="button" title="Keyboard shortcuts (?)" aria-label="Keyboard shortcuts">?</button>' +
      '</div>';

    host.appendChild(bar);

    var nav = bar.querySelector('.sd-nav-c');
    if (nav && nav.scrollWidth > nav.clientWidth + 4) nav.classList.add('sd-scrolls');

    var fb = document.getElementById('sd-focus-btn');
    if (fb) fb.addEventListener('click', function () { UI.toggleFocusMode(); });
    var kb = document.getElementById('sd-keys-btn');
    if (kb) kb.addEventListener('click', function () { UI.showShortcuts(); });

    window.addEventListener('online', function () { net(true); });
    window.addEventListener('offline', function () { net(false); });
  }

  function net(online) {
    var pill = document.getElementById('sd-net-pill');
    if (!pill) return;
    var dot = pill.querySelector('.sd-pdot');
    var txt = pill.querySelector('.sd-ptxt');
    if (dot) dot.className = 'sd-pdot ' + (online ? 'sd-live' : 'sd-off');
    if (txt) txt.textContent = online ? 'ONLINE' : 'OFFLINE';
    if (!online) UI.alert('Network lost — dashboards continue on cached telemetry.', 'warn');
  }
  /* ----------------------------------------------------------- splash ----- */
  var splash = null;
  function buildSplash() {
    splash = el('div', 'sd-splash',
      '<div class="sd-splash-in">' +
        '<img class="sd-splash-logo" src="./favicon.svg" alt="" width="72" height="72">' +
        '<div class="sd-splash-nm">SURYA<span>DRISHTI</span></div>' +
        '<div class="sd-splash-sub">ADITYA-L1 · SOLAR FLARE INTELLIGENCE</div>' +
        '<div class="sd-splash-bar"><i></i></div>' +
        '<div class="sd-splash-note">Initialising telemetry, ephemeris and model kernels…</div>' +
      '</div>');
    document.body.appendChild(splash);
  }
  function hideSplash() {
    if (!splash || splash.classList.contains('sd-gone')) return;
    splash.classList.add('sd-gone');
    window.setTimeout(function () {
      if (splash && splash.parentNode) splash.parentNode.removeChild(splash);
      splash = null;
    }, reducedMotion() ? 0 : 620);
  }
  UI.hideSplash = hideSplash;

  /* -------------------------------------------------------- shortcuts ----- */
  var KEYS = [
    ['F', 'Toggle focus mode (hide chrome for presentations)'],
    ['?', 'Show / hide this shortcut sheet'],
    ['Space', 'Play or pause the telemetry replay'],
    ['→ / ←', 'Step the replay timeline'],
    ['D', 'Toggle demo mode'],
    ['1 / 2 / 3', 'Jump to 3D deck, 2D analytics, overview'],
    ['Esc', 'Close any open dialog or inspect view'],
    ['+ / − / 0', 'Zoom in / out / reset inside an inspector'],
    ['Wheel + drag', 'Zoom and pan any 3D object'],
    ['Double-click', 'Open a 3D object in the fullscreen inspector']
  ];

  UI.showShortcuts = function () {
    if (document.querySelector('.sd-sheet')) return UI.hideShortcuts();
    var rows = KEYS.map(function (k) {
      return '<div class="sd-keyrow"><kbd>' + esc(k[0]) + '</kbd><span>' + esc(k[1]) + '</span></div>';
    }).join('');
    var sheet = el('div', 'sd-sheet',
      '<div class="sd-sheet-card" role="dialog" aria-modal="true" aria-label="Keyboard shortcuts">' +
        '<div class="sd-sheet-hd"><b>Keyboard shortcuts</b>' +
        '<button class="sd-sheet-x" type="button" aria-label="Close">×</button></div>' +
        '<div class="sd-sheet-bd">' + rows + '</div>' +
        '<div class="sd-sheet-ft">Press <kbd>?</kbd> or <kbd>Esc</kbd> to close</div>' +
      '</div>');
    document.body.appendChild(sheet);
    sheet.addEventListener('click', function (e) {
      if (e.target === sheet || e.target.classList.contains('sd-sheet-x')) UI.hideShortcuts();
    });
  };
  UI.hideShortcuts = function () {
    var s = document.querySelector('.sd-sheet');
    if (s && s.parentNode) s.parentNode.removeChild(s);
  };

  function bindKeys() {
    document.addEventListener('keydown', function (e) {
      var t = e.target || {};
      var typing = t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' ||
                   t.tagName === 'SELECT' || t.isContentEditable;
      if (typing) return;
      var k = e.key;
      if (k === '?') { e.preventDefault(); UI.showShortcuts(); return; }
      if (k === 'Escape') { UI.hideShortcuts(); return; }
      if (k === 'f' || k === 'F') { e.preventDefault(); UI.toggleFocusMode(); return; }
      if (k === '1') { location.href = './dashboard.html'; return; }
      if (k === '2') { location.href = './dashboard_2d.html'; return; }
      if (k === '3') { location.href = './index.html'; return; }
    });
    }

  /* ----------------------------------------------- mobile menu toggle --- */
  function bindMobileMenu() {
    var btn = document.getElementById('mobile-menu-btn');
    var inner = document.querySelector('.h-right-inner');
    if (!btn || !inner) return;
    btn.setAttribute('aria-expanded', 'false');
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var expanded = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', !expanded);
      inner.classList.toggle('mobile-open', !expanded);
      inner.classList.toggle('mobile-closed', expanded);
    });
    btn.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ' || e.key === 'Escape') {
        e.preventDefault();
        btn.click();
      }
    });
    // close menu when clicking outside
    document.addEventListener('click', function () {
      inner.classList.remove('mobile-open');
      inner.classList.add('mobile-closed');
      btn.setAttribute('aria-expanded', 'false');
    });
    // close on ESC
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        inner.classList.remove('mobile-open');
        inner.classList.add('mobile-closed');
        btn.setAttribute('aria-expanded', 'false');
      }
    });
  }

  /* ---------------------------------------------------- alert watcher ----- */
  function watchAlerts() {
    if (store(STORE.toast) === 'off') return;
    var last = '';
    function current() {
      var a = document.getElementById('al-level');
      var b = document.getElementById('alert-panel');
      var txt = (a && a.textContent) || '';
      var cls = (b && b.className) || '';
      return (cls + '|' + txt).trim();
    }
    function check() {
      var now = current();
      if (now === last) return;
      last = now;
      var lvl = (document.getElementById('al-level') || {}).textContent || '';
      var desc = (document.getElementById('al-desc') || {}).textContent || '';
      if (/CRITICAL/i.test(lvl)) {
        UI.alert('CRITICAL — X-class flare risk elevated. ' + desc.slice(0, 120), 'err');
      } else if (/ELEVATED|HIGH/i.test(lvl)) {
        UI.alert('ELEVATED — M-class flare signatures detected. ' + desc.slice(0, 120), 'warn');
      }
    }
    window.setInterval(check, 2500);
  }

  /* -------------------------------------------------------------- boot ---- */
  function init() {
    if (!document.getElementById('sd-shell')) {
      var host = el('div', 'sd-shell');
      host.id = 'sd-shell';
      document.body.insertBefore(host, document.body.firstChild);
    }
    buildSplash();
    buildNav();
    bindKeys();
    bindMobileMenu();
    watchAlerts();

    if (store(STORE.focus) === '1') UI.setFocusMode(true);

    var done = function () {
      window.setTimeout(function () {
        hideSplash();
        if (PAGE === 'home') return;
      }, reducedMotion() ? 0 : 380);
    };
    if (document.readyState === 'complete') done();
    else window.addEventListener('load', done);
    /* hard safety net: never leave the splash up */
    window.setTimeout(hideSplash, 6000);

    window.addEventListener('beforeunload', function () {
      if (PAGE !== 'home') store(STORE.view, PAGE);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
