"""
Orchestrator: Coordinates the entire README generation workflow
(Ablation: Validator removed — single-pass, no iterative feedback)
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from config import Config
from utils import clone_repo, save_json, load_json
from code_analyzer import CodeAnalyzer
from material_collector import MaterialCollector
from llm_client import LLMClient
from agent_reader import AgentReader
from agent_analyzer import AgentAnalyzer
from agent_retriever import AgentRetriever, extract_links_from_text
from template_spec import TEMPLATE_SPEC
from logger import get_logger
from execution_analyzer import ExecutionOrderAnalyzer, format_for_analyzer

console = Console()
logger = get_logger("orchestrator")


class Orchestrator:
    """Orchestrator for README generation workflow (Validator removed, single-pass)"""
    
    def __init__(self, repo_url: str, ref: str = None, github_token: Optional[str] = None,
                 enable_external_fetch: bool = True, max_rounds: int = 5):
        logger.info("Initializing orchestrator (ablation: no Validator)")
        self.repo_url = repo_url
        self.ref = ref or Config.DEFAULT_REF
        self.github_token = github_token or Config.GITHUB_TOKEN
        self.enable_external_fetch = enable_external_fetch
        self.max_rounds = max_rounds
        
        logger.info(f"Config - Repo: {self.repo_url}, Branch: {self.ref}, Max rounds: {self.max_rounds}")
        
        self.repo_path: Optional[Path] = None
        
        self.project_name = self._extract_project_name(repo_url)
        self.output_dir = Path(Config.OUTPUT_DIR) / self.project_name
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Project name: {self.project_name}")
        logger.info(f"Output directory: {self.output_dir}")
        
        logger.info(f"Initializing LLM client (provider: {Config.LLM_PROVIDER})")
        self.llm_client = LLMClient()
        self.reader = AgentReader(self.llm_client)
        self.analyzer = AgentAnalyzer(self.llm_client)
        self.retriever = AgentRetriever(self.llm_client)
        logger.info("Agents initialized (Reader, Analyzer, Retriever) — Validator skipped")
        
        self.project_materials: Optional[Dict[str, Any]] = None
        self.code_analysis_results: Optional[Dict[str, Any]] = None
        self.execution_order_info: str = ""
        self.external_research_results: Optional[Dict[str, Any]] = None
        self.evidence_map: list = []
        self.facts_store: Dict[str, Any] = {}
    
    def run(self) -> Dict[str, Any]:
        """Execute the complete workflow (single-pass, no Validator feedback)"""
        logger.info("Starting README generation workflow (ablation: no Validator)")
        console.print("[bold green]Starting README generation workflow (no Validator)[/bold green]")
        
        logger.info("Entering preprocessing phase")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task1 = progress.add_task("Cloning repository...", total=None)
            self._preprocess()
            progress.update(task1, completed=True)
        logger.info("Preprocessing phase completed")
        
        # Single pass: Reader → Analyzer → done (no Validator to iterate)
        console.print(f"\n[bold cyan]=== Single Pass (no Validator) ===[/bold cyan]")
        
        # Reader: Generate draft
        logger.info("Reader: Generating initial README")
        console.print("[yellow]Reader: Generating initial README...[/yellow]")
        draft_result = self.reader.generate_draft(
            project_materials=self._get_project_materials_summary(),
            previous_review_report=None,
            previous_readme=None
        )
        self._save_round_output(1, "draft", draft_result)
        logger.info(f"Reader: Draft generated, contains {len(draft_result.get('gap_list', []))} items to complete")
        
        # Analyzer: Complete draft
        logger.info("Analyzer: Starting content completion")
        console.print("[yellow]Analyzer: Completing content...[/yellow]")
        complete_result = self.analyzer.analyze(
            draft_readme=draft_result["draft_readme_markdown"],
            gap_list=draft_result.get("gap_list", []),
            code_analysis_results=self.code_analysis_results,
            project_materials=self._get_project_materials_summary(),
            execution_order_info=self.execution_order_info
        )
        logger.info("Analyzer: Content completion finished")
        
        # Merge evidence map
        self._merge_evidence_map(draft_result.get("evidence_map", []))
        self._merge_evidence_map(complete_result.get("evidence_map_delta", []))
        logger.debug(f"Current evidence map contains {len(self.evidence_map)} items")
        
        self._save_round_output(1, "readme", complete_result)
        
        final_readme = complete_result["updated_readme_markdown"]
        
        console.print("[green]Single pass completed[/green]")
        
        # Save final result
        if final_readme:
            logger.info("Saving final README")
            self._save_final_output(final_readme)
        else:
            logger.warning("No final README generated")
        
        logger.info("README generation workflow completed")
        return {
            "success": True,
            "final_readme": final_readme,
            "output_dir": str(self.output_dir)
        }
    
    def _preprocess(self):
        """Preprocessing phase"""
        logger.info(f"Starting repository clone: {self.repo_url} (ref: {self.ref})")
        self.repo_path = clone_repo(self.repo_url, self.ref, "temp_repo")
        logger.info(f"Repository cloned to: {self.repo_path}")
        console.print(f"[green]✓ Repository cloned to: {self.repo_path}[/green]")
        
        logger.info("Starting material collection")
        console.print("[yellow]Collecting project materials...[/yellow]")
        collector = MaterialCollector(self.repo_path, self.enable_external_fetch)
        self.project_materials = collector.collect()
        save_json(self.project_materials, self.output_dir / "project_materials.json")
        logger.info(f"Material collection completed - collected {len(self.project_materials)} items")
        console.print("[green]✓ Material collection completed[/green]")
        
        logger.info("Starting code analysis")
        console.print("[yellow]Analyzing code...[/yellow]")
        analyzer = CodeAnalyzer(self.repo_path)
        self.code_analysis_results = analyzer.analyze()
        save_json(self.code_analysis_results, self.output_dir / Config.CODE_ANALYSIS_FILE)
        logger.info("Code analysis completed")
        console.print("[green]✓ Code analysis completed[/green]")
        
        logger.info("Starting execution order analysis")
        console.print("[yellow]Analyzing execution order...[/yellow]")
        try:
            exec_analyzer = ExecutionOrderAnalyzer(self.repo_path)
            exec_result = exec_analyzer.analyze()
            self.execution_order_info = format_for_analyzer(exec_result)
            save_json(exec_result.to_dict(), self.output_dir / "execution_order.json")
            if self.execution_order_info:
                logger.info(f"Found {len(exec_result.entry_points)} entry points, execution order suggestion generated")
                console.print(f"[green]✓ Execution order analysis completed ({len(exec_result.entry_points)} entry points)[/green]")
            else:
                logger.info("Single entry or no entry project, skipping execution order analysis")
                console.print("[green]✓ Execution order analysis completed (single entry project)[/green]")
        except Exception as e:
            logger.warning(f"Execution order analysis failed: {e}")
            console.print("[yellow]⚠ Execution order analysis skipped[/yellow]")
            self.execution_order_info = ""
        
        if self.enable_external_fetch:
            logger.info("Retriever: Starting external link research")
            console.print("[yellow]Retriever: Researching external links...[/yellow]")
            try:
                self._run_retriever_research()
                console.print("[green]✓ Retriever: External research completed[/green]")
            except Exception as e:
                logger.warning(f"Retriever research failed: {e}")
                console.print("[yellow]⚠ Retriever: External research skipped[/yellow]")
                self.external_research_results = None
        
        logger.info("Initializing facts_store")
        self.facts_store = {
            "repo_url": self.repo_url,
            "ref": self.ref,
            "project_materials": self.project_materials,
            "code_analysis_results": self.code_analysis_results,
            "external_research_results": self.external_research_results
        }
        save_json(self.facts_store, self.output_dir / Config.FACTS_STORE_FILE)
        logger.info("facts_store saved")
    
    def _get_project_materials_summary(self) -> str:
        """Get project materials summary (including code analysis and Retriever research)."""
        collector = MaterialCollector(self.repo_path, self.enable_external_fetch)
        collector.materials = self.project_materials
        summary = collector.get_summary(code_analysis=self.code_analysis_results)
        
        retriever_summary = self._get_retriever_summary()
        if retriever_summary:
            summary += retriever_summary
        
        return summary
    
    def _merge_evidence_map(self, new_evidence: list):
        """Merge evidence map"""
        existing_ids = {e.get("evidence_id") for e in self.evidence_map if "evidence_id" in e}
        for evidence in new_evidence:
            if evidence.get("evidence_id") not in existing_ids:
                self.evidence_map.append(evidence)
    
    def _save_round_output(self, round_num: int, output_type: str, data: Dict[str, Any]):
        """Save each round's output"""
        if output_type == "draft":
            dir_path = self.output_dir / "drafts"
            dir_path.mkdir(parents=True, exist_ok=True)
            file_path = dir_path / f"round_{round_num}.md"
            if "draft_readme_markdown" in data:
                file_path.write_text(data["draft_readme_markdown"], encoding='utf-8')
            json_path = dir_path / f"round_{round_num}_full.json"
            save_json(data, json_path)
        
        elif output_type == "readme":
            dir_path = self.output_dir / "drafts"
            dir_path.mkdir(parents=True, exist_ok=True)
            file_path = dir_path / f"round_{round_num}_updated.md"
            if "updated_readme_markdown" in data:
                file_path.write_text(data["updated_readme_markdown"], encoding='utf-8')
    
    def _save_final_output(self, readme_content: str):
        """Save final output"""
        readme_path = self.output_dir / Config.GENERATED_README_FILE
        readme_path.write_text(readme_content, encoding='utf-8')
        console.print(f"[bold green]✓ Final README saved to: {readme_path}[/bold green]")
        
        self.facts_store["final_readme"] = readme_content
        self.facts_store["evidence_map"] = self.evidence_map
        save_json(self.facts_store, self.output_dir / Config.FACTS_STORE_FILE)
    
    def _extract_project_name(self, repo_url: str) -> str:
        """Extract project name from GitHub URL"""
        url = repo_url.rstrip('/')
        if url.endswith('.git'):
            url = url[:-4]
        
        parts = url.split('/')
        if len(parts) >= 2:
            owner = parts[-2]
            repo = parts[-1]
            return f"{owner}_{repo}"
        
        from datetime import datetime
        return f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _run_retriever_research(self):
        """Retriever: proactively fetch and analyze external links (preprocess)."""
        links_to_research = []
        
        readme_content = self.project_materials.get("readme", {}).get("content", "")
        if readme_content:
            extracted_links = extract_links_from_text(readme_content)
            links_to_research.extend(extracted_links)
            logger.info(f"Retriever: Extracted {len(extracted_links)} links from README")
        
        for doc in self.project_materials.get("documentation", []):
            doc_content = doc.get("content", "")
            if doc_content:
                doc_links = extract_links_from_text(doc_content)
                links_to_research.extend(doc_links)
        
        for guide in self.project_materials.get("install_guides", []):
            guide_content = guide.get("content", "")
            if guide_content:
                guide_links = extract_links_from_text(guide_content)
                links_to_research.extend(guide_links)
        
        seen_urls = set()
        unique_links = []
        for link in links_to_research:
            url = link.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_links.append(link)
        
        if not unique_links:
            logger.info("Retriever: No external links found to research")
            self.external_research_results = {"links_analyzed": 0, "deployment_info": {}}
            return
        
        logger.info(f"Retriever: Found {len(unique_links)} unique external links to research")
        console.print(f"[cyan]Retriever: Analyzing {len(unique_links)} external links...[/cyan]")
        
        project_context = f"Project: {self.project_name}, URL: {self.repo_url}"
        
        max_links = 10
        if len(unique_links) > max_links:
            logger.info(f"Retriever: Limiting to {max_links} most relevant links")
            unique_links = unique_links[:max_links]
        
        self.external_research_results = self.retriever.fetch_and_analyze_links(
            links=unique_links,
            project_context=project_context
        )
        
        save_json(self.external_research_results, self.output_dir / "retriever_research.json")
        
        analyzed_count = len(self.external_research_results.get("analyzed_links", []))
        logger.info(f"Retriever: Successfully analyzed {analyzed_count} links")
        
        deployment_info = self.external_research_results.get("deployment_info", {})
        if deployment_info:
            self.project_materials["retriever_deployment_info"] = deployment_info
            logger.info("Retriever: Deployment information extracted and added to project materials")
    
    def _get_retriever_summary(self) -> str:
        """Summarize Retriever output for Reader/Analyzer context."""
        if not self.external_research_results:
            return ""
        
        deployment_info = self.external_research_results.get("deployment_info", {})
        if not deployment_info:
            return ""
        
        summary_parts = []
        summary_parts.append("\n## External Research Results (Retriever)\n")
        
        installation = deployment_info.get("installation", {})
        if installation:
            commands = installation.get("commands", [])
            if commands:
                summary_parts.append("### Installation Commands (from external docs)")
                for cmd in commands[:5]:
                    summary_parts.append(f"- `{cmd}`")
        
        configuration = deployment_info.get("configuration", {})
        if configuration:
            env_vars = configuration.get("environment_variables", [])
            if env_vars:
                summary_parts.append("\n### Environment Variables (from external docs)")
                for var in env_vars[:10]:
                    summary_parts.append(f"- {var}")
            
            ports = configuration.get("port_numbers", [])
            if ports:
                summary_parts.append(f"\n### Ports: {', '.join(map(str, ports))}")
        
        requirements = deployment_info.get("system_requirements", [])
        if requirements:
            summary_parts.append("\n### System Requirements (from external docs)")
            for req in requirements[:5]:
                summary_parts.append(f"- {req}")
        
        troubleshooting = deployment_info.get("troubleshooting", [])
        if troubleshooting:
            summary_parts.append("\n### Troubleshooting Tips")
            for tip in troubleshooting[:3]:
                summary_parts.append(f"- {tip}")
        
        if len(summary_parts) > 1:
            return "\n".join(summary_parts)
        return ""
