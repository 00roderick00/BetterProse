from betterprose.comparison import compare_documents
from betterprose.providers.local import LocalProvider
from betterprose.rubric import load_rubric


def test_compare_documents_reports_deltas_and_diff(tmp_path) -> None:
    before = tmp_path / "before.md"
    after = tmp_path / "after.md"
    before.write_text("The result was 12%.")
    after.write_text("The measured result was 12%. It remained stable.")
    report = compare_documents(before, after)
    assert report.word_delta > 0
    assert "+The measured result" in report.diff
    assert report.fact_lock.approved


def test_compare_documents_can_include_assessment_deltas(tmp_path) -> None:
    before = tmp_path / "before.md"
    after = tmp_path / "after.md"
    before.write_text("A proposal.")
    after.write_text(
        "A proposal should be adopted because it reduces delay.\n\n"
        "However, implementation risk remains."
    )
    report = compare_documents(
        before,
        after,
        rubric=load_rubric("academic_argument"),
        provider=LocalProvider(),
    )
    assert report.assessment is not None
    assert len(report.assessment.criteria) == 12
    assert report.assessment.after_overall > report.assessment.before_overall
