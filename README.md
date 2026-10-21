# Resume AI Analyser

Django app that parses PDF resumes, matches them against a job description,
and produces a configurable score with missing-skills analysis.

## Run locally
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
