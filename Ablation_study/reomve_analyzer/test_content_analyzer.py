#!/usr/bin/env python3
"""
Test the content analyzer.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from content_analyzer import (
    ContentAnalyzer,
    PythonContentAnalyzer,
    JavaScriptContentAnalyzer,
    JavaContentAnalyzer,
    CContentAnalyzer,
    CppContentAnalyzer,
    identify_priority_files
)


def test_python_analyzer():
    """Test Python analyzer."""
    print("=" * 60)
    print("Test Python content analyzer")
    print("=" * 60)
    
    # Create sample code
    test_code = Path("test_sample.py")
    test_code.write_text("""
import os
import sys
from flask import Flask, request
import redis

app = Flask(__name__)

class Config:
    DEBUG = os.getenv("DEBUG", "False")
    DATABASE_URL = os.getenv("DATABASE_URL")
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    API_KEY = os.environ.get("API_KEY")

@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
""")
    
    analyzer = PythonContentAnalyzer()
    result = analyzer.analyze(test_code)
    
    print(f"\n✅ Analysis result:")
    print(f"  Imports: {len(result['imports'])}")
    for imp in result['imports'][:5]:
        print(f"    - {imp}")
    
    print(f"\n  Environment variables: {len(result['env_vars'])}")
    for env in result['env_vars']:
        required = "required" if env['required'] else "optional"
        default = f" (default: {env['default']})" if env.get('default') else ""
        print(f"    - {env['name']} [{required}]{default}")
    
    print(f"\n  Config variables: {len(result['config_vars'])}")
    for var in result['config_vars']:
        print(f"    - {var['name']} = {var['value']}")
    
    print(f"\n  Detected frameworks: {', '.join(result['frameworks'])}")
    
    if result['main_block']:
        print(f"\n  Main block:")
        print(f"    - has_app_run: {result['main_block']['has_app_run']}")
        print(f"    - has_uvicorn: {result['main_block']['has_uvicorn']}")
    
    # Cleanup
    test_code.unlink()
    
    return True


def test_javascript_analyzer():
    """Test JavaScript analyzer."""
    print("\n" + "=" * 60)
    print("Test JavaScript content analyzer")
    print("=" * 60)
    
    # Create sample code
    test_code = Path("test_sample.js")
    test_code.write_text("""
const express = require('express');
const redis = require('redis');

const app = express();
const PORT = process.env.PORT || 3000;
const DB_HOST = process.env.DB_HOST;

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
""")
    
    analyzer = JavaScriptContentAnalyzer()
    result = analyzer.analyze(test_code)
    
    print(f"\n✅ Analysis result:")
    print(f"  Imports: {len(result['imports'])}")
    for imp in result['imports']:
        print(f"    - {imp['module']} ({imp['type']})")
    
    print(f"\n  Environment variables: {len(result['env_vars'])}")
    for env in result['env_vars']:
        print(f"    - {env['name']}")
    
    print(f"\n  Server port: {result['server_port']}")
    print(f"  Detected frameworks: {', '.join(result['frameworks'])}")
    
    # Cleanup
    test_code.unlink()
    
    return True


def test_priority_files():
    """Test priority file identification."""
    print("\n" + "=" * 60)
    print("Test priority file identification")
    print("=" * 60)
    
    # Use current project
    repo_path = Path(__file__).parent
    priority_files = identify_priority_files(repo_path)
    
    print(f"\nFound {len(priority_files)} priority files:")
    
    high = [f for f, p in priority_files if p == 'high']
    medium = [f for f, p in priority_files if p == 'medium']
    
    print(f"\nHigh priority ({len(high)}):")
    for file in high[:5]:
        print(f"  - {file.name}")
    
    print(f"\nMedium priority ({len(medium)}):")
    for file in medium[:5]:
        print(f"  - {file.name}")
    
    return True


def test_full_analyzer():
    """Test full ContentAnalyzer."""
    print("\n" + "=" * 60)
    print("Test full content analyzer")
    print("=" * 60)
    
    analyzer = ContentAnalyzer()
    
    # Analyze main.py in this project
    main_file = Path(__file__).parent / "main.py"
    if main_file.exists():
        result = analyzer.analyze_file(main_file)
        
        if result:
            print(f"\n✅ Analyzed main.py successfully")
            print(f"  Language: {result.get('language')}")
            print(f"  Imports: {len(result.get('imports', []))}")
            print(f"  Environment variables: {len(result.get('env_vars', []))}")
            print(f"  Detected frameworks: {', '.join(result.get('frameworks', []))}")
        else:
            print("⚠️  Empty analysis result")
    else:
        print("⚠️  main.py not found")
    
    return True


def test_java_analyzer():
    """Test Java analyzer."""
    print("\n" + "=" * 60)
    print("Test Java content analyzer")
    print("=" * 60)
    
    # Create sample code
    test_code = Path("test_sample.java")
    test_code.write_text("""
package com.example.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.beans.factory.annotation.Value;

@SpringBootApplication
public class DemoApplication {
    
    @Value("${server.port:8080}")
    private int serverPort;
    
    @Value("${database.url}")
    private String databaseUrl;
    
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}

@RestController
class HelloController {
    @GetMapping("/hello")
    public String hello() {
        return "Hello World";
    }
}
""")
    
    analyzer = JavaContentAnalyzer()
    result = analyzer.analyze(test_code)
    
    print(f"\n✅ Analysis result:")
    print(f"  Imports: {len(result['imports'])}")
    for imp in result['imports'][:5]:
        print(f"    - {imp}")
    
    print(f"\n  Annotations: {', '.join(result['annotations'])}")
    print(f"  Configuration properties: {len(result['properties'])}")
    for prop in result['properties']:
        required = "required" if prop['required'] else "optional"
        default = f" (default: {prop['default']})" if prop.get('default') else ""
        print(f"    - {prop['name']} [{required}]{default}")
    
    print(f"\n  Server port: {result['server_port']}")
    print(f"  Detected frameworks: {', '.join(result['frameworks'])}")
    print(f"  Has main method: {result['main_method']}")
    
    # Cleanup
    test_code.unlink()
    
    return True


def test_c_analyzer():
    """Test C analyzer."""
    print("\n" + "=" * 60)
    print("Test C content analyzer")
    print("=" * 60)
    
    # Create sample code
    test_code = Path("test_sample.c")
    test_code.write_text("""
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include "config.h"

#define MAX_BUFFER 1024
#define PORT 8080
#define DEBUG 1

typedef struct {
    int id;
    char name[100];
} User;

int process_data(char *buffer) {
    printf("Processing: %s\\n", buffer);
    return 0;
}

int main(int argc, char *argv[]) {
    printf("Server starting on port %d\\n", PORT);
    
    pthread_t thread;
    // ... more code ...
    
    return 0;
}
""")
    
    analyzer = CContentAnalyzer()
    result = analyzer.analyze(test_code)
    
    print(f"\n✅ Analysis result:")
    print(f"  Header includes: {len(result['includes'])}")
    for inc in result['includes']:
        print(f"    - {inc['file']} ({inc['type']})")
    
    print(f"\n  Macro defines: {len(result['defines'])}")
    for define in result['defines'][:5]:
        value = f" = {define['value']}" if define['value'] else ""
        print(f"    - {define['name']}{value}")
    
    print(f"\n  Function definitions: {len(result['functions'])}")
    for func in result['functions'][:5]:
        print(f"    - {func}")
    
    print(f"\n  Detected libraries: {', '.join(result['libraries'])}")
    print(f"  Has main function: {result['main_function']}")
    
    # Cleanup
    test_code.unlink()
    
    return True


def test_cpp_analyzer():
    """Test C++ analyzer."""
    print("\n" + "=" * 60)
    print("Test C++ content analyzer")
    print("=" * 60)
    
    # Create sample code
    test_code = Path("test_sample.cpp")
    test_code.write_text("""
#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <boost/asio.hpp>

using namespace std;
using namespace boost;

class Server {
private:
    int port;
    string host;
    
public:
    Server(int p, const string& h) : port(p), host(h) {}
    
    void start() {
        cout << "Server starting on " << host << ":" << port << endl;
    }
};

class Database {
public:
    void connect(const string& url) {
        cout << "Connecting to: " << url << endl;
    }
};

int main(int argc, char* argv[]) {
    auto server = make_unique<Server>(8080, "localhost");
    server->start();
    
    return 0;
}
""")
    
    analyzer = CppContentAnalyzer()
    result = analyzer.analyze(test_code)
    
    print(f"\n✅ Analysis result:")
    print(f"  Header includes: {len(result['includes'])}")
    for inc in result['includes'][:5]:
        print(f"    - {inc['file']} ({inc['type']})")
    
    print(f"\n  Namespaces: {', '.join(result['namespaces'])}")
    
    print(f"\n  Class definitions: {len(result['classes'])}")
    for cls in result['classes']:
        print(f"    - {cls}")
    
    print(f"\n  C++ standard: {result['std_version']}")
    print(f"  Detected libraries: {', '.join(result['libraries'])}")
    print(f"  Has main function: {result['main_function']}")
    
    # Cleanup
    test_code.unlink()
    
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Content analyzer test suite")
    print("=" * 60)
    
    tests = [
        ("Python analyzer", test_python_analyzer),
        ("JavaScript analyzer", test_javascript_analyzer),
        ("Java analyzer", test_java_analyzer),
        ("C analyzer", test_c_analyzer),
        ("C++ analyzer", test_cpp_analyzer),
        ("Priority file identification", test_priority_files),
        ("Full analyzer", test_full_analyzer),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {name}: passed")
            else:
                failed += 1
                print(f"\n❌ {name}: failed")
        except Exception as e:
            failed += 1
            print(f"\n❌ {name}: exception - {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total: {passed + failed}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
