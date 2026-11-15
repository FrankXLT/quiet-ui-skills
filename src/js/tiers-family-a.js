/* SPDX-License-Identifier: MIT */
/**
 * Quiet UI v8.2 — Family A Tier Event Controllers (Doc-1, Doc-2, Doc-3, Doc-4b, Doc-4a)
 */
(function(window) {
  'use strict';

  function activateSiblingBtn(btn) {
    if (btn && btn.parentElement) {
      btn.parentElement.querySelectorAll('button').forEach(function(b) {
        b.classList.remove('active', 'is-active');
      });
      btn.classList.add('active', 'is-active');
    }
  }

  // --- Global Shell Drawer Handlers (<1100px & N4 Mobile Dock) ---
  window.openShellDrawer = function() {
    const d = document.getElementById('va-shell-drawer');
    if (d && typeof d.showModal === 'function' && !d.open) d.showModal();
  };

  window.closeShellDrawer = function() {
    const d = document.getElementById('va-shell-drawer');
    if (d && typeof d.close === 'function' && d.open) d.close();
  };

  // --- Doc-1: Scientific Monograph Sidenote Hover & Mobile TOC ---
  window.highlightDoc1Sidenote = function(id, isHighlight) {
    const el = document.getElementById(id);
    if (el) {
      el.classList.toggle('is-highlighted', !!isHighlight);
    }
  };

  window.toggleLeftRailCollapse = function() {
    const layout = document.querySelector('.doc1-layout');
    if (layout) {
      layout.classList.toggle('is-collapsed');
    }
  };

  // --- Doc-2 & Common Figures: Diagram Source & Zoom ---
  window.toggleMermaidSource = function(btn) {
    const card = btn ? btn.closest('.va-figure-card') : null;
    const code = card ? card.querySelector('.va-mermaid-code') : document.querySelector('.va-mermaid-code');
    if (!code) return;
    const willShow = code.hasAttribute('hidden') || window.getComputedStyle(code).display === 'none';
    if (willShow) {
      code.removeAttribute('hidden');
      code.style.display = 'block';
    } else {
      code.setAttribute('hidden', '');
      code.style.display = 'none';
    }
    if (btn) btn.setAttribute('aria-expanded', willShow ? 'true' : 'false');
  };

  window.openFigureZoom = function(btn) {
    const card = btn ? btn.closest('.va-figure-card') : null;
    const split = card ? card.querySelector('.va-fig-split-grid') : null;
    const target = split || (card ? card.querySelector('svg') : null);
    const dlg = document.getElementById('va-fig-zoom-dialog');
    if (!dlg || !target) return;
    const container = dlg.querySelector('.va-fig-zoom-content') || dlg;
    container.innerHTML = '<div style="max-height:78vh;overflow:auto;padding:0.75rem;">' + target.outerHTML + '</div>' +
      '<div style="text-align:right;margin-top:0.5rem;"><button type="button" class="va-btn-ghost" onclick="this.closest(\'dialog\').close()">Close</button></div>';
    if (typeof dlg.showModal === 'function') dlg.showModal();
  };

  // --- Doc-3: Normative Clause Filtering ---
  window.filterRfcClauses = function(type, btn) {
    activateSiblingBtn(btn);
    const target = (type || 'ALL').toUpperCase();
    document.querySelectorAll('#rfc-clause-table tbody tr[data-clause]').forEach(function(tr) {
      const c = (tr.getAttribute('data-clause') || '').toUpperCase();
      tr.style.display = (target === 'ALL' || c === target) ? '' : 'none';
    });
  };

  // --- Doc-4B: Situation Decision Table Modal ---
  window.toggleDoc4BTableModal = function() {
    const dlg = document.getElementById('doc4b-table-modal');
    if (dlg) {
      if (dlg.open) dlg.close();
      else if (typeof dlg.showModal === 'function') dlg.showModal();
    }
  };

  // --- Doc-4A: Split-Pane Runbook Step & Console Controller ---
  const DOC4A_SNIPPETS = {
    CLI: [
      '# Step 01: Verify 1064 nm Uplink Beacon Lock\ndsoc-groundctl beacon status --facility table-mountain\ndsoc-groundctl beacon lock-verify --threshold-urad 0.50\n[OK] Uplink beacon centroid locked: 0.38 urad RMS jitter',
      '# Step 02: Calibrate Relativistic Point-Ahead Angle\ndsoc-groundctl ephemeris sync --range-au 2.6 --fsm-loop closed\n[OK] Point-ahead vector +33.4 urad applied to Fine Steering Mirror',
      '# Step 03: Align Beam Divergence & Transmit Power\ndsoc-groundctl tx power-set --watts 1250 --divergence-urad 12.5\n[OK] Laser downlink channel stabilized: 1550.0 nm at 1.25 kW peak',
      '# Step 04: Engage SCPPM M=64 Iterative Decoder\ndsoc-fpga configure --ppm-order 64 --code-rate 1/2 --slot-ps 500\n[OK] BCJR soft decoder locked at 10 iterations (ASM sync verified)',
      '# Step 05: Validate Science Packet Frame Stream\ndsoc-groundctl stream dump --apid 0x0428 --frames 5000\n[OK] 5,000 CCSDS Space Packets received at 267.0 Mbps (FER < 1e-6)',
      '# Step 06: Safing & Handover Disengage\ndsoc-groundctl handover disengage --flywheel-duration 30s\n[OK] Ground collector stowed; telemetry logs flushed to NTRS archive'
    ],
    Python: [
      'from dsoc_sdk import GroundTerminal\ntmo = GroundTerminal("table-mountain")\nassert tmo.verify_beacon_lock(max_urad=0.50).rms_urad <= 0.50',
      'from dsoc_sdk import EphemerisSolver\noffset = EphemerisSolver(range_au=2.6).compute_point_ahead()\ntmo.apply_fsm_vector(offset)',
      'from dsoc_sdk import OpticalDownlink\ntx = OpticalDownlink(wavelength_nm=1550, power_watts=1250)\ntx.align_divergence(urad=12.5)',
      'from dsoc_sdk import ScppmDecoder\ndec = ScppmDecoder(bar0=0xF000_0000)\ndec.configure(ppm_order=64, slot_width_ps=500, iterations=10)',
      'from dsoc_sdk import FrameExtractor\nstream = FrameExtractor(apid=0x0428)\nassert stream.validate_fer(threshold=1e-6)',
      'from dsoc_sdk import TerminalSafing\nsafe = TerminalSafing()\nsafe.archive_telemetry_and_stow()'
    ],
    YAML: [
      'step: 1\nfacility: table-mountain-observatory\nbeacon_wavelength_nm: 1064\nmax_centroid_jitter_urad: 0.50',
      'step: 2\ntrajectory_range_au: 2.6\nfsm_closed_loop: true\npoint_ahead_compensation: relativistic_2way',
      'step: 3\ntx_power_watts: 1250\nwavelength_nm: 1550\nbeam_divergence_urad: 12.5',
      'step: 4\ndecoder: ccsds_142_0_b_1_scppm\nmodulation_order_m: 64\nslot_width_ps: 500',
      'step: 5\nstream_apid: 0x0428\nthroughput_target_mbps: 267.0\nmax_frame_error_rate: 1.0e-6',
      'step: 6\nhandover_mode: spatial_diversity\nholdover_flywheel_sec: 30\npost_pass_status: nominal_safed'
    ],
    FPGACSR: [
      'CSR_BEACON_STAT [0x0010]: 0x0000_0003  // Beacon locked, loop closed\nCSR_CENTROID_JIT [0x0014]: 0x0000_0026  // Jitter 0.38 urad',
      'CSR_FSM_X_VEC   [0x0020]: 0x0000_021C  // +33.4 urad az\nCSR_FSM_Y_VEC   [0x0024]: 0x0000_004F  // +7.9 urad el',
      'CSR_TX_CTRL     [0x0030]: 0x0000_04E2  // Power 1250 mW enabled\nCSR_DIVERGENCE  [0x0034]: 0x0000_007D  // 12.5 urad aperture',
      'CSR_DECODER_CFG [0x0040]: 0x0000_0040  // M=64 SCPPM active\nCSR_ITER_COUNT  [0x0044]: 0x0000_000A  // 10 BCJR iterations',
      'CSR_FRAME_COUNT [0x0050]: 0x0000_1388  // 5000 frames validated\nCSR_FER_METRIC  [0x0054]: 0x0000_0000  // Zero frame aborts',
      'CSR_SAFE_STATUS [0x0060]: 0x0000_0001  // Terminal safely stowed'
    ]
  };

  let doc4aStep = 0;
  let doc4aLang = 'CLI';

  function renderDoc4aCode() {
    const pre = document.getElementById('doc4a-code-pre');
    const sync = document.getElementById('doc4a-sync-status');
    const list = DOC4A_SNIPPETS[doc4aLang] || DOC4A_SNIPPETS.CLI;
    const snippet = list[doc4aStep] || list[0];
    if (pre) pre.innerHTML = '<code>' + snippet + '</code>';
    if (sync) sync.innerHTML = '<i class="fa-solid fa-circle-check" style="color:var(--status-ok, #16a34a);"></i> SYNCED: STEP 0' + (doc4aStep + 1) + ' // ' + doc4aLang;
  }

  window.selectRunbookStep = function(idx) {
    doc4aStep = Math.max(0, Math.min(5, idx));
    document.querySelectorAll('.doc4a-step').forEach(function(s, i) {
      s.classList.toggle('is-active', i === doc4aStep);
    });
    document.querySelectorAll('.va-seq-step-band').forEach(function(b, i) {
      b.classList.toggle('is-active', i === doc4aStep);
    });
    renderDoc4aCode();
  };

  window.selectRunbookLang = function(lang, btn) {
    doc4aLang = lang;
    activateSiblingBtn(btn);
    renderDoc4aCode();
  };

  window.copyDoc4aSnippet = function(btn) {
    const list = DOC4A_SNIPPETS[doc4aLang] || DOC4A_SNIPPETS.CLI;
    const snippet = list[doc4aStep] || list[0];
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(snippet).then(function() {
        if (btn) {
          const old = btn.innerHTML;
          btn.innerHTML = '<i class="fa-solid fa-check"></i> Copied';
          setTimeout(function() { btn.innerHTML = old; }, 1800);
        }
      });
    }
  };

})(typeof window !== 'undefined' ? window : this);
