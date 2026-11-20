# SPDX-License-Identifier: Apache-2.0
"""Multi-Ecosystem Config Snippet & 5-Tab Drawer Generator for Quiet Evidence."""

from __future__ import annotations

import json
import re
from typing import Any

from .tokens_and_scales import esc


def _gantt_snippets(payload: dict[str, Any]) -> tuple[str, str, str, str]:
    title = str(payload.get("title") or "Project Critical Path")
    x_lbl = str((payload.get("x") or {}).get("name") or "Schedule Day, t / d")
    tasks = payload.get("tasks") or []
    t_names = [t.get("label", "Task") for t in tasks]
    t_starts = [t.get("start", 0) for t in tasks]
    t_durs = [max(0.5, float(t.get("end", 1)) - float(t.get("start", 0))) for t in tasks]
    plotly = (
        f"fig = go.Figure(go.Bar(y={t_names[:4]!r}, x={t_durs[:4]!r}, base={t_starts[:4]!r}, orientation='h'))\n"
        f"fig.update_layout(template='plotly_white', xaxis_title='{x_lbl}', yaxis=dict(autorange='reversed'))"
    )
    mpl = (
        f"ax.barh(tasks, durations, left=starts, height=0.55)\n"
        f"ax.invert_yaxis(); ax.spines[['top', 'right']].set_visible(False)\n"
        f"ax.set(xlabel='{x_lbl}', title='{title}')"
    )
    bokeh = (
        f"p = figure(y_range=list(reversed(tasks)), x_axis_label='{x_lbl}', toolbar_location=None)\n"
        f"p.hbar(y='label', left='start', right='end', height=0.5, source=src)"
    )
    m_lines = ["gantt", f"    title {title}", "    dateFormat X", "    axisFormat %s"]
    cur_phase = ""
    for t in tasks[:6]:
        ph = str(t.get("phase") or "Execution")
        if ph != cur_phase:
            m_lines.append(f"    section {ph}")
            cur_phase = ph
        tag = "crit, " if t.get("critical") else ("milestone, " if t.get("milestone") else "")
        s_val = int(round(float(t.get("start", 0))))
        e_val = int(round(float(t.get("end", s_val + 1))))
        m_lines.append(f"    {t.get('label', 'Task')} :{tag}{t.get('id', 't')}, {s_val}, {max(s_val + 1, e_val)}")
    return plotly, mpl, bokeh, "\n".join(m_lines)


def _heatmap_snippets(payload: dict[str, Any]) -> tuple[str, str, str, str]:
    title = str(payload.get("title") or "2D Matrix Heatmap")
    x_cats = payload.get("xCategories") or []
    y_cats = payload.get("yCategories") or []
    unit = str(payload.get("unit") or "%")
    plotly = (
        f"fig = go.Figure(go.Heatmap(z=matrix, x={x_cats[:4]!r}, y={y_cats[:4]!r}, colorscale='Blues'))\n"
        f"fig.update_layout(template='plotly_white', title='{title} ({unit})')"
    )
    mpl = (
        f"im = ax.imshow(matrix, aspect='auto', cmap='cividis')\n"
        f"fig.colorbar(im, ax=ax, label='{unit}')\nax.set_title('{title}')"
    )
    bokeh = (
        f"p = figure(x_range=x_cats, y_range=list(reversed(y_cats)), toolbar_location=None)\n"
        f"p.rect(x='x', y='y', width=1, height=1, source=src, fill_color=linear_cmap('val', 'Cividis256', low, high))"
    )
    mermaid = f"xychart-beta\n    title \"{title} ({unit})\"\n    x-axis {json.dumps(x_cats[:6])}\n    bar {[c[2] for c in (payload.get('cells') or [])[:6]]}"
    return plotly, mpl, bokeh, mermaid


def _sankey_snippets(payload: dict[str, Any]) -> tuple[str, str, str, str]:
    title = str(payload.get("title") or "Flow Sankey")
    unit = str(payload.get("unit") or "")
    links = payload.get("links") or []
    plotly = (
        "fig = go.Figure(go.Sankey(node=dict(label=[n['name'] for n in nodes]),\n"
        f"    link=dict(source=src_idx, target=dst_idx, value=[l['value'] for l in links])))\n"
        f"fig.update_layout(template='plotly_white', title='{title}')"
    )
    mpl = (
        "from matplotlib.sankey import Sankey\n"
        "Sankey(ax=ax, unit=' " + unit + "', flows=[l['value'] for l in links]).finish()\n"
        f"ax.set_title('{title}')"
    )
    bokeh = (
        "p = figure(title='" + title + "', toolbar_location=None)\n"
        "p.bezier(x0='x0', y0='y0', x1='x1', y1='y1', cx0='mx', cy0='y0', cx1='mx', cy1='y1', source=src)"
    )
    m_lines = ["flowchart LR"]
    for lk in links[:6]:
        m_lines.append(f"    {lk['source'].replace(' ', '_')} -->|\"{lk['value']} {unit}\"| {lk['target'].replace(' ', '_')}")
    return plotly, mpl, bokeh, "\n".join(m_lines)


def _strip_chart_snippets(payload: dict[str, Any]) -> tuple[str, str, str, str]:
    title = str(payload.get("title") or "Telemetry Strip Chart")
    x_lbl = str((payload.get("x") or {}).get("name") or "Elapsed Time, t / s")
    tracks = payload.get("tracks") or []
    plotly = (
        f"fig = make_subplots(rows={max(1, len(tracks))}, cols=1, shared_xaxes=True)\n"
        "for i, tr in enumerate(tracks, 1):\n"
        "    fig.add_scatter(x=t, y=tr['y'], row=i, col=1, name=tr['name'])\n"
        f"fig.update_layout(template='plotly_white', xaxis_title='{x_lbl}')"
    )
    mpl = (
        f"fig, axes = plt.subplots({max(1, len(tracks))}, 1, sharex=True)\n"
        "for ax, tr in zip(axes, tracks):\n"
        "    ax.axhspan(*tr['nominalBand'], color='#ECFDF5', alpha=0.6); ax.plot(t, tr['y'])\n"
        f"axes[-1].set_xlabel('{x_lbl}'); fig.suptitle('{title}')"
    )
    bokeh = (
        "figs = [figure(height=120, x_range=x_rng, y_axis_label=tr['unit']) for tr in tracks]\n"
        "show(column(*figs))"
    )
    first_pts = ((tracks[0].get("data") if tracks else None) or [])[::20][:6]
    vals = [round(p[1], 2) for p in first_pts]
    mermaid = f"xychart-beta\n    title \"{title}\"\n    x-axis {[p[0] for p in first_pts]}\n    line {vals}"
    return plotly, mpl, bokeh, mermaid


def eco_snippets(payload: dict[str, Any]) -> list[tuple[str, str, str]]:
    """Generate copyable 5-ecosystem snippets (ECharts, Plotly, Matplotlib, Bokeh, Mermaid)."""
    kind = payload["kind"]
    if kind == "sankey":
        echarts_cfg = json.dumps({"renderer": "svg", "kind": "sankey", "nodes": payload.get("nodes", [])[:6], "links": payload.get("links", [])[:6]}, indent=2, ensure_ascii=False)
        plotly, mpl, bokeh, mermaid = _sankey_snippets(payload)
        return [("echarts", "Apache ECharts", echarts_cfg), ("plotly", "Plotly (Python)", plotly), ("matplotlib", "Matplotlib", mpl), ("bokeh", "Bokeh", bokeh), ("mermaid", "Mermaid", mermaid)]
    if kind == "strip_chart":
        echarts_cfg = json.dumps({"renderer": "svg", "kind": "strip_chart", "xAxis": payload.get("x"), "dataZoom": [{"type": "slider"}], "tracks": [{"name": t["name"], "unit": t["unit"], "nominalBand": t.get("nominalBand")} for t in payload.get("tracks", [])]}, indent=2, ensure_ascii=False)
        plotly, mpl, bokeh, mermaid = _strip_chart_snippets(payload)
        return [("echarts", "Apache ECharts", echarts_cfg), ("plotly", "Plotly (Python)", plotly), ("matplotlib", "Matplotlib", mpl), ("bokeh", "Bokeh", bokeh), ("mermaid", "Mermaid", mermaid)]
    x_lbl = str((payload.get("x") or {}).get("name") or "Category")
    y_lbl = str((payload.get("y") or {}).get("name") or payload.get("yName") or "Value")
    echarts_obj: dict[str, Any] = {
        "renderer": "svg",
        "kind": kind,
        "xAxis": {"name": x_lbl, "type": "log" if (payload.get("x") or {}).get("log") else ("category" if kind in {"waterfall", "stacked_bar", "heatmap"} else "value")},
        "yAxis": {"name": y_lbl, "type": "log" if (payload.get("y") or {}).get("log") else ("category" if kind in {"gantt", "heatmap", "forest"} else "value")},
    }
    if (payload.get("y") or {}).get("min") is not None:
        echarts_obj["yAxis"]["min"] = payload["y"]["min"]
        echarts_obj["yAxis"]["max"] = payload["y"]["max"]
    if kind == "heatmap":
        echarts_obj["visualMap"] = {"min": payload.get("min", 0), "max": payload.get("max", 100)}
    elif kind == "gantt":
        echarts_obj["todayMarker"] = payload.get("todayMarker")
    else:
        echarts_obj["markLine"] = [{"yAxis": e["value"], "name": e["label"]} for e in payload.get("envelopes", []) if "value" in e]
    echarts_cfg = json.dumps(echarts_obj, indent=2, ensure_ascii=False)

    if kind == "gantt":
        plotly, mpl, bokeh, mermaid = _gantt_snippets(payload)
    elif kind == "heatmap":
        plotly, mpl, bokeh, mermaid = _heatmap_snippets(payload)
    elif kind == "stacked_bar":
        plotly = f"for s in stack_series:\n    fig.add_bar(x=hours, y=s['data'], name=s['name'])\nfig.update_layout(barmode='relative', template='plotly_white', yaxis_title='{y_lbl}')"
        mpl = f"ax.bar(hours, solar, label='Solar'); ax.bar(hours, export, label='Export')\nax.spines[['top', 'right']].set_visible(False)\nax.set(xlabel='{x_lbl}', ylabel='{y_lbl}')"
        bokeh = f"p = figure(x_range=hours, y_axis_label='{y_lbl}', toolbar_location=None)\np.vbar_stack(['solar', 'grid', 'batt'], x='hour', width=0.7, source=src)"
        mermaid = f"xychart-beta\n    title \"{payload.get('title', 'Energy')}\"\n    x-axis [\"00:00\", \"06:00\", \"12:00\", \"14:00\", \"18:00\", \"23:00\"]\n    y-axis \"{y_lbl}\" {payload['y']['min']} --> {payload['y']['max']}\n    bar [0, 0.28, 4.94, 5.10, 1.12, 0]"
    elif kind == "dumbbell":
        plotly = f"fig.add_trace(go.Scatter(x=cats, y=before, mode='markers', name='Before'))\nfig.add_trace(go.Scatter(x=cats, y=after, mode='markers', name='After'))\nfig.update_layout(template='plotly_white', yaxis_title='{y_lbl}')"
        mpl = f"ax.vlines(cats, after, before, color='gray'); ax.scatter(cats, before, label='Before'); ax.scatter(cats, after, label='After')\nax.spines[['top', 'right']].set_visible(False); ax.set_ylabel('{y_lbl}')"
        bokeh = f"p = figure(x_range=cats, y_axis_label='{y_lbl}', toolbar_location=None)\np.segment(x0='cat', y0='before', x1='cat', y1='after', source=src)"
        mermaid = f"xychart-beta\n    title \"{payload.get('title', 'Dumbbell')}\"\n    y-axis \"{y_lbl}\"\n    bar [10, 20, 30]"
    elif kind == "forest":
        plotly = f"fig.add_trace(go.Scatter(x=est, y=subgroups, mode='markers', error_x=dict(type='data', array=hi_err, arrayminus=lo_err)))\nfig.add_vline(x={payload.get('nullValue', 1.0)}, line_dash='dash')"
        mpl = f"ax.errorbar(est, y_pos, xerr=[lo_err, hi_err], fmt='s', capsize=3); ax.axvline({payload.get('nullValue', 1.0)}, ls='--')\nax.spines[['top', 'right']].set_visible(False); ax.set_xlabel('{x_lbl}')"
        bokeh = f"p = figure(y_range=subgroups, x_axis_label='{x_lbl}', toolbar_location=None)\np.square(x='est', y='label', size=8, source=src)"
        mermaid = f"xychart-beta\n    title \"{payload.get('title', 'Forest CI')}\"\n    y-axis \"{x_lbl}\"\n    line [0.74, 0.79, 0.68, 0.71]"
    else:
        plotly = f"fig.add_trace(go.Scatter(x=x, y=y, mode='markers+lines', error_y=dict(type='data', array=u_y)))\nfig.update_layout(template='plotly_white', xaxis_title='{x_lbl}', yaxis_title='{y_lbl}')"
        mpl = f"ax.errorbar(x, y, yerr=u_y, fmt='o-', capsize=3, elinewidth=1.2)\nax.spines[['top', 'right']].set_visible(False)\nax.set(xlabel='{x_lbl}', ylabel='{y_lbl}')"
        bokeh = f"p = figure(x_axis_label='{x_lbl}', y_axis_label='{y_lbl}', toolbar_location=None)\np.line(x, y, line_width=2); p.add_layout(Whisker(base='x', upper='hi', lower='lo', source=src))"
        mermaid = f"xychart-beta\n    title \"{payload.get('title', 'Plot')}\"\n    y-axis \"{y_lbl}\"\n    line [0, 25, 50, 75, 100]"

    return [
        ("echarts", "Apache ECharts", echarts_cfg),
        ("plotly", "Plotly (Python)", plotly),
        ("matplotlib", "Matplotlib", mpl),
        ("bokeh", "Bokeh", bokeh),
        ("mermaid", "Mermaid", mermaid),
    ]


def render_ecosystem_drawer_from_payload(spec: dict[str, Any], payload: dict[str, Any] | None) -> str:
    """Render full-width 5-tab ecosystem code viewer with Copy Snippet button."""
    if payload is None:
        return ""
    slug = re.sub(r"[^a-z0-9]+", "-", str(spec.get("id") or "plot").lower()).strip("-") or "plot"
    uid = f"qe-eco-{slug}"
    tabs: list[str] = []
    panels: list[str] = []
    for idx, (key, label, code) in enumerate(eco_snippets(payload)):
        sel = "true" if idx == 0 else "false"
        t_idx = "0" if idx == 0 else "-1"
        hid = "" if idx == 0 else ' hidden="until-found"'
        tid, pid = f"{uid}-tab-{key}", f"{uid}-panel-{key}"
        tabs.append(
            f'<button type="button" class="qe-eco-tab" role="tab" id="{tid}" aria-controls="{pid}" '
            f'aria-selected="{sel}" tabindex="{t_idx}">{esc(label)}</button>'
        )
        panels.append(
            f'<div class="qe-eco-panel" role="tabpanel" id="{pid}" aria-labelledby="{tid}"{hid}>'
            f'<pre class="qe-eco-pre" tabindex="0"><code>{esc(code)}</code></pre></div>'
        )
    return (
        f'<details class="qe-eco-drawer" data-eco-root="{uid}">'
        '<summary class="qe-eco-summary">Inspect Ecosystem Config (ECharts · Plotly · Matplotlib · Bokeh · Mermaid)</summary>'
        '<div class="qe-eco-tabs-wrap">'
        '<div class="qe-eco-bar">'
        '<div class="qe-eco-tablist" role="tablist" aria-label="Plotting Ecosystem Formats">'
        f'{"".join(tabs)}</div>'
        '<div class="qe-eco-copy-wrap">'
        '<button type="button" class="qe-copy-btn" aria-label="Copy active ecosystem code snippet">Copy Snippet</button>'
        '<span class="qe-copy-status" role="status" aria-live="polite"></span>'
        '</div></div>'
        f'<div class="qe-eco-panels">{"".join(panels)}</div>'
        '</div></details>'
    )
