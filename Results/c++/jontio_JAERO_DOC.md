# JAERO Deployment Document

## Platform

- **Base Image:** ubuntu:24.04
- **Build System:** qmake (Qt5)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    build-essential=12.10ubuntu1 \
    autoconf=2.71-3 \
    libtool=2.4.7-7build1 \
    cmake=3.28.3-1build7 \
    qtbase5-dev=5.15.13+dfsg-1ubuntu1 \
    qt5-qmake=5.15.13+dfsg-1ubuntu1 \
    qtbase5-dev-tools=5.15.13+dfsg-1ubuntu1 \
    qtmultimedia5-dev=5.15.13-1build1 \
    libqt5multimedia5-plugins=5.15.13-1build1 \
    libqt5svg5-dev=5.15.13-1build1 \
    libqt5sql5-sqlite=5.15.13+dfsg-1ubuntu1 \
    libqcustomplot-dev=2.1.1+dfsg1-2build1 \
    libqcustomplot2.1=2.1.1+dfsg1-2build1 \
    libvorbis-dev=1.3.7-1build3 \
    libogg-dev=1.3.5-3build1 \
    libzmq3-dev=4.3.5-1build2 \
    cpputest=4.0-2build1 \
    checkinstall=1.6.2+git20170426.d24a630-3ubuntu1 \
    git=1:2.43.0-1ubuntu7
```

```bash
# qmqtt
git clone --depth 1 https://github.com/emqx/qmqtt && cd qmqtt
qmake && make -j$(nproc) && make install && cd ..

# libacars
git clone --depth 1 https://github.com/szpajder/libacars && cd libacars
mkdir build && cd build && cmake .. && make -j$(nproc) && make install && cd ../..

# libcorrect
git clone --depth 1 https://github.com/quiet/libcorrect && cd libcorrect
mkdir build && cd build && cmake .. && make -j$(nproc) && make install && cd ../..

# JFFT (header-only)
git clone --depth 1 https://github.com/jontio/JFFT

# libaeroambe (mbelib)
git clone --depth 1 https://github.com/jontio/libaeroambe && cd libaeroambe
cd mbelib && mkdir build && cd build && cmake .. && make -j$(nproc) && make install && cd ../..
sed -i 's/\$\$\[QT_INSTALL_HEADERS\]/\/usr\/local\/include/g' libaeroambe.pro
sed -i 's/\$\$\[QT_INSTALL_LIBS\]/\/usr\/local\/lib\//g' libaeroambe.pro
qmake && make -j$(nproc) && make install && cd ..
```

## Build Steps

Fix libqcustomplot symlink:
```bash
ln -s /usr/lib/x86_64-linux-gnu/libQCustomPlot.so.2.1 /usr/lib/x86_64-linux-gnu/libqcustomplot.so
ldconfig
```


```bash
cd /app/JAERO/JAERO
qmake CONFIG+=CI && make -j$(nproc)
```

## Test Steps

```bash
cd /app/JAERO/JAERO
QT_QPA_PLATFORM=offscreen ./JAERO -v 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- CI unit tests are noted as broken in the project's own `ci-linux-build.sh` (`turnOnNewDeleteOverloads` not a member of `MemoryLeakWarningPlugin`)
- `QT_QPA_PLATFORM=offscreen` required since there's no display server in Docker
- Building 5 external dependencies from source is the main time cost
