"""
ExecutionOrderAnalyzer: Multi-Entry Program Execution Order Analyzer

Analyzes multiple independently executable entry programs in a project,
inferring execution order through data flow analysis.
Supported Languages: Python, Java, C, C++, Go, JavaScript/TypeScript
"""

import re
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from collections import deque

from logger import get_logger

logger = get_logger("execution_analyzer")


@dataclass
class EntryPoint:
    """Entry Point"""
    file_path: str          # Relative path
    language: str           # python/java/c/cpp/go/javascript/typescript/shell
    entry_type: str         # Entry type: python_main, java_main, c_main, etc.


@dataclass
class FileIO:
    """File Input/Output"""
    inputs: List[str] = field(default_factory=list)   # Files read
    outputs: List[str] = field(default_factory=list)  # Files written


@dataclass
class ExecutionOrderResult:
    """Analysis Result (No Confidence Score)"""
    entry_points: List[Dict]           # Entry point list
    data_flow: Dict[str, Dict]         # Data flow information
    dependency_graph: Dict[str, List]  # Dependency graph
    suggested_order: List[str]         # Order based on data flow
    naming_order: List[str]            # Order based on naming patterns
    
    def to_dict(self) -> Dict:
        """Convert to a dictionary."""
        return {
            "entry_points": self.entry_points,
            "data_flow": self.data_flow,
            "dependency_graph": self.dependency_graph,
            "suggested_order": self.suggested_order,
            "naming_order": self.naming_order,
        }


class ExecutionOrderAnalyzer:
    """Analyze execution order of multi-entry programs"""
    
    # Skip directory and file patterns
    SKIP_PATTERNS = [
        r'test_.*\.py$',
        r'.*_test\.py$',
        r'__init__\.py$',
        r'setup\.py$',
        r'conftest\.py$',
        r'/tests?/',
        r'/examples?/',
        r'/docs?/',
        r'node_modules/',
        r'\.git/',
        r'__pycache__/',
        r'/venv/',
        r'/\.venv/',
        r'/env/',
    ]
    
    # Data file extensions
    DATA_EXTENSIONS = {
        '.csv', '.pkl', '.pickle', '.json', '.jsonl',
        '.parquet', '.h5', '.hdf5', '.npy', '.npz',
        '.txt', '.tsv', '.xlsx', '.xls',
        '.pt', '.pth', '.ckpt', '.model', '.weights',
        '.png', '.jpg', '.jpeg', '.gif', '.bmp',
        '.db', '.sqlite', '.sqlite3',
        '.xml', '.yaml', '.yml',
        '.bin', '.dat',
    }
    
    def __init__(self, repo_path: Path):
        self.repo_path = Path(repo_path)
        self.entry_points: List[EntryPoint] = []
        self.data_flow: Dict[str, FileIO] = {}
        self.dependency_graph: Dict[str, List[str]] = {}
    
    def analyze(self) -> ExecutionOrderResult:
        """Main analysis flow"""
        logger.info(f"Starting execution order analysis: {self.repo_path}")
        
        # Step 1: Discover entry points
        self.entry_points = self._find_entry_points()
        logger.info(f"Found {len(self.entry_points)} entry point(s)")
        
        # Single or zero entry points: return immediately
        if len(self.entry_points) <= 1:
            logger.info("Only one or zero entry points; no ordering needed")
            order = [e.file_path for e in self.entry_points]
            return ExecutionOrderResult(
                entry_points=[{"file_path": e.file_path, "language": e.language, "entry_type": e.entry_type} 
                             for e in self.entry_points],
                data_flow={},
                dependency_graph={},
                suggested_order=order,
                naming_order=order,
            )
        
        # Step 2: Analyze data flow for each entry
        for entry in self.entry_points:
            # Skip special entries (npm:xxx, make:xxx)
            if entry.file_path.startswith(("npm:", "make:")):
                continue
            file_path = self.repo_path / entry.file_path
            if file_path.exists():
                self.data_flow[entry.file_path] = self._extract_file_io(file_path, entry.language)
        
        logger.info(f"Data flow analysis completed, analyzed {len(self.data_flow)} files")
        
        # Step 3: Build dependency graph
        self.dependency_graph = self._build_dependency_graph()
        
        # Step 4: Topological sort
        suggested_order = self._topological_sort(self.dependency_graph)
        
        # Step 5: Naming-pattern hints
        naming_order = self._analyze_naming_patterns()
        
        # Build result
        result = ExecutionOrderResult(
            entry_points=[{"file_path": e.file_path, "language": e.language, "entry_type": e.entry_type} 
                         for e in self.entry_points],
            data_flow={k: {"inputs": v.inputs, "outputs": v.outputs} for k, v in self.data_flow.items()},
            dependency_graph=self.dependency_graph,
            suggested_order=suggested_order,
            naming_order=naming_order,
        )
        
        logger.info(f"Execution order analysis completed, suggested order: {suggested_order}")
        return result
    
    def _should_skip(self, file_path: Path) -> bool:
        """Return whether this path should be skipped."""
        path_str = str(file_path)
        return any(re.search(p, path_str) for p in self.SKIP_PATTERNS)
    
    def _find_entry_points(self) -> List[EntryPoint]:
        """Identify entry points for all languages"""
        entry_points = []
        
        # === Python ===
        for f in self.repo_path.rglob("*.py"):
            if self._should_skip(f):
                continue
            try:
                content = f.read_text(encoding='utf-8', errors='ignore')
                if re.search(r'if\s+__name__\s*==\s*["\']__main__["\']', content):
                    entry_points.append(EntryPoint(
                        file_path=str(f.relative_to(self.repo_path)),
                        language="python",
                        entry_type="python_main"
                    ))
            except Exception as e:
                logger.debug(f"Failed to read {f}: {e}")
        
        # === Java ===
        for f in self.repo_path.rglob("*.java"):
            if self._should_skip(f):
                continue
            try:
                content = f.read_text(encoding='utf-8', errors='ignore')
                if re.search(r'public\s+static\s+void\s+main\s*\(\s*String', content):
                    entry_points.append(EntryPoint(
                        file_path=str(f.relative_to(self.repo_path)),
                        language="java",
                        entry_type="java_main"
                    ))
            except Exception as e:
                logger.debug(f"Failed to read {f}: {e}")
        
        # === C ===
        for f in self.repo_path.rglob("*.c"):
            if self._should_skip(f):
                continue
            try:
                content = f.read_text(encoding='utf-8', errors='ignore')
                if re.search(r'(int|void)\s+main\s*\(', content):
                    entry_points.append(EntryPoint(
                        file_path=str(f.relative_to(self.repo_path)),
                        language="c",
                        entry_type="c_main"
                    ))
            except Exception as e:
                logger.debug(f"Failed to read {f}: {e}")
        
        # === C++ ===
        for ext in ["*.cpp", "*.cc", "*.cxx"]:
            for f in self.repo_path.rglob(ext):
                if self._should_skip(f):
                    continue
                try:
                    content = f.read_text(encoding='utf-8', errors='ignore')
                    if re.search(r'(int|void)\s+main\s*\(', content):
                        entry_points.append(EntryPoint(
                            file_path=str(f.relative_to(self.repo_path)),
                            language="cpp",
                            entry_type="cpp_main"
                        ))
                except Exception as e:
                    logger.debug(f"Failed to read {f}: {e}")
        
        # === Go ===
        for f in self.repo_path.rglob("*.go"):
            if self._should_skip(f):
                continue
            try:
                content = f.read_text(encoding='utf-8', errors='ignore')
                if re.search(r'package\s+main', content) and re.search(r'func\s+main\s*\(\s*\)', content):
                    entry_points.append(EntryPoint(
                        file_path=str(f.relative_to(self.repo_path)),
                        language="go",
                        entry_type="go_main"
                    ))
            except Exception as e:
                logger.debug(f"Failed to read {f}: {e}")
        
        # === JavaScript/TypeScript - package.json scripts ===
        package_json = self.repo_path / "package.json"
        if package_json.exists():
            try:
                pkg = json.loads(package_json.read_text(encoding='utf-8'))
                scripts = pkg.get("scripts", {})
                # Only record scripts that may be entry points
                entry_scripts = ["start", "dev", "build", "serve", "main", 
                               "preprocess", "train", "test", "lint"]
                for name in scripts.keys():
                    if name in entry_scripts or any(kw in name.lower() for kw in 
                        ["start", "run", "build", "serve", "process", "train", "eval"]):
                        entry_points.append(EntryPoint(
                            file_path=f"npm:{name}",
                            language="javascript",
                            entry_type="npm_script"
                        ))
            except Exception as e:
                logger.debug(f"Failed to parse package.json: {e}")
        
        # === JavaScript/TypeScript - standalone entry files ===
        js_entry_names = ["index.js", "index.ts", "main.js", "main.ts", 
                         "app.js", "app.ts", "server.js", "server.ts"]
        for ext in ["*.js", "*.ts", "*.mjs"]:
            for f in self.repo_path.rglob(ext):
                if self._should_skip(f):
                    continue
                if f.name in js_entry_names:
                    entry_points.append(EntryPoint(
                        file_path=str(f.relative_to(self.repo_path)),
                        language="typescript" if f.suffix == ".ts" else "javascript",
                        entry_type="js_entry"
                    ))
        
        # === Shell scripts ===
        for f in self.repo_path.rglob("*.sh"):
            if self._should_skip(f):
                continue
            # Only include shell scripts that look like entry points
            name_lower = f.name.lower()
            if any(kw in name_lower for kw in 
                   ["run", "start", "setup", "install", "deploy", "build", "train", "process"]):
                entry_points.append(EntryPoint(
                    file_path=str(f.relative_to(self.repo_path)),
                    language="shell",
                    entry_type="shell_script"
                ))
        
        # === Makefile targets ===
        makefile = self.repo_path / "Makefile"
        if makefile.exists():
            try:
                targets = self._parse_makefile_targets(makefile)
                for target in targets:
                    entry_points.append(EntryPoint(
                        file_path=f"make:{target}",
                        language="makefile",
                        entry_type="make_target"
                    ))
            except Exception as e:
                logger.debug(f"Failed to parse Makefile: {e}")
        
        return entry_points
    
    def _parse_makefile_targets(self, makefile: Path) -> List[str]:
        """Parse primary targets from a Makefile."""
        content = makefile.read_text(encoding='utf-8', errors='ignore')
        targets = []
        
        # Match target: dependencies lines
        pattern = r'^([a-zA-Z_][a-zA-Z0-9_-]*):'
        for match in re.finditer(pattern, content, re.MULTILINE):
            target = match.group(1)
            # Only include common entry targets
            if target in ["all", "build", "run", "install", "clean", "test", 
                         "deploy", "start", "train", "process", "setup"]:
                targets.append(target)
        
        return targets
    
    def _extract_file_io(self, file_path: Path, language: str) -> FileIO:
        """Extract file I/O by language."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            logger.debug(f"Failed to read {file_path}: {e}")
            return FileIO()
        
        if language == "python":
            return self._extract_python_io(content)
        elif language == "java":
            return self._extract_java_io(content)
        elif language == "c":
            return self._extract_c_io(content)
        elif language == "cpp":
            return self._extract_cpp_io(content)
        elif language == "go":
            return self._extract_go_io(content)
        elif language in ["javascript", "typescript"]:
            return self._extract_js_io(content)
        else:
            return FileIO()
    
    def _extract_python_io(self, code: str) -> FileIO:
        """Extract Python file I/O"""
        inputs, outputs = [], []
        
        # Read patterns
        read_patterns = [
            r'open\s*\(\s*["\']([^"\']+)["\'].*?["\']r',
            r'open\s*\(\s*["\']([^"\']+)["\']\s*\)',  # default read mode
            r'pd\.read_csv\s*\(\s*["\']([^"\']+)["\']',
            r'pd\.read_pickle\s*\(\s*["\']([^"\']+)["\']',
            r'pd\.read_json\s*\(\s*["\']([^"\']+)["\']',
            r'pd\.read_excel\s*\(\s*["\']([^"\']+)["\']',
            r'pd\.read_parquet\s*\(\s*["\']([^"\']+)["\']',
            r'pd\.read_feather\s*\(\s*["\']([^"\']+)["\']',
            r'pd\.read_hdf\s*\(\s*["\']([^"\']+)["\']',
            r'json\.load\s*\(.*?open\s*\(\s*["\']([^"\']+)["\']',
            r'pickle\.load\s*\(.*?open\s*\(\s*["\']([^"\']+)["\']',
            r'joblib\.load\s*\(\s*["\']([^"\']+)["\']',
            r'torch\.load\s*\(\s*["\']([^"\']+)["\']',
            r'np\.load\s*\(\s*["\']([^"\']+)["\']',
            r'np\.loadtxt\s*\(\s*["\']([^"\']+)["\']',
            r'np\.genfromtxt\s*\(\s*["\']([^"\']+)["\']',
            r'cv2\.imread\s*\(\s*["\']([^"\']+)["\']',
            r'Image\.open\s*\(\s*["\']([^"\']+)["\']',
            r'yaml\.safe_load\s*\(.*?open\s*\(\s*["\']([^"\']+)["\']',
            r'yaml\.load\s*\(.*?open\s*\(\s*["\']([^"\']+)["\']',
            r'toml\.load\s*\(\s*["\']([^"\']+)["\']',
            r'sqlite3\.connect\s*\(\s*["\']([^"\']+)["\']',
            r'h5py\.File\s*\(\s*["\']([^"\']+)["\']\s*,\s*["\']r',
        ]
        
        # Write patterns
        write_patterns = [
            r'open\s*\(\s*["\']([^"\']+)["\'].*?["\']w',
            r'open\s*\(\s*["\']([^"\']+)["\'].*?["\']a',  # append mode
            r'\.to_csv\s*\(\s*["\']([^"\']+)["\']',
            r'\.to_pickle\s*\(\s*["\']([^"\']+)["\']',
            r'\.to_json\s*\(\s*["\']([^"\']+)["\']',
            r'\.to_excel\s*\(\s*["\']([^"\']+)["\']',
            r'\.to_parquet\s*\(\s*["\']([^"\']+)["\']',
            r'\.to_feather\s*\(\s*["\']([^"\']+)["\']',
            r'\.to_hdf\s*\(\s*["\']([^"\']+)["\']',
            r'json\.dump\s*\([^,]+,\s*open\s*\(\s*["\']([^"\']+)["\']',
            r'pickle\.dump\s*\([^,]+,\s*open\s*\(\s*["\']([^"\']+)["\']',
            r'joblib\.dump\s*\([^,]+,\s*["\']([^"\']+)["\']',
            r'torch\.save\s*\([^,]+,\s*["\']([^"\']+)["\']',
            r'np\.save\s*\(\s*["\']([^"\']+)["\']',
            r'np\.savetxt\s*\(\s*["\']([^"\']+)["\']',
            r'cv2\.imwrite\s*\(\s*["\']([^"\']+)["\']',
            r'\.save\s*\(\s*["\']([^"\']+)["\']',
            r'h5py\.File\s*\(\s*["\']([^"\']+)["\']\s*,\s*["\']w',
        ]
        
        for pattern in read_patterns:
            for match in re.findall(pattern, code):
                if self._is_data_file(match):
                    inputs.append(match)
        for pattern in write_patterns:
            for match in re.findall(pattern, code):
                if self._is_data_file(match):
                    outputs.append(match)
        
        return FileIO(inputs=list(set(inputs)), outputs=list(set(outputs)))
    
    def _extract_java_io(self, code: str) -> FileIO:
        """Extract Java file I/O"""
        inputs, outputs = [], []
        
        read_patterns = [
            r'new\s+FileReader\s*\(\s*["\']([^"\']+)["\']',
            r'new\s+FileInputStream\s*\(\s*["\']([^"\']+)["\']',
            r'new\s+BufferedReader\s*\(.*?["\']([^"\']+)["\']',
            r'Files\.readAllLines\s*\(\s*Paths\.get\s*\(\s*["\']([^"\']+)["\']',
            r'Files\.readString\s*\(\s*Paths\.get\s*\(\s*["\']([^"\']+)["\']',
            r'Files\.readAllBytes\s*\(\s*Paths\.get\s*\(\s*["\']([^"\']+)["\']',
            r'new\s+Scanner\s*\(\s*new\s+File\s*\(\s*["\']([^"\']+)["\']',
            r'ObjectInputStream.*?FileInputStream\s*\(\s*["\']([^"\']+)["\']',
            r'getResourceAsStream\s*\(\s*["\']([^"\']+)["\']',
            r'new\s+File\s*\(\s*["\']([^"\']+)["\'].*?\.exists\s*\(\)',
        ]
        
        write_patterns = [
            r'new\s+FileWriter\s*\(\s*["\']([^"\']+)["\']',
            r'new\s+FileOutputStream\s*\(\s*["\']([^"\']+)["\']',
            r'new\s+PrintWriter\s*\(\s*["\']([^"\']+)["\']',
            r'new\s+BufferedWriter\s*\(.*?["\']([^"\']+)["\']',
            r'Files\.write\s*\(\s*Paths\.get\s*\(\s*["\']([^"\']+)["\']',
            r'Files\.writeString\s*\(\s*Paths\.get\s*\(\s*["\']([^"\']+)["\']',
            r'ObjectOutputStream.*?FileOutputStream\s*\(\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in read_patterns:
            for match in re.findall(pattern, code):
                if self._is_data_file(match):
                    inputs.append(match)
        for pattern in write_patterns:
            for match in re.findall(pattern, code):
                if self._is_data_file(match):
                    outputs.append(match)
        
        return FileIO(inputs=list(set(inputs)), outputs=list(set(outputs)))
    
    def _extract_c_io(self, code: str) -> FileIO:
        """Extract C file I/O"""
        inputs, outputs = [], []
        
        read_patterns = [
            r'fopen\s*\(\s*["\']([^"\']+)["\']\s*,\s*["\']r[b]?["\']',
            r'freopen\s*\(\s*["\']([^"\']+)["\']\s*,\s*["\']r',
        ]
        
        write_patterns = [
            r'fopen\s*\(\s*["\']([^"\']+)["\']\s*,\s*["\']w[b]?["\']',
            r'fopen\s*\(\s*["\']([^"\']+)["\']\s*,\s*["\']a[b]?["\']',
            r'freopen\s*\(\s*["\']([^"\']+)["\']\s*,\s*["\']w',
        ]
        
        for pattern in read_patterns:
            for match in re.findall(pattern, code):
                if self._is_data_file(match):
                    inputs.append(match)
        for pattern in write_patterns:
            for match in re.findall(pattern, code):
                if self._is_data_file(match):
                    outputs.append(match)
        
        return FileIO(inputs=list(set(inputs)), outputs=list(set(outputs)))
    
    def _extract_cpp_io(self, code: str) -> FileIO:
        """Extract C++ file I/O."""
        inputs, outputs = [], []
        
        read_patterns = [
            r'ifstream\s+\w+\s*\(\s*["\']([^"\']+)["\']',
            r'ifstream\s+\w+\s*;\s*\w+\.open\s*\(\s*["\']([^"\']+)["\']',
            r'fstream\s+\w+\s*\(\s*["\']([^"\']+)["\']\s*,\s*ios::in',
            r'fopen\s*\(\s*["\']([^"\']+)["\']\s*,\s*["\']r',
        ]
        
        write_patterns = [
            r'ofstream\s+\w+\s*\(\s*["\']([^"\']+)["\']',
            r'ofstream\s+\w+\s*;\s*\w+\.open\s*\(\s*["\']([^"\']+)["\']',
            r'fstream\s+\w+\s*\(\s*["\']([^"\']+)["\']\s*,\s*ios::out',
            r'fopen\s*\(\s*["\']([^"\']+)["\']\s*,\s*["\']w',
        ]
        
        for pattern in read_patterns:
            for match in re.findall(pattern, code):
                if self._is_data_file(match):
                    inputs.append(match)
        for pattern in write_patterns:
            for match in re.findall(pattern, code):
                if self._is_data_file(match):
                    outputs.append(match)
        
        return FileIO(inputs=list(set(inputs)), outputs=list(set(outputs)))
    
    def _extract_go_io(self, code: str) -> FileIO:
        """Extract Go file I/O."""
        inputs, outputs = [], []
        
        read_patterns = [
            r'os\.Open\s*\(\s*["\']([^"\']+)["\']',
            r'os\.ReadFile\s*\(\s*["\']([^"\']+)["\']',
            r'ioutil\.ReadFile\s*\(\s*["\']([^"\']+)["\']',
            r'bufio\.NewReader.*?os\.Open\s*\(\s*["\']([^"\']+)["\']',
            r'json\.NewDecoder.*?os\.Open\s*\(\s*["\']([^"\']+)["\']',
        ]
        
        write_patterns = [
            r'os\.Create\s*\(\s*["\']([^"\']+)["\']',
            r'os\.WriteFile\s*\(\s*["\']([^"\']+)["\']',
            r'ioutil\.WriteFile\s*\(\s*["\']([^"\']+)["\']',
            r'os\.OpenFile\s*\(\s*["\']([^"\']+)["\']\s*,\s*os\.O_',
        ]
        
        for pattern in read_patterns:
            for match in re.findall(pattern, code):
                if self._is_data_file(match):
                    inputs.append(match)
        for pattern in write_patterns:
            for match in re.findall(pattern, code):
                if self._is_data_file(match):
                    outputs.append(match)
        
        return FileIO(inputs=list(set(inputs)), outputs=list(set(outputs)))
    
    def _extract_js_io(self, code: str) -> FileIO:
        """Extract JavaScript/TypeScript file I/O"""
        inputs, outputs = [], []
        
        read_patterns = [
            r'fs\.readFileSync\s*\(\s*["\']([^"\']+)["\']',
            r'fs\.readFile\s*\(\s*["\']([^"\']+)["\']',
            r'fs\.promises\.readFile\s*\(\s*["\']([^"\']+)["\']',
            r'require\s*\(\s*["\']([^"\']+\.json)["\']',
            r'fetch\s*\(\s*["\']file://([^"\']+)["\']',
            r'readJSON\s*\(\s*["\']([^"\']+)["\']',
        ]
        
        write_patterns = [
            r'fs\.writeFileSync\s*\(\s*["\']([^"\']+)["\']',
            r'fs\.writeFile\s*\(\s*["\']([^"\']+)["\']',
            r'fs\.promises\.writeFile\s*\(\s*["\']([^"\']+)["\']',
            r'fs\.appendFileSync\s*\(\s*["\']([^"\']+)["\']',
            r'fs\.createWriteStream\s*\(\s*["\']([^"\']+)["\']',
            r'writeJSON\s*\(\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in read_patterns:
            for match in re.findall(pattern, code):
                if self._is_data_file(match):
                    inputs.append(match)
        for pattern in write_patterns:
            for match in re.findall(pattern, code):
                if self._is_data_file(match):
                    outputs.append(match)
        
        return FileIO(inputs=list(set(inputs)), outputs=list(set(outputs)))
    
    def _is_data_file(self, file_path: str) -> bool:
        """Determine if file is a data file"""
        # Exclude config files and code files
        exclude_patterns = [
            r'config\.',
            r'settings\.',
            r'\.env',
            r'requirements\.txt',
            r'package\.json',
            r'\.py$',
            r'\.js$',
            r'\.ts$',
            r'\.java$',
            r'\.go$',
            r'\.c$',
            r'\.cpp$',
            r'\.h$',
        ]
        
        for pattern in exclude_patterns:
            if re.search(pattern, file_path, re.IGNORECASE):
                return False
        
        # Check extension
        ext = Path(file_path).suffix.lower()
        if ext in self.DATA_EXTENSIONS:
            return True
        
        # No extension but path looks like data file
        if not ext and any(kw in file_path.lower() for kw in 
                          ['data', 'model', 'output', 'result', 'cache']):
            return True
        
        return False
    
    def _build_dependency_graph(self) -> Dict[str, List[str]]:
        """Build dependency graph: A's output = B's input implies B depends on A."""
        # Initialize graph
        graph = {}
        for entry in self.entry_points:
            if not entry.file_path.startswith(("npm:", "make:")):
                graph[entry.file_path] = []
        
        # Output file → producer mapping
        output_to_producer = {}
        for file_path, file_io in self.data_flow.items():
            for output_file in file_io.outputs:
                normalized = self._normalize_filename(output_file)
                output_to_producer[normalized] = file_path
        
        # Establish dependencies
        for file_path, file_io in self.data_flow.items():
            if file_path not in graph:
                continue
            for input_file in file_io.inputs:
                normalized = self._normalize_filename(input_file)
                if normalized in output_to_producer:
                    producer = output_to_producer[normalized]
                    if producer != file_path and producer not in graph[file_path]:
                        graph[file_path].append(producer)
                        logger.debug(f"Found dependency: {file_path} depends on {producer} (via {input_file})")
        
        return graph
    
    def _normalize_filename(self, path: str) -> str:
        """Normalize filename for matching"""
        # Keep only filename, ignore directory
        return Path(path).name.lower()
    
    def _topological_sort(self, graph: Dict[str, List[str]]) -> List[str]:
        """Topological sort."""
        if not graph:
            return []
        
        # Calculate in-degree
        in_degree = {node: len(deps) for node, deps in graph.items()}
        
        # Nodes with in-degree zero
        queue = [n for n in in_degree if in_degree[n] == 0]
        result = []
        
        while queue:
            # Stable sort
            queue.sort()
            current = queue.pop(0)
            result.append(current)
            
            # Update nodes that depend on it
            for node, deps in graph.items():
                if current in deps:
                    in_degree[node] -= 1
                    if in_degree[node] == 0:
                        queue.append(node)
        
        # Append unsorted to end (possible circular dependency)
        remaining = [n for n in graph if n not in result]
        if remaining:
            logger.warning(f"Possible circular dependency detected, following files cannot be sorted: {remaining}")
            result.extend(sorted(remaining))
        
        return result
    
    def _analyze_naming_patterns(self) -> List[str]:
        """Sort based on naming patterns"""
        files = [e.file_path for e in self.entry_points 
                 if not e.file_path.startswith(("npm:", "make:"))]
        
        if not files:
            return []
        
        # Numeric prefix sort
        def get_number_prefix(f):
            match = re.match(r'^.*?(\d+)[_\-\.]', Path(f).name)
            return int(match.group(1)) if match else 999
        
        if all(get_number_prefix(f) != 999 for f in files):
            return sorted(files, key=get_number_prefix)
        
        # Stage keyword sort
        stage_keywords = [
            ['setup', 'init', 'install', 'config', 'prepare', 'bootstrap', 'create'],
            ['download', 'fetch', 'collect', 'crawl', 'scrape', 'extract', 'get'],
            ['preprocess', 'clean', 'transform', 'parse', 'convert', 'prepare_data'],
            ['train', 'fit', 'learn', 'build', 'process', 'main', 'run', 'execute'],
            ['eval', 'evaluate', 'test', 'validate', 'verify', 'check', 'score'],
            ['predict', 'infer', 'serve', 'deploy', 'export', 'output', 'generate'],
            ['visualize', 'plot', 'report', 'analyze', 'summary', 'show'],
            ['cleanup', 'finalize', 'archive', 'backup', 'post'],
        ]
        
        def get_stage(file_path):
            name = Path(file_path).stem.lower()
            for i, keywords in enumerate(stage_keywords):
                if any(kw in name for kw in keywords):
                    return i
            return 50  # Unknown stage goes in middle
        
        return sorted(files, key=lambda f: (get_stage(f), f))


def format_for_analyzer(result: ExecutionOrderResult) -> str:
    """Format as supplementary information readable by Analyzer.

    Design Principles:
    1. As supplementary info, does not affect existing flow
    2. Only output when multiple entry points exist
    3. Provide objective data, no subjective judgments
    """
    
    # Only single or no entry points, output nothing
    if len(result.entry_points) <= 1:
        return ""
    
    lines = []
    lines.append("=" * 60)
    lines.append("Multi-Entry Program Analysis (Supplementary Information)")
    lines.append("=" * 60)
    lines.append("")
    
    # 1. Entry point list
    lines.append("### Identified Program Entry Points")
    for entry in result.entry_points:
        lines.append(f"- {entry['file_path']} ({entry['language']}, {entry['entry_type']})")
    lines.append("")
    
    # 2. Data flow info (if any)
    has_data_flow = any(
        io.get('inputs') or io.get('outputs') 
        for io in result.data_flow.values()
    )
    
    if has_data_flow:
        lines.append("### Data Flow Analysis")
        for file_path, io in result.data_flow.items():
            if io.get('inputs') or io.get('outputs'):
                inputs_str = ', '.join(io.get('inputs', [])) or 'None'
                outputs_str = ', '.join(io.get('outputs', [])) or 'None'
                lines.append(f"- {file_path}")
                lines.append(f"  - Reads: {inputs_str}")
                lines.append(f"  - Outputs: {outputs_str}")
        lines.append("")
    
    # 3. Dependencies (if any)
    has_dependencies = any(deps for deps in result.dependency_graph.values())
    
    if has_dependencies:
        lines.append("### Dependencies")
        for file_path, deps in result.dependency_graph.items():
            if deps:
                deps_str = ', '.join(deps)
                lines.append(f"- {file_path} depends on: {deps_str}")
        lines.append("")
    
    # 4. Order suggestions
    lines.append("### Execution Order Reference")
    
    if result.suggested_order:
        lines.append("Based on data flow analysis:")
        for i, f in enumerate(result.suggested_order, 1):
            lines.append(f"  {i}. {f}")
    
    if result.naming_order and result.naming_order != result.suggested_order:
        lines.append("")
        lines.append("Based on naming patterns:")
        for i, f in enumerate(result.naming_order, 1):
            lines.append(f"  {i}. {f}")
    
    lines.append("")
    lines.append("Please use the correct execution order in README deployment steps based on above analysis.")
    lines.append("If project has multiple independent execution flows, explain each flow's steps separately.")
    lines.append("")
    
    return '\n'.join(lines)


# Backward compatibility (deprecated name)
format_for_agent3 = format_for_analyzer


