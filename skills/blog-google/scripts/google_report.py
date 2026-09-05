#!/usr/bin/env python3
"""
Google SEO Report Generator - PDF/HTML reports from API data.

Consumes JSON output from blog-google scripts and generates formatted reports
with charts, analytics tables, and priority findings.

Usage:
    python google_report.py --type cwv-audit --data cwv-data.json --domain example.com
    python google_report.py --type gsc-performance --data gsc-data.json --domain example.com
    python google_report.py --type indexation --data inspect-data.json --domain example.com
    python google_report.py --type full --data full-data.json --domain example.com
    cat data.json | python google_report.py --type cwv-audit --domain example.com
"""

import argparse
import html
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
except ImportError:
    print("Error: matplotlib required. Install with: pip install matplotlib", file=sys.stderr)
    sys.exit(1)

try:
    from weasyprint import HTML
except ImportError:
    HTML = None

# ─── Brand Colors ────────────────────────────────────────────────────────────

BRAND = {
    "primary": "#1a56db",
    "secondary": "#6366f1",
    "accent": "#06b6d4",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "dark": "#1e293b",
    "light_bg": "#f8fafc",
    "grid": "#e2e8f0",
    "muted": "#94a3b8",
}


def _score_color(score):
    if score >= 90:
        return BRAND["success"]
    elif score >= 50:
        return BRAND["warning"]
    return BRAND["danger"]


def _rating_color(rating):
    r = str(rating).lower().replace("-", "_").replace(" ", "_")
    if r in ("good", "pass", "fast"):
        return BRAND["success"]
    elif r in ("needs_improvement", "needs-improvement", "average", "warn"):
        return BRAND["warning"]
    return BRAND["danger"]


def _h(value) -> str:
    return html.escape(str(value), quote=True)


def _css_string(value) -> str:
    return str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")


# ─── Chart Setup ─────────────────────────────────────────────────────────────

def _setup_matplotlib():
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
        "axes.facecolor": "white",
        "figure.facecolor": "white",
        "axes.grid": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })


_setup_matplotlib()


# ─── Chart Functions ─────────────────────────────────────────────────────────

def chart_lighthouse_gauges(data: dict, output_dir: Path) -> str:
    """Generate 2x2 Lighthouse score gauges."""
    scores = data.get("lighthouse_scores", {})
    if not scores:
        return ""

    fig, axes = plt.subplots(2, 2, figsize=(8, 6), subplot_kw={"projection": "polar"})
    categories = [
        ("performance", "Performance"),
        ("accessibility", "Accessibility"),
        ("best-practices", "Best Practices"),
        ("seo", "SEO"),
    ]

    for ax, (key, label) in zip(axes.flat, categories):
        score = scores.get(key, 0)
        theta_bg = np.linspace(np.pi, 0, 100)
        theta_fill = np.linspace(np.pi, np.pi - (score / 100) * np.pi, 100)

        ax.plot(theta_bg, [1] * 100, linewidth=16, color="#e2e8f0", solid_capstyle="round")
        ax.plot(theta_fill, [1] * 100, linewidth=16, color=_score_color(score), solid_capstyle="round")

        ax.text(np.pi / 2, 0.35, f"{score}", ha="center", va="center",
                fontsize=28, fontweight="bold", color=BRAND["dark"])
        ax.text(np.pi / 2, -0.05, label, ha="center", va="center",
                fontsize=10, color=BRAND["muted"])

        ax.set_ylim(0, 1.3)
        ax.set_rticks([])
        ax.set_thetagrids([])
        ax.spines["polar"].set_visible(False)

    plt.tight_layout(pad=2)
    path = output_dir / "lighthouse_gauges.png"
    plt.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    return str(path)


def chart_cwv_distributions(data: dict, output_dir: Path) -> str:
    """Generate stacked horizontal bars for CWV metric distributions."""
    crux = data.get("crux", {})
    metrics = crux.get("metrics", {})
    if not metrics:
        return ""

    cwv_order = [
        "largest_contentful_paint", "interaction_to_next_paint",
        "cumulative_layout_shift", "first_contentful_paint",
        "experimental_time_to_first_byte",
    ]

    labels, goods, nis, poors = [], [], [], []
    for name in cwv_order:
        m = metrics.get(name)
        if not m or "distribution" not in m:
            continue
        d = m["distribution"]
        labels.append(m.get("label", name))
        goods.append(d.get("good", 0))
        nis.append(d.get("needs_improvement", 0))
        poors.append(d.get("poor", 0))

    if not labels:
        return ""

    fig, ax = plt.subplots(figsize=(8, max(2.5, len(labels) * 0.7)))
    y = range(len(labels))

    ax.barh(y, goods, color=BRAND["success"], label="Good", height=0.5)
    ax.barh(y, nis, left=goods, color=BRAND["warning"], label="Needs Improvement", height=0.5)
    left2 = [g + n for g, n in zip(goods, nis)]
    ax.barh(y, poors, left=left2, color=BRAND["danger"], label="Poor", height=0.5)

    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlim(0, 100)
    ax.set_xlabel("% of page loads")
    ax.legend(loc="lower right", fontsize=9)
    ax.invert_yaxis()

    for i, (g, n, p) in enumerate(zip(goods, nis, poors)):
        if g > 10:
            ax.text(g / 2, i, f"{g:.0f}%", ha="center", va="center", fontsize=8, color="white", fontweight="bold")
        if n > 10:
            ax.text(g + n / 2, i, f"{n:.0f}%", ha="center", va="center", fontsize=8, color="white", fontweight="bold")
        if p > 10:
            ax.text(g + n + p / 2, i, f"{p:.0f}%", ha="center", va="center", fontsize=8, color="white", fontweight="bold")

    plt.tight_layout()
    path = output_dir / "cwv_distributions.png"
    plt.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    return str(path)


def chart_cwv_timeline(data: dict, output_dir: Path) -> str:
    """Generate CWV timeline chart from CrUX History data."""
    metrics = data.get("metrics", {})
    periods = data.get("collection_periods", [])
    if not metrics or not periods:
        return ""

    cwv_metrics = ["largest_contentful_paint", "interaction_to_next_paint", "cumulative_layout_shift"]
    available = [m for m in cwv_metrics if m in metrics]
    if not available:
        return ""

    fig, axes = plt.subplots(len(available), 1, figsize=(10, 3 * len(available)), sharex=True)
    if len(available) == 1:
        axes = [axes]

    x_labels = [p.get("last", "")[-5:] for p in periods]  # MM-DD format
    x = range(len(x_labels))

    for ax, metric_name in zip(axes, available):
        m = metrics[metric_name]
        p75s = m.get("p75_values", [])
        label = m.get("label", metric_name)
        good_t = m.get("good_threshold", 0)
        poor_t = m.get("poor_threshold", 0)

        valid_x = [i for i, v in enumerate(p75s) if v is not None]
        valid_y = [v for v in p75s if v is not None]

        if not valid_y:
            continue

        # Threshold bands
        if good_t and poor_t:
            ax.axhspan(0, good_t, alpha=0.1, color=BRAND["success"])
            ax.axhspan(good_t, poor_t, alpha=0.1, color=BRAND["warning"])
            ax.axhline(y=good_t, color=BRAND["success"], linestyle="--", alpha=0.5, linewidth=1)
            ax.axhline(y=poor_t, color=BRAND["danger"], linestyle="--", alpha=0.5, linewidth=1)

        ax.plot(valid_x, valid_y, color=BRAND["primary"], linewidth=2, marker="o", markersize=3)
        ax.fill_between(valid_x, valid_y, alpha=0.1, color=BRAND["primary"])

        unit = m.get("unit", "")
        ax.set_ylabel(f"{label} (p75{unit})")
        ax.set_title(label, fontsize=12, fontweight="bold")

    if x_labels:
        step = max(1, len(x_labels) // 8)
        axes[-1].set_xticks(range(0, len(x_labels), step))
        axes[-1].set_xticklabels([x_labels[i] for i in range(0, len(x_labels), step)], rotation=45, fontsize=8)

    plt.tight_layout()
    path = output_dir / "cwv_timeline.png"
    plt.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    return str(path)


def chart_top_queries(data: dict, output_dir: Path) -> str:
    """Generate horizontal bar chart of top queries by clicks."""
    rows = data.get("rows", [])
    if not rows:
        return ""

    top = sorted(rows, key=lambda r: r.get("clicks", 0), reverse=True)[:15]
    if not top:
        return ""

    labels = [r.get("query", r.get("keys", ["?"])[0])[:40] for r in top]
    clicks = [r.get("clicks", 0) for r in top]

    fig, ax = plt.subplots(figsize=(8, max(3, len(labels) * 0.4)))
    y = range(len(labels))
    bars = ax.barh(y, clicks, color=BRAND["primary"], height=0.6)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Clicks")
    ax.invert_yaxis()

    for bar, val in zip(bars, clicks):
        if val > 0:
            ax.text(bar.get_width() + max(clicks) * 0.02, bar.get_y() + bar.get_height() / 2,
                    str(val), va="center", fontsize=8, color=BRAND["dark"])

    plt.tight_layout()
    path = output_dir / "top_queries.png"
    plt.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    return str(path)


def chart_index_status(data: dict, output_dir: Path) -> str:
    """Generate donut chart for URL inspection results."""
    summary = data.get("summary", {})
    if not summary:
        return ""

    labels, sizes, colors = [], [], []
    for key, label, color in [
        ("pass", "Indexed", BRAND["success"]),
        ("fail", "Not Indexed", BRAND["danger"]),
        ("neutral", "Neutral", BRAND["grid"]),
        ("error", "Error", BRAND["muted"]),
    ]:
        val = summary.get(key, 0)
        if val > 0:
            labels.append(f"{label} ({val})")
            sizes.append(val)
            colors.append(color)

    if not sizes:
        return ""

    fig, ax = plt.subplots(figsize=(5, 4))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, autopct="%1.0f%%",
        startangle=90, pctdistance=0.75, textprops={"fontsize": 9},
    )
    centre = plt.Circle((0, 0), 0.50, fc="white")
    ax.add_artist(centre)
    total = sum(sizes)
    ax.text(0, 0, f"{total}\nURLs", ha="center", va="center",
            fontsize=16, fontweight="bold", color=BRAND["dark"])

    plt.tight_layout()
    path = output_dir / "index_status.png"
    plt.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    return str(path)


# ─── CSS Template ────────────────────────────────────────────────────────────

def _base_css(domain: str) -> str:
    """Battle-tested A4 report CSS extracted from generate_pdf.py."""
    css_domain = _css_string(domain)
    return f"""
    @page {{ size: A4; margin: 22mm 18mm 25mm 18mm;
      @bottom-center {{ content: counter(page); font-size: 9pt; color: #94a3b8; font-family: 'DejaVu Sans', Arial, sans-serif; }}
      @bottom-right {{ content: "{css_domain} Google SEO Report"; font-size: 8pt; color: #cbd5e1; font-family: 'DejaVu Sans', Arial, sans-serif; }}
    }}
    @page :first {{ margin: 0; @bottom-center {{ content: none; }} @bottom-right {{ content: none; }} }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'DejaVu Sans', Arial, Helvetica, sans-serif; font-size: 10pt; line-height: 1.55; color: #1e293b; background: white; }}
    .title-page {{ page: first; width: 210mm; height: 297mm; background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #1a56db 100%); display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; color: white; position: relative; padding: 40mm 25mm; }}
    .title-page .badge {{ background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.2); border-radius: 20px; padding: 6px 18px; font-size: 10pt; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 20mm; color: #93c5fd; }}
    .title-page h1 {{ font-size: 30pt; font-weight: bold; margin-bottom: 6mm; letter-spacing: -0.5px; line-height: 1.2; }}
    .title-page .subtitle {{ font-size: 16pt; color: #93c5fd; margin-bottom: 12mm; font-weight: 300; }}
    .title-page .url {{ font-size: 14pt; color: #60a5fa; margin-bottom: 20mm; padding: 5mm 10mm; border: 1px solid rgba(96, 165, 250, 0.3); border-radius: 8px; background: rgba(96, 165, 250, 0.08); }}
    .title-page .score-box {{ background: rgba(255,255,255,0.1); border: 2px solid rgba(255,255,255,0.2); border-radius: 16px; padding: 8mm 15mm; margin-bottom: 15mm; }}
    .title-page .score-number {{ font-size: 48pt; font-weight: bold; color: #fbbf24; line-height: 1; }}
    .title-page .score-label {{ font-size: 11pt; color: #93c5fd; margin-top: 2mm; }}
    .title-page .meta {{ font-size: 10pt; color: #94a3b8; margin-top: 10mm; }}
    div.section {{ page-break-before: always; }}
    .section-header {{ background: #f8fafc; border-left: 4px solid #1a56db; padding: 5mm 6mm; margin-bottom: 6mm; page-break-after: avoid; }}
    .section-header h2 {{ font-size: 16pt; color: #0f172a; margin-bottom: 1mm; }}
    .section-header .section-score {{ font-size: 12pt; font-weight: bold; float: right; margin-top: -6mm; }}
    h3 {{ font-size: 12pt; color: #1a56db; margin-top: 6mm; margin-bottom: 3mm; padding-bottom: 1.5mm; border-bottom: 1px solid #e2e8f0; page-break-after: avoid; }}
    h4 {{ font-size: 10.5pt; color: #334155; margin-top: 4mm; margin-bottom: 2mm; page-break-after: avoid; }}
    p {{ margin-bottom: 3mm; color: #334155; }}
    .highlight {{ background: #fef3c7; border-left: 3px solid #f59e0b; padding: 3mm 4mm; margin: 4mm 0; font-size: 9.5pt; page-break-inside: avoid; }}
    .critical-box {{ background: #fef2f2; border-left: 3px solid #ef4444; padding: 3mm 4mm; margin: 4mm 0; font-size: 9.5pt; page-break-inside: avoid; }}
    .success-box {{ background: #f0fdf4; border-left: 3px solid #10b981; padding: 3mm 4mm; margin: 4mm 0; font-size: 9.5pt; page-break-inside: avoid; }}
    table {{ width: 100%; border-collapse: collapse; margin: 4mm 0 6mm 0; font-size: 9pt; page-break-inside: avoid; }}
    thead th {{ background: #f1f5f9; color: #0f172a; font-weight: bold; padding: 2.5mm 3mm; text-align: left; border-bottom: 2px solid #cbd5e1; font-size: 9pt; }}
    tbody td {{ padding: 2.5mm 3mm; border-bottom: 1px solid #f1f5f9; vertical-align: top; }}
    tbody tr:nth-child(even) {{ background: #fafbfc; }}
    .status-pass {{ color: #10b981; font-weight: bold; }}
    .status-fail {{ color: #ef4444; font-weight: bold; }}
    .status-warn {{ color: #f59e0b; font-weight: bold; }}
    .chart-container {{ text-align: center; margin: 5mm 0; page-break-inside: avoid; }}
    .chart-container img {{ max-width: 100%; height: auto; }}
    .chart-caption {{ font-size: 8.5pt; color: #94a3b8; font-style: italic; margin-top: 2mm; text-align: center; }}
    .chart-half {{ display: inline-block; width: 48%; vertical-align: top; text-align: center; margin: 2mm 0; }}
    .chart-half img {{ max-width: 100%; height: auto; }}
    .two-col {{ display: table; width: 100%; table-layout: fixed; margin: 3mm 0; }}
    .two-col .col {{ display: table-cell; vertical-align: top; padding: 0 2mm; }}
    .metric-card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 3mm 4mm; text-align: center; margin: 2mm 0; }}
    .metric-card .value {{ font-size: 18pt; font-weight: bold; line-height: 1.2; }}
    .metric-card .label {{ font-size: 8pt; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }}
    .action-item {{ background: #f8fafc; border-radius: 4px; padding: 3mm 4mm; margin: 3mm 0; border-left: 3px solid #cbd5e1; page-break-inside: avoid; }}
    .action-item.critical {{ border-left-color: #ef4444; background: #fef2f2; }}
    .action-item.high {{ border-left-color: #f59e0b; background: #fffbeb; }}
    .action-item.medium {{ border-left-color: #1a56db; background: #eff6ff; }}
    .priority-tag {{ display: inline-block; padding: 0.5mm 3mm; border-radius: 3px; font-size: 8pt; font-weight: bold; color: white; margin-right: 2mm; }}
    .priority-critical {{ background: #ef4444; }}
    .priority-high {{ background: #f59e0b; }}
    .priority-medium {{ background: #1a56db; }}
    .data-freshness {{ font-size: 8pt; color: #94a3b8; font-style: italic; margin-top: 4mm; padding-top: 2mm; border-top: 1px solid #e2e8f0; }}
    """


# ─── Section Builders ────────────────────────────────────────────────────────

def _img(path):
    """Convert file path to file:// URI for WeasyPrint."""
    if not path:
        return ""
    uri = Path(path).resolve().as_uri()
    return f'<div class="chart-container"><img src="{_h(uri)}"></div>'


def _metric_card(value, label, color=None):
    style = f' style="color: {_h(color)};"' if color else ""
    return f'<div class="metric-card"><div class="value"{style}>{_h(value)}</div><div class="label">{_h(label)}</div></div>'


def _rating_class(rating):
    r = str(rating).lower()
    if "good" in r or "pass" in r:
        return "status-pass"
    elif "poor" in r or "fail" in r:
        return "status-fail"
    return "status-warn"


def section_title_page(domain, report_title, subtitle, score=None, meta_items=None):
    score_html = ""
    if score is not None:
        score_html = f'''
        <div class="score-box">
            <div class="score-number">{_h(score)}</div>
            <div class="score-label">Lighthouse Performance Score</div>
        </div>'''

    meta_html = ""
    if meta_items:
        spans = " &bull; ".join(f"<span>{_h(item)}</span>" for item in meta_items)
        meta_html = f'<div class="meta">{spans}</div>'

    return f'''
    <div class="title-page">
        <div class="badge">{_h(report_title)}</div>
        <h1>Google SEO Report</h1>
        <div class="subtitle">{_h(subtitle)}</div>
        <div class="url">{_h(domain)}</div>
        {score_html}
        {meta_html}
    </div>'''


def section_cwv_audit(psi_data, crux_data, charts, history_data=None):
    """Build the Core Web Vitals audit section."""
    html = '<div class="section"><div class="section-header"><h2>Core Web Vitals Audit</h2></div>'

    # Lighthouse scores
    psi = psi_data if isinstance(psi_data, dict) else {}
    mobile = psi.get("psi", {}).get("mobile", psi)
    scores = mobile.get("lighthouse_scores", {})
    if scores:
        html += '<h3>Lighthouse Scores</h3>'
        html += charts.get("gauges", "")

    # Lab metrics
    lab = mobile.get("lab_metrics", {})
    if lab:
        html += '<h3>Lab Metrics</h3><table><thead><tr><th>Metric</th><th>Value</th><th>Score</th></tr></thead><tbody>'
        for k, v in lab.items():
            score_val = v.get("score")
            score_pct = f"{score_val:.0%}" if score_val is not None else "N/A"
            cls = "status-pass" if score_val and score_val >= 0.9 else ("status-warn" if score_val and score_val >= 0.5 else "status-fail")
            html += f'<tr><td>{_h(k)}</td><td>{_h(v.get("display", ""))}</td><td class="{_h(cls)}">{_h(score_pct)}</td></tr>'
        html += '</tbody></table>'

    # CrUX field data
    crux = crux_data if isinstance(crux_data, dict) else {}
    crux_metrics = crux.get("metrics", {})
    if crux_metrics:
        html += '<h3>CrUX Field Data (28-day Rolling Average)</h3>'
        html += charts.get("distributions", "")
        html += '<table><thead><tr><th>Metric</th><th>p75</th><th>Rating</th><th>Good %</th><th>NI %</th><th>Poor %</th></tr></thead><tbody>'
        for name, m in crux_metrics.items():
            rating = m.get("rating", "?")
            dist = m.get("distribution", {})
            unit = m.get("unit", "")
            p75 = m.get("p75", "?")
            display_val = f"{p75:.3f}" if name == "cumulative_layout_shift" else f"{p75}{unit}"
            html += f'<tr><td>{_h(m.get("label", name))}</td><td>{_h(display_val)}</td>'
            html += f'<td class="{_h(_rating_class(rating))}">{_h(str(rating).upper())}</td>'
            html += f'<td>{_h(dist.get("good", "N/A"))}%</td><td>{_h(dist.get("needs_improvement", "N/A"))}%</td><td>{_h(dist.get("poor", "N/A"))}%</td></tr>'
        html += '</tbody></table>'
        cp = crux.get("collection_period", {})
        if cp:
            html += f'<p class="data-freshness">Collection period: {_h(cp.get("first", "?"))} to {_h(cp.get("last", "?"))}. CrUX data is a 28-day rolling average updated daily ~04:00 UTC.</p>'
    elif crux.get("error"):
        html += f'<div class="highlight"><strong>CrUX Field Data:</strong> {_h(crux["error"])}</div>'

    # CrUX History timeline
    if history_data and not history_data.get("error"):
        html += '<h3>Core Web Vitals Trends (25-week)</h3>'
        html += charts.get("timeline", "")
        trends = history_data.get("trends", {})
        if trends:
            html += '<table><thead><tr><th>Metric</th><th>Direction</th><th>Change</th><th>Earliest Avg</th><th>Latest Avg</th></tr></thead><tbody>'
            for name, t in trends.items():
                direction = t.get("direction", "?")
                cls = "status-pass" if direction == "improving" else ("status-fail" if direction == "degrading" else "")
                change_pct = f"{t.get('change_pct', 0):+.1f}"
                html += f'<tr><td>{_h(t.get("label", name))}</td><td class="{_h(cls)}">{_h(str(direction).upper())}</td>'
                html += f'<td>{_h(change_pct)}%</td><td>{_h(t.get("earliest_avg", "?"))}</td><td>{_h(t.get("latest_avg", "?"))}</td></tr>'
            html += '</tbody></table>'

    # Failed audits
    failed = mobile.get("failed_audits", [])
    if failed:
        html += f'<h3>Failed / Warning Audits ({len(failed)})</h3>'
        html += '<table><thead><tr><th>Audit</th><th>Score</th><th>Details</th></tr></thead><tbody>'
        for a in failed[:20]:
            score_pct = f"{a['score']:.0%}" if a.get("score") is not None else "?"
            html += f'<tr><td>{_h(a.get("title", ""))}</td><td class="status-fail">{_h(score_pct)}</td><td>{_h(a.get("display", ""))}</td></tr>'
        html += '</tbody></table>'

    # SEO audits
    seo_audits = mobile.get("seo_audits", [])
    if seo_audits:
        seo_failed = [a for a in seo_audits if not a.get("pass")]
        if seo_failed:
            html += f'<h3>SEO Audit Issues ({len(seo_failed)})</h3>'
            for a in seo_failed:
                html += f'<div class="action-item critical"><h4>{_h(a.get("title", ""))}</h4></div>'
        else:
            html += f'<div class="success-box"><strong>SEO:</strong> All {len(seo_audits)} Lighthouse SEO checks passed.</div>'

    # Accessibility issues
    a11y = mobile.get("accessibility_audits", [])
    if a11y:
        html += f'<h3>Accessibility Issues ({len(a11y)})</h3>'
        html += '<table><thead><tr><th>Issue</th><th>Score</th></tr></thead><tbody>'
        for a in a11y:
            score_text = f"{a.get('score', 0):.0%}"
            html += f'<tr><td>{_h(a.get("title", ""))}</td><td class="status-fail">{_h(score_text)}</td></tr>'
        html += '</tbody></table>'

    # Opportunities
    opps = mobile.get("opportunities", [])
    if opps:
        html += f'<h3>Optimization Opportunities ({len(opps)})</h3>'
        html += '<table><thead><tr><th>Opportunity</th><th>Estimated Savings</th></tr></thead><tbody>'
        for o in opps:
            html += f'<tr><td>{_h(o.get("title", ""))}</td><td>{_h(o.get("savings_ms", 0))}ms</td></tr>'
        html += '</tbody></table>'

    html += '</div>'
    return html


def section_gsc_performance(gsc_data, charts):
    """Build the GSC performance section."""
    html = '<div class="section"><div class="section-header"><h2>Search Console Performance</h2></div>'

    totals = gsc_data.get("totals", {})
    dr = gsc_data.get("date_range", {})

    if totals:
        html += f'<p>Period: {_h(dr.get("start", "?"))} to {_h(dr.get("end", "?"))} | Property: {_h(gsc_data.get("property", "?"))}</p>'
        clicks_val = f'{totals.get("clicks", 0):,}'
        impr_val = f'{totals.get("impressions", 0):,}'
        ctr_val = f'{totals.get("ctr", 0)}%'
        rows_val = str(gsc_data.get("row_count", 0))
        html += '<div class="two-col">'
        html += f'<div class="col">{_metric_card(clicks_val, "Total Clicks", BRAND["primary"])}</div>'
        html += f'<div class="col">{_metric_card(impr_val, "Total Impressions", BRAND["secondary"])}</div>'
        html += '</div><div class="two-col">'
        html += f'<div class="col">{_metric_card(ctr_val, "Average CTR", BRAND["accent"])}</div>'
        html += f'<div class="col">{_metric_card(rows_val, "Queries Found")}</div>'
        html += '</div>'

    # Top queries chart
    html += charts.get("top_queries", "")

    # Top queries table
    rows = gsc_data.get("rows", [])
    if rows:
        html += '<h3>Top Queries</h3>'
        html += '<table><thead><tr><th>#</th><th>Query</th><th>Clicks</th><th>Impressions</th><th>CTR</th><th>Position</th></tr></thead><tbody>'
        sorted_rows = sorted(rows, key=lambda r: r.get("clicks", 0), reverse=True)
        for i, r in enumerate(sorted_rows[:25], 1):
            query = r.get("query", r.get("keys", ["?"])[0])
            impressions = f'{r.get("impressions", 0):,}'
            html += f'<tr><td>{_h(i)}</td><td>{_h(query)}</td><td>{_h(r.get("clicks", 0))}</td><td>{_h(impressions)}</td>'
            html += f'<td>{_h(r.get("ctr", 0))}%</td><td>{_h(r.get("position", 0))}</td></tr>'
        html += '</tbody></table>'

    # Quick wins
    qw = gsc_data.get("quick_wins", [])
    if qw:
        html += f'<h3>Quick Wins ({len(qw)} opportunities)</h3>'
        html += '<div class="highlight">These queries rank at position 4-10 with high impressions. A small ranking improvement could yield significant traffic gains.</div>'
        html += '<table><thead><tr><th>Query</th><th>Position</th><th>Impressions</th><th>Clicks</th></tr></thead><tbody>'
        for w in qw:
            query = w.get("keys", ["?"])[0] if w.get("keys") else "?"
            impressions = f'{w.get("impressions", 0):,}'
            html += f'<tr><td>{_h(query)}</td><td>{_h(w.get("position", 0))}</td><td>{_h(impressions)}</td><td>{_h(w.get("clicks", 0))}</td></tr>'
        html += '</tbody></table>'

    html += f'<p class="data-freshness">Search Analytics data has a 2-3 day lag. Data available for ~16 months.</p>'
    html += '</div>'
    return html


def section_indexation(inspect_data, charts):
    """Build the indexation status section."""
    html = '<div class="section"><div class="section-header"><h2>Indexation Status</h2></div>'

    summary = inspect_data.get("summary", {})
    total = inspect_data.get("total", 0)

    if summary:
        html += charts.get("index_status", "")
        html += f'<p>Total URLs inspected: {_h(total)}</p>'
        html += '<div class="two-col">'
        html += f'<div class="col">{_metric_card(summary.get("pass", 0), "Indexed", BRAND["success"])}</div>'
        html += f'<div class="col">{_metric_card(summary.get("fail", 0), "Not Indexed", BRAND["danger"])}</div>'
        html += '</div>'

    results = inspect_data.get("results", [])
    if results:
        html += '<h3>Per-URL Results</h3>'
        html += '<table><thead><tr><th>URL</th><th>Verdict</th><th>Coverage</th><th>Last Crawl</th></tr></thead><tbody>'
        for r in results:
            verdict = r.get("verdict", "?")
            cls = "status-pass" if verdict == "PASS" else ("status-fail" if verdict == "FAIL" else "")
            idx = r.get("index_status", {})
            cov = idx.get("coverage_state", r.get("error", "N/A"))
            crawl = idx.get("last_crawl_time", "N/A")
            if crawl and crawl != "N/A":
                crawl = crawl[:10]
            html += f'<tr><td style="word-break:break-all;font-size:8pt;">{_h(r.get("url", "?"))}</td>'
            html += f'<td class="{_h(cls)}">{_h(verdict)}</td><td>{_h(cov)}</td><td>{_h(crawl)}</td></tr>'
        html += '</tbody></table>'

    html += f'<p class="data-freshness">URL Inspection API: 2,000 inspections/day per site.</p>'
    html += '</div>'
    return html


# ─── Report Assemblers ───────────────────────────────────────────────────────

def generate_report(report_type, data, domain, output_dir, output_format="pdf"):
    """
    Generate a complete report.

    Args:
        report_type: 'cwv-audit', 'gsc-performance', 'indexation', or 'full'.
        data: Dictionary with all input data.
        domain: Domain name for the report header.
        output_dir: Directory for output files.
        output_format: 'pdf', 'html', or 'both'.

    Returns:
        Dictionary with output paths.
    """
    output_dir = Path(output_dir)
    charts_dir = output_dir / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    result = {"report_type": report_type, "domain": domain, "files": [], "error": None}

    # Generate charts based on report type
    chart_paths = {}

    if report_type in ("cwv-audit", "full"):
        psi = data.get("psi", data)
        mobile = psi.get("psi", {}).get("mobile", psi) if isinstance(psi, dict) else {}
        chart_paths["gauges"] = _img(chart_lighthouse_gauges(mobile, charts_dir))
        crux = data.get("crux", {})
        chart_paths["distributions"] = _img(chart_cwv_distributions({"crux": crux} if crux else data, charts_dir))
        history = data.get("crux_history", {})
        if history and not history.get("error"):
            chart_paths["timeline"] = _img(chart_cwv_timeline(history, charts_dir))

    if report_type in ("gsc-performance", "full"):
        gsc = data.get("gsc", data)
        chart_paths["top_queries"] = _img(chart_top_queries(gsc, charts_dir))

    if report_type in ("indexation", "full"):
        inspect = data.get("inspection", data)
        chart_paths["index_status"] = _img(chart_index_status(inspect, charts_dir))

    # Build HTML sections
    sections = []

    # Title page
    if report_type == "cwv-audit":
        mobile = data.get("psi", data).get("psi", {}).get("mobile", data) if isinstance(data, dict) else {}
        perf_score = mobile.get("lighthouse_scores", {}).get("performance")
        sections.append(section_title_page(domain, "Core Web Vitals Audit", "Performance & User Experience Analysis",
                                           score=perf_score, meta_items=[timestamp, "PSI + CrUX"]))
        sections.append(section_cwv_audit(data, data.get("crux", {}), chart_paths, data.get("crux_history")))

    elif report_type == "gsc-performance":
        gsc = data.get("gsc", data)
        clicks = gsc.get("totals", {}).get("clicks", 0)
        sections.append(section_title_page(domain, "Search Console Performance", "Google Search Analytics Report",
                                           score=clicks, meta_items=[timestamp, "Google Search Console API"]))
        sections.append(section_gsc_performance(gsc, chart_paths))

    elif report_type == "indexation":
        inspect = data.get("inspection", data)
        total = inspect.get("total", 0)
        sections.append(section_title_page(domain, "Indexation Status Report", "URL Index Coverage Analysis",
                                           score=total, meta_items=[timestamp, "URL Inspection API"]))
        sections.append(section_indexation(inspect, chart_paths))

    elif report_type == "full":
        sections.append(section_title_page(domain, "Google SEO Intelligence Report", "Comprehensive Analysis",
                                           meta_items=[timestamp, "All Google APIs"]))
        if data.get("psi") or data.get("crux"):
            sections.append(section_cwv_audit(data.get("psi", {}), data.get("crux", {}), chart_paths, data.get("crux_history")))
        if data.get("gsc"):
            sections.append(section_gsc_performance(data["gsc"], chart_paths))
        if data.get("inspection"):
            sections.append(section_indexation(data["inspection"], chart_paths))

    # Assemble HTML
    css = _base_css(domain)
    body = "\n".join(sections)
    html_content = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><style>{css}</style></head><body>{body}</body></html>"""

    # Output (closes audit VULN-014 path traversal on --domain)
    # Whitelist: alphanumerics + dot + underscore + hyphen. Anything else
    # (incl. "..", "/", "\\", NUL, Windows drive letters) becomes "_".
    import re
    safe_domain = re.sub(r"[^A-Za-z0-9._-]", "_", domain)[:128] or "report"
    base_name = f"Google-SEO-Report-{safe_domain}-{report_type}"

    # Re-resolve and assert containment inside output_dir (defense in depth).
    out_root = Path(output_dir).resolve()

    def _safe_path(name: str) -> Path:
        candidate = (out_root / name).resolve()
        if out_root != candidate.parent and out_root not in candidate.parents:
            raise ValueError(
                f"Refusing to write outside output_dir: {candidate}"
            )
        return candidate

    html_path = _safe_path(f"{base_name}.html")

    def _write_html_once() -> str:
        if str(html_path) not in result["files"]:
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            result["files"].append(str(html_path))
        return str(html_path)

    if output_format in ("html", "both"):
        _write_html_once()

    if output_format in ("pdf", "both"):
        pdf_path = _safe_path(f"{base_name}.pdf")
        if HTML is None:
            _write_html_once()
            result["error"] = "PDF generation skipped: weasyprint is not installed. HTML report generated."
        else:
            try:
                HTML(string=html_content).write_pdf(str(pdf_path))
                result["files"].append(str(pdf_path))
            except Exception as e:
                _write_html_once()
                result["error"] = f"PDF generation failed: {e}. HTML report generated."

    return result


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Google SEO Report Generator - PDF/HTML reports"
    )
    parser.add_argument(
        "--type", "-t",
        choices=["cwv-audit", "gsc-performance", "indexation", "full"],
        required=True,
        help="Report type",
    )
    parser.add_argument("--data", "-d", help="Path to JSON data file (or pipe via stdin)")
    parser.add_argument("--domain", required=True, help="Domain name for the report header")
    parser.add_argument("--output-dir", "-o", default=".", help="Output directory (default: current)")
    parser.add_argument(
        "--format", "-f",
        choices=["pdf", "html", "both"],
        default="pdf",
        help="Output format (default: pdf)",
    )
    parser.add_argument("--json", "-j", action="store_true", help="Output metadata as JSON")

    args = parser.parse_args()

    # Load data
    if args.data:
        try:
            with open(args.data, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading data file: {e}", file=sys.stderr)
            sys.exit(1)
    elif not sys.stdin.isatty():
        try:
            data = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(f"Error parsing stdin JSON: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Error: Provide --data file or pipe JSON via stdin.", file=sys.stderr)
        sys.exit(1)

    result = generate_report(
        report_type=args.type,
        data=data,
        domain=args.domain,
        output_dir=args.output_dir,
        output_format=args.format,
    )

    if result.get("error"):
        print(f"Error: {result['error']}", file=sys.stderr)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for f in result.get("files", []):
            print(f"Generated: {f}")


if __name__ == "__main__":
    main()
