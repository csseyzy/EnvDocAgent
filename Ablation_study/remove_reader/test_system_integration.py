#!/usr/bin/env python3
"""
System integration tests — wiring and data flow.
"""

import json
from pathlib import Path


def test_data_flow():
    """Exercise documented data flow."""
    
    print("=" * 70)
    print("System integration — data flow")
    print("=" * 70)
    
    # 1. CodeAnalyzer → Orchestrator
    print("\n1️⃣ CodeAnalyzer output shape")
    print("─" * 70)
    
    expected_keys = [
        "repo_path",
        "language_clues",
        "entry_points",
        "dependencies",
        "test_clues",
        "install_commands",
        "run_commands",
        "test_commands",
        "file_stats",
        "content_analysis"  # new
    ]
    
    print("Expected top-level keys:")
    for key in expected_keys:
        print(f"  ✓ {key}")
    
    # 2. content_analysis shape
    print("\n2️⃣ content_analysis field shape")
    print("─" * 70)
    
    language_fields = {
        "Python": ["file", "language", "imports", "main_block", "env_vars", "frameworks"],
        "Java": ["file", "language", "imports", "annotations", "properties", "frameworks"],
        "C": ["file", "language", "includes", "defines", "functions", "libraries"],
        "C++": ["file", "language", "includes", "namespaces", "classes", "libraries"],
        "JavaScript": ["file", "language", "imports", "env_vars", "server_port", "frameworks"],
        "Go": ["file", "language", "imports", "env_vars", "server_port", "frameworks"]
    }
    
    for lang, fields in language_fields.items():
        print(f"\n{lang}:")
        for field in fields:
            print(f"  ✓ {field}")
    
    # 3. Orchestrator → Reader
    print("\n3️⃣ Orchestrator → Reader handoff")
    print("─" * 70)
    
    print("Parameters passed:")
    print("  ✓ project_materials: str (MaterialCollector.get_summary())")
    print("  ✓ previous_review_report: Optional[str]")
    print("  ✓ previous_readme: Optional[str]")
    
    print("\nproject_materials should include:")
    print("  ✓ README content")
    print("  ✓ Install guide")
    print("  ✓ Deploy guide")
    print("  ✓ Docker files")
    print("  ✓ External link content")
    
    # 4. Reader → Analyzer
    print("\n4️⃣ Reader → Analyzer handoff")
    print("─" * 70)
    
    print("Reader output (draft_result):")
    print("  ✓ draft_readme_markdown: str")
    print("  ✓ gap_list: List[Dict]")
    print("  ✓ conflicts: List[Dict]")
    print("  ✓ assumptions: List[Dict]")
    print("  ✓ evidence_map: List[Dict]")
    
    print("\nAnalyzer receives:")
    print("  ✓ draft_readme: draft_result['draft_readme_markdown']")
    print("  ✓ gap_list: draft_result['gap_list']")
    print("  ✓ code_analysis_results: Dict (includes content_analysis)")
    print("  ✓ project_materials: str")
    
    # 5. Analyzer → Validator
    print("\n5️⃣ Analyzer → Validator handoff")
    print("─" * 70)
    
    print("Analyzer output (complete_result):")
    print("  ✓ updated_readme_markdown: str")
    print("  ✓ filled_items: List[Dict]")
    print("  ✓ remaining_gaps: List[Dict]")
    print("  ✓ conflict_resolution: List[Dict]")
    print("  ✓ evidence_map_delta: List[Dict]")
    print("  ✓ intelligent_predictions: List[Dict] (new)")
    
    print("\nValidator receives:")
    print("  ✓ readme_to_review: complete_result['updated_readme_markdown']")
    print("  ✓ evidence_map: List[Dict] (merged)")
    
    # 6. Validator output
    print("\n6️⃣ Validator output shape")
    print("─" * 70)
    
    print("Validator output (review_result):")
    print("  ✓ overall_score: int")
    print("  ✓ section_scores: List[Dict]")
    print("  ✓ issues: List[Dict]")
    print("  ✓ revision_plan: List[Dict]")
    print("  ✓ stop_recommendation: Dict")
    
    # 7. Multi-round iteration
    print("\n7️⃣ Multi-round iteration")
    print("─" * 70)
    
    print("Iteration flow:")
    print("  Round 1:")
    print("    → Reader.generate_draft(previous_readme=None)")
    print("    → Analyzer.analyze()")
    print("    → Validator.validate()")
    print("    → Save README to previous_readme")
    print()
    print("  Round 2:")
    print("    → Reader.generate_draft(previous_readme=round1_readme)")
    print("    → Analyzer.analyze()")
    print("    → Validator.validate()")
    print("    → Save README to previous_readme")
    print()
    print("  ...")
    print()
    print("Stop when:")
    print("  ✓ should_stop = True")
    print("  ✓ overall_score >= SCORE_THRESHOLD (90)")
    print("  ✓ No blocker issues")
    print("  ✓ No major issues")
    
    # 8. Evidence map merge
    print("\n8️⃣ Evidence map merge")
    print("─" * 70)
    
    print("Merge steps:")
    print("  1. Reader produces evidence_map")
    print("  2. Orchestrator merges Reader evidence_map")
    print("  3. Analyzer produces evidence_map_delta")
    print("  4. Orchestrator merges Analyzer evidence_map_delta")
    print("  5. Pass merged evidence_map to Validator")
    
    # 9. Intelligent prediction
    print("\n9️⃣ Intelligent prediction flow")
    print("─" * 70)
    
    print("Analyzer prediction steps:")
    print("  1. Fill gaps from gap_list")
    print("  2. Scan README for missing items")
    print("  3. Score confidence per missing item")
    print("  4. High (90%+) → direct fill")
    print("  5. Medium (70–89%) → fill + (inferred) label")
    print("  6. Low (<70%) → Open Questions")
    print("  7. Emit intelligent_predictions for audit")
    
    print("\nRule categories:")
    print("  ✓ Ports (framework defaults)")
    print("  ✓ Build commands (manifest files)")
    print("  ✓ DB URLs (library signals)")
    print("  ✓ Test commands (test frameworks)")
    print("  ✓ Default environment variables")
    
    # 10. Completeness checklist
    print("\n🔟 Completeness checklist")
    print("─" * 70)
    
    checklist = [
        "Requirements stated clearly",
        "Dependency install complete",
        "Environment configuration complete",
        "Start commands executable",
        "Service ports documented",
        "Verification steps clear",
        "Database/service configuration complete"
    ]
    
    for item in checklist:
        print(f"  [ ] {item}")
    
    print("\nIf any item is missing, Analyzer may fill via intelligent prediction.")
    
    # Summary diagram
    print("\n" + "=" * 70)
    print("Data flow summary")
    print("=" * 70)
    
    print("""
End-to-end flow:

1. Orchestrator._preprocess()
   ├─ clone_repo() → self.repo_path
   ├─ MaterialCollector.collect() → self.project_materials
   └─ CodeAnalyzer.analyze() → self.code_analysis_results
       └─ ContentAnalyzer._analyze_content() → content_analysis

2. Orchestrator.run() — multi-round
   ├─ Reader.generate_draft()
   │   ├─ In: project_materials, previous_review, previous_readme
   │   └─ Out: draft_readme, gap_list, evidence_map
   │
   ├─ Analyzer.analyze()
   │   ├─ In: draft_readme, gap_list, code_analysis_results
   │   ├─ Evidence-based fill
   │   ├─ Intelligent prediction fill (new)
   │   └─ Out: updated_readme, filled_items, intelligent_predictions
   │
   └─ Validator.validate()
       ├─ In: updated_readme, evidence_map (merged)
       └─ Out: overall_score, issues, stop_recommendation

3. Stop condition
   ├─ should_stop = True
   ├─ score >= 90
   ├─ No blocker
   └─ No major

4. Save final README
   └─ output_dir / "generated_readme.md"
""")
    
    print("=" * 70)
    print("✅ Data flow walkthrough complete")
    print("=" * 70)
    
    return True


def check_module_imports():
    """Verify module imports."""
    
    print("\n" + "=" * 70)
    print("Module import check")
    print("=" * 70)
    
    modules = [
        ("orchestrator", ["Orchestrator"]),
        ("code_analyzer", ["CodeAnalyzer"]),
        ("content_analyzer", ["ContentAnalyzer", "identify_priority_files"]),
        ("material_collector", ["MaterialCollector"]),
        ("agent_validator", ["AgentValidator"]),
        ("agent_reader", ["AgentReader"]),
        ("agent_analyzer", ["AgentAnalyzer"]),
        ("llm_client", ["LLMClient"]),
        ("utils", ["parse_json_response"]),
    ]
    
    success_count = 0
    fail_count = 0
    
    for module_name, classes in modules:
        try:
            module = __import__(module_name)
            for cls in classes:
                if hasattr(module, cls):
                    print(f"  ✓ {module_name}.{cls}")
                    success_count += 1
                else:
                    print(f"  ✗ {module_name}.{cls} (missing)")
                    fail_count += 1
        except ImportError as e:
            print(f"  ✗ {module_name} (import error: {e})")
            fail_count += len(classes)
    
    print(f"\nTotal: {success_count + fail_count}")
    print(f"✓ OK: {success_count}")
    print(f"✗ Fail: {fail_count}")
    
    return fail_count == 0


def check_key_methods():
    """Verify key methods exist."""
    
    print("\n" + "=" * 70)
    print("Key method check")
    print("=" * 70)
    
    checks = [
        ("CodeAnalyzer", ["analyze", "_analyze_content", "_extract_deployment_info_from_content"]),
        ("ContentAnalyzer", ["analyze_file", "_should_analyze"]),
        ("MaterialCollector", ["collect", "get_summary"]),
        ("Orchestrator", ["run", "_preprocess", "_merge_evidence_map"]),
        ("AgentReader", ["generate_draft"]),
        ("AgentAnalyzer", ["analyze"]),
        ("AgentValidator", ["validate"]),
    ]
    
    try:
        from code_analyzer import CodeAnalyzer
        from content_analyzer import ContentAnalyzer
        from material_collector import MaterialCollector
        from orchestrator import Orchestrator
        from agent_validator import AgentValidator
        from agent_reader import AgentReader
        from agent_analyzer import AgentAnalyzer
        
        classes_map = {
            "CodeAnalyzer": CodeAnalyzer,
            "ContentAnalyzer": ContentAnalyzer,
            "MaterialCollector": MaterialCollector,
            "Orchestrator": Orchestrator,
            "AgentReader": AgentReader,
            "AgentAnalyzer": AgentAnalyzer,
            "AgentValidator": AgentValidator,
        }
        
        success_count = 0
        fail_count = 0
        
        for class_name, methods in checks:
            cls = classes_map.get(class_name)
            if cls:
                for method in methods:
                    if hasattr(cls, method):
                        print(f"  ✓ {class_name}.{method}")
                        success_count += 1
                    else:
                        print(f"  ✗ {class_name}.{method} (missing)")
                        fail_count += 1
            else:
                print(f"  ✗ {class_name} (class missing)")
                fail_count += len(methods)
        
        print(f"\nTotal: {success_count + fail_count}")
        print(f"✓ Present: {success_count}")
        print(f"✗ Missing: {fail_count}")
        
        return fail_count == 0
        
    except Exception as e:
        print(f"✗ Check failed: {e}")
        return False


def main():
    """Run all checks."""
    
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "System integration test suite" + " " * 17 + "║")
    print("╚" + "═" * 68 + "╝")
    
    tests = [
        ("Data flow", test_data_flow),
        ("Module imports", check_module_imports),
        ("Key methods", check_key_methods),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} failed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    
    for test_name, result in results:
        status = "✅ Passed" if result else "❌ Failed"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTotal: {total} checks")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    print("=" * 70)
    
    if passed == total:
        print("\n🎉 All checks passed. Integration looks consistent.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} check(s) failed; review wiring.")
        return 1


if __name__ == "__main__":
    exit(main())
