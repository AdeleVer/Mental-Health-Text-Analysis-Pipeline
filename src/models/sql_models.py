import os
import secrets
from datetime import datetime, timezone
from cryptography.fernet import Fernet

from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db

# ADD: Encryption key (use from .env in production!)
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
if not ENCRYPTION_KEY:
    raise ValueError("ENCRYPTION_KEY environment variable is required")

cipher_suite = Fernet(ENCRYPTION_KEY)

# ADD: Mixin for text encryption
class EncryptedTextMixin:
    _original_text = db.Column('original_text', db.LargeBinary)
    
    @property
    def original_text(self):
        """Decrypt text when accessing property"""
        if self._original_text:
            try:
                return cipher_suite.decrypt(self._original_text).decode('utf-8')
            except Exception:
                return "[Decryption Error]"
        return None

    @original_text.setter
    def original_text(self, value):
        """Encrypt text before saving to database"""
        if value:
            self._original_text = cipher_suite.encrypt(value.encode('utf-8'))
        else:
            self._original_text = None

# ADD: User model for authentication
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    api_key = db.Column(db.String(100), unique=True, default=lambda: secrets.token_urlsafe(32))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_therapist = db.Column(db.Boolean, default=False)
    
    # ADD: Relationship with analyses (one-to-many)
    analyses = db.relationship('AnalysisResult', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash password before saving"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Return user data as dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'api_key': self.api_key,
            'is_therapist': self.is_therapist,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AnalysisResult(db.Model, EncryptedTextMixin):  # ADD: Inherit encryption mixin
    __tablename__ = 'analysis_results'
    
    id = db.Column(db.Integer, primary_key=True)
       # ADD: Relationship with user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
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
            'created_at': self.created_at.isoformat() if self.created_at else None,
            # ADD: User ID for convenience
            'user_id': self.user_id
        }