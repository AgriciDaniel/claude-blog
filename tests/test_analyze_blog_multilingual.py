"""Language profiles for Spanish, Portuguese, Russian and Ukrainian.

Readability expectations are computed by hand in the comments so a change in
the syllable heuristic or in a formula is caught explicitly.
"""

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import analyze_blog


# ---------------------------------------------------------------------------
# Profiles
# ---------------------------------------------------------------------------


def test_every_profile_resolves_every_field_of_the_english_default():
    required = set(analyze_blog.LANGUAGE_PROFILES["en"])
    for code in ("en", "tr", "es", "pt", "ru", "uk"):
        profile = analyze_blog._language_profile(code)
        assert required <= set(profile), code
        assert profile["readability_model"] in analyze_blog.READABILITY_MODELS


def test_turkish_inherits_english_defaults_for_new_fields():
    tr = analyze_blog._language_profile("tr")
    en = analyze_blog.LANGUAGE_PROFILES["en"]
    for field in ("example_patterns", "definition_patterns", "percent_pattern",
                  "topic_token_pattern", "sentence_splitting", "editorial_patterns"):
        assert tr[field] == en[field]
    assert tr["readability_model"] == "atesman"


# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("frontmatter", "expected"),
    [
        ({"lang": "es"}, "es"),
        ({"lang": "es-ES"}, "es"),
        ({"language": "es_MX"}, "es"),
        ({"inLanguage": "pt-BR"}, "pt"),
        ({"lang": "pt-PT"}, "pt"),
        ({"lang": "ru"}, "ru"),
        ({"language": "ru-RU"}, "ru"),
        ({"inLanguage": "uk-UA"}, "uk"),
        ({"lang": "uk"}, "uk"),
        ({"lang": "ua"}, "uk"),
        ({"lang": "Spanish"}, "es"),
        ({"lang": "en-US"}, "en"),
        ({"lang": "tr-TR"}, "tr"),
    ],
)
def test_declared_language_variants(frontmatter, expected):
    language, method = analyze_blog.detect_language_details(frontmatter, "Any body.")
    assert language == expected
    assert method == "declared"


def test_unsupported_declared_language_falls_back_to_english():
    assert analyze_blog.detect_language_details({"lang": "fr-FR"}, "Texte.") == (
        "en", "declared-unsupported",
    )


SPANISH_BODY = (
    "El arbitraje P2P consiste en comprar cripto a un precio y venderla a otro "
    "más alto. Para el comerciante, la diferencia que se ve en el libro no es "
    "el margen real, porque hay comisiones y costes del método de pago. También "
    "hay riesgos: los pagos de terceros pueden borrar en una orden lo que dejaron "
    "muchos ciclos, y por eso conviene medir con cuidado cuándo y cómo se opera."
)
PORTUGUESE_BODY = (
    "O arbitragem P2P consiste em comprar cripto a um preço e vender por outro "
    "mais alto. Para o comerciante, a diferença que se vê no livro não é a margem "
    "real, porque há taxas e custos do método de pagamento. Também há riscos: os "
    "pagamentos de terceiros podem apagar em uma ordem o que muitos ciclos "
    "deixaram, e por isso você deve medir com cuidado quando e como opera."
)
RUSSIAN_BODY = (
    "Арбитраж P2P это покупка криптовалюты по одной цене и продажа по более "
    "высокой. Для торговца разница, которую он видит в стакане, это ещё не "
    "реальная маржа, потому что есть комиссии и расходы на способ оплаты. Также "
    "есть риски: платежи третьих лиц могут уничтожить за одну сделку то, что "
    "принесли многие циклы, и поэтому нужно очень внимательно считать, если вы "
    "работаете каждый день и они тоже."
)
UKRAINIAN_BODY = (
    "Арбітраж P2P це купівля криптовалюти за однією ціною і продаж за вищою. "
    "Для торговця різниця, яку він бачить у стакані, ще не є реальною маржею, "
    "бо є комісії та витрати на спосіб оплати. Також є ризики: платежі третіх "
    "осіб можуть знищити за одну угоду те, що принесли багато циклів, і тому "
    "потрібно дуже уважно рахувати, якщо ви працюєте щодня, а вони також."
)
ENGLISH_BODY = (
    "P2P arbitrage is buying crypto at one price and selling it at a higher one. "
    "For the merchant, the gap that is visible in the order book is not the real "
    "margin, because there are fees and payment method costs. There are also "
    "risks: third-party payments can erase in one order what many cycles earned, "
    "and that is why you should measure carefully when and how you trade."
)


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        (SPANISH_BODY, "es"),
        (PORTUGUESE_BODY, "pt"),
        (RUSSIAN_BODY, "ru"),
        (UKRAINIAN_BODY, "uk"),
    ],
)
def test_undeclared_language_uses_conservative_stopword_fallback(body, expected):
    assert analyze_blog.detect_language_details({}, body) == (expected, "stopwords")


def test_english_and_short_texts_keep_the_english_default():
    assert analyze_blog.detect_language_details({}, ENGLISH_BODY) == ("en", "default")
    short_spanish = "El arbitraje es comprar barato y vender caro."
    assert analyze_blog.detect_language_details({}, short_spanish) == ("en", "default")


def test_acronym_letters_are_not_mistaken_for_portuguese():
    body = "\n".join(f"- [[E-E-A-T note {i}]] and E-E-A-T review" for i in range(12))
    assert analyze_blog.detect_language_details({}, body)[0] == "en"


def test_declaration_wins_over_body_detection():
    assert analyze_blog.detect_language_details({"lang": "en"}, SPANISH_BODY)[0] == "en"


# ---------------------------------------------------------------------------
# Syllables and readability
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("word", "syllables"),
    [
        ("gato", 2), ("bueno", 2), ("día", 2), ("ciudad", 2), ("país", 2),
        ("leer", 2), ("aéreo", 4), ("guion", 1), ("muy", 1), ("hoy", 1),
        ("y", 1), ("mayo", 2), ("Bybit", 2), ("útil", 2), ("vecino", 3),
    ],
)
def test_spanish_syllables(word, syllables):
    assert analyze_blog._count_syllables(word, "es") == syllables


@pytest.mark.parametrize(
    ("word", "syllables"),
    [("mão", 1), ("põe", 1), ("peixe", 2), ("comunicação", 5), ("grande", 2)],
)
def test_portuguese_syllables(word, syllables):
    assert analyze_blog._count_syllables(word, "pt") == syllables


@pytest.mark.parametrize(
    ("word", "language", "syllables"),
    [("собака", "ru", 3), ("лает", "ru", 2), ("спит", "ru", 1),
     ("гавкає", "uk", 3), ("кіт", "uk", 1), ("їжак", "uk", 2)],
)
def test_cyrillic_syllables_count_each_vowel_letter(word, language, syllables):
    assert analyze_blog._count_syllables(word, language) == syllables


def test_spanish_fernandez_huerta_and_inflesz():
    # 9 words, 16 syllables, 2 sentences:
    # La(1) ciudad(2) tiene(2) un(1) país(2) vecino(3) / Leer(2) es(1) útil(2)
    # P = 1600/9 = 177.78; F = 200/9 = 22.22
    # FH = 206.84 - 0.60*177.78 - 1.02*22.22 = 77.51
    # Szigriszt = 206.835 - 62.3*16/9 - 9/2 = 91.58 -> INFLESZ "muy fácil"
    result = analyze_blog.analyze_readability(
        "La ciudad tiene un país vecino. Leer es útil.", "es"
    )
    assert result["reading_model"] == "fernandez-huerta"
    assert result["word_count"] == 9
    assert result["syllable_count"] == 16
    assert result["sentence_count"] == 2
    assert result["reading_ease"] == pytest.approx(77.5, abs=0.05)
    assert result["fernandez_huerta_reading_ease"] == pytest.approx(77.5, abs=0.05)
    assert result["szigriszt_pazos"] == pytest.approx(91.6, abs=0.05)
    assert result["inflesz_band"] == "muy fácil"
    assert result["estimated"] is False
    assert "flesch_reading_ease" not in result


def test_portuguese_flesch_martins():
    # 14 words, 34 syllables, 3 sentences:
    # O(1) gato(2) come(2) peixe(2) / A(1) mão(1) dele(2) é(1) grande(2) /
    # A(1) comunicação(5) institucional(5) apresenta(4) dificuldades(5)
    # 248.835 - 1.015*(14/3) - 84.6*(34/14) = 38.64
    result = analyze_blog.analyze_readability(
        "O gato come peixe. A mão dele é grande. "
        "A comunicação institucional apresenta dificuldades.",
        "pt",
    )
    assert result["reading_model"] == "flesch-pt"
    assert (result["word_count"], result["syllable_count"], result["sentence_count"]) == (14, 34, 3)
    assert result["reading_ease"] == pytest.approx(38.6, abs=0.05)


def test_russian_oborneva():
    # 5 words, 10 syllables, 2 sentences: Кошка(2) спит(1) / Собака(3) громко(2) лает(2)
    # 206.835 - 1.3*2.5 - 60.1*2.0 = 83.39
    result = analyze_blog.analyze_readability("Кошка спит. Собака громко лает.", "ru")
    assert result["reading_model"] == "oborneva"
    assert (result["word_count"], result["syllable_count"], result["sentence_count"]) == (5, 10, 2)
    assert result["reading_ease"] == pytest.approx(83.4, abs=0.05)
    assert result["estimated"] is False


def test_ukrainian_uses_oborneva_as_flagged_approximation():
    # 5 words, 11 syllables, 2 sentences: Кіт(1) спить(1) / Собака(3) голосно(3) гавкає(3)
    # 206.835 - 1.3*2.5 - 60.1*2.2 = 71.37
    result = analyze_blog.analyze_readability("Кіт спить. Собака голосно гавкає.", "uk")
    assert result["reading_model"] == "oborneva-uk"
    assert (result["word_count"], result["syllable_count"], result["sentence_count"]) == (5, 11, 2)
    assert result["reading_ease"] == pytest.approx(71.4, abs=0.05)
    assert result["estimated"] is True
    assert "approximation" in result["approximation_note"]


@pytest.mark.parametrize(
    ("model", "score", "points"),
    [
        ("fernandez-huerta", 70, 7), ("fernandez-huerta", 83, 5),
        ("fernandez-huerta", 88, 3), ("fernandez-huerta", 95, 1),
        ("flesch-pt", 60, 7), ("flesch-pt", 78, 5), ("flesch-pt", 30, 1),
        ("oborneva", 65, 7), ("oborneva-uk", 50, 3),
    ],
)
def test_readability_bands_map_onto_the_seven_point_slot(model, score, points):
    bands = analyze_blog.READABILITY_MODELS[model]["bands"]
    earned = next((p for low, high, p in bands if low <= score <= high), 1)
    assert earned == points


def test_english_flesch_bands_are_unchanged():
    assert analyze_blog.READABILITY_MODELS["flesch"]["bands"] == (
        (60, 70, 7), (55, 75, 5), (45, 80, 3),
    )
    assert analyze_blog.READABILITY_MODELS["atesman"]["bands"] == (
        (50, 69, 7), (30, 89, 5), (0, 100, 3),
    )


# ---------------------------------------------------------------------------
# Sentence splitting
# ---------------------------------------------------------------------------


def test_spanish_thousands_separators_and_abbreviations_do_not_split():
    text = (
        "Bybit permite anuncios de hasta 1.000.000 USDT. "
        "El límite diario es de 1 000 000 pesos. "
        "Por ejemplo, p. ej. el Sr. García paga 2,5 USDT por orden."
    )
    sentences = analyze_blog._split_sentences(text, "es")
    assert len(sentences) == 3
    assert sentences[0] == "Bybit permite anuncios de hasta 1.000.000 USDT."
    assert len(sentences[1].split()) == 7  # "1 000 000" counts as one token
    assert sentences[2].startswith("Por ejemplo, p. ej. el Sr. García")


def test_spanish_abbreviation_followed_by_capital_does_not_split():
    sentences = analyze_blog._split_sentences("Lo firma la Dra. Pérez. Fin del texto.", "es")
    assert sentences == ["Lo firma la Dra. Pérez.", "Fin del texto."]


def test_russian_abbreviations_and_numbers_do_not_split():
    text = "Сумма 1 000 000 рублей, т. е. миллион. Это много. Т. е. запас есть."
    sentences = analyze_blog._split_sentences(text, "ru")
    assert sentences == [
        "Сумма 1000000 рублей, т. е. миллион.",
        "Это много.",
        "Т. е. запас есть.",
    ]


def test_portuguese_and_ukrainian_number_protection():
    assert len(analyze_blog._split_sentences("Custa 1.500,75 reais. Pague já.", "pt")) == 2
    assert len(analyze_blog._split_sentences("Це 1 000 гривень, т. зв. ліміт. Все.", "uk")) == 2


def test_protected_splitter_breaks_at_blank_lines():
    text = "Título sin punto\n\nPrimera frase del párrafo. Segunda frase."
    assert analyze_blog._split_sentences(text, "es") == [
        "Título sin punto", "Primera frase del párrafo.", "Segunda frase.",
    ]


def test_english_keeps_the_legacy_splitter():
    text = "It costs 1.000 dollars. Mr. Smith agrees.\n\nNext para"
    assert analyze_blog._split_sentences(text, "en") == re.split(r"(?<=[.!?])\s+", text)


def test_block_breaks_keep_headings_and_list_items_apart():
    body = "## Requisitos clave\n- Tener KYC\n- Depositar 200 USDT\n\n> **Lo esencial**\n> - Uno."
    plain = analyze_blog._plain_text_for_analysis(body, block_breaks=True)
    sentences = analyze_blog._split_sentences(plain, "es")
    assert "Requisitos clave" in sentences
    assert "Tener KYC" in sentences
    assert "Depositar 200 USDT" in sentences
    # The legacy (English) path still glues the heading to the list items.
    legacy = analyze_blog._split_sentences(analyze_blog._plain_text_for_analysis(body), "en")
    assert "Requisitos clave" not in legacy


def test_mdx_comments_are_not_prose_in_protected_profiles():
    body = "Texto visible.\n\n{/* [PERSONAL EXPERIENCE] nota interna */}\n\nOtro texto."
    plain = analyze_blog._plain_text_for_analysis(body, block_breaks=True)
    assert "nota interna" not in plain


# ---------------------------------------------------------------------------
# Summary labels, examples and definitions
# ---------------------------------------------------------------------------


CASES = {
    "es": (
        "> **Lo esencial**\n> - Uno.\n\n## Qué es\n\n"
        "El **arbitraje P2P** es comprar barato. Los **anunciantes** son usuarios. "
        "**Bybit** está aquí.\n\nPor ejemplo, compras 100 USDT. Pongamos que "
        "vendes; p. ej. a 1,02.",
        1 + 1, 3,
    ),
    "pt": (
        "## Pontos-chave\n\n- Um.\n\n## O que é\n\n"
        "O **spread** é a diferença. Os **anunciantes** são usuários.\n\n"
        "Por exemplo, você compra 100 USDT. Digamos que vende.",
        2, 2,
    ),
    "ru": (
        "## Главное\n\n- Одно.\n\n## Что это\n\n"
        "**Арбитраж** \u2014 это покупка дешевле. **Спред** означает разницу.\n\n"
        "Например, вы покупаете 100 USDT. Допустим, продаёте.",
        2, 2,
    ),
    "uk": (
        "## Головне\n\n- Одне.\n\n## Що це\n\n"
        "**Арбітраж** \u2014 це купівля дешевше. **Спред** означає різницю.\n\n"
        "Наприклад, ви купуєте 100 USDT. Припустимо, продаєте.",
        2, 2,
    ),
}


@pytest.mark.parametrize("language", sorted(CASES))
def test_summary_labels_examples_and_definitions(language):
    body, definitions, examples = CASES[language]
    headings = analyze_blog.analyze_headings(body)
    faq = analyze_blog.analyze_faq(body, language)
    ready = analyze_blog.analyze_ai_citation_readiness(body, headings, faq, language)
    engagement = analyze_blog.analyze_engagement(body, language)
    assert ready["has_tldr"] is True
    assert ready["entity_definitions"] == definitions
    assert engagement["example_count"] == examples
    # The English profile does not recognize any of these.
    en_ready = analyze_blog.analyze_ai_citation_readiness(body, headings, faq, "en")
    assert en_ready["entity_definitions"] == 0
    assert analyze_blog.analyze_engagement(body, "en")["example_count"] == 0


def test_spanish_acerca_de_alone_is_not_an_about_page():
    profile = analyze_blog._language_profile("es")
    prose = "Hablamos acerca de los riesgos del P2P."
    link = "Lee [quiénes somos](/sobre-nosotros) o [la autora](/autor/ana)."
    assert not any(re.search(p, prose, re.IGNORECASE) for p in profile["about_patterns"])
    assert any(re.search(p, link, re.IGNORECASE) for p in profile["about_patterns"])


def test_spanish_percentages_with_space_are_statistics():
    content = "Un 80 % de compleción y un 2,5 % de comisión (Bybit, 2026)."
    assert analyze_blog.analyze_citations(content, "es")["total_statistics"] == 2
    assert analyze_blog.analyze_citations(content, "en")["total_statistics"] == 0


def test_cyrillic_topic_terms_survive_tokenization():
    assert "арбитраж" in analyze_blog._topic_terms("Арбитраж P2P: гид", "ru")
    assert analyze_blog._topic_terms("Арбитраж P2P: гид", "en") == {"p2p"}
    assert "guía" in analyze_blog._topic_terms("Arbitraje P2P: guía honesta", "es")


def test_spanish_bad_anchor_text_is_flagged():
    links = analyze_blog.analyze_links("Mira [aquí](/blog/x) y [la guía](/blog/y).", "es")
    assert links["bad_anchor_texts"] == ["aquí"]


# ---------------------------------------------------------------------------
# Whole-file integration
# ---------------------------------------------------------------------------


SPANISH_POST = """---
title: Arbitraje P2P de cripto: guía y margen real
description: Qué es el arbitraje P2P de criptomonedas y cómo medir tu margen real con costes y ciclos.
author: Ana Pérez
slug: arbitraje-p2p
---
# Arbitraje P2P de cripto: guía y margen real

> **Lo esencial**
> - El arbitraje P2P es comprar cripto barato y venderla más cara.
> - La brecha del libro no es tu margen.

El **arbitraje P2P** es comprar cripto en el mercado entre personas y venderla a otro precio.
Según la [documentación oficial](https://www.bybit.com/es-ES/help-center/p2p) el mercado
publica límites de 1.000.000 USDT por anuncio.

## Cómo se mide el margen

Por ejemplo, si compras a 1,00 y vendes a 1,02, la brecha es del 2 %
([guía de Bybit](https://www.bybit.com/es-ES/help-center/fees)). Pongamos que pagas
comisiones: el **margen real** es lo que queda después de costes.

## Riesgos

Los **pagos de terceros** son el riesgo principal. Lee [quiénes somos](/sobre-nosotros),
la [política editorial](/politica-editorial) y [contacto](/contacto).

## Metodología

Comprobamos 30 órdenes reales en [el libro](https://www.bybit.com/fiat/trade/otc) en 2026.
"""


def test_spanish_file_is_detected_and_scored_with_spanish_profile(tmp_path):
    path = tmp_path / "articulo.mdx"
    path.write_text(SPANISH_POST, encoding="utf-8")

    result = analyze_blog.analyze_file(str(path))

    assert result["language"] == "es"
    assert result["language_detection"]["method"] == "stopwords"
    assert result["readability"]["reading_model"] == "fernandez-huerta"
    assert result["ai_citation_readiness"]["has_tldr"] is True
    assert result["ai_citation_readiness"]["entity_definitions"] == 3
    assert result["engagement"]["example_count"] >= 2
    assert result["originality"]["methodology_count"] >= 1
    assert result["score"]["category_details"]["eeat_signals"]["breakdown"]["trust"] == 4
    seo = result["score"]["category_details"]["seo_optimization"]["breakdown"]
    assert seo["title"] == 4 and seo["keyword_placement"] == 4

    forced_en = analyze_blog.analyze_file(str(path), language="en")
    assert forced_en["language"] == "en"
    assert forced_en["language_detection"]["method"] == "cli-override"
    assert result["score"]["total"] > forced_en["score"]["total"]


@pytest.mark.parametrize(
    ("lang", "title", "body"),
    [
        ("ru", "Арбитраж P2P", RUSSIAN_BODY),
        ("uk", "Арбітраж P2P", UKRAINIAN_BODY),
        ("pt", "Arbitragem P2P", PORTUGUESE_BODY),
    ],
)
def test_declared_profiles_score_title_overlap_with_unicode_tokens(tmp_path, lang, title, body):
    post = f"---\ntitle: {title}\ndescription: {title}\nauthor: Autor Real\nlang: {lang}\n---\n# {title}\n\n## {title}\n\n{body}\n"
    path = tmp_path / f"{lang}.md"
    path.write_text(post, encoding="utf-8")

    result = analyze_blog.analyze_file(str(path))

    assert result["language"] == lang
    assert result["language_detection"]["method"] == "declared"
    seo = result["score"]["category_details"]["seo_optimization"]["breakdown"]
    assert seo["title"] == 4
    assert result["ai_citation_readiness"]["purpose_statement"] is True


def test_unknown_forced_language_returns_an_error(tmp_path):
    path = tmp_path / "x.md"
    path.write_text("# Title\n\nBody.\n", encoding="utf-8")
    assert "error" in analyze_blog.analyze_file(str(path), language="xx")


def test_markdown_report_names_the_language_model(tmp_path):
    path = tmp_path / "articulo.mdx"
    path.write_text(SPANISH_POST, encoding="utf-8")
    report = analyze_blog._format_markdown(analyze_blog.analyze_file(str(path)))
    assert "Fernández-Huerta" in report
    assert "INFLESZ" in report
