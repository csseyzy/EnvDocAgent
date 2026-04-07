#!/usr/bin/env python3
"""
Test the generalized JSON parser.

Covers various LLM response formats.
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils import parse_json_response


def test_case(name: str, response: str, should_succeed: bool = True):
    """Single test case."""
    print(f"\n{'='*60}")
    print(f"Test: {name}")
    print(f"{'='*60}")
    print(f"Response ({len(response)} chars):")
    print(response[:200] + ("..." if len(response) > 200 else ""))
    print("-" * 60)
    
    try:
        result = parse_json_response(response)
        if should_succeed:
            print(f"✅ Parsed successfully")
            print(f"   Keys: {list(result.keys())}")
            if isinstance(result, dict) and len(result) <= 3:
                print(f"   Content: {json.dumps(result, ensure_ascii=False, indent=2)[:200]}")
        else:
            print(f"❌ Expected failure but parsing succeeded")
            return False
        return True
    except Exception as e:
        if not should_succeed:
            print(f"✅ Expected failure: {e}")
        else:
            print(f"❌ Parse failed: {e}")
            return False
        return True


def run_tests():
    """Run all tests."""
    print("=" * 60)
    print("Generalized JSON parser tests")
    print("=" * 60)
    
    test_cases = [
        # 1. Standard format
        ("Standard JSON object", '{"name": "test", "value": 123}', True),
        
        # 2. Markdown code block
        ("Markdown JSON code block", '```json\n{"name": "test", "value": 123}\n```', True),
        
        # 3. Plain code block
        ("Plain code block", '```\n{"name": "test", "value": 123}\n```', True),
        
        # 4. Empty code block (should skip)
        ("Empty code block + JSON", '```\n\n```\n\n{"name": "test", "value": 123}', True),
        
        # 5. Surrounding prose
        ("Text before and after", 'Here is the result:\n{"name": "test", "value": 123}\nThat\'s all.', True),
        
        # 6. Nested JSON
        ("Nested object", '{"outer": {"inner": {"deep": "value"}}, "list": [1, 2, 3]}', True),
        
        # 7. Quoted values
        ("Quotes inside value", '{"text": "He said \\"hello\\" to me", "value": 123}', True),
        
        # 8. Multiline string (\\n)
        ("Multiline string", '{"readme": "Line 1\\nLine 2\\nLine 3", "value": 123}', True),
        
        # 9. Trailing comma (needs repair)
        ("Trailing comma", '{"name": "test", "value": 123,}', True),
        
        # 10. Mixed format (markdown + text)
        ("Mixed format", 'Here is the JSON:\n```json\n{"name": "test"}\n```\nDone!', True),
        
        # 11. Empty response (should fail)
        ("Empty response", '', False),
        
        # 12. Plain text only (should fail)
        ("Plain text only", 'This is just plain text without any JSON.', False),
        
        # 13. Array format
        ("JSON array", '[{"id": 1}, {"id": 2}, {"id": 3}]', True),
        
        # 14. Complex nesting
        ("Complex nesting", '''{
  "draft_readme_markdown": "Project: Test\\nStack: Python\\n\\n```bash\\ngit clone repo\\n```",
  "gap_list": [
    {"slot": "Environment variables", "missing": "Not found"}
  ],
  "evidence_map": [
    {"evidence_id": "E1", "type": "file", "ref": "README.md", "quote": "Python 3.9+"}
  ]
}''', True),
        
        # 15. Malformed quotes (needs repair)
        ("Malformed quote escaping", '{"key": \\"value\\", "number": 123}', True),
    ]
    
    passed = 0
    failed = 0
    
    for name, response, should_succeed in test_cases:
        if test_case(name, response, should_succeed):
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total: {passed + failed}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
