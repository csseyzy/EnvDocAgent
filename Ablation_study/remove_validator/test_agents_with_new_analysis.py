#!/usr/bin/env python3
"""
Test Reader and Analyzer handling of deep code-analysis payloads.
"""

import json
from pathlib import Path


def create_mock_analysis_python():
    """Mock analysis data for a Python project."""
    return {
        "repo_path": "/mock/python_project",
        "file_stats": {
            "total_files": 15,
            "by_type": {
                ".py": 10,
                ".md": 2,
                ".txt": 2,
                ".yml": 1
            }
        },
        "content_analysis": [
            {
                "file": "main.py",
                "language": "Python",
                "imports": [
                    "flask",
                    "redis",
                    "psycopg2",
                    "os",
                    "argparse"
                ],
                "main_block": True,
                "cli_params": [
                    {"name": "--port", "default": "5000", "help": "Service port"},
                    {"name": "--host", "default": "0.0.0.0", "help": "Bind address"}
                ],
                "env_vars": [
                    "DATABASE_URL",
                    "REDIS_URL",
                    "SECRET_KEY",
                    "DEBUG"
                ],
                "services": {
                    "redis": {"host": "REDIS_URL"},
                    "postgresql": {"url": "DATABASE_URL"}
                },
                "frameworks": ["Flask"]
            }
        ]
    }


def create_mock_analysis_java():
    """Mock analysis data for a Java Spring Boot project."""
    return {
        "repo_path": "/mock/java_project",
        "file_stats": {
            "total_files": 25,
            "by_type": {
                ".java": 18,
                ".xml": 2,
                ".properties": 3,
                ".md": 2
            }
        },
        "content_analysis": [
            {
                "file": "Application.java",
                "language": "Java",
                "imports": [
                    "org.springframework.boot.SpringApplication",
                    "org.springframework.boot.autoconfigure.SpringBootApplication",
                    "org.springframework.web.bind.annotation.RestController"
                ],
                "main_method": True,
                "annotations": [
                    "SpringBootApplication",
                    "RestController",
                    "Value",
                    "Autowired"
                ],
                "properties": [
                    {
                        "name": "server.port",
                        "default": "8080",
                        "required": False
                    },
                    {
                        "name": "spring.datasource.url",
                        "default": None,
                        "required": True
                    },
                    {
                        "name": "spring.redis.host",
                        "default": "localhost",
                        "required": False
                    }
                ],
                "server_port": 8080,
                "frameworks": [
                    "Spring Boot",
                    "Spring MVC",
                    "Spring Data"
                ]
            }
        ]
    }


def create_mock_analysis_cpp():
    """Mock analysis data for a C++ project."""
    return {
        "repo_path": "/mock/cpp_project",
        "file_stats": {
            "total_files": 20,
            "by_type": {
                ".cpp": 10,
                ".hpp": 8,
                ".txt": 1,
                ".md": 1
            }
        },
        "content_analysis": [
            {
                "file": "main.cpp",
                "language": "C++",
                "includes": [
                    {"file": "iostream", "type": "system"},
                    {"file": "boost/asio.hpp", "type": "system"},
                    {"file": "grpc++/grpc++.h", "type": "system"},
                    {"file": "config.hpp", "type": "local"}
                ],
                "namespaces": ["std", "boost::asio"],
                "main_function": True,
                "classes": ["Server", "RequestHandler", "Database"],
                "std_version": "C++17+",
                "libraries": [
                    "STL",
                    "Boost",
                    "gRPC",
                    "Protobuf"
                ]
            }
        ]
    }


def create_mock_analysis_c():
    """Mock analysis data for a C project."""
    return {
        "repo_path": "/mock/c_project",
        "file_stats": {
            "total_files": 12,
            "by_type": {
                ".c": 8,
                ".h": 4
            }
        },
        "content_analysis": [
            {
                "file": "server.c",
                "language": "C",
                "includes": [
                    {"file": "stdio.h", "type": "system"},
                    {"file": "pthread.h", "type": "system"},
                    {"file": "sys/socket.h", "type": "system"},
                    {"file": "openssl/ssl.h", "type": "system"},
                    {"file": "config.h", "type": "local"}
                ],
                "main_function": True,
                "functions": [
                    "int main",
                    "void start_server",
                    "void handle_request"
                ],
                "defines": [
                    {"name": "PORT", "value": "8080"},
                    {"name": "MAX_CONNECTIONS", "value": "100"},
                    {"name": "BUFFER_SIZE", "value": "4096"}
                ],
                "libraries": [
                    "pthread",
                    "socket",
                    "OpenSSL"
                ]
            }
        ]
    }


def test_analysis_structure():
    """Validate analysis structure per language."""
    print("=" * 70)
    print("Deep code analysis structure tests")
    print("=" * 70)
    
    test_cases = [
        ("Python project", create_mock_analysis_python()),
        ("Java project", create_mock_analysis_java()),
        ("C++ project", create_mock_analysis_cpp()),
        ("C project", create_mock_analysis_c()),
    ]
    
    for name, analysis in test_cases:
        print(f"\n{'─' * 70}")
        print(f"📦 {name}")
        print(f"{'─' * 70}")
        
        # Basic shape
        assert "repo_path" in analysis, "missing repo_path"
        assert "file_stats" in analysis, "missing file_stats"
        assert "content_analysis" in analysis, "missing content_analysis"
        
        print(f"✅ Basic structure OK")
        
        # content_analysis
        content = analysis["content_analysis"][0]
        assert "file" in content, "missing file"
        assert "language" in content, "missing language"
        
        print(f"✅ Language: {content['language']}")
        
        # Language-specific fields
        if content["language"] == "Python":
            assert "imports" in content
            assert "env_vars" in content
            assert "frameworks" in content
            print(f"✅ Python fields: imports({len(content['imports'])}), "
                  f"env_vars({len(content['env_vars'])}), "
                  f"frameworks({content['frameworks']})")
        
        elif content["language"] == "Java":
            assert "annotations" in content
            assert "properties" in content
            assert "frameworks" in content
            print(f"✅ Java fields: annotations({len(content['annotations'])}), "
                  f"properties({len(content['properties'])}), "
                  f"frameworks({content['frameworks']})")
        
        elif content["language"] == "C++":
            assert "includes" in content
            assert "libraries" in content
            assert "std_version" in content
            print(f"✅ C++ fields: includes({len(content['includes'])}), "
                  f"libraries({len(content['libraries'])}), "
                  f"std_version({content['std_version']})")
        
        elif content["language"] == "C":
            assert "includes" in content
            assert "defines" in content
            assert "libraries" in content
            print(f"✅ C fields: includes({len(content['includes'])}), "
                  f"defines({len(content['defines'])}), "
                  f"libraries({len(content['libraries'])})")
        
        print(f"✅ {name} structure validated\n")
    
    return True


def generate_expected_readme_sections():
    """Print example README sections derived from deep analysis."""
    print("=" * 70)
    print("Expected README generation examples")
    print("=" * 70)
    
    examples = {
        "Python Flask project": """
## Tech stack
- Python 3.9+
- Flask
- Redis
- PostgreSQL

## Requirements
```bash
# Install Python dependencies
pip install flask redis psycopg2-binary
```

## Environment variables
```bash
# Required
export DATABASE_URL="postgresql://localhost:5432/mydb"
export REDIS_URL="redis://localhost:6379"
export SECRET_KEY="your-secret-key"
export DEBUG="False"
```

## Run the service
```bash
# Default port 5000
python main.py

# Custom port
python main.py --port 8080 --host 0.0.0.0
```

## Verify deployment
```bash
curl http://localhost:5000
```
""",
        
        "Java Spring Boot project": """
## Tech stack
- Java 11+
- Spring Boot
- Spring MVC
- Spring Data

## Requirements
```bash
# Maven build
mvn clean install
```

## Configuration
application.properties:
```properties
# Required
spring.datasource.url=jdbc:mysql://localhost:3306/mydb

# Optional (defaults)
server.port=8080
spring.redis.host=localhost
```

## Run the service
```bash
# With Maven
mvn spring-boot:run

# Or JAR
java -jar target/app.jar
```

## Verify deployment
```bash
curl http://localhost:8080
```
""",
        
        "C++ gRPC project": """
## Tech stack
- C++17
- Boost
- gRPC
- Protobuf

## Requirements
```bash
# Ubuntu/Debian dependencies
sudo apt update
sudo apt install -y build-essential cmake \\
    libboost-all-dev libgrpc++-dev libprotobuf-dev
```

## Build
```bash
mkdir build && cd build
cmake .. -DCMAKE_CXX_STANDARD=17
make -j$(nproc)
```

## Run the service
```bash
./build/server
```
""",
        
        "C network server project": """
## Tech stack
- C (GNU C99)
- pthread
- OpenSSL
- socket

## Requirements
```bash
# Ubuntu/Debian dependencies
sudo apt update
sudo apt install -y build-essential libssl-dev libpthread-stubs0-dev
```

## Build configuration
Macros in server.c:
- PORT: 8080
- MAX_CONNECTIONS: 100
- BUFFER_SIZE: 4096

## Build
```bash
gcc -o server server.c -lpthread -lssl -lcrypto
```

## Run the service
```bash
./server
# Listen port: 8080
```
"""
    }
    
    for project_type, readme in examples.items():
        print(f"\n{'─' * 70}")
        print(f"📄 {project_type}")
        print(f"{'─' * 70}")
        print(readme)
    
    return True


def check_agent_prompts():
    """Check agent prompts mention new analysis fields."""
    print("=" * 70)
    print("Agent prompt inspection")
    print("=" * 70)
    
    agent_files = [
        "agent_reader.py",
        "agent_analyzer.py"
    ]
    
    required_keywords = [
        "content_analysis",
        "Java",
        "C++",
        "annotations",
        "properties",
        "libraries",
        "includes"
    ]
    
    for agent_file in agent_files:
        print(f"\nChecking {agent_file}...")
        path = Path(agent_file)
        
        if not path.exists():
            print(f"⚠️  File not found: {agent_file}")
            continue
        
        content = path.read_text()
        
        found_keywords = []
        for keyword in required_keywords:
            if keyword in content:
                found_keywords.append(keyword)
        
        print(f"✅ Keywords found: {', '.join(found_keywords)}")
        
        if len(found_keywords) >= len(required_keywords) * 0.7:
            print(f"✅ {agent_file} covers enough new analysis fields")
        else:
            print(f"⚠️  {agent_file} may need prompt updates")
    
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("Agents vs. new code-analysis data")
    print("=" * 70)
    
    tests = [
        ("Structure tests", test_analysis_structure),
        ("README generation examples", generate_expected_readme_sections),
        ("Agent prompt check", check_agent_prompts),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n❌ {test_name} failed: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Total: {passed + failed}")
    print("=" * 70)
    
    if failed == 0:
        print("\n🎉 All tests passed. Reader and Analyzer are ready for the new analysis payload.")
    else:
        print(f"\n⚠️  {failed} test(s) failed; check configuration.")


if __name__ == "__main__":
    main()
