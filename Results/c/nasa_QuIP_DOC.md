# QuIP Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Minimal build mode is essential for headless/Docker environments. The project has many optional features (CUDA, OpenCL, OpenGL/X11, OpenCV, FFmpeg, ncurses, sound, camera SDKs) that should be disabled.

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7

apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 \
    build-essential=12.10ubuntu1 autoconf=2.71-3 automake=1:1.16.5-1.3ubuntu1 libtool=2.4.7-7build1 \
    pkg-config=1.8.1-2build1 bison=2:3.8.2+dfsg-1build2 flex=2.6.4-8.2build1 \
    tree grep sed gawk=1:5.2.1-2build3
```


## Build Steps

```bash
cd /app/project
autoreconf -i

ac_cv_type_off_t=yes ac_cv_type_gid_t=yes ac_cv_type_mode_t=yes \
ac_cv_type_pid_t=yes ac_cv_type_uid_t=yes \
./configure --enable-minimal-build --disable-tty-ctl --disable-use_history

make -j$(nproc)
```

Final link step requires linker group flags to resolve circular static library dependencies:

```bash
cd /app/project/src
make -j$(nproc) \
    quip_LDFLAGS='-L../libs -Wl,-rpath,/usr/local/cuda/lib -Wl,--start-group' \
    LIBS='-Wl,--end-group -lgcrypt -lm'
```

The `ac_cv_type_*=yes` variables are required to avoid type redefinition issues on Ubuntu 24.04.


## Test Steps

```bash
cd /app/project/src
make check
```


## Unexpected Issues

- **Circular static library dependency at link time:** The `quip` binary links ~30 internal static archives with circular dependencies. Must use `--start-group`/`--end-group` linker flags (see build step above).
- **Configure type-check cache overrides:** The configure script's type checks for `off_t`, `gid_t`, `mode_t`, `pid_t`, `uid_t` may need to be pre-set via `ac_cv_type_*=yes` environment variables.
- **`--enable-minimal-build` essential for Docker:** Without it, configure fails on missing optional dependencies (X11, OpenGL, CUDA, etc.).
- **`README.md` is essentially empty** (just `# QuIP`). Build instructions must be inferred from `configure.ac` and `README.packages`.
- **No source code modifications needed.** Build succeeds through configure flags and make variable overrides.
