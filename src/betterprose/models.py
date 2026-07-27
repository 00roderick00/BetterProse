from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Confidence = Literal["low", "medium", "high"]
IntegrityStatus = Literal["clear", "review_needed", "material_failure", "not_applicable"]


class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    location: str
    quotation: str
    explanation: str


class CriterionFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    criterion_id: str
    rating: float = Field(ge=0, le=4)
    confidence: Confidence
    rationale: str
    supporting_evidence: list[Evidence] = Field(default_factory=list)
    limiting_evidence: list[Evidence] = Field(default_factory=list)
    revision_action: str


class CriterionScore(CriterionFinding):
    label: str
    weight: float = Field(gt=0)
    points: float = Field(ge=0)


class AssessmentDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reader_account: str
    principal_strengths: list[str]
    priority_revisions: list[str]
    integrity_status: IntegrityStatus = "review_needed"
    integrity_notes: list[str] = Field(default_factory=list)
    findings: list[CriterionFinding]

    @field_validator("priority_revisions")
    @classmethod
    def limit_priorities(cls, value: list[str]) -> list[str]:
        return value[:3]


class AssessmentReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    document_name: str
    profile_name: str
    profile_version: str
    provider: str
    model: str | None = None
    audience: str | None = None
    purpose: str | None = None
    overall_score: float = Field(ge=0, le=100)
    overall_confidence: Confidence
    reader_account: str
    principal_strengths: list[str]
    priority_revisions: list[str]
    integrity_status: IntegrityStatus
    integrity_notes: list[str]
    scores: list[CriterionScore]
    warnings: list[str] = Field(default_factory=list)


class RubricCriterion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    label: str
    weight: float = Field(gt=0)
    question: str
    rating_4: str
    rating_2: str
    rating_0: str


class Rubric(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    label: str
    version: str
    description: str
    criteria: list[RubricCriterion]


class VoiceRegister(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    label: str
    use_when: str
    instructions: list[str]


class VoiceVocabulary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prefer: list[str]
    avoid: list[str]


class VoiceCalibrationExample(BaseModel):
    model_config = ConfigDict(extra="forbid")

    not_voice: str
    in_voice: str


class VoiceProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    label: str
    version: str
    description: str
    provenance: list[str]
    persona: str
    registers: list[VoiceRegister]
    shared_principles: list[str]
    mechanics: list[str]
    spelling: list[str]
    vocabulary: VoiceVocabulary
    safeguards: list[str]
    calibration_examples: list[VoiceCalibrationExample]


class RevisionDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    revised_text: str
    change_summary: list[str]
    unresolved_issues: list[str] = Field(default_factory=list)


class LockedItem(BaseModel):
    kind: str
    value: str


class FactLockAudit(BaseModel):
    mode: Literal["strict", "advisory"]
    approved: bool
    removed: list[LockedItem]
    added: list[LockedItem]
    warnings: list[str]


class RevisionResult(BaseModel):
    source_path: str
    candidate_path: str
    provider: str
    focus: list[str]
    voice_profile: str | None = None
    voice_version: str | None = None
    voice_register: str | None = None
    change_summary: list[str]
    unresolved_issues: list[str]
    audit: FactLockAudit
    diff: str


class VoiceRevisionReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1.0"
    voice_profile: str
    voice_version: str
    voice_register: str
    provider: str
    model: str | None = None
    focus: list[str]
    revised_text: str
    change_summary: list[str]
    unresolved_issues: list[str]
    audit: FactLockAudit
    diff: str
    warnings: list[str] = Field(default_factory=list)


class DocumentStats(BaseModel):
    words: int
    sentences: int
    paragraphs: int
    characters: int


class CriterionDelta(BaseModel):
    criterion_id: str
    label: str
    before_rating: float
    after_rating: float
    rating_delta: float
    before_points: float
    after_points: float
    points_delta: float


class AssessmentDelta(BaseModel):
    profile_name: str
    provider: str
    before_overall: float
    after_overall: float
    overall_delta: float
    criteria: list[CriterionDelta]


class ComparisonReport(BaseModel):
    before_path: str
    after_path: str
    before: DocumentStats
    after: DocumentStats
    word_delta: int
    sentence_delta: int
    paragraph_delta: int
    fact_lock: FactLockAudit
    diff: str
    assessment: AssessmentDelta | None = None
