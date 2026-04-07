"""
Test that all modules import successfully.
"""

def test_imports():
    """Test imports."""
    try:
        from config import Config
        print("✓ config imported successfully")
        
        from template_spec import TEMPLATE_SPEC
        print("✓ template_spec imported successfully")
        
        from constraints import GLOBAL_CONSTRAINTS
        print("✓ constraints imported successfully")
        
        from utils import clone_repo, save_json, load_json
        print("✓ utils imported successfully")
        
        from code_analyzer import CodeAnalyzer
        print("✓ code_analyzer imported successfully")
        
        from material_collector import MaterialCollector
        print("✓ material_collector imported successfully")
        
        from llm_client import LLMClient
        print("✓ llm_client imported successfully")
        
        from agent_reader import AgentReader
        print("✓ agent_reader imported successfully")
        
        from agent_analyzer import AgentAnalyzer
        print("✓ agent_analyzer imported successfully")
        
        from orchestrator import Orchestrator
        print("✓ orchestrator imported successfully")
        
        print("\nAll modules imported successfully!")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_imports()

