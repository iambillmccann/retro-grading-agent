# 🧠 Retrospective Grading Agent

This command-line tool provides automated grading for student assignments:
1. **AI-powered grading** for sprint retrospectives using GPT-4-turbo
2. **Rule-based grading** for JSON assignment submissions

Supports `.docx`, `.pdf`, `.txt`, and `.json` files with outputs to CSV and/or JSON format.

---

## ✅ Features

### AI-Powered Retrospective Grading
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

### Rule-Based JSON Assignment Grading
- Grades JSON submission files based on a structured rubric
- Validates filename format, JSON syntax, key names, and values
- Automatic scoring with detailed feedback
- Generates CSV reports with scores and feedback

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
-or-
python main.py data/sprint-4-103 --prompt app/prompts/final_retro.txt --save results/sprint4-103.csv
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

---

## 📊 Rule-Based JSON Assignment Grading

The `grade_json_assignment.py` script provides automated grading for JSON assignment submissions.

### Usage

```bash
python grade_json_assignment.py <input_directory> <output_csv_file>
```

### Examples

```bash
# Grade cs490-hw1 submissions
python grade_json_assignment.py data/cs490-hw1 results/cs490-hw1.csv

# Grade cs684-hw1 submissions  
python grade_json_assignment.py data/cs684-hw1 results/cs684-hw1.csv
```

### Grading Rubric (5 points total)

1. **File named correctly** (1 point)  
   - Must follow pattern: `[lastname]-[firstname].json`
   - Example: `mccann-bill.json`

2. **Well-formed JSON** (1 point)  
   - File must be valid JSON syntax

3. **Key names correctly specified** (1 point)  
   - Must have exactly these keys (case-sensitive): `name`, `ucid`, `discordId`, `githubId`

4. **All values supplied** (2 points)  
   - All four values must be present and non-empty
   - Partial credit (1 point) if only 1-2 values are missing

### Output Format

The script generates a CSV file with the following columns:
- `filename` - The original submission filename
- `name` - Student's name from JSON
- `ucid` - Student's UCID from JSON  
- `discordId` - Student's Discord ID from JSON
- `githubId` - Student's GitHub ID from JSON
- `score` - Points earned (0-5)
- `feedback` - Detailed feedback on what points were lost (if any)

### Example Output

```csv
filename,name,ucid,discordId,githubId,score,feedback
mccann-bill.json,Bill McCann,wfm8,iambillmccann,iambillmccann,5,Perfect!
smith-john.json,John Smith,js123,,,2,"Keys: Missing keys: discordId, githubId"
```

