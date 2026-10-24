# Resume AI Analyser

A full-stack web application that analyses resumes against job descriptions using keyword matching and semantic similarity. It helps job seekers understand how their resume aligns with a target role, identify skill gaps, and explore opportunities to improve their resume.

**Current development status:** Phase 4 completed.

## Overview

Finding a suitable job involves more than submitting a resume. Job seekers need to understand job requirements, identify relevant skills, and present their experience clearly.

Resume AI Analyser helps simplify this process by comparing resume content with a job description and presenting an explainable analysis.

The application combines a Django backend with a React frontend. It uses keyword matching and sentence embeddings to evaluate how closely resume content relates to job requirements.

## Features

- **Resume Analysis:** Upload a PDF resume and analyse it against a job description.
- **Keyword Matching:** Identify relevant skills and terms shared between a resume and a job description.
- **Semantic Matching:** Use sentence embeddings to compare job requirements with relevant resume passages.
- **Match Scoring:** Calculate an overall score using configurable component weights.
- **Skill Gap Identification:** Highlight job requirements that may not be adequately represented in the resume.
- **Evidence-Based Results:** Provide relevant resume excerpts to help users understand the analysis.
- **Optional AI Suggestions:** Generate resume wording suggestions using Claude when explicitly enabled.
- **Regression Testing:** Include a regression test for the personal details section to help protect existing resume-parsing behaviour.

> The match score is an estimate produced by the application's matching logic. It is not an official ATS score and does not guarantee interview selection.

## Technology Stack

| Component | Technologies |
|---|---|
| Backend | Python, Django |
| Frontend | React, Vite, JavaScript |
| Resume processing | PDF text extraction and section parsing |
| Matching | Keyword matching, sentence embeddings |
| Database | SQLite |
| Optional AI integration | Anthropic Claude API |
| Testing | Python/Django tests |
| Version control | Git, GitHub |

## Architecture

```text
                  USER
                    |
                    v
          +-------------------+
          |   React / Vite    |
          |-------------------|
          | Resume Input      |
          | Job Description   |
          | Analysis Results  |
          | Scoring Controls  |
          +-------------------+
                    |
                    | HTTP / API
                    v
          +-------------------+
          | Django Backend    |
          |-------------------|
          | Request Handling  |
          | Resume Processing |
          | Analysis Logic    |
          | Result Generation |
          +-------------------+
                    |
                    v
          +-------------------+
          | Analysis Services |
          |-------------------|
          | Keyword Matching  |
          | Semantic Matching |
          | Result Breakdown  |
          | Optional AI Text  |
          +-------------------+
                    |
                    v
          +-------------------+
          | SQLite Database   |
          | Analysis Records  |
          +-------------------+
```

The React frontend provides the user interface, while Django handles requests and coordinates resume analysis. The analysis services compare job requirements with resume content and return results for display.

## How Resume Matching Works

The application combines keyword matching and semantic similarity.

### 1. Resume and Job Description Input

The user provides a PDF resume and the target job description.

### 2. Resume Text Processing

The backend processes the resume content and identifies relevant passages for comparison.

### 3. Keyword Matching

The application checks for relevant words and skills shared between the resume and job requirements.

### 4. Semantic Matching

Sentence embeddings help identify relevant resume passages even when the wording differs from the job description.

### 5. Score Calculation

The application combines its configured scoring components to calculate a match score. Users can adjust component weights through the interface.

### 6. Results and Skill Gaps

The frontend displays the analysis score and result breakdown, helping users review which requirements are supported by their resume and which may need attention.

### 7. Optional AI Suggestions

When enabled by the user, the optional Claude integration can suggest improvements to selected resume wording. Suggestions should be reviewed for accuracy before being used.

## Getting Started

### Prerequisites

Install the following software:

- Python
- Node.js and npm
- Git

Verify your installations:

```powershell
python --version
node --version
npm --version
git --version
```

### 1. Clone the Repository

```powershell
git clone https://github.com/lokesh051001/resume-ai-analyser.git
cd resume-ai-analyser
```

### 2. Create a Python Virtual Environment

On Windows PowerShell:

```powershell
python -m venv venv
```

Activate the environment:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can run this command for the current terminal session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the environment again.

### 3. Install Backend Dependencies

From the project root, run:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables

The repository includes an `.env.example` file for environment configuration.

For optional Claude suggestions, copy the example file:

```powershell
Copy-Item .env.example .env
```

Configure the relevant environment variables in `.env` using your own credentials.

Claude suggestions are optional and disabled by default. Enable them only when you have configured a valid API key and explicitly want to use the feature.

**Security:** Never commit `.env` or API keys to GitHub. Do not deploy the application with a development-only secret key.

### 5. Apply Database Migrations

From the project root:

```powershell
python manage.py migrate
```

### 6. Start the Django Backend

```powershell
python manage.py runserver
```

The backend will normally be available at:

```text
http://127.0.0.1:8000/
```

Keep this terminal running.

### 7. Start the React Frontend

Open a second terminal and navigate to the frontend directory:

```powershell
cd frontend
npm install
npm run dev
```

Vite will display the local development URL. It is normally:

```text
http://localhost:5173/
```

Open the displayed URL in your browser to use the application.

**Note:** The first run of semantic matching may download the sentence-embedding model. Allow additional time for the initial setup.

## Optional Claude Integration

The application supports optional AI-powered resume wording suggestions through Anthropic's Claude API.

To enable the feature:

1. Configure your API key in `.env`.
2. Set `CLAUDE_SUGGESTIONS_ENABLED=true`.
3. Restart the Django backend.
4. Select the suggestion option in the interface when analysing a resume.

The integration is intended to suggest alternative wording, not invent qualifications or experience.

Review all generated suggestions before using them in a job application.

When this feature is selected, the backend sends limited resume text and skill-gap information to the external API. Do not submit sensitive information unless you understand and accept the associated privacy implications.

## Testing

Run the Django test suite from the project root:

```powershell
python manage.py test
```

For changes to resume parsing, run the relevant regression tests as well.

In particular, the personal details section should continue to behave correctly when changes are made to section detection or extraction logic.

Test changes before publishing a new release.

## Project Development Phases

The repository uses GitHub releases to track development progress.

| Phase | Status | Reference |
|---|---|---|
| Phase 1 | Released | [View Phase 1](https://github.com/lokesh051001/resume-ai-analyser/releases/tag/phase-1) |
| Phase 2 | Released | [View Phase 2](https://github.com/lokesh051001/resume-ai-analyser/releases/tag/phase-2) |
| Phase 3 | Released | [View Phase 3](https://github.com/lokesh051001/resume-ai-analyser/releases/tag/phase-3) |
| Phase 4 | Released | [View Phase 4](https://github.com/lokesh051001/resume-ai-analyser/releases/tag/phase-4) |

### Future Enhancements

Potential future improvements include:

- More robust resume section and skill extraction.
- Expanded regression and automated API tests.
- Improved semantic matching evaluation.
- More detailed and explainable scoring.
- Better handling of different resume formats.
- Job application tracking and status management.
- Dashboard statistics and analysis history.
- Deployment and production configuration.

These are planned enhancements and are not necessarily implemented in the current release.

## Data and Privacy

The current application stores analysis records in SQLite, including the filename, job description, score, and result breakdown. Semantic matching results may include excerpts from the resume.

The optional Claude feature sends selected resume text and skill-gap information to the external API only when the feature is enabled and requested.

Use resumes that you own or have permission to process. Review the code and configuration before deploying the application or processing confidential documents.

## Limitations

- The match score is an estimate and should not be treated as a hiring prediction.
- Keyword and semantic matching may miss relevant skills or incorrectly identify relationships.
- Results depend on resume quality, job description detail, and the configured matching logic.
- Suggested resume wording requires human review.
- The application does not guarantee improved ATS ranking or interview selection.

## Author

**Lokesh Karakambeti**

MCA Graduate | Python and Full-Stack Development

GitHub: [lokesh051001](https://github.com/lokesh051001)

Project Repository: [Resume AI Analyser](https://github.com/lokesh051001/resume-ai-analyser)

---

*Built as a practical full-stack project to explore resume processing, semantic text matching, backend development, and explainable job-description analysis.*
