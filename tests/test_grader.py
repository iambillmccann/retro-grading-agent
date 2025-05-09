# tests/test_grader.py

import pytest
from app.grader import grade_retrospective


@pytest.mark.skip(reason="Requires OpenAI API call")
def test_grade_retrospective_live():
    sample_text = """
    My team worked well during sprint 1. I implemented the login feature. We finished early.
    One issue was scheduling meetings. I rate teammates highly.
    """
    result = grade_retrospective(sample_text)
    assert isinstance(result, dict)
    assert 0 <= result["score"] <= 5
    assert "breakdown" in result
