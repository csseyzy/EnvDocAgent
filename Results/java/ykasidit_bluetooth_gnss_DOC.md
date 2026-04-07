# bluetooth_gnss Deployment Document

## Platform

- **Base Image:** `ubuntu:24.04`
- **JDK:** OpenJDK 17 (`openjdk-17-jdk` = 17.0.18+8-1~24.04.1)

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7 \
    openjdk-17-jdk=17.0.18+8-1~24.04.1 \
    curl=8.5.0-2ubuntu10 \
    unzip=6.0-28ubuntu4 \
    zip=3.0-13build1 \
    wget=1.21.4-1ubuntu4 \
    ca-certificates=20240203
```

## Build Steps

### Install Android SDK

```bash
export ANDROID_SDK_ROOT=/opt/android-sdk
mkdir -p /opt/android-sdk/cmdline-tools
curl -fsSL https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip -o /tmp/cmdline-tools.zip
unzip -q /tmp/cmdline-tools.zip -d /opt/android-sdk/cmdline-tools
mv /opt/android-sdk/cmdline-tools/cmdline-tools /opt/android-sdk/cmdline-tools/latest
yes | /opt/android-sdk/cmdline-tools/latest/bin/sdkmanager --licenses
/opt/android-sdk/cmdline-tools/latest/bin/sdkmanager "platforms;android-36" "build-tools;36.0.0" "platform-tools"
```

### Install Flutter SDK

```bash
git clone --depth 1 -b stable https://github.com/flutter/flutter /opt/flutter
/opt/flutter/bin/flutter config --no-analytics
/opt/flutter/bin/flutter precache --android
```

### Create dummy keystore and key.properties

```bash
keytool -genkeypair -keystore /app/dummy.keystore -storepass dummypassword -keypass dummypassword \
    -alias bluetooth_gnss -keyalg RSA -keysize 2048 -validity 10000 \
    -dname "CN=Dummy, OU=Dev, O=Org, L=City, S=State, C=US"

cat > /app/project/key.properties << 'EOF'
storePassword=dummypassword
keyPassword=dummypassword
keyAlias=bluetooth_gnss
storeFile=/app/dummy.keystore
EOF
```

### Source Modification Required

Add to `android/app/build.gradle` inside the `android {}` block:

```groovy
testOptions {
    unitTests.returnDefaultValues = true
}
```

### Flutter pub get

```bash
cd /app/project
mkdir -p rust_builder/lib
/opt/flutter/bin/flutter pub get
```



## Test Steps


```bash
cd /app/project/android
ANDROID_SDK_ROOT=/opt/android-sdk JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 \
    ./gradlew :app:testDebugUnitTest --no-daemon
```

## Unexpected Issues

- `build.gradle` unconditionally loads `key.properties` — crashes without it.
- `rust_builder/lib` directory must exist or `flutter pub get` fails.
- `test_ntrip_conn_mgr` connects to live NTRIP server `caster.centipede.fr:2101` — network-dependent.
- 3 androidTest files are instrumented tests requiring Android device/emulator.
