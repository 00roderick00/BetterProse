from __future__ import annotations

from collections import Counter
from statistics import mean

from betterprose.document import Document
from betterprose.models import AssessmentReport, CriterionScore, Rubric
from betterprose.providers.base import AssessmentProvider


def assess_document(
    document: Document,
    rubric: Rubric,
    provider: AssessmentProvider,
    *,
    audience: str | None = None,
    purpose: str | None = None,
) -> AssessmentReport:
    if not document.text.strip():
        raise ValueError("Cannot assess an empty document.")
    draft = provider.assess(document, rubric, audience=audience, purpose=purpose)
    findings = {finding.criterion_id: finding for finding in draft.findings}
    expected = {criterion.id for criterion in rubric.criteria}
    missing = expected - findings.keys()
    unknown = findings.keys() - expected
    if missing or unknown or len(findings) != len(draft.findings):
        raise ValueError(
            f"Provider criterion mismatch. Missing={sorted(missing)}, unknown={sorted(unknown)}, "
            "or duplicate IDs were returned."
        )

    scores: list[CriterionScore] = []
    for criterion in rubric.criteria:
        finding = findings[criterion.id]
        points = round(criterion.weight * finding.rating / 4, 2)
        scores.append(
            CriterionScore(
                **finding.model_dump(),
                label=criterion.label,
                weight=criterion.weight,
                points=points,
            )
        )

    overall = round(sum(score.points for score in scores), 2)
    confidence_counts = Counter(score.confidence for score in scores)
    overall_confidence = (
        "high"
        if confidence_counts["high"] >= 8
        else "medium"
        if confidence_counts["high"] + confidence_counts["medium"] >= 8
        else "low"
    )
    warnings = []
    if provider.name == "local":
        warnings.append(
            "Offline scores are low-confidence diagnostics and must not be treated as grades."
        )
    if document.stats.words < 150:
        warnings.append("The document is short; several criteria may not have enough evidence.")

    return AssessmentReport(
        document_name=document.name,
        profile_name=rubric.name,
        profile_version=rubric.version,
        provider=provider.name,
        model=provider.model,
        audience=audience,
        purpose=purpose,
        overall_score=overall,
        overall_confidence=overall_confidence,
        reader_account=draft.reader_account,
        principal_strengths=draft.principal_strengths,
        priority_revisions=draft.priority_revisions[:3],
        integrity_status=draft.integrity_status,
        integrity_notes=draft.integrity_notes,
        scores=scores,
        warnings=warnings,
    )


def coaching_plan(report: AssessmentReport) -> dict[str, object]:
    lowest = sorted(report.scores, key=lambda score: (score.rating, -score.weight))[:3]
    return {
        "document": report.document_name,
        "profile": report.profile_name,
        "provider": report.provider,
        "reader_account": report.reader_account,
        "priorities": [
            {
                "criterion": score.label,
                "rating": score.rating,
                "why": score.rationale,
                "action": score.revision_action,
            }
            for score in lowest
        ],
        "defer": [
            "Do not line-edit passages that may be removed or reorganized.",
            "Verify global purpose, reasoning, support, and structure before polishing diction.",
        ],
    }


def average_rating(report: AssessmentReport) -> float:
    return mean(score.rating for score in report.scores)
