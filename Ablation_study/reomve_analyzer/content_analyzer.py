"""
Content-level code analyzer — deep analysis of code content to extract deployment information.
Cost optimization: analyze only code snippets related to deployment.
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import json


class ContentAnalyzer:
    """Code content analyzer (base class)."""
    
    # File size limit (avoid analyzing overly large files)
    MAX_FILE_SIZE = 200 * 1024  # 200KB
    MAX_LINES = 1500  # Analyze at most 1500 lines
    
    def __init__(self):
        self.python_analyzer = PythonContentAnalyzer()
        self.javascript_analyzer = JavaScriptContentAnalyzer()
        self.go_analyzer = GoContentAnalyzer()
        self.java_analyzer = JavaContentAnalyzer()
        self.c_analyzer = CContentAnalyzer()
        self.cpp_analyzer = CppContentAnalyzer()
        self.config_analyzer = ConfigFileAnalyzer()
    
    def analyze_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Analyze a single file."""
        if not self._should_analyze(file_path):
            return None
        
        # Choose analyzer by file extension or filename
        suffix = file_path.suffix.lower()
        filename = file_path.name.lower()
        
        if suffix == '.py':
            return self.python_analyzer.analyze(file_path)
        elif suffix in ['.js', '.ts', '.jsx', '.tsx']:
            return self.javascript_analyzer.analyze(file_path)
        elif suffix == '.go':
            return self.go_analyzer.analyze(file_path)
        elif suffix == '.java':
            return self.java_analyzer.analyze(file_path)
        elif suffix == '.c':
            return self.c_analyzer.analyze(file_path)
        elif suffix in ['.cpp', '.cc', '.cxx', '.hpp', '.h']:
            return self.cpp_analyzer.analyze(file_path)
        # Config file support
        elif suffix in ['.gradle', '.properties', '.yml', '.yaml', '.xml', '.toml', '.json']:
            return self.config_analyzer.analyze(file_path)
        elif filename in ['makefile', 'cmakelists.txt', 'dockerfile', 'docker-compose.yml', 'docker-compose.yaml']:
            return self.config_analyzer.analyze(file_path)
        
        return None
    
    def _should_analyze(self, file_path: Path) -> bool:
        """Determine whether this file should be analyzed."""
        try:
            # 1. Check file size
            if file_path.stat().st_size > self.MAX_FILE_SIZE:
                return False
            
            # 2. Skip binary and generated artifacts
            # Match by directory name so we do not exclude files like build.gradle
            excluded_dirs = [
                '__pycache__', 'node_modules', '.git',
                'dist', '.egg-info',
                'venv', '.venv',
                'target',  # Maven build output
                '.gradle',  # Gradle cache directory
            ]
            
            # Check directory components of the path
            path_parts = file_path.parts
            for part in path_parts[:-1]:  # Exclude the filename itself
                if part in excluded_dirs:
                    return False
                # Special case: exclude only directories named "build", not build.gradle
                if part == 'build' and part != file_path.name:
                    return False
                # Exclude virtualenv-style dirs (exact "env" or names ending with _env / -env)
                if part == 'env' or part.endswith('_env') or part.endswith('-env'):
                    return False
            
            # 3. Skip test files (but keep config files)
            filename = file_path.name
            if filename.startswith('test_') or '_test.' in filename or '.spec.' in filename:
                # Do not skip test config files
                if not filename.endswith(('.yml', '.yaml', '.properties', '.xml', '.json')):
                    return False
            
            return True
        except:
            return False
    
    def _read_file_safe(self, file_path: Path) -> Optional[str]:
        """Read file safely (handles encoding issues)."""
        try:
            return file_path.read_text(encoding='utf-8', errors='ignore')
        except:
            return None


class PythonContentAnalyzer:
    """Python code content analyzer."""
    
    def analyze(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a Python file."""
        try:
            code = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # If the file is too large, analyze only the leading portion
            lines = code.split('\n')
            if len(lines) > 1500:
                code = '\n'.join(self._smart_sample(lines))
            
            return {
                "file": str(file_path),
                "language": "Python",
                "imports": self._extract_imports(code),
                "main_block": self._extract_main_block(code),
                "cli_params": self._extract_cli_params(code),
                "env_vars": self._extract_env_vars(code),
                "service_init": self._extract_service_init(code),
                "config_vars": self._extract_config_vars(code),
                "frameworks": self._detect_frameworks(code)
            }
        except Exception as e:
            return {"error": str(e), "file": str(file_path)}
    
    def _smart_sample(self, lines: List[str]) -> List[str]:
        """Smart sampling of salient code lines."""
        sampled = []
        
        # 1. First 100 lines (imports and initialization)
        sampled.extend(lines[:100])
        
        # 2. Find if __name__ == "__main__" block
        for i, line in enumerate(lines):
            if '__name__' in line and '__main__' in line:
                sampled.extend(lines[i:min(i+100, len(lines))])
                break
        
        # 3. Find config classes
        for i, line in enumerate(lines):
            if re.match(r'\s*class\s+\w*[Cc]onfig\w*', line):
                sampled.extend(lines[i:min(i+50, len(lines))])
        
        # 4. Find main function
        for i, line in enumerate(lines):
            if re.match(r'\s*def\s+main\s*\(', line):
                sampled.extend(lines[i:min(i+50, len(lines))])
        
        return sampled
    
    def _extract_imports(self, code: str) -> List[Dict]:
        """Extract import statements."""
        imports = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append({
                            "module": alias.name,
                            "alias": alias.asname,
                            "type": "import"
                        })
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append({
                            "module": node.module,
                            "names": [n.name for n in node.names] if node.names else [],
                            "type": "from"
                        })
        except:
            # If AST parsing fails, fall back to regex
            import_pattern = r'^\s*(?:from\s+([\w\.]+)\s+)?import\s+([\w\s,\.]+)'
            for match in re.finditer(import_pattern, code, re.MULTILINE):
                imports.append({
                    "module": match.group(1) or match.group(2),
                    "type": "regex"
                })
        
        return imports
    
    def _extract_main_block(self, code: str) -> Optional[Dict]:
        """Extract if __name__ == '__main__' block."""
        pattern = r'if\s+__name__\s*==\s*["\']__main__["\']\s*:\s*\n((?:[ \t]+.+\n)+)'
        match = re.search(pattern, code)
        
        if match:
            block_content = match.group(1)
            return {
                "content": block_content[:500],  # Truncate length
                "has_app_run": 'app.run' in block_content or '.run(' in block_content,
                "has_uvicorn": 'uvicorn' in block_content.lower(),
                "has_cli": any(x in block_content for x in ['argparse', 'click', 'typer'])
            }
        
        return None
    
    def _extract_cli_params(self, code: str) -> List[Dict]:
        """Extract CLI parameters."""
        params = []
        
        # 1. argparse
        argparse_pattern = r'\.add_argument\(["\']([^"\']+)["\'].*?(?:default=([^,\)]+))?'
        for match in re.finditer(argparse_pattern, code):
            params.append({
                "name": match.group(1),
                "default": match.group(2).strip() if match.group(2) else None,
                "framework": "argparse"
            })
        
        # 2. click
        click_pattern = r'@click\.option\(["\']([^"\']+)["\'].*?(?:default=([^,\)]+))?'
        for match in re.finditer(click_pattern, code):
            params.append({
                "name": match.group(1),
                "default": match.group(2).strip() if match.group(2) else None,
                "framework": "click"
            })
        
        return params
    
    def _extract_env_vars(self, code: str) -> List[Dict]:
        """Extract environment variables."""
        env_vars = []
        seen = set()
        
        # Match common patterns for reading environment variables
        patterns = [
            # os.getenv("VAR", "default")
            r'os\.getenv\(["\'](\w+)["\'](?:\s*,\s*["\']([^"\']*)["\'])?\)',
            # os.environ.get("VAR", "default")
            r'os\.environ\.get\(["\'](\w+)["\'](?:\s*,\s*["\']([^"\']*)["\'])?\)',
            # os.environ["VAR"]
            r'os\.environ\[["\'](\w+)["\']\]',
            # env("VAR", default="value")
            r'env\(["\'](\w+)["\'](?:.*?default=["\']([^"\']*)["\'])?\)',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, code):
                var_name = match.group(1)
                if var_name not in seen:
                    seen.add(var_name)
                    default = match.group(2) if len(match.groups()) > 1 else None
                    env_vars.append({
                        "name": var_name,
                        "default": default,
                        "required": default is None or default == ""
                    })
        
        return env_vars
    
    def _extract_service_init(self, code: str) -> List[Dict]:
        """Extract service initialization (database, cache, etc.)."""
        services = []
        
        service_patterns = {
            "redis": r'redis\.Redis|Redis\(',
            "mongodb": r'MongoClient|pymongo\.MongoClient',
            "postgresql": r'psycopg2\.connect|create_engine.*postgresql',
            "mysql": r'mysql\.connector|MySQLdb|pymysql',
            "elasticsearch": r'Elasticsearch\(',
            "rabbitmq": r'pika\.BlockingConnection',
            "celery": r'Celery\('
        }
        
        for service, pattern in service_patterns.items():
            if re.search(pattern, code, re.IGNORECASE):
                services.append({
                    "service": service,
                    "detected": True
                })
        
        return services
    
    def _extract_config_vars(self, code: str) -> List[Dict]:
        """Extract config variables (Config classes)."""
        config_vars = []
        
        # Find Config classes
        class_pattern = r'class\s+\w*[Cc]onfig\w*.*?:\s*\n((?:[ \t]+.+\n)+)'
        match = re.search(class_pattern, code)
        
        if match:
            class_body = match.group(1)
            # Extract class attributes
            var_pattern = r'^\s*(\w+)\s*=\s*(.+?)(?:\s*#.*)?$'
            for var_match in re.finditer(var_pattern, class_body, re.MULTILINE):
                config_vars.append({
                    "name": var_match.group(1),
                    "value": var_match.group(2).strip()[:100]  # Truncate length
                })
        
        return config_vars
    
    def _detect_frameworks(self, code: str) -> List[str]:
        """Detect frameworks in use."""
        frameworks = []
        
        framework_patterns = {
            "Flask": r'from\s+flask\s+import|Flask\(__name__\)',
            "FastAPI": r'from\s+fastapi\s+import|FastAPI\(',
            "Django": r'from\s+django|django\.core',
            "Tornado": r'import\s+tornado|tornado\.web',
            "Sanic": r'from\s+sanic\s+import|Sanic\(',
            "Streamlit": r'import\s+streamlit|streamlit\.run',
            "Celery": r'from\s+celery\s+import|Celery\(',
            "SQLAlchemy": r'from\s+sqlalchemy\s+import|create_engine'
        }
        
        for framework, pattern in framework_patterns.items():
            if re.search(pattern, code):
                frameworks.append(framework)
        
        return frameworks


class JavaScriptContentAnalyzer:
    """JavaScript/TypeScript code content analyzer."""
    
    def analyze(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a JavaScript/TypeScript file."""
        try:
            code = file_path.read_text(encoding='utf-8', errors='ignore')
            
            return {
                "file": str(file_path),
                "language": "JavaScript/TypeScript",
                "imports": self._extract_imports(code),
                "exports": self._extract_exports(code),
                "env_vars": self._extract_env_vars(code),
                "server_port": self._extract_server_port(code),
                "frameworks": self._detect_frameworks(code)
            }
        except Exception as e:
            return {"error": str(e), "file": str(file_path)}
    
    def _extract_imports(self, code: str) -> List[Dict]:
        """Extract import/require statements."""
        imports = []
        
        # ES6 imports
        import_patterns = [
            r'import\s+(\w+)\s+from\s+["\']([^"\']+)["\']',
            r'import\s+{([^}]+)}\s+from\s+["\']([^"\']+)["\']',
            r'import\s+\*\s+as\s+(\w+)\s+from\s+["\']([^"\']+)["\']'
        ]
        
        for pattern in import_patterns:
            for match in re.finditer(pattern, code):
                imports.append({
                    "module": match.group(2) if len(match.groups()) > 1 else match.group(1),
                    "type": "es6"
                })
        
        # CommonJS requires
        require_pattern = r'(?:const|let|var)\s+(\w+)\s*=\s*require\(["\']([^"\']+)["\']\)'
        for match in re.finditer(require_pattern, code):
            imports.append({
                "module": match.group(2),
                "type": "commonjs"
            })
        
        return imports
    
    def _extract_exports(self, code: str) -> List[str]:
        """Extract export statements."""
        exports = []
        
        export_patterns = [
            r'export\s+(?:default\s+)?(?:function|class|const|let|var)\s+(\w+)',
            r'module\.exports\s*=\s*(\w+)',
        ]
        
        for pattern in export_patterns:
            for match in re.finditer(pattern, code):
                exports.append(match.group(1))
        
        return exports
    
    def _extract_env_vars(self, code: str) -> List[Dict]:
        """Extract environment variables."""
        env_vars = []
        seen = set()
        
        patterns = [
            r'process\.env\.(\w+)',
            r'env\.(\w+)',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, code):
                var_name = match.group(1)
                if var_name not in seen:
                    seen.add(var_name)
                    env_vars.append({
                        "name": var_name,
                        "required": True  # Usually treated as required in JS
                    })
        
        return env_vars
    
    def _extract_server_port(self, code: str) -> Optional[int]:
        """Extract server listen port."""
        patterns = [
            r'\.listen\((\d+)',
            r'port:\s*(\d+)',
            r'PORT\s*=\s*(\d+)',
            r'process\.env\.PORT\s*\|\|\s*(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, code)
            if match:
                try:
                    return int(match.group(1))
                except:
                    pass
        
        return None
    
    def _detect_frameworks(self, code: str) -> List[str]:
        """Detect frameworks in use."""
        frameworks = []
        
        framework_patterns = {
            "Express": r'require\(["\']express["\']\)|from\s+["\']express["\']',
            "Koa": r'require\(["\']koa["\']\)|from\s+["\']koa["\']',
            "Fastify": r'require\(["\']fastify["\']\)|from\s+["\']fastify["\']',
            "NestJS": r'@nestjs/|from\s+["\']@nestjs',
            "Next.js": r'next/|from\s+["\']next',
            "React": r'from\s+["\']react["\']',
            "Vue": r'from\s+["\']vue["\']',
        }
        
        for framework, pattern in framework_patterns.items():
            if re.search(pattern, code):
                frameworks.append(framework)
        
        return frameworks


class GoContentAnalyzer:
    """Go code content analyzer."""
    
    def analyze(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a Go file."""
        try:
            code = file_path.read_text(encoding='utf-8', errors='ignore')
            
            return {
                "file": str(file_path),
                "language": "Go",
                "imports": self._extract_imports(code),
                "main_func": self._has_main_func(code),
                "env_vars": self._extract_env_vars(code),
                "server_port": self._extract_server_port(code),
                "frameworks": self._detect_frameworks(code)
            }
        except Exception as e:
            return {"error": str(e), "file": str(file_path)}
    
    def _extract_imports(self, code: str) -> List[str]:
        """Extract import statements."""
        imports = []
        
        # Single import
        single_pattern = r'import\s+"([^"]+)"'
        for match in re.finditer(single_pattern, code):
            imports.append(match.group(1))
        
        # Multiple imports
        multi_pattern = r'import\s+\((.*?)\)'
        match = re.search(multi_pattern, code, re.DOTALL)
        if match:
            import_block = match.group(1)
            for line in import_block.split('\n'):
                pkg_match = re.search(r'"([^"]+)"', line)
                if pkg_match:
                    imports.append(pkg_match.group(1))
        
        return imports
    
    def _has_main_func(self, code: str) -> bool:
        """Check whether a main function exists."""
        return bool(re.search(r'func\s+main\s*\(\s*\)', code))
    
    def _extract_env_vars(self, code: str) -> List[Dict]:
        """Extract environment variables."""
        env_vars = []
        seen = set()
        
        pattern = r'os\.Getenv\("(\w+)"\)'
        for match in re.finditer(pattern, code):
            var_name = match.group(1)
            if var_name not in seen:
                seen.add(var_name)
                env_vars.append({
                    "name": var_name,
                    "required": True
                })
        
        return env_vars
    
    def _extract_server_port(self, code: str) -> Optional[int]:
        """Extract server port."""
        patterns = [
            r':(\d+)',  # :8080
            r'Port:\s*(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, code)
            if match:
                try:
                    return int(match.group(1))
                except:
                    pass
        
        return None
    
    def _detect_frameworks(self, code: str) -> List[str]:
        """Detect frameworks in use."""
        frameworks = []
        
        framework_patterns = {
            "Gin": r'"github\.com/gin-gonic/gin"',
            "Echo": r'"github\.com/labstack/echo"',
            "Fiber": r'"github\.com/gofiber/fiber"',
            "Chi": r'"github\.com/go-chi/chi"',
        }
        
        for framework, pattern in framework_patterns.items():
            if re.search(pattern, code):
                frameworks.append(framework)
        
        return frameworks


class JavaContentAnalyzer:
    """Java code content analyzer."""
    
    def analyze(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a Java file."""
        try:
            code = file_path.read_text(encoding='utf-8', errors='ignore')
            
            return {
                "file": str(file_path),
                "language": "Java",
                "imports": self._extract_imports(code),
                "main_method": self._has_main_method(code),
                "annotations": self._extract_annotations(code),
                "properties": self._extract_properties(code),
                "server_port": self._extract_server_port(code),
                "frameworks": self._detect_frameworks(code)
            }
        except Exception as e:
            return {"error": str(e), "file": str(file_path)}
    
    def _extract_imports(self, code: str) -> List[str]:
        """Extract import statements."""
        imports = []
        pattern = r'import\s+(?:static\s+)?([a-zA-Z0-9_.]+(?:\.\*)?);'
        
        for match in re.finditer(pattern, code):
            imports.append(match.group(1))
        
        return imports
    
    def _has_main_method(self, code: str) -> bool:
        """Check whether a main method exists."""
        pattern = r'public\s+static\s+void\s+main\s*\(\s*String\s*\[\s*\]\s+\w+\s*\)'
        return bool(re.search(pattern, code))
    
    def _extract_annotations(self, code: str) -> List[str]:
        """Extract annotations (Spring Boot, etc.)."""
        annotations = []
        pattern = r'@(\w+)(?:\([^)]*\))?'
        
        for match in re.finditer(pattern, code):
            annotation = match.group(1)
            # Record only common framework annotations
            if annotation in [
                'SpringBootApplication', 'RestController', 'Controller',
                'Service', 'Repository', 'Component', 'Configuration',
                'Bean', 'Value', 'Autowired', 'RequestMapping',
                'GetMapping', 'PostMapping', 'PutMapping', 'DeleteMapping'
            ]:
                annotations.append(annotation)
        
        return list(set(annotations))
    
    def _extract_properties(self, code: str) -> List[Dict]:
        """Extract configuration properties (@Value annotations)."""
        properties = []
        
        # @Value("${property.name:defaultValue}")
        pattern = r'@Value\s*\(\s*"\$\{([^:}]+)(?::([^}]*))?\}"\s*\)'
        
        for match in re.finditer(pattern, code):
            prop_name = match.group(1)
            default_value = match.group(2) if match.group(2) else None
            properties.append({
                "name": prop_name,
                "default": default_value,
                "required": default_value is None
            })
        
        return properties
    
    def _extract_server_port(self, code: str) -> Optional[int]:
        """Extract server port."""
        patterns = [
            r'server\.port\s*=\s*(\d+)',
            r'PORT\s*=\s*(\d+)',
            r'@Value\s*\(\s*"\$\{server\.port:(\d+)\}"\s*\)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, code)
            if match:
                try:
                    return int(match.group(1))
                except:
                    pass
        
        return None
    
    def _detect_frameworks(self, code: str) -> List[str]:
        """Detect frameworks in use."""
        frameworks = []
        
        framework_patterns = {
            "Spring Boot": r'import\s+org\.springframework\.boot|@SpringBootApplication',
            "Spring MVC": r'import\s+org\.springframework\.web|@Controller|@RestController',
            "Spring Data": r'import\s+org\.springframework\.data|@Repository',
            "Hibernate": r'import\s+org\.hibernate|@Entity',
            "JPA": r'import\s+javax\.persistence|@Entity',
            "MyBatis": r'import\s+org\.mybatis|@Mapper',
            "Netty": r'import\s+io\.netty',
            "Vertx": r'import\s+io\.vertx',
        }
        
        for framework, pattern in framework_patterns.items():
            if re.search(pattern, code):
                frameworks.append(framework)
        
        return frameworks


class CContentAnalyzer:
    """C code content analyzer."""
    
    def analyze(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a C file."""
        try:
            code = file_path.read_text(encoding='utf-8', errors='ignore')
            
            return {
                "file": str(file_path),
                "language": "C",
                "includes": self._extract_includes(code),
                "main_function": self._has_main_function(code),
                "functions": self._extract_functions(code),
                "defines": self._extract_defines(code),
                "libraries": self._detect_libraries(code)
            }
        except Exception as e:
            return {"error": str(e), "file": str(file_path)}
    
    def _extract_includes(self, code: str) -> List[Dict]:
        """Extract #include directives."""
        includes = []
        
        # System headers <xxx.h>
        system_pattern = r'#include\s*<([^>]+)>'
        for match in re.finditer(system_pattern, code):
            includes.append({
                "file": match.group(1),
                "type": "system"
            })
        
        # Local headers "xxx.h"
        local_pattern = r'#include\s*"([^"]+)"'
        for match in re.finditer(local_pattern, code):
            includes.append({
                "file": match.group(1),
                "type": "local"
            })
        
        return includes
    
    def _has_main_function(self, code: str) -> bool:
        """Check whether a main function exists."""
        pattern = r'\bint\s+main\s*\('
        return bool(re.search(pattern, code))
    
    def _extract_functions(self, code: str) -> List[str]:
        """Extract function definitions (first few only)."""
        functions = []
        
        # Simple function matching (may be imperfect)
        pattern = r'^\s*(?:static\s+)?(?:inline\s+)?(\w+\s+\**\s*\w+)\s*\([^)]*\)\s*\{'
        
        for match in re.finditer(pattern, code, re.MULTILINE):
            func_sig = match.group(1).strip()
            if not func_sig.startswith('#'):  # Exclude preprocessor directives
                functions.append(func_sig)
                if len(functions) >= 10:  # Keep at most 10
                    break
        
        return functions
    
    def _extract_defines(self, code: str) -> List[Dict]:
        """Extract #define macros."""
        defines = []
        
        pattern = r'#define\s+(\w+)(?:\s+(.+?))?(?:\n|$)'
        
        for match in re.finditer(pattern, code):
            defines.append({
                "name": match.group(1),
                "value": match.group(2).strip() if match.group(2) else None
            })
            if len(defines) >= 20:  # Keep at most 20
                break
        
        return defines
    
    def _detect_libraries(self, code: str) -> List[str]:
        """Detect libraries in use."""
        libraries = []
        
        library_patterns = {
            "pthread": r'#include\s*<pthread\.h>|pthread_',
            "socket": r'#include\s*<sys/socket\.h>|socket\(',
            "OpenSSL": r'#include\s*<openssl/',
            "curl": r'#include\s*<curl/curl\.h>|curl_',
            "sqlite": r'#include\s*<sqlite3\.h>|sqlite3_',
            "MySQL": r'#include\s*<mysql\.h>|mysql_',
            "PostgreSQL": r'#include\s*<libpq',
            "GTK": r'#include\s*<gtk/',
            "Qt": r'#include\s*<Q\w+>',
        }
        
        for lib, pattern in library_patterns.items():
            if re.search(pattern, code):
                libraries.append(lib)
        
        return libraries


class CppContentAnalyzer:
    """C++ code content analyzer."""
    
    def analyze(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a C++ file."""
        try:
            code = file_path.read_text(encoding='utf-8', errors='ignore')
            
            return {
                "file": str(file_path),
                "language": "C++",
                "includes": self._extract_includes(code),
                "namespaces": self._extract_namespaces(code),
                "main_function": self._has_main_function(code),
                "classes": self._extract_classes(code),
                "std_version": self._detect_cpp_version(code),
                "libraries": self._detect_libraries(code)
            }
        except Exception as e:
            return {"error": str(e), "file": str(file_path)}
    
    def _extract_includes(self, code: str) -> List[Dict]:
        """Extract #include directives."""
        includes = []
        
        # System headers <xxx>
        system_pattern = r'#include\s*<([^>]+)>'
        for match in re.finditer(system_pattern, code):
            includes.append({
                "file": match.group(1),
                "type": "system"
            })
        
        # Local headers "xxx"
        local_pattern = r'#include\s*"([^"]+)"'
        for match in re.finditer(local_pattern, code):
            includes.append({
                "file": match.group(1),
                "type": "local"
            })
        
        return includes
    
    def _extract_namespaces(self, code: str) -> List[str]:
        """Extract using namespace directives."""
        namespaces = []
        
        pattern = r'using\s+namespace\s+([a-zA-Z_][\w:]*);'
        
        for match in re.finditer(pattern, code):
            namespaces.append(match.group(1))
        
        return namespaces
    
    def _has_main_function(self, code: str) -> bool:
        """Check whether a main function exists."""
        pattern = r'\bint\s+main\s*\('
        return bool(re.search(pattern, code))
    
    def _extract_classes(self, code: str) -> List[str]:
        """Extract class definitions (class names only)."""
        classes = []
        
        pattern = r'\bclass\s+(\w+)\s*(?::\s*(?:public|private|protected)\s+\w+\s*)?{'
        
        for match in re.finditer(pattern, code):
            classes.append(match.group(1))
            if len(classes) >= 10:  # Keep at most 10
                break
        
        return classes
    
    def _detect_cpp_version(self, code: str) -> Optional[str]:
        """Detect C++ version markers."""
        if 'std::filesystem' in code or '#include <filesystem>' in code:
            return "C++17+"
        elif 'auto ' in code and ('std::make_unique' in code or 'std::shared_ptr' in code):
            return "C++14+"
        elif 'auto ' in code or 'nullptr' in code:
            return "C++11+"
        elif 'std::' in code:
            return "C++98+"
        return None
    
    def _detect_libraries(self, code: str) -> List[str]:
        """Detect libraries and frameworks in use."""
        libraries = []
        
        library_patterns = {
            "STL": r'#include\s*<(?:vector|map|string|algorithm|iostream)>',
            "Boost": r'#include\s*<boost/',
            "Qt": r'#include\s*<Q\w+>',
            "OpenCV": r'#include\s*<opencv2?/',
            "Eigen": r'#include\s*<Eigen/',
            "Protobuf": r'#include\s*<google/protobuf/',
            "gRPC": r'#include\s*<grpc\+\+/',
            "ROS": r'#include\s*<ros/',
            "CUDA": r'#include\s*<cuda',
            "OpenGL": r'#include\s*<GL/',
            "Vulkan": r'#include\s*<vulkan/',
        }
        
        for lib, pattern in library_patterns.items():
            if re.search(pattern, code):
                libraries.append(lib)
        
        return libraries


class ConfigFileAnalyzer:
    """Config file analyzer — supports Gradle, Properties, YAML, XML, etc."""
    
    def analyze(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a config file."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            suffix = file_path.suffix.lower()
            filename = file_path.name.lower()
            
            result = {
                "file": str(file_path),
                "language": "Config",
                "config_type": self._detect_config_type(file_path),
            }
            
            # Analyze by file type
            if suffix == '.gradle' or filename.endswith('.gradle.kts'):
                result.update(self._analyze_gradle(content))
            elif suffix == '.properties':
                result.update(self._analyze_properties(content))
            elif suffix in ['.yml', '.yaml']:
                result.update(self._analyze_yaml(content))
            elif suffix == '.xml':
                result.update(self._analyze_xml(content, filename))
            elif suffix == '.toml':
                result.update(self._analyze_toml(content))
            elif suffix == '.json':
                result.update(self._analyze_json(content))
            elif filename == 'makefile':
                result.update(self._analyze_makefile(content))
            elif filename == 'cmakelists.txt':
                result.update(self._analyze_cmake(content))
            elif filename.startswith('dockerfile'):
                result.update(self._analyze_dockerfile(content))
            elif filename.startswith('docker-compose'):
                result.update(self._analyze_docker_compose(content))
            
            return result
        except Exception as e:
            return {"error": str(e), "file": str(file_path)}
    
    def _detect_config_type(self, file_path: Path) -> str:
        """Detect config file type."""
        suffix = file_path.suffix.lower()
        filename = file_path.name.lower()
        
        if suffix == '.gradle' or filename.endswith('.gradle.kts'):
            return "Gradle"
        elif suffix == '.properties':
            if 'application' in filename:
                return "Spring Properties"
            return "Properties"
        elif suffix in ['.yml', '.yaml']:
            if 'application' in filename:
                return "Spring YAML"
            elif 'docker-compose' in filename:
                return "Docker Compose"
            return "YAML"
        elif suffix == '.xml':
            if filename == 'pom.xml':
                return "Maven POM"
            return "XML"
        elif suffix == '.toml':
            return "TOML"
        elif suffix == '.json':
            if filename == 'package.json':
                return "NPM Package"
            return "JSON"
        elif filename == 'makefile':
            return "Makefile"
        elif filename == 'cmakelists.txt':
            return "CMake"
        elif filename.startswith('dockerfile'):
            return "Dockerfile"
        return "Config"
    
    def _analyze_gradle(self, content: str) -> Dict[str, Any]:
        """Analyze Gradle build files."""
        result = {
            "plugins": [],
            "dependencies": [],
            "java_version": None,
            "tasks": [],
            "repositories": []
        }
        
        # Extract plugins
        plugin_patterns = [
            r'id\s*["\']([^"\']+)["\']',
            r'apply\s+plugin:\s*["\']([^"\']+)["\']',
        ]
        for pattern in plugin_patterns:
            for match in re.finditer(pattern, content):
                plugin = match.group(1)
                if plugin not in result["plugins"]:
                    result["plugins"].append(plugin)
        
        # Extract dependencies
        dep_patterns = [
            r'(?:implementation|api|compile|testImplementation)\s*["\']([^"\']+)["\']',
            r'(?:implementation|api|compile)\s*\(\s*["\']([^"\']+)["\']\s*\)',
        ]
        for pattern in dep_patterns:
            for match in re.finditer(pattern, content):
                dep = match.group(1)
                if dep not in result["dependencies"] and len(result["dependencies"]) < 30:
                    result["dependencies"].append(dep)
        
        # Extract Java version
        java_version_patterns = [
            r'sourceCompatibility\s*=\s*["\']?(\d+(?:\.\d+)?)["\']?',
            r'JavaLanguageVersion\.of\((\d+)\)',
            r'jvmTarget\s*=\s*["\'](\d+(?:\.\d+)?)["\']',
        ]
        for pattern in java_version_patterns:
            match = re.search(pattern, content)
            if match:
                result["java_version"] = match.group(1)
                break
        
        # Extract tasks
        task_pattern = r'task\s+(\w+)'
        for match in re.finditer(task_pattern, content):
            task = match.group(1)
            if task not in result["tasks"] and len(result["tasks"]) < 20:
                result["tasks"].append(task)
        
        # Extract repositories
        repo_patterns = [
            r'mavenCentral\(\)',
            r'mavenLocal\(\)',
            r'google\(\)',
            r'jcenter\(\)',
            r'maven\s*\{\s*url\s*["\']([^"\']+)["\']',
        ]
        for pattern in repo_patterns:
            if re.search(pattern, content):
                if 'url' in pattern:
                    for match in re.finditer(pattern, content):
                        result["repositories"].append(match.group(1))
                else:
                    repo_name = pattern.replace('\\(\\)', '').replace('\\', '')
                    if repo_name not in result["repositories"]:
                        result["repositories"].append(repo_name)
        
        return result
    
    def _analyze_properties(self, content: str) -> Dict[str, Any]:
        """Analyze properties files."""
        result = {
            "properties": [],
            "server_port": None,
            "database_url": None,
            "profiles": []
        }
        
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if '=' in line:
                key, _, value = line.partition('=')
                key = key.strip()
                value = value.strip()
                
                # Record only salient settings
                if len(result["properties"]) < 30:
                    result["properties"].append({"key": key, "value": value[:100]})
                
                # Special keys
                if key == 'server.port':
                    result["server_port"] = value
                elif 'datasource.url' in key or 'database.url' in key:
                    result["database_url"] = value
                elif key == 'spring.profiles.active':
                    result["profiles"] = [p.strip() for p in value.split(',')]
        
        return result
    
    def _analyze_yaml(self, content: str) -> Dict[str, Any]:
        """Analyze YAML files."""
        result = {
            "server_port": None,
            "database_url": None,
            "services": [],
            "env_vars": []
        }
        
        # Extract server port
        port_patterns = [
            r'port:\s*(\d+)',
            r'server\.port:\s*(\d+)',
        ]
        for pattern in port_patterns:
            match = re.search(pattern, content)
            if match:
                result["server_port"] = int(match.group(1))
                break
        
        # Extract database URL
        db_patterns = [
            r'url:\s*jdbc:([^\s]+)',
            r'datasource:\s*\n\s+url:\s*([^\s]+)',
        ]
        for pattern in db_patterns:
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                result["database_url"] = match.group(1)
                break
        
        # Extract Docker Compose services
        if 'services:' in content:
            service_pattern = r'^  (\w+):\s*$'
            for match in re.finditer(service_pattern, content, re.MULTILINE):
                service = match.group(1)
                if service not in result["services"]:
                    result["services"].append(service)
        
        # Extract environment variables
        env_pattern = r'^\s*-?\s*(\w+)=\$\{(\w+)(?::([^}]*))?\}'
        for match in re.finditer(env_pattern, content, re.MULTILINE):
            result["env_vars"].append({
                "name": match.group(2),
                "default": match.group(3) if match.group(3) else None
            })
        
        return result
    
    def _analyze_xml(self, content: str, filename: str) -> Dict[str, Any]:
        """Analyze XML files (mainly pom.xml)."""
        result = {
            "dependencies": [],
            "plugins": [],
            "java_version": None,
            "packaging": None,
            "parent": None
        }
        
        if filename == 'pom.xml':
            # Extract dependencies
            dep_pattern = r'<dependency>\s*<groupId>([^<]+)</groupId>\s*<artifactId>([^<]+)</artifactId>'
            for match in re.finditer(dep_pattern, content, re.DOTALL):
                dep = f"{match.group(1)}:{match.group(2)}"
                if dep not in result["dependencies"] and len(result["dependencies"]) < 30:
                    result["dependencies"].append(dep)
            
            # Extract plugins
            plugin_pattern = r'<plugin>\s*<groupId>([^<]+)</groupId>\s*<artifactId>([^<]+)</artifactId>'
            for match in re.finditer(plugin_pattern, content, re.DOTALL):
                plugin = f"{match.group(1)}:{match.group(2)}"
                if plugin not in result["plugins"] and len(result["plugins"]) < 20:
                    result["plugins"].append(plugin)
            
            # Extract Java version
            java_patterns = [
                r'<java\.version>([^<]+)</java\.version>',
                r'<maven\.compiler\.source>([^<]+)</maven\.compiler\.source>',
            ]
            for pattern in java_patterns:
                match = re.search(pattern, content)
                if match:
                    result["java_version"] = match.group(1)
                    break
            
            # Extract packaging type
            packaging_match = re.search(r'<packaging>([^<]+)</packaging>', content)
            if packaging_match:
                result["packaging"] = packaging_match.group(1)
            
            # Extract parent POM
            parent_pattern = r'<parent>\s*<groupId>([^<]+)</groupId>\s*<artifactId>([^<]+)</artifactId>'
            parent_match = re.search(parent_pattern, content, re.DOTALL)
            if parent_match:
                result["parent"] = f"{parent_match.group(1)}:{parent_match.group(2)}"
        
        return result
    
    def _analyze_toml(self, content: str) -> Dict[str, Any]:
        """Analyze TOML files."""
        result = {
            "sections": [],
            "dependencies": []
        }
        
        # Extract sections
        section_pattern = r'^\[([^\]]+)\]'
        for match in re.finditer(section_pattern, content, re.MULTILINE):
            section = match.group(1)
            if section not in result["sections"]:
                result["sections"].append(section)
        
        # Extract dependencies (pyproject.toml style)
        dep_pattern = r'^(\w[\w-]*)\s*=\s*["\']([^"\']+)["\']'
        in_deps = False
        for line in content.split('\n'):
            if '[dependencies]' in line or '[project.dependencies]' in line:
                in_deps = True
            elif line.startswith('[') and 'dependencies' not in line:
                in_deps = False
            elif in_deps:
                match = re.match(dep_pattern, line.strip())
                if match:
                    result["dependencies"].append(f"{match.group(1)}={match.group(2)}")
        
        return result
    
    def _analyze_json(self, content: str) -> Dict[str, Any]:
        """Analyze JSON files."""
        result = {
            "scripts": {},
            "dependencies": [],
            "dev_dependencies": []
        }
        
        try:
            data = json.loads(content)
            
            # package.json
            if "scripts" in data:
                result["scripts"] = {k: v for k, v in list(data["scripts"].items())[:10]}
            
            if "dependencies" in data:
                result["dependencies"] = list(data["dependencies"].keys())[:20]
            
            if "devDependencies" in data:
                result["dev_dependencies"] = list(data["devDependencies"].keys())[:20]
        except:
            pass
        
        return result
    
    def _analyze_makefile(self, content: str) -> Dict[str, Any]:
        """Analyze Makefile."""
        result = {
            "targets": [],
            "variables": []
        }
        
        # Extract targets
        target_pattern = r'^([a-zA-Z_][\w-]*):'
        for match in re.finditer(target_pattern, content, re.MULTILINE):
            target = match.group(1)
            if target not in result["targets"] and len(result["targets"]) < 20:
                result["targets"].append(target)
        
        # Extract variables
        var_pattern = r'^([A-Z_]+)\s*[?:]?='
        for match in re.finditer(var_pattern, content, re.MULTILINE):
            var = match.group(1)
            if var not in result["variables"] and len(result["variables"]) < 20:
                result["variables"].append(var)
        
        return result
    
    def _analyze_cmake(self, content: str) -> Dict[str, Any]:
        """Analyze CMakeLists.txt."""
        result = {
            "project_name": None,
            "cmake_version": None,
            "targets": [],
            "find_packages": []
        }
        
        # Extract project name
        project_match = re.search(r'project\s*\(\s*(\w+)', content, re.IGNORECASE)
        if project_match:
            result["project_name"] = project_match.group(1)
        
        # Extract CMake version
        version_match = re.search(r'cmake_minimum_required\s*\(\s*VERSION\s+([\d.]+)', content, re.IGNORECASE)
        if version_match:
            result["cmake_version"] = version_match.group(1)
        
        # Extract targets
        target_patterns = [
            r'add_executable\s*\(\s*(\w+)',
            r'add_library\s*\(\s*(\w+)',
        ]
        for pattern in target_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                target = match.group(1)
                if target not in result["targets"]:
                    result["targets"].append(target)
        
        # Extract find_package calls
        find_pattern = r'find_package\s*\(\s*(\w+)'
        for match in re.finditer(find_pattern, content, re.IGNORECASE):
            pkg = match.group(1)
            if pkg not in result["find_packages"]:
                result["find_packages"].append(pkg)
        
        return result
    
    def _analyze_dockerfile(self, content: str) -> Dict[str, Any]:
        """Analyze Dockerfile."""
        result = {
            "base_image": None,
            "exposed_ports": [],
            "env_vars": [],
            "commands": []
        }
        
        # Extract base image
        from_match = re.search(r'^FROM\s+([^\s]+)', content, re.MULTILINE | re.IGNORECASE)
        if from_match:
            result["base_image"] = from_match.group(1)
        
        # Extract exposed ports
        expose_pattern = r'^EXPOSE\s+(\d+)'
        for match in re.finditer(expose_pattern, content, re.MULTILINE | re.IGNORECASE):
            port = int(match.group(1))
            if port not in result["exposed_ports"]:
                result["exposed_ports"].append(port)
        
        # Extract environment variables
        env_pattern = r'^ENV\s+(\w+)(?:=|\s+)([^\s]+)?'
        for match in re.finditer(env_pattern, content, re.MULTILINE | re.IGNORECASE):
            result["env_vars"].append({
                "name": match.group(1),
                "value": match.group(2) if match.group(2) else None
            })
        
        # Extract main commands
        cmd_patterns = [
            (r'^CMD\s+(.+)$', 'CMD'),
            (r'^ENTRYPOINT\s+(.+)$', 'ENTRYPOINT'),
        ]
        for pattern, cmd_type in cmd_patterns:
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                result["commands"].append({
                    "type": cmd_type,
                    "command": match.group(1)[:100]
                })
        
        return result
    
    def _analyze_docker_compose(self, content: str) -> Dict[str, Any]:
        """Analyze docker-compose.yml."""
        result = {
            "services": [],
            "volumes": [],
            "networks": []
        }
        
        # Extract services
        service_pattern = r'^  ([a-zA-Z][\w-]*):\s*$'
        in_services = False
        for line in content.split('\n'):
            if line.strip() == 'services:':
                in_services = True
            elif line.startswith('volumes:') or line.startswith('networks:'):
                in_services = False
            elif in_services:
                match = re.match(service_pattern, line)
                if match:
                    result["services"].append(match.group(1))
        
        # Extract volumes
        if 'volumes:' in content:
            volume_section = content.split('volumes:')[1].split('\n')
            for line in volume_section:
                if line.startswith('  ') and ':' in line and not line.strip().startswith('-'):
                    vol_name = line.split(':')[0].strip()
                    if vol_name and not vol_name.startswith('#'):
                        result["volumes"].append(vol_name)
                elif not line.startswith(' ') and line.strip():
                    break
        
        return result


def identify_priority_files(repo_path: Path) -> List[tuple]:
    """Identify high-priority files (for deep analysis)."""
    priority_files = []
    seen_files = set()  # Avoid duplicates
    
    # High-priority patterns — entry points and core config
    high_priority_patterns = [
        # Python
        ('main.py', 'high'),
        ('app.py', 'high'),
        ('server.py', 'high'),
        ('cli.py', 'high'),
        ('config.py', 'high'),
        ('settings.py', 'high'),
        # JavaScript/TypeScript
        ('index.js', 'high'),
        ('app.js', 'high'),
        ('server.js', 'high'),
        ('index.ts', 'high'),
        ('app.ts', 'high'),
        ('package.json', 'high'),
        # Go
        ('main.go', 'high'),
        # Java
        ('Application.java', 'high'),
        ('Main.java', 'high'),
        ('App.java', 'high'),
        # C/C++
        ('main.c', 'high'),
        ('main.cpp', 'high'),
        ('main.cc', 'high'),
        # Build config (high priority)
        ('pom.xml', 'high'),
        ('build.gradle', 'high'),
        ('build.gradle.kts', 'high'),
        ('settings.gradle', 'high'),
        ('settings.gradle.kts', 'high'),
        # Docker
        ('Dockerfile', 'high'),
        ('docker-compose.yml', 'high'),
        ('docker-compose.yaml', 'high'),
    ]
    
    # Medium-priority patterns — secondary config and helper files
    medium_priority_patterns = [
        # Python
        ('setup.py', 'medium'),
        ('pyproject.toml', 'medium'),
        ('manage.py', 'medium'),
        ('requirements.txt', 'medium'),
        # Java/Spring
        ('application.properties', 'medium'),
        ('application.yml', 'medium'),
        ('application.yaml', 'medium'),
        ('application-dev.properties', 'medium'),
        ('application-prod.properties', 'medium'),
        ('bootstrap.properties', 'medium'),
        ('bootstrap.yml', 'medium'),
        # Gradle
        ('gradle.properties', 'medium'),
        # C/C++
        ('Makefile', 'medium'),
        ('makefile', 'medium'),
        ('CMakeLists.txt', 'medium'),
        ('configure.ac', 'medium'),
        # Go
        ('go.mod', 'medium'),
        # Rust
        ('Cargo.toml', 'medium'),
        # Node.js
        ('tsconfig.json', 'medium'),
        ('webpack.config.js', 'medium'),
        # Other config
        ('.env.example', 'medium'),
        ('env.example', 'medium'),
    ]
    
    # Directories to exclude
    excluded_dirs = {
        '__pycache__', 'node_modules', '.git', '.idea', '.vscode',
        'dist', 'target', '.gradle', 'out', 'bin',
        'venv', '.venv', 'env', 'virtualenv',
        '.egg-info', 'eggs', '*.egg',
        'coverage', '.coverage', 'htmlcov',
    }
    
    def should_skip_path(path: Path) -> bool:
        """Check whether the path should be skipped."""
        for part in path.parts:
            if part in excluded_dirs or part.startswith('.'):
                # Do not skip files like .env at repo root
                if part == path.name:
                    continue
                return True
        return False
    
    # Walk the repository for files
    for file_path in repo_path.rglob('*'):
        if not file_path.is_file():
            continue
        
        # Skip excluded directories
        rel_path = file_path.relative_to(repo_path)
        if should_skip_path(rel_path):
            continue
        
        filename = file_path.name
        file_key = str(rel_path)
        
        # Avoid duplicate entries
        if file_key in seen_files:
            continue
        
        # Check high priority
        matched = False
        for pattern, priority in high_priority_patterns:
            if filename == pattern or filename.lower() == pattern.lower():
                priority_files.append((file_path, priority))
                seen_files.add(file_key)
                matched = True
                break
        
        if not matched:
            # Check medium priority
            for pattern, priority in medium_priority_patterns:
                if filename == pattern or filename.lower() == pattern.lower():
                    priority_files.append((file_path, priority))
                    seen_files.add(file_key)
                    break
    
    # For Java projects, also find Spring Boot application classes (exclude test trees)
    for file_path in repo_path.rglob('*.java'):
        rel_path = file_path.relative_to(repo_path)
        rel_path_str = str(rel_path).lower()
        
        # Skip excluded and test directories
        if should_skip_path(rel_path):
            continue
        if '/test/' in rel_path_str or '/tests/' in rel_path_str or 'test' in rel_path.parts:
            continue
        
        file_key = str(rel_path)
        if file_key in seen_files:
            continue
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            # Only classes annotated with @SpringBootApplication
            if '@SpringBootApplication' in content:
                priority_files.append((file_path, 'high'))
                seen_files.add(file_key)
        except:
            pass
    
    return priority_files























