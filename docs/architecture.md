\# Architecture



\## Analysis pipeline



1\. \*\*Extract text:\*\* PDFs with pdfplumber. If a full-width header sits above two columns, the

&#x20;  header is read first, then each column separately. DOCX paragraphs and table cells are read

&#x20;  with python-docx.

2\. \*\*Split into sections:\*\* headings are matched against an alias table (for example

&#x20;  "Career Objective" becomes `summary`). Personal details form their own section, which is

&#x20;  never scored or embedded.

3\. \*\*Keyword matching:\*\* a skills vocabulary with aliases and whole-word matching, so `java`

&#x20;  does not match inside `javascript`.

4\. \*\*Semantic matching:\*\* each job-requirement line is compared with resume passages using

&#x20;  local sentence embeddings. A requirement counts as met above a similarity threshold, and the

&#x20;  closest passage is kept as evidence.

5\. \*\*Score:\*\* five components, each 0 to 1, combined with configurable weights. A component that

&#x20;  does not apply (for example no "nice to have" section) is skipped and the rest are rescaled.



| Component | Default weight |

|---|---|

| Required skills | 40 |

| Semantic match | 20 |

| Evidence in projects or experience | 15 |

| Completeness | 15 |

| Preferred skills | 10 |



\## Data model



\- `User` has many `JobApplication` and many `Analysis`.

\- `JobApplication` has many `Analysis`. Deleting an application keeps its analyses.

\- `Analysis` stores the score and a JSON breakdown, never the resume file.



\## Design decisions



\- \*\*Rules before models.\*\* Section and skill detection are deterministic and explainable.

&#x20; Embeddings and the language model are added only where rules cannot do the job.

\- \*\*Ownership on the server.\*\* Every query filters on the logged-in user, so another user's

&#x20; record is a 404, not a hidden row. Clients cannot set `owner`.

\- \*\*The optional AI is checked, not trusted.\*\* Output must be valid JSON, quote a line that was

&#x20; actually sent, and add no new numbers or vocabulary skills.

\- \*\*Optional parts fail soft.\*\* If semantic matching or the Claude call fails, the analysis

&#x20; still completes.



\## Testing



Tests use Django's test runner and DRF's `APITestCase`. They cover ownership isolation,

authentication, upload validation (size, extension and file contents), scoring, section

parsing, DOCX extraction, the dashboard, and the suggestion validator with a mocked provider.

