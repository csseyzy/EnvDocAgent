"""
LLM Client (Supports OpenAI, Azure OpenAI, AWS Bedrock, and Anthropic)
"""

import json
from typing import Optional, Dict, Any
from config import Config
import openai
from openai import AzureOpenAI
from anthropic import Anthropic
from logger import get_logger

logger = get_logger("llm_client")


class LLMClient:
    """LLM Client with token usage tracking"""
    
    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or Config.LLM_PROVIDER
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_calls = 0
        logger.info(f"Initializing LLM client - Provider: {self.provider}")
        
        if self.provider == "openai":
            if not Config.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set")
            # Create OpenAI client with optional custom base_url
            client_kwargs = {"api_key": Config.OPENAI_API_KEY}
            if Config.OPENAI_BASE_URL:
                client_kwargs["base_url"] = Config.OPENAI_BASE_URL
                logger.info(f"Using custom API endpoint: {Config.OPENAI_BASE_URL}")
            self.client = openai.OpenAI(**client_kwargs)
            self.model = Config.OPENAI_MODEL
            logger.info(f"OpenAI client initialized - Model: {self.model}")
        
        elif self.provider == "azure":
            if not Config.AZURE_OPENAI_API_KEY:
                raise ValueError("AZURE_OPENAI_API_KEY not set")
            if not Config.AZURE_OPENAI_ENDPOINT:
                raise ValueError("AZURE_OPENAI_ENDPOINT not set")
            if not Config.AZURE_OPENAI_DEPLOYMENT:
                raise ValueError("AZURE_OPENAI_DEPLOYMENT not set")
            
            # Create Azure OpenAI client
            self.client = AzureOpenAI(
                api_key=Config.AZURE_OPENAI_API_KEY,
                api_version=Config.AZURE_OPENAI_API_VERSION,
                azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
            )
            # Azure uses deployment name instead of model name
            self.model = Config.AZURE_OPENAI_DEPLOYMENT
            logger.info(f"Azure OpenAI client initialized")
            logger.info(f"  Endpoint: {Config.AZURE_OPENAI_ENDPOINT}")
            logger.info(f"  Deployment: {self.model}")
            logger.info(f"  API Version: {Config.AZURE_OPENAI_API_VERSION}")
        
        elif self.provider == "bedrock":
            if not Config.AWS_ACCESS_KEY_ID:
                raise ValueError("AWS_ACCESS_KEY_ID not set")
            if not Config.AWS_SECRET_ACCESS_KEY:
                raise ValueError("AWS_SECRET_ACCESS_KEY not set")
            
            try:
                import boto3
            except ImportError:
                raise ImportError("Please install boto3: pip install boto3")
            
            # Create Bedrock Runtime client
            self.client = boto3.client(
                service_name='bedrock-runtime',
                region_name=Config.AWS_REGION_NAME,
                aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
            )
            self.model = Config.AWS_BEDROCK_MODEL
            logger.info(f"AWS Bedrock client initialized")
            logger.info(f"  Region: {Config.AWS_REGION_NAME}")
            logger.info(f"  Model: {self.model}")
        
        elif self.provider == "anthropic":
            if not Config.ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY not set")
            self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
            self.model = Config.ANTHROPIC_MODEL
            logger.info(f"Anthropic client initialized - Model: {self.model}")
        
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def call(self, system_prompt: str, user_prompt: str, temperature: float = 0.3, json_mode: bool = True) -> str:
        """Call LLM
        
        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            temperature: Temperature parameter
            json_mode: Whether to enable JSON mode (default True)
        """
        logger.debug(f"Calling LLM - Provider: {self.provider}, Model: {self.model}, temperature: {temperature}, json_mode: {json_mode}")
        logger.debug(f"System prompt length: {len(system_prompt)}, User prompt length: {len(user_prompt)}")
        
        try:
            if self.provider in ["openai", "azure"]:
                # OpenAI and Azure OpenAI use the same API interface
                # Build base parameters
                call_params = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                }
                
                # Azure special handling: some deployments/models don't support custom temperature
                # Only add temperature for standard OpenAI or when explicitly supported
                if self.provider == "openai":
                    # Standard OpenAI API supports temperature
                    call_params["temperature"] = temperature
                elif self.provider == "azure":
                    # Azure OpenAI - some models don't support custom temperature
                    # Don't add temperature, use default
                    logger.debug("Using default temperature (some Azure deployments don't support custom values)")
                
                # Enable JSON mode (force LLM to output valid JSON)
                if json_mode:
                    try:
                        call_params["response_format"] = {"type": "json_object"}
                        logger.debug("JSON response mode enabled")
                    except Exception as e:
                        logger.warning(f"JSON mode setup failed (may not be supported): {e}")
                
                response = self.client.chat.completions.create(**call_params)
                result = response.choices[0].message.content
                self._record_usage(response)
                logger.debug(f"{self.provider.upper()} response length: {len(result)}")
                return result
            
            elif self.provider == "bedrock":
                # AWS Bedrock Claude API
                # Build request body for Claude on Bedrock
                request_body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 8192,
                    "system": system_prompt,
                    "messages": [
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": temperature
                }
                
                logger.debug(f"Calling Bedrock model: {self.model}")
                
                response = self.client.invoke_model(
                    modelId=self.model,
                    contentType="application/json",
                    accept="application/json",
                    body=json.dumps(request_body)
                )
                
                response_body = json.loads(response['body'].read())
                result = response_body['content'][0]['text']
                self._record_bedrock_usage(response_body)
                logger.debug(f"Bedrock response length: {len(result)}")
                return result
            
            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temperature
                )
                result = response.content[0].text
                self._record_anthropic_usage(response)
                logger.debug(f"Anthropic response length: {len(result)}")
                return result
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
    
    def _record_usage(self, response):
        """Record token usage from OpenAI / Azure response."""
        self.total_calls += 1
        usage = getattr(response, "usage", None)
        if usage:
            pt = getattr(usage, "prompt_tokens", 0) or 0
            ct = getattr(usage, "completion_tokens", 0) or 0
            self.total_prompt_tokens += pt
            self.total_completion_tokens += ct
            logger.debug(f"Token usage — prompt: {pt}, completion: {ct}")
    
    def _record_bedrock_usage(self, response_body: dict):
        """Record token usage from Bedrock response."""
        self.total_calls += 1
        usage = response_body.get("usage", {})
        pt = usage.get("input_tokens", 0)
        ct = usage.get("output_tokens", 0)
        self.total_prompt_tokens += pt
        self.total_completion_tokens += ct
        logger.debug(f"Token usage — prompt: {pt}, completion: {ct}")
    
    def _record_anthropic_usage(self, response):
        """Record token usage from Anthropic response."""
        self.total_calls += 1
        usage = getattr(response, "usage", None)
        if usage:
            pt = getattr(usage, "input_tokens", 0) or 0
            ct = getattr(usage, "output_tokens", 0) or 0
            self.total_prompt_tokens += pt
            self.total_completion_tokens += ct
            logger.debug(f"Token usage — prompt: {pt}, completion: {ct}")
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Return cumulative token usage and estimated cost."""
        total_tokens = self.total_prompt_tokens + self.total_completion_tokens
        
        input_price = Config.PRICE_PER_1K_INPUT_TOKENS
        output_price = Config.PRICE_PER_1K_OUTPUT_TOKENS
        
        input_cost = (self.total_prompt_tokens / 1000.0) * input_price
        output_cost = (self.total_completion_tokens / 1000.0) * output_price
        total_cost = input_cost + output_cost
        
        return {
            "total_calls": self.total_calls,
            "prompt_tokens": self.total_prompt_tokens,
            "completion_tokens": self.total_completion_tokens,
            "total_tokens": total_tokens,
            "input_cost_usd": round(input_cost, 4),
            "output_cost_usd": round(output_cost, 4),
            "total_cost_usd": round(total_cost, 4),
            "model": self.model,
            "provider": self.provider,
        }


