"""
grader.py

This module uses the new OpenAI SDK (>=1.0.0) to evaluate a student's
sprint retrospective using GPT-4-turbo.
"""

import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4-turbo")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)


def grade_retrospective(text: str) -> dict:
    """
    Analyze the given retrospective text and return a grading breakdown.

    Args:
        text (str): The student's retrospective submission.

    Returns:
        dict: A structured grading result.
    """
    prompt = f"""
You are grading a student's sprint retrospective. The grading rubric is:

1 point: Overall thoughts on the sprint
1 point: Personal contributions
1 point: Things that went well
1 point: Things that could be improved
1 point: Teammate ratings

Analyze the text below and return a JSON object with the following keys:
- student_name (string)
- score (integer from 0 to 5)
- breakdown (dictionary with one sentence for each of the five criteria)

Respond ONLY with valid JSON. Do NOT include any explanation or formatting.

Text:
{text}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    content = response.choices[0].message.content

    # After receiving content = response.choices[0].message.content
    # Strip Markdown-style ```json ... ``` if present
    cleaned = re.sub(r"^```json\s*|\s*```$", "", content.strip(), flags=re.MULTILINE)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Model response could not be parsed as JSON:\n{e}\nRaw content:\n{content}"
        )
