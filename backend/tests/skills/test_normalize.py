"""Tests for turning any spelling of a skill into one lookup key (M4.2). No database."""

from app.skills.normalize import normalize, tokens


def test_case_and_spaces_dont_matter() -> None:
    assert normalize("  PostgreSQL ") == "postgresql"
    assert normalize("Machine   Learning") == "machine learning"


def test_french_accents_dont_matter() -> None:
    assert normalize("Développement Web") == normalize("developpement web")
    assert normalize("Sécurité des réseaux") == "securite des reseaux"
    assert normalize("COMPÉTENCES") == "competences"


def test_punctuation_becomes_a_space_except_plus_and_hash() -> None:
    assert normalize("Node.js") == "node js"
    assert normalize("front-end") == normalize("front end")
    assert normalize("CI/CD") == "ci cd"
    assert normalize("C++") == "c++"
    assert normalize("C#") == "c#"
    assert normalize(".NET") == "net"
    assert normalize("d'équipe") == "d equipe"


def test_arabic_diacritics_and_hamza_forms_dont_matter() -> None:
    assert normalize("قَوَاعِدُ البَيَانَات") == normalize("قواعد البيانات")
    assert normalize("أمن") == normalize("امن")


def test_tokens_keep_the_original_text_next_to_the_key() -> None:
    assert tokens("Built a REST API with Node.js") == [
        ("Built", "built"),
        ("a", "a"),
        ("REST", "rest"),
        ("API", "api"),
        ("with", "with"),
        ("Node", "node"),
        ("js", "js"),
    ]
    assert tokens("C++, C# et l'équipe") == [
        ("C++", "c++"),
        ("C#", "c#"),
        ("et", "et"),
        ("l", "l"),
        ("équipe", "equipe"),
    ]
