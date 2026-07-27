from betterprose.document import map_document
from betterprose.pipeline import assess_document, coaching_plan
from betterprose.providers.local import LocalProvider
from betterprose.rubric import load_rubric

TEXT = """
Agencies should publish plain-language summaries because technically accurate
reports can still be unusable to citizens.

Critics may argue that summaries oversimplify findings. However, agencies can
link every summary claim to the relevant section and state uncertainty.

This change would give readers an accountable entrance into public evidence.
""".strip()


def test_pipeline_calculates_weighted_total() -> None:
    report = assess_document(
        map_document(TEXT, "essay.md"),
        load_rubric("academic_argument"),
        LocalProvider(),
        audience="citizens",
        purpose="recommend summaries",
    )
    assert len(report.scores) == 12
    assert report.overall_score == round(sum(item.points for item in report.scores), 2)
    assert report.overall_confidence == "low"
    assert report.provider == "local"


def test_coaching_plan_limits_priorities() -> None:
    report = assess_document(
        map_document(TEXT, "essay.md"),
        load_rubric("professional_prose"),
        LocalProvider(),
    )
    plan = coaching_plan(report)
    assert len(plan["priorities"]) == 3
