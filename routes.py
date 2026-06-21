import uuid
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, abort
from models import db, Analysis
from services.github_service import (
    get_user_profile,
    get_user_repos,
    get_language_breakdown,
    get_commit_activity,
    compute_profile_stats,
)
from services.ai_service import analyze_profile
import json

main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET"])
def index():
    recent = (
        Analysis.query.order_by(Analysis.created_at.desc()).limit(6).all()
    )
    return render_template("index.html", recent=recent)


@main_bp.route("/analyze", methods=["POST"])
def analyze():
    username = request.form.get("username", "").strip().lower()
    if not username:
        return redirect(url_for("main.index"))

    # Check cache (same username analyzed in last 24h)
    from datetime import datetime, timedelta
    cutoff = datetime.utcnow() - timedelta(hours=24)
    cached = (
        Analysis.query.filter_by(username=username)
        .filter(Analysis.created_at >= cutoff)
        .order_by(Analysis.created_at.desc())
        .first()
    )
    if cached:
        return redirect(url_for("main.report", slug=cached.slug))

    try:
        # Fetch GitHub data
        profile = get_user_profile(username)
        repos = get_user_repos(username)
        languages = get_language_breakdown(repos)
        commit_activity = get_commit_activity(username, repos)
        stats = compute_profile_stats(profile, repos)

        # AI analysis
        ai_result = analyze_profile(profile, repos, stats, languages)

        # Persist
        slug = f"{username}-{uuid.uuid4().hex[:8]}"
        analysis = Analysis(
            username=username,
            slug=slug,
            ai_persona=ai_result["persona"],
            ai_strengths=json.dumps(ai_result["strengths"]),
            ai_gaps=json.dumps(ai_result["gaps"]),
            ai_suggestions=json.dumps(ai_result["suggestions"]),
            ai_score=ai_result["score"],
            ai_role_fit=json.dumps(ai_result["role_fit"]),
        )
        analysis.profile_data = profile
        analysis.repo_data = repos
        analysis.language_data = languages
        analysis.commit_activity = commit_activity

        db.session.add(analysis)
        db.session.commit()

        return redirect(url_for("main.report", slug=slug))

    except ValueError as e:
        return render_template("index.html", error=str(e), recent=[])
    except Exception as e:
        return render_template("index.html", error=f"Analysis failed: {str(e)}", recent=[])


@main_bp.route("/report/<slug>")
def report(slug):
    analysis = Analysis.query.filter_by(slug=slug).first_or_404()
    return render_template("report.html", a=analysis)


@main_bp.route("/api/report/<slug>")
def api_report(slug):
    """JSON endpoint — useful for testing."""
    analysis = Analysis.query.filter_by(slug=slug).first_or_404()
    return jsonify({
        "username": analysis.username,
        "score": analysis.ai_score,
        "persona": analysis.ai_persona,
        "strengths": analysis.strengths_list,
        "gaps": analysis.gaps_list,
        "suggestions": analysis.suggestions_list,
        "role_fit": analysis.role_fit_list,
        "languages": analysis.language_data,
        "top_repos": analysis.repo_data[:5],
    })


@main_bp.route("/history")
def history():
    all_analyses = Analysis.query.order_by(Analysis.created_at.desc()).limit(50).all()
    return render_template("history.html", analyses=all_analyses)
