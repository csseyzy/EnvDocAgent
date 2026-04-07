# NiL.JS Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- .NET SDK: 9.0
- Runtime: Mono (for net48 target framework tests)

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7
apt-get update && apt-get install -y --no-install-recommends tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 wget=1.21.4-1ubuntu4 curl=8.5.0-2ubuntu10.8
```

```bash
wget https://dot.net/v1/dotnet-install.sh -O dotnet-install.sh
chmod +x ./dotnet-install.sh
./dotnet-install.sh --channel 9.0 --install-dir /usr/share/dotnet
ln -s /usr/share/dotnet/dotnet /usr/local/bin/dotnet
rm dotnet-install.sh
```

## Build Steps

```bash
apt-get update && apt-get install -y libicu-dev
apt-get update && apt-get install -y mono-complete
```

```bash
git clone --recurse-submodules https://github.com/nilproject/NiL.JS nil_js
cd nil_js
```

Edit `NiL.JS/NiL.JS.csproj` to remove `net10.0` from `<TargetFrameworks>` (not supported by SDK 9).

Edit `Tests/Tests.csproj` to change `net10.0` to `net9.0` in `<TargetFrameworks>`:

Change `<TargetFrameworks>net48;net10.0</TargetFrameworks>` to `<TargetFrameworks>net48;net9.0</TargetFrameworks>`.

Build:

```bash
cd NiL.JS && dotnet clean && dotnet restore
dotnet build --no-restore -c Release -property:SignAssembly=false -property:PublicSign=false
```

## Test Steps

```bash
cd /app/nil_js/Tests
dotnet run --project ../Utility/tiny-t4/ --framework net9.0
```

Using the net48 target framework (requires Mono):

```bash
cd /app/nil_js/Tests
dotnet test bin/Release/net48/Tests.dll --logger "console;verbosity=normal" --logger "trx;LogFileName=test_results.trx"
```

## Unexpected Issues

- The upstream csproj contains the `net10.0` target framework, which is not supported by .NET SDK 9 — must be changed to `net9.0`
- Tests targeting net9.0 have numerous CS1504 errors (path separator issues); use net48 + Mono to run tests instead
- Without Mono installed, net48 tests fail with a "mono host not found" error
- The `-property:SignAssembly=false -property:PublicSign=false` flags are required to skip assembly signing
- A small number of tests (ShouldProcessCodeTypeSwitch, PerformanceTest, etc.) may fail
