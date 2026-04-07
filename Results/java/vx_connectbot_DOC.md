# connectbot (VX ConnectBot) Deployment Document

## Platform

- **Base Image:** `ubuntu:24.04`
- **JDK:** OpenJDK 8 (`openjdk-8-jdk` = 8u482-ga~us1-0ubuntu1~24.04) for APK signing + OpenJDK 17 for `sdkmanager`

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7 \
    openjdk-8-jdk=8u482-ga~us1-0ubuntu1~24.04 \
    openjdk-17-jdk=17.0.13+11-2ubuntu1~24.04 \
    ant=1.10.14-1 \
    wget=1.21.4-1ubuntu4 \
    unzip=6.0-28ubuntu4 \
    zip=3.0-13build1 \
    curl=8.5.0-2ubuntu10 \
    ca-certificates=20240203
```

## Build Steps

### Step 1: Install Android SDK

```bash
export ANDROID_SDK_ROOT=/opt/android-sdk
mkdir -p $ANDROID_SDK_ROOT/cmdline-tools
wget -O cmdline-tools.zip https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
unzip -q cmdline-tools.zip -d $ANDROID_SDK_ROOT/cmdline-tools
mv $ANDROID_SDK_ROOT/cmdline-tools/cmdline-tools $ANDROID_SDK_ROOT/cmdline-tools/latest

export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
yes | sdkmanager --licenses
sdkmanager "platform-tools" "platforms;android-15" "build-tools;28.0.3"
```

### Step 2: Install legacy SDK tools

```bash
cd $ANDROID_SDK_ROOT
wget -O tools.zip https://dl.google.com/android/repository/tools_r25.2.5-linux.zip
unzip -q tools.zip && rm tools.zip
```

### Step 3: Build with Java 8

```bash
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
cd /app/project
android update project -p .
ant -Djavac.source=1.7 -Djavac.target=1.7 clean debug
```

### Step 4: Static analysis

```bash
ant lint-html
```


## Test Steps

```bash
cd /app/project/tests
android update test-project -p . -m ..
ant debug
adb install -r ../bin/VX\ ConnectBot-debug.apk
adb install -r bin/VX\ ConnectBot-tests-debug.apk
adb shell am instrument -w org.vx.connectbot.tests/android.test.InstrumentationTestRunner
```

## Unexpected Issues

- Requires Java 8 for APK signing (`NoClassDefFoundError: sun/misc/BASE64Encoder` with Java 11+).
- Legacy SDK Tools r25.2.5 must be downloaded separately (not available via `sdkmanager`).
- `git describe` fails in shallow clones (version string gets "fatal: No names found").
- No JVM unit tests exist; only instrumentation tests requiring a device.
- `res/values-ru/strings.xml` may contain malformed XML that needs fixing.
