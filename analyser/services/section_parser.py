import re

# Map many possible heading names to one standard section name.
SECTION_ALIASES = {
    "summary": ["career objective", "objective", "summary", "professional summary", "profile", "about me"],
    "education": ["education", "academic background", "qualifications"],
    "skills": ["technical skills", "skills", "key skills", "core competencies"],
    "experience": ["experience", "work experience", "professional experience", "internships", "employment history"],
    "projects": ["academic projects", "projects", "personal projects"],
    "certifications": ["certificates", "certifications", "courses"],
    "interests": ["interests", "hobbies"],
}

# Reverse lookup: "technical skills" -> "skills"
_HEADING_TO_SECTION = {
    alias: section
    for section, aliases in SECTION_ALIASES.items()
    for alias in aliases
}


def _match_heading(line: str):
    """Return the standard section name if this line is a heading, else None."""
    cleaned = re.sub(r"[^a-z ]", "", line.lower()).strip()
    return _HEADING_TO_SECTION.get(cleaned)


def split_sections(text: str) -> dict:
    """Split resume text into {section_name: text}. Lines before the first heading go under 'header'."""
    sections = {"header": []}
    current = "header"

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        section = _match_heading(line)
        if section:
            current = section
            sections.setdefault(current, [])
        else:
            sections[current].append(line)

    return {name: "\n".join(lines) for name, lines in sections.items()}
