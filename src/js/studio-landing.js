/* SPDX-License-Identifier: Apache-2.0 */
/**
 * Quiet UI v9.5 — OAW-Style Overview Landing Page & Live Medium Morph Preview
 */
(function (window, document) {
  'use strict';

  const DOMAIN_DESCRIPTIONS = {
    '01-clinical-icu-and-trials': 'Bedside hemodynamic waveform monitors, Phase III CONSORT subgroup briefs, and plain-language patient recovery guides.',
    '02-cloud-cyber-and-ai-ops': 'Tail-latency SRE workbenches, zero-trust enclave specs, AI calibration lineage, and release critical-path triage.',
    '03-industrial-grid-and-manufacturing': 'Microgrid POI dispatch SCADA, 10-foot plant wall KPI kiosks, and Shewhart statistical quality reports.',
    '04-civic-finance-and-stem-learning': 'Municipal reserve waterfalls, Monte Carlo rate-shock solvers, interactive physics labs, and student capstone defenses.',
    '05-physical-systems-auto-and-aero': 'Propulsion efficiency monographs, CAN-FD reflection scopes, collimated optical HUDs, and smart-glass overlays.',
    '06-smart-home-and-energy': 'Ambient living-room picture-frame kiosks and Home Assistant solar, climate, and two-step door access consoles.',
  };

  const MORPH_MODES = {
    screen: { label: '1080p Screen · 1920×1080', note: 'White desk monitor surface with dual-pane signal waveform, KPI tiles, and interactive ceiling.' },
    paper: { label: 'Archival Paper · 1056×1368', note: 'Warm print sheet using Georgia serif typography, high-contrast black ink rules, and zero chrome clutter.' },
    mobile: { label: 'Mobile Phone · 390×844', note: 'Responsive 390px handset bezel stacking scalar summary tiles and mobile dock controls smoothly.' },
    dark: { label: 'Dark Cockpit · Slate / OLED', note: 'Night-operations polarity preserving crisp gridlines and reserving amber strictly for threshold crossings.' },
    brief: { label: 'Executive Brief · Summary Lens', note: 'Compression lens leading with operational margin delta and threshold disposition before detail proof.' },
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
    const yText = yT >= 38 ? +(yT - 6).toFixed(1) : +(yT + 14).toFixed(1);
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
    return '<svg class="va-morph-svg" viewBox="0 0 460 150" role="img" aria-label="Live Arterial Pressure Signal Preview">' +
      grids + xTicks +
      '<path d="' + pathD + '" fill="none" stroke="var(--morph-accent)" stroke-width="2" stroke-linejoin="round"/>' +
      dots +
      '<line id="va-morph-thresh-line" x1="' + x0 + '" y1="' + yT + '" x2="' + x1 + '" y2="' + yT + '" stroke="var(--morph-warn)" stroke-width="1.6" stroke-dasharray="5 3"/>' +
      '<text id="va-morph-thresh-label" class="va-svg-halo-text" x="' + (x1 - 4) + '" y="' + yText + '" text-anchor="end" font-size="12" font-weight="700" paint-order="stroke" stroke="var(--morph-bg)" stroke-width="3" fill="var(--morph-warn)">Ceiling ' + threshold + ' mmHg</text>' +
      '</svg>';
  }

  function renderLanding(manifest, portalApi) {
    const root = document.getElementById('va-studio-landing');
    if (!root) return;
    const worlds = (manifest && manifest.worlds) ? manifest.worlds : [];
    const totalViews = worlds.reduce(function (acc, w) { return acc + ((w.views && w.views.length) || 0); }, 0);
    const getPreset = window.QuietStudioPresetsRailV9 ? window.QuietStudioPresetsRailV9.getViewPreset : function () { return { preset_label: '1080p Screen' }; };

    const domainCardsHtml = worlds.map(function (w, idx) {
      const num = String(idx + 1).padStart(2, '0');
      const desc = DOMAIN_DESCRIPTIONS[w.world_id] || w.title;
      const viewsHtml = (w.views || []).map(function (v) {
        const pre = getPreset(v.view_id);
        return '<button type="button" class="va-domain-view-btn" data-launch-world="' + esc(w.world_id) + '" data-launch-view="' + esc(v.view_id) + '">' +
          '<span>' + esc(v.option_label) + '</span>' +
          '<span class="va-view-preset-tag">' + esc(pre.preset_label) + '</span></button>';
      }).join('');
      const firstView = (w.views && w.views[0]) ? w.views[0].view_id : '';
      return '<article class="va-domain-card">' +
        '<div class="va-domain-card-top"><span class="va-step-icon-tile">' + svgTileIcon(domainIconKind(w.world_id)) + '</span>' +
        '<span class="va-domain-slug">&gt; domain_' + num + '_</span></div>' +
        '<h3>' + esc(w.title) + '</h3>' +
        '<p class="va-domain-desc">' + esc(desc) + '</p>' +
        '<div class="va-domain-view-list">' + viewsHtml + '</div>' +
        '<div class="va-domain-launch"><button type="button" class="va-domain-launch-btn" data-launch-world="' + esc(w.world_id) + '" data-launch-view="' + esc(firstView) + '">Launch Domain ' + num + ' &rarr;</button></div>' +
        '</article>';
    }).join('');

    const installCmd = 'git clone https://github.com/FrankXLT/quiet-ui-skills.git && cd quiet-ui-skills && ./install.sh';
    root.innerHTML = '<div class="va-landing-wrap">' +
      '<section class="va-landing-hero" aria-label="Quiet UI Introduction">' +
      '<span class="va-landing-kicker">DETERMINISTIC DESIGN &amp; METROLOGY FOR AI AGENTS</span>' +
      '<h1 class="va-landing-h1">Interfaces Engineered to Be Read, Not Decorated</h1>' +
      '<p class="va-landing-sub">One zero-dependency design system and SVG/ECharts compiler suite that adapts engineering telemetry, clinical scopes, and technical briefs across screen, print, and mobile.</p>' +
      '<div class="va-landing-chips">' +
      '<button type="button" class="va-landing-chip" data-scroll-target="va-landing-pillars"><span class="va-chip-prompt">&gt;</span><span>quiet_ui_</span></button>' +
      '<button type="button" class="va-landing-chip" data-scroll-target="va-landing-pillars"><span class="va-chip-prompt">&gt;</span><span>quiet_evidence_</span></button>' +
      '<button type="button" class="va-landing-chip" data-scroll-target="va-landing-pillars"><span class="va-chip-prompt">&gt;</span><span>quiet_bridge_</span></button>' +
      '</div>' +
      '<div class="va-landing-chips">' +
      '<button type="button" class="va-landing-chip" data-open-examples="1"><span class="va-chip-prompt">&gt;</span><span>' + totalViews + '_live_examples_</span></button>' +
      '<button type="button" class="va-landing-chip" data-open-components="1"><span class="va-chip-prompt">&gt;</span><span>44_components_</span></button>' +
      '<button type="button" class="va-landing-chip" data-scroll-target="va-landing-pillars"><span class="va-chip-prompt">&gt;</span><span>portable_auditor_</span></button>' +
      '<button type="button" class="va-landing-chip" data-scroll-target="va-landing-pillars"><span class="va-chip-prompt">&gt;</span><span>60s_brand_kits_</span></button>' +
      '</div></section>' +

      '<section id="va-landing-morph-card" class="va-morph-card" aria-label="How the Showcase Works and Live Preview">' +
      '<div class="va-morph-steps">' +
      '<div class="va-morph-step"><span class="va-step-icon-tile">' + svgTileIcon('step') + '</span><div><h2>1. Step Across Mediums</h2><p>Use &lt; and &gt; in the portal bar to step across domains as views morph between 1080p screen, archival paper, 390px mobile, and dark cockpit.</p></div></div>' +
      '<div class="va-morph-step"><span class="va-step-icon-tile">' + svgTileIcon('proof') + '</span><div><h2>2. Inspect Calibrated Proof</h2><p>Every chart uses 1-2-5 ticks, knockout halos, and conserved corpus numbers. Click Why? on any view to read its plain-English design rationale.</p></div></div>' +
      '<div class="va-morph-step"><span class="va-step-icon-tile">' + svgTileIcon('rail') + '</span><div><h2>3. Test Live Shell Controls</h2><p>Collapse the inner app sidebar, isolate focused sections, switch themes or density from the rail footer, or drag portal handles.</p></div></div>' +
      '</div>' +
      '<div class="va-morph-stage-wrap">' +
      '<div class="va-morph-stage-hdr">' +
      '<div class="va-morph-stage-title"><span>LIVE MEDIUM MORPH PREVIEW</span><span>·</span><span id="va-morph-mode-label">1080p Screen · 1920×1080</span></div>' +
      '<div class="va-morph-stage-actions">' +
      '<span id="va-morph-status-pill" class="va-morph-status-pill" data-state="warn">CAUTION · MAP &lt; 75 mmHg</span>' +
      '<button type="button" id="va-morph-open-portal" class="va-landing-cta">Open in 1080p Portal &rarr;</button>' +
      '</div></div>' +
      '<div id="va-morph-canvas" class="va-morph-canvas" data-morph-mode="screen">' +
      '<div id="va-morph-svg-host" class="va-morph-plot-box">' + buildWaveformSvgHtml(75) + '</div>' +
      '<div><div class="va-morph-kpis">' +
      '<div class="va-morph-kpi"><span>Mean MAP</span><strong>63.5 mmHg</strong></div>' +
      '<div class="va-morph-kpi"><span>Peak Systolic</span><strong>94.0 mmHg</strong></div>' +
      '<div class="va-morph-kpi"><span>Ceiling Margin</span><strong id="va-morph-margin-val">-11.5 mmHg</strong></div>' +
      '</div><p id="va-morph-mode-note" class="va-morph-summary">' + esc(MORPH_MODES.screen.note) + '</p></div></div>' +
      '<div class="va-morph-controls">' +
      '<div class="va-morph-mode-group" role="group" aria-label="Preview Medium">' +
      '<button type="button" class="va-morph-mode-btn" data-morph-btn="screen" aria-pressed="true">1. 1080p Screen</button>' +
      '<button type="button" class="va-morph-mode-btn" data-morph-btn="paper" aria-pressed="false">2. Paper Sheet</button>' +
      '<button type="button" class="va-morph-mode-btn" data-morph-btn="mobile" aria-pressed="false">3. 390px Mobile</button>' +
      '<button type="button" class="va-morph-mode-btn" data-morph-btn="dark" aria-pressed="false">4. Dark Cockpit</button>' +
      '<button type="button" class="va-morph-mode-btn" data-morph-btn="brief" aria-pressed="false">5. Executive Brief</button>' +
      '</div>' +
      '<div class="va-morph-slider-wrap"><label for="va-morph-threshold">Alert Ceiling: <strong id="va-morph-threshold-val" class="va-nums">75 mmHg</strong></label>' +
      '<input type="range" id="va-morph-threshold" min="55" max="95" step="1" value="75" aria-valuetext="75 mmHg"></div>' +
      '</div></div></section>' +

      '<section id="va-landing-domains" aria-label="Explore Domains and Portal Views">' +
      '<div class="va-landing-sec-hdr"><h2>Explore ' + worlds.length + ' Domains &amp; ' + totalViews + ' Live Views</h2>' +
      '<span>Click any example to open its curated screen, paper, mobile, or cockpit preset.</span></div>' +
      '<div class="va-domain-grid">' + domainCardsHtml + '</div></section>' +

      '<section id="va-landing-pillars" class="va-pillars-card" aria-label="Three Pillars and Quick Install">' +
      '<div class="va-landing-sec-hdr"><h2>Three Orthogonal Pillars &amp; Quick Install</h2><span>Zero-dependency Python 3.10+ stdlib compilers &amp; portable auditor</span></div>' +
      '<div class="va-pillars-grid">' +
      '<div class="va-pillar-col"><h3>quiet-ui (7 Mediums)</h3><p>Screen, archival print, stateful workbenches, POI terminals, wall kiosks, and optical HUDs with persistent <code>.quiet-ui.md</code> contracts and <code>audit_quiet_html.py</code>.</p></div>' +
      '<div class="va-pillar-col"><h3>quiet-evidence (6 Modalities)</h3><p>Deterministic SVG/ECharts compilers for 1-2-5 plots, waveforms, bitfields, tables, and schematics across 44 interactive Component Library specimens.</p></div>' +
      '<div class="va-pillar-col"><h3>quiet-bridge (7 Audience Lenses)</h3><p>Executive, peer engineering, operator, and learner projection rules enforcing plain-English clarity and end-to-end numerical conservation.</p></div>' +
      '</div>' +
      '<div class="va-install-bar">' +
      '<div class="va-install-code-row"><code>' + esc(installCmd) + '</code>' +
      '<button type="button" id="va-landing-copy-install" class="va-studio-btn">Copy</button>' +
      '<span id="va-landing-copy-status" class="va-copy-status" role="status"></span></div>' +
      '<button type="button" id="va-landing-open-components" class="va-landing-cta">Browse All 44 Components &rarr;</button>' +
      '</div></section></div>';

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
        statusPill.textContent = warn ? ('CAUTION · MAP < ' + th + ' mmHg') : ('Nominal · MAP >= ' + th + ' mmHg');
      }
    }
    if (slider) {
      syncMorphSlider();
      slider.addEventListener('input', syncMorphSlider);
    }

    root.querySelectorAll('[data-morph-btn]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        const mode = btn.getAttribute('data-morph-btn') || 'screen';
        const cfg = MORPH_MODES[mode] || MORPH_MODES.screen;
        if (canvas) canvas.setAttribute('data-morph-mode', mode);
        if (modeLbl) modeLbl.textContent = cfg.label;
        if (modeNote) modeNote.textContent = cfg.note;
        root.querySelectorAll('[data-morph-btn]').forEach(function (b) {
          b.setAttribute('aria-pressed', b === btn ? 'true' : 'false');
        });
      });
    });

    root.querySelectorAll('[data-launch-view]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        if (portalApi && portalApi.openExamples) {
          portalApi.openExamples(btn.getAttribute('data-launch-world'), btn.getAttribute('data-launch-view'));
        }
      });
    });
    root.querySelectorAll('[data-open-examples]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        if (portalApi && portalApi.openExamples) portalApi.openExamples();
      });
    });
    root.querySelectorAll('[data-open-components]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        if (portalApi && portalApi.openComponents) portalApi.openComponents();
      });
    });
    const openPortalBtn = document.getElementById('va-morph-open-portal');
    if (openPortalBtn) {
      openPortalBtn.addEventListener('click', function () {
        if (portalApi && portalApi.openExamples) portalApi.openExamples('01-clinical-icu-and-trials', 'v01-icu-bedside-terminal');
      });
    }
    const openCompBtn = document.getElementById('va-landing-open-components');
    if (openCompBtn) {
      openCompBtn.addEventListener('click', function () {
        if (portalApi && portalApi.openComponents) portalApi.openComponents();
      });
    }
    root.querySelectorAll('[data-scroll-target]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        const tgt = document.getElementById(btn.getAttribute('data-scroll-target') || '');
        if (tgt && tgt.scrollIntoView) tgt.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    });
    const copyBtn = document.getElementById('va-landing-copy-install');
    const copyStatus = document.getElementById('va-landing-copy-status');
    if (copyBtn) {
      copyBtn.addEventListener('click', function () {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(installCmd).then(function () {
            if (copyStatus) copyStatus.textContent = 'Install command copied';
          }, function () {
            if (copyStatus) copyStatus.textContent = 'Copy unavailable';
          });
        }
      });
    }
  }

  window.QuietStudioLandingV9 = {
    renderLanding: renderLanding,
  };
})(window, document);
