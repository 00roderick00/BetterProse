import json

from betterprose.document import map_document
from betterprose.pipeline import assess_document
from betterprose.providers.local import LocalProvider
from betterprose.reporting import write_assessment
from betterprose.rubric import load_rubric


def test_assessment_writes_three_formats(tmp_path) -> None:
    report = assess_document(
        map_document("A claim because a reason. However, a limit remains.", "draft.md"),
        load_rubric("academic_argument"),
        LocalProvider(),
    )
    written = write_assessment(report, tmp_path)
    assert {path.suffix for path in written} == {".md", ".html", ".json"}
    payload = json.loads((tmp_path / "assessment.json").read_text())
    assert payload["overall_score"] == report.overall_score
    assert "BetterProse assessment" in (tmp_path / "assessment.md").read_text()
