"""
Reader: Extracts project signals and drafts README from materials.
"""

from typing import Dict, Any, Optional
from llm_client import LLMClient
from template_spec import TEMPLATE_SPEC
from constraints import GLOBAL_CONSTRAINTS
from utils import parse_json_response


class AgentReader:
    """Reader: Template-guided draft generator from project materials."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    def generate_draft(self, project_materials: str, template_spec: str = TEMPLATE_SPEC, 
                      previous_review_report: Optional[str] = None,
                      previous_readme: Optional[str] = None) -> Dict[str, Any]:
        """Generate/optimize README draft"""
        
        is_first_round = previous_readme is None
        
        if is_first_round:
            task_description = "generate a five-section README"
            mode = "Initial Generation"
        else:
            task_description = "optimize the previous README based on Validator feedback"
            mode = "Iterative Optimization"
        
        if is_first_round:
            mode_instruction = """
[First Round: Initial Generation]
Extract information from project materials and generate the initial README
with exactly five sections: Platform, Prerequisites, Build Steps, Test Steps,
Unexpected Issues.
"""
        else:
            mode_instruction = """
[Subsequent Rounds: Incremental Optimization]
Do NOT regenerate from scratch. Only fix issues pointed out by Validator:
1. Keep the structure and content of previous README
2. Only modify problematic parts
3. Add missing commands or information
4. Keep other parts unchanged
"""

        gen_label = "Initial" if is_first_round else "Optimized"
        gen_instruction = (
            "[Initial Generation] Create the five-section README from project materials."
            if is_first_round else
            "[Incremental Optimization] Only modify problematic parts, keep other content unchanged."
        )

        prev_readme_block = ""
        if previous_readme:
            prev_readme_block = "[Previous README]\n<<<\n" + previous_readme + "\n<<<\n"

        prev_review_block = ""
        if previous_review_report:
            prev_review_block = (
                "[Validator feedback]\n<<<\n" + previous_review_report
                + "\n<<<\nFix only the issues above. Keep correct parts unchanged.\n"
            )
        
        system_prompt = f"""
{GLOBAL_CONSTRAINTS}

You are Reader (README Drafter).
Task: {task_description}.

{'='*60}
Mode: {mode}
{'='*60}

{mode_instruction}

============================================================
Five-Section Template
============================================================

The README MUST contain exactly these five sections in order:

1. **Platform** - OS, language runtime, compiler, global constraints with versions.
2. **Prerequisites** - Project-specific packages, libraries, services with install commands.
3. **Build Steps** - Ordered commands: clone, configure, compile, initialize.
4. **Test Steps** - Verification commands with expected output.
5. **Unexpected Issues** - External obstacles (permissions, network, host limits) with fixes,
   or "No known unexpected issues."

============================================================
Core Principles
============================================================

1. **No placeholders**: No <port>, <name>, etc. Use concrete values.
2. **Intelligently predict values**: Use code analysis and conventions.
3. **Commands directly executable**: Every command can be copy-pasted.
4. **Single path**: One way to build, one way to test.
5. **Explicit versions**: 3.10 not 3.x, not latest.
6. **Expected output for tests**: Every test command states success criteria.
7. **Missing info goes to gap_list**: Uncertain items go to gap_list for Analyzer.

============================================================
Using content_analysis Data
============================================================

project_materials contains content_analysis with deep code scan results.

Supported languages and key fields:
  Python: imports, env_vars, cli_params, frameworks, services
  Java: annotations, properties, frameworks, server_port
  C/C++: includes, libraries, defines, std_version
  JS/TS: imports, env_vars, server_port, frameworks
  Go: imports, env_vars, server_port, frameworks

How to map analysis to sections:

  content_analysis field       README section
  -----------------------------------------------
  std_version, frameworks      Platform
  includes, libraries, imports Prerequisites (install commands)
  env_vars, cli_params         Build Steps (environment setup)
  server_port                  Test Steps (verification URL)
  services (Redis, DB, etc.)   Prerequisites + Build Steps

Intelligent Prediction (when values are missing):
  - Port: framework convention (Flask: 8000, Express: 3000, Spring: 8080)
  - Database: library convention (psycopg2: postgresql://localhost:5432/db)
  - Test values: test_key_12345, test@example.com
  - Versions: common stable (Python 3.10, Node 18.0)

  Confidence handling:
  - 90%+: use directly
  - 70-89%: use + annotate "(recommended for testing)"
  - <70%: use common default + annotate "(default, adjust as needed)"

============================================================
Section-by-Section Drafting Guide
============================================================

**Platform:**
  - Extract OS requirements from Dockerfile, CI configs, or README hints.
  - Extract language version from runtime files (setup.py, go.mod, pom.xml).
  - If not found, predict from framework conventions.

**Prerequisites:**
  - Python: pip packages from imports/requirements.txt
  - C/C++: system libraries from includes (apt-get install ...)
  - Java: JDK version from pom.xml, build tool
  - JS: Node version from package.json engines
  - Go: Go version from go.mod
  - Always provide the full install command.

**Build Steps:**
  - Start with git clone + cd.
  - Then install commands (pip install, npm install, make, mvn, etc.).
  - Then environment configuration (export, .env file).
  - Then compile / build if needed.
  - Then post-build init (db migration, etc.).

**Test Steps:**
  - If test suite exists: pytest, npm test, mvn test, go test, ctest, etc.
  - If web service: curl + expected output.
  - If CLI tool: run with --version or --help + expected output.
  - Always state expected output.

**Unexpected Issues:**
  - Common: permission issues, missing system libs, port conflicts.
  - Each with symptom, cause, fix command.
  - If none known, write "No known unexpected issues."

Output Requirements:
- draft_readme_markdown: The {gen_label} five-section README
- gap_list: Missing information affecting setup
- conflicts: Command or configuration conflicts
- assumptions: Key assumptions made
- evidence_map: Evidence mapping (concise)

Output Format:
1. Only output JSON object, no explanations or extra text
2. Do not wrap with markdown code blocks
3. Use newline characters for newlines in draft_readme_markdown
4. JSON must be complete and correctly formatted
"""
        
        user_prompt = f"""
template_spec:
<<<
{template_spec}

{prev_readme_block}

{prev_review_block}

project_materials:
<<<
{project_materials}

{gen_instruction}

JSON Format:
{{
  "draft_readme_markdown": "## Platform\\n...\\n\\n## Prerequisites\\n...\\n\\n## Build Steps\\n...\\n\\n## Test Steps\\n...\\n\\n## Unexpected Issues\\n...",
  "gap_list": [
    {{"slot": "prerequisites", "missing": "...", "deployment_impact": "..."}}
  ],
  "conflicts": [],
  "assumptions": [
    {{"assumption": "...", "risk": "...", "action_needed": "..."}}
  ],
  "evidence_map": [
    {{"evidence_id": "E1", "type": "file", "ref": "...", "quote": "..."}}
  ]
}}

Now please directly output JSON:
"""
        
        response = self.llm_client.call(system_prompt, user_prompt)
        result = parse_json_response(response)
        
        return result
