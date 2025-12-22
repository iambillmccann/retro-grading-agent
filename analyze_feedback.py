"""
Analyze professor feedback from Sprint 4 retrospectives
"""

import os
from pathlib import Path
import re
from app.parser import extract_text
from collections import defaultdict


def analyze_feedback_sections(text):
    """Extract relevant feedback sections from retrospective text."""
    feedback_points = []

    # Split text into lines for better analysis
    lines = text.split("\n")

    # Track if we're in a feedback section
    in_feedback_section = False
    current_section = []

    # Keywords that indicate feedback/criticism sections
    feedback_indicators = [
        "professor feedback",
        "feedback for professor",
        "feedback to professor",
        "what i didn't like",
        "what i disliked",
        "didn't like",
        "could be improved",
        "improvement",
        "suggestions",
        "suggestion",
        "challenges",
        "difficulties",
        "issues",
        "problems",
        "would have appreciated",
        "would have preferred",
        "would have liked",
        "wish",
        "hope",
        "next time",
        "going forward",
        "criticism",
        "concern",
        "complaint",
    ]

    for i, line in enumerate(lines):
        line_lower = line.lower().strip()

        # Check if this line starts a feedback section
        if any(indicator in line_lower for indicator in feedback_indicators):
            in_feedback_section = True
            current_section = [line]
            continue

        if in_feedback_section:
            # Continue collecting until we hit a section break
            if line.strip() and not line_lower.startswith(
                ("what i liked", "what went well", "positives", "strengths")
            ):
                current_section.append(line)
                # Check if this seems like an end (question number, new major section)
                if re.match(r"^\d+\.|\*\*|^[A-Z][^a-z]+:|\n\n", line):
                    feedback_text = " ".join(current_section).strip()
                    if len(feedback_text) > 20:  # Ignore very short snippets
                        feedback_points.append(feedback_text)
                    in_feedback_section = False
                    current_section = []
            elif not line.strip():  # Empty line might indicate section end
                if current_section:
                    feedback_text = " ".join(current_section).strip()
                    if len(feedback_text) > 20:
                        feedback_points.append(feedback_text)
                in_feedback_section = False
                current_section = []

    # Add any remaining section
    if current_section:
        feedback_text = " ".join(current_section).strip()
        if len(feedback_text) > 20:
            feedback_points.append(feedback_text)

    return feedback_points


def categorize_feedback(all_feedback):
    """Categorize feedback into common themes."""
    categories = defaultdict(list)

    # Define category keywords
    category_keywords = {
        "Tickets/Jira Issues": [
            "ticket",
            "jira",
            "requirements",
            "scope",
            "contradictory",
            "redundant",
            "workload",
            "expectations",
        ],
        "Deployment/Hosting": [
            "deployment",
            "deploy",
            "hosting",
            "cloud",
            "ci/cd",
            "pipeline",
            "production",
        ],
        "Time Management/Deadlines": [
            "time",
            "deadline",
            "finals",
            "week",
            "stress",
            "rushed",
            "crunch",
        ],
        "Communication": [
            "communication",
            "clarity",
            "instructions",
            "confusion",
            "unclear",
        ],
        "Grading/Evaluation": [
            "grading",
            "grade",
            "evaluation",
            "points",
            "credit",
            "fair",
        ],
        "Tools/Technology": ["tools", "technology", "github", "framework", "platform"],
        "Team Issues": ["team", "group", "member", "collaboration", "coordination"],
        "Course Structure": ["course", "class", "lecture", "structure", "format"],
        "Demo/Presentation": ["demo", "presentation", "showing", "display"],
    }

    for feedback_item in all_feedback:
        feedback_lower = feedback_item.lower()
        categorized = False

        for category, keywords in category_keywords.items():
            if any(keyword in feedback_lower for keyword in keywords):
                categories[category].append(feedback_item)
                categorized = True
                break

        if not categorized:
            categories["Other"].append(feedback_item)

    return categories


def main():
    sprint_dirs = [
        "/home/iambillmccann/repositories/retro-grading-agent/data/sprint-4-101",
        "/home/iambillmccann/repositories/retro-grading-agent/data/sprint-4-103",
    ]

    all_feedback = []

    for sprint_dir in sprint_dirs:
        if not os.path.exists(sprint_dir):
            continue

        for file_path in Path(sprint_dir).iterdir():
            if file_path.is_file():
                try:
                    text = extract_text(str(file_path))
                    feedback_points = analyze_feedback_sections(text)
                    all_feedback.extend(feedback_points)
                except Exception as e:
                    print(f"Error processing {file_path.name}: {e}")

    print(f"Extracted {len(all_feedback)} feedback points")

    # Categorize
    categories = categorize_feedback(all_feedback)

    # Create markdown summary
    output_lines = ["# Sprint 4 - Professor Feedback Summary\n"]
    output_lines.append(f"*Compiled from {78} student retrospectives*\n")
    output_lines.append("---\n")

    # Sort categories by number of items (most common first)
    sorted_categories = sorted(
        categories.items(), key=lambda x: len(x[1]), reverse=True
    )

    for category, items in sorted_categories:
        if not items:
            continue

        output_lines.append(f"\n## {category} ({len(items)} mentions)\n")

        # Show unique feedback points
        seen = set()
        unique_items = []
        for item in items:
            # Simple deduplication based on similarity
            item_clean = re.sub(r"\s+", " ", item.lower()).strip()
            if item_clean not in seen:
                seen.add(item_clean)
                unique_items.append(item)

        for item in unique_items[:10]:  # Limit to top 10 per category
            # Clean up the feedback for display
            clean_item = re.sub(r"^\d+\.|^-|^\*", "", item).strip()
            clean_item = re.sub(r"\s+", " ", clean_item)
            if len(clean_item) > 30:  # Only include substantial feedback
                output_lines.append(f"- {clean_item}\n")

    # Write to file
    output_path = "/home/iambillmccann/repositories/retro-grading-agent/results/professor-feedback.md"
    with open(output_path, "w") as f:
        f.writelines(output_lines)

    print(f"\nFeedback summary written to {output_path}")


if __name__ == "__main__":
    main()
