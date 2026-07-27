import pytest

from betterprose.voice import (
    load_voice_profile,
    register_names,
    render_voice_instructions,
    resolve_register,
    voice_names,
)


def test_roderick_voice_profile_is_versioned_and_selectable() -> None:
    assert "roderick_b_jones" in voice_names()
    profile = load_voice_profile("roderick_b_jones")
    assert profile.version == "2"
    assert register_names(profile) == [
        "auto",
        "historian_essay",
        "futurist_column",
    ]


def test_rendered_voice_instructions_include_safeguards() -> None:
    profile = load_voice_profile("roderick_b_jones")
    rendered = render_voice_instructions(profile, "historian_essay")
    assert "Use only the historian's essay register" in rendered
    assert "Never invent personal experience" in rendered
    assert "Not this voice:" in rendered
    assert "In this voice:" in rendered


def test_unknown_register_is_rejected() -> None:
    profile = load_voice_profile("roderick_b_jones")
    with pytest.raises(ValueError, match="Unknown register"):
        resolve_register(profile, "press_release")
