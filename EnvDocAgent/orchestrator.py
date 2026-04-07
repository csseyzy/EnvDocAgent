"""
Orchestrator: Coordinates the entire README generation workflow
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from config import Config
from utils import clone_repo, save_json, load_json
from code_analyzer import CodeAnalyzer
from material_collector import MaterialCollector
from llm_client import LLMClient
from agent_validator import AgentValidator
from agent_reader import AgentReader
from agent_analyzer import AgentAnalyzer
from agent_retriever import AgentRetriever, extract_links_from_text
from template_spec import TEMPLATE_SPEC
from logger import get_logger
from execution_analyzer import ExecutionOrderAnalyzer, format_for_analyzer

console = Console()
logger = get_logger("orchestrator")


class Orchestrator:
    """Orchestrator for README generation workflow"""
    
    def __init__(self, repo_url: str, ref: str = None, github_token: Optional[str] = None,
                 enable_external_fetch: bool = True, max_rounds: int = 5):
        logger.info("Initializing orchestrator")
        self.repo_url = repo_url
        self.ref = ref or Config.DEFAULT_REF
        self.github_token = github_token or Config.GITHUB_TOKEN
        self.enable_external_fetch = enable_external_fetch
        self.max_rounds = max_rounds
        
        logger.info(f"Config - Repo: {self.repo_url}, Branch: {self.ref}, Max rounds: {self.max_rounds}")
        
        self.repo_path: Optional[Path] = None
        
        # Extract project name and create project-specific output directory
        self.project_name = self._extract_project_name(repo_url)
        self.output_dir = Path(Config.OUTPUT_DIR) / self.project_name
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Project name: {self.project_name}")
        logger.info(f"Output directory: {self.output_dir}")
        
        # Initialize LLM client and Agents
        logger.info(f"Initializing LLM client (provider: {Config.LLM_PROVIDER})")
        self.llm_client = LLMClient()
        self.validator = AgentValidator(self.llm_client)
        self.reader = AgentReader(self.llm_client)
        self.analyzer = AgentAnalyzer(self.llm_client)
        self.retriever = AgentRetriever(self.llm_client)
        logger.info("All agents initialized (Validator, Reader, Analyzer, Retriever)")
        
        # Store intermediate results
        self.project_materials: Optional[Dict[str, Any]] = None
        self.code_analysis_results: Optional[Dict[str, Any]] = None
        self.execution_order_info: str = ""  # Multi-entry execution order analysis info
        self.external_research_results: Optional[Dict[str, Any]] = None  # Retriever results
        self.evidence_map: list = []
        self.facts_store: Dict[str, Any] = {}
    
    def run(self) -> Dict[str, Any]:
        """Execute the complete workflow"""
        run_start_time = time.time()
        logger.info("Starting README generation workflow")
        console.print("[bold green]Starting README generation workflow[/bold green]")
        
        # Preprocessing phase
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
        
        # Iterative execution
        final_readme = None
        previous_readme = None  # Save previous round's README
        for round_num in range(1, self.max_rounds + 1):
            logger.info(f"Starting round {round_num}/{self.max_rounds}")
            console.print(f"\n[bold cyan]=== Round {round_num} ===[/bold cyan]")
            
            # Reader: Generate/optimize draft
            if round_num == 1:
                logger.info("Reader: Generating initial README")
                console.print("[yellow]Reader: Generating initial README...[/yellow]")
            else:
                logger.info(f"Reader: Optimizing README based on round {round_num-1}")
                console.print(f"[yellow]Reader: Optimizing README (based on round {round_num-1})...[/yellow]")
            
            previous_review = self._get_previous_review(round_num - 1)
            draft_result = self.reader.generate_draft(
                project_materials=self._get_project_materials_summary(),
                previous_review_report=previous_review,
                previous_readme=previous_readme  # Pass previous round's README
            )
            self._save_round_output(round_num, "draft", draft_result)
            logger.info(f"Reader: Draft {'generated' if round_num == 1 else 'optimized'}, contains {len(draft_result.get('gap_list', []))} items to complete")
            
            # Analyzer: Complete draft
            logger.info("Analyzer: Starting content completion")
            console.print("[yellow]Analyzer: Completing content...[/yellow]")
            complete_result = self.analyzer.analyze(
                draft_readme=draft_result["draft_readme_markdown"],
                gap_list=draft_result.get("gap_list", []),
                code_analysis_results=self.code_analysis_results,
                project_materials=self._get_project_materials_summary(),
                execution_order_info=self.execution_order_info  # Multi-entry execution order info
            )
            logger.info("Analyzer: Content completion finished")
            
            # Merge evidence map
            self._merge_evidence_map(draft_result.get("evidence_map", []))
            self._merge_evidence_map(complete_result.get("evidence_map_delta", []))
            logger.debug(f"Current evidence map contains {len(self.evidence_map)} items")
            
            # Validator: Review / score
            logger.info("Validator: Starting quality review")
            console.print("[yellow]Validator: Reviewing quality...[/yellow]")
            review_result = self.validator.validate(
                readme_to_review=complete_result["updated_readme_markdown"],
                evidence_map=self.evidence_map
            )
            self._save_round_output(round_num, "review", review_result)
            self._save_round_output(round_num, "readme", complete_result)
            
            final_readme = complete_result["updated_readme_markdown"]
            previous_readme = final_readme  # Save current README for next round
            
            overall_score = review_result.get("overall_score", 0)
            issues_count = len(review_result.get("issues", []))
            
            logger.info(f"Validator: Review completed - Score: {overall_score}/100, Issues found: {issues_count}")
            console.print(f"[green]Round score: {overall_score}/100[/green]")
            
            if issues_count > 0:
                logger.info(f"Next round will fix {issues_count} issues based on current README")
            else:
                logger.info("No issues in this round, may end iteration")
            
            # Check stop conditions
            should_stop = review_result.get("stop_recommendation", {}).get("should_stop", False)
            has_blocker = any(issue.get("severity") == "blocker" 
                            for issue in review_result.get("issues", []))
            has_major = any(issue.get("severity") == "major" 
                          for issue in review_result.get("issues", []))
            
            logger.info(f"Stop condition check - should_stop: {should_stop}, blocker: {has_blocker}, major: {has_major}")
            
            if should_stop or (overall_score >= Config.SCORE_THRESHOLD and not has_blocker and not has_major):
                logger.info(f"Stop condition met, ending iteration at round {round_num}")
                console.print("[bold green]✓ Stop condition met, ending iteration[/bold green]")
                break
        
        # Save final result
        if final_readme:
            logger.info("Saving final README")
            self._save_final_output(final_readme)
        else:
            logger.warning("No final README generated")
        
        elapsed_seconds = time.time() - run_start_time
        usage = self.llm_client.get_usage_summary()
        
        self._print_cost_summary(elapsed_seconds, usage)
        
        logger.info("README generation workflow completed")
        return {
            "success": True,
            "final_readme": final_readme,
            "output_dir": str(self.output_dir),
            "elapsed_seconds": round(elapsed_seconds, 2),
            "api_usage": usage,
        }
    
    def _preprocess(self):
        """Preprocessing phase"""
        # Clone repository
        logger.info(f"Starting repository clone: {self.repo_url} (ref: {self.ref})")
        self.repo_path = clone_repo(self.repo_url, self.ref, "temp_repo")
        logger.info(f"Repository cloned to: {self.repo_path}")
        console.print(f"[green]✓ Repository cloned to: {self.repo_path}[/green]")
        
        # Collect materials
        logger.info("Starting material collection")
        console.print("[yellow]Collecting project materials...[/yellow]")
        collector = MaterialCollector(self.repo_path, self.enable_external_fetch)
        self.project_materials = collector.collect()
        save_json(self.project_materials, self.output_dir / "project_materials.json")
        logger.info(f"Material collection completed - collected {len(self.project_materials)} items")
        console.print("[green]✓ Material collection completed[/green]")
        
        # Code analysis
        logger.info("Starting code analysis")
        console.print("[yellow]Analyzing code...[/yellow]")
        analyzer = CodeAnalyzer(self.repo_path)
        self.code_analysis_results = analyzer.analyze()
        save_json(self.code_analysis_results, self.output_dir / Config.CODE_ANALYSIS_FILE)
        logger.info("Code analysis completed")
        console.print("[green]✓ Code analysis completed[/green]")
        
        # Execution order analysis (multi-entry programs)
        logger.info("Starting execution order analysis")
        console.print("[yellow]Analyzing execution order...[/yellow]")
        try:
            exec_analyzer = ExecutionOrderAnalyzer(self.repo_path)
            exec_result = exec_analyzer.analyze()
            self.execution_order_info = format_for_analyzer(exec_result)
            # Save analysis results
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
        
        # Retriever: External link research (proactive phase)
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
        
        # Initialize facts_store
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
        # Key fix: Pass code analysis results including dependencies and deep analysis
        summary = collector.get_summary(code_analysis=self.code_analysis_results)
        
        # Retriever research results
        retriever_summary = self._get_retriever_summary()
        if retriever_summary:
            summary += retriever_summary
        
        return summary
    
    def _get_previous_review(self, round_num: int) -> Optional[str]:
        """Get previous round's review report"""
        if round_num == 0:
            return None
        
        review_file = self.output_dir / "review_reports" / f"round_{round_num}.json"
        if review_file.exists():
            review_data = load_json(review_file)
            if review_data:
                return json.dumps(review_data, ensure_ascii=False, indent=2)
        return None
    
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
            # Also save complete JSON
            json_path = dir_path / f"round_{round_num}_full.json"
            save_json(data, json_path)
        
        elif output_type == "review":
            dir_path = self.output_dir / "review_reports"
            dir_path.mkdir(parents=True, exist_ok=True)
            file_path = dir_path / f"round_{round_num}.json"
            save_json(data, file_path)
        
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
        
        # Update facts_store
        self.facts_store["final_readme"] = readme_content
        self.facts_store["evidence_map"] = self.evidence_map
        save_json(self.facts_store, self.output_dir / Config.FACTS_STORE_FILE)
    
    def _print_cost_summary(self, elapsed_seconds: float, usage: Dict[str, Any]):
        """Print elapsed time and API cost summary."""
        minutes, secs = divmod(elapsed_seconds, 60)
        
        console.print("\n" + "=" * 60)
        console.print("[bold cyan]  Run Summary[/bold cyan]")
        console.print("=" * 60)
        console.print(f"  Model:              {usage['model']} ({usage['provider']})")
        console.print(f"  Total LLM calls:    {usage['total_calls']}")
        console.print(f"  Prompt tokens:      {usage['prompt_tokens']:,}")
        console.print(f"  Completion tokens:  {usage['completion_tokens']:,}")
        console.print(f"  Total tokens:       {usage['total_tokens']:,}")
        console.print(f"  Input cost:         ${usage['input_cost_usd']:.4f}")
        console.print(f"  Output cost:        ${usage['output_cost_usd']:.4f}")
        console.print(f"  [bold]Total cost:         ${usage['total_cost_usd']:.4f}[/bold]")
        console.print(f"  Elapsed time:       {int(minutes)}m {secs:.1f}s ({elapsed_seconds:.1f}s)")
        console.print("=" * 60)
        
        logger.info(f"Run summary — time: {elapsed_seconds:.1f}s, calls: {usage['total_calls']}, "
                     f"tokens: {usage['total_tokens']:,}, cost: ${usage['total_cost_usd']:.4f}")
        
        save_json({"elapsed_seconds": round(elapsed_seconds, 2), **usage},
                  self.output_dir / "run_cost_summary.json")
    
    def _extract_project_name(self, repo_url: str) -> str:
        """Extract project name from GitHub URL
        
        Args:
            repo_url: GitHub repository URL, e.g. https://github.com/owner/repo
            
        Returns:
            Project name in the form owner_repo
        """
        # Strip trailing / and .git
        url = repo_url.rstrip('/')
        if url.endswith('.git'):
            url = url[:-4]
        
        # Parse URL to get owner and repo
        parts = url.split('/')
        if len(parts) >= 2:
            owner = parts[-2]
            repo = parts[-1]
            return f"{owner}_{repo}"
        
        # If parsing fails, use timestamp as fallback
        from datetime import datetime
        return f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _run_retriever_research(self):
        """Retriever: proactively fetch and analyze external links (preprocess).

        Extracts links from collected materials; Retriever analyzes them for deployment hints.
        """
        # 1. Extract external links from project materials
        links_to_research = []
        
        # Extract links from README content
        readme_content = self.project_materials.get("readme", {}).get("content", "")
        if readme_content:
            extracted_links = extract_links_from_text(readme_content)
            links_to_research.extend(extracted_links)
            logger.info(f"Retriever: Extracted {len(extracted_links)} links from README")
        
        # Extract links from other documentation
        for doc in self.project_materials.get("documentation", []):
            doc_content = doc.get("content", "")
            if doc_content:
                doc_links = extract_links_from_text(doc_content)
                links_to_research.extend(doc_links)
        
        # Extract links from install guides
        for guide in self.project_materials.get("install_guides", []):
            guide_content = guide.get("content", "")
            if guide_content:
                guide_links = extract_links_from_text(guide_content)
                links_to_research.extend(guide_links)
        
        # Deduplicate
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
        
        # 2. Retriever analyzes links
        project_context = f"Project: {self.project_name}, URL: {self.repo_url}"
        
        # Limit number of links analyzed (avoid excessive API calls)
        max_links = 10
        if len(unique_links) > max_links:
            logger.info(f"Retriever: Limiting to {max_links} most relevant links")
            unique_links = unique_links[:max_links]
        
        self.external_research_results = self.retriever.fetch_and_analyze_links(
            links=unique_links,
            project_context=project_context
        )
        
        # 3. Persist research artifact
        save_json(self.external_research_results, self.output_dir / "retriever_research.json")
        
        analyzed_count = len(self.external_research_results.get("analyzed_links", []))
        logger.info(f"Retriever: Successfully analyzed {analyzed_count} links")
        
        # 4. Attach deployment hints to project_materials
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
        
        # Installation info
        installation = deployment_info.get("installation", {})
        if installation:
            commands = installation.get("commands", [])
            if commands:
                summary_parts.append("### Installation Commands (from external docs)")
                for cmd in commands[:5]:
                    summary_parts.append(f"- `{cmd}`")
        
        # Configuration info
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
        
        # System requirements
        requirements = deployment_info.get("system_requirements", [])
        if requirements:
            summary_parts.append("\n### System Requirements (from external docs)")
            for req in requirements[:5]:
                summary_parts.append(f"- {req}")
        
        # Troubleshooting
        troubleshooting = deployment_info.get("troubleshooting", [])
        if troubleshooting:
            summary_parts.append("\n### Troubleshooting Tips")
            for tip in troubleshooting[:3]:
                summary_parts.append(f"- {tip}")
        
        if len(summary_parts) > 1:
            return "\n".join(summary_parts)
        return ""


