# caliper-benchmarks Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Node.js: 20.x
- Go: 1.20
- Java: OpenJDK 8
- Docker: required (Docker-in-Docker or socket mount)

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7 curl=8.5.0-2ubuntu10.8 wget=1.21.4-1ubuntu4 build-essential=12.10ubuntu1 python3=3.12.3-0ubuntu2 openjdk-8-jdk=8u402-ga-8build1 docker.io docker-compose-v2
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs
wget -q https://go.dev/dl/go1.20.14.linux-amd64.tar.gz
tar -C /usr/local -xzf go1.20.14.linux-amd64.tar.gz && rm go1.20.14.linux-amd64.tar.gz
export PATH="/usr/local/go/bin:${PATH}"
```

## Build Steps

```bash
cd /app/caliper-benchmarks
npm install --only=prod @hyperledger/caliper-cli@0.6.0
npx caliper bind --caliper-bind-sut fabric:fabric-gateway
```

## Test Steps

Running actual benchmarks requires a Hyperledger Fabric network (Docker-in-Docker):

```bash
# Download Fabric samples + binaries
curl -sSL https://raw.githubusercontent.com/hyperledger/fabric/main/scripts/bootstrap.sh | bash -s -- 2.5.7

# Start Fabric network
cd fabric-samples/test-network
./network.sh up createChannel -s couchdb

# Deploy chaincode & run benchmark
cd ../../caliper-benchmarks
.github/scripts/deploy-chaincode.sh go fabcar
.github/scripts/run-benchmark.sh fabcar
```

## Unexpected Issues

- This project requires **Docker-in-Docker** or Docker socket mounting (`-v /var/run/docker.sock:/var/run/docker.sock`) to run a Fabric network
- The container must be started with `--privileged` for Docker access
- Without a running Fabric network, only CLI installation can be verified (`npx caliper --version`)
- The CI workflow (`.github/workflows/fabric-tests.yaml`) shows the full test flow
- This is fundamentally an infrastructure-level constraint, not a code issue
