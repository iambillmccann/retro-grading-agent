import shlex
import sys
from datetime import datetime
from pathlib import Path


def log_cli_command(
    argv: list[str] | None = None,
    log_file: Path | None = None,
) -> None:
    """Append a timestamped command entry to logs/commands.txt."""
    args = argv if argv is not None else sys.argv
    command_text = shlex.join(args)
    entry = f"{datetime.now().isoformat(timespec='seconds')} {command_text}\n"

    destination = (
        log_file
        if log_file is not None
        else Path(__file__).resolve().parent.parent / "logs" / "commands.txt"
    )
    destination.parent.mkdir(parents=True, exist_ok=True)

    with destination.open("a", encoding="utf-8") as file_obj:
        file_obj.write(entry)
