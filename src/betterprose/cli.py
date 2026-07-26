from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from betterprose.comparison import compare_documents
from betterprose.document import load_document
from betterprose.pipeline import assess_document, coaching_plan
from betterprose.providers.base import AssessmentProvider
from betterprose.providers.local import LocalProvider
from betterprose.reporting import (
    write_assessment,
    write_coaching,
    write_comparison,
    write_revision,
)
from betterprose.revision import revise_document
from betterprose.rubric import load_rubric, profile_names

app = typer.Typer(
    name="betterprose",
    no_args_is_help=True,
    help="Transparent prose assessment, coaching, controlled revision, and comparison.",
)

PathArg = Annotated[Path, typer.Argument(exists=True, dir_okay=False, readable=True)]


def _provider(name: str) -> AssessmentProvider:
    if name == "local":
        return LocalProvider()
    if name == "openai":
        from betterprose.providers.openai_provider import OpenAIProvider

        return OpenAIProvider()
    raise typer.BadParameter("Provider must be 'local' or 'openai'.")


def _default_output(kind: str, path: Path) -> Path:
    return Path(kind) / path.stem


@app.command()
def assess(
    path: PathArg,
    profile: Annotated[str, typer.Option(help="Rubric profile.")] = "academic_argument",
    provider: Annotated[str, typer.Option(help="local or openai.")] = "local",
    audience: Annotated[str | None, typer.Option(help="Intended reader.")] = None,
    purpose: Annotated[str | None, typer.Option(help="Intended effect.")] = None,
    output_dir: Annotated[Path | None, typer.Option(help="Report directory.")] = None,
) -> None:
    """Assess a Markdown or text document and write Markdown, HTML, and JSON reports."""
    try:
        document = load_document(path)
        rubric = load_rubric(profile)
        report = assess_document(
            document,
            rubric,
            _provider(provider),
            audience=audience,
            purpose=purpose,
        )
        target = output_dir or _default_output("reports", path)
        written = write_assessment(report, target)
    except (ValueError, RuntimeError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(
        f"Assessment: {report.overall_score:.2f}/100 ({report.overall_confidence} confidence)"
    )
    for item in written:
        typer.echo(str(item))


@app.command()
def coach(
    path: PathArg,
    profile: Annotated[str, typer.Option(help="Rubric profile.")] = "academic_argument",
    provider: Annotated[str, typer.Option(help="local or openai.")] = "local",
    audience: Annotated[str | None, typer.Option(help="Intended reader.")] = None,
    purpose: Annotated[str | None, typer.Option(help="Intended effect.")] = None,
    output_dir: Annotated[Path | None, typer.Option(help="Report directory.")] = None,
) -> None:
    """Create a prioritized revision plan without changing the source."""
    try:
        report = assess_document(
            load_document(path),
            load_rubric(profile),
            _provider(provider),
            audience=audience,
            purpose=purpose,
        )
        written = write_coaching(
            coaching_plan(report),
            output_dir or _default_output("reports", path),
        )
    except (ValueError, RuntimeError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    for item in written:
        typer.echo(str(item))


@app.command()
def revise(
    path: PathArg,
    provider: Annotated[str, typer.Option(help="local or openai.")] = "local",
    focus: Annotated[str, typer.Option(help="Comma-separated revision dimensions.")] = "clarity",
    audience: Annotated[str | None, typer.Option(help="Intended reader.")] = None,
    purpose: Annotated[str | None, typer.Option(help="Intended effect.")] = None,
    fact_lock: Annotated[str, typer.Option(help="strict or advisory.")] = "strict",
    output_dir: Annotated[Path | None, typer.Option(help="Revision directory.")] = None,
) -> None:
    """Create a separate candidate revision and fact-lock audit."""
    if fact_lock not in {"strict", "advisory"}:
        raise typer.BadParameter("Fact lock must be 'strict' or 'advisory'.")
    focus_items = [item.strip() for item in focus.split(",") if item.strip()]
    try:
        target = output_dir or _default_output("revisions", path)
        result = revise_document(
            path,
            load_document(path),
            _provider(provider),
            target,
            focus=focus_items,
            audience=audience,
            purpose=purpose,
            fact_lock_mode=fact_lock,
        )
        written = write_revision(result, target)
    except (ValueError, RuntimeError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(f"Fact lock: {'approved' if result.audit.approved else 'review required'}")
    for item in written:
        typer.echo(str(item))


@app.command("compare")
def compare_command(
    before: PathArg,
    after: PathArg,
    assess: Annotated[
        bool,
        typer.Option("--assess", help="Include before-and-after rubric scores."),
    ] = False,
    profile: Annotated[str, typer.Option(help="Rubric profile.")] = "academic_argument",
    provider: Annotated[str, typer.Option(help="local or openai.")] = "local",
    audience: Annotated[str | None, typer.Option(help="Intended reader.")] = None,
    purpose: Annotated[str | None, typer.Option(help="Intended effect.")] = None,
    output_dir: Annotated[Path | None, typer.Option(help="Comparison directory.")] = None,
) -> None:
    """Compare two drafts and write an auditable diff report."""
    try:
        report = compare_documents(
            before,
            after,
            rubric=load_rubric(profile) if assess else None,
            provider=_provider(provider) if assess else None,
            audience=audience,
            purpose=purpose,
        )
        target = output_dir or Path("comparisons") / f"{before.stem}-to-{after.stem}"
        written = write_comparison(report, target)
    except (ValueError, RuntimeError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    for item in written:
        typer.echo(str(item))


@app.command()
def profiles() -> None:
    """List installed rubric profiles and their weights."""
    for name in profile_names():
        rubric = load_rubric(name)
        typer.echo(f"{rubric.name} (v{rubric.version}) — {rubric.label}")
        for criterion in rubric.criteria:
            typer.echo(f"  {criterion.id}: {criterion.weight:g}")
