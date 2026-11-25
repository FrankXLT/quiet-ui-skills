/* SPDX-License-Identifier: Apache-2.0 */
/**
 * Quiet UI v9.5 — Everyday Plain-English Overview Landing Page & Live Layout Preview
 */
(function (window, document) {
  'use strict';

  const DOMAIN_META = {
    '01-clinical-icu-and-trials': { title: 'Healthcare & Patient Care', desc: 'Hospital bedside monitors, clinical study results, and clear at-home recovery guides patients can read on their phone.', cta: 'Launch Healthcare Examples' },
    '02-cloud-cyber-and-ai-ops': { title: 'Cloud Software & AI', desc: 'Live server outage consoles, security review checklists, AI accuracy tracking, and software release timelines.', cta: 'Launch Cloud Examples' },
    '03-industrial-grid-and-manufacturing': { title: 'Power Grid & Factory', desc: 'Solar and battery microgrid controls, across-the-room factory status boards, and production quality reports.', cta: 'Launch Grid Examples' },
    '04-civic-finance-and-stem-learning': { title: 'Budgets, Finance & Classrooms', desc: 'City budget breakdowns, interest-rate stress calculators, hands-on physics labs, and student lab reports.', cta: 'Launch Finance Examples' },
    '05-physical-systems-auto-and-aero': { title: 'Vehicles, Flight & Smart Glass', desc: 'Engine efficiency studies, vehicle wiring scopes, aircraft head-up displays, and boat windshield overlays.', cta: 'Launch Vehicle Examples' },
    '06-smart-home-and-energy': { title: 'Smart Home & Energy', desc: 'Framed living-room art displays with subtle weather and solar status, plus a mobile home-control app.', cta: 'Launch Home Examples' },
  };

  const MORPH_MODES = {
    screen: { label: 'Desktop (1080p) · 1920×1080', note: 'Standard 1080p desktop view: live graph on the left, key numbers on the right, and plenty of room to scan.' },
    paper: { label: 'Printed Page · 1056×1368', note: 'Print-ready page: warm paper background, book-style serif text, and zero app menus so it exports cleanly to PDF.' },
    mobile: { label: 'Phone · 390×844', note: 'Phone screen (390px): stacks key numbers into one thumb-friendly column with comfortable tap targets.' },
    dark: { label: 'Dark Mode · Low-Glare', note: 'Low-glare dark theme: keeps backgrounds calm and saves bright yellow or red strictly for real warnings.' },
    brief: { label: 'Quick Summary · Key Points First', note: 'Busy-reader summary: puts the bottom-line status and safety margin first before the detailed graph.' },
  };

  function esc(val) {
    if (window.QuietStudioSheetV9 && window.QuietStudioSheetV9.escHtml) return window.QuietStudioSheetV9.escHtml(val);
    return String(val == null ? '' : val).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function svgTileIcon(kind) {
    const map = {
      step: '<path d="M3 8h10M9.5 4.5 13 8l-3.5 3.5" fill="none"/>',
      proof: '<path d="M2.5 12.5h11M4.5 9.5 7 6.5l2.2 2 3-4" fill="none"/>',
      rail: '<rect x="2.5" y="2.5" width="11" height="11" rx="1.5" fill="none"/><path d="M6.5 2.5v11" fill="none"/>',
      clinical: '<path d="M1.5 8h3l1.6-4 2.2 8 1.6-4h4.6" fill="none"/>',
      cloud: '<path d="M8 2 13 4v4c0 3-2 4.8-5 5.8C5 12.8 3 11 3 8V4z" fill="none"/>',
      grid: '<path d="M9 1.5 3.5 9H8l-1 5.5L12.5 7H8z" fill="none"/>',
      finance: '<path d="M2.5 6.5 8 3l5.5 3.5M4 6.5v5.5M8 6.5v5.5M12 6.5v5.5M2.5 13.5h11" fill="none"/>',
      aero: '<circle cx="8" cy="8" r="5.5" fill="none"/><path d="M8 4v4l2.5 1.5" fill="none"/>',
      home: '<path d="M2.5 7.5 8 2.5l5.5 5v6H10V9.5H6v4H2.5z" fill="none"/>',
    };
    return '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      (map[kind] || map.proof) + '</svg>';
  }

  function domainIconKind(worldId) {
    if (worldId.indexOf('01-') === 0) return 'clinical';
    if (worldId.indexOf('02-') === 0) return 'cloud';
    if (worldId.indexOf('03-') === 0) return 'grid';
    if (worldId.indexOf('04-') === 0) return 'finance';
    if (worldId.indexOf('05-') === 0) return 'aero';
    return 'home';
  }

  function pointToSegDist(px, py, ax, ay, bx, by) {
    const dx = bx - ax, dy = by - ay, len2 = dx * dx + dy * dy;
    const t = len2 > 0 ? Math.max(0, Math.min(1, ((px - ax) * dx + (py - ay) * dy) / len2)) : 0;
    const cx = ax + t * dx, cy = ay + t * dy;
    return Math.hypot(px - cx, py - cy);
  }

  function boxClearance(bx0, by0, bx1, by1, coords) {
    let minD = Infinity;
    for (let i = 0; i < coords.length; i += 1) {
      const p = coords[i];
      const cx = Math.max(bx0, Math.min(bx1, p[0])), cy = Math.max(by0, Math.min(by1, p[1]));
      minD = Math.min(minD, Math.hypot(p[0] - cx, p[1] - cy));
      if (i + 1 < coords.length) {
        const q = coords[i + 1];
        for (let s = 0; s <= 4; s += 1) {
          const sx = p[0] + (q[0] - p[0]) * (s / 4), sy = p[1] + (q[1] - p[1]) * (s / 4);
          const rx = Math.max(bx0, Math.min(bx1, sx)), ry = Math.max(by0, Math.min(by1, sy));
          minD = Math.min(minD, Math.hypot(sx - rx, sy - ry));
        }
        minD = Math.min(minD, pointToSegDist((bx0 + bx1) / 2, (by0 + by1) / 2, p[0], p[1], q[0], q[1]));
      }
    }
    return minD;
  }

  function placeThresholdLabel(coords, yT, x0, x1, txt) {
    const estW = txt.length * 6.3, padX = 5, padY = 3;
    const xs = [299, 156, 223, 385, 86];
    const yOpts = [];
    if (yT >= 32) yOpts.push({ y: +(yT - 7).toFixed(1), top: yT - 18, bot: yT - 5, bonus: 1.5 });
    if (yT <= 108) yOpts.push({ y: +(yT + 14).toFixed(1), top: yT + 3, bot: yT + 16, bonus: 0.0 });
    let best = { x: 299, anchor: 'middle', y: yOpts[0].y, score: -1 };
    yOpts.forEach(function (yo) {
      xs.forEach(function (cx) {
        const half = estW / 2;
        let lx = cx, anchor = 'middle', bx0 = cx - half, bx1 = cx + half;
        if (bx0 < x0 + 4) { lx = x0 + 4; anchor = 'start'; bx0 = lx; bx1 = lx + estW; }
        else if (bx1 > x1 - 4) { lx = x1 - 4; anchor = 'end'; bx0 = lx - estW; bx1 = lx; }
        const clear = boxClearance(bx0 - padX, yo.top - padY, bx1 + padX, yo.bot + padY, coords) + yo.bonus;
        if (clear > best.score) best = { x: lx, anchor: anchor, y: yo.y, score: clear };
      });
    });
    return best;
  }

  function buildWaveformSvgHtml(threshold) {
    const pts = [88, 94, 72, 62, 68, 91, 74, 63.5, 66, 89, 71, 63.5];
    const x0 = 46, x1 = 436, yTop = 20, yBot = 120;
    const yOf = function (v) { return +(yBot - ((v - 40) / 60) * (yBot - yTop)).toFixed(1); };
    const coords = pts.map(function (v, idx) {
      const x = +(x0 + idx * ((x1 - x0) / (pts.length - 1))).toFixed(1);
      return [x, yOf(v)];
    });
    const pathD = coords.map(function (p, i) { return (i === 0 ? 'M' : 'L') + p[0] + ' ' + p[1]; }).join(' ');
    const yT = yOf(threshold);
    const lblTxt = 'Limit ' + threshold + ' mmHg';
    const pos = placeThresholdLabel(coords, yT, x0, x1, lblTxt);
    const grids = [100, 80, 60, 40].map(function (v) {
      const gy = yOf(v);
      return '<line x1="' + x0 + '" y1="' + gy + '" x2="' + x1 + '" y2="' + gy + '" stroke="var(--morph-border)" stroke-width="0.9"/>' +
        '<text x="40" y="' + (gy + 4) + '" text-anchor="end" font-size="12" fill="var(--morph-muted)">' + v + '</text>';
    }).join('');
    const xTicks = [['0 s', x0, 'start'], ['2 s', 176, 'middle'], ['4 s', 306, 'middle'], ['6 s', x1, 'end']].map(function (t) {
      return '<text x="' + t[1] + '" y="140" text-anchor="' + t[2] + '" font-size="12" fill="var(--morph-muted)">' + t[0] + '</text>';
    }).join('');
    const dots = coords.map(function (p) {
      return '<circle cx="' + p[0] + '" cy="' + p[1] + '" r="2.8" fill="var(--morph-accent)"/>';
    }).join('');
    return '<svg class="va-morph-svg" viewBox="0 0 460 150" role="img" aria-label="Live Pressure Chart Preview">' +
      grids + xTicks +
      '<path d="' + pathD + '" fill="none" stroke="var(--morph-accent)" stroke-width="2" stroke-linejoin="round"/>' +
      dots +
      '<line id="va-morph-thresh-line" x1="' + x0 + '" y1="' + yT + '" x2="' + x1 + '" y2="' + yT + '" stroke="var(--morph-warn)" stroke-width="1.6" stroke-dasharray="5 3"/>' +
      '<text id="va-morph-thresh-label" class="va-svg-halo-text" x="' + pos.x + '" y="' + pos.y + '" text-anchor="' + pos.anchor + '" font-size="11.5" font-weight="700" paint-order="stroke fill" stroke="var(--morph-elevated)" stroke-width="4" stroke-linejoin="round" fill="var(--morph-warn)">' + lblTxt + '</text>' +
      '</svg>';
  }

  function buildDomainCardsHtml(worlds, getPreset) {
    return worlds.map(function (w, idx) {
      const num = String(idx + 1).padStart(2, '0');
      const meta = DOMAIN_META[w.world_id] || {};
      const viewsHtml = (w.views || []).map(function (v) {
        const pre = getPreset(v.view_id);
        return '<button type="button" class="va-domain-view-btn" data-launch-world="' + esc(w.world_id) + '" data-launch-view="' + esc(v.view_id) + '">' +
          '<span>' + esc(v.option_label) + '</span><span class="va-view-preset-tag">' + esc(pre.preset_label) + '</span></button>';
      }).join('');
      const firstView = (w.views && w.views[0]) ? w.views[0].view_id : '';
      return '<article class="va-domain-card"><div class="va-domain-card-top"><span class="va-step-icon-tile">' + svgTileIcon(domainIconKind(w.world_id)) + '</span>' +
        '<span class="va-domain-slug">&gt; domain_' + num + '_</span></div><h3>' + esc(meta.title || w.title) + '</h3>' +
        '<p class="va-domain-desc">' + esc(meta.desc || w.title) + '</p><div class="va-domain-view-list">' + viewsHtml + '</div>' +
        '<div class="va-domain-launch"><button type="button" class="va-domain-launch-btn" data-launch-world="' + esc(w.world_id) + '" data-launch-view="' + esc(firstView) + '">' + esc(meta.cta || ('Launch Domain ' + num)) + ' &rarr;</button></div></article>';
    }).join('');
  }

  function buildLandingHtml(worlds, totalViews, domainCardsHtml, installCmd) {
    return '<div class="va-landing-wrap"><section class="va-landing-hero" aria-label="Quiet UI Introduction">' +
      '<span class="va-landing-kicker">CLEAN INTERFACES &amp; HONEST CHARTS FOR AI CODING TOOLS</span>' +
      '<h1 class="va-landing-h1">Screens &amp; Reports Built to Be Read, Not Decorated</h1>' +
      '<p class="va-landing-sub">Most AI tools default to cluttered, neon dashboards that tire your eyes. Quiet UI gives AI coding agents calm layouts, readable charts, and automatic quality checks for desktop screens, printed pages, and phones.</p>' +
      '<div class="va-landing-chips">' +
      '<button type="button" class="va-landing-chip" data-scroll-target="va-landing-morph-card"><span class="va-chip-prompt">&gt;</span><span>how_it_works_</span></button>' +
      '<button type="button" class="va-landing-chip" data-scroll-target="va-landing-standards"><span class="va-chip-prompt">&gt;</span><span>real_world_rules_</span></button>' +
      '<button type="button" class="va-landing-chip" data-open-examples="1"><span class="va-chip-prompt">&gt;</span><span>' + totalViews + '_live_examples_</span></button>' +
      '<button type="button" class="va-landing-chip" data-open-components="1"><span class="va-chip-prompt">&gt;</span><span>49_building_blocks_</span></button>' +
      '<button type="button" class="va-landing-chip" data-scroll-target="va-landing-pillars"><span class="va-chip-prompt">&gt;</span><span>three_skills_</span></button>' +
      '<button type="button" class="va-landing-chip" data-scroll-target="va-landing-pillars"><span class="va-chip-prompt">&gt;</span><span>one_minute_install_</span></button>' +
      '</div></section>' +
      '<section id="va-landing-morph-card" class="va-morph-card" aria-label="How the Showcase Works and Live Preview"><div class="va-morph-steps">' +
      '<div class="va-morph-step"><span class="va-step-icon-tile">' + svgTileIcon('step') + '</span><div><h2>1. Flip Through Real Screens</h2><p>Use &lt; and &gt; in the top bar to step through ' + totalViews + ' examples across desktop monitors, printable pages, phones, and dark mode.</p></div></div>' +
      '<div class="va-morph-step"><span class="va-step-icon-tile">' + svgTileIcon('proof') + '</span><div><h2>2. See Why Every Choice Matters</h2><p>Labels never collide with chart lines, numbers match from summary to detail, and clicking <strong>Why?</strong> explains each layout in plain English.</p></div></div>' +
      '<div class="va-morph-step"><span class="va-step-icon-tile">' + svgTileIcon('rail') + '</span><div><h2>3. Try the Live Controls</h2><p>Open or close the sidebar, jump along live signal graphs, click table rows to inspect details, or drag the window edges to resize.</p></div></div>' +
      '</div><div class="va-morph-stage-wrap"><div class="va-morph-stage-hdr">' +
      '<div class="va-morph-stage-title"><span>LIVE LAYOUT PREVIEW</span><span>·</span><span id="va-morph-mode-label">Desktop (1080p) · 1920×1080</span></div>' +
      '<div class="va-morph-stage-actions"><span id="va-morph-status-pill" class="va-morph-status-pill" data-state="warn">Caution · Avg &lt; 75 mmHg</span>' +
      '<button type="button" id="va-morph-open-portal" class="va-landing-cta">Open Live Example &rarr;</button></div></div>' +
      '<div id="va-morph-canvas" class="va-morph-canvas" data-morph-mode="screen">' +
      '<div id="va-morph-svg-host" class="va-morph-plot-box">' + buildWaveformSvgHtml(75) + '</div>' +
      '<div><div class="va-morph-kpis"><div class="va-morph-kpi"><span>Average Pressure</span><strong>63.5 mmHg</strong></div>' +
      '<div class="va-morph-kpi"><span>Peak Reading</span><strong>94.0 mmHg</strong></div><div class="va-morph-kpi"><span>Safety Margin</span><strong id="va-morph-margin-val">-11.5 mmHg</strong></div></div>' +
      '<p id="va-morph-mode-note" class="va-morph-summary">' + esc(MORPH_MODES.screen.note) + '</p></div></div>' +
      '<div class="va-morph-controls"><div class="va-morph-mode-group" role="group" aria-label="Preview Layout">' +
      '<button type="button" class="va-morph-mode-btn" data-morph-btn="screen" aria-pressed="true">1. Desktop (1080p)</button>' +
      '<button type="button" class="va-morph-mode-btn" data-morph-btn="paper" aria-pressed="false">2. Printed Page</button>' +
      '<button type="button" class="va-morph-mode-btn" data-morph-btn="mobile" aria-pressed="false">3. Phone (390px)</button>' +
      '<button type="button" class="va-morph-mode-btn" data-morph-btn="dark" aria-pressed="false">4. Dark Mode</button>' +
      '<button type="button" class="va-morph-mode-btn" data-morph-btn="brief" aria-pressed="false">5. Quick Summary</button></div>' +
      '<div class="va-morph-slider-wrap"><label for="va-morph-threshold">Warning Limit: <strong id="va-morph-threshold-val" class="va-nums">75 mmHg</strong></label>' +
      '<input type="range" id="va-morph-threshold" min="55" max="95" step="1" value="75" aria-valuetext="75 mmHg"></div></div></div></section>' +
      '<section id="va-landing-standards" aria-label="Standards Grounded in Practical Real-World Rules"><div class="va-landing-sec-hdr"><h2>Grounded in Practical Real-World Standards</h2>' +
      '<span>Instead of guessing what looks good, Quiet UI borrows proven everyday rules from science labs, hospitals, aviation, and power-grid control rooms.</span></div>' +
      '<div class="va-standards-grid">' +
      '<article class="va-standard-card"><h3>1. Numbers &amp; Charts That Never Mislead</h3><p>Chart axes count by clean 1, 2, or 5 steps instead of awkward decimals, every number shows its unit clearly, and missing sensor data leaves an honest gap instead of faking a smooth line.</p><div class="va-std-tags"><span class="va-std-tag">NIST SP 811</span><span class="va-std-tag">ISO 80000</span><span class="va-std-tag">Quality Charts</span></div></article>' +
      '<article class="va-standard-card"><h3>2. Calm Screens So Real Warnings Stand Out</h3><p>Borrowed from power-plant control rooms: normal readings stay quiet gray and blue instead of rainbow widgets—saving bright amber and red strictly for problems that need action.</p><div class="va-std-tags"><span class="va-std-tag">ISA-101</span><span class="va-std-tag">NRC NUREG-0700</span><span class="va-std-tag">Safety Trees</span></div></article>' +
      '<article class="va-standard-card"><h3>3. Readable Text &amp; Mistake-Proof Buttons</h3><p>Borrowed from hospital monitors and flight decks: text never shrinks below 11px, phone buttons fit real thumbs (44px), and critical switches take two steps (Arm, then Run) to prevent slips.</p><div class="va-std-tags"><span class="va-std-tag">FDA IEC 62366</span><span class="va-std-tag">NASA-STD-3001</span><span class="va-std-tag">Optical HUDs</span></div></article>' +
      '<article class="va-standard-card"><h3>4. Clear Forms, Diagrams &amp; Honest AI</h3><p>Forms explain how to fix an input instead of locking buttons silently, empty searches always offer a one-click reset, and summary numbers trace straight back to real source data.</p><div class="va-std-tags"><span class="va-std-tag">NIST AI RMF</span><span class="va-std-tag">SAE J1939</span><span class="va-std-tag">US Web Design</span></div></article></div></section>' +
      '<section id="va-landing-domains" aria-label="Explore Domains and Live Examples"><div class="va-landing-sec-hdr"><h2>Explore ' + worlds.length + ' Real-World Domains &amp; ' + totalViews + ' Live Examples</h2>' +
      '<span>Click any example below to open it in a desktop window, printable page, or phone frame.</span></div><div class="va-domain-grid">' + domainCardsHtml + '</div></section>' +
      '<section id="va-landing-pillars" class="va-pillars-card" aria-label="Three Focused Skills and One-Minute Install">' +
      '<div class="va-landing-sec-hdr"><h2>Three Focused Skills &amp; One-Minute Install</h2><span>Works locally with Antigravity, Claude Code, Cursor, Codex, and Windsurf — zero extra packages required.</span></div>' +
      '<div class="va-pillars-grid"><div class="va-pillar-col"><h3>quiet-ui (Clean Layouts)</h3><p>Chooses sensible spacing, fonts, and menus for desktop apps, printed reports, wall boards, and phones — plus <code>audit_quiet_html.py</code> to catch layout bugs automatically.</p></div>' +
      '<div class="va-pillar-col"><h3>quiet-evidence (Honest Charts)</h3><p>Builds 49 ready-to-use charts, timelines, tables, signal traces, and diagrams where labels stay readable across light and dark themes.</p></div>' +
      '<div class="va-pillar-col"><h3>quiet-bridge (Plain Language)</h3><p>Tailors complex data for executives, engineers, operators, or students in clear everyday language without altering a single number.</p></div></div>' +
      '<div class="va-install-bar"><div class="va-install-code-row"><code>' + esc(installCmd) + '</code><button type="button" id="va-landing-copy-install" class="va-studio-btn">Copy</button>' +
      '<span id="va-landing-copy-status" class="va-copy-status" role="status"></span></div><button type="button" id="va-landing-open-components" class="va-landing-cta">Browse All 49 Building Blocks &rarr;</button></div></section></div>';
  }

  function wireMorphControls(root) {
    const canvas = document.getElementById('va-morph-canvas');
    const modeLbl = document.getElementById('va-morph-mode-label');
    const modeNote = document.getElementById('va-morph-mode-note');
    const svgHost = document.getElementById('va-morph-svg-host');
    const statusPill = document.getElementById('va-morph-status-pill');
    const marginVal = document.getElementById('va-morph-margin-val');
    const slider = document.getElementById('va-morph-threshold');
    const sliderVal = document.getElementById('va-morph-threshold-val');
    function syncMorphSlider() {
      if (!slider) return;
      const th = parseInt(slider.value || '75', 10);
      const pct = ((th - 55) / (95 - 55)) * 100;
      slider.style.setProperty('--slider-progress', pct.toFixed(1) + '%');
      slider.setAttribute('aria-valuetext', th + ' mmHg');
      if (sliderVal) sliderVal.textContent = th + ' mmHg';
      if (svgHost) svgHost.innerHTML = buildWaveformSvgHtml(th);
      const margin = 63.5 - th;
      if (marginVal) marginVal.textContent = (margin >= 0 ? '+' : '') + margin.toFixed(1) + ' mmHg';
      if (statusPill) {
        const warn = margin < 0;
        statusPill.setAttribute('data-state', warn ? 'warn' : 'nominal');
        statusPill.textContent = warn ? ('Caution · Avg < ' + th + ' mmHg') : ('Normal · Avg >= ' + th + ' mmHg');
      }
    }
    if (slider) { syncMorphSlider(); slider.addEventListener('input', syncMorphSlider); }
    root.querySelectorAll('[data-morph-btn]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        const mode = btn.getAttribute('data-morph-btn') || 'screen';
        const cfg = MORPH_MODES[mode] || MORPH_MODES.screen;
        if (canvas) canvas.setAttribute('data-morph-mode', mode);
        if (modeLbl) modeLbl.textContent = cfg.label;
        if (modeNote) modeNote.textContent = cfg.note;
        root.querySelectorAll('[data-morph-btn]').forEach(function (b) { b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); });
      });
    });
  }

  function wireLandingActions(root, portalApi, installCmd) {
    root.querySelectorAll('[data-launch-view]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        if (portalApi && portalApi.openExamples) portalApi.openExamples(btn.getAttribute('data-launch-world'), btn.getAttribute('data-launch-view'));
      });
    });
    root.querySelectorAll('[data-open-examples]').forEach(function (btn) {
      btn.addEventListener('click', function () { if (portalApi && portalApi.openExamples) portalApi.openExamples(); });
    });
    root.querySelectorAll('[data-open-components]').forEach(function (btn) {
      btn.addEventListener('click', function () { if (portalApi && portalApi.openComponents) portalApi.openComponents(); });
    });
    const openPortalBtn = document.getElementById('va-morph-open-portal');
    if (openPortalBtn) openPortalBtn.addEventListener('click', function () {
      if (portalApi && portalApi.openExamples) portalApi.openExamples('01-clinical-icu-and-trials', 'v01-icu-bedside-terminal');
    });
    const openCompBtn = document.getElementById('va-landing-open-components');
    if (openCompBtn) openCompBtn.addEventListener('click', function () { if (portalApi && portalApi.openComponents) portalApi.openComponents(); });
    root.querySelectorAll('[data-scroll-target]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        const tgt = document.getElementById(btn.getAttribute('data-scroll-target') || '');
        if (tgt && tgt.scrollIntoView) tgt.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    });
    const copyBtn = document.getElementById('va-landing-copy-install');
    const copyStatus = document.getElementById('va-landing-copy-status');
    if (copyBtn) copyBtn.addEventListener('click', function () {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(installCmd).then(
          function () { if (copyStatus) copyStatus.textContent = 'Install command copied'; },
          function () { if (copyStatus) copyStatus.textContent = 'Copy unavailable'; }
        );
      }
    });
  }

  function renderLanding(manifest, portalApi) {
    const root = document.getElementById('va-studio-landing');
    if (!root) return;
    const worlds = (manifest && manifest.worlds) ? manifest.worlds : [];
    const totalViews = worlds.reduce(function (acc, w) { return acc + ((w.views && w.views.length) || 0); }, 0);
    const getPreset = window.QuietStudioPresetsRailV9 ? window.QuietStudioPresetsRailV9.getViewPreset : function () { return { preset_label: '1080p Screen' }; };
    const ghHost = (window.location && window.location.hostname) || '';
    const rawSeg = ((window.location && window.location.pathname) || '').split('/').filter(Boolean)[0] || '';
    const ghOwner = /\.github\.io$/i.test(ghHost) ? ghHost.replace(/\.github\.io$/i, '').replace(/[^a-zA-Z0-9-]/g, '') : '';
    const ghRepo = (rawSeg && !/\.html?$/i.test(rawSeg) ? rawSeg : 'quiet-ui-skills').replace(/[^a-zA-Z0-9._-]/g, '') || 'quiet-ui-skills';
    const installCmd = ghOwner ? ('git clone https://github.com/' + ghOwner + '/' + ghRepo + '.git && cd ' + ghRepo + ' && ./install.sh') : './install.sh';
    root.innerHTML = buildLandingHtml(worlds, totalViews, buildDomainCardsHtml(worlds, getPreset), installCmd);
    wireMorphControls(root);
    wireLandingActions(root, portalApi, installCmd);
  }

  window.QuietStudioLandingV9 = {
    renderLanding: renderLanding,
  };
})(window, document);
