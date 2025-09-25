"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Literal 

class Entities(BaseModel):
    """Entity extraction model for emotions and skills"""
    emotions: List[str] = Field(default_factory=list, description="List of detected emotions")
    skills: List[str] = Field(default_factory=list, description="List of mentioned skills")

class AnalysisRequest(BaseModel):
    """Request model for text analysis"""
    text: str
    language: str = Field("ru", pattern="^(ru|en)$", description="Analysis language: ru or en")

    @field_validator('text')
    @classmethod
    def validate_text_length(cls, v):
        """
        Custom validator for text length with user-friendly error codes.
        This replaces technical Pydantic messages with codes we can translate.
        """
        if len(v) < 10:
            raise ValueError('Text is too short. Minimum length is 10 characters.')
        if len(v) > 2000:
            raise ValueError('Text is too long. Maximum length is 2000 characters.')
        return v

class AnalysisResponse(BaseModel):
    """Response model for analysis results"""
    sentiment: Literal["positive", "negative", "neutral", "mixed"] = Field(..., description="Overall sentiment")
    entities: Entities = Field(..., description="Extracted entities and emotions")
    distortions: List[str] = Field(default_factory=list, description="Cognitive distortions detected")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Model confidence score")