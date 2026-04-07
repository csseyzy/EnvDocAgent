# titanium_desktop Deployment Document

## Platform

- **Base Image:** ubuntu:18.04
- **Build System:** SCons (Python 2.7)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    build-essential=12.4ubuntu1 \
    python2.7=2.7.17-1~18.04ubuntu1.13 \
    scons=3.0.1-1 \
    git=1:2.17.1-1ubuntu0.18 \
    libpoco-dev=1.8.0.1-1ubuntu4 \
    libgtk2.0-dev=2.24.32-1ubuntu1 \
    libxml2-dev=2.9.4+dfsg1-6.1ubuntu1.9 \
    libcairo2-dev=1.15.10-2ubuntu0.1 \
    libpango1.0-dev=1.40.14-1ubuntu0.1 \
    libglib2.0-dev=2.56.4-0ubuntu0.18.04.9 \
    libx11-dev=2:1.6.4-3ubuntu0.4 \
    libcurl4-openssl-dev=7.58.0-2ubuntu3.24 \
    uuid-dev=2.31.1-0.4ubuntu3.7 \
    pkg-config=0.29.1-0ubuntu2
```

## Build Steps

```bash
cd /app/project

# Fix thirdparty symlinks
mkdir -p kroll/thirdparty-linux-x86_64-r31/poco
ln -s /usr/include kroll/thirdparty-linux-x86_64-r31/poco/include
ln -s /usr/lib/x86_64-linux-gnu kroll/thirdparty-linux-x86_64-r31/poco/lib

python2.7 $(which scons)
```

## Test Steps


```bash
cd /app/project
python2.7 $(which scons) --help | head -5 && echo "BUILD SYSTEM OK"
```

## Unexpected Issues

- **UNFIXABLE without major porting effort**: This project depends on WebKit 1.x (not WebKit2GTK). The API is completely different and the thirdparty binaries were proprietary and no longer available.
- The project is archived and unmaintained since ~2012
- Python 2.7 and SCons 3.x are required
- Even with all symlinks correct, compilation will fail on WebKit API incompatibilities
- Recommend marking as **unbuildable**
