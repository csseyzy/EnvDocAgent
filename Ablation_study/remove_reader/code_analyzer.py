"""
Code analysis module (deterministic tools, not LLM-based).
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml
import toml

# Import deep content analyzer
try:
    from content_analyzer import ContentAnalyzer, identify_priority_files
    CONTENT_ANALYZER_AVAILABLE = True
except ImportError:
    CONTENT_ANALYZER_AVAILABLE = False
    print("Warning: content_analyzer module not found, skipping deep code analysis")


class CodeAnalyzer:
    """Code Analyzer"""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.results = {
            "repo_path": str(repo_path),
            "language_clues": [],
            "entry_points": [],
            "dependencies": [],
            "test_clues": [],
            "install_commands": [],
            "run_commands": [],
            "test_commands": [],
            "file_stats": {},
            "content_analysis": []  # Deep code analysis results
        }
    
    def analyze(self) -> Dict[str, Any]:
        """Execute complete analysis"""
        # File-level analysis
        self._analyze_languages()
        self._analyze_dependencies()
        self._analyze_entry_points()
        self._analyze_tests()
        self._analyze_ci_workflows()
        self._collect_file_stats()
        
        # Deep content analysis
        if CONTENT_ANALYZER_AVAILABLE:
            self._analyze_content()
        
        return self.results
    
    def _collect_file_stats(self):
        """Collect file statistics"""
        file_counts = {}
        total_files = 0
        
        # Count various file types
        for file_path in self.repo_path.rglob('*'):
            if file_path.is_file():
                total_files += 1
                suffix = file_path.suffix.lower()
                if suffix:
                    file_counts[suffix] = file_counts.get(suffix, 0) + 1
        
        self.results["file_stats"] = {
            "total_files": total_files,
            "by_type": file_counts
        }
    
    def _analyze_content(self):
        """Deep code content analysis"""
        try:
            print("Starting deep code content analysis...")
            
            # 1. Identify high priority files
            priority_files = identify_priority_files(self.repo_path)
            print(f"Found {len(priority_files)} high priority files")
            
            # 2. Create content analyzer
            content_analyzer = ContentAnalyzer()
            
            # 3. Analyze each high-priority file
            analyzed_count = 0
            for file_path, priority in priority_files:
                try:
                    result = content_analyzer.analyze_file(file_path)
                    if result and not result.get("error"):
                        self.results["content_analysis"].append(result)
                        analyzed_count += 1
                        print(f"  ✓ Analyzed: {file_path.name} ({result.get('language', 'Unknown')})")
                except Exception as e:
                    print(f"  ✗ Analysis failed {file_path.name}: {e}")
            
            print(f"Deep code content analysis finished. Successfully analyzed {analyzed_count} file(s).")
            
            # 4. Extract deployment info from deep analysis results
            self._extract_deployment_info_from_content()
            
        except Exception as e:
            print(f"Deep code content analysis error: {e}")
            import traceback
            traceback.print_exc()
    
    def _extract_deployment_info_from_content(self):
        """Extract deployment-related information from deep analysis results."""
        if not self.results["content_analysis"]:
            return
        
        for analysis in self.results["content_analysis"]:
            language = analysis.get("language", "")
            file_name = Path(analysis.get("file", "")).name
            
            # Python project
            if language == "Python":
                # Extract framework information
                frameworks = analysis.get("frameworks", [])
                for framework in frameworks:
                    if framework not in [lc.get("evidence") for lc in self.results["language_clues"]]:
                        self.results["language_clues"].append({
                            "language": "Python",
                            "evidence": f"{framework} framework detected",
                            "file": file_name,
                            "type": "framework",
                            "framework": framework
                        })
                
                # Extract CLI arguments
                cli_params = analysis.get("cli_params", [])
                if cli_params:
                    self.results["entry_points"].append({
                        "name": file_name,
                        "path": file_name,
                        "type": "cli_with_params",
                        "file": file_name,
                        "params": cli_params
                    })
            
            # Java project
            elif language == "Java":
                # Extract framework information
                frameworks = analysis.get("frameworks", [])
                for framework in frameworks:
                    self.results["language_clues"].append({
                        "language": "Java",
                        "evidence": f"{framework} detected",
                        "file": file_name,
                        "type": "framework",
                        "framework": framework
                    })
                
                # Extract Spring Boot port
                server_port = analysis.get("server_port")
                if server_port:
                    self.results["language_clues"].append({
                        "language": "Java",
                        "evidence": f"Server port: {server_port}",
                        "file": file_name,
                        "type": "config",
                        "port": server_port
                    })
            
            # C/C++ project
            elif language in ["C", "C++"]:
                # Extract library dependencies
                libraries = analysis.get("libraries", [])
                for lib in libraries:
                    self.results["dependencies"].append({
                        "name": lib,
                        "version": "unspecified",
                        "type": "system_library",
                        "source": f"{file_name} (content analysis)",
                        "file": file_name
                    })
            
            # JavaScript/TypeScript project
            elif language in ["JavaScript", "TypeScript"]:
                # Extract framework information
                frameworks = analysis.get("frameworks", [])
                for framework in frameworks:
                    self.results["language_clues"].append({
                        "language": "JavaScript",
                        "evidence": f"{framework} framework detected",
                        "file": file_name,
                        "type": "framework",
                        "framework": framework
                    })
                
                # Extract server port
                server_port = analysis.get("server_port")
                if server_port:
                    self.results["language_clues"].append({
                        "language": "JavaScript",
                        "evidence": f"Server port: {server_port}",
                        "file": file_name,
                        "type": "config",
                        "port": server_port
                    })
            
            # Go project
            elif language == "Go":
                # Extract framework information
                frameworks = analysis.get("frameworks", [])
                for framework in frameworks:
                    self.results["language_clues"].append({
                        "language": "Go",
                        "evidence": f"{framework} framework detected",
                        "file": file_name,
                        "type": "framework",
                        "framework": framework
                    })
                
                # Extract server port
                server_port = analysis.get("server_port")
                if server_port:
                    self.results["language_clues"].append({
                        "language": "Go",
                        "evidence": f"Server port: {server_port}",
                        "file": file_name,
                        "type": "config",
                        "port": server_port
                    })
            
            # Config files
            elif language == "Config":
                config_type = analysis.get("config_type", "")
                
                # Gradle config
                if config_type == "Gradle":
                    # Extract plugin information
                    plugins = analysis.get("plugins", [])
                    for plugin in plugins:
                        if "spring" in plugin.lower():
                            self.results["language_clues"].append({
                                "language": "Java",
                                "evidence": f"Gradle plugin: {plugin}",
                                "file": file_name,
                                "type": "build_plugin",
                                "plugin": plugin
                            })
                    
                    # Extract Java version
                    java_version = analysis.get("java_version")
                    if java_version:
                        self.results["language_clues"].append({
                            "language": "Java",
                            "version": java_version,
                            "evidence": f"Java version from {file_name}",
                            "file": file_name,
                            "type": "version_constraint"
                        })
                    
                    # Extract dependencies
                    deps = analysis.get("dependencies", [])
                    for dep in deps[:20]:  # limit count
                        self.results["dependencies"].append({
                            "name": dep,
                            "version": "unspecified",
                            "type": "runtime",
                            "source": f"{file_name} (Gradle)",
                            "file": file_name
                        })
                
                # Maven POM config
                elif config_type == "Maven POM":
                    # Extract Java version
                    java_version = analysis.get("java_version")
                    if java_version:
                        self.results["language_clues"].append({
                            "language": "Java",
                            "version": java_version,
                            "evidence": f"Java version from {file_name}",
                            "file": file_name,
                            "type": "version_constraint"
                        })
                    
                    # Extract dependencies
                    deps = analysis.get("dependencies", [])
                    for dep in deps[:20]:
                        self.results["dependencies"].append({
                            "name": dep,
                            "version": "unspecified",
                            "type": "runtime",
                            "source": f"{file_name} (Maven)",
                            "file": file_name
                        })
                    
                    # Extract parent
                    parent = analysis.get("parent")
                    if parent and "spring-boot" in parent.lower():
                        self.results["language_clues"].append({
                            "language": "Java",
                            "evidence": f"Spring Boot parent: {parent}",
                            "file": file_name,
                            "type": "framework",
                            "framework": "Spring Boot"
                        })
                
                # Spring config files
                elif config_type in ["Spring Properties", "Spring YAML"]:
                    # Extract server port
                    server_port = analysis.get("server_port")
                    if server_port:
                        self.results["language_clues"].append({
                            "language": "Java",
                            "evidence": f"Server port: {server_port}",
                            "file": file_name,
                            "type": "config",
                            "port": server_port
                        })
                    
                    # Extract database URL
                    database_url = analysis.get("database_url")
                    if database_url:
                        self.results["language_clues"].append({
                            "language": "Java",
                            "evidence": f"Database URL configured",
                            "file": file_name,
                            "type": "config",
                            "database_url": database_url
                        })
                
                # Dockerfile
                elif config_type == "Dockerfile":
                    # Extract base image
                    base_image = analysis.get("base_image")
                    if base_image:
                        self.results["language_clues"].append({
                            "language": "Docker",
                            "evidence": f"Base image: {base_image}",
                            "file": file_name,
                            "type": "container",
                            "base_image": base_image
                        })
                    
                    # Extract exposed ports
                    exposed_ports = analysis.get("exposed_ports", [])
                    for port in exposed_ports:
                        self.results["language_clues"].append({
                            "language": "Docker",
                            "evidence": f"Exposed port: {port}",
                            "file": file_name,
                            "type": "config",
                            "port": port
                        })
                
                # Docker Compose
                elif config_type == "Docker Compose":
                    services = analysis.get("services", [])
                    if services:
                        self.results["language_clues"].append({
                            "language": "Docker",
                            "evidence": f"Docker Compose services: {', '.join(services)}",
                            "file": file_name,
                            "type": "container",
                            "services": services
                        })
    
    def _analyze_languages(self):
        """Analyze programming languages and versions."""
        # Python
        if (self.repo_path / "setup.py").exists():
            self.results["language_clues"].append({
                "language": "Python",
                "evidence": "setup.py exists",
                "file": "setup.py",
                "type": "build_file"
            })
        
        if (self.repo_path / "pyproject.toml").exists():
            self.results["language_clues"].append({
                "language": "Python",
                "evidence": "pyproject.toml exists",
                "file": "pyproject.toml",
                "type": "build_file"
            })
        
        # Node.js
        if (self.repo_path / "package.json").exists():
            self.results["language_clues"].append({
                "language": "JavaScript/TypeScript",
                "evidence": "package.json exists",
                "file": "package.json",
                "type": "build_file"
            })
        
        # Java
        if (self.repo_path / "pom.xml").exists():
            self.results["language_clues"].append({
                "language": "Java",
                "evidence": "pom.xml exists",
                "file": "pom.xml",
                "type": "build_file"
            })
        
        if (self.repo_path / "build.gradle").exists():
            self.results["language_clues"].append({
                "language": "Java",
                "evidence": "build.gradle exists",
                "file": "build.gradle",
                "type": "build_file"
            })
        
        # Go
        if (self.repo_path / "go.mod").exists():
            self.results["language_clues"].append({
                "language": "Go",
                "evidence": "go.mod exists",
                "file": "go.mod",
                "type": "build_file"
            })
        
        # Rust
        if (self.repo_path / "Cargo.toml").exists():
            self.results["language_clues"].append({
                "language": "Rust",
                "evidence": "Cargo.toml exists",
                "file": "Cargo.toml",
                "type": "build_file"
            })
        
        # Try to read version info from files
        self._extract_version_from_files()
    
    def _extract_version_from_files(self):
        """Extract version information from build files."""
        # Python - pyproject.toml
        pyproject_path = self.repo_path / "pyproject.toml"
        if pyproject_path.exists():
            try:
                data = toml.load(pyproject_path)
                if "project" in data and "requires-python" in data["project"]:
                    version = data["project"]["requires-python"]
                    self.results["language_clues"].append({
                        "language": "Python",
                        "version": version,
                        "evidence": f"requires-python in pyproject.toml",
                        "file": "pyproject.toml",
                        "type": "version_constraint"
                    })
            except:
                pass
        
        # Node.js - package.json engines
        package_json_path = self.repo_path / "package.json"
        if package_json_path.exists():
            try:
                data = json.loads(package_json_path.read_text())
                if "engines" in data:
                    for engine, version in data["engines"].items():
                        self.results["language_clues"].append({
                            "language": engine,
                            "version": version,
                            "evidence": f"engines.{engine} in package.json",
                            "file": "package.json",
                            "type": "version_constraint"
                        })
            except:
                pass
    
    def _analyze_dependencies(self):
        """Analyze dependencies"""
        # Python
        self._analyze_python_deps()
        # Node.js
        self._analyze_node_deps()
        # Java
        self._analyze_java_deps()
        # Go
        self._analyze_go_deps()
        # Rust
        self._analyze_rust_deps()
    
    def _analyze_python_deps(self):
        """Analyze Python dependencies"""
        # requirements.txt
        req_path = self.repo_path / "requirements.txt"
        if req_path.exists():
            deps = self._parse_requirements(req_path)
            for dep in deps:
                self.results["dependencies"].append({
                    "name": dep["name"],
                    "version": dep.get("version", "unspecified"),
                    "type": "runtime",
                    "source": "requirements.txt",
                    "file": "requirements.txt",
                    "line": dep.get("line")
                })
        
        # pyproject.toml
        pyproject_path = self.repo_path / "pyproject.toml"
        if pyproject_path.exists():
            try:
                data = toml.load(pyproject_path)
                # dependencies
                if "project" in data and "dependencies" in data["project"]:
                    for dep in data["project"]["dependencies"]:
                        name, version = self._parse_dependency_string(dep)
                        self.results["dependencies"].append({
                            "name": name,
                            "version": version,
                            "type": "runtime",
                            "source": "pyproject.toml",
                            "file": "pyproject.toml"
                        })
                # dev-dependencies
                if "project" in data and "optional-dependencies" in data["project"]:
                    for group, deps in data["project"]["optional-dependencies"].items():
                        for dep in deps:
                            name, version = self._parse_dependency_string(dep)
                            self.results["dependencies"].append({
                                "name": name,
                                "version": version,
                                "type": "dev",
                                "source": f"pyproject.toml[optional-dependencies.{group}]",
                                "file": "pyproject.toml"
                            })
            except:
                pass
        
        # requirements-dev.txt
        req_dev_path = self.repo_path / "requirements-dev.txt"
        if req_dev_path.exists():
            deps = self._parse_requirements(req_dev_path)
            for dep in deps:
                self.results["dependencies"].append({
                    "name": dep["name"],
                    "version": dep.get("version", "unspecified"),
                    "type": "dev",
                    "source": "requirements-dev.txt",
                    "file": "requirements-dev.txt"
                })
    
    def _analyze_node_deps(self):
        """Analyze Node.js dependencies"""
        package_json_path = self.repo_path / "package.json"
        if package_json_path.exists():
            try:
                data = json.loads(package_json_path.read_text())
                # dependencies
                if "dependencies" in data:
                    for name, version in data["dependencies"].items():
                        self.results["dependencies"].append({
                            "name": name,
                            "version": version,
                            "type": "runtime",
                            "source": "package.json dependencies",
                            "file": "package.json"
                        })
                # devDependencies
                if "devDependencies" in data:
                    for name, version in data["devDependencies"].items():
                        self.results["dependencies"].append({
                            "name": name,
                            "version": version,
                            "type": "dev",
                            "source": "package.json devDependencies",
                            "file": "package.json"
                        })
            except:
                pass
    
    def _analyze_java_deps(self):
        """Analyze Java dependencies"""
        pom_path = self.repo_path / "pom.xml"
        if pom_path.exists():
            # Simple pom.xml parsing (can be improved)
            content = pom_path.read_text(encoding='utf-8', errors='ignore')
            # More complex XML parsing can be added here
            pass
    
    def _analyze_go_deps(self):
        """Analyze Go dependencies."""
        go_mod_path = self.repo_path / "go.mod"
        if go_mod_path.exists():
            content = go_mod_path.read_text(encoding='utf-8', errors='ignore')
            # Parse go.mod
            for line in content.split('\n'):
                if line.strip().startswith('require '):
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        name = parts[1]
                        version = parts[2]
                        self.results["dependencies"].append({
                            "name": name,
                            "version": version,
                            "type": "runtime",
                            "source": "go.mod",
                            "file": "go.mod"
                        })
    
    def _analyze_rust_deps(self):
        """Analyze Rust dependencies"""
        cargo_path = self.repo_path / "Cargo.toml"
        if cargo_path.exists():
            try:
                data = toml.load(cargo_path)
                if "dependencies" in data:
                    for name, spec in data["dependencies"].items():
                        if isinstance(spec, str):
                            version = spec
                        elif isinstance(spec, dict) and "version" in spec:
                            version = spec["version"]
                        else:
                            version = "unspecified"
                        self.results["dependencies"].append({
                            "name": name,
                            "version": version,
                            "type": "runtime",
                            "source": "Cargo.toml",
                            "file": "Cargo.toml"
                        })
            except:
                pass
    
    def _parse_requirements(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse requirements.txt."""
        deps = []
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            for i, line in enumerate(content.split('\n'), 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                name, version = self._parse_dependency_string(line)
                deps.append({
                    "name": name,
                    "version": version,
                    "line": i
                })
        except:
            pass
        return deps
    
    def _parse_dependency_string(self, dep_str: str) -> tuple:
        """Parse dependency string; return (name, version)."""
        # Strip comments
        dep_str = dep_str.split('#')[0].strip()
        
        # Match various formats: package==1.0.0, package>=1.0.0, package~=1.0.0, etc.
        match = re.match(r'^([a-zA-Z0-9_-]+(?:\[.*?\])?)(.*)$', dep_str)
        if match:
            name = match.group(1)
            version = match.group(2).strip() if match.group(2) else "unspecified"
            return name, version
        return dep_str, "unspecified"
    
    def _analyze_entry_points(self):
        """Analyze entry points"""
        # Python - setup.py / pyproject.toml
        pyproject_path = self.repo_path / "pyproject.toml"
        if pyproject_path.exists():
            try:
                data = toml.load(pyproject_path)
                if "project" in data and "scripts" in data["project"]:
                    for name, path in data["project"]["scripts"].items():
                        self.results["entry_points"].append({
                            "name": name,
                            "path": path,
                            "type": "console_script",
                            "file": "pyproject.toml"
                        })
            except:
                pass
        
        # Find common entry files
        common_entries = ["main.py", "app.py", "server.py", "index.js", "main.go", "src/main.rs"]
        for entry in common_entries:
            if (self.repo_path / entry).exists():
                self.results["entry_points"].append({
                    "name": entry,
                    "path": str(self.repo_path / entry),
                    "type": "file",
                    "file": entry
                })
        
        # package.json scripts
        package_json_path = self.repo_path / "package.json"
        if package_json_path.exists():
            try:
                data = json.loads(package_json_path.read_text())
                if "scripts" in data:
                    for name, command in data["scripts"].items():
                        self.results["entry_points"].append({
                            "name": name,
                            "command": command,
                            "type": "npm_script",
                            "file": "package.json"
                        })
            except:
                pass
    
    def _analyze_tests(self):
        """Analyze test-related clues."""
        # Find test files
        test_patterns = ["**/test_*.py", "**/*_test.py", "**/*.test.js", "**/*.spec.js", 
                        "**/*_test.go", "**/*test.rs"]
        for pattern in test_patterns:
            for test_file in self.repo_path.rglob(pattern):
                self.results["test_clues"].append({
                    "file": str(test_file.relative_to(self.repo_path)),
                    "type": "test_file"
                })
        
        # Infer test commands
        if (self.repo_path / "pytest.ini").exists() or any("pytest" in str(d["name"]) for d in self.results["dependencies"]):
            self.results["test_commands"].append({
                "command": "pytest",
                "evidence": "pytest.ini or pytest dependency",
                "type": "inferred"
            })
        
        if (self.repo_path / "package.json").exists():
            package_json_path = self.repo_path / "package.json"
            try:
                data = json.loads(package_json_path.read_text())
                if "scripts" in data and "test" in data["scripts"]:
                    self.results["test_commands"].append({
                        "command": data["scripts"]["test"],
                        "evidence": "package.json scripts.test",
                        "type": "documented",
                        "file": "package.json"
                    })
            except:
                pass
    
    def _analyze_ci_workflows(self):
        """Analyze CI workflows."""
        workflows_path = self.repo_path / ".github" / "workflows"
        if workflows_path.exists():
            for workflow_file in workflows_path.glob("*.yml"):
                try:
                    with open(workflow_file, 'r', encoding='utf-8') as f:
                        workflow = yaml.safe_load(f)
                    
                    # Extract install, run, test commands
                    if "jobs" in workflow:
                        for job_name, job in workflow["jobs"].items():
                            if "steps" in job:
                                for step in job["steps"]:
                                    if "run" in step:
                                        command = step["run"]
                                        step_name = step.get("name", "")
                                        
                                        if any(keyword in step_name.lower() for keyword in ["install", "setup", "build"]):
                                            self.results["install_commands"].append({
                                                "command": command,
                                                "evidence": f".github/workflows/{workflow_file.name}",
                                                "file": str(workflow_file.relative_to(self.repo_path))
                                            })
                                        elif any(keyword in step_name.lower() for keyword in ["test", "test"]):
                                            self.results["test_commands"].append({
                                                "command": command,
                                                "evidence": f".github/workflows/{workflow_file.name}",
                                                "file": str(workflow_file.relative_to(self.repo_path))
                                            })
                                        elif any(keyword in step_name.lower() for keyword in ["run", "start"]):
                                            self.results["run_commands"].append({
                                                "command": command,
                                                "evidence": f".github/workflows/{workflow_file.name}",
                                                "file": str(workflow_file.relative_to(self.repo_path))
                                            })
                except:
                    pass


