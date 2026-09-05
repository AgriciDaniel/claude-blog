import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = ROOT / "skills" / "blog-chart" / "scripts" / "generate_chart_svg.py"


def load_generator():
    spec = importlib.util.spec_from_file_location("generate_chart_svg", GENERATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def base_config(chart_type="horizontal_bar"):
    return {
        "type": chart_type,
        "title": "AI Citation Sources",
        "subtitle": "Share of citations by platform",
        "source": {
            "title": "Example Study",
            "date": "2026-07-08",
            "url": "https://example.com/study",
        },
        "data": [
            {"label": "ChatGPT", "value": 43.8},
            {"label": "Perplexity", "value": 6.6},
            {"label": "Google AI Overviews", "value": 2.2},
        ],
    }


def test_render_chart_has_accessibility_and_figcaption():
    generator = load_generator()
    markup = generator.render_figure(base_config())

    assert 'role="img"' in markup
    assert 'aria-labelledby="ai-citation-sources-title ai-citation-sources-desc"' in markup
    assert '<title id="ai-citation-sources-title">AI Citation Sources</title>' in markup
    assert '<desc id="ai-citation-sources-desc">' in markup
    assert "<figcaption>Source: <a href=\"https://example.com/study\">Example Study</a>, 2026-07-08.</figcaption>" in markup
    assert "prefers-reduced-motion" in markup


def test_render_chart_escapes_labels_and_rejects_unsafe_source_url():
    generator = load_generator()
    config = base_config()
    config["data"][0]["label"] = 'Bad "label" <script>'
    config["source"]["url"] = "javascript:alert(1)"
    markup = generator.render_figure(config)

    assert "&lt;script&gt;" in markup
    assert "&quot;label&quot;" in markup
    assert "javascript:alert" not in markup
    assert "<figcaption>Source: Example Study, 2026-07-08.</figcaption>" in markup


def test_all_supported_chart_types_render():
    generator = load_generator()
    configs = [base_config(t) for t in ["horizontal_bar", "donut", "line", "lollipop", "area", "radar"]]
    grouped = {
        "type": "grouped_bar",
        "title": "Before After",
        "source": "Example Source",
        "data": [
            {"label": "Workflow A", "values": {"Before": 10, "After": 18}},
            {"label": "Workflow B", "values": {"Before": 8, "After": 15}},
        ],
    }
    configs.append(grouped)

    for config in configs:
        markup = generator.render_figure(config)
        assert "<figure" in markup
        assert "<svg" in markup
        assert "<figcaption>" in markup


def test_cli_writes_file_and_json_status(tmp_path, capsys):
    generator = load_generator()
    chart_json = tmp_path / "chart.json"
    chart_json.write_text(json.dumps(base_config()), encoding="utf-8")
    output = tmp_path / "chart.html"

    code = generator.main([
        "--root",
        str(tmp_path),
        "--input",
        "chart.json",
        "--output",
        "chart.html",
        "--json",
    ])
    captured = json.loads(capsys.readouterr().out)

    assert code == 0
    assert captured["status"] == "success"
    assert captured["output"] == "chart.html"
    assert output.read_text(encoding="utf-8").startswith('<figure class="blog-chart">')


def test_cli_rejects_paths_outside_root(tmp_path, capsys):
    generator = load_generator()
    outside = tmp_path.parent / "outside-chart.json"
    outside.write_text(json.dumps(base_config()), encoding="utf-8")

    code = generator.main([
        "--root",
        str(tmp_path),
        "--input",
        str(outside),
        "--json",
    ])
    captured = json.loads(capsys.readouterr().out)

    assert code == 1
    assert captured["status"] == "error"
    assert "escapes root" in captured["error"]
