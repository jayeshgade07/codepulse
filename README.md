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

## 🚀 Local Setup

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

### Option B: Deploying on PythonAnywhere (Persistent SQLite)
1. Sign up for a free account on [PythonAnywhere](https://www.pythonanywhere.com/).
2. Open a **Bash Console** and clone your repo, create a virtual environment, and install dependencies.
3. In the **Web** tab, create a new manual configuration web app pointing to your project directory.
4. Set the virtualenv path under the web configurations.
5. Create a `.env` file in the project folder with your API keys.
6. Edit the auto-generated WSGI configuration file in their editor to load `.env` and start `create_app()`:
   ```python
   from dotenv import load_dotenv
   import sys, os
   path = '/home/yourusername/codepulse'
   sys.path.insert(0, path)
   load_dotenv(os.path.join(path, '.env'))
   from app import create_app
   application = create_app()
   ```
7. Click **Reload** to go live!

---

## 🗄️ Database Schema

**`analyses` table**

| Column | Type | Description |
|---|---|---|
| id | Integer PK | Auto-increment identifier |
| username | String | GitHub username |
| slug | String UNIQUE | URL-safe caching link |
| created_at | DateTime | Generation timestamp |
| profile_data | Text (JSON) | GitHub user profile info |
| repo_data | Text (JSON) | Top repository attributes |
| language_data | Text (JSON) | Language % breakdown |
| commit_activity | Text (JSON) | 26-week commit history array |
| ai_persona | Text | AI-generated persona summary |
| ai_strengths | Text (JSON) | Computed strengths list |
| ai_gaps | Text (JSON) | Identified gaps list |
| ai_suggestions | Text (JSON) | Specific suggestions list |
| ai_score | Integer | 0–100 portfolio score |
| ai_role_fit | Text (JSON) | Career role suggestions |

---

## 🔌 API Endpoints

| Method | URL | Description |
|---|---|---|
| GET | `/` | Landing page |
| POST | `/analyze` | Submit username, trigger Groq analysis |
| GET | `/report/<slug>` | View HTML report |
| GET | `/api/report/<slug>` | JSON API response |
| GET | `/history` | History database log |

---

## 🎤 Interview Questions & Answers

### Q1: Why Flask over Django?
> "This project has a small scope — 4 routes, 1 model. Flask's minimal footprint meant faster development without unnecessary boilerplate. If the project were to scale (user auth, admin panel, complex ORM relationships), Django would be the right call."

### Q2: How does the SQLite caching work?
> "Each analysis is stored in the `analyses` table with a `created_at` timestamp. On `/analyze`, I first query for an existing row with the same username within the last 24 hours. If found, I redirect to the cached report — skipping both GitHub API and Groq API calls. This keeps the app fast and avoids rate limits."

### Q3: Explain the Groq AI integration.
> "I build a structured prompt with the user's GitHub data — repos, languages, stats — and send it to `llama-3.3-70b-versatile` via the Groq SDK. I instruct the model to respond only in JSON with a specific schema (persona, score, strengths, gaps, suggestions, role_fit) and enforce this using Groq's JSON mode. I parse the response with `json.loads()`."

### Q4: What's SQLAlchemy ORM and why use it?
> "SQLAlchemy ORM maps Python classes to database tables. Instead of writing raw SQL like `INSERT INTO analyses VALUES (...)`, I create an `Analysis` object and call `db.session.add()`. It makes the code database-agnostic — I can swap SQLite for PostgreSQL by just changing the `DATABASE_URL` environment variable, with zero code changes."

### Q5: How would you scale this to handle 1000 users/day?
> "Three changes: (1) Replace SQLite with PostgreSQL for concurrent writes. (2) Add a task queue like Celery + Redis so analysis jobs run async — the user gets a 'processing' page instead of waiting 10 seconds. (3) Cache GitHub API responses in Redis with a 1-hour TTL to avoid hitting rate limits."

### Q6: What is OOP used in this project?
> "The `Analysis` model is an OOP class with `@property` decorators that serialize/deserialize JSON columns transparently. The service layer (`github_service.py`, `ai_service.py`) uses pure functions with single responsibility — easy to test in isolation. The Flask Blueprint (`routes.py`) encapsulates all route handlers."

---

## 📄 License

MIT License — free to use, modify, and deploy.
