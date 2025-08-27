"""
Integration test for prompt assembly functionality.
Tests that system prompts and few-shot examples are correctly combined.
"""

import json
import os
import sys
from pathlib import Path

# Add project root to Python path for imports
sys.path.append('.')

def load_test_cases():
    """Load test cases from golden standard dataset"""
    try:
        # Load test cases from JSON file
        with open('data/golden_standard_ru.json', 'r', encoding='utf-8') as f:
            test_cases = json.load(f)
        print(f"✅ Loaded {len(test_cases)} test cases")
        return test_cases
        
    except FileNotFoundError:
        print("❌ Error: File data/golden_standard_ru.json not found")
        return []
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON format in test cases file")
        return []

def build_prompt(user_text, language="ru"):
    """Build complete prompt from system instructions and few-shot examples"""
    try:
        # Load system prompt (model instructions)
        system_prompt = Path(f"prompts/system_prompt_{language}.txt").read_text(encoding="utf-8")
        
        # Load few-shot examples (training examples)
        few_shot_examples = Path(f"prompts/few_shot_examples_{language}.txt").read_text(encoding="utf-8")
        
        # Combine all parts: instructions + examples + user input
        full_prompt = f"{system_prompt}\n\n{few_shot_examples}\n\nUSER: {user_text}\nASSISTANT:"
        
        print("✅ Prompt assembled successfully")
        return full_prompt
        
    except FileNotFoundError:
        print(f"❌ Error: Prompt files not found in prompts/ directory")
        return None

def test_prompt_assembly():
    """Test prompt assembly with first 3 test cases"""
    print("=== TESTING PROMPT ASSEMBLY ===\n")
    
    # Load test cases
    test_cases = load_test_cases()
    
    # Test 1: Verify test cases were loaded
    assert len(test_cases) > 0, "No test cases found in golden_standard_ru.json"
    print(f"✅ Test 1 passed: Found {len(test_cases)} test cases")
    
    # Test 2: Verify prompt assembly works for first case
    first_case = test_cases[0]
    full_prompt = build_prompt(first_case['input_text'])
    
    assert full_prompt is not None, "Prompt assembly failed - returned None"
    assert len(full_prompt) > 0, "Prompt assembly failed - empty prompt"
    print(f"✅ Test 2 passed: Prompt assembled successfully ({len(full_prompt)} characters)")
    
    # Test 3: Verify prompt contains expected components
    assert "USER:" in full_prompt, "Prompt should contain USER section"
    assert "ASSISTANT:" in full_prompt, "Prompt should contain ASSISTANT section"
    assert first_case['input_text'] in full_prompt, "Prompt should contain user input text"
    print("✅ Test 3 passed: Prompt contains all required components")
    
    # Test 4: Verify multiple languages (if available)
    try:
        en_prompt = build_prompt("Test text", "en")
        if en_prompt:
            assert "USER:" in en_prompt, "English prompt should contain USER section"
            print("✅ Test 4 passed: English prompt assembly works")
        else:
            print("⚠️  English prompt files not available (skipping)")
    except:
        print("⚠️  English prompt test skipped (files may not exist)")
    
    print("\n✅ All prompt assembly tests passed!")

def test_prompt_structure():
    """Test specific prompt structure requirements"""
    print("\n=== TESTING PROMPT STRUCTURE ===\n")
    
    test_cases = load_test_cases()
    assert len(test_cases) > 0, "Need test cases to run structure tests"
    
    # Test with a simple text
    test_text = "This is a test message for prompt structure validation"
    full_prompt = build_prompt(test_text)
    
    # Verify prompt structure - UPDATED FOR ACTUAL PROMPT CONTENT
    assert full_prompt.startswith("# РОЛЬ И КОНТЕКСТ") or \
           full_prompt.startswith("# ROLE AND CONTEXT"), \
           "Prompt should start with role definition section"
    
    assert "Ты — AI-ассистент" in full_prompt or \
           "You are an AI assistant" in full_prompt, \
           "Prompt should contain AI assistant definition"
    
    assert "USER: " + test_text in full_prompt, \
           "Prompt should contain user input with USER prefix"
    
    assert full_prompt.endswith("ASSISTANT:"), \
           "Prompt should end with ASSISTANT: waiting for model response"
    
    # Additional checks for critical components
    assert "JSON" in full_prompt, "Prompt should mention JSON output format"
    assert "sentiment" in full_prompt, "Prompt should mention sentiment analysis"
    assert "entities" in full_prompt, "Prompt should mention entities extraction"
    
    print("✅ All prompt structure tests passed!")

def main():
    """Main test function"""
    print("🔧 Testing prompt assembly functionality\n")
    
    try:
        # Run all tests
        test_prompt_assembly()
        test_prompt_structure()
        
        print("\n🎉 Success! All prompt tests passed.")
        print("Next step: Connect to YandexGPT API")
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

# Run the tests
if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)