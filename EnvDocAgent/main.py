"""
Main Entry Point (Supports single project and batch generation)
"""

import argparse
import sys
import os
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from rich.console import Console
from orchestrator import Orchestrator
from config import Config
from logger import Logger, get_logger

console = Console()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Multi-Agent README Generation/Completion Framework (Supports single project and batch generation)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage Examples:

Single project:
  python3 main.py https://github.com/owner/repo

Batch generation:
  python3 main.py --batch github_links.txt

Batch generation (with custom output directory):
  python3 main.py --batch repos.txt --output-dir output/my_batch
        """
    )
    
    # Batch mode arguments
    parser.add_argument("--batch", metavar="FILE", 
                       help="Batch generation mode: Read multiple GitHub links from file (one per line)")
    
    # Single project argument (optional in batch mode)
    parser.add_argument("repo_url", nargs='?',
                       help="GitHub repository URL (e.g., https://github.com/owner/repo)")
    
    # Project arguments
    parser.add_argument("--ref", default=None, help="Branch/tag/commit (default: main/master)")
    parser.add_argument("--github-token", default=None, help="GitHub Token (optional)")
    
    # External fetch arguments
    enable_external_fetch_group = parser.add_mutually_exclusive_group()
    enable_external_fetch_group.add_argument("--enable-external-fetch", action="store_true",
                                             default=Config.DEFAULT_ENABLE_EXTERNAL_FETCH,
                                             help="Enable external link content fetching (default)")
    enable_external_fetch_group.add_argument("--disable-external-fetch", action="store_false",
                                             dest="enable_external_fetch",
                                             help="Disable external link content fetching")
    
    # Runtime arguments
    parser.add_argument("--max-rounds", type=int, default=Config.DEFAULT_MAX_ROUNDS,
                       help=f"Maximum iteration rounds (default: {Config.DEFAULT_MAX_ROUNDS})")
    parser.add_argument("--output-dir", default=Config.OUTPUT_DIR,
                       help=f"Output directory (default: {Config.OUTPUT_DIR})")
    
    # Logging arguments
    parser.add_argument("--log-dir", default=Config.LOG_DIR,
                       help=f"Log directory (default: {Config.LOG_DIR})")
    parser.add_argument("--log-level", default=Config.LOG_LEVEL,
                       choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                       help=f"Log level (default: {Config.LOG_LEVEL})")
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.batch and args.repo_url:
        console.print("[bold red]Error: Cannot use batch mode and specify single repository at the same time[/bold red]")
        console.print("Use --batch for batch generation, or specify repository URL directly")
        sys.exit(1)
    
    if not args.batch and not args.repo_url:
        console.print("[bold red]Error: Must specify repository URL or use --batch parameter[/bold red]")
        parser.print_help()
        sys.exit(1)
    
    # Initialize logging system
    logger = Logger.setup(log_dir=args.log_dir, log_level=args.log_level)
    
    # Check LLM configuration
    has_openai = bool(Config.OPENAI_API_KEY)
    has_azure = bool(Config.AZURE_OPENAI_API_KEY and Config.AZURE_OPENAI_ENDPOINT and Config.AZURE_OPENAI_DEPLOYMENT)
    has_bedrock = bool(Config.AWS_ACCESS_KEY_ID and Config.AWS_SECRET_ACCESS_KEY)
    has_anthropic = bool(Config.ANTHROPIC_API_KEY)
    
    if not (has_openai or has_azure or has_bedrock or has_anthropic):
        error_msg = "No LLM service configured"
        logger.error(error_msg)
        console.print(f"[bold red]Error: {error_msg}[/bold red]")
        console.print("Please configure one of the following services in .env file:")
        console.print("  1. OpenAI: OPENAI_API_KEY")
        console.print("  2. Azure OpenAI: AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT")
        console.print("  3. AWS Bedrock: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION_NAME")
        console.print("  4. Anthropic: ANTHROPIC_API_KEY")
        sys.exit(1)
    
    try:
        # Determine batch or single mode
        if args.batch:
            # Batch generation mode
            run_batch_mode(args, logger)
        else:
            # Single project mode
            run_single_mode(args, logger)
    except KeyboardInterrupt:
        logger.warning("User interrupted program")
        console.print("\n[yellow]User interrupted[/yellow]")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Program exited abnormally: {e}")
        console.print(f"[bold red]Error: {e}[/bold red]")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)


def run_single_mode(args, logger):
    """Run single project generation mode"""
    logger.info("="*80)
    logger.info("README Agent Started (Single Project Mode)")
    logger.info(f"Repository URL: {args.repo_url}")
    logger.info(f"Branch/Ref: {args.ref or 'default'}")
    logger.info(f"Max iteration rounds: {args.max_rounds}")
    logger.info(f"Output directory: {args.output_dir}")
    logger.info(f"Log file: {Logger.get_log_file()}")
    logger.info("="*80)
    
    # Create orchestrator and run
    logger.info("Creating orchestrator and starting run")
    orchestrator = Orchestrator(
        repo_url=args.repo_url,
        ref=args.ref,
        github_token=args.github_token,
        enable_external_fetch=args.enable_external_fetch,
        max_rounds=args.max_rounds
    )
    
    result = orchestrator.run()
    
    if result["success"]:
        logger.info("="*80)
        logger.info("README generation successful")
        logger.info(f"Output directory: {result['output_dir']}")
        logger.info(f"Generated README: {Path(result['output_dir']) / Config.GENERATED_README_FILE}")
        logger.info(f"Log file: {Logger.get_log_file()}")
        
        usage = result.get("api_usage", {})
        elapsed = result.get("elapsed_seconds", 0)
        if usage:
            logger.info(f"Total time: {elapsed}s | LLM calls: {usage.get('total_calls', 0)} | "
                        f"Tokens: {usage.get('total_tokens', 0):,} | Cost: ${usage.get('total_cost_usd', 0):.4f}")
        logger.info("="*80)
        
        console.print(f"\n[bold green]✓ Complete! Output directory: {result['output_dir']}[/bold green]")
        console.print(f"[green]Generated README: {Path(result['output_dir']) / Config.GENERATED_README_FILE}[/green]")
        console.print(f"[blue]Log file: {Logger.get_log_file()}[/blue]")
        console.print(f"[blue]Cost summary: {Path(result['output_dir']) / 'run_cost_summary.json'}[/blue]")
    else:
        logger.error("README generation failed")
        console.print("[bold red]✗ Generation failed[/bold red]")
        sys.exit(1)
    

def run_batch_mode(args, logger):
    """Run batch generation mode"""
    logger.info("="*80)
    logger.info("README Agent Started (Batch Generation Mode)")
    logger.info(f"Input file: {args.batch}")
    logger.info(f"Output directory: {args.output_dir}")
    logger.info(f"Max iteration rounds: {args.max_rounds}")
    logger.info(f"Log file: {Logger.get_log_file()}")
    logger.info("="*80)
    
    # Read GitHub links
    github_links = read_github_links(args.batch, logger)
    
    if not github_links:
        logger.error("No valid GitHub links found")
        console.print("[bold red]Error: No valid GitHub links found[/bold red]")
        sys.exit(1)
    
    total_count = len(github_links)
    success_count = 0
    failed_count = 0
    results: List[Dict[str, Any]] = []
    
    # Batch report output directory
    batch_output_dir = args.output_dir
    os.makedirs(batch_output_dir, exist_ok=True)
    
    console.print(f"\n[bold cyan]Starting batch README generation[/bold cyan]")
    console.print(f"Total: {total_count}")
    console.print(f"Output directory: {batch_output_dir}/<project_name>/")
    console.print("="*70)
    print()
    
    start_time = datetime.now()
    
    # Generate one by one
    for index, github_url in enumerate(github_links, 1):
        result = generate_single_project(
            github_url=github_url,
            index=index,
            total=total_count,
            args=args,
            logger=logger,
            batch_output_dir=batch_output_dir
        )
        results.append(result)
        
        if result['status'] == 'success':
            success_count += 1
        else:
            failed_count += 1
        
        # Print progress
        print()
        console.print(f"[cyan]Progress: {index}/{total_count} ({index*100//total_count}%)[/cyan]")
        console.print(f"[green]Success: {success_count}[/green], [red]Failed: {failed_count}[/red]")
        print()
        
        # Brief delay to avoid rapid requests
        if index < total_count:
            time.sleep(2)
    
    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()
    
    # Generate summary report
    generate_batch_report(
        results=results,
        total_count=total_count,
        success_count=success_count,
        failed_count=failed_count,
        total_duration=total_duration,
        batch_output_dir=batch_output_dir,
        logger=logger
    )


def read_github_links(input_file: str, logger) -> List[str]:
    """Read GitHub links from file"""
    if not os.path.exists(input_file):
        logger.error(f"Input file does not exist: {input_file}")
        return []
    
    links = []
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comment lines
                if not line or line.startswith('#'):
                    continue
                
                # Validate if it's a GitHub link
                if not is_valid_github_url(line):
                    logger.warning(f"Line {line_num} is not a valid GitHub link: {line}")
                    continue
                
                links.append(line)
        
        logger.info(f"Read {len(links)} valid GitHub links from {input_file}")
        return links
    
    except Exception as e:
        logger.error(f"Failed to read file: {e}")
        return []


def is_valid_github_url(url: str) -> bool:
    """Validate if URL is a valid GitHub URL"""
    url = url.lower()
    return (url.startswith('https://github.com/') or 
            url.startswith('http://github.com/'))


def extract_repo_name(github_url: str) -> str:
    """Extract repository name from GitHub URL"""
    url = github_url.rstrip('/')
    if url.endswith('.git'):
        url = url[:-4]
    
    parts = url.split('/')
    if len(parts) >= 5:
        owner = parts[-2]
        repo = parts[-1]
        return f"{owner}_{repo}"
    
    return "unknown_repo"


def generate_single_project(github_url: str, index: int, total: int, 
                           args, logger, batch_output_dir: str) -> Dict[str, Any]:
    """Generate README for a single project"""
    repo_name = extract_repo_name(github_url)
    
    logger.info("=" * 70)
    logger.info(f"[{index}/{total}] Starting README generation: {repo_name}")
    logger.info(f"GitHub URL: {github_url}")
    logger.info("=" * 70)
    
    console.print(f"[bold cyan][{index}/{total}] Starting generation: {repo_name}[/bold cyan]")
    console.print(f"[cyan]URL: {github_url}[/cyan]")
    
    result = {
        'index': index,
        'github_url': github_url,
        'repo_name': repo_name,
        'status': 'unknown',
        'output_file': None,
        'output_dir': None,
        'error': None,
        'start_time': datetime.now(),
        'end_time': None,
        'duration': None
    }
    
    try:
        # Create Orchestrator
        orchestrator = Orchestrator(
            repo_url=github_url,
            ref=args.ref,
            github_token=args.github_token,
            enable_external_fetch=args.enable_external_fetch,
            max_rounds=args.max_rounds
        )
        
        # Generate README using run() method
        run_result = orchestrator.run()
        
        if not run_result.get("success") or not run_result.get("final_readme"):
            raise ValueError("Generated README content is empty")
        
        # Output directory is already created by Orchestrator under output/<project_name>/
        result['status'] = 'success'
        result['output_dir'] = run_result.get("output_dir")
        result['output_file'] = os.path.join(run_result.get("output_dir", ""), Config.GENERATED_README_FILE)
        
        logger.info(f"✅ [{index}/{total}] Successfully generated: {result['output_dir']}")
        console.print(f"[bold green]✅ [{index}/{total}] Success: {repo_name}[/bold green]")
        console.print(f"[green]   Output: {result['output_dir']}[/green]")
    
    except Exception as e:
        result['status'] = 'failed'
        result['error'] = str(e)
        
        logger.error(f"❌ [{index}/{total}] Generation failed: {repo_name}")
        logger.error(f"Error message: {e}")
        console.print(f"[bold red]❌ [{index}/{total}] Failed: {repo_name}[/bold red]")
        console.print(f"[red]Error: {e}[/red]")
    
    finally:
        result['end_time'] = datetime.now()
        result['duration'] = (result['end_time'] - result['start_time']).total_seconds()
    
    return result


def generate_batch_report(results: List[Dict[str, Any]], total_count: int, 
                         success_count: int, failed_count: int, 
                         total_duration: float, batch_output_dir: str, logger):
    """Generate batch generation summary report"""
    logger.info("=" * 70)
    logger.info("Batch generation completed - Summary report")
    logger.info("=" * 70)
    
    print()
    console.print("[bold cyan]" + "="*68 + "[/bold cyan]")
    console.print("[bold cyan]" + " "*20 + "Batch Generation Summary Report" + " "*20 + "[/bold cyan]")
    console.print("[bold cyan]" + "="*68 + "[/bold cyan]")
    print()
    
    console.print(f"Total: {total_count}")
    console.print(f"[green]✅ Success: {success_count}[/green]")
    console.print(f"[red]❌ Failed: {failed_count}[/red]")
    console.print(f"[cyan]⏱️  Total time: {total_duration:.1f} sec ({total_duration/60:.1f} min)[/cyan]")
    console.print(f"[cyan]📊 Average: {total_duration/total_count:.1f} sec/project[/cyan]")
    print()
    
    # Success list
    if success_count > 0:
        console.print("[bold green]" + "━"*70 + "[/bold green]")
        console.print("[bold green]✅ Successfully generated projects:[/bold green]")
        console.print("[bold green]" + "━"*70 + "[/bold green]")
        for result in results:
            if result['status'] == 'success':
                console.print(f"  [{result['index']}] {result['repo_name']}")
                console.print(f"      Output Dir: {result['output_dir']}")
                console.print(f"      README: {result['output_file']}")
                console.print(f"      Duration: {result['duration']:.1f} sec")
                print()
    
    # Failed list
    if failed_count > 0:
        console.print("[bold red]" + "━"*70 + "[/bold red]")
        console.print("[bold red]❌ Failed projects:[/bold red]")
        console.print("[bold red]" + "━"*70 + "[/bold red]")
        for result in results:
            if result['status'] == 'failed':
                console.print(f"  [{result['index']}] {result['repo_name']}")
                console.print(f"      URL: {result['github_url']}")
                console.print(f"      Error: {result['error']}")
                print()
    
    # Save detailed report to file
    report_path = os.path.join(batch_output_dir, "batch_report.txt")
    save_detailed_report(report_path, results, total_count, success_count, 
                        failed_count, total_duration, logger)
    
    console.print("━"*70)
    console.print(f"[blue]📄 Detailed report saved to: {report_path}[/blue]")
    console.print("━"*70)


def save_detailed_report(report_path: str, results: List[Dict[str, Any]],
                        total_count: int, success_count: int, failed_count: int,
                        total_duration: float, logger):
    """Save detailed report to file"""
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("Batch README Generation Detailed Report\n")
        f.write("=" * 70 + "\n\n")
        
        f.write(f"Generation time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write(f"Total: {total_count}\n")
        f.write(f"Success: {success_count}\n")
        f.write(f"Failed: {failed_count}\n")
        f.write(f"Success rate: {success_count*100//total_count if total_count > 0 else 0}%\n")
        f.write(f"Total time: {total_duration:.1f} sec ({total_duration/60:.1f} min)\n")
        f.write(f"Average time: {total_duration/total_count:.1f} sec/project\n\n")
        
        f.write("=" * 70 + "\n")
        f.write("Detailed Results\n")
        f.write("=" * 70 + "\n\n")
        
        for result in results:
            f.write(f"[{result['index']}] {result['repo_name']}\n")
            f.write(f"  URL: {result['github_url']}\n")
            f.write(f"  Status: {'✅ Success' if result['status'] == 'success' else '❌ Failed'}\n")
            
            if result['status'] == 'success':
                f.write(f"  Output directory: {result['output_dir']}\n")
                f.write(f"  README file: {result['output_file']}\n")
            else:
                f.write(f"  Error message: {result['error']}\n")
            
            f.write(f"  Duration: {result['duration']:.1f} sec\n")
            f.write(f"  Start time: {result['start_time'].strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"  End time: {result['end_time'].strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("\n")
    
    logger.info(f"Detailed report saved to: {report_path}")


if __name__ == "__main__":
    main()

