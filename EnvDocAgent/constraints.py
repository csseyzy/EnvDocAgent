"""
Global Hard Constraints (must be included in all LLM Agent system prompts)
"""

GLOBAL_CONSTRAINTS = """
## Global Hard Constraints

The README must contain exactly five sections: Platform, Prerequisites, Build Steps, Test Steps, Unexpected Issues.

You can only use the materials provided in the input (project_materials / code_analysis_results / draft_readme / evidence_map, etc.) to produce content; you must not fabricate facts.

For each key fact (language version, dependency version, install/run/test commands, ports, environment variables), you must provide evidence references and write them to evidence_map.

If you can only obtain a version "range/constraint" rather than an exact version, you must clearly mark it as "constraint" and provide the best concrete value via intelligent prediction.

If there are conflicts (different sources giving different commands/versions), do not forcibly merge: you must mark the conflict and provide "which one to use as the main process + reason", and record the rest in the conflicts output field.

Output must be strict JSON (no explanatory text allowed), and JSON can contain markdown fields.
"""


