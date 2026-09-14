import re
from datetime import datetime, timedelta, timezone

def is_recent_france_travail(date_creation_iso: str, max_hours: int = 48) -> bool:
    if not date_creation_iso:
        return False
    try:
        posted = datetime.fromisoformat(date_creation_iso.replace("Z", "+00:00"))
    except ValueError:
        return False
    now = datetime.now(timezone.utc)
    return (now - posted) <= timedelta(hours=max_hours)

def is_recent_indeed_text(text: str, max_hours: int = 24) -> bool:
    if not text:
        return False
    text = text.lower()

    # "à l'instant", "aujourd'hui" -> considéré récent
    if "instant" in text or "aujourd" in text:
        return True

    # "il y a X jour(s)"
    match = re.search(r"il y a (\d+)\+?\s*jour", text)
    if match:
        days = int(match.group(1))
        return (days * 24) <= max_hours

    # "il y a X heure(s)"
    match = re.search(r"il y a (\d+)\+?\s*heure", text)
    if match:
        hours = int(match.group(1))
        return hours <= max_hours

    return False