from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


class Analysis(db.Model):
    """Stores cached GitHub profile analysis results."""

    __tablename__ = "analyses"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, index=True)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # GitHub raw data (stored as JSON strings)
    _profile_data = db.Column("profile_data", db.Text, nullable=False)
    _repo_data = db.Column("repo_data", db.Text, nullable=False)
    _language_data = db.Column("language_data", db.Text, nullable=False)
    _commit_activity = db.Column("commit_activity", db.Text, nullable=False)

    # AI-generated report
    ai_persona = db.Column(db.Text, nullable=False)
    ai_strengths = db.Column(db.Text, nullable=False)   # JSON list
    ai_gaps = db.Column(db.Text, nullable=False)         # JSON list
    ai_suggestions = db.Column(db.Text, nullable=False)  # JSON list
    ai_score = db.Column(db.Integer, nullable=False, default=0)
    ai_role_fit = db.Column(db.Text, nullable=False)    # JSON list

    @property
    def profile_data(self):
        return json.loads(self._profile_data)

    @profile_data.setter
    def profile_data(self, value):
        self._profile_data = json.dumps(value)

    @property
    def repo_data(self):
        return json.loads(self._repo_data)

    @repo_data.setter
    def repo_data(self, value):
        self._repo_data = json.dumps(value)

    @property
    def language_data(self):
        return json.loads(self._language_data)

    @language_data.setter
    def language_data(self, value):
        self._language_data = json.dumps(value)

    @property
    def commit_activity(self):
        return json.loads(self._commit_activity)

    @commit_activity.setter
    def commit_activity(self, value):
        self._commit_activity = json.dumps(value)

    @property
    def strengths_list(self):
        return json.loads(self.ai_strengths)

    @property
    def gaps_list(self):
        return json.loads(self.ai_gaps)

    @property
    def suggestions_list(self):
        return json.loads(self.ai_suggestions)

    @property
    def role_fit_list(self):
        return json.loads(self.ai_role_fit)

    def __repr__(self):
        return f"<Analysis username={self.username} slug={self.slug}>"
