import os
import requests
from collections import defaultdict


GITHUB_API_BASE = "https://api.github.com"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")


def _headers():
    h = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return h


def get_user_profile(username: str) -> dict:
    """Fetch basic GitHub user profile."""
    resp = requests.get(f"{GITHUB_API_BASE}/users/{username}", headers=_headers(), timeout=10)
    if resp.status_code == 404:
        raise ValueError(f"GitHub user '{username}' not found.")
    resp.raise_for_status()
    data = resp.json()
    return {
        "login": data.get("login"),
        "name": data.get("name") or data.get("login"),
        "bio": data.get("bio") or "",
        "avatar_url": data.get("avatar_url"),
        "public_repos": data.get("public_repos", 0),
        "followers": data.get("followers", 0),
        "following": data.get("following", 0),
        "created_at": data.get("created_at", ""),
        "location": data.get("location") or "",
        "blog": data.get("blog") or "",
        "company": data.get("company") or "",
    }


def get_user_repos(username: str) -> list:
    """Fetch up to 100 repos sorted by stars."""
    resp = requests.get(
        f"{GITHUB_API_BASE}/users/{username}/repos",
        headers=_headers(),
        params={"per_page": 100, "sort": "updated", "direction": "desc"},
        timeout=10,
    )
    resp.raise_for_status()
    repos = resp.json()

    result = []
    for r in repos:
        if r.get("fork"):
            continue  # skip forks
        result.append({
            "name": r["name"],
            "description": r.get("description") or "",
            "language": r.get("language") or "Unknown",
            "stars": r.get("stargazers_count", 0),
            "forks": r.get("forks_count", 0),
            "has_readme": True,  # approximated
            "topics": r.get("topics", []),
            "updated_at": r.get("updated_at", ""),
            "size": r.get("size", 0),
            "open_issues": r.get("open_issues_count", 0),
        })

    result.sort(key=lambda x: x["stars"], reverse=True)
    return result[:20]  # top 20


def get_language_breakdown(repos: list) -> dict:
    """Compute language distribution from repos list."""
    lang_count = defaultdict(int)
    for repo in repos:
        lang = repo.get("language") or "Unknown"
        lang_count[lang] += 1

    total = sum(lang_count.values()) or 1
    return {
        lang: round((count / total) * 100, 1)
        for lang, count in sorted(lang_count.items(), key=lambda x: -x[1])
        if lang != "Unknown"
    }


def get_commit_activity(username: str, repos: list) -> list:
    """Get commit activity for the top 5 repos (weekly, last 26 weeks)."""
    activity = [0] * 26
    checked = 0

    for repo in repos[:5]:
        try:
            resp = requests.get(
                f"{GITHUB_API_BASE}/repos/{username}/{repo['name']}/stats/commit_activity",
                headers=_headers(),
                timeout=10,
            )
            if resp.status_code == 200:
                weeks = resp.json()
                for i, week in enumerate(weeks[-26:]):
                    activity[i] += week.get("total", 0)
                checked += 1
        except Exception:
            continue

    return activity


def compute_profile_stats(profile: dict, repos: list) -> dict:
    """Compute derived stats for scoring."""
    total_stars = sum(r["stars"] for r in repos)
    total_forks = sum(r["forks"] for r in repos)
    repos_with_desc = sum(1 for r in repos if r["description"])
    repos_with_topics = sum(1 for r in repos if r["topics"])
    top_lang = ""
    lang_counts = defaultdict(int)
    for r in repos:
        if r["language"] != "Unknown":
            lang_counts[r["language"]] += 1
    if lang_counts:
        top_lang = max(lang_counts, key=lang_counts.get)

    return {
        "total_stars": total_stars,
        "total_forks": total_forks,
        "repo_count": len(repos),
        "repos_with_desc_pct": round((repos_with_desc / max(len(repos), 1)) * 100),
        "repos_with_topics_pct": round((repos_with_topics / max(len(repos), 1)) * 100),
        "top_language": top_lang,
        "account_age_years": _account_age(profile.get("created_at", "")),
    }


def _account_age(created_at: str) -> float:
    if not created_at:
        return 0
    from datetime import datetime
    try:
        created = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
        delta = datetime.utcnow() - created
        return round(delta.days / 365, 1)
    except Exception:
        return 0
