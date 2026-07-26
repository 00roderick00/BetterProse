from __future__ import annotations

import difflib
from pathlib import Path

from betterprose.document import load_document
from betterprose.models import (
    AssessmentDelta,
    AssessmentReport,
    ComparisonReport,
    CriterionDelta,
    Rubric,
)
from betterprose.pipeline import assess_document
from betterprose.providers.base import AssessmentProvider
from betterprose.revision import audit_fact_lock


def compare_documents(
    before_path: Path,
    after_path: Path,
    *,
    rubric: Rubric | None = None,
    provider: AssessmentProvider | None = None,
    audience: str | None = None,
    purpose: str | None = None,
) -> ComparisonReport:
    before = load_document(before_path)
    after = load_document(after_path)
    if (rubric is None) != (provider is None):
        raise ValueError("Rubric and provider must be supplied together for assessment deltas.")
    assessment = None
    if rubric is not None and provider is not None:
        before_report = assess_document(
            before,
            rubric,
            provider,
            audience=audience,
            purpose=purpose,
        )
        after_report = assess_document(
            after,
            rubric,
            provider,
            audience=audience,
            purpose=purpose,
        )
        assessment = assessment_delta(before_report, after_report)
    diff = "".join(
        difflib.unified_diff(
            before.text.splitlines(keepends=True),
            after.text.splitlines(keepends=True),
            fromfile=str(before_path),
            tofile=str(after_path),
        )
    )
    return ComparisonReport(
        before_path=str(before_path),
        after_path=str(after_path),
        before=before.stats,
        after=after.stats,
        word_delta=after.stats.words - before.stats.words,
        sentence_delta=after.stats.sentences - before.stats.sentences,
        paragraph_delta=after.stats.paragraphs - before.stats.paragraphs,
        fact_lock=audit_fact_lock(before.text, after.text, mode="advisory"),
        diff=diff,
        assessment=assessment,
    )


def assessment_delta(
    before: AssessmentReport,
    after: AssessmentReport,
) -> AssessmentDelta:
    if before.profile_name != after.profile_name:
        raise ValueError("Cannot compare assessment scores from different rubric profiles.")
    before_scores = {score.criterion_id: score for score in before.scores}
    after_scores = {score.criterion_id: score for score in after.scores}
    if before_scores.keys() != after_scores.keys():
        raise ValueError("Assessment reports have different criterion sets.")
    criteria = []
    for score in before.scores:
        revised = after_scores[score.criterion_id]
        criteria.append(
            CriterionDelta(
                criterion_id=score.criterion_id,
                label=score.label,
                before_rating=score.rating,
                after_rating=revised.rating,
                rating_delta=round(revised.rating - score.rating, 2),
                before_points=score.points,
                after_points=revised.points,
                points_delta=round(revised.points - score.points, 2),
            )
        )
    return AssessmentDelta(
        profile_name=before.profile_name,
        provider=before.provider,
        before_overall=before.overall_score,
        after_overall=after.overall_score,
        overall_delta=round(after.overall_score - before.overall_score, 2),
        criteria=criteria,
    )
