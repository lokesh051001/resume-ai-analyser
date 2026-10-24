"""Opt-in Claude suggestions. Resume text is sent only for this request."""
import json
import re
import urllib.error
import urllib.request

from django.conf import settings

from .skill_matcher import find_skills

NUMBER_PATTERN = r"\d+(?:[.,]\d+)?%?"
EXPECTED_KEYS = {"original", "suggested_rewrite", "reason", "question"}
FORMAT_ERROR = "Claude returned an unexpected response format."
DETAILS_ERROR = "Claude returned a rewrite with unsupported details."


class SuggestionError(Exception):
    pass


def _validate(payload, source_lines):
    if not isinstance(payload, dict) or set(payload) != {"suggestions"}:
        raise SuggestionError(FORMAT_ERROR)
    suggestions = payload["suggestions"]
    if not isinstance(suggestions, list) or len(suggestions) > 5:
        raise SuggestionError(FORMAT_ERROR)

    validated = []
    for item in suggestions:
        if not isinstance(item, dict) or set(item) != EXPECTED_KEYS:
            raise SuggestionError(FORMAT_ERROR)
        if not all(isinstance(item[k], str) for k in item):
            raise SuggestionError(FORMAT_ERROR)

        original = item["original"]
        rewrite = item["suggested_rewrite"]

        if original.strip() not in source_lines:
            raise SuggestionError("Claude returned a suggestion that did not match the supplied resume text.")
        if not rewrite.strip():
            raise SuggestionError(DETAILS_ERROR)

        # Reject new numeric claims. This catches invented metrics and dates.
        if not set(re.findall(NUMBER_PATTERN, rewrite)) <= set(re.findall(NUMBER_PATTERN, original)):
            raise SuggestionError(DETAILS_ERROR)

        # Reject technologies the original line didn't mention (vocabulary-based, so a partial guard).
        if not find_skills(rewrite) <= find_skills(original):
            raise SuggestionError(DETAILS_ERROR)

        validated.append({k: item[k].strip() for k in ("original", "suggested_rewrite", "reason", "question")})

    return {"suggestions": validated, "draft_notice": "AI-generated drafts. Review every detail before using."}


def create_suggestions(sections, missing, not_demonstrated):
    if not settings.CLAUDE_SUGGESTIONS_ENABLED or not settings.ANTHROPIC_API_KEY:
        raise SuggestionError("AI suggestions are disabled. Configure the Claude API key and enable the feature in .env.")

    source_lines = [
        line.strip() for section in ("experience", "projects", "summary")
        for line in sections.get(section, "").splitlines() if len(line.split()) >= 4
    ]
    source = "\n".join(source_lines)[:10000]
    if not source:
        raise SuggestionError("No experience, project, or summary text was found to improve.")
    # Validate against exactly the lines sent to Claude, never unseen content.
    source_lines = source.splitlines()

    prompt = {
        "resume_sections": source,
        "missing_skills": sorted(missing),
        "listed_but_not_demonstrated_skills": sorted(not_demonstrated),
    }
    body = json.dumps({
        "model": settings.ANTHROPIC_MODEL,
        "max_tokens": 1200,
        "system": (
            "You improve resume wording without changing facts. Never invent or imply experience, "
            "metrics, dates, outcomes, responsibilities, or technologies. Rewrite only lines present "
            "in the supplied sections. Do not claim a missing or listed-only skill was used. If a "
            "stronger bullet needs a missing detail, keep the wording factual and put a concise question "
            "in question. Return only JSON shaped as {\"suggestions\":[{\"original\":string,"
            "\"suggested_rewrite\":string,\"reason\":string,\"question\":string}]}; at most five items."
        ),
        "messages": [{"role": "user", "content": json.dumps(prompt)}],
    }).encode("utf-8")
    request = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=body, method="POST",
        headers={
            "content-type": "application/json",
            "x-api-key": settings.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=35) as response:
            response_data = json.loads(response.read().decode("utf-8"))
        text = "".join(
            block.get("text", "")
            for block in response_data.get("content", [])
            if block.get("type") == "text"
        ).strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
        result = json.loads(text)
        return _validate(result, set(source_lines))
    except SuggestionError:
        raise
    except urllib.error.HTTPError as error:
        # Keep diagnostics useful without exposing the key or any resume content.
        try:
            provider_error = json.loads(error.read().decode("utf-8"))
            detail = provider_error.get("error", {}).get("message", "")
            if not isinstance(detail, str):
                detail = ""
            detail = " ".join(detail.split())
            detail = detail.replace(settings.ANTHROPIC_API_KEY, "[redacted]")
            for line in source_lines:
                detail = detail.replace(" ".join(line.split()), "[resume text redacted]")
            detail = detail[:240]
        except (json.JSONDecodeError, UnicodeDecodeError, AttributeError, TypeError):
            detail = ""
        if error.code in (401, 403):
            message = f"Anthropic rejected the API key or its permissions (HTTP {error.code}). Check the key in .env."
        elif error.code == 400:
            message = "Anthropic rejected the request (HTTP 400)."
        elif error.code == 429:
            message = "Anthropic rate limit or account quota reached (HTTP 429). Try again later or check your account."
        else:
            message = f"Anthropic returned HTTP {error.code}. Try again later."
        if detail:
            message = f"{message} Details: {detail}"
        raise SuggestionError(message)
    except urllib.error.URLError:
        raise SuggestionError("Could not connect to Anthropic. Check internet access and try again.")
    except (TimeoutError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        raise SuggestionError("Anthropic returned an unreadable response. The analysis is still available.")