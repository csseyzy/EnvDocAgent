"""
Configuration Management
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration Class"""
    
    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL: Optional[str] = os.getenv("OPENAI_BASE_URL")  # Custom API endpoint
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_API_KEY: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT: Optional[str] = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_DEPLOYMENT: Optional[str] = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    # Anthropic Configuration
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
    
    # AWS Bedrock Configuration
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION_NAME: str = os.getenv("AWS_REGION_NAME", "us-east-1")
    AWS_BEDROCK_MODEL: str = os.getenv("AWS_BEDROCK_MODEL", "us.anthropic.claude-sonnet-4-5-20250929-v1:0")
    
    # Default provider: OpenAI > Azure OpenAI > Bedrock > Anthropic
    LLM_PROVIDER: str = os.getenv(
        "LLM_PROVIDER", 
        "openai" if OPENAI_API_KEY else (
            "azure" if AZURE_OPENAI_API_KEY else (
                "bedrock" if AWS_ACCESS_KEY_ID else "anthropic"
            )
        )
    )
    
    # GitHub Configuration
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
    
    # Default Parameters
    DEFAULT_REF: str = os.getenv("DEFAULT_REF", "main")
    DEFAULT_MAX_ROUNDS: int = int(os.getenv("DEFAULT_MAX_ROUNDS", "5"))
    DEFAULT_ENABLE_EXTERNAL_FETCH: bool = os.getenv("DEFAULT_ENABLE_EXTERNAL_FETCH", "true").lower() == "true"
    
    # Output Directory
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "output")
    FACTS_STORE_FILE: str = "facts_store.json"
    CODE_ANALYSIS_FILE: str = "code_analysis_results.json"
    GENERATED_README_FILE: str = "README.generated.md"
    
    # Log Configuration
    LOG_DIR: str = os.getenv("LOG_DIR", "logs")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Score Threshold (minimum score to stop iteration)
    SCORE_THRESHOLD: int = int(os.getenv("SCORE_THRESHOLD", "97"))
    
    # Retriever (external fetch / search); env var name kept for compatibility
    AGENT4_MAX_DEPTH: int = int(os.getenv("AGENT4_MAX_DEPTH", "3"))  # Maximum self-call depth
    WEB_SEARCH_PROVIDER: str = os.getenv("WEB_SEARCH_PROVIDER", "duckduckgo")  # tavily or duckduckgo
    TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY")


