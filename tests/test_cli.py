from typer.testing import CliRunner

from betterprose.cli import app

runner = CliRunner()


def test_cli_help_lists_commands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "assess" in result.stdout
    assert "coach" in result.stdout
    assert "revise" in result.stdout
    assert "compare" in result.stdout


def test_cli_assess_runs_offline(tmp_path) -> None:
    source = tmp_path / "draft.md"
    output = tmp_path / "report"
    source.write_text("A claim because a reason.\n\nHowever, one limit remains.")
    result = runner.invoke(
        app,
        ["assess", str(source), "--provider", "local", "--output-dir", str(output)],
    )
    assert result.exit_code == 0
    assert (output / "assessment.json").exists()
