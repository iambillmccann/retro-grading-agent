"""
Script to extract professor feedback from Sprint 4 retrospectives
"""

import os
from pathlib import Path
from collections import Counter
import re
from app.parser import extract_text


def extract_professor_feedback(text):
    """Extract professor feedback from retrospective text."""
    # Look for common patterns
    patterns = [
        r"professor feedback[:\s]+(.+?)(?:\n\n|\n[A-Z]|\Z)",
        r"feedback for professor[:\s]+(.+?)(?:\n\n|\n[A-Z]|\Z)",
        r"what i (?:didn\'t like|disliked)[:\s]+(.+?)(?:\n\n|\n[A-Z]|\Z)",
        r"improvements?[:\s]+(.+?)(?:\n\n|\n[A-Z]|\Z)",
        r"suggestions?[:\s]+(.+?)(?:\n\n|\n[A-Z]|\Z)",
    ]

    feedback_items = []
    text_lower = text.lower()

    for pattern in patterns:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE | re.DOTALL)
        for match in matches:
            feedback = match.group(1).strip()
            if feedback:
                feedback_items.append(feedback)

    return feedback_items


def main():
    sprint_dirs = [
        "/home/iambillmccann/repositories/retro-grading-agent/data/sprint-4-101",
        "/home/iambillmccann/repositories/retro-grading-agent/data/sprint-4-103",
    ]

    all_feedback = []
    files_processed = 0

    for sprint_dir in sprint_dirs:
        if not os.path.exists(sprint_dir):
            continue

        for file_path in Path(sprint_dir).iterdir():
            if file_path.is_file():
                try:
                    print(f"Processing {file_path.name}...")
                    text = extract_text(str(file_path))
                    feedback = extract_professor_feedback(text)

                    # Also store the full text for manual review
                    all_feedback.append(
                        {
                            "file": file_path.name,
                            "text": text,
                            "extracted_feedback": feedback,
                        }
                    )
                    files_processed += 1
                except Exception as e:
                    print(f"Error processing {file_path.name}: {e}")

    print(f"\nProcessed {files_processed} files")

    # Write raw data to a temp file for analysis
    with open("/tmp/feedback_raw.txt", "w") as f:
        for item in all_feedback:
            f.write(f"\n{'='*80}\n")
            f.write(f"FILE: {item['file']}\n")
            f.write(f"{'='*80}\n")
            f.write(item["text"])
            f.write(f"\n\nExtracted feedback: {item['extracted_feedback']}\n")

    print(f"Raw feedback written to /tmp/feedback_raw.txt")


if __name__ == "__main__":
    main()
