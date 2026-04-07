"""
Azure OpenAI configuration diagnostic tool
"""

import os
from pathlib import Path

def diagnose_azure_config():
    """Diagnose Azure OpenAI configuration"""
    
    print("\n" + "="*80)
    print("Azure OpenAI configuration diagnostic tool")
    print("="*80 + "\n")
    
    # Read .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    config = {}
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                config[key] = value
    
    # Check configuration
    print("📋 Current configuration:")
    print("-" * 80)
    
    azure_key = config.get('AZURE_OPENAI_API_KEY', '')
    azure_endpoint = config.get('AZURE_OPENAI_ENDPOINT', '')
    azure_deployment = config.get('AZURE_OPENAI_DEPLOYMENT', '')
    azure_version = config.get('AZURE_OPENAI_API_VERSION', '')
    
    print(f"✓ AZURE_OPENAI_API_KEY: {'*' * 20}...{azure_key[-4:] if azure_key else 'not set'}")
    print(f"{'✓' if azure_endpoint else '✗'} AZURE_OPENAI_ENDPOINT: {azure_endpoint or 'not set'}")
    print(f"{'✓' if azure_deployment else '✗'} AZURE_OPENAI_DEPLOYMENT: {azure_deployment or 'not set'}")
    print(f"✓ AZURE_OPENAI_API_VERSION: {azure_version or '2024-02-15-preview (default)'}")
    
    print("\n" + "-" * 80)
    
    # Problem diagnosis
    print("\n🔍 Problem diagnosis:")
    print("-" * 80)
    
    issues = []
    
    if not azure_key:
        issues.append("❌ Azure API Key is not set")
    
    if not azure_endpoint:
        issues.append("❌ Azure Endpoint is not set")
    
    if not azure_deployment:
        issues.append("❌ Azure Deployment is not set")
    else:
        print(f"\n⚠️  Current deployment name: '{azure_deployment}'")
        print(f"   The error indicates this deployment does not exist in your Azure resource.")
    
    if azure_endpoint:
        # Extract resource name
        try:
            resource_name = azure_endpoint.split('//')[1].split('.')[0]
            print(f"\n📍 Your Azure resource name: {resource_name}")
        except:
            issues.append("⚠️  Endpoint format may be incorrect")
    
    if issues:
        print("\nIssues found:")
        for issue in issues:
            print(f"  {issue}")
    
    # Solutions
    print("\n" + "="*80)
    print("💡 Solutions")
    print("="*80 + "\n")
    
    print("Follow these steps to find the correct deployment name:\n")
    
    print("Method 1: Use Azure Portal")
    print("-" * 40)
    print("1. Visit: https://portal.azure.com")
    print("2. Search for your Azure OpenAI resource")
    if azure_endpoint:
        try:
            resource_name = azure_endpoint.split('//')[1].split('.')[0]
            print(f"   Resource name: {resource_name}")
        except:
            pass
    print("3. Click 'Model deployments' in the left menu")
    print("4. Check the 'Deployment name' column")
    print("5. Copy the deployment name you want to use\n")
    
    print("Method 2: Use Azure OpenAI Studio")
    print("-" * 40)
    print("1. Visit: https://oai.azure.com/")
    print("2. Select your subscription and resource")
    print("3. Click 'Deployments'")
    print("4. See the names in the deployment list\n")
    
    print("Method 3: If you have no deployment, create one")
    print("-" * 40)
    print("1. In Azure Portal or Studio")
    print("2. Click 'Create new deployment'")
    print("3. Select a model (e.g. gpt-4, gpt-35-turbo)")
    print("4. Enter a deployment name (e.g. a simple name like 'gpt4')")
    print("5. Use that name after creation\n")
    
    print("="*80)
    print("📝 After you find the deployment name, update the .env file:")
    print("="*80 + "\n")
    print("AZURE_OPENAI_DEPLOYMENT=your-actual-deployment-name\n")
    print("Then rerun the test:")
    print("  source readme/bin/activate")
    print("  python test_azure_openai.py\n")
    
    print("="*80)
    print("\n💬 Common deployment name examples:")
    print("  - gpt4")
    print("  - gpt-4")
    print("  - gpt-35-turbo")
    print("  - my-gpt4-deployment")
    print("  - gpt-4-32k\n")
    
    print("⚠️  Note: Deployment names are case-sensitive!\n")
    
    return True


if __name__ == "__main__":
    diagnose_azure_config()




