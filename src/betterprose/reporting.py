from __future__ import annotations

import html
import json
from pathlib import Path

from betterprose.models import AssessmentReport, ComparisonReport, RevisionResult


def write_assessment(report: AssessmentReport, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "assessment.json"
    markdown_path = output_dir / "assessment.md"
    html_path = output_dir / "assessment.html"
    json_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    markdown = render_assessment_markdown(report)
    markdown_path.write_text(markdown, encoding="utf-8")
    html_path.write_text(_html_document(markdown), encoding="utf-8")
    return [markdown_path, html_path, json_path]


def render_assessment_markdown(report: AssessmentReport) -> str:
    score_rows = "\n".join(
        f"| {score.label} | {score.rating:.2f}/4 | {score.points:.2f}/{score.weight:g} | "
        f"{score.confidence.title()} |"
        for score in report.scores
    )
    sections = []
    for score in report.scores:
        support = (
            "\n".join(
                f"- **{item.location}:** “{item.quotation}” — {item.explanation}"
                for item in score.supporting_evidence
            )
            or "- No supporting passage was identified."
        )
        limitations = (
            "\n".join(
                f"- **{item.location}:** “{item.quotation}” — {item.explanation}"
                for item in score.limiting_evidence
            )
            or "- No limiting passage was identified."
        )
        sections.append(
            f"## {score.label}\n\n"
            f"**Rating:** {score.rating:.2f}/4 · **Points:** {score.points:.2f}/{score.weight:g} "
            f"· **Confidence:** {score.confidence.title()}\n\n"
            f"{score.rationale}\n\n"
            f"### Evidence of success\n\n{support}\n\n"
            f"### Evidence limiting the score\n\n{limitations}\n\n"
            f"**Revision action:** {score.revision_action}\n"
        )
    strengths = "\n".join(f"- {item}" for item in report.principal_strengths)
    priorities = "\n".join(
        f"{index}. {item}" for index, item in enumerate(report.priority_revisions, start=1)
    )
    integrity = "\n".join(f"- {item}" for item in report.integrity_notes)
    warnings = "\n".join(f"- {item}" for item in report.warnings) or "- None."
    return (
        "# BetterProse assessment\n\n"
        f"- **Document:** {report.document_name}\n"
        f"- **Profile:** {report.profile_name} v{report.profile_version}\n"
        f"- **Provider:** {report.provider}"
        f"{f' ({report.model})' if report.model else ''}\n"
        f"- **Overall quality:** {report.overall_score:.2f}/100\n"
        f"- **Assessment confidence:** {report.overall_confidence.title()}\n"
        f"- **Integrity status:** {report.integrity_status.replace('_', ' ').title()}\n\n"
        "## Reader account\n\n"
        f"{report.reader_account}\n\n"
        "## Principal strengths\n\n"
        f"{strengths}\n\n"
        "## Priority revisions\n\n"
        f"{priorities}\n\n"
        "## Scorecard\n\n"
        "| Criterion | Rating | Points | Confidence |\n"
        "|---|---:|---:|---|\n"
        f"{score_rows}\n\n"
        "## Integrity notes\n\n"
        f"{integrity}\n\n"
        "## Warnings\n\n"
        f"{warnings}\n\n" + "\n".join(sections)
    )


def write_coaching(plan: dict[str, object], output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "coaching.json"
    markdown_path = output_dir / "coaching.md"
    json_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    priorities = "\n\n".join(
        f"{index}. **{item['criterion']}** ({item['rating']:.2f}/4)\n"
        f"   - Why: {item['why']}\n"
        f"   - Action: {item['action']}"
        for index, item in enumerate(plan["priorities"], start=1)
    )
    defer = "\n".join(f"- {item}" for item in plan["defer"])
    markdown_path.write_text(
        "# BetterProse coaching plan\n\n"
        f"{plan['reader_account']}\n\n"
        "## Revision priorities\n\n"
        f"{priorities}\n\n"
        "## Defer until global revision is complete\n\n"
        f"{defer}\n",
        encoding="utf-8",
    )
    return [markdown_path, json_path]


def write_revision(result: RevisionResult, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "revision-audit.json"
    diff_path = output_dir / "revision.diff"
    json_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    diff_path.write_text(result.diff, encoding="utf-8")
    return [Path(result.candidate_path), diff_path, json_path]


def write_comparison(report: ComparisonReport, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "comparison.json"
    markdown_path = output_dir / "comparison.md"
    json_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    assessment = ""
    if report.assessment is not None:
        rows = "\n".join(
            f"| {item.label} | {item.before_rating:.2f} | {item.after_rating:.2f} | "
            f"{item.rating_delta:+.2f} |"
            for item in report.assessment.criteria
        )
        assessment = (
            "## Rubric-aware assessment delta\n\n"
            f"- Profile: {report.assessment.profile_name}\n"
            f"- Provider: {report.assessment.provider}\n"
            f"- Overall: {report.assessment.before_overall:.2f} → "
            f"{report.assessment.after_overall:.2f} "
            f"({report.assessment.overall_delta:+.2f})\n\n"
            "| Criterion | Before | After | Delta |\n"
            "|---|---:|---:|---:|\n"
            f"{rows}\n\n"
        )
    markdown_path.write_text(
        "# BetterProse draft comparison\n\n"
        f"- Words: {report.before.words} → {report.after.words} "
        f"({report.word_delta:+d})\n"
        f"- Sentences: {report.before.sentences} → {report.after.sentences} "
        f"({report.sentence_delta:+d})\n"
        f"- Paragraphs: {report.before.paragraphs} → {report.after.paragraphs} "
        f"({report.paragraph_delta:+d})\n"
        f"- Fact-lock review: {'clear' if report.fact_lock.approved else 'review needed'}\n\n"
        f"{assessment}"
        "## Unified diff\n\n```diff\n"
        f"{report.diff}\n```\n",
        encoding="utf-8",
    )
    return [markdown_path, json_path]


def _html_document(markdown: str) -> str:
    escaped = html.escape(markdown)
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<title>BetterProse assessment</title>"
        "<style>body{max-width:960px;margin:2rem auto;padding:0 1rem;font:16px/1.55 "
        "system-ui;color:#17202a}pre{white-space:pre-wrap;background:#f5f7f9;padding:1.5rem;"
        "border-radius:.5rem}</style></head><body>"
        f"<pre>{escaped}</pre></body></html>"
    )
