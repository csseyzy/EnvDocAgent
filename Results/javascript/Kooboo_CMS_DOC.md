# CMS (Kooboo) Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Runtime: Mono (for .NET Framework on Linux)

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7 gnupg=2.4.4-2ubuntu17 ca-certificates=20240203 wget=1.21.4-1ubuntu4 curl=8.5.0-2ubuntu10.8 unzip=6.0-28ubuntu4
gpg --homedir /tmp --no-default-keyring --keyring /usr/share/keyrings/mono-official-archive-keyring.gpg \
    --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF
echo "deb [signed-by=/usr/share/keyrings/mono-official-archive-keyring.gpg] https://download.mono-project.com/repo/ubuntu stable-focal main" \
    | tee /etc/apt/sources.list.d/mono-official-stable.list
apt-get update && apt-get install -y mono-complete mono-devel msbuild nunit-console ca-certificates-mono
```

## Build Steps

Use the **Mono-specific solution file** (NOT `Kooboo.CMS.sln`):

```bash
cd /app/CMS/Kooboo.CMS
nuget restore Kooboo.CMS.Mono.sln
msbuild Kooboo.CMS.Mono.sln /p:Configuration=Debug /t:Build /p:PostBuildEvent=
```

## Test Steps

```bash
nunit-console Kooboo.CMS.Sites.Tests/bin/Debug/Kooboo.CMS.Sites.Tests.dll
```

## Unexpected Issues

- All 8 test projects reference `Microsoft.VisualStudio.QualityTools.UnitTestFramework` (MSTest v10.0.0.0) - Windows-only, unavailable on Mono
- Test compilation fails with 108 errors: `The type or namespace name 'VisualStudio' does not exist in the namespace 'Microsoft'`
- Add `/p:PostBuildEvent=` to suppress Windows-specific post-build `copy` commands that fail on Linux
- Converting MSTest to NUnit requires modifying test attributes and references in all test projects
