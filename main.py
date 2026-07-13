# main.py

import argparse
import os
import json
from pathlib import Path
import csv
from app.parser import extract_text
from app.grader import grade_with_prompt
from app.utils import log_cli_command
from rich import print


def resolve_prompt_path(prompt_arg: str) -> str:
    """Resolve a prompt path from CLI input.

    Supports:
    - exact relative/absolute paths passed by the user
    - shorthand paths like ./prompts/foo.txt by mapping to app/prompts/foo.txt
    """
    prompt_path = Path(prompt_arg)

    if prompt_path.exists():
        return str(prompt_path)

    repo_root = Path(__file__).parent
    alt_candidates = [
        repo_root / prompt_arg,
        repo_root / "app" / "prompts" / prompt_path.name,
    ]

    for candidate in alt_candidates:
        if candidate.exists():
            return str(candidate)

    raise FileNotFoundError(
        f"Prompt file not found: {prompt_arg}. Try one of: "
        f"app/prompts/{prompt_path.name}"
    )


def process_file(filepath: str, prompt_path: str) -> dict:
    print(f"[bold cyan]Reading:[/bold cyan] {filepath}")
    try:
        text = extract_text(filepath)
        print("[bold cyan]Grading...[/bold cyan]")
        result = grade_with_prompt(text, prompt_path)

        # Dynamically attach filename
        result["filename"] = Path(filepath).name

        # Safe, dynamic summary for console
        student = result.get("student_name", "Unknown")
        score = result.get("score", "?")
        print(f"[bold green]Graded: {student} — Score: {score}[/bold green]")

        return result

    except Exception as e:
        print(f"[bold red]Error processing {filepath}:[/bold red] {e}")
        return None


def write_results_to_csv(results: list[dict], output_file: str):
    os.makedirs(Path(output_file).parent, exist_ok=True)
    # Collect all unique fieldnames from all results
    fieldnames = set()
    for result in results:
        fieldnames.update(result.keys())
    ordered_hw2 = [
        "filename",
        "claims",
        "assumptions",
        "refused",
        "oracles",
        "confidence",
        "score",
        "feedback",
    ]
    ordered_retro = [
        "filename",
        "student_name",
        "score",
        "overall_thoughts",
        "personal_contributions",
        "things_that_went_well",
        "things_that_could_be_improved",
        "teammate_ratings",
        "breakdown",
        "students_with_poor_ratings",
    ]

    if set(ordered_hw2).issubset(fieldnames):
        extra = sorted(fieldnames - set(ordered_hw2))
        fieldnames = ordered_hw2 + extra
    elif {"filename", "student_name", "score"}.issubset(fieldnames):
        base = [name for name in ordered_retro if name in fieldnames]
        extra = sorted(fieldnames - set(base))
        fieldnames = base + extra
    else:
        fieldnames = sorted(fieldnames)  # Sort for consistent column order

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"\n[bold green]Results saved to:[/bold green] {output_file}")


def write_results_to_json(results: list[dict], output_file: str):
    os.makedirs(Path(output_file).parent, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n[bold green]Results saved to:[/bold green] {output_file}")


def main():
    try:
        log_cli_command()
    except Exception as exc:
        print(f"[bold yellow]Warning: could not write command log:[/bold yellow] {exc}")

    parser = argparse.ArgumentParser(description="Grade student assignments using AI.")
    parser.add_argument("path", help="Path to a file or folder")
    parser.add_argument(
        "--prompt",
        required=True,
        help="Path to the .txt file containing the grading prompt",
    )
    parser.add_argument(
        "--save",
        nargs="?",
        const="results/grading_results.csv",
        help="Optional output CSV path",
    )
    parser.add_argument(
        "--json",
        nargs="?",
        const="results/grading_results.json",
        help="Optional output JSON path",
    )
    args = parser.parse_args()

    try:
        prompt_path = resolve_prompt_path(args.prompt)
    except FileNotFoundError as e:
        print(f"[bold red]{e}[/bold red]")
        return

    path = Path(args.path)
    all_results = []

    if path.is_file():
        result = process_file(str(path), prompt_path)
        if result and args.save:
            all_results.append(result)
    elif path.is_dir():
        files = (
            list(path.glob("*.docx"))
            + list(path.glob("*.pdf"))
            + list(path.glob("*.txt"))
        )
        if not files:
            print(
                f"[bold yellow]No .docx, .pdf, or .txt files found in {path}[/bold yellow]"
            )
            return
        for file in files:
            result = process_file(str(file), prompt_path)
            if result:
                all_results.append(result)
    else:
        print(f"[bold red]Invalid path:[/bold red] {args.path}")
        return

    if args.save and all_results:
        write_results_to_csv(all_results, args.save)
    if args.json and all_results:
        write_results_to_json(all_results, args.json)


if __name__ == "__main__":
    main()
