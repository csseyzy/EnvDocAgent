#!/usr/bin/env python3
"""
README completeness checker

Checks whether a generated README includes a full deployment command sequence
"""

import sys
import re
from pathlib import Path
from typing import Dict


class ReadmeCompletenessChecker:
    """README completeness checker"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
    
    def check(self, readme_path: str) -> Dict:
        """Check README completeness"""
        content = Path(readme_path).read_text()
        
        # 1. Detect project type
        project_type = self._detect_project_type(content)
        print(f"Detected project type: {project_type}")
        
        # 2. Required commands by project type
        if project_type == "Python":
            self._check_python_project(content)
        elif project_type == "Node.js":
            self._check_nodejs_project(content)
        elif project_type == "Java":
            self._check_java_project(content)
        elif project_type == "Go":
            self._check_go_project(content)
        elif project_type == "Docker":
            self._check_docker_project(content)
        else:
            self.warnings.append({
                "type": "unknown_project_type",
                "message": f"Could not determine project type; skipping type-specific checks"
            })
        
        # 3. Generic checks
        self._check_command_sequence(content)
        self._check_verification(content)
        
        # 4. Score
        score = self._calculate_score()
        
        return {
            "project_type": project_type,
            "score": score,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "is_complete": score >= 95
        }
    
    def _detect_project_type(self, content: str) -> str:
        """Detect project type"""
        content_lower = content.lower()
        
        # Docker
        if "docker" in content_lower and "docker-compose" in content_lower:
            return "Docker"
        
        # Python
        if "python" in content_lower or "pip install" in content_lower:
            return "Python"
        
        # Node.js
        if "node" in content_lower or "npm install" in content_lower:
            return "Node.js"
        
        # Java
        if "java" in content_lower or "mvn" in content_lower or "gradle" in content_lower:
            return "Java"
        
        # Go
        if "golang" in content_lower or "go mod" in content_lower or "go build" in content_lower:
            return "Go"
        
        return "Unknown"
    
    def _check_python_project(self, content: str):
        """Check required commands for Python projects"""
        # 1. Dependency install
        if not re.search(r'pip\s+install', content, re.IGNORECASE):
            self.errors.append({
                "type": "missing_dependency_install",
                "severity": "blocker",
                "message": "Missing dependency install: pip install",
                "fix": "Add: pip install -r requirements.txt"
            })
        else:
            self.info.append("✅ Includes Python dependency install: pip install")
        
        # 2. Virtualenv (optional but recommended)
        if "venv" in content or "virtualenv" in content:
            self.info.append("✅ Includes virtual environment setup")
        else:
            self.warnings.append({
                "type": "missing_venv",
                "message": "Consider adding virtualenv: python -m venv venv"
            })
        
        # 3. DB migrations if DB mentioned
        if "database" in content.lower() or "postgresql" in content.lower() or "mysql" in content.lower():
            if not re.search(r'migrate|db\s+upgrade', content, re.IGNORECASE):
                self.warnings.append({
                    "type": "missing_db_migration",
                    "message": "Database mentioned but no migration command"
                })
            else:
                self.info.append("✅ Includes database migration command")
        
        # 4. Start command
        if not re.search(r'python\s+\w+\.py|flask\s+run|uvicorn|gunicorn', content, re.IGNORECASE):
            self.errors.append({
                "type": "missing_start_command",
                "severity": "blocker",
                "message": "Missing Python app start command",
                "fix": "Add a start command, e.g.: python app.py"
            })
        else:
            self.info.append("✅ Includes app start command")
    
    def _check_nodejs_project(self, content: str):
        """Check required commands for Node.js projects"""
        # 1. Dependency install
        if not re.search(r'npm\s+install|yarn\s+install|pnpm\s+install', content, re.IGNORECASE):
            self.errors.append({
                "type": "missing_dependency_install",
                "severity": "blocker",
                "message": "Missing dependency install: npm install",
                "fix": "Add: npm install"
            })
        else:
            self.info.append("✅ Includes Node.js dependency install")
        
        # 2. Build (TypeScript)
        if "typescript" in content.lower() or ".ts" in content:
            if not re.search(r'npm\s+run\s+build|tsc|build', content, re.IGNORECASE):
                self.warnings.append({
                    "type": "missing_build",
                    "message": "TypeScript projects should include a build step: npm run build"
                })
            else:
                self.info.append("✅ Includes build command")
        
        # 3. Start command
        if not re.search(r'npm\s+start|node\s+\w+\.js|yarn\s+start', content, re.IGNORECASE):
            self.errors.append({
                "type": "missing_start_command",
                "severity": "blocker",
                "message": "Missing Node.js app start command",
                "fix": "Add a start command, e.g.: npm start"
            })
        else:
            self.info.append("✅ Includes app start command")
    
    def _check_java_project(self, content: str):
        """Check required commands for Java projects"""
        # 1. Build (required)
        has_maven = re.search(r'mvn|maven', content, re.IGNORECASE)
        has_gradle = re.search(r'gradle', content, re.IGNORECASE)
        
        if not has_maven and not has_gradle:
            self.errors.append({
                "type": "missing_build",
                "severity": "blocker",
                "message": "Java project missing build command",
                "fix": "Add build: mvn clean package or gradle build"
            })
        else:
            tool = "Maven" if has_maven else "Gradle"
            self.info.append(f"✅ Includes {tool} build command")
        
        # 2. Run command
        if not re.search(r'java\s+-jar|mvn\s+spring-boot:run|gradle\s+bootRun', content, re.IGNORECASE):
            self.errors.append({
                "type": "missing_start_command",
                "severity": "blocker",
                "message": "Missing Java app run command",
                "fix": "Add run command, e.g.: java -jar target/app.jar"
            })
        else:
            self.info.append("✅ Includes app run command")
    
    def _check_go_project(self, content: str):
        """Check required commands for Go projects"""
        # 1. Dependencies
        if not re.search(r'go\s+mod\s+(download|tidy)|go\s+get', content, re.IGNORECASE):
            self.errors.append({
                "type": "missing_dependency_install",
                "severity": "blocker",
                "message": "Missing Go dependency download command",
                "fix": "Add: go mod download"
            })
        else:
            self.info.append("✅ Includes Go dependency download")
        
        # 2. Build or run
        if not re.search(r'go\s+build|go\s+run', content, re.IGNORECASE):
            self.errors.append({
                "type": "missing_start_command",
                "severity": "blocker",
                "message": "Missing Go build/run command",
                "fix": "Add: go build -o app or go run main.go"
            })
        else:
            self.info.append("✅ Includes app build/run command")
    
    def _check_docker_project(self, content: str):
        """Check required commands for Docker projects"""
        # 1. docker-compose up
        if not re.search(r'docker[- ]compose\s+up', content, re.IGNORECASE):
            self.errors.append({
                "type": "missing_docker_start",
                "severity": "blocker",
                "message": "Missing docker-compose up",
                "fix": "Add: docker-compose up -d"
            })
        else:
            self.info.append("✅ Includes docker-compose up")
        
        # 2. Local deps (scripts / fallback)
        has_pip = re.search(r'pip\s+install', content, re.IGNORECASE)
        has_npm = re.search(r'npm\s+install', content, re.IGNORECASE)
        
        if not has_pip and not has_npm:
            self.warnings.append({
                "type": "missing_dependency_install_docker",
                "message": "Docker READMEs often include local install (pip/npm) for scripts or fallback"
            })
        else:
            self.info.append("✅ Includes local dependency install")
        
        # 3. Env file
        if ".env" not in content:
            self.warnings.append({
                "type": "missing_env_file",
                "message": "Consider documenting a .env file for Docker projects"
            })
        else:
            self.info.append("✅ Mentions .env file")
        
        # 4. Wait for services
        if "sleep" in content or "wait" in content or "pg_isready" in content:
            self.info.append("✅ Includes wait-for-ready steps")
        else:
            self.warnings.append({
                "type": "missing_wait",
                "message": "Consider adding commands to wait for services to be ready"
            })
        
        # 5. Non-Docker fallback
        if "backup" in content.lower() or "fallback" in content.lower() or "without docker" in content.lower():
            self.info.append("✅ Includes local fallback when Docker is unavailable")
        else:
            self.warnings.append({
                "type": "missing_fallback",
                "message": "Consider a fallback run path when Docker is unavailable"
            })
    
    def _check_command_sequence(self, content: str):
        """Check command ordering in README"""
        # Extract fenced command blocks
        code_blocks = re.findall(r'```(?:bash|sh)?\n(.*?)```', content, re.DOTALL)
        
        if not code_blocks:
            self.warnings.append({
                "type": "no_code_blocks",
                "message": "No code blocks found; command format may be wrong"
            })
            return
        
        full_content = '\n'.join(code_blocks)
        
        # git clone
        if "git clone" not in content:
            self.warnings.append({
                "type": "missing_clone",
                "message": "Consider adding git clone"
            })
        
        # Order: install before start
        install_patterns = [r'pip\s+install', r'npm\s+install', r'go\s+mod', r'mvn\s+package']
        start_patterns = [r'python\s+\w+\.py', r'npm\s+start', r'java\s+-jar', r'go\s+run']
        
        install_pos = -1
        start_pos = -1
        
        for pattern in install_patterns:
            match = re.search(pattern, full_content, re.IGNORECASE)
            if match:
                install_pos = match.start()
                break
        
        for pattern in start_patterns:
            match = re.search(pattern, full_content, re.IGNORECASE)
            if match:
                start_pos = match.start()
                break
        
        if install_pos > 0 and start_pos > 0 and install_pos > start_pos:
            self.errors.append({
                "type": "wrong_command_order",
                "severity": "blocker",
                "message": "Wrong order: dependency install appears after start command",
                "fix": "Put dependency install before the start command"
            })
    
    def _check_verification(self, content: str):
        """Check verification steps"""
        # 1. Verification command
        if not re.search(r'curl|wget|http|verify', content, re.IGNORECASE):
            self.warnings.append({
                "type": "missing_verification",
                "message": "Missing command to verify deployment"
            })
        else:
            self.info.append("✅ Includes verification command")
        
        # 2. Expected output
        if re.search(r'expected\s*[:：]|anticipated:', content, re.IGNORECASE):
            self.info.append("✅ Includes expected output")
        else:
            self.warnings.append({
                "type": "missing_expected_output",
                "message": "Consider expected output for verification commands"
            })
    
    def _calculate_score(self) -> int:
        """Compute score"""
        base_score = 100
        
        # blocker errors: -20 each
        for error in self.errors:
            if error.get('severity') == 'blocker':
                base_score -= 20
        
        # warnings: -5 each
        for warning in self.warnings:
            base_score -= 5
        
        return max(base_score, 0)


def main():
    if len(sys.argv) < 2:
        print("Usage: python check_readme_completeness.py <readme_path>")
        sys.exit(1)
    
    readme_path = sys.argv[1]
    
    if not Path(readme_path).exists():
        print(f"❌ File not found: {readme_path}")
        sys.exit(1)
    
    print("=" * 70)
    print("README completeness checker — command sequence validation")
    print("=" * 70)
    print()
    
    checker = ReadmeCompletenessChecker()
    result = checker.check(readme_path)
    
    print()
    print("=" * 70)
    print("Check results")
    print("=" * 70)
    print(f"Project type: {result['project_type']}")
    print(f"Completeness score: {result['score']}/100")
    print(f"Complete: {'✅ yes' if result['is_complete'] else '❌ no'}")
    print()
    
    if result['info']:
        print("✅ Present:")
        for info in result['info']:
            print(f"  {info}")
        print()
    
    if result['errors']:
        print(f"❌ Errors ({len(result['errors'])}) — must fix:")
        for i, error in enumerate(result['errors'], 1):
            print(f"\n  {i}. [{error.get('severity', 'error').upper()}] {error['message']}")
            if 'fix' in error:
                print(f"     Fix: {error['fix']}")
        print()
    
    if result['warnings']:
        print(f"⚠️  Warnings ({len(result['warnings'])}) — recommended:")
        for i, warning in enumerate(result['warnings'], 1):
            print(f"  {i}. {warning['message']}")
        print()
    
    print("=" * 70)
    
    if result['is_complete']:
        print("✅ README command sequence looks complete for LLM-assisted deployment.")
    else:
        print("❌ README command sequence is incomplete; add the missing commands.")
    
    print("=" * 70)
    
    sys.exit(0 if result['is_complete'] else 1)


if __name__ == "__main__":
    main()
