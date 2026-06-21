import os
import json
import groq

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")


def analyze_profile(profile: dict, repos: list, stats: dict, languages: dict) -> dict:
    """
    Send GitHub profile data to Groq and get structured AI analysis.
    Returns dict with persona, strengths, gaps, suggestions, score, role_fit.
    """
    client = groq.Groq(api_key=GROQ_API_KEY)

    top_repos = [
        f"- {r['name']} ({r['language']}, ⭐{r['stars']}): {r['description'][:80] if r['description'] else 'No description'}"
        for r in repos[:8]
    ]

    lang_str = ", ".join([f"{l} ({p}%)" for l, p in list(languages.items())[:6]])

    prompt = f"""You are a senior engineering recruiter and developer mentor. Analyze this GitHub profile and provide a structured JSON report.

GITHUB PROFILE DATA:
- Username: {profile['login']}
- Name: {profile['name']}
- Bio: {profile['bio'] or 'Not provided'}
- Public repos: {profile['public_repos']}
- Followers: {profile['followers']}
- Account age: {stats['account_age_years']} years
- Total stars earned: {stats['total_stars']}
- Location: {profile['location'] or 'Not specified'}

TOP REPOSITORIES:
{chr(10).join(top_repos)}

LANGUAGE DISTRIBUTION:
{lang_str or 'No data'}

DOCUMENTATION QUALITY:
- {stats['repos_with_desc_pct']}% repos have descriptions
- {stats['repos_with_topics_pct']}% repos have topics/tags

Respond ONLY with a valid JSON object (no markdown, no extra text) in this exact structure:
{{
  "persona": "A 2-3 sentence developer persona narrative. What kind of developer are they? What do they build?",
  "score": <integer 0-100 representing overall portfolio quality>,
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "gaps": ["gap 1", "gap 2", "gap 3"],
  "suggestions": ["actionable suggestion 1", "actionable suggestion 2", "actionable suggestion 3", "actionable suggestion 4"],
  "role_fit": ["Best Fit Role 1", "Best Fit Role 2", "Best Fit Role 3"]
}}

Be specific, honest, and constructive. Base everything on the actual data provided."""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a senior engineering recruiter and developer mentor. You must respond ONLY with a valid JSON object matching the requested schema.",
            },
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        max_tokens=1000,
    )

    raw = completion.choices[0].message.content.strip()

    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    data = json.loads(raw)

    return {
        "persona": data.get("persona", ""),
        "score": int(data.get("score", 50)),
        "strengths": data.get("strengths", []),
        "gaps": data.get("gaps", []),
        "suggestions": data.get("suggestions", []),
        "role_fit": data.get("role_fit", []),
    }
