"""
grader.py

This module uses the OpenAI SDK (>=1.0.0) to evaluate text using a provided prompt template.
"""

import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4-turbo")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)


def grade_with_prompt(text: str, prompt_path: str) -> dict:
    """
    Sends the provided text to OpenAI using the specified prompt template.
    The prompt should include a `{text}` placeholder.

    Args:
        text (str): The input student text to grade.
        prompt_path (str): Path to the prompt file with a {text} placeholder.

    Returns:
        dict: The parsed response from the model.
    """
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    prompt = prompt_template.format(text=text)

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    content = response.choices[0].message.content

    # Strip Markdown-style ```json blocks if present
    cleaned = re.sub(r"^```json\s*|\s*```$", "", content.strip(), flags=re.MULTILINE)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Model response could not be parsed as JSON:\n{e}\nRaw content:\n{content}"
        )
