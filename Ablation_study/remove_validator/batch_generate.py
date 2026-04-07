#!/usr/bin/env python3
"""
Batch README generation tool

⚠️ Deprecated: logic has been merged into main.py
Use: python3 main.py --batch github_links.txt

Reads multiple GitHub URLs from a txt file and generates README files for each
"""

print("=" * 70)
print("⚠️  Note: batch_generate.py has been merged into main.py")
print("=" * 70)
print()
print("Use these commands instead:")
print()
print("  # Batch generation")
print("  python3 main.py --batch github_links.txt")
print()
print("  # Custom output directory")
print("  python3 main.py --batch repos.txt --output-dir output/my_batch")
print()
print("  # Help")
print("  python3 main.py --help")
print()
print("=" * 70)
import sys
sys.exit(0)

import os
import sys
import argparse
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from orchestrator import Orchestrator
from logger import get_logger

logger = get_logger(__name__)


class BatchGenerator:
    """Batch README generator"""
    
    def __init__(self, input_file: str, output_dir: str = "output/batch", 
                 enable_external_fetch: bool = False):
        """
        Initialize batch generator
        
        Args:
            input_file: Path to txt file with one GitHub URL per line
            output_dir: Output directory
            enable_external_fetch: Whether to fetch external docs
        """
        self.input_file = input_file
        self.output_dir = output_dir
        self.enable_external_fetch = enable_external_fetch
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.total_count = 0
        self.success_count = 0
        self.failed_count = 0
        self.results: List[Dict[str, Any]] = []
    
    def read_github_links(self) -> List[str]:
        """
        Read GitHub URLs from file
        
        Returns:
            List of GitHub URLs
        """
        if not os.path.exists(self.input_file):
            logger.error(f"Input file not found: {self.input_file}")
            return []
        
        links = []
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    if not line or line.startswith('#'):
                        continue
                    
                    if not self._is_valid_github_url(line):
                        logger.warning(f"Line {line_num} is not a valid GitHub URL: {line}")
                        continue
                    
                    links.append(line)
            
            logger.info(f"Read {len(links)} valid GitHub URL(s) from {self.input_file}")
            return links
        
        except Exception as e:
            logger.error(f"Failed to read file: {e}")
            return []
    
    def _is_valid_github_url(self, url: str) -> bool:
        """
        Return True if url looks like a GitHub repo URL
        
        Args:
            url: URL string
            
        Returns:
            Whether URL is accepted
        """
        url = url.lower()
        return (url.startswith('https://github.com/') or 
                url.startswith('http://github.com/'))
    
    def _extract_repo_name(self, github_url: str) -> str:
        """
        Derive owner_repo name from GitHub URL
        
        Args:
            github_url: GitHub URL
            
        Returns:
            Name used for output files
        """
        # https://github.com/owner/repo -> owner_repo
        # https://github.com/owner/repo.git -> owner_repo
        
        url = github_url.rstrip('/')
        if url.endswith('.git'):
            url = url[:-4]
        
        parts = url.split('/')
        if len(parts) >= 5:
            owner = parts[-2]
            repo = parts[-1]
            return f"{owner}_{repo}"
        
        return "unknown_repo"
    
    def generate_single(self, github_url: str, index: int, total: int) -> Dict[str, Any]:
        """
        Generate README for one repo
        
        Args:
            github_url: GitHub URL
            index: Current index (1-based)
            total: Total count
            
        Returns:
            Result dict
        """
        repo_name = self._extract_repo_name(github_url)
        
        logger.info("=" * 70)
        logger.info(f"[{index}/{total}] Starting README generation: {repo_name}")
        logger.info(f"GitHub URL: {github_url}")
        logger.info("=" * 70)
        
        result = {
            'index': index,
            'github_url': github_url,
            'repo_name': repo_name,
            'status': 'unknown',
            'output_file': None,
            'error': None,
            'start_time': datetime.now(),
            'end_time': None,
            'duration': None
        }
        
        try:
            orchestrator = Orchestrator(
                repo_url=github_url,
                enable_external_fetch=self.enable_external_fetch
            )
            
            readme_content = orchestrator.generate_readme()
            
            if not readme_content:
                raise ValueError("Generated README content is empty")
            
            output_filename = f"README_{repo_name}.md"
            output_path = os.path.join(self.output_dir, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            result['status'] = 'success'
            result['output_file'] = output_path
            
            logger.info(f"✅ [{index}/{total}] Success: {output_path}")
            self.success_count += 1
        
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            
            logger.error(f"❌ [{index}/{total}] Failed: {repo_name}")
            logger.error(f"Error: {e}")
            self.failed_count += 1
        
        finally:
            result['end_time'] = datetime.now()
            result['duration'] = (result['end_time'] - result['start_time']).total_seconds()
        
        return result
    
    def generate_batch(self):
        """Generate READMEs for all URLs in the input file"""
        start_time = datetime.now()
        
        github_links = self.read_github_links()
        
        if not github_links:
            logger.error("No valid GitHub URLs found")
            return
        
        self.total_count = len(github_links)
        
        logger.info("=" * 70)
        logger.info(f"Starting batch README generation")
        logger.info(f"Total: {self.total_count}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info("=" * 70)
        print()
        
        for index, github_url in enumerate(github_links, 1):
            result = self.generate_single(github_url, index, self.total_count)
            self.results.append(result)
            
            print()
            logger.info(f"Progress: {index}/{self.total_count} ({index*100//self.total_count}%)")
            logger.info(f"Succeeded: {self.success_count}, failed: {self.failed_count}")
            print()
            
            if index < self.total_count:
                time.sleep(2)
        
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        
        self._generate_summary_report(total_duration)
    
    def _generate_summary_report(self, total_duration: float):
        """
        Print and persist summary report
        
        Args:
            total_duration: Total elapsed seconds
        """
        logger.info("=" * 70)
        logger.info("Batch complete — summary")
        logger.info("=" * 70)
        
        print()
        print("╔" + "=" * 68 + "╗")
        print("║" + " Batch generation summary ".center(68) + "║")
        print("╚" + "=" * 68 + "╝")
        print()
        
        print(f"Total: {self.total_count}")
        print(f"✅ Succeeded: {self.success_count}")
        print(f"❌ Failed: {self.failed_count}")
        print(f"⏱️  Total time: {total_duration:.1f} s ({total_duration/60:.1f} min)")
        print(f"📊 Avg time: {total_duration/self.total_count:.1f} s per repo")
        print()
        
        if self.success_count > 0:
            print("━" * 70)
            print("✅ Succeeded:")
            print("━" * 70)
            for result in self.results:
                if result['status'] == 'success':
                    print(f"  [{result['index']}] {result['repo_name']}")
                    print(f"      File: {result['output_file']}")
                    print(f"      Duration: {result['duration']:.1f} s")
                    print()
        
        if self.failed_count > 0:
            print("━" * 70)
            print("❌ Failed:")
            print("━" * 70)
            for result in self.results:
                if result['status'] == 'failed':
                    print(f"  [{result['index']}] {result['repo_name']}")
                    print(f"      URL: {result['github_url']}")
                    print(f"      Error: {result['error']}")
                    print()
        
        report_path = os.path.join(self.output_dir, "batch_report.txt")
        self._save_detailed_report(report_path, total_duration)
        
        print("━" * 70)
        print(f"📄 Detailed report saved to: {report_path}")
        print("━" * 70)
    
    def _save_detailed_report(self, report_path: str, total_duration: float):
        """
        Write detailed report to disk
        
        Args:
            report_path: Report file path
            total_duration: Total elapsed seconds
        """
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("Batch README generation — detailed report\n")
            f.write("=" * 70 + "\n\n")
            
            f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Input file: {self.input_file}\n")
            f.write(f"Output directory: {self.output_dir}\n\n")
            
            f.write(f"Total: {self.total_count}\n")
            f.write(f"Succeeded: {self.success_count}\n")
            f.write(f"Failed: {self.failed_count}\n")
            f.write(f"Success rate: {self.success_count*100//self.total_count if self.total_count > 0 else 0}%\n")
            f.write(f"Total time: {total_duration:.1f} s ({total_duration/60:.1f} min)\n")
            f.write(f"Avg time: {total_duration/self.total_count:.1f} s per repo\n\n")
            
            f.write("=" * 70 + "\n")
            f.write("Per-repo results\n")
            f.write("=" * 70 + "\n\n")
            
            for result in self.results:
                f.write(f"[{result['index']}] {result['repo_name']}\n")
                f.write(f"  URL: {result['github_url']}\n")
                f.write(f"  Status: {'✅ success' if result['status'] == 'success' else '❌ failed'}\n")
                
                if result['status'] == 'success':
                    f.write(f"  Output file: {result['output_file']}\n")
                else:
                    f.write(f"  Error: {result['error']}\n")
                
                f.write(f"  Duration: {result['duration']:.1f} s\n")
                f.write(f"  Started: {result['start_time'].strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"  Finished: {result['end_time'].strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("\n")


def main():
    """CLI entry"""
    parser = argparse.ArgumentParser(
        description='Batch README generation — read GitHub URLs from a txt file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:

1. Default input file (github_links.txt):
   python3 batch_generate.py

2. Custom input file:
   python3 batch_generate.py -i repos.txt

3. Custom output directory:
   python3 batch_generate.py -i repos.txt -o output/my_batch

4. Enable external doc fetch:
   python3 batch_generate.py -i repos.txt --fetch-docs

Input format (one GitHub URL per line):
─────────────────────────────────────
https://github.com/owner1/repo1
https://github.com/owner2/repo2
https://github.com/owner3/repo3

# Comments are skipped
https://github.com/owner4/repo4
─────────────────────────────────────
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        default='github_links.txt',
        help='Txt file with GitHub URLs (default: github_links.txt)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='output/batch',
        help='Output directory (default: output/batch)'
    )
    
    parser.add_argument(
        '--fetch-docs',
        action='store_true',
        help='Enable external doc fetch (e.g. from README.md)'
    )
    
    args = parser.parse_args()
    
    generator = BatchGenerator(
        input_file=args.input,
        output_dir=args.output,
        enable_external_fetch=args.fetch_docs
    )
    
    try:
        generator.generate_batch()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted — saving partial results...")
        generator._generate_summary_report(0)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Batch generation error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
