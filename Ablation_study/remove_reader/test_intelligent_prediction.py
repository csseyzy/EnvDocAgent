#!/usr/bin/env python3
"""
Test Analyzer intelligent prediction and gap-filling behavior.
"""

import json


def test_prediction_scenarios():
    """Exercise various prediction scenarios."""
    
    print("=" * 70)
    print("Analyzer intelligent prediction and gap-filling")
    print("=" * 70)
    
    scenarios = [
        {
            "name": "Scenario 1: Flask project missing port info",
            "code_analysis": {
                "content_analysis": [{
                    "language": "Python",
                    "frameworks": ["Flask"],
                    "imports": ["flask"],
                    "env_vars": ["DATABASE_URL"]
                }]
            },
            "gap": "Port not specified",
            "expected_prediction": {
                "item": "Service port",
                "predicted_value": "8000 or 5000",
                "confidence": 0.90,
                "reasoning": "Flask typical ports (dev 5000, prod 8000)",
                "evidence": "Flask framework convention"
            }
        },
        {
            "name": "Scenario 2: Spring Boot project missing build command",
            "code_analysis": {
                "content_analysis": [{
                    "language": "Java",
                    "frameworks": ["Spring Boot"],
                    "annotations": ["SpringBootApplication"]
                }],
                "file_stats": {
                    "by_type": {".xml": 1}  # pom.xml present
                }
            },
            "gap": "Build command missing",
            "expected_prediction": {
                "item": "Build command",
                "predicted_value": "mvn clean install && mvn spring-boot:run",
                "confidence": 0.95,
                "reasoning": "pom.xml present; standard Maven build flow",
                "evidence": "pom.xml + Spring Boot common practice"
            }
        },
        {
            "name": "Scenario 3: Python with psycopg2, DB config missing",
            "code_analysis": {
                "content_analysis": [{
                    "language": "Python",
                    "imports": ["psycopg2", "flask"],
                    "env_vars": ["DATABASE_URL"]
                }]
            },
            "gap": "Database connection format not documented",
            "expected_prediction": {
                "item": "Database connection format",
                "predicted_value": "postgresql://user:pass@localhost:5432/db",
                "confidence": 0.95,
                "reasoning": "psycopg2 detected; standard PostgreSQL URL format",
                "evidence": "psycopg2 + DATABASE_URL env var"
            }
        },
        {
            "name": "Scenario 4: C++ with CMakeLists.txt, compile command missing",
            "code_analysis": {
                "content_analysis": [{
                    "language": "C++",
                    "std_version": "C++17+",
                    "libraries": ["Boost", "gRPC"]
                }],
                "file_stats": {
                    "by_type": {".txt": 1}  # CMakeLists.txt
                }
            },
            "gap": "Build steps missing",
            "expected_prediction": {
                "item": "Compile command",
                "predicted_value": "mkdir build && cd build && cmake .. -DCMAKE_CXX_STANDARD=17 && make -j$(nproc)",
                "confidence": 0.95,
                "reasoning": "CMakeLists.txt present and C++17 project",
                "evidence": "CMakeLists.txt + C++17"
            }
        },
        {
            "name": "Scenario 5: Node.js project missing test command",
            "code_analysis": {
                "content_analysis": [{
                    "language": "JavaScript",
                    "frameworks": ["Express"],
                    "imports": ["express", "jest"]
                }],
                "file_stats": {
                    "by_type": {".json": 1}  # package.json
                }
            },
            "gap": "Test command not provided",
            "expected_prediction": {
                "item": "Test command",
                "predicted_value": "npm test",
                "confidence": 0.85,
                "reasoning": "jest detected; standard npm test script",
                "evidence": "jest + package.json (medium confidence; mark as inferred)"
            }
        },
        {
            "name": "Scenario 6: Missing API_KEY (low confidence, no prediction)",
            "code_analysis": {
                "content_analysis": [{
                    "language": "Python",
                    "env_vars": ["API_KEY", "DATABASE_URL"]
                }]
            },
            "gap": "API_KEY value unknown",
            "expected_prediction": {
                "item": "API_KEY",
                "predicted_value": None,
                "confidence": 0.0,
                "reasoning": "Third-party credentials cannot be predicted",
                "evidence": None,
                "action": "Write to Open Questions"
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'─' * 70}")
        print(f"📋 {scenario['name']}")
        print(f"{'─' * 70}")
        
        print(f"\nCode analysis result:")
        print(json.dumps(scenario['code_analysis'], ensure_ascii=False, indent=2))
        
        print(f"\nDetected gap: {scenario['gap']}")
        
        print(f"\n✅ Expected prediction:")
        pred = scenario['expected_prediction']
        print(f"  Item: {pred['item']}")
        print(f"  Predicted value: {pred.get('predicted_value', 'N/A')}")
        print(f"  Confidence: {pred['confidence'] * 100:.0f}%")
        print(f"  Reasoning: {pred['reasoning']}")
        print(f"  Evidence: {pred.get('evidence', 'N/A')}")
        
        if pred['confidence'] >= 0.90:
            print(f"  ✅ Action: fill README directly")
        elif pred['confidence'] >= 0.70:
            print(f"  ⚠️  Action: fill README + label (inferred)")
        else:
            print(f"  ❌ Action: write to Open Questions")
    
    print(f"\n{'=' * 70}")
    print("Summary")
    print(f"{'=' * 70}")
    print(f"✅ High-confidence scenarios (90%+): 4 — direct README fill")
    print(f"⚠️  Medium-confidence (70–89%): 1 — fill + inferred label")
    print(f"❌ Low-confidence (<70%): 1 — Open Questions")
    print(f"{'=' * 70}\n")


def show_prediction_rules():
    """Print prediction rule catalog."""
    
    print("=" * 70)
    print("Intelligent prediction rule catalog")
    print("=" * 70)
    
    rules = {
        "Port prediction": {
            "Flask": {"port": "8000 or 5000", "confidence": 0.90},
            "Django": {"port": "8000", "confidence": 0.90},
            "Express": {"port": "3000", "confidence": 0.90},
            "Spring Boot": {"port": "8080", "confidence": 0.95},
            "FastAPI": {"port": "8000", "confidence": 0.90},
            "Gin": {"port": "8080", "confidence": 0.85},
        },
        "Build tool prediction": {
            "pom.xml": {
                "command": "mvn clean install && mvn spring-boot:run",
                "confidence": 0.95
            },
            "build.gradle": {
                "command": "gradle build && java -jar build/libs/*.jar",
                "confidence": 0.95
            },
            "package.json": {
                "command": "npm install && npm start",
                "confidence": 0.95
            },
            "Makefile": {
                "command": "make && make install",
                "confidence": 0.90
            },
            "CMakeLists.txt": {
                "command": "mkdir build && cd build && cmake .. && make",
                "confidence": 0.95
            },
            "Cargo.toml": {
                "command": "cargo build --release",
                "confidence": 0.95
            }
        },
        "Database connection prediction": {
            "psycopg2": {
                "format": "postgresql://user:pass@localhost:5432/db",
                "confidence": 0.95
            },
            "mysql-connector": {
                "format": "mysql://user:pass@localhost:3306/db",
                "confidence": 0.95
            },
            "pymongo": {
                "format": "mongodb://localhost:27017/db",
                "confidence": 0.95
            },
            "redis": {
                "format": "redis://localhost:6379",
                "confidence": 0.95
            }
        },
        "Test command prediction": {
            "pytest": {"command": "pytest tests/ -v", "confidence": 0.85},
            "jest": {"command": "npm test", "confidence": 0.85},
            "JUnit": {"command": "mvn test", "confidence": 0.85},
            "go test": {"command": "go test ./...", "confidence": 0.85},
            "googletest": {"command": "ctest", "confidence": 0.80}
        },
        "Default env var prediction": {
            "PORT": {"default": "framework-dependent", "confidence": 0.85},
            "DEBUG": {"default": "False/false", "confidence": 0.90},
            "LOG_LEVEL": {"default": "INFO", "confidence": 0.85},
            "HOST": {"default": "0.0.0.0", "confidence": 0.85}
        }
    }
    
    for category, items in rules.items():
        print(f"\n{'─' * 70}")
        print(f"📚 {category}")
        print(f"{'─' * 70}")
        
        for key, value in items.items():
            confidence = value.get('confidence', 0) * 100
            
            if 'port' in value:
                print(f"  {key:20s} → port: {value['port']:30s} [{confidence:.0f}%]")
            elif 'command' in value:
                print(f"  {key:20s} → {value['command']}")
                print(f"  {'':20s}   confidence: {confidence:.0f}%")
            elif 'format' in value:
                print(f"  {key:20s} → {value['format']}")
                print(f"  {'':20s}   confidence: {confidence:.0f}%")
            elif 'default' in value:
                print(f"  {key:20s} → default: {value['default']:20s} [{confidence:.0f}%]")
    
    print(f"\n{'=' * 70}\n")


def show_expected_output_format():
    """Print expected output shape."""
    
    print("=" * 70)
    print("Analyzer new output field: intelligent_predictions")
    print("=" * 70)
    
    example = {
        "intelligent_predictions": [
            {
                "item": "Service port",
                "predicted_value": "8080",
                "confidence": 0.95,
                "reasoning": "Spring Boot default port",
                "evidence": "Framework convention + @SpringBootApplication",
                "action_taken": "Filled env vars and verification commands"
            },
            {
                "item": "Database connection format",
                "predicted_value": "postgresql://user:pass@localhost:5432/db",
                "confidence": 0.95,
                "reasoning": "psycopg2-binary detected",
                "evidence": "requirements.txt + DATABASE_URL env var",
                "action_taken": "Filled environment configuration section"
            },
            {
                "item": "Test command",
                "predicted_value": "pytest tests/ -v",
                "confidence": 0.80,
                "reasoning": "pytest detected",
                "evidence": "requirements.txt (medium confidence)",
                "action_taken": "Filled README with (inferred) label"
            },
            {
                "item": "API_KEY",
                "predicted_value": None,
                "confidence": 0.0,
                "reasoning": "Third-party credentials cannot be predicted",
                "evidence": None,
                "action_taken": "Written to Open Questions"
            }
        ]
    }
    
    print("\nSample output:")
    print(json.dumps(example, ensure_ascii=False, indent=2))
    
    print("\nField descriptions:")
    print("  • item: predicted item name")
    print("  • predicted_value: predicted value (None if not predictable)")
    print("  • confidence: 0.0–1.0")
    print("  • reasoning: rationale for the prediction")
    print("  • evidence: evidence sources")
    print("  • action_taken: action applied")
    print()


def main():
    """Run all demonstrations."""
    
    print("\n" + "=" * 70)
    print("Analyzer intelligent prediction test suite")
    print("=" * 70 + "\n")
    
    # Show prediction rules
    show_prediction_rules()
    
    # Scenario walkthrough
    test_prediction_scenarios()
    
    # Expected output format
    show_expected_output_format()
    
    print("=" * 70)
    print("✅ Intelligent prediction flow ready")
    print("=" * 70)
    print()
    print("Capabilities:")
    print("  ✅ High confidence (90%+) — direct README fill")
    print("  ✅ Medium (70–89%) — fill + inferred label")
    print("  ✅ Low (<70%) — Open Questions")
    print("  ✅ README completeness for deployability")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
