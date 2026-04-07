# Thetis Deployment Document

## Platform

- Base image: `ubuntu:24.04`

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7.3 \
    build-essential=12.10ubuntu1 \
    cmake=3.28.3-1build7 \
    make=4.3-4.1build2 \
    pkg-config=1.8.1-2build1 \
    libasound2-dev=1.2.11-1ubuntu0.2
```

## Build Steps


```bash
cmake -S "/app/thetis/Project Files/lib/portaudio-19.7.0" \
      -B "/app/thetis/Project Files/lib/portaudio-19.7.0/build" \
      -DPA_BUILD_TESTS=ON -DPA_BUILD_EXAMPLES=OFF
cmake --build "/app/thetis/Project Files/lib/portaudio-19.7.0/build"
```

## Test Steps

```bash
# Pure computational test (no audio hardware needed)
"/app/thetis/Project Files/lib/portaudio-19.7.0/build/test/patest_converters"

# Initialize/terminate lifecycle test
"/app/thetis/Project Files/lib/portaudio-19.7.0/build/test/patest_init"
```

## Unexpected Issues

- The main Thetis application is a C#/.NET Windows Forms app -- cannot be built on Linux
- Only the bundled PortAudio library is buildable and testable on Linux
- Most PortAudio tests (`patest_sine*`, `patest_wire`, etc.) require audio hardware and will fail in Docker
- `patest_converters` is the best test -- pure computational, no audio devices needed
- `patest_init` tests Pa_Initialize()/Pa_Terminate() and should work without audio devices
