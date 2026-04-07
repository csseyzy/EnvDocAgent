"""
README Template Specification — five-section format.

Every generated README must contain exactly these five sections in order:
  1. Platform
  2. Prerequisites
  3. Build Steps
  4. Test Steps
  5. Unexpected Issues
"""

TEMPLATE_SPEC = """
# README Template Specification

The generated README must contain **exactly five sections**, in the order below.
All commands must be directly executable — no placeholders, no choices.

============================================================
## Section 1 — Platform
============================================================

Describes the most fundamental execution requirements:
  • Operating system (e.g., Ubuntu 22.04)
  • Programming language runtime and version (e.g., Python 3.10, GCC 12)
  • Other global platform constraints (e.g., x86_64 architecture, CUDA 12.0)

Rules:
  - Versions must be explicit (3.10, not 3.x or latest).
  - State one concrete OS; do not list alternatives.
  - If the project is OS-agnostic, state "Linux (Ubuntu 22.04 recommended)".

Example:
```
## Platform
- OS: Ubuntu 22.04 (x86_64)
- Compiler: GCC 12
- CMake: 3.22
```

============================================================
## Section 2 — Prerequisites
============================================================

Given the platform above, lists project-specific dependencies that must be
installed before the project can be built or executed:
  • Required packages and libraries (with versions)
  • External services (e.g., PostgreSQL 15, Redis 7)
  • Installation commands for every prerequisite

Rules:
  - Every prerequisite must have an install command.
  - Commands must be directly executable (no placeholders).
  - Use the platform's native package manager (apt, brew, etc.).
  - If a version is pinned upstream, state it; otherwise mark
    "(constraint: distro-provided)" and give the install command.

Example:
```
## Prerequisites
```bash
sudo apt-get update
sudo apt-get install -y build-essential libssl-dev libcurl4-openssl-dev
pip install pytest==7.4.0
```
```

============================================================
## Section 3 — Build Steps
============================================================

Ordered procedures for initializing or compiling the project,
given the platform and prerequisites above:
  • Clone / download
  • Configuration (cmake, ./configure, environment variables, etc.)
  • Compilation / installation
  • Any post-build initialization (database migration, asset generation, etc.)

Rules:
  - Every step must be a directly executable command.
  - Commands must be in correct dependency order.
  - No placeholders — use the actual repo URL, actual directory names, etc.
  - If environment variables are needed, provide concrete example values.
  - Single path only — no "or" alternatives.

Example:
```
## Build Steps
```bash
git clone https://github.com/owner/repo.git
cd repo

mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
sudo make install
```
```

============================================================
## Section 4 — Test Steps
============================================================

Validation procedures to confirm the environment is correctly set up:
  • Commands to run tests or verify the build
  • Expected output or success criteria for each command

Rules:
  - Every test command must state its expected output or success condition.
  - If the project has a test suite, use it.
  - If no test suite exists, provide a minimal smoke-test command
    (e.g., run the binary with --version or --help and state expected output).

Example:
```
## Test Steps
```bash
cd build
ctest --output-on-failure
# Expected: "100% tests passed, 0 tests failed"

repo_binary --version
# Expected: "repo_binary 1.2.3"
```
```

============================================================
## Section 5 — Unexpected Issues
============================================================

External obstacles that may arise during setup but are NOT caused by
defects in the project itself or incompleteness in its documentation:
  • Permission restrictions (e.g., needs sudo, SELinux policies)
  • Network failures (e.g., package mirror unreachable)
  • Host-specific system limitations (e.g., low memory, missing kernel module)

Rules:
  - Each issue must have: symptom, cause, and a concrete fix command.
  - Only list issues external to the project.
  - If no known issues exist, write "No known unexpected issues."

Example:
```
## Unexpected Issues

Issue: "Permission denied" when running make install
Cause: Requires root privileges
Fix: sudo make install

Issue: cmake fails with "Could NOT find OpenSSL"
Cause: libssl-dev not installed
Fix: sudo apt-get install -y libssl-dev
```

============================================================
## Output Format Rules
============================================================

Prohibited:
  ❌ Placeholders: <port>, <name>, <url>, your_xxx, xxx_here
  ❌ Ambiguous versions: 3.x, latest, >=3.9
  ❌ Multiple choices: "can use A or B", "alternatively"
  ❌ Manual-action instructions: "please replace", "please modify"
  ❌ Fluff: feature overviews, welcome text, badges

Required:
  ✅ Concrete values everywhere (port 8000, not <port>)
  ✅ Every command directly copy-pasteable
  ✅ Single path — one way to build, one way to test
  ✅ Expected output stated for every verification command
  ✅ Explicit version numbers

============================================================
## Checklist (before finalising)
============================================================

- [ ] Platform section lists OS, language runtime, versions
- [ ] Prerequisites section has install commands for every dependency
- [ ] Build Steps section has ordered, executable commands
- [ ] Test Steps section has commands with expected output
- [ ] Unexpected Issues section lists external obstacles or states "none"
- [ ] Zero placeholders in the entire document
- [ ] Zero "or" alternatives
- [ ] All version numbers are explicit
"""
