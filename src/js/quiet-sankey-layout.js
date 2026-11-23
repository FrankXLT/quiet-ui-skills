// SPDX-License-Identifier: Apache-2.0
(function (root) {
  'use strict';

  function nodeIdOf(n, fallbackIdx) {
    if (!n || typeof n !== 'object') return String(fallbackIdx);
    if (n.id != null) return String(n.id);
    if (n.name != null) return String(n.name);
    return String(fallbackIdx);
  }

  function nodeColOf(n) {
    var raw = n && (n.col != null ? n.col : (n.column != null ? n.column : (n.stage != null ? n.stage : n.depth)));
    var num = Number(raw);
    return Number.isFinite(num) ? num : 0;
  }

  function nodeCountOf(n) {
    var raw = n && (n.count != null ? n.count : (n.value != null ? n.value : 0));
    var num = Number(raw);
    return Number.isFinite(num) ? num : 0;
  }

  /**
   * Order multi-column Sankey intermediate columns by (primaryTargetRank, -count)
   * right-to-left to minimize diagonal ribbon crossings over labels.
   */
  function sortColumnsTopologically(nodes, edges, opts) {
    var srcNodes = Array.isArray(nodes) ? nodes : [], srcEdges = Array.isArray(edges) ? edges : [], cfg = opts || {};
    var byCol = Object.create(null), nodeMeta = Object.create(null), outEdges = Object.create(null);
    srcNodes.forEach(function (n, idx) {
      var id = nodeIdOf(n, idx), col = nodeColOf(n), cnt = nodeCountOf(n);
      var entry = { raw: n, id: id, col: col, count: cnt, origIdx: idx };
      nodeMeta[id] = entry;
      if (!byCol[col]) byCol[col] = [];
      byCol[col].push(entry);
    });
    srcEdges.forEach(function (e) {
      if (!e || e.source == null || e.target == null) return;
      var s = String(e.source), t = String(e.target), w = Number(e.count != null ? e.count : (e.value != null ? e.value : 0));
      if (!outEdges[s]) outEdges[s] = [];
      outEdges[s].push({ target: t, weight: Number.isFinite(w) ? w : 0 });
    });

    var colKeys = Object.keys(byCol).map(Number).sort(function (a, b) { return a - b; });
    var rankById = Object.create(null), orderedCols = Object.create(null);
    if (!colKeys.length) return { nodes: [], columns: orderedCols, rankById: rankById };

    var lastCol = colKeys[colKeys.length - 1];
    var termList = byCol[lastCol].slice();
    if (cfg.preserveTerminalOrder !== true) {
      termList.sort(function (a, b) {
        var ra = a.raw && a.raw.rank != null && a.raw.rank !== '' && Number.isFinite(Number(a.raw.rank)) ? Number(a.raw.rank) : Infinity;
        var rb = b.raw && b.raw.rank != null && b.raw.rank !== '' && Number.isFinite(Number(b.raw.rank)) ? Number(b.raw.rank) : Infinity;
        if (ra !== rb) return ra - rb;
        if (b.count !== a.count) return b.count - a.count;
        return a.origIdx - b.origIdx;
      });
    }
    orderedCols[lastCol] = termList.map(function (e, i) { rankById[e.id] = i; return e.raw; });

    var startColIdx = cfg.sortSource ? 0 : 1;
    if (colKeys.length > 1 && startColIdx === 1) {
      orderedCols[colKeys[0]] = byCol[colKeys[0]].map(function (e, i) { rankById[e.id] = i; return e.raw; });
    }
    for (var ci = colKeys.length - 2; ci >= startColIdx; ci -= 1) {
      var ck = colKeys[ci], list = byCol[ck].slice();
      list.forEach(function (entry) {
        var outs = outEdges[entry.id] || [], bestRank = Infinity, bestWeight = -1;
        outs.forEach(function (edge) {
          var tr = Object.prototype.hasOwnProperty.call(rankById, edge.target) ? rankById[edge.target] : Infinity;
          if (!Number.isFinite(tr)) return;
          if (edge.weight > bestWeight || (edge.weight === bestWeight && tr < bestRank)) {
            bestWeight = edge.weight;
            bestRank = tr;
          }
        });
        entry.primaryTargetRank = bestRank;
      });
      list.sort(function (a, b) {
        if (a.primaryTargetRank !== b.primaryTargetRank) return a.primaryTargetRank - b.primaryTargetRank;
        if (b.count !== a.count) return b.count - a.count;
        return a.origIdx - b.origIdx;
      });
      orderedCols[ck] = list.map(function (e, i) { rankById[e.id] = i; return e.raw; });
    }

    var orderedNodes = [];
    colKeys.forEach(function (ck) { Array.prototype.push.apply(orderedNodes, orderedCols[ck]); });
    return { nodes: orderedNodes, columns: orderedCols, rankById: rankById };
  }

  /** Compute proportional vertical highlight bounds for a partially matched Sankey node bar. */
  function computeActiveSlice(nodeY, nodeH, nodeCount, matchedCount, ribbonOffsetY) {
    var y = Number(nodeY) || 0, h = Number(nodeH) || 0, tot = Number(nodeCount) || 0, m = Number(matchedCount) || 0;
    if (!Number.isFinite(h) || h <= 0 || !Number.isFinite(tot) || tot <= 0 || !Number.isFinite(m) || m <= 0) {
      return { isFullBar: false, sliceY: y, sliceH: 0 };
    }
    var ratio = Math.min(1, Math.max(0, m / tot));
    if (ratio >= 0.9999) return { isFullBar: true, sliceY: y, sliceH: h };
    var sliceH = Math.min(h, Math.max(1.5, h * ratio));
    var off = Number.isFinite(Number(ribbonOffsetY)) ? Math.max(0, Number(ribbonOffsetY)) : 0;
    var sliceY = y + Math.min(off, Math.max(0, h - sliceH));
    return { isFullBar: false, sliceY: Math.round(sliceY * 100) / 100, sliceH: Math.round(sliceH * 100) / 100 };
  }

  /** Deduplicate redundant 'brand · brand@' stems into clean single addresses. */
  function dedupeStemEmail(stem, localPart) {
    var s = String(stem || '').trim(), lp = String(localPart || '').trim();
    if (!s) return lp;
    if (!lp) return s;
    var lpHead = lp.split('@')[0].trim();
    var norm = function (v) { return String(v || '').toLowerCase().replace(/[^a-z0-9]/g, ''); };
    var ns = norm(s), nh = norm(lpHead);
    if (s.toLowerCase() === lp.toLowerCase() || s.toLowerCase() === lpHead.toLowerCase() || (ns.length >= 2 && ns === nh)) {
      return lp.indexOf('@') >= 0 ? lp : s;
    }
    return s + ' · ' + lp;
  }

  var api = {
    sortColumnsTopologically: sortColumnsTopologically,
    computeActiveSlice: computeActiveSlice,
    dedupeStemEmail: dedupeStemEmail,
  };
  root.QuietSankeyLayout = api;
  if (typeof module === 'object' && module.exports) module.exports = api;
}(typeof window !== 'undefined' ? window : globalThis));
