"""
YandexGPT API client for mental health text analysis.
Handles prompt assembly and API communication for both English and Russian.
"""

import json
import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any
import requests
from pydantic import ValidationError

# Add project root to Python path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.api.models import AnalysisRequest, AnalysisResponse

# Configure logging
logger = logging.getLogger(__name__)

class YandexGPTClient:
    """Client for interacting with YandexGPT API for text analysis."""
    
    def __init__(self):
        self.api_key = os.getenv('YANDEX_API_KEY')
        self.folder_id = os.getenv('YANDEX_FOLDER_ID')
        self.api_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        
        # Validate environment variables
        if not self.api_key:
            raise ValueError("YANDEX_API_KEY environment variable is not set")
        if not self.folder_id:
            raise ValueError("YANDEX_FOLDER_ID environment variable is not set")
            
        self.headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json"
        }
        logger.info("YandexGPTClient initialized successfully")
    
    def _load_prompt_file(self, filename: str) -> str:
        """Load prompt content from file."""
        try:
            filepath = os.path.join('prompts', filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read().strip()
            logger.debug(f"Loaded prompt file: {filename}")
            return content
        except FileNotFoundError:
            error_msg = f"Prompt file not found: {filename}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Error reading prompt file {filename}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def _build_complete_prompt(self, text: str, language: str) -> str:
        """Build complete prompt with system instructions and user text."""
        try:
            # Load appropriate prompts based on language
            system_prompt_file = f"system_prompt_{language}.md"
            examples_file = f"few_shot_examples_{language}.md"
            
            system_prompt = self._load_prompt_file(system_prompt_file)
            few_shot_examples = self._load_prompt_file(examples_file)
            
            # Construct the complete prompt
            complete_prompt = f"""{system_prompt}

{few_shot_examples}

USER TEXT TO ANALYZE:
{text}

ASSISTANT RESPONSE (JSON ONLY):
"""
            logger.debug(f"Built prompt for {language} language, length: {len(complete_prompt)}")
            return complete_prompt
            
        except Exception as e:
            error_msg = f"Failed to build prompt: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def _call_yandex_gpt(self, prompt: str) -> Dict[str, Any]:
        """Make actual API call to YandexGPT."""
        payload = {
            "modelUri": f"gpt://{self.folder_id}/yandexgpt",
            "completionOptions": {
                "stream": False,
                "temperature": 0.1,  # Low temperature for consistent JSON output
                "maxTokens": 2000
            },
            "messages": [
                {
                    "role": "system",
                    "text": "You are a helpful assistant that always responds with valid JSON."
                },
                {
                    "role": "user",
                    "text": prompt
                }
            ]
        }
        
        try:
            logger.info("Sending request to YandexGPT API")
            response = requests.post(
                    self.api_url, 
                    headers=self.headers, 
                    json=payload,
                    timeout=30
                )
                    
            if response.status_code != 200:
                    error_text = response.text
                    error_msg = f"YandexGPT API error {response.status}: {error_text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                    
            result = response.json()
            logger.info("Successfully received response from YandexGPT API")
            return result
                    
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error calling YandexGPT: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error calling YandexGPT: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def analyze_text(self, text: str, language: str = "ru") -> AnalysisResponse:
        """
        Main method to analyze text using YandexGPT.
        
        Args:
            text: User text to analyze
            language: Analysis language ('ru' or 'en')
            
        Returns:
            AnalysisResponse: Validated analysis results
            
        Raises:
            Exception: If API call fails or response validation fails
        """
        # Validate input parameters
        analysis_request = AnalysisRequest(text=text, language=language)
        logger.info(f"Starting analysis for text (length: {len(text)} chars, language: {language})")
        
        try:
            # Build the complete prompt
            prompt = self._build_complete_prompt(analysis_request.text, analysis_request.language)
            
            # Call YandexGPT API
            api_response = self._call_yandex_gpt(prompt)
            
            # Extract and clean the response text
            response_text = api_response.get('result', {}).get('alternatives', [{}])[0].get('message', {}).get('text', '')
            
            if not response_text:
                error_msg = "Empty response from YandexGPT"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Clean response - remove markdown code blocks if present
            cleaned_response = response_text.strip().replace('```json', '').replace('```', '').strip()
            logger.debug(f"Cleaned response received (length: {len(cleaned_response)} chars)")
            
            # Parse JSON response
            try:
                response_data = json.loads(cleaned_response)
            except json.JSONDecodeError as e:
                error_msg = f"Failed to parse JSON response: {str(e)}\nResponse length: {len(response_text)} chars"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Validate response against our Pydantic model
            analysis_response = AnalysisResponse(**response_data)
            logger.info(f"Analysis completed successfully. Sentiment: {analysis_response.sentiment}, Confidence: {analysis_response.confidence_score}")
            
            return analysis_response
            
        except ValidationError as e:
            error_msg = f"Response validation failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

_yandex_gpt_client_instance = None

def get_yandex_gpt_client():
    """Get or create YandexGPT client instance."""
    global _yandex_gpt_client_instance
    if _yandex_gpt_client_instance is None:
        _yandex_gpt_client_instance = YandexGPTClient()
    return _yandex_gpt_client_instance