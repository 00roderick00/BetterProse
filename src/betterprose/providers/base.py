from __future__ import annotations

from typing import Protocol

from betterprose.document import Document
from betterprose.models import AssessmentDraft, RevisionDraft, Rubric, VoiceProfile


class AssessmentProvider(Protocol):
    name: str
    model: str | None

    def assess(
        self,
        document: Document,
        rubric: Rubric,
        *,
        audience: str | None,
        purpose: str | None,
    ) -> AssessmentDraft: ...

    def revise(
        self,
        document: Document,
        *,
        focus: list[str],
        audience: str | None,
        purpose: str | None,
        voice_profile: VoiceProfile | None,
        voice_register: str | None,
    ) -> RevisionDraft: ...
