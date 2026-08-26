#!/usr/bin/env python3
"""
Blog Quality Analyzer - 5-Category, 100-Point Scoring System

Analyzes blog post files for content quality, SEO optimization, E-E-A-T signals,
technical elements, and AI citation readiness. Returns structured JSON, markdown
reports, or compact tables.

Usage:
    python3 analyze_blog.py <file>                          # Default JSON output
    python3 analyze_blog.py <file> --format markdown        # Markdown report
    python3 analyze_blog.py <file> --format table           # Compact table
    python3 analyze_blog.py <directory> --batch --sort score # Batch with sorting
    python3 analyze_blog.py <file> --category seo           # Single category detail
    python3 analyze_blog.py <file> --fix                    # Output specific fixes

Scoring:
    Content Quality       30 pts   Coverage, readability, originality, structure, utility, grammar
    SEO Optimization      25 pts   Title, headings, keywords, linking, meta, URL
    E-E-A-T Signals       15 pts   Author, citations, trust, evidence basis
    Technical Elements    15 pts   Schema, images, structured data, speed, mobile, social
    AI Citation Readiness 15 pts   Evidence, purpose, entities, utility, crawler access

Bands:
    90-100  Exceptional
    80-89   Strong
    70-79   Acceptable
    60-69   Below Standard
    <60     Rewrite

Optional dependencies (graceful degradation):
    pip install textstat beautifulsoup4
"""

import argparse
import errno
import json
import os
import re
import stat
import sys
import tempfile
import urllib.parse
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


def _project_version() -> str:
    """Read the package version from pyproject.toml."""
    try:
        text = (Path(__file__).resolve().parent.parent / "pyproject.toml").read_text(encoding="utf-8")
    except OSError:
        return "0.0.0"
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    return match.group(1) if match else "0.0.0"


# ---------------------------------------------------------------------------
# Optional dependency detection
# ---------------------------------------------------------------------------

try:
    import textstat
    HAS_TEXTSTAT = True
except ImportError:
    HAS_TEXTSTAT = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


def _print_dependency_notice() -> None:
    """Print missing-dependency notice to stderr so JSON output stays clean."""
    missing: list[str] = []
    if not HAS_TEXTSTAT:
        missing.append('textstat')
    if not HAS_BS4:
        missing.append('beautifulsoup4')
    if missing:
        print(
            f"Note: Optional dependencies not found: {', '.join(missing)}. "
            f"Install with: pip install {' '.join(missing)}",
            file=sys.stderr,
        )


# ---------------------------------------------------------------------------
# Editorial style diagnostic phrases
# ---------------------------------------------------------------------------

AI_PHRASES = [
    "in today's digital landscape", "it's important to note", "in conclusion",
    "dive into", "game-changer", "navigate the landscape", "revolutionize",
    "leverage", "comprehensive guide", "in the ever-evolving", "seamlessly",
    "cutting-edge", "harness the power", "at its core", "rich tapestry",
    "empower", "state-of-the-art",
]

# Configurable editorial terms to flag for manual review.
AI_TRIGGER_WORDS = [
    "delve", "tapestry", "multifaceted", "testament", "pivotal", "robust",
    "cutting-edge", "furthermore", "indeed", "moreover", "utilize", "leverage",
    "comprehensive", "landscape", "crucial", "foster", "illuminate", "underscore",
    "embark", "endeavor", "facilitate", "paramount", "nuanced", "intricate",
    "meticulous", "realm",
]

# Transition words/phrases for readability scoring
TRANSITION_WORDS = [
    "however", "therefore", "furthermore", "moreover", "additionally",
    "consequently", "nevertheless", "meanwhile", "similarly", "likewise",
    "nonetheless", "accordingly", "subsequently", "hence", "thus",
    "in contrast", "on the other hand", "for example", "for instance",
    "in addition", "as a result", "in other words", "that said",
    "in particular", "specifically", "alternatively", "conversely",
    "in fact", "notably", "importantly", "significantly",
]

# ---------------------------------------------------------------------------
# Content type word-count benchmarks
# ---------------------------------------------------------------------------

CONTENT_TYPE_BENCHMARKS: dict[str, tuple[int, int]] = {
    'guide': (2500, 5000),
    'how-to': (1500, 3000),
    'listicle': (1200, 2500),
    'opinion': (800, 1500),
    'case-study': (1500, 3000),
    'news': (600, 1200),
    'review': (1000, 2000),
    'default': (1200, 3000),
}

# ---------------------------------------------------------------------------
# Source tier classification
# ---------------------------------------------------------------------------

MAX_INPUT_BYTES = 10 * 1024 * 1024

TIER1_DOMAINS = [
    'nature.com', 'science.org', 'gov', 'edu', 'who.int', 'nih.gov',
    'cdc.gov', 'bls.gov', 'census.gov', 'europa.eu', 'un.org',
    'ieee.org', 'acm.org', 'arxiv.org', 'pubmed.ncbi',
]

TIER2_DOMAINS = [
    'reuters.com', 'apnews.com', 'bbc.com', 'nytimes.com',
    'washingtonpost.com', 'economist.com', 'forbes.com', 'hbr.org',
    'mckinsey.com', 'gartner.com', 'statista.com', 'pew', 'gallup.com',
]

LANGUAGE_PROFILES: dict[str, dict[str, Any]] = {
    'en': {
        'summary_labels': (
            r'TL;?DR', r'key takeaway', r'the bottom line',
            r'what you.ll learn', r'at a glance', r'in brief',
        ),
        'about_patterns': (
            r'\babout\s+(?:us|the author|me)\b', r'/about(?:[/?#]|$)',
        ),
        'contact_patterns': (r'\bcontact\b', r'/contact(?:[/?#]|$)'),
        'first_person_patterns': (
            r'\bI\s+(?:found|discovered|tested|built|created|noticed|learned|experienced)\b',
            r'\b(?:we|our team)\s+(?:tested|built|ran|analyzed|measured|conducted|found|discovered)\b',
            r'\bin (?:my|our) experience\b',
            r'\bfrom (?:my|our) (?:testing|research|analysis|work)\b',
        ),
        'methodology_patterns': (
            r'\b(?:methodology|sample size|test setup|testing method|research method)\b',
            r'\b(?:we|I|our team)\s+(?:tested|measured|analyzed|conducted)\b[^.\n]{0,180}'
            r'(?:\d|https?://|\[[^\]]+\]\(https?://)',
        ),
        'readability_model': 'flesch',
    },
    'tr': {
        'summary_labels': (r'özet', r'özetle', r'kısaca'),
        'about_patterns': (
            r'/biz-kimiz(?:[/?#]|$)', r'/hakk[ıi]m[ıi]zda(?:[/?#]|$)',
            r'\bbiz kimiz\b', r'\bhakk[ıi]m[ıi]zda\b',
        ),
        'contact_patterns': (
            r'/ilet[iİ]ş[iİ]m(?:[/?#]|$)', r'\bilet[iİ]ş[iİ]m\b',
        ),
        'first_person_patterns': (
            r'\b(?:biz|ekibimiz)\s+(?:test ettik|oluşturduk|inceledik|ölçtük|analiz ettik|derledik|bulduk)\b',
            r'\b(?:kendi\s+)?(?:kayıtlarımızdan|verilerimizden|analizimizden)\s+'
            r'(?:derlediğimiz|çıkardığımız|ölçtüğümüz)\b',
            r'\bportfolyomuzun\b[^.\n]{0,120}\bsayımından çıkarıldı\b',
            r'\b(?:deneyimimize|tecrübemize) göre\b',
        ),
        'methodology_patterns': (
            r'\b(?:yöntem|metodoloji|örneklem|örneklem büyüklüğü|test düzeni|araştırma yöntemi|sayım|kayıt)\b',
            r'\b(?:biz|ekibimiz)\s+(?:test ettik|ölçtük|analiz ettik)\b[^.\n]{0,180}'
            r'(?:\d|https?://|\[[^\]]+\]\(https?://)',
        ),
        'readability_model': 'atesman',
    },
}


def _read_safely(path: Path, max_bytes: int = MAX_INPUT_BYTES) -> str:
    """Read a regular non-symlink file with a size cap."""
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    elif path.is_symlink():
        raise ValueError(f"refusing to follow symlink: {path}")
    try:
        fd = os.open(str(path), flags)
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            raise ValueError(f"refusing to follow symlink: {path}") from exc
        raise
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise ValueError(f"not a regular file: {path}")
        if st.st_size > max_bytes:
            raise ValueError(f"input exceeds size cap ({st.st_size} > {max_bytes}): {path}")
        data = os.read(fd, max_bytes + 1)
    finally:
        os.close(fd)
    if len(data) > max_bytes:
        raise ValueError(f"input exceeds size cap after read ({max_bytes}): {path}")
    return data.decode("utf-8")


def _safe_write_text(path: str | Path, text: str) -> None:
    """Write output atomically and refuse symlink targets."""
    out = Path(path)
    if out.exists() and out.is_symlink():
        raise ValueError(f"output path is a symlink: {out}")
    if not out.parent.exists():
        raise ValueError(f"output directory does not exist: {out.parent}")
    fd, tmp = tempfile.mkstemp(dir=str(out.parent), prefix=f".{out.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, out)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _hostname(url: str) -> str:
    try:
        parsed = urllib.parse.urlparse(url)
    except ValueError:
        return ""
    return (parsed.hostname or "").lower().rstrip(".")


def _host_matches_domain(host: str, domain: str) -> bool:
    domain = domain.lower().rstrip(".")
    if domain in {"gov", "edu"}:
        if host == domain or host.endswith(f".{domain}"):
            return True
        labels = host.split(".")
        country_suffix = len(labels[-1]) == 2 and labels[-1].isalpha()
        if country_suffix and len(labels) >= 2 and labels[-2] == domain:
            return True
        if domain == "edu" and country_suffix and len(labels) >= 2 and labels[-2] == "ac":
            return True
        return False
    return host == domain or host.endswith(f".{domain}")

# ---------------------------------------------------------------------------
# Frontmatter extraction (kept from original)
# ---------------------------------------------------------------------------


def extract_frontmatter(content: str) -> dict[str, Any]:
    """Extract YAML frontmatter from markdown/MDX content."""
    frontmatter: dict[str, Any] = {}
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        fm_text = match.group(1)
        for line in fm_text.split('\n'):
            if ':' in line:
                key, _, value = line.partition(':')
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if value:
                    frontmatter[key] = value
    return frontmatter


def strip_frontmatter(content: str) -> str:
    """Remove YAML frontmatter from content."""
    return re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, count=1, flags=re.DOTALL)


class _HTMLAnalysisParser(HTMLParser):
    """Extract page metadata and a Markdown-like reader-visible HTML view."""

    _SKIPPED_TAGS = {'script', 'style', 'template', 'noscript', 'svg'}
    _BLOCK_TAGS = {
        'article', 'aside', 'div', 'footer', 'header', 'main', 'nav', 'p',
        'section',
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.metadata: dict[str, str] = {}
        self._metadata_priority: dict[str, int] = {}
        self._parts: list[str] = []
        self._in_head = False
        self._in_title = False
        self._title_parts: list[str] = []
        self._skip_depth = 0
        self._anchors: list[str] = []
        self._lists: list[str] = []
        self._table_depth = 0
        self._table_first_row = False
        self._table_row_cells = 0
        self._json_ld_parts: list[str] | None = None

    def _set_metadata(self, key: str, value: Any, priority: int) -> None:
        text = str(value or '').strip()
        if text and priority > self._metadata_priority.get(key, -1):
            self.metadata[key] = text
            self._metadata_priority[key] = priority

    def _newline(self, count: int = 1) -> None:
        if not self._parts:
            return
        trailing = len(self._parts[-1]) - len(self._parts[-1].rstrip('\n'))
        if trailing < count:
            self._parts.append('\n' * (count - trailing))

    def _extract_json_ld_metadata(self, raw: str) -> None:
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return

        def visit(value: Any) -> None:
            if isinstance(value, dict):
                schema_type = value.get('@type', '')
                types = {schema_type} if isinstance(schema_type, str) else set(schema_type or [])
                priority = 2 if types & {'Article', 'BlogPosting', 'NewsArticle'} else 1
                self._set_metadata('title', value.get('headline') or value.get('name'), priority)
                self._set_metadata('description', value.get('description'), priority)
                self._set_metadata('date', value.get('datePublished'), priority)
                self._set_metadata('lastUpdated', value.get('dateModified'), priority)
                self._set_metadata('language', value.get('inLanguage'), priority)
                author = value.get('author')
                if isinstance(author, dict):
                    self._set_metadata('author', author.get('name'), priority)
                elif isinstance(author, list):
                    names = [str(item.get('name', '')).strip() for item in author if isinstance(item, dict)]
                    self._set_metadata('author', ', '.join(name for name in names if name), priority)
                elif isinstance(author, str):
                    self._set_metadata('author', author, priority)
                for child in value.values():
                    if isinstance(child, (dict, list)):
                        visit(child)
            elif isinstance(value, list):
                for item in value:
                    visit(item)

        visit(data)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        values = {str(key).lower(): value or '' for key, value in attrs}
        if tag == 'html':
            self._set_metadata('language', values.get('lang'), 3)
        elif tag == 'head':
            self._in_head = True
        elif tag == 'title':
            self._in_title = True
            self._title_parts = []
        elif tag == 'meta':
            identity = (
                values.get('name') or values.get('property')
                or values.get('itemprop') or ''
            ).lower()
            content = values.get('content', '')
            fields = {
                'description': ('description', 3),
                'og:description': ('description', 2),
                'twitter:description': ('description', 1),
                'author': ('author', 3),
                'article:author': ('author', 2),
                'date': ('date', 3),
                'datepublished': ('date', 3),
                'article:published_time': ('date', 3),
                'datemodified': ('lastUpdated', 3),
                'last-modified': ('lastUpdated', 3),
                'article:modified_time': ('lastUpdated', 3),
                'og:title': ('title', 2),
                'twitter:title': ('title', 1),
            }
            if identity in fields:
                key, priority = fields[identity]
                self._set_metadata(key, content, priority)
        elif tag == 'link' and 'canonical' in values.get('rel', '').lower().split():
            canonical = values.get('href', '').strip()
            if canonical:
                parsed = urllib.parse.urlparse(canonical)
                path = urllib.parse.unquote(parsed.path or '/')
                self._set_metadata('slug', path.rstrip('/') or '/', 3)
        elif tag == 'time':
            identity = (values.get('itemprop') or values.get('class') or '').lower()
            if 'datemodified' in identity:
                self._set_metadata('lastUpdated', values.get('datetime'), 2)
            elif 'datepublished' in identity or 'published' in identity:
                self._set_metadata('date', values.get('datetime'), 2)

        if tag == 'script' and values.get('type', '').lower() == 'application/ld+json':
            self._json_ld_parts = []
        if tag in self._SKIPPED_TAGS:
            self._skip_depth += 1
            return
        if self._skip_depth or self._in_head:
            return

        if re.fullmatch(r'h[1-6]', tag):
            self._newline(2)
            self._parts.append('#' * int(tag[1]) + ' ')
        elif tag == 'a':
            self._parts.append('[')
            self._anchors.append(values.get('href', ''))
        elif tag in {'ul', 'ol'}:
            self._lists.append(tag)
            self._newline(1)
        elif tag == 'li':
            self._newline(1)
            self._parts.append('1. ' if self._lists and self._lists[-1] == 'ol' else '- ')
        elif tag == 'br':
            self._newline(1)
        elif tag == 'blockquote':
            self._newline(2)
            self._parts.append('> ')
        elif tag in {'strong', 'b'}:
            self._parts.append('**')
        elif tag in {'em', 'i'}:
            self._parts.append('*')
        elif tag == 'table':
            self._table_depth += 1
            self._table_first_row = True
            self._newline(2)
        elif tag == 'tr' and self._table_depth:
            self._table_row_cells = 0
            self._newline(1)
        elif tag in {'th', 'td'} and self._table_depth:
            self._table_row_cells += 1
            self._parts.append('| ')
        elif tag in self._BLOCK_TAGS:
            self._newline(2)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == 'title':
            self._in_title = False
            self._set_metadata('title', ''.join(self._title_parts), 3)
        elif tag == 'head':
            self._in_head = False

        if tag in self._SKIPPED_TAGS:
            if tag == 'script' and self._json_ld_parts is not None:
                self._extract_json_ld_metadata(''.join(self._json_ld_parts))
                self._json_ld_parts = None
            self._skip_depth = max(self._skip_depth - 1, 0)
            return
        if self._skip_depth or self._in_head:
            return

        if re.fullmatch(r'h[1-6]', tag) or tag in self._BLOCK_TAGS or tag == 'blockquote':
            self._newline(2)
        elif tag == 'a' and self._anchors:
            self._parts.append(f']({self._anchors.pop()})')
        elif tag in {'ul', 'ol'}:
            if self._lists:
                self._lists.pop()
            self._newline(2)
        elif tag == 'li':
            self._newline(1)
        elif tag in {'strong', 'b'}:
            self._parts.append('**')
        elif tag in {'em', 'i'}:
            self._parts.append('*')
        elif tag in {'th', 'td'} and self._table_depth:
            self._parts.append(' ')
        elif tag == 'tr' and self._table_depth:
            self._parts.append('|\n')
            if self._table_first_row and self._table_row_cells:
                self._parts.append('| ' + ' | '.join(['---'] * self._table_row_cells) + ' |\n')
                self._table_first_row = False
        elif tag == 'table':
            self._table_depth = max(self._table_depth - 1, 0)
            self._newline(2)

    def handle_data(self, data: str) -> None:
        if self._json_ld_parts is not None:
            self._json_ld_parts.append(data)
            return
        if self._in_title:
            self._title_parts.append(data)
            return
        if self._skip_depth or self._in_head:
            return
        text = re.sub(r'\s+', ' ', data)
        if text.strip():
            self._parts.append(text)

    def analysis_text(self) -> str:
        lines = [line.strip() for line in ''.join(self._parts).splitlines()]
        return re.sub(r'\n{3,}', '\n\n', '\n'.join(lines)).strip()


def extract_html_for_analysis(content: str) -> tuple[dict[str, Any], str]:
    """Return HTML metadata and normalized reader-visible analysis text."""
    parser = _HTMLAnalysisParser()
    parser.feed(content)
    parser.close()
    return dict(parser.metadata), parser.analysis_text()


def _detect_language(frontmatter: dict[str, Any], body: str) -> str:
    """Resolve a supported language profile without broad language guessing."""
    declared = str(
        frontmatter.get('lang')
        or frontmatter.get('language')
        or frontmatter.get('inLanguage')
        or ''
    ).strip().lower()
    if declared:
        primary = re.split(r'[-_]', declared, maxsplit=1)[0]
        return primary if primary in LANGUAGE_PROFILES else 'en'

    strong_turkish_markers = len(re.findall(r'[ığşİĞŞ]', body))
    letters = len(re.findall(r'[^\W\d_]', body, re.UNICODE))
    if strong_turkish_markers >= 2 and strong_turkish_markers / max(letters, 1) >= 0.002:
        return 'tr'
    return 'en'


def _plain_text_for_analysis(content: str) -> str:
    """Remove non-prose payloads while retaining reader-visible prose."""
    text = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    text = re.sub(r'<(?:script|style|svg)\b.*?</(?:script|style|svg)\s*>', '', text,
                  flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'^\s*\|.*\|\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*(?:[-*+]|\d+\.)\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*>\s?', '', text, flags=re.MULTILINE)
    return re.sub(r'\n{3,}', '\n\n', text).strip()


# ---------------------------------------------------------------------------
# Heading analysis (extended from original)
# ---------------------------------------------------------------------------


def analyze_headings(content: str) -> dict[str, Any]:
    """Analyze heading structure and keyword placement."""
    headings: list[dict[str, Any]] = []
    for match in re.finditer(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE):
        level = len(match.group(1))
        text = match.group(2).strip()
        is_question = text.rstrip().endswith('?')
        headings.append({
            'level': level,
            'text': text,
            'is_question': is_question,
        })

    h1_count = sum(1 for h in headings if h['level'] == 1)
    h2_count = sum(1 for h in headings if h['level'] == 2)
    h3_count = sum(1 for h in headings if h['level'] == 3)
    h2_questions = sum(1 for h in headings if h['level'] == 2 and h['is_question'])
    question_ratio = h2_questions / h2_count if h2_count > 0 else 0

    # Check for hierarchy skips
    hierarchy_clean = True
    prev_level = 0
    for h in headings:
        if h['level'] > prev_level + 1 and prev_level > 0:
            hierarchy_clean = False
        prev_level = h['level']

    return {
        'headings': headings,
        'h1_count': h1_count,
        'h2_count': h2_count,
        'h3_count': h3_count,
        'h2_question_count': h2_questions,
        'h2_question_ratio': round(question_ratio, 2),
        'hierarchy_clean': hierarchy_clean,
        'total': len(headings),
    }


# ---------------------------------------------------------------------------
# Paragraph analysis (kept from original)
# ---------------------------------------------------------------------------


def analyze_paragraphs(content: str) -> dict[str, Any]:
    """Analyze paragraph lengths."""
    cleaned = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    cleaned = re.sub(r'<[^>]+>', '', cleaned)
    cleaned = re.sub(r'^#{1,6}\s+.*$', '', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'!\[.*?\]\(.*?\)', '', cleaned)

    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', cleaned) if p.strip()]

    word_counts: list[int] = []
    over_150 = 0
    over_200 = 0
    in_range = 0  # 40-80 words (ideal paragraph range)

    for p in paragraphs:
        words = len(p.split())
        if words < 5:
            continue
        word_counts.append(words)
        if words > 200:
            over_200 += 1
        if words > 150:
            over_150 += 1
        if 40 <= words <= 80:
            in_range += 1

    total = len(word_counts)
    avg = sum(word_counts) / total if total else 0
    in_range_ratio = in_range / total if total else 0

    return {
        'total_paragraphs': total,
        'avg_word_count': round(avg, 1),
        'over_150_words': over_150,
        'over_200_words': over_200,
        # Backward-compatible aliases
        'over_100_words': over_150,
        'in_ideal_range': in_range,
        'in_40_55_range': in_range,
        'in_range_ratio': round(in_range_ratio, 2),
        'max_word_count': max(word_counts) if word_counts else 0,
        'total_word_count': sum(word_counts),
    }


# ---------------------------------------------------------------------------
# Image analysis (extended from original)
# ---------------------------------------------------------------------------


def analyze_images(content: str) -> dict[str, Any]:
    """Count images and check alt text, formats, optimization signals."""
    md_images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
    html_images: list[tuple[str, str]] = []
    for tag in re.findall(r'<img\b[^>]*>', content, re.IGNORECASE):
        src_match = re.search(r'\bsrc\s*=\s*["\']([^"\']+)["\']', tag, re.IGNORECASE)
        if not src_match:
            continue
        alt_match = re.search(r'\balt\s*=\s*["\']([^"\']*)["\']', tag, re.IGNORECASE)
        html_images.append((
            alt_match.group(1) if alt_match else "",
            src_match.group(1),
        ))

    images: list[dict[str, Any]] = []
    for alt, src in md_images:
        ext = Path(src.split('?')[0]).suffix.lower()
        images.append({
            'src': src,
            'has_alt': bool(alt.strip()),
            'alt_length': len(alt.strip()),
            'format': ext,
            'source': 'pixabay' if 'pixabay' in src else
                      'unsplash' if 'unsplash' in src else
                      'pexels' if 'pexels' in src else 'other',
        })

    for alt, src in html_images:
        has_alt = bool(alt.strip())
        ext = Path(src.split('?')[0]).suffix.lower()
        images.append({
            'src': src,
            'has_alt': has_alt,
            'alt_length': len(alt.strip()),
            'format': ext,
            'source': 'pixabay' if 'pixabay' in src else
                      'unsplash' if 'unsplash' in src else
                      'pexels' if 'pexels' in src else 'other',
        })

    with_alt = sum(1 for img in images if img['has_alt'])
    modern_formats = sum(1 for img in images if img.get('format') in ('.webp', '.avif', '.svg'))

    return {
        'count': len(images),
        'with_alt_text': with_alt,
        'without_alt_text': len(images) - with_alt,
        'modern_format_count': modern_formats,
        'formats': list(set(img.get('format', '') for img in images)),
        'sources': {s: sum(1 for i in images if i['source'] == s)
                    for s in set(i['source'] for i in images)} if images else {},
    }


# ---------------------------------------------------------------------------
# Chart analysis (kept from original)
# ---------------------------------------------------------------------------


def analyze_charts(content: str) -> dict[str, Any]:
    """Count SVG charts and check for type diversity."""
    svg_count = len(re.findall(r'<svg\b', content, re.IGNORECASE))
    figure_count = len(re.findall(r'<figure\b', content, re.IGNORECASE))

    return {
        'svg_count': svg_count,
        'figure_count': figure_count,
        'chart_count': max(svg_count, figure_count),
    }


# ---------------------------------------------------------------------------
# Citation analysis (extended from original)
# ---------------------------------------------------------------------------


def _classify_source_tier(url: str) -> int:
    """Classify a URL into tier 1, 2, or 3."""
    host = _hostname(url)
    if not host:
        return 3
    for domain in TIER1_DOMAINS:
        if _host_matches_domain(host, domain):
            return 1
    for domain in TIER2_DOMAINS:
        if _host_matches_domain(host, domain):
            return 2
    return 3


def analyze_citations(content: str) -> dict[str, Any]:
    """Analyze statistics and their citations with tier classification."""
    stat_patterns = re.findall(r'\d+\.?\d*%', content)

    # Inline citations: [text](url)
    inline_matches = re.findall(r'\[([^\]]+)\]\((https?://[^)]+)\)', content)
    citations_with_urls = [(text, url) for text, url in inline_matches]

    # Parenthetical citations (Source Name, year)
    paren_citations = re.findall(r'\(([^)]*(?:20\d{2})[^)]*)\)', content)

    # Tier classification
    tier_counts = {1: 0, 2: 0, 3: 0}
    for _, url in citations_with_urls:
        tier = _classify_source_tier(url)
        tier_counts[tier] += 1

    # Sourced vs unsourced stats
    sourced_stats = 0
    unsourced_stats = 0
    for stat_value in stat_patterns:
        pos = content.find(stat_value)
        if pos >= 0:
            context = content[pos:pos + 200]
            if re.search(r'\[.+\]\(https?://', context) or re.search(r'\([^)]*20\d{2}[^)]*\)', context):
                sourced_stats += 1
            else:
                unsourced_stats += 1

    return {
        'total_statistics': len(stat_patterns),
        'sourced_statistics': sourced_stats,
        'unsourced_statistics': unsourced_stats,
        'inline_citations': len(citations_with_urls),
        'paren_citations': len(paren_citations),
        'unique_sources': len(set(url.lower() for _, url in citations_with_urls)),
        'tier_counts': tier_counts,
    }


# ---------------------------------------------------------------------------
# FAQ analysis (kept from original)
# ---------------------------------------------------------------------------


def analyze_faq(content: str) -> dict[str, Any]:
    """Check for FAQ section and schema."""
    has_faq_section = bool(re.search(r'(?i)#{1,3}\s*(?:FAQ|Frequently Asked)', content))
    has_faq_schema = bool(re.search(r'(?i)FAQSchema|FAQPage|faqpage', content))

    faq_items = 0
    if has_faq_section:
        faq_match = re.search(r'(?i)#{1,3}\s*(?:FAQ|Frequently Asked).*', content, re.DOTALL)
        if faq_match:
            faq_text = faq_match.group()
            faq_items = len(re.findall(r'^#{3,4}\s+.+\?', faq_text, re.MULTILINE))

    return {
        'has_faq_section': has_faq_section,
        'has_faq_schema': has_faq_schema,
        'faq_item_count': faq_items,
    }


# ---------------------------------------------------------------------------
# Freshness analysis (kept from original)
# ---------------------------------------------------------------------------


def analyze_freshness(frontmatter: dict[str, Any]) -> dict[str, Any]:
    """Check freshness signals."""
    return {
        'has_date': 'date' in frontmatter,
        'has_last_updated': 'lastUpdated' in frontmatter or 'last_updated' in frontmatter,
        'date': frontmatter.get('date', ''),
        'last_updated': frontmatter.get('lastUpdated', frontmatter.get('last_updated', '')),
    }


# ---------------------------------------------------------------------------
# Self-promotion analysis (kept from original)
# ---------------------------------------------------------------------------


def analyze_self_promotion(content: str, brand_name: str = '') -> dict[str, Any]:
    """Check self-promotion levels."""
    promo_patterns = [
        r'(?i)at \w+,\s+we',
        r'(?i)our (?:team|company|product|platform|solution)',
        r'(?i)we (?:offer|provide|deliver|help|specialize)',
    ]

    promo_count = sum(len(re.findall(p, content)) for p in promo_patterns)

    return {
        'self_promotion_patterns': promo_count,
        'exceeds_limit': promo_count > 1,
    }


# ---------------------------------------------------------------------------
# NEW: Readability analysis (graceful degradation)
# ---------------------------------------------------------------------------


def analyze_readability(text: str, language: str = 'en') -> dict[str, Any]:
    """Compute readability metrics using textstat if available, else estimate."""
    words = re.findall(r"[^\W\d_]+(?:['’][^\W\d_]+)?", text, re.UNICODE)
    word_count = len(words)
    sentences = re.findall(r'[.!?]+', text)
    sentence_count = len(sentences) if sentences else 1
    avg_sentence_len = word_count / sentence_count

    if LANGUAGE_PROFILES.get(language, LANGUAGE_PROFILES['en'])["readability_model"] == 'atesman':
        vowel_count = sum(len(re.findall(r'[aeıioöuü]', word.lower())) for word in words)
        mean_syllables = vowel_count / max(word_count, 1)
        score = 198.825 - 40.175 * mean_syllables - 2.610 * avg_sentence_len
        score = max(0.0, min(100.0, score))
        return {
            'reading_model': 'atesman',
            'reading_ease': round(score, 1),
            'atesman_reading_ease': round(score, 1),
            'reading_time_minutes': round(word_count / 238, 1),
            'avg_sentence_length': round(avg_sentence_len, 1),
            'mean_syllables_per_word': round(mean_syllables, 2),
            'estimated': False,
        }

    if HAS_TEXTSTAT:
        fre = textstat.flesch_reading_ease(text)
        fkg = textstat.flesch_kincaid_grade(text)
        fog = textstat.gunning_fog(text)
        try:
            reading_time = round(textstat.reading_time(text, ms_per_char=14.69) / 60, 1)
        except Exception:
            reading_time = round(word_count / 238, 1)
        return {
            'reading_model': 'flesch',
            'reading_ease': round(fre, 1),
            'flesch_reading_ease': round(fre, 1),
            'flesch_kincaid_grade': round(fkg, 1),
            'gunning_fog': round(fog, 1),
            'reading_time_minutes': reading_time,
            'avg_sentence_length': round(avg_sentence_len, 1),
            'estimated': False,
        }
    else:
        # Rough Flesch estimate: 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)
        avg_word_len = len(text) / max(word_count, 1)
        est_syllable_ratio = avg_word_len / 4.7  # crude approximation
        fre = max(0, 206.835 - 1.015 * avg_sentence_len - 84.6 * est_syllable_ratio)
        return {
            'reading_model': 'flesch-estimate',
            'reading_ease': round(fre, 1),
            'flesch_reading_ease': round(fre, 1),
            'reading_time_minutes': round(word_count / 238, 1),
            'avg_sentence_length': round(avg_sentence_len, 1),
            'estimated': True,
        }


# ---------------------------------------------------------------------------
# NEW: Sentence analysis
# ---------------------------------------------------------------------------


def analyze_sentences(text: str) -> dict[str, Any]:
    """Analyze sentence lengths, burstiness (variance), and engagement."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    lengths = [len(s.split()) for s in sentences if len(s.split()) > 2]
    if not lengths:
        return {
            'count': 0,
            'avg_length': 0,
            'max_length': 0,
            'burstiness': 0.0,
            'std_dev': 0.0,
            'very_long_count': 0,
        }

    avg = sum(lengths) / len(lengths)
    std_dev = (sum((length - avg) ** 2 for length in lengths) / len(lengths)) ** 0.5
    burstiness = std_dev / avg if avg > 0 else 0
    very_long = sum(1 for length in lengths if length > 40)
    over_20 = sum(1 for length in lengths if length > 20)
    over_25 = sum(1 for length in lengths if length > 25)
    total = len(lengths)

    return {
        'count': total,
        'avg_length': round(avg, 1),
        'max_length': max(lengths),
        'burstiness': round(burstiness, 2),
        'std_dev': round(std_dev, 1),
        'very_long_count': very_long,
        'over_20_count': over_20,
        'over_20_pct': round(over_20 / total * 100, 1) if total else 0,
        'over_25_count': over_25,
    }


# ---------------------------------------------------------------------------
# Editorial style diagnostics
# ---------------------------------------------------------------------------


def analyze_ai_signals(text: str, sentences_info: dict[str, Any]) -> dict[str, Any]:
    """Return non-scoring editorial style diagnostics.

    Phrase frequency, type-token ratio, and sentence-length variance cannot
    determine authorship. The legacy keys remain for output compatibility, but
    the analyzer never converts these observations into an AI probability or a
    quality-gate decision.
    """
    found_phrases: list[dict[str, Any]] = []
    lower_text = text.lower()
    for phrase in AI_PHRASES:
        count = lower_text.count(phrase)
        if count > 0:
            found_phrases.append({'phrase': phrase, 'count': count})

    words = text.split()
    unique = len(set(w.lower() for w in words))
    ttr = unique / len(words) if words else 0

    return {
        'ai_phrases_found': found_phrases,
        'ai_phrase_count': sum(p['count'] for p in found_phrases),
        'vocabulary_diversity_ttr': round(ttr, 3),
        'burstiness': sentences_info.get('burstiness', 0),
        'likely_ai': None,
        'editorial_style_only': True,
        'not_an_authorship_classifier': True,
    }


# ---------------------------------------------------------------------------
# NEW: Passive voice estimation
# ---------------------------------------------------------------------------


def analyze_passive_voice(text: str) -> dict[str, Any]:
    """Estimate passive voice percentage using regex heuristics."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s for s in sentences if len(s.split()) > 2]
    if not sentences:
        return {'passive_count': 0, 'total_sentences': 0, 'passive_pct': 0.0}

    passive_pattern = re.compile(
        r'\b(was|were|been|being|is|are|am|get|got|gets|getting)\s+'
        r'(\w+ly\s+)?'  # optional adverb
        r'(\w+ed|written|spoken|taken|given|made|done|seen|known|shown|built|sent|found|held|told|left|run|set|kept|brought|thought|put)\b',
        re.IGNORECASE,
    )
    passive_count = sum(1 for s in sentences if passive_pattern.search(s))

    return {
        'passive_count': passive_count,
        'total_sentences': len(sentences),
        'passive_pct': round(passive_count / len(sentences) * 100, 1),
    }


# ---------------------------------------------------------------------------
# NEW: Transition word analysis
# ---------------------------------------------------------------------------


def analyze_transition_words(text: str) -> dict[str, Any]:
    """Measure percentage of sentences containing transition words."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s for s in sentences if len(s.split()) > 2]
    if not sentences:
        return {'transition_count': 0, 'total_sentences': 0, 'transition_pct': 0.0}

    lower_sentences = [s.lower() for s in sentences]
    transition_count = 0
    for s in lower_sentences:
        for tw in TRANSITION_WORDS:
            if tw in s:
                transition_count += 1
                break  # count each sentence once

    return {
        'transition_count': transition_count,
        'total_sentences': len(sentences),
        'transition_pct': round(transition_count / len(sentences) * 100, 1),
    }


# ---------------------------------------------------------------------------
# NEW: AI trigger word detection
# ---------------------------------------------------------------------------


def analyze_ai_trigger_words(text: str) -> dict[str, Any]:
    """Count AI trigger words per 1,000 words."""
    words = text.split()
    word_count = len(words)
    if word_count == 0:
        return {'trigger_count': 0, 'per_1k': 0.0, 'found': []}

    lower_text = text.lower()
    found: list[dict[str, Any]] = []
    total = 0
    for tw in AI_TRIGGER_WORDS:
        count = len(re.findall(r'\b' + re.escape(tw) + r'\b', lower_text))
        if count > 0:
            found.append({'word': tw, 'count': count})
            total += count

    per_1k = round(total / word_count * 1000, 1)

    return {
        'trigger_count': total,
        'per_1k': per_1k,
        'found': found,
    }


# ---------------------------------------------------------------------------
# NEW: Schema / structured data detection (graceful degradation)
# ---------------------------------------------------------------------------


def analyze_schema(content: str) -> dict[str, Any]:
    """Detect JSON-LD schema markup in content."""
    schemas: list[str] = []

    def collect_types(value: Any) -> None:
        if isinstance(value, dict):
            schema_type = value.get('@type')
            if isinstance(schema_type, str):
                schemas.append(schema_type)
            elif isinstance(schema_type, list):
                schemas.extend(item for item in schema_type if isinstance(item, str))
            for child in value.values():
                if isinstance(child, (dict, list)):
                    collect_types(child)
        elif isinstance(value, list):
            for item in value:
                collect_types(item)

    if HAS_BS4:
        try:
            soup = BeautifulSoup(content, 'html.parser')
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    data = json.loads(script.string)
                    collect_types(data)
                except (json.JSONDecodeError, TypeError):
                    pass
        except Exception:
            pass
    else:
        # Fallback: parse JSON-LD script bodies without an HTML dependency.
        for script_body in re.findall(
            r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script\s*>',
            content,
            re.DOTALL | re.IGNORECASE,
        ):
            try:
                collect_types(json.loads(script_body))
            except (json.JSONDecodeError, TypeError):
                for match in re.findall(r'"@type"\s*:\s*"([^"]+)"', script_body):
                    schemas.append(match)

    return {
        'schemas_found': schemas,
        'schema_count': len(schemas),
        'has_blogposting': 'BlogPosting' in schemas or 'Article' in schemas,
        'has_faqpage': 'FAQPage' in schemas,
        'has_person': 'Person' in schemas,
        'has_organization': 'Organization' in schemas,
        'has_breadcrumblist': 'BreadcrumbList' in schemas,
    }


# ---------------------------------------------------------------------------
# NEW: Link analysis
# ---------------------------------------------------------------------------


def analyze_links(content: str) -> dict[str, Any]:
    """Analyze internal and external links, anchor quality, and tiers."""
    # Internal links: relative paths (not starting with http or /)
    internal = re.findall(r'\[([^\]]+)\]\((?!https?://|#)([^)]+)\)', content)
    # External links
    external = re.findall(r'\[([^\]]+)\]\((https?://[^)]+)\)', content)

    bad_anchor_keywords = {'click here', 'read more', 'this article', 'here', 'link', 'this'}
    bad_anchors = [a for a, _ in internal + external if a.lower().strip() in bad_anchor_keywords]

    # Tier classification for external links
    tier_counts = {1: 0, 2: 0, 3: 0}
    for _, url in external:
        tier = _classify_source_tier(url)
        tier_counts[tier] += 1

    return {
        'internal_count': len(internal),
        'external_count': len(external),
        'total_links': len(internal) + len(external),
        'bad_anchor_texts': bad_anchors,
        'external_tier_counts': tier_counts,
    }


# ---------------------------------------------------------------------------
# NEW: Originality markers
# ---------------------------------------------------------------------------


def analyze_originality(content: str, language: str = 'en') -> dict[str, Any]:
    """Detect distinctive evidence and first-hand claims without inferring truth."""
    markers: list[str] = []

    if re.search(r'(?:\[|<!--\s*)ORIGINAL DATA(?:\]|(?:\s*:.*)?-->)', content, re.IGNORECASE):
        markers.append('original_data_tag')
    if re.search(r'(?:\[|<!--\s*)PERSONAL EXPERIENCE(?:\]|(?:\s*:.*)?-->)', content, re.IGNORECASE):
        markers.append('personal_experience_tag')
    if re.search(r'(?:\[|<!--\s*)UNIQUE INSIGHT(?:\]|(?:\s*:.*)?-->)', content, re.IGNORECASE):
        markers.append('unique_insight_tag')

    profile = LANGUAGE_PROFILES.get(language, LANGUAGE_PROFILES['en'])
    first_person_patterns = profile['first_person_patterns']
    first_person_count = 0
    for pattern in first_person_patterns:
        first_person_count += len(re.findall(pattern, content, re.IGNORECASE))
    if first_person_count > 0:
        markers.append('first_person_experience')

    methodology_patterns = profile['methodology_patterns']
    methodology_count = sum(
        len(re.findall(pattern, content, re.IGNORECASE))
        for pattern in methodology_patterns
    )
    evidence_marker_count = sum(
        1 for marker in markers
        if marker in {'original_data_tag', 'personal_experience_tag', 'unique_insight_tag'}
    )
    unsupported_experience_claims = 0
    for paragraph in re.split(r'\n\s*\n', content):
        has_claim = any(re.search(pattern, paragraph, re.IGNORECASE)
                        for pattern in first_person_patterns)
        has_method = any(re.search(pattern, paragraph, re.IGNORECASE)
                         for pattern in methodology_patterns)
        has_support = bool(re.search(
            r'(?:ORIGINAL DATA|PERSONAL EXPERIENCE|UNIQUE INSIGHT|\d|https?://)',
            paragraph,
            re.IGNORECASE,
        ))
        if has_claim and not (has_method or has_support):
            unsupported_experience_claims += 1

    return {
        'markers': markers,
        'marker_count': len(markers),
        'first_person_count': first_person_count,
        'evidence_marker_count': evidence_marker_count,
        'methodology_count': methodology_count,
        'unsupported_experience_claims': unsupported_experience_claims,
    }


# ---------------------------------------------------------------------------
# NEW: Engagement elements
# ---------------------------------------------------------------------------


def analyze_engagement(content: str) -> dict[str, Any]:
    """Detect questions in body text, examples, call-to-action patterns."""
    # Questions in body (not in headings)
    body_lines = [line for line in content.split('\n') if not line.strip().startswith('#')]
    body_text = '\n'.join(body_lines)
    questions_in_text = len(re.findall(r'[^#]\?', body_text))

    # Example markers
    example_patterns = [
        r'(?i)\bfor example\b', r'(?i)\bfor instance\b', r'(?i)\bsuch as\b',
        r'(?i)\bconsider\b', r'(?i)\blet\'s say\b', r'(?i)\bimagine\b',
        r'(?i)\bhere\'s (?:an|a) example\b',
    ]
    example_count = sum(len(re.findall(p, content)) for p in example_patterns)

    return {
        'questions_in_text': questions_in_text,
        'example_count': example_count,
    }


# ---------------------------------------------------------------------------
# NEW: AI citation readiness
# ---------------------------------------------------------------------------


def analyze_ai_citation_readiness(content: str, headings_info: dict[str, Any],
                                  faq_info: dict[str, Any],
                                  language: str = 'en') -> dict[str, Any]:
    """Assess evidence-backed reuse readiness without fixed passage lengths."""
    section_pattern = re.compile(
        r'^##\s+(.+?)\s*$\n(.*?)(?=^##\s+|\Z)',
        re.MULTILINE | re.DOTALL,
    )
    sections = section_pattern.findall(content)
    evidence_backed_sections = 0
    self_contained_sections = 0
    for heading, section in sections:
        has_source = bool(re.search(r'\[[^\]]+\]\(https?://[^)]+\)', section))
        has_evidence_marker = bool(re.search(
            r'(?:ORIGINAL DATA|PERSONAL EXPERIENCE|UNIQUE INSIGHT)',
            section,
            re.IGNORECASE,
        ))
        has_definition = bool(re.search(
            r'\*\*[^*]+\*\*\s*(?:is|are|refers to|means)',
            section,
            re.IGNORECASE,
        ))
        has_specific_support = bool(re.search(r'\b\d+(?:\.\d+)?%?\b', section))
        if has_source or has_evidence_marker:
            evidence_backed_sections += 1
        if section.strip() and (has_source or has_evidence_marker or has_definition) and (
            has_specific_support or has_definition
        ):
            self_contained_sections += 1

    # Q&A detection: question headings followed by direct answers
    qa_pairs = 0
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if re.match(r'^#{2,4}\s+.+\?', line):
            # Check if next non-empty line starts with a direct statement
            for j in range(i + 1, min(i + 5, len(lines))):
                if lines[j].strip():
                    if not lines[j].strip().startswith('#'):
                        qa_pairs += 1
                    break

    # Entity clarity: detect defined terms (bold terms followed by explanations)
    entity_definitions = len(re.findall(r'\*\*[^*]+\*\*\s*(?:is|are|refers to|means)', content))

    # Extraction-friendly structures
    profile = LANGUAGE_PROFILES.get(language, LANGUAGE_PROFILES['en'])
    summary_pattern = '|'.join(profile['summary_labels'])
    has_tldr = bool(re.search(rf'(?i)(?:{summary_pattern})', content))
    table_count = len(re.findall(r'^\|.+\|$', content, re.MULTILINE))
    list_count = len(re.findall(r'^[\s]*[-*+]\s', content, re.MULTILINE))

    # AI crawler accessibility: inspect actual meta / robots directives only.
    has_robots_meta = bool(re.search(
        r'(?is)<meta[^>]+name=["\']robots["\'][^>]+content=["\'][^"\']*(?:noindex|noai)[^"\']*["\']',
        content,
    ))
    intro = re.split(r'^##\s+', content, maxsplit=1, flags=re.MULTILINE)[0]
    purpose_statement = bool(re.search(r'[A-Za-z]{3,}', intro))
    relevant_media_count = (
        len(re.findall(r'!\[[^\]]+\]\([^)]+\)', content))
        + len(re.findall(r'<(?:img|figure|svg)\b', content, re.IGNORECASE))
    )

    return {
        # Compatibility alias: now counts evidence-backed, self-contained
        # sections rather than passages in a prescribed word-count band.
        'citable_passages': self_contained_sections,
        'self_contained_sections': self_contained_sections,
        'evidence_backed_sections': evidence_backed_sections,
        'section_count': len(sections),
        'qa_pairs': qa_pairs,
        'entity_definitions': entity_definitions,
        'has_tldr': has_tldr,
        'table_count': table_count,
        'list_count': list_count,
        'has_robots_restriction': has_robots_meta,
        'purpose_statement': purpose_statement,
        'relevant_media_count': relevant_media_count,
    }


# ---------------------------------------------------------------------------
# NEW: OG / social meta tags
# ---------------------------------------------------------------------------


def analyze_social_meta(content: str, frontmatter: dict[str, Any]) -> dict[str, Any]:
    """Detect Open Graph and social media meta tags."""
    og_tags = re.findall(r'(?:og:|twitter:)\w+', content)

    # Also check frontmatter for common social fields
    social_fields = ['image', 'og_image', 'ogImage', 'twitter_image',
                     'social_image', 'thumbnail', 'cover']
    has_social_image = any(f in frontmatter for f in social_fields)

    return {
        'og_tags_found': len(og_tags),
        'has_social_image': has_social_image,
        'social_fields_in_frontmatter': [f for f in social_fields if f in frontmatter],
    }


# ---------------------------------------------------------------------------
# NEW: Structured data signals (tables, lists)
# ---------------------------------------------------------------------------


def analyze_structured_data(content: str) -> dict[str, Any]:
    """Detect tables, ordered/unordered lists, and other structured elements."""
    table_rows = len(re.findall(r'^\|.+\|$', content, re.MULTILINE))
    tables = 0
    if table_rows > 0:
        # Estimate number of tables (each table has at least a header separator row)
        tables = len(re.findall(r'^\|[-:| ]+\|$', content, re.MULTILINE))

    unordered_items = len(re.findall(r'^[\s]*[-*+]\s', content, re.MULTILINE))
    ordered_items = len(re.findall(r'^[\s]*\d+\.\s', content, re.MULTILINE))
    code_blocks = len(re.findall(r'```', content)) // 2
    blockquotes = len(re.findall(r'^>\s', content, re.MULTILINE))

    return {
        'table_count': tables,
        'table_rows': table_rows,
        'unordered_list_items': unordered_items,
        'ordered_list_items': ordered_items,
        'code_blocks': code_blocks,
        'blockquotes': blockquotes,
    }


# ---------------------------------------------------------------------------
# Scoring: 5-category, 100-point system
# ---------------------------------------------------------------------------

_TOPIC_STOPWORDS = {
    'about', 'after', 'also', 'and', 'are', 'but', 'for', 'from', 'have',
    'how', 'into', 'its', 'not', 'that', 'the', 'their', 'this', 'with',
    'what', 'when', 'where', 'which', 'why', 'your',
}


def _topic_terms(value: str) -> set[str]:
    """Return normalized topic terms for purpose-consistency checks."""
    return {
        token
        for token in re.findall(r"[A-Za-z0-9][A-Za-z0-9'-]*", value.lower())
        if token not in _TOPIC_STOPWORDS and not token.isdigit()
    }


def _detect_content_type(frontmatter: dict[str, Any], headings_info: dict[str, Any],
                         content: str) -> str:
    """Guess the content type from frontmatter or content patterns."""
    category = frontmatter.get('category', '').lower()
    title = frontmatter.get('title', '').lower()
    content_type = frontmatter.get('type', '').lower()

    if content_type and content_type in CONTENT_TYPE_BENCHMARKS:
        return content_type
    if 'guide' in title or 'guide' in category:
        return 'guide'
    if 'how to' in title or 'how-to' in category:
        return 'how-to'
    if re.search(r'^\d+\s', title) or 'listicle' in category:
        return 'listicle'
    if 'review' in title or 'review' in category:
        return 'review'
    if 'case study' in title or 'case-study' in category:
        return 'case-study'
    if 'opinion' in category:
        return 'opinion'
    if 'news' in category:
        return 'news'
    return 'default'


def calculate_score(analysis: dict[str, Any]) -> dict[str, Any]:
    """Calculate the 5-category, 100-point quality score."""
    issues: list[dict[str, Any]] = []
    category_details: dict[str, dict[str, Any]] = {}

    # ===================================================================
    # CONTENT QUALITY (30 pts)
    # ===================================================================
    cq = 0
    cq_breakdown: dict[str, Any] = {}

    # Coverage / comprehensiveness: 7 pts. Word count is reported for context,
    # never used as a quality target or scoring shortcut.
    headings = analysis['headings']
    citations = analysis['citations']
    engagement = analysis['engagement']
    depth_score = 0
    if headings['h2_count'] >= 1:
        depth_score += 2
    if headings['h2_count'] >= 3:
        depth_score += 1
    if citations['inline_citations'] + citations['paren_citations'] >= 1:
        depth_score += 2
    if engagement['example_count'] >= 1:
        depth_score += 1
    if analysis['structured_data']['table_count'] >= 1 or (
        analysis['structured_data']['unordered_list_items']
        + analysis['structured_data']['ordered_list_items']
    ) >= 3:
        depth_score += 1
    if depth_score < 3:
        issues.append({
            'category': 'content',
            'severity': 'high',
            'issue': 'Coverage is thin: add missing subtopics, evidence, or useful examples for the reader intent',
        })
    cq += depth_score
    cq_breakdown['depth'] = depth_score

    # Readability: 7 pts
    # Default band: Flesch Ease 60-70 (Grade 7-8)
    # Persona bands: Consumer 60-80, Professional 50-60, Technical 30-50
    readability = analysis['readability']
    reading_ease = readability.get(
        'reading_ease', readability.get('flesch_reading_ease', 50)
    )
    reading_model = readability.get('reading_model', 'flesch')
    if reading_model == 'atesman' and 50 <= reading_ease <= 69:
        read_score = 7
    elif reading_model == 'atesman' and 30 <= reading_ease <= 89:
        read_score = 5
    elif reading_model == 'atesman' and 0 <= reading_ease <= 100:
        read_score = 3
    elif 60 <= reading_ease <= 70:
        read_score = 7
    elif 55 <= reading_ease <= 75:
        read_score = 5
    elif 45 <= reading_ease <= 80:
        read_score = 3
    else:
        read_score = 1
        issues.append({'category': 'content', 'severity': 'medium',
                       'issue': f'Flesch reading ease ({reading_ease}) outside acceptable range (55-75)'})
    cq += read_score
    cq_breakdown['readability'] = read_score

    # Originality / differentiated evidence: 5 pts
    orig = analysis['originality']
    orig_score = min(orig.get('evidence_marker_count', 0) * 2, 4)
    if orig.get('methodology_count', 0) > 0:
        orig_score = min(5, orig_score + 1)
    elif citations['unique_sources'] >= 2 and engagement['example_count'] >= 1:
        # Neutral explainers can demonstrate value through synthesis and examples.
        orig_score = max(orig_score, 3)
    if orig_score == 0:
        issues.append({'category': 'content', 'severity': 'medium',
                       'issue': 'No differentiated evidence or analysis found - add original data, a sourced synthesis, a case example, or a clearly labeled unique insight'})
    if orig.get('unsupported_experience_claims', 0) > 0:
        issues.append({
            'category': 'content',
            'severity': 'high',
            'issue': 'First-hand testing claims need supporting methodology, measurements, or evidence',
        })
    cq += orig_score
    cq_breakdown['originality'] = orig_score

    # Logical structure: 4 pts
    struct_score = 0
    if headings['h2_count'] >= 3:
        struct_score += 2
    elif headings['h2_count'] >= 1:
        struct_score += 1
    else:
        issues.append({'category': 'content', 'severity': 'high',
                       'issue': 'No H2 headings - add section headings for structure'})
    if headings['hierarchy_clean']:
        struct_score += 1
    else:
        issues.append({'category': 'content', 'severity': 'medium',
                       'issue': 'Heading hierarchy has skips (e.g., H2 to H4)'})
    # A single H1 provides a clear document-level topic without relying on
    # paragraph-length thresholds.
    if headings['h1_count'] == 1:
        struct_score += 1
    cq += struct_score
    cq_breakdown['structure'] = struct_score

    # Reader utility elements: 4 pts. Questions are not a scoring requirement.
    eng_score = 0
    if engagement['example_count'] >= 2:
        eng_score += 2
    elif engagement['example_count'] >= 1:
        eng_score += 1
    ai_ready = analysis['ai_citation_readiness']
    if ai_ready['has_tldr']:
        eng_score += 1
    if analysis['structured_data']['table_count'] >= 1:
        eng_score += 1
    elif analysis['structured_data']['unordered_list_items'] + analysis['structured_data']['ordered_list_items'] >= 3:
        eng_score += 1
    eng_score = min(eng_score, 4)
    if eng_score < 2:
        issues.append({'category': 'content', 'severity': 'low',
                       'issue': 'Reader utility is limited - add a relevant example, summary, table, or decision aid when useful'})
    cq += eng_score
    cq_breakdown['engagement'] = eng_score

    # Grammar / clarity: 3 pts. Authorship-style diagnostics never affect score.
    sentences = analysis['sentences']
    transitions = analysis.get('transition_words', {})
    gram_score = 1 if sentences['count'] > 0 else 0
    if sentences['very_long_count'] == 0:
        gram_score += 1
    if sentences['very_long_count'] > 0:
        issues.append({'category': 'content', 'severity': 'low',
                       'issue': f'{sentences["very_long_count"]} sentences over 40 words - consider splitting'})
    transition_pct = transitions.get('transition_pct', 0)
    if sentences['count'] > 0 and 8 <= sentences['avg_length'] <= 30:
        gram_score += 1
    if transition_pct > 50:
        issues.append({'category': 'content', 'severity': 'low',
                       'issue': f'Transition words occur in {transition_pct}% of sentences - review for repetitive connective phrasing'})
    gram_score = min(gram_score, 3)
    cq += gram_score
    cq_breakdown['grammar_antipattern'] = gram_score

    cq = min(cq, 30)
    category_details['content_quality'] = {'score': cq, 'max': 30, 'breakdown': cq_breakdown}

    # ===================================================================
    # SEO OPTIMIZATION (25 pts)
    # ===================================================================
    seo = 0
    seo_breakdown: dict[str, Any] = {}
    fm = analysis['frontmatter']

    # Title clarity and purpose fit: 4 pts. Character bands, sentiment, power
    # words, and exact-match keyword placement do not earn points.
    title = fm.get('title', '')
    title_score = 0
    body = analysis.get('_body_text', '')
    heading_text = ' '.join(h['text'] for h in headings['headings'])
    title_terms = _topic_terms(title)
    body_terms = _topic_terms(body)
    heading_terms = _topic_terms(heading_text)
    if title:
        title_score += 1
        if title.strip().lower() not in {'home', 'blog', 'post', 'untitled'}:
            title_score += 1
        if title_terms & body_terms:
            title_score += 1
        if title_terms & heading_terms:
            title_score += 1
    if not title:
        issues.append({'category': 'seo', 'severity': 'high',
                       'issue': 'Missing title in frontmatter'})
    elif not (title_terms & body_terms):
        issues.append({'category': 'seo', 'severity': 'medium',
                       'issue': 'Title does not clearly match the visible page topic'})
    seo += title_score
    seo_breakdown['title'] = title_score

    # Heading hierarchy and reader navigation: 5 pts.
    heading_score = 0
    if headings['h1_count'] == 1:
        heading_score += 2
    elif headings['h1_count'] == 0 and title:
        heading_score += 2  # Frontmatter title can serve as the document H1.
    if headings['total'] > 0 and headings['hierarchy_clean']:
        heading_score += 2
    heading_values = [h['text'].strip().lower() for h in headings['headings']]
    if heading_values and all(heading_values) and len(heading_values) == len(set(heading_values)):
        heading_score += 1
    heading_score = min(heading_score, 5)
    seo += heading_score
    seo_breakdown['headings'] = heading_score

    # Semantic topic consistency: 4 pts. Keep the compatibility field name,
    # but ignore exact-match placement quotas.
    keyword_score = 0
    if title_terms & body_terms:
        keyword_score += 2
    if title_terms & heading_terms:
        keyword_score += 1
    if heading_terms & body_terms:
        keyword_score += 1
    keyword_score = min(keyword_score, 4)
    seo += keyword_score
    seo_breakdown['keyword_placement'] = keyword_score

    # Internal linking (3-10 contextual): 4 pts
    links = analysis['links']
    int_score = 0
    ic = links['internal_count']
    if 3 <= ic <= 10:
        int_score = 4
    elif ic >= 1:
        int_score = 2
    else:
        issues.append({'category': 'seo', 'severity': 'high',
                       'issue': 'No internal links - add 3-10 contextual internal links'})
    if links['bad_anchor_texts']:
        int_score = max(int_score - 1, 0)
        issues.append({'category': 'seo', 'severity': 'low',
                       'issue': f'Bad anchor texts found: {links["bad_anchor_texts"]}'})
    seo += int_score
    seo_breakdown['internal_linking'] = int_score

    # Meta description accuracy and visible-content consistency: 3 pts.
    desc = fm.get('description', fm.get('meta_description', ''))
    meta_score = 0
    if desc:
        meta_score += 1
        desc_terms = _topic_terms(desc)
        if desc_terms & (title_terms | heading_terms):
            meta_score += 1
        if desc_terms & body_terms:
            meta_score += 1
    else:
        issues.append({'category': 'seo', 'severity': 'high',
                       'issue': 'Missing meta description in frontmatter'})
    seo += meta_score
    seo_breakdown['meta_description'] = meta_score

    # External linking (tier 1-3): 2 pts
    ext_score = 0
    if links['external_count'] >= 2:
        ext_score += 1
    tier_ext = links.get('external_tier_counts', {})
    if tier_ext.get(1, 0) >= 1 or tier_ext.get(2, 0) >= 1:
        ext_score += 1
    seo += ext_score
    seo_breakdown['external_linking'] = ext_score

    # URL structure: 3 pts (from frontmatter slug)
    slug = fm.get('slug', fm.get('url', ''))
    url_score = 0
    if slug:
        if len(slug) <= 60:
            url_score += 1
        if '-' in slug and ' ' not in slug:
            url_score += 1
        if not re.search(r'\d{8,}', slug):  # No long numeric strings
            url_score += 1
    else:
        url_score = 1  # Partial credit; many static site generators auto-generate
    url_score = min(url_score, 3)
    seo += url_score
    seo_breakdown['url_structure'] = url_score

    seo = min(seo, 25)
    category_details['seo_optimization'] = {'score': seo, 'max': 25, 'breakdown': seo_breakdown}

    # ===================================================================
    # E-E-A-T SIGNALS (15 pts)
    # ===================================================================
    eeat = 0
    eeat_breakdown: dict[str, Any] = {}

    # Author attribution: 4 pts
    author = fm.get('author', fm.get('authors', ''))
    author_score = 0
    if author and author.lower() not in ('admin', 'administrator', 'staff', 'team', ''):
        author_score = 4
    elif author:
        author_score = 1
        issues.append({'category': 'eeat', 'severity': 'medium',
                       'issue': f'Generic author name "{author}" - use a real person name'})
    else:
        issues.append({'category': 'eeat', 'severity': 'high',
                       'issue': 'No author attribution in frontmatter'})
    eeat += author_score
    eeat_breakdown['author'] = author_score

    # Source citations: 4 pts (tier-aware)
    cit = analysis['citations']
    cit_score = 0
    total_citations = cit['inline_citations'] + cit['paren_citations']
    if total_citations >= 5:
        cit_score += 2
    elif total_citations >= 2:
        cit_score += 1
    # Tier bonus
    tier_c = cit.get('tier_counts', {})
    if tier_c.get(1, 0) >= 1:
        cit_score += 2
    elif tier_c.get(2, 0) >= 1:
        cit_score += 1
    cit_score = min(cit_score, 4)
    if total_citations == 0:
        issues.append({'category': 'eeat', 'severity': 'high',
                       'issue': 'No source citations - add inline citations to credible sources'})
    eeat += cit_score
    eeat_breakdown['citations'] = cit_score

    # Trust indicators: 4 pts (about/contact links, editorial mentions)
    trust_score = 0
    body = analysis.get('_body_text', '')
    language = analysis.get('language', 'en')
    profile = LANGUAGE_PROFILES.get(language, LANGUAGE_PROFILES['en'])
    if any(re.search(pattern, body, re.IGNORECASE)
           for pattern in profile['about_patterns']):
        trust_score += 2
    if any(re.search(pattern, body, re.IGNORECASE)
           for pattern in profile['contact_patterns']):
        trust_score += 1
    if re.search(r'(?i)\b(?:editorial|reviewed by|fact.?check|editor)\b', body):
        trust_score += 1
    trust_score = min(trust_score, 4)
    eeat += trust_score
    eeat_breakdown['trust'] = trust_score

    # Evidence basis: 3 pts. Never require or invent first-person experience.
    orig = analysis['originality']
    exp_score = 0
    if orig.get('methodology_count', 0) >= 1 and orig.get('evidence_marker_count', 0) >= 1:
        exp_score = 3
    elif cit['unique_sources'] >= 3 and cit['unsourced_statistics'] == 0:
        exp_score = 3
    elif cit['unique_sources'] >= 1:
        exp_score = 2
    elif orig.get('evidence_marker_count', 0) >= 1:
        exp_score = 1
    if exp_score == 0:
        issues.append({'category': 'eeat', 'severity': 'medium',
                       'issue': 'Evidence basis is unclear - add verifiable sources, transparent methodology, or clearly supported original material'})
    eeat += exp_score
    eeat_breakdown['experience'] = exp_score

    eeat = min(eeat, 15)
    category_details['eeat_signals'] = {'score': eeat, 'max': 15, 'breakdown': eeat_breakdown}

    # ===================================================================
    # TECHNICAL ELEMENTS (15 pts)
    # ===================================================================
    tech = 0
    tech_breakdown: dict[str, Any] = {}

    # Schema markup (JSON-LD): 4 pts
    schema = analysis['schema']
    schema_score = 0
    if schema['has_blogposting']:
        schema_score += 2
    if schema['has_person']:
        schema_score += 1
    if schema.get('has_organization') or schema.get('has_breadcrumblist'):
        schema_score += 1
    if schema['schema_count'] == 0:
        # Check if there are any schema signals at all
        if re.search(r'(?i)json-ld|structured.?data|schema\.org', analysis.get('_raw_content', '')):
            schema_score = 1
    schema_score = min(schema_score, 4)
    if schema_score == 0:
        issues.append({'category': 'technical', 'severity': 'medium',
                       'issue': 'No JSON-LD schema markup detected - add BlogPosting schema'})
    tech += schema_score
    tech_breakdown['schema'] = schema_score

    # Image optimization (alt text, formats): 3 pts
    images = analysis['images']
    img_score = 0
    if images['count'] > 0:
        alt_ratio = images['with_alt_text'] / images['count']
        if alt_ratio == 1.0:
            img_score += 2
        elif alt_ratio >= 0.8:
            img_score += 1
        else:
            issues.append({'category': 'technical', 'severity': 'medium',
                           'issue': f'{images["without_alt_text"]} images missing alt text'})
        if images['modern_format_count'] > 0:
            img_score += 1
    else:
        img_score = 1  # No images is OK for some content types
    img_score = min(img_score, 3)
    tech += img_score
    tech_breakdown['images'] = img_score

    # Structured data (tables, lists): 2 pts
    struct_data = analysis['structured_data']
    sdata_score = 0
    if struct_data['table_count'] >= 1:
        sdata_score += 1
    if struct_data['unordered_list_items'] + struct_data['ordered_list_items'] >= 3:
        sdata_score += 1
    sdata_score = min(sdata_score, 2)
    tech += sdata_score
    tech_breakdown['structured_data'] = sdata_score

    # Page speed signals: 2 pts
    speed_score = 0
    # Check for lazy loading
    if re.search(r'loading=["\']lazy["\']', analysis.get('_raw_content', '')):
        speed_score += 1
    # Check for modern image formats or optimization attributes
    if images.get('modern_format_count', 0) > 0:
        speed_score += 1
    elif images['count'] == 0:
        speed_score = 1  # No images to slow things down
    speed_score = min(speed_score, 2)
    tech += speed_score
    tech_breakdown['page_speed'] = speed_score

    # Mobile-friendly: 2 pts. Score observable rendering signals, never prose
    # length.
    mobile_score = 0
    raw_content = analysis.get('_raw_content', '')
    fixed_width_layout = bool(re.search(
        r'style=["\'][^"\']*\bwidth\s*:\s*(?:1\d{3}|[2-9]\d{3,})px',
        raw_content,
        re.IGNORECASE,
    ))
    if not fixed_width_layout:
        mobile_score += 1
    if re.search(
        r'srcset|<picture|name=["\']viewport["\']',
        raw_content,
        re.IGNORECASE,
    ):
        mobile_score += 1
    elif images['count'] == 0 and not re.search(
        r'<(?:iframe|video)\b', raw_content, re.IGNORECASE
    ):
        mobile_score += 1
    mobile_score = min(mobile_score, 2)
    tech += mobile_score
    tech_breakdown['mobile'] = mobile_score

    # OG/social meta tags: 2 pts
    social = analysis['social_meta']
    social_score = 0
    if social['og_tags_found'] >= 2:
        social_score += 1
    if social['has_social_image']:
        social_score += 1
    elif any(f in fm for f in ('image', 'thumbnail', 'cover')):
        social_score += 1
    social_score = min(social_score, 2)
    tech += social_score
    tech_breakdown['social_meta'] = social_score

    tech = min(tech, 15)
    category_details['technical_elements'] = {'score': tech, 'max': 15, 'breakdown': tech_breakdown}

    # ===================================================================
    # AI CITATION READINESS (15 pts)
    # ===================================================================
    ai = 0
    ai_breakdown: dict[str, Any] = {}
    ai_ready = analysis['ai_citation_readiness']
    cit = analysis['citations']

    # Evidence-backed, self-contained sections: 4 pts. No fixed word band.
    cite_score = 0
    supported_sections = ai_ready.get('evidence_backed_sections', 0)
    self_contained = ai_ready.get('self_contained_sections', 0)
    if supported_sections >= 3 and self_contained >= 2 and cit['unsourced_statistics'] == 0:
        cite_score = 4
    elif supported_sections >= 2 and self_contained >= 1:
        cite_score = 3
    elif supported_sections >= 1:
        cite_score = 2
    elif cit['inline_citations'] >= 1:
        cite_score = 1
    else:
        issues.append({'category': 'ai_citation', 'severity': 'medium',
                       'issue': 'No evidence-backed sections found - support reusable claims with clear sources or transparent original evidence'})
    ai += cite_score
    ai_breakdown['citability'] = cite_score

    # Purpose fit: 3 pts. Declarative headings and optional FAQs are valid.
    purpose_score = 0
    if ai_ready.get('purpose_statement'):
        purpose_score += 1
    if headings['hierarchy_clean'] and headings['h2_count'] >= 1:
        purpose_score += 1
    if engagement['example_count'] >= 1 or ai_ready.get('has_tldr'):
        purpose_score += 1
    ai += purpose_score
    ai_breakdown['purpose_fit'] = purpose_score

    # Entity clarity: 3 pts
    ent_score = 0
    ed = ai_ready['entity_definitions']
    if ed >= 3:
        ent_score = 3
    elif ed >= 1:
        ent_score = 2
    else:
        ent_score = 0
        issues.append({'category': 'ai_citation', 'severity': 'low',
                       'issue': 'No entity definitions found - use **term** is/are patterns'})
    ai += ent_score
    ai_breakdown['entity_clarity'] = ent_score

    # Reader-useful structure: 3 pts. No single format is mandatory.
    ext_score = 0
    if ai_ready['has_tldr'] or engagement['example_count'] >= 1:
        ext_score += 1
    if struct_data['table_count'] >= 1:
        ext_score += 1
    elif struct_data['unordered_list_items'] + struct_data['ordered_list_items'] >= 3:
        ext_score += 1
    if ai_ready.get('relevant_media_count', 0) >= 1:
        ext_score += 1
    ext_score = min(ext_score, 3)
    ai += ext_score
    ai_breakdown['extraction'] = ext_score

    # AI crawler accessibility: 2 pts
    crawl_score = 2  # Default: accessible
    if ai_ready['has_robots_restriction']:
        crawl_score = 0
        issues.append({'category': 'ai_citation', 'severity': 'medium',
                       'issue': 'Robots/noai restriction detected - may block AI crawlers'})
    ai += crawl_score
    ai_breakdown['crawler_access'] = crawl_score

    ai = min(ai, 15)
    category_details['ai_citation_readiness'] = {'score': ai, 'max': 15, 'breakdown': ai_breakdown}

    # ===================================================================
    # TOTAL
    # ===================================================================
    total = cq + seo + eeat + tech + ai

    if total >= 90:
        rating = 'Exceptional'
    elif total >= 80:
        rating = 'Strong'
    elif total >= 70:
        rating = 'Acceptable'
    elif total >= 60:
        rating = 'Below Standard'
    else:
        rating = 'Rewrite'

    # Sort issues by severity
    severity_order = {'high': 0, 'medium': 1, 'low': 2}
    issues.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 3))

    return {
        'total': total,
        'rating': rating,
        'methodology': 'internal_editorial_readiness_heuristic',
        'calibrated_probability': False,
        'categories': {
            'content_quality': cq,
            'seo_optimization': seo,
            'eeat_signals': eeat,
            'technical_elements': tech,
            'ai_citation_readiness': ai,
        },
        'category_details': category_details,
        'issues': issues,
        'content_type': _detect_content_type(analysis['frontmatter'], analysis['headings'], ''),
    }


# ---------------------------------------------------------------------------
# File analysis orchestrator
# ---------------------------------------------------------------------------


def analyze_file(file_path: str) -> dict[str, Any]:
    """Analyze a single blog file with all analyzers."""
    path = Path(file_path)
    if not path.exists():
        return {'error': f'File not found: {file_path}'}

    try:
        content = _read_safely(path)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        return {'error': f'Could not analyze {file_path}: {exc}'}
    if path.suffix.lower() == '.html':
        frontmatter, body = extract_html_for_analysis(content)
    else:
        frontmatter = extract_frontmatter(content)
        body = strip_frontmatter(content)
    language = _detect_language(frontmatter, body)

    # Strip markdown formatting for plain-text analysis
    plain_text = _plain_text_for_analysis(body)

    headings_info = analyze_headings(body)
    sentences_info = analyze_sentences(plain_text)
    faq_info = analyze_faq(body)

    ai_citation_readiness = analyze_ai_citation_readiness(
        body, headings_info, faq_info, language
    )
    if path.suffix.lower() == '.html':
        ai_citation_readiness['has_robots_restriction'] = bool(re.search(
            r'(?is)<meta[^>]+name=["\']robots["\'][^>]+content=["\'][^"\']*(?:noindex|noai)[^"\']*["\']',
            content,
        ))

    analysis: dict[str, Any] = {
        'file': str(path),
        'format': path.suffix,
        'language': language,
        'methodology': {
            'name': 'internal editorial readiness heuristic',
            'calibrated_probability': False,
            'authorship_classifier': False,
        },
        'frontmatter': frontmatter,
        'headings': headings_info,
        'paragraphs': analyze_paragraphs(body),
        'images': analyze_images(content),
        'charts': analyze_charts(content),
        'citations': analyze_citations(body),
        'faq': faq_info,
        'freshness': analyze_freshness(frontmatter),
        'self_promotion': analyze_self_promotion(body),
        'readability': analyze_readability(plain_text, language),
        'sentences': sentences_info,
        'ai_signals': analyze_ai_signals(plain_text, sentences_info),
        'passive_voice': analyze_passive_voice(plain_text),
        'transition_words': analyze_transition_words(plain_text),
        'ai_trigger_words': analyze_ai_trigger_words(plain_text),
        'schema': analyze_schema(content),
        'links': analyze_links(body),
        'originality': analyze_originality(body, language),
        'engagement': analyze_engagement(body),
        'ai_citation_readiness': ai_citation_readiness,
        'social_meta': analyze_social_meta(content, frontmatter),
        'structured_data': analyze_structured_data(body),
        # Internal refs used by scoring (not included in output)
        '_body_text': body,
        '_raw_content': content,
    }

    analysis['score'] = calculate_score(analysis)

    # Remove internal-only keys before returning
    analysis.pop('_body_text', None)
    analysis.pop('_raw_content', None)

    return analysis


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------


def _format_markdown(result: dict[str, Any]) -> str:
    """Format analysis result as a human-readable markdown report."""
    if 'error' in result:
        return f"## Error\n\n{result['error']}"

    score = result['score']
    lines: list[str] = []
    filename = Path(result['file']).name

    lines.append(f"## Blog Quality Report: {filename}")
    lines.append('')
    lines.append(f"### Overall Score: {score['total']}/100 - {score['rating']}")
    lines.append('')

    # Category table
    lines.append('| Category | Score | Max |')
    lines.append('|----------|------:|----:|')
    cat_names = {
        'content_quality': 'Content Quality',
        'seo_optimization': 'SEO Optimization',
        'eeat_signals': 'E-E-A-T Signals',
        'technical_elements': 'Technical Elements',
        'ai_citation_readiness': 'AI Citation Readiness',
    }
    cat_maxes = {
        'content_quality': 30,
        'seo_optimization': 25,
        'eeat_signals': 15,
        'technical_elements': 15,
        'ai_citation_readiness': 15,
    }
    for key, label in cat_names.items():
        s = score['categories'].get(key, 0)
        m = cat_maxes[key]
        lines.append(f'| {label} | {s} | {m} |')
    lines.append('')

    # Editorial style diagnostics
    ai_sig = result.get('ai_signals', {})
    lines.append('### Editorial Style Diagnostics')
    lines.append('- These descriptive observations do not infer authorship and do not affect the score.')
    lines.append(f'- Sentence-length variation: {ai_sig.get("burstiness", 0)}')
    lines.append(f'- Configured style phrases: {ai_sig.get("ai_phrase_count", 0)} found')
    lines.append(f'- Vocabulary diversity sample: {ai_sig.get("vocabulary_diversity_ttr", 0)}')
    lines.append('')

    # Readability
    read = result.get('readability', {})
    passive = result.get('passive_voice', {})
    transitions = result.get('transition_words', {})
    ai_triggers = result.get('ai_trigger_words', {})
    sents = result.get('sentences', {})
    lines.append('### Readability')
    lines.append(f'- Flesch Reading Ease: {read.get("flesch_reading_ease", "N/A")} (target: 60-70)')
    if read.get('flesch_kincaid_grade'):
        lines.append(f'- Flesch-Kincaid Grade: {read.get("flesch_kincaid_grade")} (target: 7-8)')
    lines.append(f'- Reading time: {read.get("reading_time_minutes", "N/A")} minutes')
    lines.append(f'- Passive voice: {passive.get("passive_pct", "N/A")}% (descriptive only)')
    lines.append(f'- Transition words: {transitions.get("transition_pct", "N/A")}% (target: 20-30%)')
    lines.append(f'- Project style-list terms: {ai_triggers.get("per_1k", "N/A")}/1K (advisory)')
    lines.append(f'- Sentences over 20 words: {sents.get("over_20_pct", "N/A")}% (target: ≤25%)')
    if ai_triggers.get('found'):
        trigger_list = ', '.join(f'{t["word"]}({t["count"]})' for t in ai_triggers['found'][:5])
        lines.append(f'- Trigger words found: {trigger_list}')
    if read.get('estimated'):
        lines.append('- *(Estimated - install textstat for accurate metrics)*')
    lines.append('')

    # Issues
    issues = score.get('issues', [])
    if issues:
        lines.append('### Issues')
        for issue in issues:
            sev = issue.get('severity', 'low').upper()
            lines.append(f'- [{sev}] {issue["issue"]}')
        lines.append('')
    else:
        lines.append('### Issues')
        lines.append('No issues detected.')
        lines.append('')

    # Content info
    lines.append('### Content Info')
    lines.append(f'- Word count: {result["paragraphs"]["total_word_count"]}')
    lines.append(f'- Content type: {score.get("content_type", "default")}')
    lines.append(f'- Sentences: {result["sentences"]["count"]}')
    lines.append(f'- Headings: {result["headings"]["total"]}')
    lines.append(f'- Internal links: {result["links"]["internal_count"]}')
    lines.append(f'- External links: {result["links"]["external_count"]}')
    lines.append(f'- Images: {result["images"]["count"]}')
    lines.append('')

    return '\n'.join(lines)


def _format_table(result: dict[str, Any]) -> str:
    """Format analysis result as a compact table."""
    if 'error' in result:
        return f"ERROR: {result['error']}"

    score = result['score']
    filename = Path(result['file']).name
    cats = score['categories']

    lines: list[str] = []
    lines.append(f'{filename}  [{score["total"]}/100 {score["rating"]}]')
    lines.append(f'  Content: {cats["content_quality"]}/30  '
                 f'SEO: {cats["seo_optimization"]}/25  '
                 f'E-E-A-T: {cats["eeat_signals"]}/15  '
                 f'Tech: {cats["technical_elements"]}/15  '
                 f'AI-Cite: {cats["ai_citation_readiness"]}/15')

    issues = score.get('issues', [])
    high_issues = [i for i in issues if i.get('severity') == 'high']
    if high_issues:
        lines.append(f'  HIGH: {"; ".join(i["issue"] for i in high_issues[:3])}')

    return '\n'.join(lines)


def _format_fix(result: dict[str, Any]) -> str:
    """Output specific, actionable fixes prioritized by impact."""
    if 'error' in result:
        return f"ERROR: {result['error']}"

    score = result['score']
    issues = score.get('issues', [])
    filename = Path(result['file']).name

    lines: list[str] = []
    lines.append(f"Fixes for {filename} (Score: {score['total']}/100)")
    lines.append('=' * 60)

    if not issues:
        lines.append('No issues found - content meets all quality checks.')
        return '\n'.join(lines)

    for i, issue in enumerate(issues, 1):
        sev = issue.get('severity', 'low').upper()
        cat = issue.get('category', '').replace('_', ' ').title()
        lines.append(f'{i}. [{sev}] ({cat}) {issue["issue"]}')

    return '\n'.join(lines)


def _format_category_detail(result: dict[str, Any], category: str) -> str:
    """Output detailed breakdown for a single category."""
    if 'error' in result:
        return f"ERROR: {result['error']}"

    score = result['score']
    cat_map = {
        'content': 'content_quality',
        'seo': 'seo_optimization',
        'eeat': 'eeat_signals',
        'technical': 'technical_elements',
        'tech': 'technical_elements',
        'ai': 'ai_citation_readiness',
        'ai_citation': 'ai_citation_readiness',
        'citation': 'ai_citation_readiness',
    }

    cat_key = cat_map.get(category.lower(), category.lower())
    details = score.get('category_details', {}).get(cat_key)

    if not details:
        available = ', '.join(cat_map.keys())
        return f"Unknown category: '{category}'. Available: {available}"

    cat_labels = {
        'content_quality': 'Content Quality',
        'seo_optimization': 'SEO Optimization',
        'eeat_signals': 'E-E-A-T Signals',
        'technical_elements': 'Technical Elements',
        'ai_citation_readiness': 'AI Citation Readiness',
    }

    lines: list[str] = []
    label = cat_labels.get(cat_key, cat_key)
    lines.append(f"{label}: {details['score']}/{details['max']}")
    lines.append('-' * 40)

    breakdown = details.get('breakdown', {})
    for sub_key, sub_score in breakdown.items():
        lines.append(f"  {sub_key.replace('_', ' ').title()}: {sub_score}")

    # Category-specific issues
    cat_issues = [i for i in score.get('issues', []) if i.get('category') == cat_key or
                  i.get('category') == category.lower()]
    if cat_issues:
        lines.append('')
        lines.append('Issues:')
        for issue in cat_issues:
            lines.append(f"  - [{issue['severity'].upper()}] {issue['issue']}")

    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------


def _process_batch(directory: Path, sort_key: str = 'score') -> dict[str, Any]:
    """Analyze all blog files in a directory."""
    results: list[dict[str, Any]] = []
    for ext in ['*.md', '*.mdx', '*.html']:
        for f in directory.glob(ext):
            results.append(analyze_file(str(f)))

    # Sort
    if sort_key == 'score':
        results.sort(key=lambda r: r.get('score', {}).get('total', 0), reverse=True)
    elif sort_key == 'name':
        results.sort(key=lambda r: r.get('file', ''))
    elif sort_key == 'words':
        results.sort(key=lambda r: r.get('paragraphs', {}).get('total_word_count', 0), reverse=True)

    return {'batch': True, 'count': len(results), 'results': results}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(args: argparse.Namespace) -> None:
    """Main execution function."""
    path = Path(args.input)
    fmt = getattr(args, 'format', 'json')
    category = getattr(args, 'category', None)
    fix_mode = getattr(args, 'fix', False)
    sort_key = getattr(args, 'sort', 'score')

    # Batch mode
    if path.is_dir() and getattr(args, 'batch', False):
        batch_result = _process_batch(path, sort_key)

        if fmt == 'markdown':
            for r in batch_result['results']:
                print(_format_markdown(r))
                print('---\n')
        elif fmt == 'table':
            for r in batch_result['results']:
                print(_format_table(r))
            print(f'\nTotal: {batch_result["count"]} files')
        else:
            output = json.dumps(batch_result, indent=2)
            if args.output:
                _safe_write_text(args.output, output)
                print(f'Report saved to {args.output}', file=sys.stderr)
            else:
                print(output)
        return

    # Single file mode
    if not path.is_file():
        error = {'error': f'Path not found or not a file: {args.input}'}
        if fmt == 'json':
            print(json.dumps(error, indent=2))
        else:
            print(f"ERROR: {error['error']}")
        sys.exit(1)

    result = analyze_file(str(path))

    # Category detail mode
    if category:
        print(_format_category_detail(result, category))
        return

    # Fix mode
    if fix_mode:
        print(_format_fix(result))
        return

    # Format output
    if fmt == 'markdown':
        output = _format_markdown(result)
        if args.output:
            _safe_write_text(args.output, output)
            print(f'Report saved to {args.output}', file=sys.stderr)
        else:
            print(output)
    elif fmt == 'table':
        print(_format_table(result))
    else:
        output = json.dumps(result, indent=2)
        if args.output:
            _safe_write_text(args.output, output)
            print(f'Report saved to {args.output}', file=sys.stderr)
        else:
            print(output)


if __name__ == '__main__':
    _print_dependency_notice()

    parser = argparse.ArgumentParser(
        description='Blog Quality Analyzer - 5-category, 100-point scoring system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 analyze_blog.py post.md                          Default JSON output
  python3 analyze_blog.py post.md --format markdown        Markdown report
  python3 analyze_blog.py post.md --format table           Compact table
  python3 analyze_blog.py ./posts --batch --sort score     Batch analysis
  python3 analyze_blog.py post.md --category seo           Single category detail
  python3 analyze_blog.py post.md --fix                    Prioritized fix list

Scoring Categories (100 points):
  Content Quality        30 pts   Depth, readability, originality, structure
  SEO Optimization       25 pts   Title, headings, keywords, linking, meta
  E-E-A-T Signals        15 pts   Author, citations, trust, experience
  Technical Elements     15 pts   Schema, images, structured data, speed
  AI Citation Readiness  15 pts   Citability, Q&A, entities, extraction

Rating Bands:
  90-100  Exceptional    80-89  Strong    70-79  Acceptable
  60-69   Below Standard   <60  Rewrite

Optional dependencies (graceful degradation):
  pip install textstat beautifulsoup4
        """,
    )
    parser.add_argument('--version', action='version', version=f'%(prog)s {_project_version()}')
    parser.add_argument('input', help='Blog file path or directory (with --batch)')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--format', '-f', choices=['json', 'markdown', 'table'],
                        default='json', help='Output format (default: json)')
    parser.add_argument('--batch', action='store_true',
                        help='Analyze all .md/.mdx/.html files in directory')
    parser.add_argument('--sort', choices=['score', 'name', 'words'],
                        default='score', help='Sort order for batch mode (default: score)')
    parser.add_argument('--category', '-c',
                        help='Show detailed breakdown for a single category '
                             '(content, seo, eeat, technical, ai)')
    parser.add_argument('--fix', action='store_true',
                        help='Output prioritized list of specific fixes')

    args = parser.parse_args()

    try:
        main(args)
    except Exception as e:
        print(json.dumps({'error': str(e)}), file=sys.stderr)
        sys.exit(1)
