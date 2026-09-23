# ResumeAI

**AI-Powered Resume Screening and Ranking System**

ResumeAI is a Flask-based application that screens and ranks candidate resumes against a Job Description using ATS-style scoring, skill matching, keyword analysis, and explainable candidate insights.

## Features

* PDF resume text extraction
* Job Description analysis
* Required and preferred skill extraction
* TF-IDF + Cosine Similarity
* Skill matching and skill-gap analysis
* Keyword coverage analysis
* Skill relevance analysis
* Explainable candidate scoring
* Candidate ranking
* Candidate search and filtering
* Candidate profile extraction
* Candidate comparison
* CSV export
* PDF screening reports

## Scoring

The current scoring model combines:

* **JD Similarity**
* **Skill Match**
* **Keyword Coverage**
* **Skill Relevance**

The final score also shows individual component contributions for better explainability.

## Tech Stack

**Backend**

* Python
* Flask

**NLP / Machine Learning**

* spaCy
* scikit-learn
* TF-IDF
* Cosine Similarity

**PDF Processing**

* PyMuPDF
* ReportLab

**Frontend**

* HTML
* CSS
* JavaScript

## Project Structure

```text
ResumeAI/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── static/
│   └── style.css
├── templates/
│   └── index.html
└── utils/
    ├── candidate_parser.py
    ├── jd_analyzer.py
    ├── pdf_extractor.py
    ├── scorer.py
    └── text_preprocessor.py
```

## Installation

```powershell
git clone https://github.com/Roypurab/ResumeAI.git
cd ResumeAI
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Run

```powershell
python app.py
```

Open:

`http://127.0.0.1:5000`

## Screening Workflow

```text
Job Description
      ↓
JD Analysis
      ↓
Resume PDF Extraction
      ↓
Text Preprocessing
      ↓
Similarity + Skill Analysis
      ↓
Explainable Scoring
      ↓
Candidate Ranking
      ↓
Reports & Candidate Insights
```

## Current Status

**Active Development**

The core resume screening, scoring, ranking, candidate analysis, comparison, and reporting workflow is implemented.

## Roadmap

* User authentication
* Database-backed screening history
* Multi-page application architecture
* Improved resume parsing
* Automated testing
* Production deployment
* Additional security and validation

## Author

**Purab Roy**
B.Tech Information Technology

GitHub: https://github.com/Roypurab/ResumeAI

---

© 2026 Purab Roy
