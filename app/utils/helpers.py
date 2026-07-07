import re


def parse_blood_pressure(bp: str):
    """'130/72' -> (130, 72)"""
    match = re.match(r"^\s*(\d{2,3})\s*/\s*(\d{2,3})\s*$", str(bp))
    if not match:
        raise ValueError(f"Invalid blood pressure format: {bp}")
    return int(match.group(1)), int(match.group(2))


def risk_bucket(score: float) -> str:
    if score >= 0.66:
        return "High"
    if score >= 0.33:
        return "Medium"
    return "Low"


def paginate(total: int, page: int, page_size: int):
    total_pages = max(1, (total + page_size - 1) // page_size)
    page = max(1, min(page, total_pages))
    offset = (page - 1) * page_size
    return page, total_pages, offset
