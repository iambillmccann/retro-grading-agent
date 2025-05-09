# tests/test_parser.py

import os
import pytest
from app.parser import extract_text


def test_extract_docx_text():
    file_path = "tests/fixtures/sample.docx"
    text = extract_text(file_path)
    assert "Retrospective" in text
    assert len(text) > 10


def test_extract_pdf_text():
    file_path = "tests/fixtures/sample.pdf"
    text = extract_text(file_path)
    assert "Sprint" in text
    assert len(text) > 10


def test_unsupported_file_type():
    with pytest.raises(ValueError):
        extract_text("tests/fixtures/sample.txt")
