"""
Validator: Deployment feasibility validation (LLM-based README review).
"""

from typing import Dict, Any
from llm_client import LLMClient
from template_spec import TEMPLATE_SPEC
from constraints import GLOBAL_CONSTRAINTS
from utils import parse_json_response
import json


class AgentValidator:
    """Validator: Deployment feasibility reviewer for LLM-auto-deploy READMEs."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    def validate(self, readme_to_review: str, evidence_map: list,
                 template_spec: str = TEMPLATE_SPEC) -> Dict[str, Any]:
        """Validate README for deployment feasibility (LLM review + scoring)."""
        
        system_prompt = f"""
{GLOBAL_CONSTRAINTS}

You are Validator.
Task: Strictly evaluate whether an LLM can **100% automatically set up and verify** the project based on this README.

The README MUST contain exactly five sections:
  1. Platform
  2. Prerequisites
  3. Build Steps
  4. Test Steps
  5. Unexpected Issues

============================================================
Scoring Criteria (100-point scale)
============================================================

1. Platform (10 pts)
   - OS stated with version (e.g., Ubuntu 22.04)
   - Language runtime / compiler with explicit version
   - No ambiguous versions (3.x, latest, >=)
   - Missing or vague → deduct up to 10

2. Prerequisites (20 pts)
   - Every dependency listed with install command
   - Versions explicit where upstream pins them
   - Commands directly executable (no placeholders)
   - Cross-check with evidence_map: every library/package found in code
     analysis MUST appear here
   - Missing dependency → blocker, deduct 15
   - Placeholder in command → blocker, deduct 10

3. Build Steps (30 pts)
   - Ordered, executable commands: clone → configure → compile → install
   - Correct dependency order (prerequisites before build)
   - No placeholders; actual repo URL, actual directory names
   - Environment variables with concrete example values
   - Missing critical step → blocker, deduct 20
   - Wrong order → blocker, deduct 15
   - Placeholder → blocker, deduct 15

4. Test Steps (25 pts)
   - At least one verification command
   - Expected output stated for every command
   - Port / URL consistency with Build Steps
   - Missing test command → blocker, deduct 20
   - Missing expected output → major, deduct 12
   - Port mismatch → major, deduct 10

5. Unexpected Issues (15 pts)
   - Lists plausible external obstacles OR explicitly states "none"
   - Each issue has symptom + cause + fix command
   - Section missing entirely → major, deduct 10
   - Issues listed without fix commands → minor, deduct 5

============================================================
Fatal / Blocker Rules
============================================================

Any of these → score capped at <70 + mark as blocker:
  - Any placeholder (<xxx>, your_xxx, xxx_here)
  - "please replace" / "please modify" instructions
  - Ambiguous version (3.x, latest, >=)
  - Multiple-choice paths ("can use A or B")
  - Missing section (any of the five)
  - Test command without expected output
  - Build command that cannot run without human edits

============================================================
Cross-checks with evidence_map
============================================================

- Every library / include / import found in evidence_map must have a
  corresponding install command in Prerequisites or Build Steps.
- Every environment variable found in evidence_map must be set with a
  concrete value in Build Steps.
- Port used in code must match port in Test Steps verification URL.

============================================================
Stop Recommendation
============================================================

Recommend stop ONLY when ALL:
  1. Score >= 97
  2. 0 blockers, 0 majors, 0 minors
  3. All five sections present and complete
  4. All commands directly executable
  5. All evidence_map items accounted for
  6. 98%+ confidence LLM can set up successfully

{'='*60}
Multi-Language Review Points
{'='*60}

🐍 Python: pip install, virtualenv, env vars, entry command
☕ Java: JDK version, mvn/gradle, JAR run command
📜 JS/TS: Node version, npm install, port config
🚀 Go: Go version, go mod, go build
🔧 C: gcc/clang version, system libs, compile+link commands
⚡ C++: C++ standard, CMake version, third-party libs, compile+link

You must output overall_score, section_scores, issues, revision_plan, stop_recommendation.
"""
        
        evidence_map_str = json.dumps(evidence_map, ensure_ascii=False, indent=2)
        
        user_prompt = f"""
template_spec:
<<<
{template_spec}

readme_to_review:
<<<
{readme_to_review}

evidence_map (merged):
<<<
{evidence_map_str}

Review the README against the five-section template.

Score each section (Platform, Prerequisites, Build Steps, Test Steps, Unexpected Issues).

section_scores slots MUST use these exact names:
  "platform", "prerequisites", "build_steps", "test_steps", "unexpected_issues"

⚠️ Output Requirements:
1. Only output JSON object, no explanations or extra text
2. Do not wrap with markdown code blocks
3. JSON must be complete and correctly formatted

JSON format:
{{
  "overall_score": 85,
  "section_scores": [
    {{"slot": "platform", "score": 90, "comment": "..."}},
    {{"slot": "prerequisites", "score": 80, "comment": "..."}},
    {{"slot": "build_steps", "score": 85, "comment": "..."}},
    {{"slot": "test_steps", "score": 70, "comment": "..."}},
    {{"slot": "unexpected_issues", "score": 95, "comment": "..."}}
  ],
  "issues": [
    {{
      "severity": "major",
      "slot": "test_steps",
      "problem": "Missing expected output for test command",
      "deployment_impact": "Cannot determine if setup succeeded",
      "fix_request": "Add expected output after each test command"
    }}
  ],
  "revision_plan": [
    {{"priority": 1, "action": "Add expected output to test commands", "owner_suggestion": "Analyzer", "acceptance": "Every test command has expected output"}}
  ],
  "stop_recommendation": {{
    "should_stop": false,
    "reason": "Test steps missing expected output",
    "confidence_level": "80-95%",
    "missing_for_stop": ["expected output for test commands"]
  }}
}}

Now please directly output JSON:
"""
        
        response = self.llm_client.call(system_prompt, user_prompt)
        result = parse_json_response(response)
        
        return result
