// Firebase initialization for SuryaDrishti (project: codex-i)
// Loaded via ES module in dashboard.html. Analytics only works over http(s).
//
// Config resolution order (no secrets are stored in git):
//   1. Firebase Hosting reserved endpoint: /__/firebase/init.json (works when
//      the site is served from Firebase Hosting).
//   2. window.FIREBASE_CONFIG from firebase-secrets.js — a gitignored file
//      kept locally so Vercel/local deployments still get the config.
//   3. If neither is available, analytics is skipped and the dashboard
//      continues to work normally.

(async function initFirebase() {
  let cfg = null;

  // 1) Firebase Hosting reserved config endpoint
  try {
    const r = await fetch('/__/firebase/init.json');
    if (r.ok) cfg = await r.json();
  } catch (e) { /* not served by Firebase Hosting */ }

  // 2) Local gitignored secrets file (present on disk at deploy time)
  if (!cfg && window.FIREBASE_CONFIG) cfg = window.FIREBASE_CONFIG;

  if (!cfg) {
    console.info('[SuryaDrishti] Firebase config unavailable — analytics disabled');
    return;
  }

  try {
    const { initializeApp } = await import('https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js');
    const { getAnalytics } = await import('https://www.gstatic.com/firebasejs/10.12.2/firebase-analytics.js');
    const app = initializeApp(cfg);
    window.__suryaFirebase = app;      // expose for other scripts
    window.__suryaAnalytics = getAnalytics(app);
    console.log('[SuryaDrishti] Firebase initialized:', cfg.projectId);
  } catch (e) {
    console.warn('[SuryaDrishti] Firebase init skipped:', e.message);
  }
})();
