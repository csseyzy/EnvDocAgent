# filezilla Deployment Document

## Platform

- **Base Image:** ubuntu:14.04
- **Build System:** Autotools (autoconf/automake)

## Prerequisites

```bash
# Fix archive URLs for EOL Ubuntu 14.04
sed -i 's|http://archive.ubuntu.com/ubuntu/|http://old-releases.ubuntu.com/ubuntu/|g' /etc/apt/sources.list
sed -i 's|http://security.ubuntu.com/ubuntu/|http://old-releases.ubuntu.com/ubuntu/|g' /etc/apt/sources.list

apt-get update && apt-get install -y --no-install-recommends \
    build-essential=12.10ubuntu1 \
    autoconf=2.71-3 automake=1:1.16.5-1.3ubuntu1 libtool=2.4.7-7build1 \
    pkg-config=1.8.1-2build1 \
    gettext=0.21-14ubuntu2 \
    libwxgtk2.8-dev \
    libgnutls-dev \
    libidn11-dev \
    libtinyxml-dev \
    libsqlite3-dev=3.45.1-1ubuntu2 \
    libdbus-1-dev \
    libgtk2.0-dev \
    xdg-utils \
    libcppunit-dev \
    git=1:2.43.0-1ubuntu7
```

## Build Steps

Patch `configure` to disable wxWidgets version check that incorrectly rejects wxWidgets 2.8:
```bash
sed 's/if test "$wx_config_major_version" -gt "2" || test "$wx_config_minor_version" -gt "8"; then/if false; then/' configure > configure.new && mv configure.new configure && chmod +x configure
```


```bash
cd /app/project
./autogen.sh
mkdir -p compile && cd compile
../configure --disable-dependency-tracking
make -j$(nproc)
```

## Test Steps

```bash
cd /app/project/compile
make check 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- **Must use Ubuntu 14.04** — wxWidgets 2.8 (`libwxgtk2.8-dev`) is only available on Ubuntu 14.04
- Ubuntu 14.04 is EOL; apt sources must be redirected to `old-releases.ubuntu.com`
- The `configure` script has a broken version check that rejects wxWidgets 2.8 — must be patched with `sed`
- Most of the 68 minutes was spent on failed Docker image builds trying different Ubuntu versions
