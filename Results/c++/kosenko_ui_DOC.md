# ui (Boost.UI) Deployment Document

## Platform

- OS: Ubuntu 16.04 (xenial)
- Dependencies Framework: Boost 1.77.0, wxWidgets 3.0.5

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7 \
    build-essential=12.1ubuntu2 \
    libgtk2.0-dev=2.24.30-1ubuntu1.16.04.2 \
    libwebkitgtk-dev=2.4.11-0ubuntu0.1 \
    python=2.7.12-1~16.04 \
    xvfb=2:1.18.4-0ubuntu0.12 \
    wget=1.21.4-1ubuntu4 \
    bzip2=1.0.6-8ubuntu0.2 \
    realpath
```

Install Microsoft core fonts (required by font-related tests):

```bash
sh -c "echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | debconf-set-selections"
apt-get install -y msttcorefonts
```

- `build-essential` (12.1ubuntu2) — GCC/g++ C++ toolchain
- `libgtk2.0-dev` (2.24.30) — GTK+ 2.0 development headers, required by wxWidgets GTK backend
- `libwebkitgtk-dev` (2.4.11) — WebKitGTK development headers, required by wxWidgets webview widget
- `python` (2.7.12) — Python 2, required by `depinst.py` dependency installer
- `xvfb` (1.18.4) — virtual framebuffer X server for headless GUI tests

## Build Steps

Clone Boost 1.77.0 superproject and set up the UI library:

```bash
git clone -b boost-1.77.0 --depth 1 https://github.com/boostorg/boost.git boost-root
cd boost-root
git submodule update --init --checkout --depth 1
git submodule update --init tools/build
git submodule update --init libs/config
git submodule update --init tools/boostdep

git clone --depth 1 https://github.com/kosenko/ui.git libs/ui

python tools/boostdep/depinst/depinst.py ui
./bootstrap.sh
./b2 headers
```

Build wxWidgets 3.0.5:

```bash
wget https://github.com/wxWidgets/wxWidgets/releases/download/v3.0.5/wxWidgets-3.0.5.tar.bz2
tar -xf wxWidgets-3.0.5.tar.bz2
mkdir build-wx && cd build-wx
../wxWidgets-3.0.5/configure --disable-optimise --enable-debug=max
make -j$(nproc)
export WX_CONFIG=$(realpath .)/wx-config
cd ..
```

Build Boost.UI library:

```bash
echo "using gcc : : g++ : <cxxflags>-std=c++17 ;" > ~/user-config.jam
./b2 libs/ui/build toolset=gcc
```

## Test Steps

```bash
cd boost-root
xvfb-run ./b2 libs/ui/test toolset=gcc
```

## Unexpected Issues

- The `build/` directory referenced in `Jamfile.v2` and `README.md` (`build/README.md`) is not present in the repository checkout; the library still builds via `./b2 libs/ui/build`.
- GUI tests require a display server; use `xvfb-run` on headless Linux to provide a virtual framebuffer.
- `datetime_test` links against `Boost.Chrono`; ensure Boost.Chrono submodule is pulled by `depinst.py`.
- wxWidgets build can take significant time; `make -j$(nproc)` can be used to parallelize.
- `libwebkitgtk-dev` (WebKit1 GTK2) is only available on Ubuntu 16.04 and older; Ubuntu 18.04+ removed this package, making xenial the required base image.
