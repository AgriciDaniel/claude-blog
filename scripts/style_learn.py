#!/usr/bin/env python3
"""Learn an author voice profile from existing blog posts.

Usage:
    python3 style_learn.py <files-or-dir...> [--min 5] [--output PATH] [--format json|markdown]

The profiler reuses scripts/analyze_blog.py for per-post style signals, then
aggregates them into a deterministic JSON profile or a VOICE.md-ready markdown
block.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import analyze_blog  # noqa: E402

SUPPORTED_EXTENSIONS = {".md", ".mdx", ".markdown", ".txt"}
MAX_SAMPLE_BYTES = 2 * 1024 * 1024

STOPWORDS = {
    "a",
    "about",
    "above",
    "after",
    "again",
    "against",
    "all",
    "also",
    "am",
    "an",
    "and",
    "any",
    "are",
    "as",
    "at",
    "be",
    "because",
    "been",
    "before",
    "being",
    "below",
    "between",
    "both",
    "but",
    "by",
    "can",
    "could",
    "did",
    "do",
    "does",
    "doing",
    "down",
    "during",
    "each",
    "few",
    "for",
    "from",
    "further",
    "had",
    "has",
    "have",
    "having",
    "he",
    "her",
    "here",
    "hers",
    "him",
    "his",
    "how",
    "i",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "itself",
    "just",
    "me",
    "more",
    "most",
    "my",
    "no",
    "nor",
    "not",
    "now",
    "of",
    "off",
    "on",
    "once",
    "only",
    "or",
    "other",
    "our",
    "ours",
    "out",
    "over",
    "own",
    "same",
    "she",
    "should",
    "so",
    "some",
    "such",
    "than",
    "that",
    "the",
    "their",
    "theirs",
    "them",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "through",
    "to",
    "too",
    "under",
    "until",
    "up",
    "very",
    "was",
    "we",
    "were",
    "what",
    "when",
    "where",
    "which",
    "while",
    "who",
    "why",
    "will",
    "with",
    "would",
    "you",
    "your",
    "yours",
}

FIRST_PERSON_TERMS = {
    "i",
    "i'd",
    "i'll",
    "i'm",
    "i've",
    "me",
    "mine",
    "my",
    "myself",
    "our",
    "ours",
    "ourselves",
    "us",
    "we",
    "we'd",
    "we'll",
    "we're",
    "we've",
}


def collect_post_paths(inputs: Sequence[str | Path]) -> tuple[list[Path], list[str]]:
    """Collect blog post files from files or directories in stable order."""
    warnings: list[str] = []
    found: list[Path] = []

    for item in inputs:
        path = Path(item)
        if path.is_dir():
            for p in sorted(path.rglob("*"), key=lambda p: str(p)):
                if p.is_symlink():
                    warnings.append(f"Skipped symlinked sample: {p}")
                    continue
                if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS:
                    found.append(p)
        elif path.is_file():
            if path.is_symlink():
                warnings.append(f"Skipped symlinked sample: {path}")
                continue
            if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                found.append(path)
            else:
                warnings.append(f"Skipped unsupported file type: {path}")
        else:
            warnings.append(f"Skipped missing path: {path}")

    unique: dict[str, Path] = {}
    for path in found:
        key = str(path.resolve())
        unique.setdefault(key, path)

    return sorted(unique.values(), key=lambda p: str(p)), warnings


def strip_to_plain_text(content: str) -> str:
    """Normalize markdown or MDX content into plain text."""
    body = analyze_blog.strip_frontmatter(content)
    body = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
    body = re.sub(r"<[^>]+>", "", body)
    body = re.sub(r"!\[.*?\]\(.*?\)", "", body)
    body = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", body)
    body = re.sub(r"^#{1,6}\s+", "", body, flags=re.MULTILINE)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip()


def sentence_lengths(text: str) -> list[int]:
    """Return sentence lengths using the same minimum as analyze_blog."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [len(sentence.split()) for sentence in sentences if len(sentence.split()) > 2]


def word_tokens(text: str) -> list[str]:
    """Return normalized word tokens for corpus-level rates."""
    tokens: list[str] = []
    current: list[str] = []
    normalized = text.lower()

    for index, char in enumerate(normalized):
        if char.isalnum():
            current.append(char)
            continue
        if (
            char == "'"
            and current
            and index + 1 < len(normalized)
            and normalized[index + 1].isalnum()
        ):
            current.append(char)
            continue
        if current:
            tokens.append("".join(current))
            current = []

    if current:
        tokens.append("".join(current))
    return tokens


def content_tokens(text: str) -> list[str]:
    """Return non-stopword content tokens for signature phrase extraction."""
    return [
        token
        for token in word_tokens(text)
        if token not in STOPWORDS and len(token) > 2
    ]


def paragraph_word_counts(content: str) -> list[int]:
    """Return paragraph word counts using the same broad cleanup as analyze_blog."""
    cleaned = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    cleaned = re.sub(r"^#{1,6}\s+.*$", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"!\[.*?\]\(.*?\)", "", cleaned)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", cleaned) if p.strip()]
    return [len(p.split()) for p in paragraphs if len(p.split()) >= 5]


def _round(value: float, digits: int = 2) -> float:
    """Round floats consistently and avoid negative zero."""
    rounded = round(value, digits)
    return 0.0 if rounded == -0.0 else rounded


def _pct(part: int | float, whole: int | float) -> float:
    """Return a rounded percentage."""
    return _round((part / whole * 100) if whole else 0.0, 2)


def _rate_per_1k(count: int | float, words: int) -> float:
    """Return a rounded per-1,000-word rate."""
    return _round((count / words * 1000) if words else 0.0, 2)


def _distribution(values: list[int]) -> dict[str, dict[str, float | int]]:
    """Bucket paragraph lengths into readable ranges."""
    bins = {
        "under_40": lambda value: value < 40,
        "40_to_80": lambda value: 40 <= value <= 80,
        "81_to_150": lambda value: 81 <= value <= 150,
        "151_to_200": lambda value: 151 <= value <= 200,
        "over_200": lambda value: value > 200,
    }
    total = len(values)
    return {
        name: {
            "count": count,
            "pct": _pct(count, total),
        }
        for name, predicate in bins.items()
        for count in [sum(1 for value in values if predicate(value))]
    }


def signature_phrases(tokens: list[str], limit: int = 12) -> list[dict[str, Any]]:
    """Return top 2-gram and 3-gram content phrases."""
    counts: Counter[tuple[str, ...]] = Counter()
    for size in (2, 3):
        for index in range(0, len(tokens) - size + 1):
            ngram = tuple(tokens[index:index + size])
            if len(set(ngram)) == 1:
                continue
            counts[ngram] += 1

    ranked = sorted(counts.items(), key=lambda item: (-item[1], len(item[0]), " ".join(item[0])))
    return [
        {
            "phrase": " ".join(ngram),
            "count": count,
            "ngram_size": len(ngram),
        }
        for ngram, count in ranked[:limit]
    ]


def derive_tone_descriptors(metrics: dict[str, Any]) -> list[str]:
    """Infer compact tone labels from aggregate metrics."""
    descriptors: list[str] = []
    sentence_mean = metrics["sentence_length"]["mean_words"]
    variance = metrics["sentence_length"]["burstiness_variance"]
    transition_pct = metrics["rates"]["transition_sentence_pct"]
    passive_pct = metrics["rates"]["passive_sentence_pct"]
    first_person = metrics["rates"]["first_person_per_1k_words"]
    question_ratio = metrics["headings"]["question_ratio"]
    ai_per_1k = metrics["rates"]["ai_trigger_words_per_1k"]
    flesch = metrics["readability"]["flesch_reading_ease_mean"]

    if sentence_mean <= 15:
        descriptors.append("punchy")
    elif sentence_mean >= 22:
        descriptors.append("expansive")
    else:
        descriptors.append("balanced cadence")

    if variance >= 80:
        descriptors.append("varied rhythm")
    elif variance <= 25:
        descriptors.append("steady rhythm")

    if passive_pct <= 8:
        descriptors.append("active voice")
    elif passive_pct >= 18:
        descriptors.append("formal construction")

    if transition_pct >= 25:
        descriptors.append("highly signposted")
    elif transition_pct <= 8:
        descriptors.append("direct")

    if first_person >= 8:
        descriptors.append("personal")
    elif first_person <= 1:
        descriptors.append("institutional")

    if question_ratio >= 0.3:
        descriptors.append("question-led")

    if ai_per_1k <= 2:
        descriptors.append("plainspoken")
    elif ai_per_1k >= 8:
        descriptors.append("buzzword-prone")

    if flesch >= 60:
        descriptors.append("accessible")
    elif flesch <= 45:
        descriptors.append("technical")

    unique: list[str] = []
    for descriptor in descriptors:
        if descriptor not in unique:
            unique.append(descriptor)
    return unique[:7]


def analyze_sample(path: Path) -> dict[str, Any]:
    """Analyze one sample post with the shared analyzer functions."""
    content = analyze_blog._read_safely(path, MAX_SAMPLE_BYTES)
    body = analyze_blog.strip_frontmatter(content)
    plain_text = strip_to_plain_text(content)

    sentences = analyze_blog.analyze_sentences(plain_text)
    readability = analyze_blog.analyze_readability(plain_text)
    transitions = analyze_blog.analyze_transition_words(plain_text)
    passive = analyze_blog.analyze_passive_voice(plain_text)
    ai_triggers = analyze_blog.analyze_ai_trigger_words(plain_text)
    paragraphs = analyze_blog.analyze_paragraphs(body)
    originality = analyze_blog.analyze_originality(body)
    headings = analyze_blog.analyze_headings(body)

    tokens = word_tokens(plain_text)
    first_person_count = sum(1 for token in tokens if token in FIRST_PERSON_TERMS)
    heading_question_count = sum(1 for heading in headings["headings"] if heading["is_question"])

    return {
        "file": str(path),
        "word_count": len(tokens),
        "word_tokens": tokens,
        "sentence_lengths": sentence_lengths(plain_text),
        "paragraph_lengths": paragraph_word_counts(body),
        "content_tokens": content_tokens(plain_text),
        "first_person_count": first_person_count,
        "heading_question_count": heading_question_count,
        "headings_total": headings["total"],
        "analysis": {
            "sentences": sentences,
            "readability": readability,
            "transition_words": transitions,
            "passive_voice": passive,
            "ai_trigger_words": ai_triggers,
            "paragraphs": paragraphs,
            "originality": originality,
            "headings": headings,
        },
    }


def learn_style(inputs: Sequence[str | Path], min_posts: int = 5) -> dict[str, Any]:
    """Learn an aggregate voice profile from files or directories."""
    paths, warnings = collect_post_paths(inputs)
    if len(paths) < min_posts:
        warnings.append(
            f"Only {len(paths)} sample post(s) supplied. Recommended minimum is {min_posts}."
        )

    samples: list[dict[str, Any]] = []
    for path in paths:
        try:
            samples.append(analyze_sample(path))
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            warnings.append(f"Skipped unreadable sample {path}: {exc}")
    sentence_values = [value for sample in samples for value in sample["sentence_lengths"]]
    paragraph_values = [value for sample in samples for value in sample["paragraph_lengths"]]
    all_word_tokens = [token for sample in samples for token in sample["word_tokens"]]
    all_tokens = [token for sample in samples for token in sample["content_tokens"]]
    total_word_count = sum(sample["word_count"] for sample in samples)
    zero_content_corpus = total_word_count == 0
    if zero_content_corpus:
        warnings.append(
            "No analyzable words found in the sample corpus. Tone descriptors were skipped."
        )

    transition_count = sum(s["analysis"]["transition_words"]["transition_count"] for s in samples)
    transition_sentences = sum(s["analysis"]["transition_words"]["total_sentences"] for s in samples)
    passive_count = sum(s["analysis"]["passive_voice"]["passive_count"] for s in samples)
    passive_sentences = sum(s["analysis"]["passive_voice"]["total_sentences"] for s in samples)
    ai_trigger_count = sum(s["analysis"]["ai_trigger_words"]["trigger_count"] for s in samples)
    first_person_count = sum(s["first_person_count"] for s in samples)
    originality_markers = sum(s["analysis"]["originality"]["marker_count"] for s in samples)
    first_person_experience = sum(s["analysis"]["originality"]["first_person_count"] for s in samples)
    heading_questions = sum(s["heading_question_count"] for s in samples)
    heading_total = sum(s["headings_total"] for s in samples)
    h2_questions = sum(s["analysis"]["headings"]["h2_question_count"] for s in samples)
    h2_total = sum(s["analysis"]["headings"]["h2_count"] for s in samples)
    readability_values = [
        s["analysis"]["readability"].get("flesch_reading_ease", 0)
        for s in samples
        if s["analysis"]["readability"].get("flesch_reading_ease") is not None
    ]

    sentence_mean = statistics.mean(sentence_values) if sentence_values else 0.0
    sentence_median = statistics.median(sentence_values) if sentence_values else 0.0
    sentence_variance = statistics.pvariance(sentence_values) if len(sentence_values) > 1 else 0.0
    paragraph_mean = statistics.mean(paragraph_values) if paragraph_values else 0.0
    paragraph_median = statistics.median(paragraph_values) if paragraph_values else 0.0
    flesch_mean = statistics.mean(readability_values) if readability_values else 0.0
    unique_words = len(set(all_word_tokens))
    vocabulary_ttr = unique_words / total_word_count if total_word_count else 0.0

    profile: dict[str, Any] = {
        "profile_version": "1.0",
        "sample": {
            "post_count": len(samples),
            "min_recommended": min_posts,
            "files": [str(path) for path in paths],
            "warnings": warnings,
        },
        "sentence_length": {
            "mean_words": _round(sentence_mean),
            "median_words": _round(float(sentence_median)),
            "burstiness_variance": _round(sentence_variance),
            "std_dev_words": _round(sentence_variance ** 0.5),
            "sentence_count": len(sentence_values),
        },
        "vocabulary": {
            "ttr": _round(vocabulary_ttr, 3),
            "total_words": total_word_count,
            "unique_words": unique_words,
        },
        "readability": {
            "flesch_reading_ease_mean": _round(flesch_mean),
        },
        "rates": {
            "transition_sentence_pct": _pct(transition_count, transition_sentences),
            "passive_sentence_pct": _pct(passive_count, passive_sentences),
            "ai_trigger_words_per_1k": _rate_per_1k(ai_trigger_count, total_word_count),
            "first_person_per_1k_words": _rate_per_1k(first_person_count, total_word_count),
        },
        "paragraph_lengths": {
            "mean_words": _round(paragraph_mean),
            "median_words": _round(float(paragraph_median)),
            "paragraph_count": len(paragraph_values),
            "distribution": _distribution(paragraph_values),
        },
        "first_person": {
            "pronoun_count": first_person_count,
            "experience_marker_count": first_person_experience,
            "originality_marker_count": originality_markers,
        },
        "headings": {
            "question_count": heading_questions,
            "total": heading_total,
            "question_ratio": _round((heading_questions / heading_total) if heading_total else 0.0, 3),
            "h2_question_ratio": _round((h2_questions / h2_total) if h2_total else 0.0, 3),
        },
        "signature_phrases": signature_phrases(all_tokens),
        "per_post": [
            {
                "file": sample["file"],
                "word_count": sample["word_count"],
                "sentence_mean_words": sample["analysis"]["sentences"]["avg_length"],
                "transition_sentence_pct": sample["analysis"]["transition_words"]["transition_pct"],
                "passive_sentence_pct": sample["analysis"]["passive_voice"]["passive_pct"],
                "ai_trigger_words_per_1k": sample["analysis"]["ai_trigger_words"]["per_1k"],
                "h2_question_ratio": sample["analysis"]["headings"]["h2_question_ratio"],
            }
            for sample in samples
        ],
    }
    profile["tone_descriptors"] = [] if zero_content_corpus else derive_tone_descriptors(profile)
    return profile


def render_json(profile: dict[str, Any]) -> str:
    """Render a deterministic JSON profile."""
    return json.dumps(profile, indent=2, sort_keys=True) + "\n"


def render_markdown(profile: dict[str, Any]) -> str:
    """Render a VOICE.md-ready markdown profile block."""
    sample = profile["sample"]
    sentence = profile["sentence_length"]
    rates = profile["rates"]
    paragraphs = profile["paragraph_lengths"]
    headings = profile["headings"]
    vocabulary = profile["vocabulary"]
    phrases = profile["signature_phrases"]
    tone = profile["tone_descriptors"]

    phrase_lines = [
        f"- `{item['phrase']}`: {item['count']} occurrence(s)"
        for item in phrases
    ] or ["- No repeated content n-grams found"]

    tone_line = ", ".join(tone) if tone else "No strong tone descriptors detected"
    warnings = sample.get("warnings", [])
    warning_lines = [f"- {warning}" for warning in warnings] or ["- None"]

    distribution_lines = [
        f"- {name}: {bucket['count']} paragraph(s), {bucket['pct']}%"
        for name, bucket in paragraphs["distribution"].items()
    ]

    return "\n".join([
        "<!-- VOICE_PROFILE_START -->",
        "## Learned Voice Profile",
        "",
        f"Sample: {sample['post_count']} post(s).",
        "",
        "### Style Baselines",
        "",
        f"- Sentence length: mean {sentence['mean_words']} words, median {sentence['median_words']} words.",
        f"- Sentence burstiness: variance {sentence['burstiness_variance']}, standard deviation {sentence['std_dev_words']} words.",
        f"- Vocabulary richness: TTR {vocabulary['ttr']} across {vocabulary['total_words']} words.",
        f"- Transition rate: {rates['transition_sentence_pct']}% of sentences.",
        f"- Passive voice rate: {rates['passive_sentence_pct']}% of sentences.",
        f"- AI trigger baseline: {rates['ai_trigger_words_per_1k']} words per 1,000.",
        f"- First-person rate: {rates['first_person_per_1k_words']} mentions per 1,000 words.",
        f"- Heading question ratio: {headings['question_ratio']}.",
        "",
        "### Paragraph Distribution",
        "",
        *distribution_lines,
        "",
        "### Tone Descriptors",
        "",
        f"- {tone_line}",
        "",
        "### Signature Phrases",
        "",
        *phrase_lines,
        "",
        "### Warnings",
        "",
        *warning_lines,
        "<!-- VOICE_PROFILE_END -->",
        "",
    ])


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser."""
    parser = argparse.ArgumentParser(description="Learn a blog author voice profile.")
    parser.add_argument("paths", nargs="+", help="Blog post files or directories to analyze")
    parser.add_argument("--min", type=int, default=5, help="Minimum sample count before warning")
    parser.add_argument("--output", help="Write the rendered profile to this path")
    parser.add_argument("--format", choices=("json", "markdown"), default="json", help="Output format")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the style learning CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    profile = learn_style(args.paths, min_posts=args.min)
    rendered = render_markdown(profile) if args.format == "markdown" else render_json(profile)

    for warning in profile["sample"].get("warnings", []):
        print(f"Warning: {warning}", file=sys.stderr)

    if args.output:
        analyze_blog._safe_write_text(args.output, rendered)
    else:
        print(rendered, end="")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
