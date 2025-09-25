"""
Flask server for Mental Health Text Analysis API.
"""

import logging
import os
import re
from flask import Flask, request, jsonify, render_template, has_request_context
from flask_sqlalchemy import SQLAlchemy 
from dotenv import load_dotenv
import json 

from pydantic import ValidationError
import pydantic_core 

from extensions import db 

load_dotenv() 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# User-friendly error messages for both languages
ERROR_MESSAGES = {
    'ru': {
        'text_too_short': 'Текст слишком короткий. Минимальная длина - 10 символов.',
        'text_too_long': 'Текст слишком длинный. Максимальная длина - 2000 символов.',
        'validation_error': 'Ошибка проверки данных'
    },
    'en': {
        'text_too_short': 'Text is too short. Minimum length is 10 characters.',
        'text_too_long': 'Text is too long. Maximum length is 2000 characters.',
        'validation_error': 'Data validation error'
    }
}

@app.errorhandler(ValidationError)
def handle_validation_error(e):
    return _handle_validation_error_internal(e)

@app.errorhandler(pydantic_core._pydantic_core.ValidationError)
def handle_pydantic_core_validation_error(e):
    return _handle_validation_error_internal(e)

def _handle_validation_error_internal(e):
    """Common logic for handling ValidationError"""
    # Detect user language from request
    language = 'ru'  # Default to Russian
    if request.data:
        try:
            data = request.get_json()
            language = data.get('language', 'ru')
        except:
            pass
    
    # Convert Pydantic errors to friendly messages
    error_messages = []
    
    # Handle different Pydantic v1/v2 error formats
    if hasattr(e, 'errors'):
        errors = e.errors()
    else:
        errors = [{'msg': str(e)}]
    
    for error in errors:
        error_msg = str(error.get('msg', '')).lower()
        
        if 'too short' in error_msg or 'text_too_short' in error_msg:
            error_code = 'text_too_short'
        elif 'too long' in error_msg or 'text_too_long' in error_msg:
            error_code = 'text_too_long'
        else:
            error_code = 'validation_error'
        
        friendly_message = ERROR_MESSAGES[language].get(
            error_code, 
            ERROR_MESSAGES[language]['validation_error']
        )
        error_messages.append(friendly_message)
    
    return jsonify({
        'error': 'Validation failed',
        'message': ' | '.join(error_messages),
        'language': language
    }), 400

# SECURITY: Filter to mask sensitive user data in logs (PII protection)
class SensitiveDataFilter(logging.Filter):
    """Filter to mask confidential data in application logs"""
    
    def filter(self, record):
        if has_request_context():
            # Mask analysis text content in logs
            if 'analyzing text:' in str(record.msg):
                record.msg = re.sub(
                    r'(analyzing text:\s*)(.{0,50})(.*)', 
                    r'\1\2***MASKED***', 
                    str(record.msg)
                )
            # Mask JSON fields containing sensitive text data
            record.msg = re.sub(r'("text"\s*:\s*")([^"]+)(")', r'\1***MASKED***\3', str(record.msg))
            record.msg = re.sub(r'("original_text"\s*:\s*")([^"]+)(")', r'\1***MASKED***\3', str(record.msg))
        
        return True

def get_database_uri():
    env_db_uri = os.getenv('DATABASE_URL')
    if env_db_uri:
        return env_db_uri
    
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, 'instance', 'mental_health_analysis.db')
    
    instance_dir = os.path.dirname(db_path)
    os.makedirs(instance_dir, exist_ok=True)
    logger.info(f"Ensured instance directory exists: {instance_dir}")
    
    return f'sqlite:///{db_path}'

app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ← SECURITY: Apply sensitive data filtering to all loggers
# IMPORTANT: This protects user privacy by masking personal data in logs
sensitive_filter = SensitiveDataFilter()
app.logger.addFilter(sensitive_filter)
logging.getLogger('werkzeug').addFilter(sensitive_filter)

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
        app.logger.info(f"Received request data: {request_data}")

        analysis_request = AnalysisRequest(**request_data)
        # ← SECURITY: Log metadata only, not actual text content
        app.logger.info(f"User {user_id} analyzing text (length: {len(analysis_request.text)} chars, language: {analysis_request.language})")
        
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
        # ← SECURITY: Log successful analysis without exposing data
        app.logger.info(f"Analysis completed successfully for user {user_id}")

        return jsonify(analysis_result.model_dump())
        
    except ValidationError as e:
        app.logger.info(f"Validation error for user {user_id}: {str(e)}")
        app.logger.error(f"VALIDATION ERROR DETAILS:")
        app.logger.error(f"Error type: {type(e)}")
        app.logger.error(f"Error message: {str(e)}")
        app.logger.error(f"Error repr: {repr(e)}")
        
        language = 'ru'
        if request.data:
            try:
                data = request.get_json()
                language = data.get('language', 'ru')
            except:
                pass

        error_msg = str(e).lower()
        
        if 'too short' in error_msg:
            user_message = ERROR_MESSAGES[language]['text_too_short']
        elif 'too long' in error_msg:
            user_message = ERROR_MESSAGES[language]['text_too_long']
        else:
            user_message = ERROR_MESSAGES[language]['validation_error']
        
        return jsonify({
            'error': 'Validation failed',
            'message': user_message,
            'language': language
        }), 400

    except Exception as e:
        # ← SECURITY: Log errors without exposing sensitive request data
        app.logger.error(f"Analysis failed for user {user_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Analysis failed", "details": "Internal server error"}), 500
    
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
        app.logger.error(f"Error fetching profile for user {user_id}: {str(e)}")
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
        app.logger.error(f"Error fetching analyses for user {user_id}: {str(e)}")
        return jsonify({"error": "Failed to fetch analyses", "details": str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        logger.info("Database tables created!")
    
    logger.info("Starting server...")
    app.run(debug=True, host='0.0.0.0', port=5000)