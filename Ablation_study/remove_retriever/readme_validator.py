#!/usr/bin/env python3
"""
README Validator - checks compliance with the five-section template.

Sections: Platform, Prerequisites, Build Steps, Test Steps, Unexpected Issues.
"""

import re
from typing import List, Dict, Tuple


REQUIRED_SECTIONS = [
    "Platform",
    "Prerequisites",
    "Build Steps",
    "Test Steps",
    "Unexpected Issues",
]


class ReadmeValidator:
    """Validates a README against the five-section template."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
    
    def validate(self, readme_content: str) -> Dict[str, any]:
        """Validate README content against the five-section template."""
        self.errors = []
        self.warnings = []
        self.info = []
        
        self._check_required_sections(readme_content)
        self._check_placeholders(readme_content)
        self._check_version_clarity(readme_content)
        self._check_command_completeness(readme_content)
        self._check_test_steps_expected_output(readme_content)
        self._check_multiple_choices(readme_content)
        self._check_manual_intervention(readme_content)
        
        score = self._calculate_score()
        
        return {
            "score": score,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "is_llm_deployable": score >= 90 and len(self.errors) == 0
        }
    
    def _check_required_sections(self, content: str):
        """Check that all five required sections are present."""
        for section in REQUIRED_SECTIONS:
            pattern = rf'#+\s*{re.escape(section)}'
            if not re.search(pattern, content, re.IGNORECASE):
                self.errors.append({
                    "type": "missing_section",
                    "severity": "blocker",
                    "content": section,
                    "issue": f"Missing required section: {section}",
                    "fix": f"Add a '## {section}' section with appropriate content"
                })
    
    def _check_placeholders(self, content: str):
        """Check for placeholders that an LLM cannot execute."""
        
        placeholder_pattern = r'<([^>]+)>'
        matches = re.finditer(placeholder_pattern, content)
        html_tags = {'br', 'hr', 'img', 'div', 'span', 'p', 'a', 'b', 'i', 'u',
                     'code', 'pre', 'em', 'strong', 'li', 'ul', 'ol', 'h1', 'h2',
                     'h3', 'h4', 'h5', 'h6', 'table', 'tr', 'td', 'th', 'details',
                     'summary', 'sup', 'sub'}
        
        for match in matches:
            placeholder = match.group(1)
            tag_name = placeholder.split()[0].strip('/').lower()
            if tag_name not in html_tags:
                line_num = content[:match.start()].count('\n') + 1
                self.errors.append({
                    "type": "placeholder",
                    "severity": "blocker",
                    "line": line_num,
                    "content": f"<{placeholder}>",
                    "issue": f"Placeholder <{placeholder}> found",
                    "fix": f"Replace with concrete value: {self._suggest_concrete_value(placeholder)}"
                })
        
        your_pattern = r'\byour_\w+'
        for match in re.finditer(your_pattern, content, re.IGNORECASE):
            line_num = content[:match.start()].count('\n') + 1
            self.errors.append({
                "type": "placeholder",
                "severity": "blocker",
                "line": line_num,
                "content": match.group(0),
                "issue": f"Placeholder {match.group(0)} found",
                "fix": "Replace with concrete test value, e.g. test_key_12345"
            })
        
        here_pattern = r'\w+_here\b'
        for match in re.finditer(here_pattern, content, re.IGNORECASE):
            line_num = content[:match.start()].count('\n') + 1
            self.errors.append({
                "type": "placeholder",
                "severity": "blocker",
                "line": line_num,
                "content": match.group(0),
                "issue": f"Placeholder {match.group(0)} found",
                "fix": "Replace with concrete test value"
            })
        
        manual_patterns = [
            r'please replace', r'please modify', r'replace with',
            r'change to your', r'fill in your',
        ]
        for pattern in manual_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                line_num = content[:match.start()].count('\n') + 1
                self.errors.append({
                    "type": "manual_action_required",
                    "severity": "blocker",
                    "line": line_num,
                    "content": match.group(0),
                    "issue": "Manual action instruction found; LLM cannot execute",
                    "fix": "Provide a concrete usable value directly"
                })
    
    def _suggest_concrete_value(self, placeholder: str) -> str:
        """Suggest a concrete replacement for a placeholder."""
        placeholder_lower = placeholder.lower()
        suggestions = {
            'port': '8000',
            'name': 'myapp',
            'url': 'http://localhost:8000',
            'host': 'localhost',
            'database': 'mydb',
            'user': 'admin',
            'password': 'test_password_123',
            'key': 'test_key_12345',
            'token': 'test_token_67890',
            'path': '/app',
            'file': 'app.py',
            'version': '1.0.0',
        }
        for key, value in suggestions.items():
            if key in placeholder_lower:
                return value
        return 'specific_value'
    
    def _check_version_clarity(self, content: str):
        """Check for ambiguous version numbers."""
        fuzzy_patterns = [
            (r'\b\d+\.x\b', 'x version'),
            (r'\b\d+\.\*\b', '* version'),
            (r'\blatest\b', 'latest'),
            (r'>=\s*\d+\.\d+', '>= version'),
            (r'>\s*\d+\.\d+', '> version'),
        ]
        for pattern, desc in fuzzy_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                line_num = content[:match.start()].count('\n') + 1
                self.warnings.append({
                    "type": "fuzzy_version",
                    "severity": "major",
                    "line": line_num,
                    "content": match.group(0),
                    "issue": f"Ambiguous version: {desc}",
                    "fix": "Use explicit version, e.g. 3.10, 16.0, 12"
                })
    
    def _check_command_completeness(self, content: str):
        """Check command blocks for completeness."""
        code_blocks = re.finditer(r'```(?:bash|sh)?\n(.*?)```', content, re.DOTALL)
        for block in code_blocks:
            commands = block.group(1)
            if 'TODO' in commands or 'FIXME' in commands:
                line_num = content[:block.start()].count('\n') + 1
                self.errors.append({
                    "type": "incomplete_command",
                    "severity": "blocker",
                    "line": line_num,
                    "content": "TODO/FIXME in command block",
                    "issue": "Incomplete command found",
                    "fix": "Replace TODO/FIXME with actual commands"
                })
    
    def _check_test_steps_expected_output(self, content: str):
        """Check that Test Steps section has expected output."""
        test_match = re.search(
            r'#+\s*Test\s*Steps(.*?)(?=\n#+\s|\Z)',
            content, re.IGNORECASE | re.DOTALL
        )
        if test_match:
            test_section = test_match.group(1)
            has_command = re.search(r'```', test_section)
            has_expected = re.search(
                r'[Ee]xpected|should\s+(?:see|output|return|print|show)',
                test_section, re.IGNORECASE
            )
            if has_command and not has_expected:
                self.warnings.append({
                    "type": "missing_expected_output",
                    "severity": "major",
                    "content": "Test Steps",
                    "issue": "Test commands lack expected output",
                    "fix": "Add '# Expected: ...' after each test command"
                })
    
    def _check_multiple_choices(self, content: str):
        """Check for multiple-choice instructions."""
        choice_patterns = [
            r'(?:can|could)\s+(?:also\s+)?use.*\bor\b',
            r'\balternatively\b',
            r'\beither\b.*\bor\b',
        ]
        for pattern in choice_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                line_num = content[:match.start()].count('\n') + 1
                self.warnings.append({
                    "type": "multiple_choices",
                    "severity": "minor",
                    "line": line_num,
                    "content": match.group(0),
                    "issue": "Multiple choices offered; provide a single path",
                    "fix": "Keep only the recommended approach"
                })
    
    def _check_manual_intervention(self, content: str):
        """Check for content requiring human intervention."""
        intervention_patterns = [
            (r'Open Questions', 'Open Questions section'),
            (r'manual\s+confirmation', 'manual confirmation'),
            (r'to\s+be\s+confirmed', 'unconfirmed info'),
        ]
        for pattern, desc in intervention_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                line_num = content[:match.start()].count('\n') + 1
                self.errors.append({
                    "type": "manual_intervention_required",
                    "severity": "blocker",
                    "line": line_num,
                    "content": match.group(0),
                    "issue": f"Requires human intervention: {desc}",
                    "fix": "Provide concrete defaults; remove manual-confirmation language"
                })
    
    def _calculate_score(self) -> int:
        """Calculate validation score."""
        base_score = 100
        for error in self.errors:
            if error['severity'] == 'blocker':
                base_score -= 20
            elif error['severity'] == 'major':
                base_score -= 10
        for warning in self.warnings:
            if warning['severity'] == 'major':
                base_score -= 5
            elif warning['severity'] == 'minor':
                base_score -= 2
        return max(base_score, 0)


def validate_readme_file(file_path: str):
    """Validate a README file and print results."""
    from pathlib import Path
    
    print("=" * 70)
    print("README Validator - Five-Section Template Check")
    print("=" * 70)
    
    path = Path(file_path)
    if not path.exists():
        print(f"\nFile not found: {file_path}")
        return
    
    content = path.read_text(encoding='utf-8')
    validator = ReadmeValidator()
    result = validator.validate(content)
    
    print(f"\nScore: {result['score']}/100")
    print(f"LLM-deployable: {'YES' if result['is_llm_deployable'] else 'NO'}")
    
    if result['errors']:
        print(f"\nErrors ({len(result['errors'])}):")
        for i, error in enumerate(result['errors'], 1):
            print(f"\n  {i}. [{error['severity'].upper()}] {error['issue']}")
            if 'line' in error:
                print(f"     Line: {error['line']}")
            print(f"     Content: {error['content']}")
            print(f"     Fix: {error['fix']}")
    
    if result['warnings']:
        print(f"\nWarnings ({len(result['warnings'])}):")
        for i, warning in enumerate(result['warnings'], 1):
            print(f"\n  {i}. [{warning['severity'].upper()}] {warning['issue']}")
            if 'line' in warning:
                print(f"     Line: {warning['line']}")
            if 'content' in warning:
                print(f"     Content: {warning['content']}")
            print(f"     Fix: {warning['fix']}")
    
    if not result['errors'] and not result['warnings']:
        print("\nAll checks passed.")
    
    print("\n" + "=" * 70)
    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        validate_readme_file(sys.argv[1])
    else:
        print("\nUsage: python3 readme_validator.py <readme_file>")
        print("Example: python3 readme_validator.py output/README.generated.md")
