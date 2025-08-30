"""
Flask server for Mental Health Text Analysis API.
"""

import logging
import os
from flask import Flask, request, jsonify, render_template
from src.api.models import AnalysisRequest
from src.api.yandex_gpt import get_yandex_gpt_client

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import json

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///instance/mental_health_analysis.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
import src.models.sql_models
from src.models.sql_models import AnalysisResult

migrate = Migrate(app, db)

@app.route('/')
def home():
    """Render main page with analysis form."""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    """Analyze text using YandexGPT API."""
    try:
        client = get_yandex_gpt_client()
        if client is None:
            return jsonify({"error": "YandexGPT client not configured"}), 500
    
        request_data = request.get_json()
        analysis_request = AnalysisRequest(**request_data)
        logger.info(f"Analyzing text: {analysis_request.text[:50]}...")
        
        analysis_result = client.analyze_text(
            text=analysis_request.text,
            language=analysis_request.language
        )
        result_dict = analysis_result.model_dump()
        
        db_record = AnalysisResult(
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
        logger.info(f"Analysis result saved to DB with ID: {db_record.id}")

        return jsonify(analysis_result.model_dump())
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Analysis failed", "details": str(e)}), 500

with app.app_context():
    db.create_all()
    logger.info("Database tables created!")

if __name__ == '__main__':

    logger.info("Starting server...")
    app.run(debug=True, host='0.0.0.0', port=5000)