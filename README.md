# 🧠 Retrospective Grading Agent

This AI-powered command-line tool grades student sprint retrospectives using GPT-4-turbo and outputs structured scores and summaries in CSV and/or JSON format. It supports `.docx`, `.pdf`, and `.txt` files.

---

## ✅ Features

- Grades retrospectives using a 5-point rubric:
  - Overall thoughts
  - Personal contributions
  - Things that went well
  - Things that could be improved
  - Teammate ratings
- Supports `.docx`, `.pdf`, and `.txt`
- Batch processing of entire folders
- Outputs to:
  - Console summaries
  - CSV report
  - JSON report
- Flags errors and skips unsupported files
- Clean CLI output with [rich](https://github.com/Textualize/rich)

---

## 🚀 Usage

### Grade a single file

```bash
python main.py data/sample.docx
````

### Grade a folder of files

```bash
python main.py data/
```

### Save results to a default CSV

```bash
python main.py data/ --save
```

### Save results to a custom CSV

```bash
python main.py data/ --save results/sprint1.csv
```

### Save to both CSV and JSON

```bash
python main.py data/ --save --json
```

### Save to custom paths

```bash
python main.py data/ --save results/sprint1.csv --json results/sprint1.json
```

### Run with a custom prompt and save as CSV

```bash
python main.py data/sprint-2-101 --prompt app/prompts/early_sprint_retro.txt --save results/sprint2-101.csv
```

---

## 🧪 File Types

* `.docx` (Word documents)
* `.pdf` (text-based PDFs)
* `.txt` (plain text)

---

## 📁 Output Format

Each row contains:

* `filename`
* `student_name`
* `score` (out of 5)
* `overall_thoughts`
* `personal_contributions`
* `things_that_went_well`
* `things_that_could_be_improved`
* `teammate_ratings`

If JSON is used, a list of structured records is written.

---

## 🔐 Environment Setup

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 📦 Folder Structure

```
retro_grading_agent/
├── app/              # Parsing and grading logic
├── data/             # Input files (ignored in .git)
├── results/          # Output CSV/JSON
├── tests/            # Unit tests
├── main.py           # CLI entry point
├── requirements.txt
└── .env
```

---

## 🧠 Powered by

* [OpenAI GPT-4 Turbo](https://platform.openai.com/docs/models/gpt-4)
* [python-docx](https://github.com/python-openxml/python-docx)
* [PyMuPDF](https://github.com/pymupdf/PyMuPDF)
* [rich](https://github.com/Textualize/rich)

---

## 📌 Coming Soon (Ideas)

* Flag retrospectives with potential team issues
* Export flagged entries only
* Integration with Google Drive or LMS

---

```

Let me know if you want a condensed version for a docstring, or want to generate a GitHub Actions workflow to auto-grade on file uploads.
```
