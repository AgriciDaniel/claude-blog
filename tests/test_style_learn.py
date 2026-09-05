"""Tests for the blog style learning script."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import style_learn


def _post(title: str, body: str) -> str:
    return f"""---
title: {title}
author: Test Author
---

# {title}

{body}
"""


def _write_posts(tmp_path, count=5):
    posts = []
    bodies = [
        """## What changed?

We tested search intent mapping with three content teams. The content strategy became easier to review because each brief named the reader job. However, the team still kept examples short.

## How did the workflow hold up?

I found that content strategy reviews moved faster when writers used direct claims. The report was written after the final review.""",
        """## Why does structure matter?

Our team measured content strategy changes across several product pages. Therefore, we now open sections with the answer before adding details.

## What should writers copy?

We use practical examples, clear nouns, and enough context for a busy editor.""",
        """## What did the samples show?

I noticed that search intent mapping reduced vague introductions. The best drafts used content strategy language that sounded specific and grounded.

## How should teams adapt?

They should keep the first paragraph focused and add examples only when the reader needs proof.""",
        """## Where does voice appear?

We built a small review checklist for content strategy quality. It asks whether a sentence makes a useful claim or only fills space.

## What should the editor preserve?

Preserve the direct opening, the practical example, and the calm explanation.""",
        """## Can the profile guide future drafts?

Our team found that search intent mapping makes content strategy easier to teach. Moreover, it helps reviewers explain why a paragraph works.

## What should be avoided?

Avoid abstract promises when a concrete example would help the reader decide.""",
    ]
    for index in range(count):
        path = tmp_path / f"post-{index}.md"
        path.write_text(_post(f"Sample {index}", bodies[index % len(bodies)]), encoding="utf-8")
        posts.append(path)
    return posts


def test_learn_style_from_directory_includes_required_fields(tmp_path):
    _write_posts(tmp_path, count=5)

    profile = style_learn.learn_style([tmp_path], min_posts=5)

    assert profile["sample"]["post_count"] == 5
    assert profile["sample"]["warnings"] == []
    assert profile["sentence_length"]["mean_words"] > 0
    assert profile["sentence_length"]["median_words"] > 0
    assert "burstiness_variance" in profile["sentence_length"]
    assert profile["vocabulary"]["ttr"] > 0
    assert "transition_sentence_pct" in profile["rates"]
    assert "passive_sentence_pct" in profile["rates"]
    assert "ai_trigger_words_per_1k" in profile["rates"]
    assert "first_person_per_1k_words" in profile["rates"]
    assert profile["paragraph_lengths"]["distribution"]["under_40"]["count"] >= 0
    assert "question_ratio" in profile["headings"]
    assert profile["tone_descriptors"]


def test_warns_but_does_not_crash_below_minimum(tmp_path):
    paths = _write_posts(tmp_path, count=2)

    profile = style_learn.learn_style(paths, min_posts=5)

    assert profile["sample"]["post_count"] == 2
    assert profile["sample"]["warnings"] == [
        "Only 2 sample post(s) supplied. Recommended minimum is 5."
    ]


def test_signature_phrases_are_deterministic(tmp_path):
    _write_posts(tmp_path, count=5)

    first = style_learn.learn_style([tmp_path], min_posts=5)
    second = style_learn.learn_style([tmp_path], min_posts=5)
    phrases = [item["phrase"] for item in first["signature_phrases"]]

    assert first["signature_phrases"] == second["signature_phrases"]
    assert "content strategy" in phrases
    assert "the content" not in phrases


def test_unicode_corpus_produces_vocabulary_metrics(tmp_path):
    body = """## Что изменилось?

Мы проверили стратегия контента на нескольких страницах. Стратегия контента стала понятнее для редакторов.

## Как команда использует профиль?

Команда пишет короткие выводы и сохраняет спокойный тон в каждом разделе.
"""
    path = tmp_path / "unicode.md"
    path.write_text(_post("Кириллический пример", body), encoding="utf-8")

    profile = style_learn.learn_style([tmp_path], min_posts=1)

    assert profile["vocabulary"]["total_words"] > 0
    assert profile["vocabulary"]["unique_words"] > 0
    assert any("стратегия" in item["phrase"] for item in profile["signature_phrases"])


def test_empty_corpus_warns_and_skips_tone_descriptors(tmp_path):
    for index in range(2):
        path = tmp_path / f"empty-{index}.md"
        path.write_text("---\ntitle: Empty\n---\n\n", encoding="utf-8")

    profile = style_learn.learn_style([tmp_path], min_posts=2)

    assert profile["vocabulary"]["total_words"] == 0
    assert profile["tone_descriptors"] == []
    assert profile["sample"]["warnings"] == [
        "No analyzable words found in the sample corpus. Tone descriptors were skipped."
    ]


def test_markdown_render_is_voice_profile_block(tmp_path):
    _write_posts(tmp_path, count=5)
    profile = style_learn.learn_style([tmp_path], min_posts=5)

    markdown = style_learn.render_markdown(profile)

    assert "<!-- VOICE_PROFILE_START -->" in markdown
    assert "## Learned Voice Profile" in markdown
    assert "Sentence length" in markdown
    assert "Signature Phrases" in markdown
    assert "<!-- VOICE_PROFILE_END -->" in markdown


def test_cli_writes_json_profile(tmp_path):
    _write_posts(tmp_path, count=5)
    output = tmp_path / "voice.json"

    exit_code = style_learn.main([str(tmp_path), "--output", str(output)])

    assert exit_code == 0
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["sample"]["post_count"] == 5
    assert "tone_descriptors" in data


def test_cli_writes_markdown_profile_and_warns(tmp_path, capsys):
    paths = _write_posts(tmp_path, count=2)
    output = tmp_path / "VOICE.md"

    exit_code = style_learn.main([
        str(paths[0]),
        str(paths[1]),
        "--min",
        "5",
        "--format",
        "markdown",
        "--output",
        str(output),
    ])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Warning: Only 2 sample post(s) supplied. Recommended minimum is 5." in captured.err
    assert "## Learned Voice Profile" in output.read_text(encoding="utf-8")
