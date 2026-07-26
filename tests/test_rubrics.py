import pytest

from betterprose.rubric import CORE_CRITERION_IDS, load_rubric, profile_names


@pytest.mark.parametrize("profile", profile_names())
def test_profiles_use_core_ids_and_total_100(profile: str) -> None:
    rubric = load_rubric(profile)
    assert tuple(item.id for item in rubric.criteria) == CORE_CRITERION_IDS
    assert sum(item.weight for item in rubric.criteria) == 100


def test_unknown_profile_is_actionable() -> None:
    with pytest.raises(ValueError, match="Available profiles"):
        load_rubric("missing")
