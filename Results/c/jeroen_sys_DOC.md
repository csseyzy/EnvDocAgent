# sys (R package) Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- R: 4.3.x

## Prerequisites

```bash
apt-get update && apt-get install -y \
    git=1:2.43.0-1ubuntu7.3 \
    r-base=4.3.3-2build2 \
    r-base-dev=4.3.3-2build2 \
    pandoc=3.1.3+ds-2 \
    libcurl4-openssl-dev=8.5.0-2ubuntu10.8 \
    libssl-dev=3.0.13-0ubuntu3.7 \
    libxml2-dev=2.9.14+dfsg-1.3ubuntu3.7 \
    zlib1g-dev=1:1.3.dfsg-3.1ubuntu2
```

## Build Steps

```bash
cd /app/sys
Rscript -e "install.packages(c('remotes','rcmdcheck','testthat','unix'), repos='https://cloud.r-project.org')"
Rscript -e "remotes::install_deps(dependencies = TRUE)"
```

## Test Steps

```bash
cd /app/sys
Rscript -e "rcmdcheck::rcmdcheck(args = c('--no-manual','--as-cran'), error_on = 'error')"
```

Or explicitly:

```bash
R CMD build .
R CMD check sys_*.tar.gz --no-manual
```

## Unexpected Issues

- `rcmdcheck` runs the full test suite as part of `R CMD check` -- the "no tests" report is incorrect
- The `testthat` and `unix` packages must be installed for tests to run
