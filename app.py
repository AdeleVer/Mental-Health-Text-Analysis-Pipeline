"""
Flask server for Mental Health Text Analysis API.
"""

import logging
from flask import Flask, request, jsonify, render_template
from src.api.models import AnalysisRequest
from src.api.yandex_gpt import get_yandex_gpt_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

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
        return jsonify(analysis_result.model_dump())
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({"error": "Analysis failed", "details": str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting server...")
    app.run(debug=True, host='0.0.0.0', port=5000)