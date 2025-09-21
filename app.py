"""
Flask server for Mental Health Text Analysis API.
"""

import logging
import os
from flask import Flask, request, jsonify, render_template 
from flask_sqlalchemy import SQLAlchemy 
from dotenv import load_dotenv
import json 

from extensions import db 

load_dotenv() 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///instance/mental_health_analysis.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

from src.models.sql_models import AnalysisResult, User
from src.api.models import AnalysisRequest
from src.api.yandex_gpt import get_yandex_gpt_client
from src.auth.utils import token_required
from src.auth.routes import auth_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')

@app.route('/')
def home():
    """Render main page with analysis form."""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
@token_required  # ADD: Protect endpoint with JWT authentication
def analyze_text(user_id):
    """Analyze text using YandexGPT API."""
    try:
        client = get_yandex_gpt_client()
        if client is None:
            return jsonify({"error": "YandexGPT client not configured"}), 500
    
        request_data = request.get_json()
        analysis_request = AnalysisRequest(**request_data)
        logger.info(f"User {user_id} analyzing text: {analysis_request.text[:50]}...")
        
        analysis_result = client.analyze_text(
            text=analysis_request.text,
            language=analysis_request.language
        )
        result_dict = analysis_result.model_dump()
        
        db_record = AnalysisResult(
            user_id=user_id,
            original_text=analysis_request.text,
            language=analysis_request.language,
            sentiment=result_dict['sentiment'],
            confidence_score=result_dict['confidence_score'],
            emotions=json.dumps(result_dict['entities']['emotions']),
            skills=json.dumps(result_dict['entities']['skills']),
            distortions=json.dumps(result_dict['distortions'])
        )
        
        db.session.add(db_record)
        db.session.commit()
        logger.info(f"Analysis result saved for user: {user_id}")

        return jsonify(analysis_result.model_dump())
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Analysis failed", "details": str(e)}), 500
    
# ADD: User profile endpoint (protected)
@app.route('/api/profile', methods=['GET'])
@token_required
def get_user_profile(user_id):
    """Get current user profile information."""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        return jsonify(user.to_dict())
        
    except Exception as e:
        logger.error(f"Error fetching user profile: {str(e)}")
        return jsonify({"error": "Failed to fetch profile", "details": str(e)}), 500

# ADD: User analysis history endpoint (protected)
@app.route('/api/analyses', methods=['GET'])
@token_required
def get_user_analyses(user_id):
    """Get analysis history for current user."""
    try:
        analyses = AnalysisResult.query.filter_by(user_id=user_id).order_by(AnalysisResult.created_at.desc()).all()
        return jsonify([analysis.to_dict() for analysis in analyses])
        
    except Exception as e:
        logger.error(f"Error fetching user analyses: {str(e)}")
        return jsonify({"error": "Failed to fetch analyses", "details": str(e)}), 500

if __name__ == '__main__': 
    database_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if database_uri.startswith('sqlite:///'):
        db_path = database_uri[10:]
        instance_dir = os.path.dirname(db_path)
        
        if not os.path.isabs(instance_dir):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            instance_dir = os.path.join(app.root_path, instance_dir)
        
        os.makedirs(instance_dir, exist_ok=True)
        logger.info(f"Ensured instance directory exists: {instance_dir}")
    
    with app.app_context():
        db.create_all()
        logger.info("Database tables created!")
    
    logger.info("Starting server...")
    app.run(debug=True, host='0.0.0.0', port=5000)