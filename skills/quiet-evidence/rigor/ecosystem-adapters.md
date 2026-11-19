# 5-Ecosystem Visualization Adapter Guide

Quiet Evidence metrology standards are **renderer-agnostic**. Use the deterministic
first-party Python SVG compiler for archival print (`M1`), schemas/bitfields/waveforms
(`M3`/`M5`/`M6`), and zero-JS standalone delivery, or translate the exact same Quiet UI
rules into **Apache ECharts**, **Plotly**, **Matplotlib**, **Bokeh**, or **Mermaid**.

---

## 1. Non-Negotiable Metrological Invariants Across All Backends

Regardless of which library renders the pixels, every chart emitted inside a Quiet UI
surface **MUST** preserve these five guarantees:

1. **Dynamic Token Binding**: Read CSS custom properties (`--text-primary`,
   `--text-secondary`, `--accent-focal`, `--status-warn`, `--status-danger`,
   `--border-hairline`) rather than hardcoding static colors so theme switches
   (`white`, `paper`, `dark`, `dark-paper`) stay WCAG-compliant.
2. **NIST SP 811 Quantity Calculus Labels**: Label axes strictly as `Symbol / Unit` or
   `Quantity, Symbol / Unit` (for example `P_grid / kW` or `η_bte / %`).
3. **Explicit Epistemic Separation**: Render discrete measurements as markers (`+/- u_y`
   error whiskers) and theoretical/empirical regressions as distinct dashed curves;
   never smooth away sparse test points with splines.
4. **Honest Dropout Handling**: Preserve `null` / `NaN` gaps as broken segments rather than
   interpolating across missing samples.
5. **Ceiling/Floor Envelopes & Safe Label Clamping**: Keep threshold reference lines
   inside plot margins with overlap guards (`hideOverlap: true`, bounded labels).

---

## 2. Apache ECharts (`renderer: 'svg'`)

Prefer the `'svg'` renderer for crisp scaling and CSS token integration. Read root CSS
tokens before invoking `chart.setOption(option)` and re-run on theme switches.

```javascript
function quietCssVar(name, fallback) {
  const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return value || fallback;
}

function buildQuietEChartsOption(seriesData, limitKw) {
  const ink = quietCssVar('--text-primary', '#0F172A');
  const muted = quietCssVar('--text-secondary', '#475569');
  const accent = quietCssVar('--accent-focal', '#0369A1');
  const warn = quietCssVar('--status-warn', '#B45309');
  const gridLine = quietCssVar('--border-hairline', '#E2E8F0');

  return {
    animation: false,
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', confine: true },
    grid: { left: 66, right: 24, top: 42, bottom: 52, containLabel: true },
    xAxis: {
      type: 'value',
      name: 'Local Time, t / h',
      nameLocation: 'middle',
      nameGap: 28,
      axisLabel: { color: muted, fontSize: 11, hideOverlap: true },
      splitLine: { lineStyle: { color: gridLine, type: 'dashed' } },
    },
    yAxis: {
      type: 'value',
      name: 'Active Power, P / kW',
      nameLocation: 'middle',
      nameGap: 44,
      axisLabel: { color: muted, fontSize: 11, hideOverlap: true },
      splitLine: { lineStyle: { color: gridLine, type: 'dashed' } },
    },
    series: [{
      name: 'Measured Power (+/- u_y)',
      type: 'line',
      connectNulls: false,
      symbol: 'circle',
      symbolSize: 6,
      itemStyle: { color: accent },
      lineStyle: { color: accent, width: 2 },
      textStyle: { color: ink },
      data: seriesData,
      markLine: {
        silent: true,
        symbol: ['none', 'none'],
        label: { position: 'insideEndTop', color: warn, fontSize: 10.5 },
        lineStyle: { color: warn, type: 'dashed', width: 1.5 },
        data: [{ name: 'Peak Tariff', yAxis: limitKw }],
      },
    }],
  };
}
```

---

## 3. Plotly (`plotly.graph_objects`)

Use `go.Scatter` with explicit `error_y`, `connectgaps=False`, crisp straight segments,
and `fig.add_hline` for operating corridors.

```python
import plotly.graph_objects as go


def make_quiet_plotly_figure(x, y_meas, u_y, x_model, y_model, ceiling_val, dark=False):
    fg = "#F8FAFC" if dark else "#0F172A"
    accent = "#38BDF8" if dark else "#0369A1"
    warn = "#FBBF24" if dark else "#B45309"

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x_model,
            y=y_model,
            mode="lines",
            name="Analytical Model",
            line={"color": "#94A3B8", "width": 1.8, "dash": "dash"},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y_meas,
            mode="markers+lines",
            name="Discrete Measurement (+/- u_y)",
            connectgaps=False,
            marker={"color": accent, "size": 6},
            line={"color": accent, "width": 2},
            error_y={"type": "data", "array": u_y, "visible": True, "thickness": 1.2},
        )
    )
    fig.add_hline(y=ceiling_val, line_dash="dashdot", line_color=warn, annotation_text="Ceiling")
    fig.update_layout(
        template="plotly_dark" if dark else "plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": fg},
        xaxis_title="Local Time, t / h",
        yaxis_title="Active Power, P / kW",
        margin={"l": 64, "r": 24, "t": 40, "b": 48},
    )
    return fig
```

---

## 4. Matplotlib (`M1` Archival Vector & Print Publications)

Match `M1` archival monographs by despine-trimming top/right rules, preserving discrete
errorbars vs. dashed model curves, and enforcing exact vector SVG/PDF export.

```python
import matplotlib.pyplot as plt


def render_quiet_matplotlib(x, y_meas, u_y, x_model, y_model, limit_val, out_svg):
    fig, ax = plt.subplots(figsize=(6.4, 3.6), constrained_layout=True)
    ax.plot(x_model, y_model, linestyle="--", linewidth=1.4, color="#475569", label="Analytical Model")
    ax.errorbar(
        x,
        y_meas,
        yerr=u_y,
        fmt="o-",
        markersize=4.5,
        linewidth=1.5,
        capsize=3,
        color="#0369A1",
        label="Measured (+/- u_y)",
    )
    ax.axhline(limit_val, linestyle="-.", linewidth=1.2, color="#B45309", label="Operating Limit")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", linestyle=":", linewidth=0.7, alpha=0.5)
    ax.set(xlabel="IMEP / bar", ylabel="eta_bte / %")
    ax.legend(frameon=False, fontsize=9)
    fig.savefig(out_svg, format="svg", transparent=True)
    plt.close(fig)
```

---

## 5. Bokeh (`bokeh.plotting` + `Whisker`)

When delivering interactive Python notebooks or server dashboards via Bokeh, bind
`ColumnDataSource` uncertainty intervals explicitly with `Whisker` annotations and
`Span` reference thresholds.

```python
from bokeh.models import ColumnDataSource, Span, Whisker
from bokeh.plotting import figure


def make_quiet_bokeh_figure(x, y, u_y, threshold):
    lower = [val - err if val is not None else None for val, err in zip(y, u_y)]
    upper = [val + err if val is not None else None for val, err in zip(y, u_y)]
    source = ColumnDataSource({"x": x, "y": y, "lower": lower, "upper": upper})

    p = figure(height=320, sizing_mode="stretch_width", toolbar_location="above")
    p.line("x", "y", source=source, line_width=2, color="#0369A1")
    p.scatter("x", "y", source=source, size=6, color="#0369A1")
    p.add_layout(Whisker(base="x", lower="lower", upper="upper", source=source, line_color="#0369A1"))
    p.add_layout(Span(location=threshold, dimension="width", line_color="#B45309", line_dash="dashed"))
    p.xaxis.axis_label = "Local Time, t / h"
    p.yaxis.axis_label = "Active Power, P / kW"
    p.outline_line_color = None
    return p
```

---

## 6. Mermaid (`%%{init: ...}%%` Neutral Quiet Theme)

For architectural diagrams outside native Quiet Evidence AST blocks, suppress Mermaid
defaults with neutral base tokens (`#F8FAFC` surfaces, `#0F172A` borders/ink, zero glow):

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#F8FAFC', 'primaryTextColor': '#0F172A', 'primaryBorderColor': '#475569', 'lineColor': '#475569'}}}%%
flowchart LR
  PV["PV-STRING-SOUTH (5.10 kW)"] --> Panel["PANEL-MAIN-200A (-1.68 kW Net)"]
  Batt["BATT-WALL-13KWH (84.0% SOC)"] --> Panel
  Panel --> Lock["LOCK-FRONT-01 (2-Step Guarded)"]
```
