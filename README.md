# ⚡ CodePulse — AI GitHub Portfolio Analyzer

> A Flask web app that analyzes any GitHub developer profile using the Groq AI API (`llama-3.3-70b-versatile`) to generate a portfolio score, developer persona, skill gaps, and career suggestions — with custom visual charts and a shareable report URL.

**Live demo:** `https://your-app-url.onrender.com`

---

## 📸 Features

| Feature | Details |
|---|---|
| 🧠 Groq AI Persona | Llama 3.3 generates a 2–3 sentence developer identity summary |
| 📊 Language Breakdown | Doughnut chart of language distribution across repos |
| 📈 Commit Activity | 26-week activity bar chart from your top repos |
| 🎯 Portfolio Score | 0–100 rating of portfolio quality |
| ⚡ Role Fit | Top 3 career roles based on actual work |
| 🔗 Shareable URL | Permanent cached link per report — send to recruiters |
| 💾 SQLite Caching | Results cached 24h to avoid API rate limits |

---

## 🏗️ Project Structure

```
codepulse/
├── app.py                  # Flask app factory
├── models.py               # SQLAlchemy ORM (Analysis model)
├── routes.py               # Flask Blueprint (all routes)
├── services/
│   ├── github_service.py   # GitHub REST API integrations
│   └── ai_service.py       # Groq AI analysis pipeline
├── templates/
│   ├── base.html           # Base layout
│   ├── index.html          # Landing page
│   ├── report.html         # Report dashboard (Chart.js)
│   └── history.html        # Past analyses log
├── static/
│   └── css/style.css       # Custom styling
├── requirements.txt        # Python package dependencies
├── Procfile                # WSGI web server config
├── railway.toml            # Platform deployment configurations
└── .env.example            # Environment variables template
```

---

 Local Setup

### 1. Clone and create virtual environment
```bash
git clone https://github.com/YOUR_USERNAME/codepulse.git
cd codepulse
python -m venv venv
source venv/bin/activate        # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Set up environment variables
```bash
cp .env.example .env
# Open .env and fill in your values
```

You need:
- **GROQ_API_KEY** — Get a free key from the [Groq Console](https://console.groq.com)
- **GITHUB_TOKEN** — Optional but recommended. Get from [GitHub Settings](https://github.com/settings/tokens) (no scopes needed)
- **SECRET_KEY** — Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`

### 3. Run
```bash
python app.py
# Open http://localhost:5000 in your browser
```

---

## ☁️ Deploy to the Web (100% Free)

### Option A: Deploying on Render (Easiest)
1. Push your repository to GitHub.
2. Sign in to [Render](https://render.com) and create a **New Web Service**.
3. Link your GitHub repository.
4. Configure the settings:
   - **Runtime:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn "app:create_app()" --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
5. In **Advanced**, add the environment variables: `GROQ_API_KEY`, `SECRET_KEY`, and `GITHUB_TOKEN` (optional).
6. Click **Create Web Service**.

*Note: Free tier instances spin down after 50 seconds of inactivity, which causes a 30-50s loading delay on first startup.*



*

---

---

