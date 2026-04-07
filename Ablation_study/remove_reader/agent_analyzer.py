"""
Analyzer: Code-aware README generation and refinement.
(Ablation: Reader removed — Analyzer generates the full README from scratch)
"""

from typing import Dict, Any, Optional
from llm_client import LLMClient
from template_spec import TEMPLATE_SPEC
from constraints import GLOBAL_CONSTRAINTS
from utils import parse_json_response
import json


class AgentAnalyzer:
    """Analyzer: generates and refines README directly from code analysis + materials."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    def analyze(self, draft_readme: str, gap_list: list, code_analysis_results: Dict[str, Any],
                project_materials: str, template_spec: str = TEMPLATE_SPEC,
                execution_order_info: str = "",
                previous_review_report: Optional[str] = None) -> Dict[str, Any]:
        """Generate or refine a five-section README from code analysis + materials.

        When draft_readme is empty, generates the README from scratch.
        When draft_readme is provided, refines it based on Validator feedback.
        """
        
        is_first_round = not draft_readme
        
        if is_first_round:
            mode_instruction = """
You are generating the README from scratch. There is no prior draft.
Use project_materials and code_analysis_results to produce a complete
five-section README: Platform, Prerequisites, Build Steps, Test Steps,
Unexpected Issues.
"""
        else:
            mode_instruction = """
You are refining a previous README based on Validator feedback.
Do NOT regenerate from scratch. Only fix the issues identified by the Validator:
1. Keep correct parts unchanged
2. Only modify problematic sections
3. Add missing commands or information
4. Fix placeholders, version ambiguity, or ordering issues
"""

        review_block = ""
        if previous_review_report:
            review_block = (
                "\n[Validator feedback from previous round]\n<<<\n"
                + previous_review_report
                + "\n<<<\nFix only the issues above. Keep correct parts unchanged.\n"
            )
        
        system_prompt = f"""
{GLOBAL_CONSTRAINTS}

You are Analyzer.
Task: Generate or refine a five-section README using code_analysis_results
and project_materials. There is no separate Reader agent — you handle
everything from initial generation to iterative refinement.

{mode_instruction}

============================================================
Five-Section Structure
============================================================

The README MUST contain exactly these five sections:
  1. Platform
  2. Prerequisites
  3. Build Steps
  4. Test Steps
  5. Unexpected Issues

============================================================
Deep Code Analysis Capabilities
============================================================

code_analysis_results contains two levels:

1. File-level Analysis (file_stats):
   - File type statistics, directory structure, config files

2. Content-level Deep Analysis (content_analysis):
   Supported languages and extracted content:

   Python: imports, main_block, cli_params, env_vars, services, frameworks
   JS/TS: imports/requires, env_vars, server_port, frameworks
   Go: imports, main_function, env_vars, server_port, frameworks
   Java: imports, main_method, annotations, properties, server_port, frameworks
   C: includes, main_function, defines, functions, libraries
   C++: includes, namespaces, main_function, classes, std_version, libraries

============================================================
Section Generation / Completion Strategy
============================================================

**Platform:**
  - Extract OS from Dockerfile/CI configs
  - Extract language version from go.mod, setup.py, pom.xml, package.json
  - Extract compiler/std version from std_version, CMakeLists.txt
  - Predict from framework conventions if not found

**Prerequisites:**
  - Python: map imports to pip packages, add install commands
  - C/C++: map includes/libraries to apt packages (libssl-dev, libboost-all-dev)
  - Java: JDK version from pom.xml, build tool version
  - JS: Node version from engines, npm packages
  - Go: Go version from go.mod
  - Every prerequisite MUST have an install command

**Build Steps:**
  - Start with git clone + cd
  - Add dependency install (pip install, npm install, go mod, mvn)
  - Add environment variable setup from env_vars
  - Add compile/build commands
  - Add database init from services
  - Ensure correct order: clone -> deps -> config -> build -> init

**Test Steps:**
  - Add test commands from test frameworks detected
  - Add curl verification from server_port
  - Add expected output for every command
  - Ensure port consistency with Build Steps

**Unexpected Issues:**
  - Add permission issues for system-level installs
  - Add network issues for external dependencies
  - Add common build failures for the detected toolchain
  - If truly none, state "No known unexpected issues."

============================================================
Intelligent Prediction
============================================================

Goal: Eliminate ALL placeholders. Every value must be concrete.

Prohibited:
  <port>, <name>, <value>, <url>
  your_key, your_url
  3.x, latest, >=
  "please modify", "please replace"

Prediction by confidence:
  90%+: complete directly, no annotation
  70-89%: complete + annotate "(recommended for testing)"
  <70%: use common default + annotate "(default, adjust as needed)"

Standard predictions:
  Port: Flask 8000, Express 3000, Spring Boot 8080, Gin 8080
  Database: psycopg2 -> postgresql://localhost:5432/mydb
  API keys: test_key_12345
  Versions: use most common stable

============================================================
Rules
============================================================

1. Prioritize content_analysis deep analysis data
2. Every claim must have evidence (code file path + specific content)
3. All values must be concrete and usable
4. Use corresponding patterns for different languages
5. Never generate "Open Questions" or manual-confirmation content

============================================================
Final Completeness Check
============================================================

After generation/refinement, verify:
  [ ] Platform: OS + runtime + versions explicit
  [ ] Prerequisites: every dependency has install command
  [ ] Build Steps: ordered, executable, no placeholders
  [ ] Test Steps: commands with expected output, port consistency
  [ ] Unexpected Issues: listed with fixes or "none"
  [ ] Zero placeholders in entire document
  [ ] Zero "or" alternatives
  [ ] All version numbers explicit

Output Requirements:
You must output: updated_readme_markdown, filled_items, remaining_gaps,
conflict_resolution, evidence_map_delta, intelligent_predictions.

Output Format:
1. Only output JSON object, no explanations or extra text
2. Do not wrap with markdown code blocks
3. Use newline characters for newlines in updated_readme_markdown
4. JSON must be complete and correctly formatted
"""
        
        code_analysis_str = json.dumps(code_analysis_results, ensure_ascii=False, indent=2)
        gap_list_str = json.dumps(gap_list, ensure_ascii=False, indent=2)
        
        draft_block = ""
        if draft_readme:
            draft_block = f"previous_readme:\n<<<\n{draft_readme}\n<<<\n"
        
        user_prompt = f"""
template_spec:
<<<
{template_spec}

{draft_block}

{review_block}

code_analysis_results:
<<<
{code_analysis_str}

project_materials:
<<<
{project_materials}

{execution_order_info}

{"Generate the five-section README from scratch using the materials and code analysis above." if is_first_round else "Refine the previous README based on Validator feedback. Fix issues, keep correct parts."}

JSON Format:
{{
  "updated_readme_markdown": "## Platform\\n...\\n\\n## Prerequisites\\n...\\n\\n## Build Steps\\n...\\n\\n## Test Steps\\n...\\n\\n## Unexpected Issues\\n...",
  "filled_items": [
    {{"slot": "prerequisites", "content_added": "libssl-dev install command", "confidence": 0.95, "status": "documented", "evidence_ids": ["E10"]}}
  ],
  "remaining_gaps": [],
  "conflict_resolution": [],
  "evidence_map_delta": [
    {{"evidence_id": "E10", "type": "code", "ref": "main.cpp#L5", "quote": "#include <openssl/ssl.h>"}}
  ],
  "intelligent_predictions": [
    {{"item": "service_port", "predicted_value": "8080", "confidence": 0.95, "reasoning": "Spring Boot default", "evidence": "Framework convention", "action_taken": "Completed in Test Steps"}}
  ]
}}

Now please directly output JSON:
"""
        
        response = self.llm_client.call(system_prompt, user_prompt)
        result = parse_json_response(response)
        
        return result
