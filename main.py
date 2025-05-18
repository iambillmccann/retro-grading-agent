# main.py

import argparse
import os
import json
from pathlib import Path
import csv
from app.parser import extract_text
from app.grader import grade_with_prompt
from rich import print


def process_file(filepath: str, prompt_path: str) -> dict:
    print(f"[bold cyan]Reading:[/bold cyan] {filepath}")
    try:
        text = extract_text(filepath)
        print("[bold cyan]Grading...[/bold cyan]")
        result = grade_with_prompt(text, prompt_path)
        print(
            f"[bold green]Graded: {result.get('student_name', 'Unknown')} — Score: {result.get('score', '?')}[/bold green]"
        )
        return {
            "filename": Path(filepath).name,
            "student_name": result.get("student_name", ""),
            "score": result.get("score", ""),
            "overall_thoughts": result["breakdown"].get(
                "Overall thoughts on the sprint", ""
            ),
            "personal_contributions": result["breakdown"].get(
                "Personal contributions", ""
            ),
            "things_that_went_well": result["breakdown"].get(
                "Things that went well", ""
            ),
            "things_that_could_be_improved": result["breakdown"].get(
                "Things that could be improved", ""
            ),
            "teammate_ratings": result["breakdown"].get("Teammate ratings", ""),
        }
    except Exception as e:
        print(f"[bold red]Error processing {filepath}:[/bold red] {e}")
        return None


def write_results_to_csv(results: list[dict], output_file: str):
    os.makedirs(Path(output_file).parent, exist_ok=True)
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"\n[bold green]Results saved to:[/bold green] {output_file}")


def write_results_to_json(results: list[dict], output_file: str):
    os.makedirs(Path(output_file).parent, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n[bold green]Results saved to:[/bold green] {output_file}")


def main():
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

    path = Path(args.path)
    all_results = []

    if path.is_file():
        result = process_file(str(path), args.prompt)
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
            result = process_file(str(file), args.prompt)
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
