# Resume AI Analyser

Django parses PDF resumes and compares them with a job description using keyword matching and local sentence embeddings. A React/Vite page displays the score and lets you adjust component weights. Optional Claude wording suggestions are available on an explicit opt-in basis.

## Run on Windows

Install dependencies once from the project root:

```bat
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
```

Keep two terminals open, with the virtual environment activated in the Django terminal:

```bat
:: Terminal 1, from D:\resume_ai
venv\Scripts\activate
python manage.py runserver
```

```bat
:: Terminal 2
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite (normally http://localhost:5173). Semantic matching uses `sentence-transformers`; its first run may download the model. Start Django inside the activated environment so matching is available.

## Tune the semantic cutoff (Step 3.5)

The labelled examples are in `analyser/data/semantic_labels.json`. They include clear matches and non-matches but are deliberately small teaching examples, not a statistically representative benchmark. Review or replace labels with examples you have permission to use.

With the venv active, from the project root run:

```bat
python scripts\tune_semantic_threshold.py
```

The script compares the embedding similarity for each labelled pair and prints accuracy, precision, and recall at cutoffs 0.30 through 0.70. The current 24 examples include several near-misses. In the latest run, 0.40 gave 79% accuracy, 73% precision, and 80% recall; 0.30 gave higher accuracy and recall (83% and 100%) but lower precision (71%). The production cutoff is set provisionally to 0.40 as a compromise. This is a small, curated set, so add examples from your use cases before relying on it. The line-pair calibration is simpler than production matching, which compares each job requirement with the best resume passage. To change production matching, update `THRESHOLD` in `analyser/services/semantic_matcher.py` and keep `STRONG_THRESHOLD` at or above it.

## Optional Claude wording suggestions

Copy `.env.example` to `.env`, add your own key, and set `CLAUDE_SUGGESTIONS_ENABLED=true`. Restart Django after changing `.env`. The feature starts disabled and the React form requires an explicit checkbox on each upload. When selected, the backend sends up to 10,000 characters of experience, project, and summary text plus skill gaps to Anthropic's Messages API. The PDF and its text are not saved by this feature. Treat suggestions as drafts and review them before use.

The response is limited to five suggestions and checked for source lines and new numeric claims. This cannot prove that every rewording is factually safe. The endpoint allows five requests per client address per hour using Django's local-memory cache; a deployment with multiple workers needs a shared rate-limit store and appropriate privacy/security settings. Keep `.env` and API keys out of Git. Do not deploy with the development `SECRET_KEY` fallback.

## Data and privacy

Analysis records store the filename, job description, score, and result breakdown in SQLite. The PDF is not saved. Semantic evidence snippets in saved results are excerpts from the resume. Use only resumes you own or have permission to process.
