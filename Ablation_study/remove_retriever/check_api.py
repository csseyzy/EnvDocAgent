#!/usr/bin/env python3
"""
API validation tool
Checks OpenAI, Azure OpenAI, and Anthropic APIs
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def print_header(title):
    """Print header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_section(title):
    """Print section title"""
    print("\n" + "-" * 80)
    print(f"  {title}")
    print("-" * 80)


def check_azure_openai():
    """Check Azure OpenAI API"""
    print_section("Check Azure OpenAI")
    
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    # Check configuration
    print("\n📋 Configuration check:")
    config_ok = True
    
    if api_key:
        print(f"  ✓ API Key: {'*' * 20}...{api_key[-4:]}")
    else:
        print("  ✗ API Key: not set")
        config_ok = False
    
    if endpoint:
        print(f"  ✓ Endpoint: {endpoint}")
    else:
        print("  ✗ Endpoint: not set")
        config_ok = False
    
    if deployment:
        print(f"  ✓ Deployment: {deployment}")
    else:
        print("  ✗ Deployment: not set")
        config_ok = False
    
    print(f"  ✓ API Version: {api_version}")
    
    if not config_ok:
        print("\n❌ Azure OpenAI configuration incomplete")
        return False
    
    # Test connection
    print("\n🔧 Test API connection:")
    try:
        from openai import AzureOpenAI
        
        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
        
        print("  ✓ Client initialized")
        
        # Test API call
        print("\n🚀 Test API call:")
        
        # Minimal params for broad compatibility
        call_params = {
            "model": deployment,
            "messages": [
                {"role": "user", "content": "Say 'API is working!' in one short sentence."}
            ]
        }
        
        # Optional params (some models may not support)
        try:
            # New API (>= 2024-08-01-preview) uses max_completion_tokens
            if api_version >= "2024-08-01-preview":
                call_params["max_completion_tokens"] = 100
            else:
                call_params["max_tokens"] = 100
        except:
            pass  # skip if unsupported
        
        response = client.chat.completions.create(**call_params)
        
        result = response.choices[0].message.content
        print(f"  ✓ API call succeeded")
        print(f"  📝 Response: {result}")
        
        if hasattr(response, 'usage'):
            print(f"\n📊 Usage:")
            print(f"  - Prompt tokens: {response.usage.prompt_tokens}")
            print(f"  - Completion tokens: {response.usage.completion_tokens}")
            print(f"  - Total tokens: {response.usage.total_tokens}")
        
        print("\n✅ Azure OpenAI API is fully available!")
        return True
        
    except ImportError:
        print("  ✗ Missing openai package, run: pip install openai")
        return False
    except Exception as e:
        print(f"  ✗ API test failed")
        print(f"\n❌ Error message:")
        print(f"  {str(e)}")
        
        error_str = str(e).lower()
        print(f"\n💡 Possible causes:")
        
        if "401" in error_str or "unauthorized" in error_str:
            print("  - API Key invalid or expired")
            print("  - Fix: Regenerate API Key in Azure Portal")
        
        elif "404" in error_str or "not found" in error_str or "deploymentnotfound" in error_str:
            print("  - Deployment name does not exist")
            print("  - Fix: run 'python3 diagnose_azure.py' for details")
            print(f"  - Current deployment name: '{deployment}'")
            print("  - Confirm the actual deployment name in Azure Portal")
        
        elif "403" in error_str or "forbidden" in error_str:
            print("  - No access or quota exhausted")
            print("  - Fix: Check Azure subscription and quota")
        
        elif "timeout" in error_str:
            print("  - Network timeout")
            print("  - Fix: Check network connection")
        
        else:
            print("  - Unknown error; see details above")
        
        return False


def check_openai():
    """Check standard OpenAI API"""
    print_section("Check standard OpenAI")
    
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    
    # Check configuration
    print("\n📋 Configuration check:")
    
    if api_key:
        print(f"  ✓ API Key: {api_key[:8]}...{api_key[-4:]}")
    else:
        print("  ✗ API Key: not set")
        return False
    
    if base_url:
        print(f"  ✓ Base URL: {base_url}")
    else:
        print(f"  ℹ Base URL: default (https://api.openai.com/v1)")
    
    print(f"  ✓ Model: {model}")
    
    # Test connection
    print("\n🔧 Test API connection:")
    try:
        import openai
        
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        
        client = openai.OpenAI(**client_kwargs)
        print("  ✓ Client initialized")
        
        # Test API call
        print("\n🚀 Test API call:")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'API is working!' in one short sentence."}
            ],
            max_tokens=50,
            temperature=0.3
        )
        
        result = response.choices[0].message.content
        print(f"  ✓ API call succeeded")
        print(f"  📝 Response: {result}")
        
        if hasattr(response, 'usage'):
            print(f"\n📊 Usage:")
            print(f"  - Prompt tokens: {response.usage.prompt_tokens}")
            print(f"  - Completion tokens: {response.usage.completion_tokens}")
            print(f"  - Total tokens: {response.usage.total_tokens}")
        
        print("\n✅ OpenAI API is fully available!")
        return True
        
    except ImportError:
        print("  ✗ Missing openai package, run: pip install openai")
        return False
    except Exception as e:
        print(f"  ✗ API test failed")
        print(f"\n❌ Error message:")
        print(f"  {str(e)}")
        
        error_str = str(e).lower()
        print(f"\n💡 Possible causes:")
        
        if "401" in error_str or "unauthorized" in error_str:
            print("  - API Key invalid")
            print("  - Fix: Verify API Key")
        elif "404" in error_str:
            print("  - Model missing or Base URL incorrect")
            print(f"  - Current model: {model}")
            if base_url:
                print(f"  - Current Base URL: {base_url}")
        elif "429" in error_str:
            print("  - Rate limit or quota exhausted")
        else:
            print("  - Unknown error; see details above")
        
        return False


def check_anthropic():
    """Check Anthropic Claude API"""
    print_section("Check Anthropic Claude")
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    model = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
    
    # Check configuration
    print("\n📋 Configuration check:")
    
    if api_key:
        print(f"  ✓ API Key: {api_key[:8]}...{api_key[-4:]}")
    else:
        print("  ✗ API Key: not set")
        return False
    
    print(f"  ✓ Model: {model}")
    
    # Test connection
    print("\n🔧 Test API connection:")
    try:
        from anthropic import Anthropic
        
        client = Anthropic(api_key=api_key)
        print("  ✓ Client initialized")
        
        # Test API call
        print("\n🚀 Test API call:")
        response = client.messages.create(
            model=model,
            max_tokens=50,
            system="You are a helpful assistant.",
            messages=[
                {"role": "user", "content": "Say 'API is working!' in one short sentence."}
            ],
            temperature=0.3
        )
        
        result = response.content[0].text
        print(f"  ✓ API call succeeded")
        print(f"  📝 Response: {result}")
        
        if hasattr(response, 'usage'):
            print(f"\n📊 Usage:")
            print(f"  - Input tokens: {response.usage.input_tokens}")
            print(f"  - Output tokens: {response.usage.output_tokens}")
        
        print("\n✅ Anthropic Claude API is fully available!")
        return True
        
    except ImportError:
        print("  ✗ Missing anthropic package, run: pip install anthropic")
        return False
    except Exception as e:
        print(f"  ✗ API test failed")
        print(f"\n❌ Error message:")
        print(f"  {str(e)}")
        
        error_str = str(e).lower()
        print(f"\n💡 Possible causes:")
        
        if "401" in error_str or "unauthorized" in error_str:
            print("  - API Key invalid")
        elif "404" in error_str:
            print("  - Model does not exist")
            print(f"  - Current model: {model}")
        elif "429" in error_str:
            print("  - Rate limit or quota exhausted")
        else:
            print("  - Unknown error; see details above")
        
        return False


def main():
    """Main entry"""
    print_header("API validation tool")
    
    # Check .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  Warning: .env file not found")
        print("Suggestion: create .env and configure API keys\n")
    
    # LLM provider from env
    provider = os.getenv("LLM_PROVIDER", "").lower()
    
    print(f"📌 LLM_PROVIDER: {provider or 'not set (auto-detect)'}\n")
    
    results = {}
    
    # Check APIs based on configuration
    if provider == "azure" or os.getenv("AZURE_OPENAI_API_KEY"):
        results["azure"] = check_azure_openai()
    
    if provider == "openai" or os.getenv("OPENAI_API_KEY"):
        results["openai"] = check_openai()
    
    if provider == "anthropic" or os.getenv("ANTHROPIC_API_KEY"):
        results["anthropic"] = check_anthropic()
    
    # Summary
    print_header("Check summary")
    
    if not results:
        print("❌ No LLM API configuration detected")
        print("\nConfigure at least one LLM in .env:")
        print("  - OpenAI: OPENAI_API_KEY")
        print("  - Azure OpenAI: AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT")
        print("  - Anthropic: ANTHROPIC_API_KEY")
        return 1
    
    available = [name for name, ok in results.items() if ok]
    unavailable = [name for name, ok in results.items() if not ok]
    
    if available:
        print("✅ Available APIs:")
        for name in available:
            print(f"  ✓ {name.upper()}")
    
    if unavailable:
        print("\n❌ Unavailable APIs:")
        for name in unavailable:
            print(f"  ✗ {name.upper()}")
    
    print("\n" + "-" * 80)
    if available:
        print("\n💡 Suggestions:")
        if len(available) == 1:
            recommended = available[0]
            print(f"  Recommended: {recommended.upper()}")
            print(f"\n  Set in .env:")
            print(f"  LLM_PROVIDER={recommended}")
        else:
            print(f"  Multiple APIs available; pick one:")
            for name in available:
                print(f"  - LLM_PROVIDER={name}")
    
    print("\n" + "-" * 80)
    print("\n📚 Related docs:")
    print("  - AZURE_OPENAI_SETUP.md - Azure OpenAI setup guide")
    print("  - README.md - Project readme")
    print("  - diagnose_azure.py - Azure config diagnostics")
    print()
    
    return 0 if available else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)



























