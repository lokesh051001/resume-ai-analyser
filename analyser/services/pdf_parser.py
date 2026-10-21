import pdfplumber


def _extract_page(page) -> str:
    """Extract a page: full-width header on top, two columns below."""
    width, height = page.width, page.height
    mid = width / 2

    # Words that straddle the midline can't belong to either column.
    # Only look in the top quarter of the page, where headers live.
    crossers = [
        w for w in page.extract_words()
        if w["x0"] < mid < w["x1"] and w["top"] < height * 0.25
    ]
    header_bottom = max((w["bottom"] for w in crossers), default=0)
    if header_bottom:
        header_bottom += 1  # small margin so we don't clip the last line

    header = ""
    if header_bottom:
        header = page.crop((0, 0, width, header_bottom)).extract_text() or ""

    left = page.crop((0, header_bottom, mid, height)).extract_text() or ""
    right = page.crop((mid, header_bottom, width, height)).extract_text() or ""

    return "\n".join(part for part in (header, left, right) if part)


def extract_text(file, two_column: bool = False) -> str:
    """Return all text from a PDF (a path or file-like object)."""
    pages = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            if two_column:
                pages.append(_extract_page(page))
            else:
                pages.append(page.extract_text() or "")
    return "\n".join(pages).strip()