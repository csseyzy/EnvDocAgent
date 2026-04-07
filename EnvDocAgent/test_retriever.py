"""
Test Retriever (external fetch / search) functionality.
"""

from agent_retriever import (
    AgentRetriever,
    WebFetcher,
    WebSearcher,
    extract_links_from_text,
)


def test_web_fetcher():
    """Test web page fetching"""
    print("=" * 60)
    print("Testing WebFetcher")
    print("=" * 60)
    
    fetcher = WebFetcher()
    
    # Test with a simple page
    result = fetcher.fetch("https://httpbin.org/html")
    print(f"Status: {result['status']}")
    print(f"Content length: {len(result.get('content', ''))}")
    print(f"Code blocks: {len(result.get('code_blocks', []))}")
    print()


def test_web_searcher_duckduckgo():
    """Test DuckDuckGo search"""
    print("=" * 60)
    print("Testing WebSearcher (DuckDuckGo)")
    print("=" * 60)
    
    searcher = WebSearcher(provider="duckduckgo")
    
    result = searcher.search("Python Flask install requirements", max_results=3)
    print(f"Status: {result['status']}")
    print(f"Provider: {result.get('provider')}")
    print(f"Results count: {len(result.get('results', []))}")
    
    for i, r in enumerate(result.get('results', []), 1):
        print(f"  [{i}] {r.get('title', '')[:50]}...")
    print()


def test_extract_links():
    """Test link extraction from text"""
    print("=" * 60)
    print("Testing Link Extraction")
    print("=" * 60)
    
    sample_text = """
    # My Project
    
    Check out the [documentation](https://docs.example.com/install) for installation.
    
    Also see https://github.com/user/project/wiki for more info.
    
    ![Badge](https://shields.io/badge/test.svg) - this should be skipped
    
    For configuration, see [setup guide](https://example.com/setup-guide).
    """
    
    links = extract_links_from_text(sample_text)
    print(f"Found {len(links)} useful links:")
    for link in links:
        print(f"  - {link['url']}")
        print(f"    Description: {link['description'][:50]}...")
    print()


def test_retriever_search():
    """Test Retriever search and answer functionality"""
    print("=" * 60)
    print("Testing Retriever Search & Answer")
    print("=" * 60)
    
    try:
        retriever = AgentRetriever()
        
        result = retriever.search_and_answer(
            question="How to install Flask in Python?",
            project_context="A Python web application"
        )
        
        print(f"Status: {result['status']}")
        print(f"Confidence: {result.get('confidence', 'N/A')}")
        print(f"Answer: {result.get('answer', 'No answer')[:200]}...")
        print()
        
    except Exception as e:
        print(f"Error (may need LLM API key configured): {e}")
        print()


def test_retriever_fetch_link():
    """Test Retriever link fetching and analysis"""
    print("=" * 60)
    print("Testing Retriever Link Fetch & Analyze")
    print("=" * 60)
    
    try:
        retriever = AgentRetriever()
        
        result = retriever.fetch_link_content(
            url="https://flask.palletsprojects.com/en/stable/installation/",
            description="Flask installation documentation",
            project_context="A Python Flask web application"
        )
        
        print(f"Status: {result['status']}")
        print(f"Title: {result.get('title', 'N/A')}")
        
        if result.get('deployment_info'):
            print("Deployment Info Found:")
            info = result['deployment_info']
            if isinstance(info, dict):
                for key, value in info.items():
                    if value:
                        print(f"  - {key}: {str(value)[:100]}...")
        print()
        
    except Exception as e:
        print(f"Error (may need LLM API key configured): {e}")
        print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Retriever tests")
    print("=" * 60 + "\n")
    
    # Test basic components
    test_extract_links()
    test_web_fetcher()
    
    # Test search (doesn't require LLM)
    test_web_searcher_duckduckgo()
    
    # These tests require LLM API key
    print("\nThe following tests require a configured LLM API key:")
    test_retriever_search()
    test_retriever_fetch_link()
    
    print("\nTests completed!")
