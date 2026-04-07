"""
Retriever: Fetches external docs and search results for deployment hints.

Responsible for:
1. Fetching and analyzing external link content
2. Performing web searches and providing clear answers
3. Filtering deployment-related information from raw content
"""

import re
import json
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from config import Config
from llm_client import LLMClient
from logger import get_logger

logger = get_logger("agent_retriever")


class WebFetcher:
    """Web page fetcher using requests + BeautifulSoup"""
    
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    def fetch(self, url: str) -> Dict[str, Any]:
        """Fetch web page content
        
        Returns:
            Dict containing:
            - url: The fetched URL
            - status: "success" or "failed"
            - title: Page title (if available)
            - content: Main text content
            - code_blocks: Extracted code blocks
            - links: Links found in the page
            - error: Error message (if failed)
        """
        logger.info(f"Fetching URL: {url}")
        
        try:
            response = requests.get(url, timeout=self.timeout, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            # Extract title
            title = soup.title.string if soup.title else ""
            
            # Extract main content
            content = soup.get_text(separator='\n', strip=True)
            
            # Extract code blocks
            code_blocks = []
            for code in soup.find_all(['code', 'pre']):
                code_text = code.get_text(strip=True)
                if code_text and len(code_text) > 10:  # Filter out tiny code snippets
                    code_blocks.append(code_text)
            
            # Extract links (for potential recursive fetching)
            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                link_text = a.get_text(strip=True)
                if href.startswith('http') and link_text:
                    links.append({
                        'url': href,
                        'text': link_text[:100]  # Limit link text length
                    })
            
            logger.info(f"Successfully fetched {url}: {len(content)} chars, {len(code_blocks)} code blocks")
            
            return {
                "url": url,
                "status": "success",
                "title": title,
                "content": content[:15000],  # Limit content length
                "code_blocks": code_blocks[:20],  # Limit code blocks
                "links": links[:30]  # Limit links
            }
            
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout fetching {url}")
            return {
                "url": url,
                "status": "failed",
                "error": "Request timeout"
            }
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            return {
                "url": url,
                "status": "failed",
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            return {
                "url": url,
                "status": "failed",
                "error": str(e)
            }


class WebSearcher:
    """Web search service supporting Tavily and DuckDuckGo"""
    
    def __init__(self, provider: str = None):
        self.provider = provider or Config.WEB_SEARCH_PROVIDER
        logger.info(f"Initializing WebSearcher with provider: {self.provider}")
        
        if self.provider == "tavily":
            if not Config.TAVILY_API_KEY:
                logger.warning("TAVILY_API_KEY not set, falling back to duckduckgo")
                self.provider = "duckduckgo"
            else:
                try:
                    from tavily import TavilyClient
                    self.tavily_client = TavilyClient(api_key=Config.TAVILY_API_KEY)
                    logger.info("Tavily client initialized successfully")
                except ImportError:
                    logger.warning("tavily-python not installed, falling back to duckduckgo")
                    self.provider = "duckduckgo"
        
        if self.provider == "duckduckgo":
            try:
                # Try new package name first (ddgs)
                try:
                    from ddgs import DDGS
                except ImportError:
                    # Fall back to old package name
                    from duckduckgo_search import DDGS
                self.ddgs_class = DDGS
                logger.info("DuckDuckGo search initialized")
            except ImportError:
                logger.error("DuckDuckGo search not installed")
                raise ImportError("Please install: pip install ddgs (or pip install duckduckgo-search)")
    
    def search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Perform web search
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            Dict containing:
            - query: The search query
            - status: "success" or "failed"
            - results: List of search results
            - error: Error message (if failed)
        """
        logger.info(f"Searching: {query} (provider: {self.provider})")
        
        try:
            if self.provider == "tavily":
                return self._search_tavily(query, max_results)
            else:
                return self._search_duckduckgo(query, max_results)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {
                "query": query,
                "status": "failed",
                "results": [],
                "error": str(e)
            }
    
    def _search_tavily(self, query: str, max_results: int) -> Dict[str, Any]:
        """Search using Tavily API"""
        response = self.tavily_client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results
        )
        
        results = []
        for item in response.get('results', []):
            results.append({
                'title': item.get('title', ''),
                'url': item.get('url', ''),
                'content': item.get('content', ''),
                'score': item.get('score', 0)
            })
        
        logger.info(f"Tavily search returned {len(results)} results")
        return {
            "query": query,
            "status": "success",
            "results": results,
            "provider": "tavily"
        }
    
    def _search_duckduckgo(self, query: str, max_results: int) -> Dict[str, Any]:
        """Search using DuckDuckGo"""
        results = []
        
        try:
            # Try new package name first (ddgs)
            try:
                from ddgs import DDGS
            except ImportError:
                # Fall back to old package name
                from duckduckgo_search import DDGS
            
            ddgs = DDGS()
            search_results = ddgs.text(query, max_results=max_results)
            
            if search_results:
                for r in search_results:
                    results.append({
                        'title': r.get('title', ''),
                        'url': r.get('href', r.get('link', '')),
                        'content': r.get('body', r.get('snippet', '')),
                        'score': 0  # DuckDuckGo doesn't provide relevance scores
                    })
        except Exception as e:
            logger.warning(f"DuckDuckGo search error: {e}")
        
        logger.info(f"DuckDuckGo search returned {len(results)} results")
        return {
            "query": query,
            "status": "success",
            "results": results,
            "provider": "duckduckgo"
        }


class AgentRetriever:
    """Retriever: Fetches external information and answers deployment questions."""
    
    MAX_TOTAL_FETCHES = 6

    def __init__(self, llm_client: LLMClient = None, max_depth: int = None):
        self.llm_client = llm_client or LLMClient()
        self.max_depth = min(max_depth or Config.AGENT4_MAX_DEPTH, 2)
        self.web_fetcher = WebFetcher()
        self.web_searcher = WebSearcher()
        
        logger.info(f"Retriever initialized with max_depth={self.max_depth}, max_fetches={self.MAX_TOTAL_FETCHES}")
    
    def fetch_and_analyze_links(self, links: List[Dict[str, str]], project_context: str = "") -> Dict[str, Any]:
        """Fetch multiple links and analyze them for deployment-related information
        
        This is called during preprocessing to gather all useful information from external links.
        
        Args:
            links: List of dicts with 'url' and 'description' keys
            project_context: Brief description of the project for context
            
        Returns:
            Dict containing:
            - analyzed_links: List of analyzed link results
            - deployment_info: Consolidated deployment-related information
        """
        logger.info(f"Analyzing {len(links)} links for deployment information")
        
        self._visited_urls: set = set()
        self._fetch_count: int = 0
        
        analyzed_links = []
        all_deployment_info = []
        
        for link_info in links:
            url = link_info.get('url', '')
            description = link_info.get('description', '')
            
            if not url:
                continue
            
            result = self.fetch_link_content(
                url=url,
                description=description,
                project_context=project_context,
                current_depth=0
            )
            
            analyzed_links.append(result)
            
            if result.get('deployment_info'):
                all_deployment_info.append({
                    'source_url': url,
                    'info': result['deployment_info']
                })
        
        # Consolidate all deployment information
        consolidated_info = self._consolidate_deployment_info(all_deployment_info, project_context)
        
        return {
            "analyzed_links": analyzed_links,
            "deployment_info": consolidated_info
        }
    
    def fetch_link_content(self, url: str, description: str = "", 
                          project_context: str = "", current_depth: int = 0) -> Dict[str, Any]:
        """Fetch a single link and extract deployment-related information
        
        Args:
            url: URL to fetch
            description: Description of what the link is about
            project_context: Context about the project
            current_depth: Current recursion depth
            
        Returns:
            Dict with extracted deployment information
        """
        logger.info(f"Fetching link (depth={current_depth}): {url}")
        
        # Normalise URL for dedup (strip trailing slash and fragment)
        norm = url.rstrip('/').split('#')[0]
        if not hasattr(self, '_visited_urls'):
            self._visited_urls = set()
        if not hasattr(self, '_fetch_count'):
            self._fetch_count = 0

        if norm in self._visited_urls:
            logger.info(f"Skipping already-visited URL: {url}")
            return {"url": url, "status": "already_visited", "deployment_info": None}
        self._visited_urls.add(norm)
        
        if self._fetch_count >= self.MAX_TOTAL_FETCHES:
            logger.warning(f"Global fetch limit ({self.MAX_TOTAL_FETCHES}) reached, skipping: {url}")
            return {"url": url, "status": "fetch_limit_reached", "deployment_info": None}
        
        if current_depth >= self.max_depth:
            logger.warning(f"Max depth {self.max_depth} reached, stopping recursion")
            return {"url": url, "status": "depth_limit_reached", "deployment_info": None}
        
        # Fetch the page
        fetch_result = self.web_fetcher.fetch(url)
        self._fetch_count += 1
        
        if fetch_result['status'] != 'success':
            return {
                "url": url,
                "status": "fetch_failed",
                "error": fetch_result.get('error'),
                "deployment_info": None
            }
        
        # Analyze content with LLM
        deployment_info = self._analyze_content_for_deployment(
            url=url,
            title=fetch_result.get('title', ''),
            content=fetch_result.get('content', ''),
            code_blocks=fetch_result.get('code_blocks', []),
            description=description,
            project_context=project_context
        )
        
        # Follow sub-links (capped by depth, per-page limit, and global fetch budget)
        sub_links_info = []
        if current_depth < self.max_depth - 1 and deployment_info.get('relevant_sub_links'):
            for sub_link in deployment_info['relevant_sub_links'][:2]:
                sub_result = self.fetch_link_content(
                    url=sub_link['url'],
                    description=sub_link.get('description', ''),
                    project_context=project_context,
                    current_depth=current_depth + 1
                )
                if sub_result.get('deployment_info'):
                    sub_links_info.append(sub_result)
        
        return {
            "url": url,
            "status": "success",
            "title": fetch_result.get('title'),
            "deployment_info": deployment_info.get('extracted_info'),
            "sub_links": sub_links_info
        }
    
    def search_and_answer(self, question: str, project_context: str = "", 
                         current_depth: int = 0) -> Dict[str, Any]:
        """Search the web for an answer to a specific question
        
        Args:
            question: The question to answer
            project_context: Context about the project
            current_depth: Current recursion depth
            
        Returns:
            Dict with the answer and supporting information
        """
        logger.info(f"Searching for answer (depth={current_depth}): {question}")
        
        # Check depth limit
        if current_depth >= self.max_depth:
            logger.warning(f"Max depth {self.max_depth} reached, returning current results")
            return {
                "question": question,
                "status": "depth_limit_reached",
                "answer": None
            }
        
        # Perform search
        search_result = self.web_searcher.search(question, max_results=5)
        
        if search_result['status'] != 'success' or not search_result['results']:
            return {
                "question": question,
                "status": "search_failed",
                "error": search_result.get('error', 'No results found'),
                "answer": None
            }
        
        # Analyze search results with LLM
        answer_result = self._analyze_search_results(
            question=question,
            search_results=search_result['results'],
            project_context=project_context
        )
        
        # If answer is not satisfactory and we have depth remaining, try refined search
        if not answer_result.get('is_satisfactory') and current_depth < self.max_depth - 1:
            refined_query = answer_result.get('suggested_refined_query')
            if refined_query and refined_query != question:
                logger.info(f"Answer not satisfactory, trying refined query: {refined_query}")
                return self.search_and_answer(
                    question=refined_query,
                    project_context=project_context,
                    current_depth=current_depth + 1
                )
        
        return {
            "question": question,
            "status": "success",
            "answer": answer_result.get('answer'),
            "confidence": answer_result.get('confidence', 'medium'),
            "sources": answer_result.get('sources', [])
        }
    
    def _analyze_content_for_deployment(self, url: str, title: str, content: str,
                                        code_blocks: List[str], description: str,
                                        project_context: str) -> Dict[str, Any]:
        """Use LLM to analyze page content and extract deployment-related information"""
        
        system_prompt = """You are Retriever, a research assistant that extracts deployment-related information from web pages.

Your task is to analyze the given web page content and extract ONLY information that is relevant to deploying/installing/configuring a software project.

Deployment-related information includes:
- Installation commands (pip install, npm install, apt-get, etc.)
- System requirements (OS, Python version, Node.js version, etc.)
- Configuration instructions (environment variables, config files)
- Build commands (make, cmake, mvn, gradle, etc.)
- Dependency information (required libraries, packages)
- Port numbers and network configuration
- Database setup instructions
- Docker/container instructions
- Common issues and troubleshooting
- Environment setup steps

Information to IGNORE:
- Feature descriptions
- Marketing content
- Project history
- Contributor information
- License details (unless affecting deployment)
- General documentation not related to deployment

You MUST output a valid JSON object."""

        # Prepare content summary
        content_summary = content[:8000] if content else ""
        code_blocks_text = "\n---\n".join(code_blocks[:10]) if code_blocks else "No code blocks found"
        
        user_prompt = f"""Analyze this web page and extract deployment-related information.

URL: {url}
Title: {title}
Link Description: {description}
Project Context: {project_context}

Page Content (truncated):
{content_summary}

Code Blocks Found:
{code_blocks_text}

Output a JSON object with:
{{
    "has_deployment_info": true/false,
    "extracted_info": {{
        "installation_commands": ["list of installation commands found"],
        "system_requirements": ["list of requirements"],
        "configuration_steps": ["list of config steps"],
        "environment_variables": ["list of env vars mentioned"],
        "port_numbers": ["list of ports mentioned"],
        "dependencies": ["list of dependencies"],
        "troubleshooting": ["common issues and solutions"],
        "other_deployment_info": "any other relevant deployment information"
    }},
    "relevant_sub_links": [
        {{"url": "full_url", "description": "why this link might have more deployment info"}}
    ],
    "summary": "1-2 sentence summary of deployment-related content found"
}}

If no deployment-related information is found, set has_deployment_info to false and extracted_info to null.
Only include relevant_sub_links if there are links that clearly point to installation/deployment documentation."""

        try:
            response = self.llm_client.call(system_prompt, user_prompt, json_mode=True)
            result = json.loads(response)
            return result
        except Exception as e:
            logger.error(f"Failed to analyze content: {e}")
            return {
                "has_deployment_info": False,
                "extracted_info": None,
                "error": str(e)
            }
    
    def _analyze_search_results(self, question: str, search_results: List[Dict],
                               project_context: str) -> Dict[str, Any]:
        """Use LLM to analyze search results and formulate an answer"""
        
        system_prompt = """You are Retriever, a research assistant that answers technical questions about software deployment.

Your task is to analyze search results and provide a clear, actionable answer to the given question.

Guidelines:
1. Focus on DEPLOYMENT-RELATED information (installation, configuration, setup)
2. Provide CONCRETE answers with specific commands, values, or steps
3. If the search results don't fully answer the question, indicate what's missing
4. Cite your sources
5. Be concise but complete

You MUST output a valid JSON object."""

        # Format search results
        results_text = ""
        for i, result in enumerate(search_results, 1):
            results_text += f"\n[{i}] {result.get('title', 'No title')}\n"
            results_text += f"URL: {result.get('url', '')}\n"
            results_text += f"Content: {result.get('content', '')[:500]}\n"
        
        user_prompt = f"""Answer this question based on the search results.

Question: {question}
Project Context: {project_context}

Search Results:
{results_text}

Output a JSON object with:
{{
    "answer": "Your clear, specific answer to the question. Include actual commands, values, or steps.",
    "is_satisfactory": true/false (whether you found a good answer),
    "confidence": "high/medium/low",
    "sources": ["list of URLs that supported your answer"],
    "suggested_refined_query": "if is_satisfactory is false, suggest a better search query"
}}

If you cannot find a satisfactory answer, still provide the best answer you can with available information, but set is_satisfactory to false."""

        try:
            response = self.llm_client.call(system_prompt, user_prompt, json_mode=True)
            result = json.loads(response)
            return result
        except Exception as e:
            logger.error(f"Failed to analyze search results: {e}")
            return {
                "answer": None,
                "is_satisfactory": False,
                "error": str(e)
            }
    
    def _consolidate_deployment_info(self, all_info: List[Dict], project_context: str) -> Dict[str, Any]:
        """Consolidate deployment information from multiple sources"""
        
        if not all_info:
            return {}
        
        system_prompt = """You are Retriever, consolidating deployment information from multiple sources.

Your task is to merge and deduplicate deployment-related information, creating a unified summary.

Guidelines:
1. Remove duplicates
2. Resolve conflicts (prefer more specific/recent information)
3. Organize by category
4. Keep only deployment-related information

You MUST output a valid JSON object."""

        info_text = json.dumps(all_info, ensure_ascii=False, indent=2)
        
        user_prompt = f"""Consolidate this deployment information from multiple sources.

Project Context: {project_context}

Information from various sources:
{info_text[:10000]}

Output a JSON object with consolidated deployment information:
{{
    "installation": {{
        "commands": ["consolidated installation commands"],
        "dependencies": ["all required dependencies"]
    }},
    "configuration": {{
        "environment_variables": ["all env vars with descriptions"],
        "config_files": ["config file information"],
        "port_numbers": ["all ports mentioned"]
    }},
    "system_requirements": ["consolidated requirements"],
    "troubleshooting": ["consolidated troubleshooting tips"],
    "summary": "Brief summary of deployment process based on all sources"
}}"""

        try:
            response = self.llm_client.call(system_prompt, user_prompt, json_mode=True)
            result = json.loads(response)
            return result
        except Exception as e:
            logger.error(f"Failed to consolidate info: {e}")
            return {"error": str(e)}


def extract_links_from_text(text: str) -> List[Dict[str, str]]:
    """Extract links with their descriptions from text (usually README content)
    
    Args:
        text: Text content (typically README)
        
    Returns:
        List of dicts with 'url' and 'description' keys
    """
    links = []
    
    # Match Markdown links: [description](url)
    markdown_pattern = r'\[([^\]]+)\]\((https?://[^\)]+)\)'
    for match in re.finditer(markdown_pattern, text):
        description = match.group(1)
        url = match.group(2)
        
        # Filter out common non-useful links
        if _is_useful_link(url, description):
            links.append({
                'url': url,
                'description': description
            })
    
    # Match plain URLs (without markdown)
    url_pattern = r'(?<!\()(https?://[^\s\)]+)(?!\))'
    for match in re.finditer(url_pattern, text):
        url = match.group(1)
        # Get surrounding context as description
        start = max(0, match.start() - 50)
        end = min(len(text), match.end() + 50)
        context = text[start:end].strip()
        
        if _is_useful_link(url, context):
            # Check if already added via markdown
            if not any(l['url'] == url for l in links):
                links.append({
                    'url': url,
                    'description': context[:100]
                })
    
    return links


def _is_useful_link(url: str, description: str) -> bool:
    """Determine if a link is potentially useful for deployment info"""
    url_lower = url.lower()
    desc_lower = description.lower()
    
    # Skip image links
    if any(ext in url_lower for ext in ['.png', '.jpg', '.gif', '.svg', '.ico']):
        return False
    
    # Skip badge links
    if any(badge in url_lower for badge in ['badge', 'shields.io', 'travis-ci', 'codecov']):
        return False
    
    # Prioritize documentation/installation links
    useful_keywords = ['doc', 'install', 'setup', 'guide', 'tutorial', 'getting-started',
                      'quickstart', 'configuration', 'deploy', 'requirement', 'wiki']
    
    if any(kw in url_lower or kw in desc_lower for kw in useful_keywords):
        return True
    
    # Include links to official documentation sites
    doc_domains = ['readthedocs', 'github.io', 'docs.', 'wiki.', 'doc.']
    if any(domain in url_lower for domain in doc_domains):
        return True
    
    # Include links from description context
    if any(kw in desc_lower for kw in ['documentation', 'instructions', 'how to', 'manual']):
        return True
    
    return False
