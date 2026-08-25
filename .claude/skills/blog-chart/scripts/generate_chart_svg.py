#!/usr/bin/env python3
"""
Generate deterministic, accessible SVG charts for claude-blog.

Usage:
    python3 generate_chart_svg.py --input chart.json --output chart.html --json
    python3 generate_chart_svg.py --input chart.json --format html

Input JSON supports these chart types: horizontal_bar, grouped_bar, donut,
line, lollipop, area, and radar. The output is a transparent inline SVG wrapped
in a figure with title, desc, aria-labelledby, and figcaption.
"""

from __future__ import annotations

import argparse
import html
import json
import math
import os
import re
import secrets
import sys
from pathlib import Path
from urllib.parse import urlparse

WIDTH = 560
HEIGHT = 380
PALETTE = ["#f97316", "#38bdf8", "#a78bfa", "#22c55e", "#facc15", "#fb7185"]
TYPE_ALIASES = {
    "bar": "horizontal_bar",
    "horizontal bar": "horizontal_bar",
    "horizontal_bar": "horizontal_bar",
    "grouped bar": "grouped_bar",
    "grouped_bar": "grouped_bar",
    "donut": "donut",
    "line": "line",
    "lollipop": "lollipop",
    "area": "area",
    "radar": "radar",
}


class ChartError(ValueError):
    """Raised for invalid chart input or unsafe paths."""


def esc(value: object) -> str:
    """Escape text for SVG and HTML attributes."""
    return html.escape(str(value), quote=True)


def slugify(value: str, fallback: str = "chart") -> str:
    """Return a stable ASCII slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or fallback


def safe_number(value: object) -> float:
    """Convert a JSON value to a finite number."""
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ChartError(f"Invalid numeric value: {value!r}") from exc
    if not math.isfinite(number):
        raise ChartError(f"Invalid numeric value: {value!r}")
    return number


def safe_nonnegative_number(value: object) -> float:
    """Convert a JSON value to a finite nonnegative number."""
    number = safe_number(value)
    if number < 0:
        raise ChartError(f"Negative chart values are not supported: {value!r}")
    return number


def normalize_type(value: str) -> str:
    """Normalize chart type aliases."""
    key = str(value or "").strip().lower().replace("-", "_")
    normalized = TYPE_ALIASES.get(key) or TYPE_ALIASES.get(key.replace("_", " "))
    if not normalized:
        raise ChartError(f"Unsupported chart type: {value}")
    return normalized


def wrap_words(text: object, max_chars: int = 18, max_lines: int = 3) -> list[str]:
    """Wrap text at word boundaries for SVG labels."""
    words = str(text).split()
    if not words:
        return [""]
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= max_chars or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
        if len(lines) == max_lines:
            break
    if len(lines) < max_lines and current:
        lines.append(current)
    if len(lines) == max_lines and len(" ".join(words)) > len(" ".join(lines)):
        lines[-1] = lines[-1].rstrip(".") + "..."
    return lines


def text_block(
    text: object,
    x: float,
    y: float,
    max_chars: int,
    anchor: str = "middle",
    line_height: int = 13,
    attrs: str = "",
) -> str:
    """Render wrapped text using tspans."""
    lines = wrap_words(text, max_chars=max_chars)
    tspans = []
    for index, line in enumerate(lines):
        dy = 0 if index == 0 else line_height
        tspans.append(f'<tspan x="{x:.1f}" dy="{dy}">{esc(line)}</tspan>')
    attr_text = f" {attrs}" if attrs else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}"{attr_text}>{"".join(tspans)}</text>'


def normalize_data(config: dict) -> list[dict]:
    """Read standard label/value data."""
    data = config.get("data")
    if not isinstance(data, list) or not data:
        raise ChartError("Expected non-empty data array")
    normalized = []
    for item in data:
        if not isinstance(item, dict):
            raise ChartError("Each data item must be an object")
        label = str(item.get("label", "")).strip()
        if not label:
            raise ChartError("Each data item needs a label")
        normalized.append({"label": label, "value": safe_nonnegative_number(item.get("value", 0))})
    return normalized


def normalize_grouped(config: dict) -> tuple[list[str], list[str], dict[tuple[str, str], float]]:
    """Read grouped data from either series or row-oriented input."""
    series = config.get("series")
    values: dict[tuple[str, str], float] = {}
    labels: list[str] = []
    names: list[str] = []

    if series is not None and not isinstance(series, list):
        raise ChartError("Grouped series must be an array")

    if isinstance(series, list) and series:
        for series_item in series:
            if not isinstance(series_item, dict):
                raise ChartError("Each series item must be an object")
            name = str(series_item.get("name", "")).strip()
            if not name:
                raise ChartError("Each series needs a name")
            names.append(name)
            points = series_item.get("data")
            if not isinstance(points, list) or not points:
                raise ChartError("Each series needs a non-empty data array")
            for point in points:
                if not isinstance(point, dict):
                    raise ChartError("Each series data point must be an object")
                label = str(point.get("label", "")).strip()
                if not label:
                    raise ChartError("Each series data point needs a label")
                if label not in labels:
                    labels.append(label)
                values[(label, name)] = safe_nonnegative_number(point.get("value", 0))
        return labels, names, values

    rows = config.get("data")
    if not isinstance(rows, list) or not rows:
        raise ChartError("Grouped charts need data or series")
    for row in rows:
        if not isinstance(row, dict):
            raise ChartError("Each grouped row must be an object")
        label = str(row.get("label", "")).strip()
        if not label:
            raise ChartError("Each grouped row needs a label")
        labels.append(label)
        row_values = row.get("values")
        if not isinstance(row_values, dict):
            raise ChartError("Grouped row needs values object")
        if not row_values:
            raise ChartError("Grouped row needs non-empty values object")
        for name, value in row_values.items():
            series_name = str(name).strip()
            if not series_name:
                raise ChartError("Grouped values need non-empty series names")
            if series_name not in names:
                names.append(series_name)
            values[(label, series_name)] = safe_nonnegative_number(value)
    return labels, names, values


def source_parts(config: dict) -> tuple[str, str, str]:
    """Normalize source metadata."""
    source = config.get("source", {})
    if isinstance(source, str):
        return source, "", ""
    if not isinstance(source, dict):
        return "", "", ""
    return (
        str(source.get("title", "")).strip(),
        str(source.get("date", "")).strip(),
        str(source.get("url", "")).strip(),
    )


def safe_url(value: str) -> str:
    """Return an allowed source URL, or an empty string."""
    if not value:
        return ""
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"}:
        return ""
    return value


def describe_data(chart_type: str, config: dict) -> str:
    """Create an accessible chart description."""
    if chart_type == "grouped_bar":
        labels, names, values = normalize_grouped(config)
        parts = []
        for label in labels:
            series_bits = [f"{name} {values.get((label, name), 0):g}" for name in names]
            parts.append(f"{label}: {', '.join(series_bits)}")
    else:
        parts = [f"{item['label']} {item['value']:g}" for item in normalize_data(config)]
    source_title, source_date, _ = source_parts(config)
    source_text = f" Source: {source_title} {source_date}.".strip() if source_title else ""
    return f"{config.get('title', 'Chart')}. {chart_type.replace('_', ' ')} data: {'; '.join(parts)}.{source_text}"


def grid_lines(x: int, y: int, width: int, height: int, count: int = 4) -> str:
    """Render horizontal grid lines."""
    lines = []
    for index in range(count + 1):
        yy = y + height - (height * index / count)
        lines.append(
            f'<line x1="{x}" y1="{yy:.1f}" x2="{x + width}" y2="{yy:.1f}" '
            'stroke="currentColor" opacity="0.08" />'
        )
    return "\n".join(lines)


def render_horizontal_bar(config: dict) -> str:
    """Render a horizontal bar chart."""
    data = normalize_data(config)
    max_value = max(max(item["value"] for item in data), 1)
    chart_x, chart_y, chart_w, chart_h = 145, 78, 365, 220
    gap = 8
    bar_h = max(14, (chart_h - gap * (len(data) - 1)) / len(data))
    rows = [grid_lines(chart_x, chart_y, chart_w, chart_h, 4)]
    for index, item in enumerate(data):
        y = chart_y + index * (bar_h + gap)
        width = chart_w * item["value"] / max_value
        color = PALETTE[index % len(PALETTE)]
        rows.append(text_block(item["label"], 136, y + bar_h * 0.65, 16, "end", 12, 'font-size="11" fill="currentColor" opacity="0.8"'))
        rows.append(f'<rect x="{chart_x}" y="{y:.1f}" width="{width:.1f}" height="{bar_h:.1f}" rx="4" fill="{color}" />')
        rows.append(f'<text x="{chart_x + width + 8:.1f}" y="{y + bar_h * 0.65:.1f}" font-size="11" fill="currentColor">{item["value"]:g}</text>')
    return "\n".join(rows)


def render_lollipop(config: dict) -> str:
    """Render a lollipop chart."""
    data = normalize_data(config)
    max_value = max(max(item["value"] for item in data), 1)
    chart_x, chart_y, chart_w, chart_h = 145, 78, 365, 220
    row_h = chart_h / max(len(data), 1)
    rows = [grid_lines(chart_x, chart_y, chart_w, chart_h, 4)]
    for index, item in enumerate(data):
        cy = chart_y + row_h * index + row_h / 2
        cx = chart_x + chart_w * item["value"] / max_value
        color = PALETTE[index % len(PALETTE)]
        rows.append(text_block(item["label"], 136, cy + 4, 16, "end", 12, 'font-size="11" fill="currentColor" opacity="0.8"'))
        rows.append(f'<line x1="{chart_x}" y1="{cy:.1f}" x2="{cx:.1f}" y2="{cy:.1f}" stroke="currentColor" opacity="0.15" stroke-width="1" />')
        rows.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="6" fill="{color}" />')
        rows.append(f'<text x="{cx + 12:.1f}" y="{cy + 4:.1f}" font-size="11" fill="currentColor">{item["value"]:g}</text>')
    return "\n".join(rows)


def render_grouped_bar(config: dict) -> str:
    """Render a grouped vertical bar chart."""
    labels, names, values = normalize_grouped(config)
    max_value = max(max(values.values()), 1)
    chart_x, chart_y, chart_w, chart_h = 72, 92, 420, 185
    group_w = chart_w / max(len(labels), 1)
    bar_w = min(18, (group_w - 14) / max(len(names), 1))
    if bar_w <= 2:
        raise ChartError("Grouped chart is too dense for the fixed SVG renderer")
    rows = [grid_lines(chart_x, chart_y, chart_w, chart_h, 4)]
    for s_index, name in enumerate(names):
        lx = chart_x + s_index * 105
        color = PALETTE[s_index % len(PALETTE)]
        rows.append(f'<rect x="{lx}" y="62" width="10" height="10" fill="{color}" />')
        rows.append(f'<text x="{lx + 15}" y="71" font-size="11" fill="currentColor">{esc(name)}</text>')
    for g_index, label in enumerate(labels):
        base_x = chart_x + g_index * group_w + group_w / 2
        for s_index, name in enumerate(names):
            value = values.get((label, name), 0)
            h = chart_h * value / max_value
            x = base_x - (len(names) * bar_w) / 2 + s_index * bar_w
            y = chart_y + chart_h - h
            color = PALETTE[s_index % len(PALETTE)]
            rows.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w - 2:.1f}" height="{h:.1f}" fill="{color}" />')
        rows.append(text_block(label, base_x, chart_y + chart_h + 18, 12, "middle", 11, 'font-size="10" fill="currentColor" opacity="0.8"'))
    return "\n".join(rows)


def polar(cx: float, cy: float, radius: float, angle: float) -> tuple[float, float]:
    """Return a point on a circle."""
    return cx + radius * math.cos(angle), cy + radius * math.sin(angle)


def donut_path(cx: float, cy: float, outer: float, inner: float, start: float, end: float) -> str:
    """Build one donut segment path."""
    large = 1 if end - start > math.pi else 0
    x1, y1 = polar(cx, cy, outer, start)
    x2, y2 = polar(cx, cy, outer, end)
    x3, y3 = polar(cx, cy, inner, end)
    x4, y4 = polar(cx, cy, inner, start)
    return (
        f"M {x1:.2f} {y1:.2f} A {outer} {outer} 0 {large} 1 {x2:.2f} {y2:.2f} "
        f"L {x3:.2f} {y3:.2f} A {inner} {inner} 0 {large} 0 {x4:.2f} {y4:.2f} Z"
    )


def render_donut(config: dict) -> str:
    """Render a donut chart."""
    data = normalize_data(config)
    total = sum(max(item["value"], 0) for item in data) or 1
    cx, cy, outer, inner = 238, 185, 92, 52
    angle = -math.pi / 2
    rows = []
    for index, item in enumerate(data):
        share = max(item["value"], 0) / total
        end = angle + share * math.tau
        rows.append(f'<path d="{donut_path(cx, cy, outer, inner, angle, end)}" fill="{PALETTE[index % len(PALETTE)]}" />')
        angle = end
    rows.append(f'<text x="{cx}" y="{cy - 3}" text-anchor="middle" font-size="22" font-weight="800" fill="currentColor">{total:g}</text>')
    rows.append(f'<text x="{cx}" y="{cy + 16}" text-anchor="middle" font-size="10" fill="var(--chart-muted, currentColor)">total</text>')
    for index, item in enumerate(data):
        y = 105 + index * 28
        rows.append(f'<rect x="360" y="{y - 9}" width="11" height="11" fill="{PALETTE[index % len(PALETTE)]}" />')
        rows.append(f'<text x="378" y="{y}" font-size="11" fill="currentColor">{esc(item["label"])} {item["value"]:g}</text>')
    return "\n".join(rows)


def line_points(data: list[dict], chart_x: int, chart_y: int, chart_w: int, chart_h: int) -> list[tuple[float, float]]:
    """Map data to line chart points."""
    max_value = max(max(item["value"] for item in data), 1)
    count = max(len(data) - 1, 1)
    points = []
    for index, item in enumerate(data):
        x = chart_x + chart_w * index / count
        y = chart_y + chart_h - chart_h * item["value"] / max_value
        points.append((x, y))
    return points


def render_line_or_area(config: dict, area: bool = False) -> str:
    """Render a line or area chart."""
    data = normalize_data(config)
    chart_x, chart_y, chart_w, chart_h = 70, 82, 430, 210
    points = line_points(data, chart_x, chart_y, chart_w, chart_h)
    point_attr = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    rows = [grid_lines(chart_x, chart_y, chart_w, chart_h, 4)]
    if area:
        area_path = f"M {chart_x} {chart_y + chart_h} L " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in points) + f" L {chart_x + chart_w} {chart_y + chart_h} Z"
        rows.append(f'<path d="{area_path}" fill="{PALETTE[0]}" opacity="0.15" />')
    rows.append(f'<polyline points="{point_attr}" fill="none" stroke="{PALETTE[0]}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />')
    for index, ((x, y), item) in enumerate(zip(points, data)):
        rows.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{PALETTE[index % len(PALETTE)]}" />')
        rows.append(text_block(item["label"], x, chart_y + chart_h + 20, 10, "middle", 11, 'font-size="10" fill="currentColor" opacity="0.8"'))
    return "\n".join(rows)


def render_radar(config: dict) -> str:
    """Render a radar chart."""
    data = normalize_data(config)
    max_value = max(max(item["value"] for item in data), 1)
    cx, cy, radius = 280, 195, 92
    count = len(data)
    rows = []
    for level in (0.25, 0.5, 0.75, 1.0):
        pts = []
        for index in range(count):
            angle = -math.pi / 2 + math.tau * index / count
            x, y = polar(cx, cy, radius * level, angle)
            pts.append(f"{x:.1f},{y:.1f}")
        rows.append(f'<polygon points="{" ".join(pts)}" fill="none" stroke="currentColor" opacity="0.12" />')
    data_pts = []
    for index, item in enumerate(data):
        angle = -math.pi / 2 + math.tau * index / count
        axis_x, axis_y = polar(cx, cy, radius, angle)
        x, y = polar(cx, cy, radius * item["value"] / max_value, angle)
        data_pts.append(f"{x:.1f},{y:.1f}")
        rows.append(f'<line x1="{cx}" y1="{cy}" x2="{axis_x:.1f}" y2="{axis_y:.1f}" stroke="currentColor" opacity="0.14" />')
        label_x, label_y = polar(cx, cy, radius + 28, angle)
        anchor = "middle"
        if label_x < cx - 20:
            anchor = "end"
        elif label_x > cx + 20:
            anchor = "start"
        rows.append(text_block(item["label"], label_x, label_y, 12, anchor, 11, 'font-size="10" fill="currentColor" opacity="0.85"'))
    rows.append(f'<polygon points="{" ".join(data_pts)}" fill="{PALETTE[0]}" opacity="0.22" stroke="{PALETTE[0]}" stroke-width="2" />')
    return "\n".join(rows)


def render_chart_body(chart_type: str, config: dict) -> str:
    """Dispatch chart renderer."""
    renderers = {
        "horizontal_bar": render_horizontal_bar,
        "grouped_bar": render_grouped_bar,
        "donut": render_donut,
        "line": render_line_or_area,
        "lollipop": render_lollipop,
        "area": lambda cfg: render_line_or_area(cfg, area=True),
        "radar": render_radar,
    }
    return renderers[chart_type](config)


def render_figure(config: dict, output_format: str = "html") -> str:
    """Render a complete figure with accessible SVG."""
    chart_type = normalize_type(config.get("type", "horizontal_bar"))
    title = str(config.get("title", "Chart")).strip() or "Chart"
    subtitle = str(config.get("subtitle", "")).strip()
    chart_id = slugify(str(config.get("id") or title))
    title_id = f"{chart_id}-title"
    desc_id = f"{chart_id}-desc"
    desc = str(config.get("description") or describe_data(chart_type, config))
    source_title, source_date, source_url = source_parts(config)
    source_label = source_title or "Source"
    source_text = f"Source: {source_label}" + (f" ({source_date})" if source_date else "")
    source_href = safe_url(source_url)
    body = render_chart_body(chart_type, config)
    subtitle_svg = ""
    if subtitle:
        subtitle_svg = text_block(subtitle, WIDTH / 2, 48, 70, "middle", 13, 'font-size="12" fill="var(--chart-muted, currentColor)"')
    figcaption = f'Source: <a href="{esc(source_href)}">{esc(source_label)}</a>'
    if not source_href:
        figcaption = f"Source: {esc(source_label)}"
    if source_date:
        figcaption += f", {esc(source_date)}"
    figcaption += "."
    svg = f'''<figure class="blog-chart">
<svg viewBox="0 0 {WIDTH} {HEIGHT}" style="max-width: 100%; height: auto; font-family: 'Inter', system-ui, sans-serif; --chart-muted: #4b5563;" role="img" aria-labelledby="{esc(title_id)} {esc(desc_id)}">
  <style>
    @media (prefers-color-scheme: dark) {{ svg {{ --chart-muted: #d1d5db; }} }}
    @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; transition: none !important; }} }}
  </style>
  <title id="{esc(title_id)}">{esc(title)}</title>
  <desc id="{esc(desc_id)}">{esc(desc)}</desc>
  <text x="{WIDTH / 2:.1f}" y="29" text-anchor="middle" font-size="18" font-weight="800" fill="currentColor">{esc(title)}</text>
  {subtitle_svg}
  {body}
  <text x="{WIDTH / 2:.1f}" y="366" text-anchor="middle" font-size="10" fill="var(--chart-muted, currentColor)">{esc(source_text)}</text>
</svg>
<figcaption>{figcaption}</figcaption>
</figure>'''
    if output_format == "mdx":
        return to_mdx(svg)
    return svg


def to_mdx(markup: str) -> str:
    """Convert common SVG attributes for JSX or MDX contexts."""
    replacements = {
        "class=": "className=",
        "text-anchor": "textAnchor",
        "font-size": "fontSize",
        "font-weight": "fontWeight",
        "stroke-width": "strokeWidth",
        "stroke-linecap": "strokeLinecap",
        "stroke-linejoin": "strokeLinejoin",
    }
    for old, new in replacements.items():
        markup = markup.replace(old, new)
    markup = re.sub(r'style="([^"]*)"', style_attr_to_jsx, markup)
    return markup


def css_property_to_jsx(name: str) -> str:
    """Convert a CSS property name to a JSX style object key."""
    if name.startswith("--"):
        return json.dumps(name)
    parts = name.split("-")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


def style_attr_to_jsx(match: re.Match[str]) -> str:
    """Convert an HTML style attribute to an MDX style object."""
    declarations = []
    for declaration in match.group(1).split(";"):
        if ":" not in declaration:
            continue
        name, value = declaration.split(":", 1)
        name = name.strip()
        value = value.strip()
        if not name or not value:
            continue
        declarations.append(f"{css_property_to_jsx(name)}: {json.dumps(value)}")
    return "style={{" + ", ".join(declarations) + "}}"


def reject_symlink_path(path: Path, root: Path) -> None:
    """Reject symlinked input or output paths under root."""
    current = path
    parts = []
    while current != root and current != current.parent:
        parts.append(current)
        current = current.parent
    for candidate in parts:
        if candidate.exists() and candidate.is_symlink():
            raise ChartError(f"Refusing symlink path: {candidate}")


def resolve_under_root(value: str, root: Path, must_exist: bool) -> Path:
    """Resolve a path under the intended root."""
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = root / path
    reject_symlink_path(path.absolute(), root)
    resolved = path.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ChartError(f"Path escapes root: {value}") from exc
    if must_exist and not resolved.exists():
        raise ChartError(f"File not found: {value}")
    reject_symlink_path(resolved, root)
    return resolved


def load_config(path: Path) -> dict:
    """Load chart config JSON."""
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        raise ChartError(f"Invalid JSON at line {exc.lineno}, column {exc.colno}") from exc
    if not isinstance(data, dict):
        raise ChartError("Input JSON must be an object")
    return data


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser."""
    parser = argparse.ArgumentParser(description="Generate accessible blog chart SVG")
    parser.add_argument("--input", required=True, help="Chart JSON input path")
    parser.add_argument("--output", help="Output path for HTML or MDX figure")
    parser.add_argument("--format", choices=["html", "mdx"], default="html", help="Output format")
    parser.add_argument("--root", default=".", help="Root directory for input and output paths")
    parser.add_argument("--json", action="store_true", help="Output structured JSON status")
    return parser


def emit(data: dict, as_json: bool) -> None:
    """Print JSON or a concise human status."""
    if as_json:
        print(json.dumps(data, indent=2))
    elif data.get("status") == "success":
        if data.get("output"):
            print(f"Wrote {data['output']}")
        else:
            print(data.get("content", ""))
    else:
        print(f"Error: {data.get('error', 'Unknown error')}", file=sys.stderr)


def output_display_path(output_arg: str, output_path: Path, root: Path) -> str:
    """Return a non-resolved output path for status messages."""
    if Path(output_arg).expanduser().is_absolute():
        return str(output_path.relative_to(root))
    return output_arg


def write_text_atomic_no_follow(path: Path, text: str) -> None:
    """Atomically write text without following a final-path symlink."""
    dir_flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        dir_flags |= os.O_DIRECTORY
    if hasattr(os, "O_NOFOLLOW"):
        dir_flags |= os.O_NOFOLLOW

    dir_fd = os.open(path.parent, dir_flags)
    tmp_name = f".{path.name}.{os.getpid()}.{secrets.token_hex(8)}.tmp"
    tmp_created = False
    try:
        file_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            file_flags |= os.O_NOFOLLOW
        fd = os.open(tmp_name, file_flags, 0o600, dir_fd=dir_fd)
        tmp_created = True
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path.name, src_dir_fd=dir_fd, dst_dir_fd=dir_fd)
        tmp_created = False
        os.fsync(dir_fd)
    finally:
        if tmp_created:
            try:
                os.unlink(tmp_name, dir_fd=dir_fd)
            except OSError:
                pass
        os.close(dir_fd)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        root = Path(args.root).expanduser().resolve(strict=False)
        if not root.exists() or not root.is_dir():
            raise ChartError(f"Root is not a directory: {args.root}")
        input_path = resolve_under_root(args.input, root, must_exist=True)
        config = load_config(input_path)
        chart_type = normalize_type(config.get("type", "horizontal_bar"))
        markup = render_figure(config, args.format)
        result = {
            "status": "success",
            "type": chart_type,
            "bytes": len(markup.encode("utf-8")),
        }
        if args.output:
            output_path = resolve_under_root(args.output, root, must_exist=False)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            if output_path.exists() and output_path.is_symlink():
                raise ChartError(f"Refusing symlink output: {output_path}")
            write_text_atomic_no_follow(output_path, markup + os.linesep)
            result["output"] = output_display_path(args.output, output_path, root)
        else:
            result["content"] = markup
        emit(result, args.json)
        return 0
    except (ChartError, OSError) as exc:
        emit({"status": "error", "error": str(exc)}, args.json)
        return 1


if __name__ == "__main__":
    sys.exit(main())
