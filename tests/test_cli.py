import json

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
    assert "voices" in result.stdout


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


def test_cli_lists_roderick_voice() -> None:
    result = runner.invoke(app, ["voices"])
    assert result.exit_code == 0
    assert "roderick_b_jones (v2)" in result.stdout
    assert "historian_essay" in result.stdout
    assert "futurist_column" in result.stdout


def test_cli_revision_records_selected_voice(tmp_path) -> None:
    source = tmp_path / "draft.md"
    output = tmp_path / "revision"
    source.write_text("The system matters because its incentives shape behaviour.")
    result = runner.invoke(
        app,
        [
            "revise",
            str(source),
            "--provider",
            "local",
            "--voice",
            "roderick_b_jones",
            "--register",
            "historian_essay",
            "--output-dir",
            str(output),
        ],
    )
    assert result.exit_code == 0
    audit = json.loads((output / "revision-audit.json").read_text())
    assert audit["voice_profile"] == "roderick_b_jones"
    assert audit["voice_version"] == "2"
    assert audit["voice_register"] == "historian_essay"
    assert any("did not apply" in issue for issue in audit["unresolved_issues"])
