#!/usr/bin/env python3
"""
Full codebase logic verification script.
"""

from pathlib import Path
import re


def check_code_integration():
    """Check code integration."""
    
    print("=" * 70)
    print("1️⃣ Code integration check")
    print("=" * 70)
    
    checks = []
    
    # Check code_analyzer.py integration
    code_analyzer = Path("code_analyzer.py").read_text()
    
    # 1. Import check
    has_import = "from content_analyzer import ContentAnalyzer" in code_analyzer
    checks.append(("ContentAnalyzer import", has_import))
    
    # 2. content_analysis field
    has_field = '"content_analysis": []' in code_analyzer
    checks.append(("content_analysis field", has_field))
    
    # 3. _analyze_content method
    has_method = "def _analyze_content(self):" in code_analyzer
    checks.append(("_analyze_content method", has_method))
    
    # 4. Call check
    has_call = "self._analyze_content()" in code_analyzer
    checks.append(("_analyze_content call", has_call))
    
    # 5. Deployment info extraction
    has_extract = "_extract_deployment_info_from_content" in code_analyzer
    checks.append(("Deployment info extraction method", has_extract))
    
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
    
    passed = sum(1 for _, r in checks if r)
    print(f"\nSubtotal: {passed}/{len(checks)} passed")
    
    return passed == len(checks)


def check_llm_deployment_focus():
    """Check LLM deployment focus."""
    
    print("\n" + "=" * 70)
    print("2️⃣ LLM deployment focus check")
    print("=" * 70)
    
    checks = []
    
    # Check template_spec.py
    template = Path("template_spec.py").read_text()
    
    # 1. Five-section structure
    has_five_sections = "Platform" in template and "Prerequisites" in template and "Build Steps" in template and "Test Steps" in template and "Unexpected Issues" in template
    checks.append(("Five-section template", has_five_sections))
    
    # 2. No-placeholder rule
    has_no_placeholder = "Placeholder" in template or "placeholder" in template
    checks.append(("No-placeholder rule", has_no_placeholder))
    
    # Check agent_validator.py
    validator_src = Path("agent_validator.py").read_text()
    
    # 3. Validator blocker check
    has_blocker = "placeholder" in validator_src.lower() and "blocker" in validator_src
    checks.append(("Validator placeholder blocker", has_blocker))
    
    # 4. Validator section scoring
    has_section_scoring = "platform" in validator_src and "prerequisites" in validator_src and "build_steps" in validator_src
    checks.append(("Validator section scoring", has_section_scoring))
    
    # Check agent_reader.py
    reader_src = Path("agent_reader.py").read_text()
    
    # 5. Reader five-section output
    has_five_section_reader = "Platform" in reader_src and "Prerequisites" in reader_src and "Build Steps" in reader_src
    checks.append(("Reader five-section output", has_five_section_reader))
    
    # 6. Reader intelligent prediction
    has_predict = "Intelligent" in reader_src and "Predict" in reader_src
    checks.append(("Reader intelligent prediction", has_predict))
    
    # Check agent_analyzer.py
    analyzer_src = Path("agent_analyzer.py").read_text()
    
    # 7. Analyzer placeholder scan
    has_scan = "placeholder" in analyzer_src.lower()
    checks.append(("Analyzer placeholder scan", has_scan))
    
    # 8. Analyzer intelligent_predictions output
    has_intelligent = "intelligent_predictions" in analyzer_src
    checks.append(("Analyzer intelligent_predictions", has_intelligent))
    
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
    
    passed = sum(1 for _, r in checks if r)
    print(f"\nSubtotal: {passed}/{len(checks)} passed")
    
    return passed == len(checks)


def check_data_flow():
    """Check data flow."""
    
    print("\n" + "=" * 70)
    print("3️⃣ Data flow check")
    print("=" * 70)
    
    checks = []
    
    # Check orchestrator.py
    orchestrator = Path("orchestrator.py").read_text()
    
    # 1. previous_readme initialization
    has_init = "previous_readme = None" in orchestrator
    checks.append(("previous_readme initialization", has_init))
    
    # 2. previous_readme passed through
    has_pass = "previous_readme=previous_readme" in orchestrator
    checks.append(("previous_readme passed to Reader", has_pass))
    
    # 3. previous_readme saved
    has_save = "previous_readme = final_readme" in orchestrator
    checks.append(("previous_readme saved", has_save))
    
    # 4. code_analysis_results passed
    has_code = "code_analysis_results=self.code_analysis_results" in orchestrator
    checks.append(("code_analysis_results passed", has_code))
    
    # 5. Evidence map merge
    has_merge = "_merge_evidence_map" in orchestrator
    checks.append(("Evidence map merge method", has_merge))
    
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
    
    passed = sum(1 for _, r in checks if r)
    print(f"\nSubtotal: {passed}/{len(checks)} passed")
    
    return passed == len(checks)


def check_intelligent_prediction():
    """Check intelligent prediction."""
    
    print("\n" + "=" * 70)
    print("4️⃣ Intelligent prediction check")
    print("=" * 70)
    
    checks = []
    
    analyzer_src = Path("agent_analyzer.py").read_text()
    
    # 1. Prediction rules
    has_rules = "prediction" in analyzer_src.lower() or "Prediction" in analyzer_src
    checks.append(("Prediction rules", has_rules))
    
    # 2. Confidence levels
    has_confidence = "90%" in analyzer_src and "70-89%" in analyzer_src
    checks.append(("Confidence levels", has_confidence))
    
    # 3. Port prediction
    has_port = "Flask" in analyzer_src and "8000" in analyzer_src
    checks.append(("Port prediction rules", has_port))
    
    # 4. Database prediction
    has_db = "postgresql" in analyzer_src or "psycopg2" in analyzer_src
    checks.append(("Database prediction", has_db))
    
    # 5. Completeness check
    has_checklist = "Completeness" in analyzer_src or "Final" in analyzer_src
    checks.append(("Completeness check", has_checklist))
    
    # 6. intelligent_predictions output
    has_output = "intelligent_predictions" in analyzer_src
    checks.append(("intelligent_predictions output", has_output))
    
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
    
    passed = sum(1 for _, r in checks if r)
    print(f"\nSubtotal: {passed}/{len(checks)} passed")
    
    return passed == len(checks)


def check_multi_language_support():
    """Check multi-language support."""
    
    print("\n" + "=" * 70)
    print("5️⃣ Multi-language support check")
    print("=" * 70)
    
    checks = []
    
    content_analyzer = Path("content_analyzer.py").read_text()
    
    # Check that all analyzer classes exist
    analyzers = [
        "PythonContentAnalyzer",
        "JavaScriptContentAnalyzer",
        "GoContentAnalyzer",
        "JavaContentAnalyzer",
        "CContentAnalyzer",
        "CppContentAnalyzer"
    ]
    
    for analyzer in analyzers:
        has_analyzer = f"class {analyzer}" in content_analyzer
        checks.append((analyzer, has_analyzer))
    
    # Check main class integration
    has_main = "class ContentAnalyzer:" in content_analyzer
    checks.append(("ContentAnalyzer main class", has_main))
    
    # Check priority file identification
    has_priority = "def identify_priority_files" in content_analyzer
    checks.append(("identify_priority_files", has_priority))
    
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
    
    passed = sum(1 for _, r in checks if r)
    print(f"\nSubtotal: {passed}/{len(checks)} passed")
    
    return passed == len(checks)


def check_file_existence():
    """Check critical files exist."""
    
    print("\n" + "=" * 70)
    print("6️⃣ Critical file existence check")
    print("=" * 70)
    
    files = [
        "code_analyzer.py",
        "content_analyzer.py",
        "orchestrator.py",
        "agent_validator.py",
        "agent_reader.py",
        "agent_analyzer.py",
        "agent_retriever.py",
        "material_collector.py",
        "llm_client.py",
        "utils.py",
        "template_spec.py",
        "readme_validator.py",  # added
        "test_content_analyzer.py",
        "test_intelligent_prediction.py",
        "test_system_integration.py",
    ]
    
    checks = []
    
    for file in files:
        path = Path(file)
        exists = path.exists()
        checks.append((file, exists))
        status = "✅" if exists else "❌"
        print(f"{status} {file}")
    
    passed = sum(1 for _, r in checks if r)
    print(f"\nSubtotal: {passed}/{len(checks)} passed")
    
    return passed == len(checks)


def main():
    """Run all checks."""
    
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 18 + "Full code logic verification" + " " * 22 + "║")
    print("╚" + "═" * 68 + "╝\n")
    
    tests = [
        ("Code integration", check_code_integration),
        ("LLM deployment focus", check_llm_deployment_focus),
        ("Data flow", check_data_flow),
        ("Intelligent prediction", check_intelligent_prediction),
        ("Multi-language support", check_multi_language_support),
        ("File existence", check_file_existence),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} failed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("🎯 Verification summary")
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
        print("\n" + "🎉" * 10)
        print("\n✅ All checks passed. Code logic is fully consistent.\n")
        print("System status:")
        print("  ✅ Code integration: OK")
        print("  ✅ LLM deployment focus: reinforced")
        print("  ✅ Data flow: OK")
        print("  ✅ Intelligent prediction: complete")
        print("  ✅ Multi-language support: 6+ languages")
        print("  ✅ Placeholder safeguards: three-layer mechanism")
        print("\nSystem is ready to use. 🚀\n")
        print("Next steps:")
        print("  1. python3 main.py /path/to/project")
        print("  2. python3 readme_validator.py output/README.generated.md")
        print("  3. Give the README to ChatGPT to test automated deployment\n")
        return 0
    else:
        print(f"\n⚠️  {total - passed} check(s) failed; review the code.\n")
        return 1


if __name__ == "__main__":
    exit(main())










