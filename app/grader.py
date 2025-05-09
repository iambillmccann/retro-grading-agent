"""
grader.py

This module handles interaction with the OpenAI API to evaluate a student's
sprint retrospective according to a predefined grading rubric.
"""

import os
import openai
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo")


def grade_retrospective(text: str, model: str = DEFAULT_MODEL) -> dict:
    """
    Analyze the given retrospective text and return a grading breakdown.

    Args:
        text (str): The student's retrospective submission.
        model (str): OpenAI model to use (default: gpt-4-turbo).

    Returns:
        dict: A structured grading result containing name, score, and justification.
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

Text:
{text}
"""

    response = openai.ChatCompletion.create(
        model=model, messages=[{"role": "user", "content": prompt}], temperature=0.2
    )

    # Attempt to parse model response as JSON
    import json

    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        raise ValueError("Model response could not be parsed as JSON.")
