#!/usr/bin/env python3
"""
Test Git clone project isolation

Verifies:
1. Each project is cloned into its own subdirectory
2. Batch runs do not overwrite each other
3. Directory naming is correct (owner_repo format)
"""

import sys
from pathlib import Path
from utils import clone_repo, extract_github_info
import shutil

def test_clone_isolation():
    """Test project clone isolation"""
    
    print("=" * 70)
    print("🧪 Test Git clone project isolation")
    print("=" * 70)
    
    # Test GitHub URLs (small projects)
    test_repos = [
        "https://github.com/psf/requests",  # requests library
        "https://github.com/pallets/flask", # Flask framework
    ]
    
    # Clean previous test directory
    test_dir = Path("temp_repo")
    if test_dir.exists():
        print(f"\n🧹 Removing old test directory: {test_dir}")
        shutil.rmtree(test_dir)
    
    print("\n" + "─" * 70)
    print("📋 Scenario: clone multiple repos in sequence")
    print("─" * 70)
    
    cloned_paths = []
    
    for i, repo_url in enumerate(test_repos, 1):
        print(f"\n{'─' * 70}")
        print(f"📥 Test {i}: clone {repo_url}")
        print(f"{'─' * 70}")
        
        try:
            # Extract repo info
            github_info = extract_github_info(repo_url)
            expected_dir_name = github_info['full_name'].replace('/', '_')
            expected_path = test_dir / expected_dir_name
            
            print(f"  Expected path: {expected_path}")
            
            # Clone repo
            actual_path = clone_repo(repo_url, ref="main", output_dir="temp_repo")
            
            print(f"  Actual path: {actual_path}")
            print(f"  Exists: {actual_path.exists()}")
            print(f"  Is directory: {actual_path.is_dir()}")
            
            # Verify
            if actual_path == expected_path:
                print(f"  ✅ Path matches")
            else:
                print(f"  ❌ Path mismatch")
                return False
            
            if actual_path.exists() and actual_path.is_dir():
                print(f"  ✅ Directory created")
            else:
                print(f"  ❌ Directory creation failed")
                return False
            
            # Check valid git repo
            git_dir = actual_path / ".git"
            if git_dir.exists():
                print(f"  ✅ Valid Git repository")
            else:
                print(f"  ❌ Not a valid Git repository")
                return False
            
            cloned_paths.append(actual_path)
            
        except Exception as e:
            print(f"  ❌ Clone failed: {e}")
            return False
    
    # Verify all projects in separate dirs
    print("\n" + "=" * 70)
    print("📊 Verification")
    print("=" * 70)
    
    print(f"\n✅ Cloned {len(cloned_paths)} projects into separate directories:")
    for path in cloned_paths:
        print(f"   • {path}")
    
    # Check directory isolation
    print(f"\n🔍 Directory isolation:")
    all_exist = all(p.exists() for p in cloned_paths)
    all_independent = len(cloned_paths) == len(set(cloned_paths))
    
    if all_exist:
        print(f"   ✅ All project directories exist")
    else:
        print(f"   ❌ Some project directories are missing")
        return False
    
    if all_independent:
        print(f"   ✅ All projects are in separate directories")
    else:
        print(f"   ❌ Duplicate project directories")
        return False
    
    # Show directory layout
    print(f"\n📁 temp_repo layout:")
    if test_dir.exists():
        for item in sorted(test_dir.iterdir()):
            if item.is_dir():
                file_count = len(list(item.rglob("*")))
                print(f"   └── {item.name}/ ({file_count} files)")
    
    print("\n" + "=" * 70)
    print("🎉 Test passed: clone isolation works")
    print("=" * 70)
    
    print("\n💡 Benefits:")
    print("   • Each project has its own directory")
    print("   • Batch generation does not overwrite")
    print("   • Clear naming (owner_repo format)")
    print("   • Multiple projects can be processed together")
    
    return True


def test_directory_naming():
    """Test directory naming rules"""
    
    print("\n" + "=" * 70)
    print("🧪 Test directory naming rules")
    print("=" * 70)
    
    test_cases = [
        ("https://github.com/psf/requests", "psf_requests"),
        ("https://github.com/pallets/flask", "pallets_flask"),
        ("https://github.com/owner/repo", "owner_repo"),
    ]
    
    all_passed = True
    
    for url, expected_name in test_cases:
        github_info = extract_github_info(url)
        actual_name = github_info['full_name'].replace('/', '_')
        
        if actual_name == expected_name:
            print(f"✅ {url}")
            print(f"   → {actual_name}")
        else:
            print(f"❌ {url}")
            print(f"   Expected: {expected_name}")
            print(f"   Actual: {actual_name}")
            all_passed = False
    
    if all_passed:
        print("\n✅ All naming rule tests passed")
    
    return all_passed


if __name__ == "__main__":
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║        Git clone project isolation tests                          ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    
    try:
        # Test 1: directory naming
        if not test_directory_naming():
            print("\n❌ Directory naming test failed")
            sys.exit(1)
        
        # Test 2: clone isolation
        print("\n")
        if not test_clone_isolation():
            print("\n❌ Clone isolation test failed")
            sys.exit(1)
        
        print("\n" + "=" * 70)
        print("✅ All tests passed!")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
