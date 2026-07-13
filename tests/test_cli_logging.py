from pathlib import Path

from app.utils import log_cli_command


def test_log_cli_command_creates_file_and_appends(tmp_path: Path):
    log_file = tmp_path / "logs" / "commands.txt"

    log_cli_command(
        argv=[
            "python",
            "main.py",
            "data/sprint-1-101",
            "--prompt",
            "app/prompts/early_sprint_retro.txt",
        ],
        log_file=log_file,
    )
    log_cli_command(
        argv=[
            "python",
            "main.py",
            "data/sprint-2-101",
            "--prompt",
            "app/prompts/early_sprint_retro.txt",
        ],
        log_file=log_file,
    )

    assert log_file.exists()

    lines = log_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert lines[0].endswith(
        "python main.py data/sprint-1-101 --prompt app/prompts/early_sprint_retro.txt"
    )
    assert lines[1].endswith(
        "python main.py data/sprint-2-101 --prompt app/prompts/early_sprint_retro.txt"
    )
    assert "T" in lines[0].split(" ", maxsplit=1)[0]
    assert "T" in lines[1].split(" ", maxsplit=1)[0]


def test_log_cli_command_preserves_existing_content(tmp_path: Path):
    log_file = tmp_path / "logs" / "commands.txt"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.write_text("existing line\n", encoding="utf-8")

    log_cli_command(
        argv=[
            "python",
            "main.py",
            "data/sample.txt",
            "--prompt",
            "app/prompts/final_retro.txt",
        ],
        log_file=log_file,
    )

    lines = log_file.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "existing line"
    assert lines[1].endswith(
        "python main.py data/sample.txt --prompt app/prompts/final_retro.txt"
    )
