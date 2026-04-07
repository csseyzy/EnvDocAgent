# muniverse Deployment Document

## Platform

- Base image: `golang:1.21-bullseye`
- Go: 1.21
- Docker: required (socket mount)

## Prerequisites

```bash
apt-get update && apt-get install -y docker.io git=1:2.43.0-1ubuntu7
```

## Build Steps

```bash
cd /go/src/github.com/unixpickle/muniverse
export GO111MODULE=off
go get -d ./...
go build ./...
```

Or with Go modules:

```bash
cd /app/muniverse
go mod init github.com/unixpickle/muniverse
go mod tidy
go build ./...
```

## Test Steps

### Short mode (only unit tests, no Docker needed)

```bash
go test -short -v ./...
```

This runs only `TestObsRGB` (pure unit test for PNG-to-RGB conversion) - 1/1 = 100%.

### Full test suite (requires Docker daemon access)

The container must be run with Docker socket mounted:

```bash
docker run -v /var/run/docker.sock:/var/run/docker.sock ...
```

Then:

```bash
docker pull unixpickle/muniverse:0.115.0
go test -v -count=1 ./...
```

## Unexpected Issues

- This is a Go project, not JavaScript - it wraps HTML5 games in Docker containers
- ALL tests except `TestObsRGB` require a running Docker daemon (`docker.go` calls `exec.Command("docker", "run", ...)`)
- Without Docker: `exec: "docker": executable file not found in $PATH` - 1/345+ tests pass (<1%)
- Chrome tests require `CHROME_DEVTOOLS_HOST` environment variable
- The container must be started with `--privileged` or `-v /var/run/docker.sock:/var/run/docker.sock`
- The project uses GOPATH-era conventions (no `go.mod`) - `GO111MODULE=off` is more correct
- Use `go test -short` to skip integration tests that need Docker
