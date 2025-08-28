"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import List, Literal 

class Entities(BaseModel):
    """Entity extraction model for emotions and skills"""
    emotions: List[str] = Field(default_factory=list, description="List of detected emotions")
    skills: List[str] = Field(default_factory=list, description="List of mentioned skills")

class AnalysisRequest(BaseModel):
    """Request model for text analysis"""
    text: str = Field(..., min_length=10, max_length=2000, description="User text for analysis")
    language: str = Field("ru", pattern="^(ru|en)$", description="Analysis language: ru or en")

class AnalysisResponse(BaseModel):
    """Response model for analysis results"""
    sentiment: Literal["positive", "negative", "neutral", "mixed"] = Field(..., description="Overall sentiment")
    entities: Entities = Field(..., description="Extracted entities and emotions")
    distortions: List[str] = Field(default_factory=list, description="Cognitive distortions detected")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Model confidence score") 