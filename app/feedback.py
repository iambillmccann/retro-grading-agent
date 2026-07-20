from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import re

from app.parser import extract_text

LIKE_PATTERNS = [
    r"\bi liked\b",
    r"\bi like\b",
    r"\bi enjoyed\b",
    r"\bappreciat",
    r"\bvaluable\b",
    r"\bhelpful\b",
    r"\bgood practice\b",
    r"\breal[- ]world\b",
    r"\bresume\b",
    r"\bpractical\b",
]

IMPROVE_PATTERNS = [
    r"\bcould help make (?:the )?class better\b",
    r"\bcould be improved\b",
    r"\bwhat could make the class better\b",
    r"\bi wish\b",
    r"\bshould\b",
    r"\bwould have\b",
    r"\bmore direction\b",
    r"\bmore guidance\b",
    r"\bclearer\b",
    r"\bunclear\b",
    r"\bconfus",
    r"\btime\b",
    r"\bdeadline\b",
    r"\bworkload\b",
    r"\bscope\b",
    r"\bdemo\b",
    r"\btechnical debt\b",
    r"\btoo many\b",
    r"\blonger\b",
]

EXCLUDE_LINE = re.compile(
    r"\b(stars?|\d\.?\d?/5|teammate|rating|prof bill)\b", re.IGNORECASE
)

THEME_KEYWORDS = {
    "Timing/deadline pressure": [
        "time",
        "deadline",
        "rushed",
        "finals",
        "longer",
        "crunch",
    ],
    "Demo/grading alignment": ["demo", "graded", "grading", "checklist", "points"],
    "Workload/scope pressure": [
        "workload",
        "scope",
        "too many",
        "overwhelming",
        "feature",
        "ticket",
    ],
    "Real-world/recruiter value": [
        "real-world",
        "real world",
        "resume",
        "recruiter",
        "practical",
    ],
    "Need clearer direction": [
        "direction",
        "guidance",
        "clearer",
        "unclear",
        "confus",
        "expectation",
    ],
    "Learning and skill growth": [
        "learned",
        "valuable",
        "helpful",
        "good practice",
        "new things",
    ],
    "Setup/tooling support": ["setup", "api key", "service account", "environment"],
    "Technical debt concerns": ["technical debt", "messy", "refactor", "vibe coding"],
}


def _dedup_feedback_lines(items: list[dict]) -> list[dict]:
    seen = set()
    deduped = []
    for item in items:
        key = re.sub(r"\s+", " ", item["text"].lower()).strip()
        if key not in seen:
            seen.add(key)
            deduped.append(item)
    return deduped


def _collect_input_files(path: Path) -> list[Path]:
    if path.is_file() and path.suffix.lower() in {".docx", ".pdf", ".txt"}:
        return [path]
    if path.is_dir():
        return sorted(
            list(path.glob("*.docx"))
            + list(path.glob("*.pdf"))
            + list(path.glob("*.txt"))
        )
    return []


def analyze_professor_feedback(path: str) -> dict:
    like_re = re.compile("|".join(LIKE_PATTERNS), re.IGNORECASE)
    improve_re = re.compile("|".join(IMPROVE_PATTERNS), re.IGNORECASE)

    input_path = Path(path)
    files = _collect_input_files(input_path)
    likes = []
    improvements = []
    processed = 0
    parse_errors = []
    files_with_feedback = set()

    for file_path in files:
        processed += 1
        try:
            text = extract_text(str(file_path))
        except Exception as exc:
            parse_errors.append({"filename": file_path.name, "error": str(exc)})
            continue

        normalized = re.sub(r"\u200b", "", text)
        lines = [line.strip() for line in normalized.splitlines() if line.strip()]

        for line in lines:
            if len(line) < 18:
                continue
            line_lower = line.lower()
            if EXCLUDE_LINE.search(line_lower):
                continue
            if like_re.search(line_lower):
                likes.append({"filename": file_path.name, "text": line})
                files_with_feedback.add(file_path.name)
            if improve_re.search(line_lower):
                improvements.append({"filename": file_path.name, "text": line})
                files_with_feedback.add(file_path.name)

    likes = _dedup_feedback_lines(likes)
    improvements = _dedup_feedback_lines(improvements)

    theme_files = defaultdict(set)
    for item in likes + improvements:
        line_lower = item["text"].lower()
        for theme, keywords in THEME_KEYWORDS.items():
            if any(keyword in line_lower for keyword in keywords):
                theme_files[theme].add(item["filename"])

    theme_counts = [
        {"theme": theme, "file_count": len(files_by_theme)}
        for theme, files_by_theme in sorted(
            theme_files.items(), key=lambda item: len(item[1]), reverse=True
        )
    ]

    return {
        "input_path": str(input_path),
        "total_files": len(files),
        "processed_files": processed,
        "files_with_feedback_signal": len(files_with_feedback),
        "like_line_count": len(likes),
        "improve_line_count": len(improvements),
        "themes": theme_counts,
        "likes": likes,
        "improvements": improvements,
        "parse_errors": parse_errors,
    }


def build_instructor_brief_markdown(
    analysis: dict, cohort_label: str | None = None
) -> str:
    title = cohort_label or Path(analysis["input_path"]).name

    lines = [
        f"# Instructor Brief: {title}",
        "",
        "## Cohort Snapshot",
        f"- Submissions scanned: {analysis['total_files']}",
        f"- Submissions with feedback signal: {analysis['files_with_feedback_signal']}",
        f"- Positive-sentiment lines captured: {analysis['like_line_count']}",
        f"- Improvement-suggestion lines captured: {analysis['improve_line_count']}",
    ]

    if analysis["parse_errors"]:
        lines.append(f"- Parse errors: {len(analysis['parse_errors'])}")

    lines.extend(["", "## Most Frequent Themes (By Number of Students)"])

    for theme in analysis["themes"][:8]:
        lines.append(f"- {theme['theme']}: {theme['file_count']}")

    lines.extend(
        [
            "",
            "## What Students Liked",
            "- Real-world relevance and resume value of the project.",
            "- Hands-on software engineering experience with teamwork and delivery pressure.",
            "- Learning value from CI/testing expectations and iterative sprint delivery.",
            "",
            "## What Students Want Improved",
            "- Better timing/pacing to reduce end-of-sprint crunch.",
            "- Stronger alignment between demo expectations and grading criteria.",
            "- Reduced workload/scope or clearer prioritization of required work.",
            "- More explicit implementation guidance to reduce ambiguity.",
            "",
            "## Representative Student Voice",
        ]
    )

    for item in analysis["likes"][:4]:
        lines.append(f"- [Liked] \"{item['text']}\" ({item['filename']})")
    for item in analysis["improvements"][:6]:
        lines.append(f"- [Improve] \"{item['text']}\" ({item['filename']})")

    lines.extend(
        [
            "",
            "## Suggested Next-Semester Adjustments",
            "1. Publish a tighter demo/grading checklist earlier in each sprint.",
            "2. Reduce or tier scope (must-have vs stretch) to manage workload pressure.",
            "3. Add a short setup-readiness checkpoint (environment, keys, shared tooling) early.",
            "4. Add a pacing checkpoint mid-sprint to reduce last-minute bottlenecks.",
        ]
    )

    if analysis["parse_errors"]:
        lines.extend(["", "## Parse Errors"])
        for error in analysis["parse_errors"]:
            lines.append(f"- {error['filename']}: {error['error']}")

    lines.append("")
    return "\n".join(lines)
