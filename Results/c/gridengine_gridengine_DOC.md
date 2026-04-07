# gridengine Deployment Document

## Platform

- Base image: `ubuntu:22.04`
- Java: OpenJDK 11 (for GUI/JAPI components, optional)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.34.1-1ubuntu1 \
    build-essential=12.9ubuntu3 \
    gcc=4:11.2.0-1ubuntu1 \
    g++=4:11.2.0-1ubuntu1 \
    csh=20110502-7 \
    tcsh=6.24.00-1build1 \
    make=4.3-4.1build1 \
    libtirpc-dev=1.3.2-2ubuntu0.1 \
    libdb5.3-dev=5.3.28+dfsg1-0.8ubuntu3 \
    libncurses-dev=6.3-2ubuntu0.1 \
    libpam0g-dev=1.4.0-11ubuntu2 \
    libssl-dev=3.0.2-0ubuntu1 \
    libhwloc-dev=2.7.0-2ubuntu1 \
    libmotif-dev=2.3.8-2.1build3 \
    libxmu-dev=2:1.1.3-3 \
    libxt-dev=1:1.2.1-1 \
    libxext-dev=2:1.3.4-1build1 \
    libxpm-dev=1:3.5.12-1ubuntu0.22.04.2 \
    openjdk-11-jdk-headless=11.0.24+8-1ubuntu3~22.04 \
    ant=1.10.12-1 \
    pkg-config=0.29.2-1ubuntu3
```

## Build Steps

```bash
cd /app/gridengine/source

# Set environment variables
export SGE_ROOT=/opt/sge
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

# Create aimk.private with tirpc and BDB configuration
cat > aimk.private << 'EOF'
set XINCD = "-I/usr/include/tirpc"
set XLIBD = ""
set XLIBS = "-ltirpc"
set XLDFLAGS = ""
set BDB_HOME = "/usr"
set BDB_INCLUDE = "/usr/include"
set BDB_LIB = "/usr/lib/x86_64-linux-gnu"
EOF

# Generate zero-length dependency files (CRITICAL)
scripts/zerodepend

# Build the dependency tool
./aimk -only-depend

# Generate all dependency files
./aimk depend

# Build core system (minimal, no GUI)
./aimk -no-qmon -no-java -no-jemalloc -spool-classic
```

For full build with BDB spooling (remove `-spool-classic`):

```bash
./aimk -no-qmon -no-java -no-jemalloc
```

## Test Steps

No formal unit test suite exists. Verification is done by checking built binaries:

```bash
ls source/LINUXAMD64/qping
ls source/LINUXAMD64/sge_qmaster
ls source/LINUXAMD64/sge_execd
ls source/LINUXAMD64/sge_shepherd
ls source/LINUXAMD64/qsub
ls source/LINUXAMD64/qstat

source/LINUXAMD64/qping -help 2>&1 || true
```

## Unexpected Issues

- **`aimk` is a csh script** -- requires `csh` or `tcsh` to be installed (easily missed)
- **SunRPC removal from glibc >= 2.26** is the #1 build blocker on modern Linux -- must use `libtirpc-dev` and pass `-I/usr/include/tirpc` and `-ltirpc` via `aimk.private`
- **`scripts/zerodepend` step is absolutely critical** -- without it, every module's Makefile fails trying to include non-existent `*_dependencies` files
- `dist/util/arch` script may need patching if it doesn't identify the platform as `lx-amd64`
- Use `-spool-classic` to avoid Berkeley DB dependency for a minimal build
- Use `-no-qmon` to skip Motif/X11 GUI dependency
- Use `-no-java` to skip Java/ant dependency
- The codebase is very old (Sun Microsystems era, ~2001-2011) and makes assumptions about system headers that don't hold on modern Linux
