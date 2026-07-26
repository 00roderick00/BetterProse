import pytest

from betterprose.mcp_tools import assess_pasted_prose, list_profiles, resolve_provider


def test_assess_pasted_prose_uses_canonical_pipeline(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    report = assess_pasted_prose(
        "Agencies should publish summaries because readers need usable reports.",
        profile="professional_prose",
        audience="citizens",
        purpose="recommend plain-language summaries",
        provider="auto",
    )
    assert report.document_name == "pasted-prose"
    assert report.profile_name == "professional_prose"
    assert report.provider == "local"
    assert len(report.scores) == 12


def test_auto_provider_is_local_without_api_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert resolve_provider("auto").name == "local"


def test_character_limit_is_enforced(monkeypatch) -> None:
    monkeypatch.setenv("BETTERPROSE_MAX_CHARS", "10")
    with pytest.raises(ValueError, match="configured limit"):
        assess_pasted_prose("This passage is longer than ten characters.")


def test_profile_catalog_is_complete() -> None:
    catalog = list_profiles()
    assert {profile.name for profile in catalog.profiles} == {
        "academic_argument",
        "professional_prose",
        "narrative_nonfiction",
    }
    assert all(sum(item.weight for item in profile.criteria) == 100 for profile in catalog.profiles)
