# gjs Deployment Document

## Platform

- OS: ubuntu:24.04
- Container: Docker

## Prerequisites

```bash
dnf -y install git
dnf -y install 'dnf-command(builddep)'
dnf -y builddep mozjs128
dnf -y install \
    binutils cairo-gobject-devel clang=21.1.8 clang-tools-extra compiler-rt \
    dbus-daemon dbus-x11 diffutils gcc-c++=15.2.1 \
    glib2-devel glibc-gconv-extra glibc-locale-source \
    gnome-desktop-testing gobject-introspection-devel=1.84.0 \
    gtk3-devel=3.24.51 gtk4-devel=4.20.3 iwyu lcov libasan libubsan \
    llvm llvm-devel make meson=1.8.5 ninja-build=1.13.1 pkgconf=2.3.0 \
    python3-packaging python3-pip readline-devel rust=1.94.0 \
    sudo sysprof-devel=49.0 systemtap-sdt-devel systemtap-sdt-dtrace \
    valgrind which Xvfb xz
pip3 install lcov-cobertura==2.1.1
```

Build and install SpiderMonkey mozjs-140 from source:

```bash
cd /root
git clone --no-tags --depth 1 https://github.com/ptomato/mozjs.git -b mozjs140
cd mozjs && mkdir _build && cd _build
../js/src/configure --prefix=/usr --libdir=/usr/lib64 \
    --disable-jemalloc --with-system-zlib --with-intl-api --enable-debug
make -j$(nproc)
make install
cd /root && rm -rf mozjs
```


```bash
useradd -u 5555 -G wheel -ms /bin/bash user
sed -i -e 's/# %wheel/%wheel/' -e '0,/%wheel/{s/%wheel/# %wheel/}' /etc/sudoers
```

## Build Steps

```bash
git clone --depth 1 https://github.com/GNOME/gjs.git /app/gjs
cd /app/gjs && chown -R user:user /app
su - user -c "cd /app/gjs && meson setup _build --prefix=/usr --buildtype=debug"
su - user -c "cd /app/gjs && meson compile -C _build"
```

## Test Steps

```bash
su - user -c "cd /app/gjs && meson test -C _build"
```


## Unexpected Issues

- mozjs-140 not packaged: `dnf builddep mozjs128` only provides mozjs-128. GJS 1.87.90 requires mozjs-140, must build from source (`ptomato/mozjs` branch `mozjs140`).
- GTK tests fail in headless container: 8 tests SIGTRAP due to `G_DEBUG=fatal-warnings,fatal-criticals` without display server.
