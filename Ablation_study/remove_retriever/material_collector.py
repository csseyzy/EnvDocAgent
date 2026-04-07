"""
Material collection module.
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from utils import read_file_safe, fetch_external_content, extract_code_blocks


class MaterialCollector:
    """Material collector."""
    
    def __init__(self, repo_path: Path, enable_external_fetch: bool = True):
        self.repo_path = repo_path
        self.enable_external_fetch = enable_external_fetch
        self.materials = {
            "readme": None,
            "docs": [],
            "install_guides": [],
            "deploy_guides": [],
            "contributing": None,
            "license": None,
            "config_files": [],
            "docker_files": [],
            "ci_workflows": [],
            "external_links": []
        }
    
    def collect(self) -> Dict[str, Any]:
        """Collect all materials."""
        self._collect_readme()
        self._collect_docs()
        self._collect_install_guides()
        self._collect_deploy_guides()
        self._collect_contributing()
        self._collect_license()
        self._collect_config_files()
        self._collect_docker_files()
        self._collect_ci_workflows()
        
        if self.enable_external_fetch:
            self._fetch_external_links()
        
        return self.materials
    
    def _collect_readme(self):
        """Collect README files."""
        readme_patterns = ["README.md", "README.rst", "README.txt", "readme.md"]
        for pattern in readme_patterns:
            readme_path = self.repo_path / pattern
            if readme_path.exists():
                content = read_file_safe(readme_path)
                if content:
                    self.materials["readme"] = {
                        "file": pattern,
                        "content": content,
                        "code_blocks": extract_code_blocks(content)
                    }
                    break
    
    def _collect_docs(self):
        """Collect documentation."""
        docs_dir = self.repo_path / "docs"
        if docs_dir.exists():
            for doc_file in docs_dir.rglob("*.md"):
                content = read_file_safe(doc_file)
                if content:
                    self.materials["docs"].append({
                        "file": str(doc_file.relative_to(self.repo_path)),
                        "content": content[:5000]  # Truncate length
                    })
    
    def _collect_install_guides(self):
        """Collect installation guides."""
        install_patterns = ["INSTALL*", "SETUP*", "QUICKSTART*"]
        for pattern in install_patterns:
            for file_path in self.repo_path.glob(pattern):
                if file_path.is_file():
                    content = read_file_safe(file_path)
                    if content:
                        self.materials["install_guides"].append({
                            "file": str(file_path.relative_to(self.repo_path)),
                            "content": content
                        })
    
    def _collect_deploy_guides(self):
        """Collect deployment guides."""
        deploy_patterns = ["DEPLOY*", "DEPLOYMENT*"]
        for pattern in deploy_patterns:
            for file_path in self.repo_path.glob(pattern):
                if file_path.is_file():
                    content = read_file_safe(file_path)
                    if content:
                        self.materials["deploy_guides"].append({
                            "file": str(file_path.relative_to(self.repo_path)),
                            "content": content
                        })
    
    def _collect_contributing(self):
        """Collect contributing guide."""
        contributing_path = self.repo_path / "CONTRIBUTING.md"
        if contributing_path.exists():
            content = read_file_safe(contributing_path)
            if content:
                self.materials["contributing"] = {
                    "file": "CONTRIBUTING.md",
                    "content": content
                }
    
    def _collect_license(self):
        """Collect license."""
        license_patterns = ["LICENSE*", "LICENCE*"]
        for pattern in license_patterns:
            for file_path in self.repo_path.glob(pattern):
                if file_path.is_file():
                    content = read_file_safe(file_path, max_size=5000)
                    if content:
                        # Try to detect license type
                        license_type = self._detect_license_type(content)
                        self.materials["license"] = {
                            "file": str(file_path.relative_to(self.repo_path)),
                            "type": license_type,
                            "content": content[:1000]  # Keep only the beginning
                        }
                        break
    
    def _detect_license_type(self, content: str) -> str:
        """Detect license type."""
        content_lower = content.lower()
        if "mit" in content_lower:
            return "MIT"
        elif "apache" in content_lower:
            return "Apache-2.0"
        elif "gpl" in content_lower:
            if "version 3" in content_lower or "v3" in content_lower:
                return "GPL-3.0"
            elif "version 2" in content_lower or "v2" in content_lower:
                return "GPL-2.0"
            return "GPL"
        elif "bsd" in content_lower:
            return "BSD"
        return "Unknown"
    
    def _collect_config_files(self):
        """Collect configuration files."""
        config_patterns = [".env.example", ".env.template", "config.example.*", 
                          "*.config.example", "config.yml", "config.yaml"]
        for pattern in config_patterns:
            for file_path in self.repo_path.rglob(pattern):
                if file_path.is_file():
                    content = read_file_safe(file_path)
                    if content:
                        self.materials["config_files"].append({
                            "file": str(file_path.relative_to(self.repo_path)),
                            "content": content
                        })
    
    def _collect_docker_files(self):
        """Collect Docker-related files."""
        docker_files = ["Dockerfile", "docker-compose.yml", "docker-compose.yaml", 
                       ".dockerignore"]
        for docker_file in docker_files:
            docker_path = self.repo_path / docker_file
            if docker_path.exists():
                content = read_file_safe(docker_path)
                if content:
                    self.materials["docker_files"].append({
                        "file": docker_file,
                        "content": content
                    })
    
    def _collect_ci_workflows(self):
        """Collect CI workflows."""
        workflows_path = self.repo_path / ".github" / "workflows"
        if workflows_path.exists():
            for workflow_file in workflows_path.glob("*.yml"):
                content = read_file_safe(workflow_file)
                if content:
                    self.materials["ci_workflows"].append({
                        "file": str(workflow_file.relative_to(self.repo_path)),
                        "content": content
                    })
    
    def _fetch_external_links(self):
        """Fetch external links."""
        # Extract links from README
        if self.materials["readme"]:
            links = self._extract_links(self.materials["readme"]["content"])
            for link in links:
                if self._is_external_link(link):
                    fetched = fetch_external_content(link)
                    if fetched:
                        self.materials["external_links"].append(fetched)
    
    def _extract_links(self, text: str) -> List[str]:
        """Extract links from text."""
        # Markdown link format: [text](url)
        markdown_links = re.findall(r'\[.*?\]\((.*?)\)', text)
        # Plain URLs
        url_pattern = r'https?://[^\s\)]+'
        urls = re.findall(url_pattern, text)
        return list(set(markdown_links + urls))
    
    def _is_external_link(self, url: str) -> bool:
        """Return True if URL is an external (http/https) link."""
        return url.startswith("http://") or url.startswith("https://")
    
    def get_summary(self, code_analysis: Optional[Dict[str, Any]] = None) -> str:
        """Build material summary (for the Agent), including code analysis results."""
        summary_parts = []
        
        if self.materials["readme"]:
            summary_parts.append(f"## README\n{self.materials['readme']['content'][:2000]}\n")
        
        if self.materials["install_guides"]:
            summary_parts.append("## Installation guides\n")
            for guide in self.materials["install_guides"]:
                summary_parts.append(f"### {guide['file']}\n{guide['content'][:1000]}\n")
        
        if self.materials["deploy_guides"]:
            summary_parts.append("## Deployment guides\n")
            for guide in self.materials["deploy_guides"]:
                summary_parts.append(f"### {guide['file']}\n{guide['content'][:1000]}\n")
        
        if self.materials["docker_files"]:
            summary_parts.append("## Docker files\n")
            for docker_file in self.materials["docker_files"]:
                summary_parts.append(f"### {docker_file['file']}\n```\n{docker_file['content'][:500]}\n```\n")
        
        if self.materials["external_links"]:
            summary_parts.append("## External link content\n")
            for link_data in self.materials["external_links"]:
                if link_data.get("status") == "success":
                    summary_parts.append(f"### {link_data['url']}\n{link_data.get('content', '')[:1000]}\n")
                    if link_data.get("code_blocks"):
                        summary_parts.append("Code blocks:\n")
                        for code in link_data["code_blocks"][:3]:
                            summary_parts.append(f"```\n{code[:200]}\n```\n")
        
        # Code analysis results (critical fix)
        if code_analysis:
            summary_parts.append("\n## Code analysis results\n")
            
            # 1. Dependency list (from manifest/config files)
            if code_analysis.get("dependencies"):
                summary_parts.append("### Dependencies (from config files)\n")
                deps_by_type = {}
                for dep in code_analysis["dependencies"]:
                    dep_type = dep.get("type", "runtime")
                    if dep_type not in deps_by_type:
                        deps_by_type[dep_type] = []
                    dep_info = f"- {dep['name']}"
                    if dep.get('version') and dep['version'] != 'unspecified':
                        dep_info += f" ({dep['version']})"
                    dep_info += f" - from {dep.get('source', 'unknown')}"
                    deps_by_type[dep_type].append(dep_info)
                
                for dep_type, deps in sorted(deps_by_type.items()):
                    summary_parts.append(f"\n**{dep_type} dependencies:**\n")
                    summary_parts.extend(deps[:30])  # Limit count
            
            # 2. Deep code analysis (from source content)
            if code_analysis.get("content_analysis"):
                summary_parts.append("\n### Deep code analysis (from source)\n")
                for analysis in code_analysis["content_analysis"][:15]:  # Limit number of files
                    file_info = []
                    file_info.append(f"\n**{analysis.get('file')}** ({analysis.get('language')}):")
                    
                    # imports/requires (dependencies in code)
                    if analysis.get("imports"):
                        imports = analysis["imports"][:15]
                        if isinstance(imports[0], dict):
                            import_names = [i.get('module', str(i)) for i in imports]
                        else:
                            import_names = imports
                        file_info.append(f"  - imports: {', '.join(import_names)}")
                    
                    # frameworks
                    if analysis.get("frameworks"):
                        file_info.append(f"  - frameworks: {', '.join(analysis['frameworks'])}")
                    
                    # env_vars (environment variables)
                    if analysis.get("env_vars"):
                        env_vars = []
                        for e in analysis['env_vars'][:10]:
                            if isinstance(e, dict):
                                env_vars.append(e.get('name', str(e)))
                            else:
                                env_vars.append(str(e))
                        file_info.append(f"  - env_vars: {', '.join(env_vars)}")
                    
                    # server_port (port number)
                    if analysis.get("server_port"):
                        file_info.append(f"  - server_port: {analysis['server_port']}")
                    
                    # cli_params (CLI arguments)
                    if analysis.get("cli_params"):
                        params = [p.get('name', str(p)) if isinstance(p, dict) else str(p) for p in analysis['cli_params'][:5]]
                        file_info.append(f"  - cli_params: {', '.join(params)}")
                    
                    # Only append files that have more than the header line
                    if len(file_info) > 1:
                        summary_parts.extend(file_info)
            
            # 3. Language clues
            if code_analysis.get("language_clues"):
                summary_parts.append("\n### Detected programming languages\n")
                for clue in code_analysis["language_clues"][:10]:
                    summary_parts.append(f"- {clue.get('language', 'unknown')}: {clue.get('file', 'unknown')}")
        
        return "\n".join(summary_parts)


