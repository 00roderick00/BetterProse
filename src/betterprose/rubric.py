from __future__ import annotations

from importlib.resources import files

import yaml

from betterprose.models import Rubric

CORE_CRITERION_IDS = (
    "rhetorical_fit",
    "motive",
    "controlling_idea",
    "development",
    "support",
    "complexity",
    "macrostructure",
    "cohesion",
    "sentence_craft",
    "diction",
    "voice",
    "conventions",
)


def profile_names() -> list[str]:
    rubric_dir = files("betterprose").joinpath("rubrics")
    return sorted(
        item.name.removesuffix(".yaml")
        for item in rubric_dir.iterdir()
        if item.name.endswith(".yaml")
    )


def load_rubric(name: str) -> Rubric:
    resource = files("betterprose").joinpath("rubrics", f"{name}.yaml")
    if not resource.is_file():
        available = ", ".join(profile_names())
        raise ValueError(f"Unknown profile '{name}'. Available profiles: {available}")
    rubric = Rubric.model_validate(yaml.safe_load(resource.read_text(encoding="utf-8")))
    validate_rubric(rubric)
    return rubric


def validate_rubric(rubric: Rubric) -> None:
    ids = tuple(criterion.id for criterion in rubric.criteria)
    if ids != CORE_CRITERION_IDS:
        raise ValueError(
            f"Profile '{rubric.name}' must use the core criterion IDs in their canonical order."
        )
    total = sum(criterion.weight for criterion in rubric.criteria)
    if abs(total - 100.0) > 0.001:
        raise ValueError(f"Profile '{rubric.name}' weights total {total}, not 100.")
