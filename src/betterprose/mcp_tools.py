from __future__ import annotations

import os
from typing import Literal

from pydantic import BaseModel

from betterprose.document import map_document
from betterprose.models import AssessmentReport
from betterprose.pipeline import assess_document
from betterprose.providers.base import AssessmentProvider
from betterprose.providers.local import LocalProvider
from betterprose.rubric import load_rubric, profile_names

ProfileName = Literal[
    "academic_argument",
    "professional_prose",
    "narrative_nonfiction",
]
ProviderName = Literal["auto", "local", "openai"]


class ProfileCriterionSummary(BaseModel):
    id: str
    label: str
    weight: float


class ProfileSummary(BaseModel):
    name: str
    label: str
    version: str
    description: str
    criteria: list[ProfileCriterionSummary]


class ProfileCatalog(BaseModel):
    profiles: list[ProfileSummary]


def assess_pasted_prose(
    text: str,
    *,
    profile: ProfileName = "academic_argument",
    audience: str | None = None,
    purpose: str | None = None,
    provider: ProviderName = "auto",
) -> AssessmentReport:
    """Run the canonical BetterProse pipeline on prose supplied in memory."""
    prose = text.strip()
    if not prose:
        raise ValueError("Paste non-empty prose in the text field.")
    maximum = _maximum_characters()
    if len(prose) > maximum:
        raise ValueError(
            f"The pasted prose has {len(prose):,} characters; the configured limit is "
            f"{maximum:,}. Split the document or change BETTERPROSE_MAX_CHARS."
        )
    selected_provider = resolve_provider(provider)
    return assess_document(
        map_document(prose, name="pasted-prose"),
        load_rubric(profile),
        selected_provider,
        audience=audience,
        purpose=purpose,
    )


def list_profiles() -> ProfileCatalog:
    """Return the installed BetterProse profiles and visible weights."""
    summaries = []
    for name in profile_names():
        rubric = load_rubric(name)
        summaries.append(
            ProfileSummary(
                name=rubric.name,
                label=rubric.label,
                version=rubric.version,
                description=rubric.description,
                criteria=[
                    ProfileCriterionSummary(
                        id=criterion.id,
                        label=criterion.label,
                        weight=criterion.weight,
                    )
                    for criterion in rubric.criteria
                ],
            )
        )
    return ProfileCatalog(profiles=summaries)


def resolve_provider(name: ProviderName) -> AssessmentProvider:
    if name == "local":
        return LocalProvider()
    if name == "openai":
        return _openai_provider()
    if os.getenv("OPENAI_API_KEY"):
        return _openai_provider()
    return LocalProvider()


def _openai_provider() -> AssessmentProvider:
    from betterprose.providers.openai_provider import OpenAIProvider

    return OpenAIProvider()


def _maximum_characters() -> int:
    raw = os.getenv("BETTERPROSE_MAX_CHARS", "100000")
    try:
        maximum = int(raw)
    except ValueError as exc:
        raise ValueError("BETTERPROSE_MAX_CHARS must be an integer.") from exc
    if maximum < 1:
        raise ValueError("BETTERPROSE_MAX_CHARS must be positive.")
    return maximum
