# GearVRf-Demos Deployment Document

## Platform

- **Base Image:** `ubuntu:22.04`
- **JDK:** OpenJDK 8 for Gradle builds, OpenJDK 17 for `sdkmanager`

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.34.1-1ubuntu1 \
    openjdk-8-jdk=8u392-ga-1~22.04 \
    openjdk-17-jdk=17.0.9+9-1~22.04 \
    wget=1.21.2-2ubuntu1 \
    unzip=6.0-26ubuntu3 \
    zip=3.0-12build2 \
    curl=7.81.0-1ubuntu1 \
    ca-certificates=20230311ubuntu0.22.04.1
```

## Build Steps

- `build.gradle`: Replace `jcenter()` with `mavenCentral()` (jcenter is sunset).
- `common.gradle`: Replace `jcenter()` with `mavenCentral()`.
- `common.gradle` line 33: Add null-safe default for `appName`: `resValue 'string', 'app_name', System.getProperty("appName") ?: "GVRDemo"`.


### Step 1: Set up Android SDK

```bash
export ANDROID_SDK_ROOT=/opt/android-sdk
mkdir -p $ANDROID_SDK_ROOT/cmdline-tools
wget -O /tmp/cmdline-tools.zip https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
unzip -q /tmp/cmdline-tools.zip -d $ANDROID_SDK_ROOT/cmdline-tools
mv $ANDROID_SDK_ROOT/cmdline-tools/cmdline-tools $ANDROID_SDK_ROOT/cmdline-tools/latest

export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
yes | sdkmanager --sdk_root=$ANDROID_SDK_ROOT --licenses
sdkmanager --sdk_root=$ANDROID_SDK_ROOT "platform-tools" "platforms;android-26" "build-tools;26.0.3"
```

### Step 2: Configure Gradle properties

```bash
echo "sdk.dir=$ANDROID_SDK_ROOT" > /app/project/local.properties

mkdir -p /root/.gradle
cat > /root/.gradle/gradle.properties << 'EOF'
org.gradle.daemon=true
org.gradle.jvmargs=-Xmx2048M
org.gradle.parallel=true
useLocalDependencies=false
backend_monoscopic=true
backend_daydream=false
backend_oculus=false
EOF
```

### Step 3: Build a single demo module

```bash
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
cd /app/project
./gradlew :gvr-simplesample:app:assembleDebug -DappName=gvr-simplesample
```
## Test Steps

```bash
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
cd /app/project
./gradlew :gvr-simplesample:app:assembleDebug -DappName=gvr-simplesample 2>&1 | tail -5
ls -la gvr-simplesample/app/build/outputs/apk/debug/*.apk && echo "BUILD VERIFICATION: APK created successfully"
```

## Unexpected Issues

- **`org.gearvrf:framework:4.0.1-SNAPSHOT` is likely no longer available** on Sonatype snapshots.
- Samsung's GearVRf framework is discontinued; artifacts may be permanently unavailable.
- `common.gradle` references `http://google.bintray.com/googlevr` which is defunct (Bintray shut down).
- Without the GearVRf framework AARs, this project **cannot be built** — it is effectively an archived/dead project.
- No test suites exist in this project.
