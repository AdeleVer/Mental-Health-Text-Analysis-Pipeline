"""
Test for Pydantic models validation.
"""

import sys
from pathlib import Path

# Add project root to Python path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.api.models import AnalysisRequest, AnalysisResponse, Entities

def test_entities_model():
    """Test Entities model validation"""
    # Test valid data
    entities = Entities(
        emotions=["joy", "anxiety"],
        skills=["communication", "problem_solving"]
    )
    assert entities.emotions == ["joy", "anxiety"]
    assert entities.skills == ["communication", "problem_solving"]
    
    # Test empty lists
    empty_entities = Entities()
    assert empty_entities.emotions == []
    assert empty_entities.skills == []
    
    print("✅ Entities model test passed!")

def test_analysis_request_model():
    """Test AnalysisRequest model validation"""
    # Test valid data
    request = AnalysisRequest(
        text="This is a test text for analysis that is long enough",
        language="ru"
    )
    assert request.text == "This is a test text for analysis that is long enough"
    assert request.language == "ru"
    
    # Test default language
    request_default = AnalysisRequest(
        text="Another test text that is sufficiently long"
    )
    assert request_default.language == "ru"
    
    print("✅ AnalysisRequest model test passed!")

def test_analysis_response_model():
    """Test AnalysisResponse model validation"""
    # Test valid data
    entities = Entities(
        emotions=["joy", "satisfaction"],
        skills=["self_reflection"]
    )
    
    response = AnalysisResponse(
        sentiment="positive",
        entities=entities,
        distortions=["overgeneralization"],
        confidence_score=0.92
    )
    
    assert response.sentiment == "positive"
    assert response.entities.emotions == ["joy", "satisfaction"]
    assert response.distortions == ["overgeneralization"]
    assert response.confidence_score == 0.92
    
    print("✅ AnalysisResponse model test passed!")

def test_confidence_score_validation():
    """Test confidence score boundary validation"""
    # Test valid boundaries
    entities = Entities(emotions=[], skills=[])
    
    # Should work
    AnalysisResponse(
        sentiment="neutral",
        entities=entities,
        distortions=[],
        confidence_score=0.0  # Minimum
    )
    
    AnalysisResponse(
        sentiment="neutral", 
        entities=entities,
        distortions=[],
        confidence_score=1.0  # Maximum
    )
    
    AnalysisResponse(
        sentiment="neutral",
        entities=entities,
        distortions=[],
        confidence_score=0.5  # Middle
    )
    
    print("✅ Confidence score validation test passed!")

def main():
    """Run all model tests"""
    print("🔧 Testing Pydantic models...\n")
    
    try:
        test_entities_model()
        test_analysis_request_model() 
        test_analysis_response_model()
        test_confidence_score_validation()
        
        print("\n🎉 All model tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)