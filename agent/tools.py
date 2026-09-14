from storage.db import get_connection
from main import run as run_scraping
from matching.scorer import score_all_offers

def search_offers(min_score: float = 0.0, location: str = None, keyword: str = None, limit: int = 10) -> list[dict]:
    """Cherche des offres en DB selon des critères."""
    query = "SELECT title, company, location, score, url, source, posted_date FROM offers WHERE score >= ?"
    params = [min_score]

    if location:
        query += " AND location LIKE ?"
        params.append(f"%{location}%")
    if keyword:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f"%{keyword}%", f"%{keyword}%"])

    query += " ORDER BY score DESC LIMIT ?"
    params.append(limit)

    with get_connection() as conn:
        cursor = conn.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_stats() -> dict:
    """Retourne des stats globales sur la base."""
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM offers").fetchone()[0]
        scored = conn.execute("SELECT COUNT(*) FROM offers WHERE score IS NOT NULL").fetchone()[0]
        avg_score = conn.execute("SELECT AVG(score) FROM offers WHERE score IS NOT NULL").fetchone()[0]
        by_source = conn.execute("SELECT source, COUNT(*) FROM offers GROUP BY source").fetchall()
    return {
        "total_offers": total,
        "scored_offers": scored,
        "avg_score": round(avg_score, 3) if avg_score else None,
        "by_source": dict(by_source),
    }

def force_refresh() -> str:
    """Force un scraping + scoring immédiat (usage ponctuel, peut prendre 1-2 min)."""
    run_scraping()
    score_all_offers()
    return "Scraping et scoring terminés."

# Format Ollama (compatible OpenAI-style function schema)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_offers",
            "description": "Recherche des offres d'emploi dans la base de données selon score minimum, localisation, ou mot-clé.",
            "parameters": {
                "type": "object",
                "properties": {
                    "min_score": {"type": "number", "description": "Score de pertinence minimum (0 à 1)"},
                    "location": {"type": "string", "description": "Filtrer par localisation (ex: Paris)"},
                    "keyword": {"type": "string", "description": "Mot-clé à chercher dans titre/description"},
                    "limit": {"type": "integer", "description": "Nombre max de résultats"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_stats",
            "description": "Retourne des statistiques globales sur la base d'offres (total, scorées, moyenne, répartition par source).",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "force_refresh",
            "description": "Force un scraping immédiat de nouvelles offres suivi du scoring. Peut prendre 1-2 minutes. Uniquement si demandé explicitement.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]

TOOL_FUNCTIONS = {
    "search_offers": search_offers,
    "get_stats": get_stats,
    "force_refresh": force_refresh,
}