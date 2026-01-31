#!/usr/bin/env python3
"""
Grade JSON assignment submissions based on a rubric.

This script grades student submissions for the Discord/GitHub setup assignment.

Usage:
    python grade_json_assignment.py data/cs490-hw1 results/cs490-hw1.csv
    python grade_json_assignment.py data/cs684-hw1 results/cs684-hw1.csv
"""

import json
import csv
import sys
from pathlib import Path
from typing import Dict, Tuple


def validate_filename(file_path: Path) -> Tuple[bool, str]:
    """
    Validate that the filename follows the pattern [lastname]-[firstname].json

    Returns:
        (is_valid, feedback) tuple
    """
    filename = file_path.stem  # Get filename without extension

    # Check if it has a dash
    if "-" not in filename:
        return False, "Filename does not follow [lastname]-[firstname] pattern"

    # Check if it has exactly one dash (simple validation)
    parts = filename.split("-")
    if len(parts) != 2:
        return (
            False,
            "Filename should have exactly one dash between lastname and firstname",
        )

    lastname, firstname = parts

    # Check that both parts are non-empty
    if not lastname or not firstname:
        return False, "Both lastname and firstname must be provided"

    return True, ""


def validate_json_structure(data: dict) -> Tuple[bool, str]:
    """
    Validate that JSON has the correct key names (case-sensitive).

    Required keys: name, ucid, discordId, githubId

    Returns:
        (is_valid, feedback) tuple
    """
    required_keys = {"name", "ucid", "discordId", "githubId"}
    actual_keys = set(data.keys())

    if actual_keys != required_keys:
        missing = required_keys - actual_keys
        extra = actual_keys - required_keys

        feedback_parts = []
        if missing:
            feedback_parts.append(f"Missing keys: {', '.join(sorted(missing))}")
        if extra:
            feedback_parts.append(f"Extra keys: {', '.join(sorted(extra))}")

        return False, "; ".join(feedback_parts)

    return True, ""


def validate_values_supplied(data: dict) -> Tuple[int, str]:
    """
    Validate that all values are provided and non-empty.

    Returns:
        (points_earned, feedback) tuple (0-2 points)
    """
    required_keys = ["name", "ucid", "discordId", "githubId"]
    empty_fields = []

    for key in required_keys:
        value = data.get(key, "")
        if not value or (isinstance(value, str) and not value.strip()):
            empty_fields.append(key)

    if not empty_fields:
        return 2, ""
    elif len(empty_fields) <= 2:
        # Partial credit if only 1-2 fields are empty
        return 1, f"Empty or missing values: {', '.join(empty_fields)}"
    else:
        return 0, f"Empty or missing values: {', '.join(empty_fields)}"


def grade_submission(file_path: Path) -> Dict:
    """
    Grade a single JSON submission file.

    Grading rubric (5 points total):
    1. File named correctly (1 point)
    2. Well-formed JSON (1 point)
    3. Key names correctly specified (1 point)
    4. All values supplied (2 points)

    Returns:
        Dictionary with student info, score, and feedback
    """
    result = {
        "filename": file_path.name,
        "name": "",
        "ucid": "",
        "discordId": "",
        "githubId": "",
        "score": 0,
        "feedback": [],
    }

    points = 0

    # 1. Check filename (1 point)
    filename_valid, filename_feedback = validate_filename(file_path)
    if filename_valid:
        points += 1
    else:
        result["feedback"].append(f"Filename: {filename_feedback}")

    # 2. Check if JSON is well-formed (1 point)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        points += 1
    except json.JSONDecodeError as e:
        result["feedback"].append(f"Invalid JSON: {str(e)}")
        result["score"] = points
        result["feedback"] = (
            "; ".join(result["feedback"]) if result["feedback"] else "Perfect!"
        )
        return result
    except Exception as e:
        result["feedback"].append(f"Error reading file: {str(e)}")
        result["score"] = points
        result["feedback"] = (
            "; ".join(result["feedback"]) if result["feedback"] else "Perfect!"
        )
        return result

    # 3. Check key names (1 point)
    keys_valid, keys_feedback = validate_json_structure(data)
    if keys_valid:
        points += 1
    else:
        result["feedback"].append(f"Keys: {keys_feedback}")

    # 4. Check values supplied (2 points)
    values_points, values_feedback = validate_values_supplied(data)
    points += values_points
    if values_feedback:
        result["feedback"].append(f"Values: {values_feedback}")

    # Extract student information if available
    if isinstance(data, dict):
        result["name"] = str(data.get("name", "")).strip()
        result["ucid"] = str(data.get("ucid", "")).strip()
        result["discordId"] = str(data.get("discordId", "")).strip()
        result["githubId"] = str(data.get("githubId", "")).strip()

    result["score"] = points
    result["feedback"] = (
        "; ".join(result["feedback"]) if result["feedback"] else "Perfect!"
    )

    return result


def grade_assignment(input_dir: str, output_csv: str):
    """
    Grade all JSON submissions in the input directory and write results to CSV.

    Args:
        input_dir: Path to directory containing student submissions
        output_csv: Path to output CSV file
    """
    input_path = Path(input_dir)

    if not input_path.exists():
        print(f"Error: Directory '{input_dir}' does not exist")
        sys.exit(1)

    if not input_path.is_dir():
        print(f"Error: '{input_dir}' is not a directory")
        sys.exit(1)

    # Find all JSON files
    json_files = sorted(input_path.glob("*.json"))

    if not json_files:
        print(f"Warning: No JSON files found in '{input_dir}'")
        return

    print(f"Found {len(json_files)} JSON files to grade...")

    # Grade each submission
    results = []
    for json_file in json_files:
        print(f"  Grading {json_file.name}...")
        result = grade_submission(json_file)
        results.append(result)

    # Write results to CSV
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "filename",
                "name",
                "ucid",
                "discordId",
                "githubId",
                "score",
                "feedback",
            ],
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"\nGrading complete! Results written to '{output_csv}'")
    print(f"Total submissions: {len(results)}")

    # Print summary statistics
    scores = [r["score"] for r in results]
    perfect_scores = sum(1 for s in scores if s == 5)
    avg_score = sum(scores) / len(scores) if scores else 0

    print(f"Perfect scores (5/5): {perfect_scores}/{len(results)}")
    print(f"Average score: {avg_score:.2f}/5.00")


def main():
    if len(sys.argv) != 3:
        print("Usage: python grade_json_assignment.py <input_dir> <output_csv>")
        print("\nExamples:")
        print("  python grade_json_assignment.py data/cs490-hw1 results/cs490-hw1.csv")
        print("  python grade_json_assignment.py data/cs684-hw1 results/cs684-hw1.csv")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_csv = sys.argv[2]

    grade_assignment(input_dir, output_csv)


if __name__ == "__main__":
    main()
