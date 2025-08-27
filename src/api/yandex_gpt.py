"""
YandexGPT API client for mental health text analysis.
Handles prompt assembly and API communication for both English and Russian. 
"""

import json
import os
from typing import Dict, Any
import aiohttp
from pydantic import ValidationError

from src.api.models import AnalysisRequest, AnalysisResponse

class YandexGPTClient:
    """Client for interacting with YandexGPT API for text analysis."""
    
    def __init__(self):
        self.api_key = os.getenv('YANDEX_API_KEY')
        self.folder_id = os.getenv('YANDEX_FOLDER_ID')
        self.api_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        self.headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json"
        }
    async def _load_prompt_file(self, filename: str) -> str:
        """Load prompt content from file."""
        try:
            filepath = os.path.join('prompts', filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except FileNotFoundError:
            raise Exception(f"Prompt file not found: {filename}")
        except Exception as e:
            raise Exception(f"Error reading prompt file {filename}: {str(e)}")
    
    async def _build_complete_prompt(self, text: str, language: str) -> str:
        """Build complete prompt with system instructions and user text."""
        try:
            # Load appropriate prompts based on language
            system_prompt_file = f"system_prompt_{language}.txt"
            examples_file = f"few_shot_examples_{language}.txt"
            
            system_prompt = await self._load_prompt_file(system_prompt_file)
            few_shot_examples = await self._load_prompt_file(examples_file)
            
            # Construct the complete prompt
            complete_prompt = f"""{system_prompt}

{few_shot_examples}

USER TEXT TO ANALYZE:
{text}

ASSISTANT RESPONSE (JSON ONLY):
"""
            return complete_prompt
            
        except Exception as e:
            raise Exception(f"Failed to build prompt: {str(e)}")
    
    async def _call_yandex_gpt(self, prompt: str) -> Dict[str, Any]:
        """Make actual API call to YandexGPT."""
        payload = {
            "modelUri": f"gpt://{self.folder_id}/yandexgpt-latest",
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
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url, 
                    headers=self.headers, 
                    json=payload,
                    timeout=30
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"YandexGPT API error {response.status}: {error_text}")
                    
                    result = await response.json()
                    return result
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Network error calling YandexGPT: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error calling YandexGPT: {str(e)}")
    
    async def analyze_text(self, text: str, language: str = "ru") -> AnalysisResponse:
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
        
        try:
            # Build the complete prompt
            prompt = await self._build_complete_prompt(analysis_request.text, analysis_request.language)
            
            # Call YandexGPT API
            api_response = await self._call_yandex_gpt(prompt)
            
            # Extract and clean the response text
            response_text = api_response.get('result', {}).get('alternatives', [{}])[0].get('message', {}).get('text', '')
            
            if not response_text:
                raise Exception("Empty response from YandexGPT")
            
            # Clean response - remove markdown code blocks if present
            cleaned_response = response_text.strip().replace('```json', '').replace('```', '').strip()
            
            # Parse JSON response
            try:
                response_data = json.loads(cleaned_response)
            except json.JSONDecodeError as e:
                raise Exception(f"Failed to parse JSON response: {str(e)}\nResponse was: {response_text}")
            
            # Validate response against our Pydantic model
            analysis_response = AnalysisResponse(**response_data)
            
            return analysis_response
            
        except ValidationError as e:
            raise Exception(f"Response validation failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Analysis failed: {str(e)}")

# Global client instance
yandex_gpt_client = YandexGPTClient()