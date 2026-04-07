"""
Utility Functions
"""

import json
import re
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
import git
import requests
from bs4 import BeautifulSoup

# Filter BeautifulSoup XML warnings
# Since fetch_external_content() mainly handles HTML, HTML parser works for occasional XML too
try:
    from bs4 import XMLParsedAsHTMLWarning
    warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
except ImportError:
    pass  # Older versions of BeautifulSoup may not have this warning class


def clone_repo(repo_url: str, ref: str = "main", output_dir: str = "temp_repo") -> Path:
    """Clone GitHub repository to local
    
    Args:
        repo_url: GitHub repository URL
        ref: Branch/tag/commit
        output_dir: Output root directory (default: temp_repo)
    
    Returns:
        Path: Cloned repository path (temp_repo/owner_repo/)
    
    Note:
        For batch processing support, each project is cloned to a separate subdirectory:
        temp_repo/owner_repo1/
        temp_repo/owner_repo2/
    """
    # Extract project name from URL (owner_repo format)
    try:
        github_info = extract_github_info(repo_url)
        repo_name = github_info['full_name'].replace('/', '_')
    except Exception:
        # If parsing fails, use last part of URL as directory name
        repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
    
    # Build project-specific directory: temp_repo/owner_repo/
    base_dir = Path(output_dir)
    repo_path = base_dir / repo_name
    
    if repo_path.exists():
        # If exists, try to update
        try:
            repo = git.Repo(repo_path)
            repo.remote().fetch()
            repo.git.checkout(ref)
            return repo_path
        except:
            # If update fails, delete and re-clone
            import shutil
            shutil.rmtree(repo_path)
    
    # Ensure parent directory exists
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Clone repository to project-specific directory
    repo = git.Repo.clone_from(repo_url, repo_path)
    
    # Switch to specified branch/tag/commit
    try:
        repo.git.checkout(ref)
    except:
        # If ref doesn't exist, try as branch name
        try:
            repo.git.checkout("-b", ref)
        except:
            # If branch creation fails, keep current branch
            pass
    
    return repo_path


def extract_github_info(repo_url: str) -> Dict[str, str]:
    """Extract owner and repo name from GitHub URL"""
    parsed = urlparse(repo_url)
    path_parts = parsed.path.strip("/").split("/")
    if len(path_parts) >= 2:
        return {
            "owner": path_parts[0],
            "repo": path_parts[1],
            "full_name": f"{path_parts[0]}/{path_parts[1]}"
        }
    raise ValueError(f"Invalid GitHub URL: {repo_url}")


def fetch_external_content(url: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
    """Fetch external link content"""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract main content
        content = soup.get_text(separator='\n', strip=True)
        
        # Extract code blocks
        code_blocks = []
        for code in soup.find_all(['code', 'pre']):
            code_blocks.append(code.get_text())
        
        return {
            "url": url,
            "content": content[:5000],  # Limit length
            "code_blocks": code_blocks[:10],  # Limit count
            "status": "success"
        }
    except Exception as e:
        return {
            "url": url,
            "content": None,
            "error": str(e),
            "status": "failed"
        }


def find_files_by_pattern(repo_path: Path, patterns: List[str]) -> List[Path]:
    """Find files by pattern"""
    files = []
    for pattern in patterns:
        files.extend(repo_path.rglob(pattern))
    return files


def read_file_safe(file_path: Path, max_size: int = 100000) -> Optional[str]:
    """Safely read file (with size limit)"""
    try:
        if file_path.stat().st_size > max_size:
            return None
        return file_path.read_text(encoding='utf-8', errors='ignore')
    except:
        return None


def extract_code_blocks(text: str) -> List[str]:
    """Extract code blocks from text"""
    pattern = r'```[\s\S]*?```'
    matches = re.findall(pattern, text)
    return matches


def save_json(data: Any, file_path: Path):
    """Save JSON file"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(file_path: Path) -> Optional[Any]:
    """Load JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None


def _fix_malformed_quotes(json_str: str) -> str:
    """Fix malformed quotes (e.g., "key": \"value\" should be "key": "value")"""
    # Fix ": \" pattern -> ": "
    json_str = re.sub(r':\s*\\"', ': "', json_str)
    # Fix \" at string end (followed by comma or closing bracket)
    json_str = re.sub(r'\\"\s*([,}\]])', r'"\1', json_str)
    return json_str


def _truncate_to_last_complete_field(json_str: str) -> str:
    """Truncate to last complete field"""
    # Try to find last complete "key": value pair
    # Simplified: find last comma, then complete
    last_comma = json_str.rfind(',')
    if last_comma > 0:
        truncated = json_str[:last_comma]
        # Ensure proper closing
        if truncated.count('{') > truncated.count('}'):
            truncated += '}'
        if truncated.count('[') > truncated.count(']'):
            truncated += ']'
        return truncated
    return json_str


def parse_json_response(text: str) -> Dict[str, Any]:
    """Parse JSON from LLM responses (generalized, robust approach).

    Design principles:
    1. Adapt to multiple LLM response formats
    2. Progressive attempts, from strict to lenient
    3. Intelligently fix common issues
    4. Meaningful logs and error messages
    """
    from logger import get_logger
    logger = get_logger("utils")
    
    # Preprocess: strip leading and trailing whitespace
    text = text.strip()
    
    # Log raw response (for debugging)
    logger.debug(f"Attempting to parse JSON, response length: {len(text)} characters")
    
    # Empty content detection
    if not text or len(text) < 2:
        logger.error("Response content is empty or too short")
        raise ValueError("LLM returned empty response")
    
    # Strategy 1: Extract markdown JSON code block (```json ... ```)
    json_block = re.search(r'```json\s*([\s\S]*?)\s*```', text, re.IGNORECASE)
    if json_block:
        content = json_block.group(1).strip()
        if content:  # Ensure extracted content is not empty
            try:
                result = json.loads(content)
                logger.debug("✓ Successfully parsed from ```json code block")
                return result
            except json.JSONDecodeError as e:
                logger.warning(f"```json code block parse failed: {e}")
        else:
            logger.debug("Skipped empty ```json code block")
    
    # Strategy 2: Extract plain code block (``` ... ```), but check content
    code_block = re.search(r'```\s*([\s\S]*?)\s*```', text)
    if code_block:
        content = code_block.group(1).strip()
        # Only try to parse if content looks like JSON (starts with { or [)
        if content and (content.startswith('{') or content.startswith('[')):
            try:
                result = json.loads(content)
                logger.debug("✓ Successfully parsed from ``` code block")
                return result
            except json.JSONDecodeError as e:
                logger.debug(f"``` code block is not valid JSON: {e}")
        else:
            logger.debug(f"Skipped non-JSON ``` code block (content: {content[:50] if content else 'empty'}...)")
    
    # Strategy 3: Intelligent extraction of JSON object/array
    # Support object {...} and array [...]
    for pattern, json_type in [(r'\{[\s\S]*\}', 'object'), (r'\[[\s\S]*\]', 'array')]:
        json_match = re.search(pattern, text)
        if json_match:
            json_str = json_match.group().strip()
            
            # 3.1 Direct parse attempt
            try:
                result = json.loads(json_str)
                logger.debug(f"✓ Successfully parsed regex-extracted JSON {json_type}")
                return result
            except json.JSONDecodeError as e:
                logger.debug(f"Regex-extracted JSON {json_type} parse failed: {e}")
            
            # 3.2 Try intelligent fix strategies
            fixes = [
                ("fix_malformed_quotes", _fix_malformed_quotes),
                ("remove_trailing_comma", lambda s: re.sub(r',(\s*[}\]])', r'\1', s)),
                ("combined_fix", lambda s: re.sub(r',(\s*[}\]])', r'\1', _fix_malformed_quotes(s))),
                ("fix_incomplete_string", lambda s: s.rstrip() + ('"}' if s.count('"') % 2 == 1 else '}')),
                ("truncate_to_complete_field", _truncate_to_last_complete_field),
            ]
            
            for fix_name, fix_func in fixes:
                try:
                    json_str_fixed = fix_func(json_str)
                    result = json.loads(json_str_fixed)
                    logger.info(f"✓ Fix successful: {fix_name}")
                    return result
                except (json.JSONDecodeError, Exception) as e:
                    logger.debug(f"Fix strategy '{fix_name}' failed: {e}")
            
            # If object, don't continue trying array (avoid repetition)
            if json_type == 'object':
                break
    
    # Strategy 4: Direct parse entire response (may be pure JSON)
    try:
        result = json.loads(text)
        logger.debug("✓ Successfully parsed entire response directly (pure JSON)")
        return result
    except json.JSONDecodeError as e:
        logger.debug(f"Entire response is not pure JSON: {e}")
    
    # Strategy 5: Lenient mode - try to extract first complete JSON object
    # For handling cases where LLM added explanatory text before/after JSON
    try:
        # Find first { and try to progressively expand to find matching }
        start = text.find('{')
        if start != -1:
            depth = 0
            in_string = False
            escape = False
            
            for i in range(start, len(text)):
                char = text[i]
                
                # Handle characters inside string
                if escape:
                    escape = False
                    continue
                if char == '\\':
                    escape = True
                    continue
                if char == '"' and not escape:
                    in_string = not in_string
                    continue
                
                # Only count brackets outside strings
                if not in_string:
                    if char == '{':
                        depth += 1
                    elif char == '}':
                        depth -= 1
                        if depth == 0:
                            # Found complete JSON object
                            json_str = text[start:i+1]
                            try:
                                result = json.loads(json_str)
                                logger.info("✓ Lenient mode: successfully extracted first complete JSON object")
                                return result
                            except json.JSONDecodeError:
                                pass
                            break
    except Exception as e:
        logger.debug(f"Lenient mode parse failed: {e}")
    
    # All strategies failed, generate detailed diagnostic info
    import tempfile
    import datetime
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    debug_file = Path(tempfile.gettempdir()) / f"readme_agent_json_error_{timestamp}.txt"
    
    # Analyze response content
    has_json_markers = '{' in text or '[' in text
    has_code_blocks = '```' in text
    starts_with_json = text.lstrip().startswith(('{', '['))
    
    # Save complete response
    try:
        debug_file.write_text(text, encoding='utf-8')
        logger.error("=" * 80)
        logger.error("❌ JSON parse completely failed")
        logger.error("=" * 80)
        logger.error(f"Complete response saved to: {debug_file}")
        logger.error(f"Response length: {len(text)} characters")
        logger.error(f"Contains JSON markers ({{/[): {has_json_markers}")
        logger.error(f"Contains code blocks (```): {has_code_blocks}")
        logger.error(f"Starts with JSON: {starts_with_json}")
        logger.error("=" * 80)
        logger.error("First 2000 characters of response:")
        logger.error("-" * 80)
        logger.error(text[:2000])
        logger.error("=" * 80)
        
        # Provide possible reasons
        if not has_json_markers:
            logger.error("⚠️  Possible reason: Response has no JSON content at all")
        elif has_code_blocks and not starts_with_json:
            logger.error("⚠️  Possible reason: JSON may be wrapped in code blocks but format is incorrect")
        else:
            logger.error("⚠️  Possible reason: JSON format is severely wrong or incomplete")
            
    except Exception as e:
        logger.error(f"Cannot save debug file: {e}")
        logger.error(f"Response content: {text[:2000]}")
    
    raise ValueError(
        f"Cannot parse JSON from LLM response.\n"
        f"Response length: {len(text)} characters\n"
        f"Complete response saved to: {debug_file}\n"
        f"Please check if LLM output format is correct."
    )


