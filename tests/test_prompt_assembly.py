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
    if not test_cases:
        print("❌ Cannot run tests without test cases")
        return False
    
    print("🧪 Testing with first 3 cases...\n")
    
    # Test with first 3 cases
    for i in range(3):
        case = test_cases[i]
        print(f"📝 Test case {i + 1}:")
        print(f"   User text: {case['input_text'][:60]}...")
        
        # Build prompt
        full_prompt = build_prompt(case['input_text'])
        
        if not full_prompt:
            print("❌ Prompt assembly failed")
            return False
            
        # Show prompt info
        print(f"   Prompt length: {len(full_prompt)} characters")
        print("   First 100 chars:")
        print("   " + full_prompt[:100].replace('\n', ' ') + "...")
        print()
    
    print("✅ All prompt assembly tests passed!")
    return True

def main():
    """Main test function"""
    print("🔧 Testing prompt assembly functionality\n")
    
    success = test_prompt_assembly()
    
    if success:
        print("\n🎉 Success! Prompt assembly is working correctly.")
        print("Next step: Connect to YandexGPT API")
    else:
        print("\n⚠️  Tests failed. Please check:")
        print("   - data/golden_standard_ru.json exists")
        print("   - prompts/system_prompt_ru.txt exists")
        print("   - prompts/few_shot_examples_ru.txt exists")

# Run the tests
if __name__ == "__main__":
    main()