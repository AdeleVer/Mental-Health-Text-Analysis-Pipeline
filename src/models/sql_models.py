from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class AnalysisResult(db.Model):
    __tablename__ = 'analysis_results'
    
    id = db.Column(db.Integer, primary_key=True)
    original_text = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(2), nullable=False)
    sentiment = db.Column(db.String(20), nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    emotions = db.Column(db.Text, default='[]')
    skills = db.Column(db.Text, default='[]')
    distortions = db.Column(db.Text, default='[]')

    def __repr__(self):
        return f'<AnalysisResult {self.id}: {self.sentiment}>'

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'original_text': self.original_text,
            'language': self.language,
            'sentiment': self.sentiment,
            'confidence_score': self.confidence_score,
            'emotions': json.loads(self.emotions),
            'skills': json.loads(self.skills),
            'distortions': json.loads(self.distortions),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }