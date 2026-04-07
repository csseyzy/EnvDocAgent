# meteor-famous-views Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Meteor: latest (via install.meteor.com)

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7 curl=8.5.0-2ubuntu10.8 build-essential=12.10ubuntu1 python3=3.12.3-0ubuntu2 libfontconfig1 ca-certificates=20240203
```

## Build Steps


The `package.js` requires `jag:pince@0.0.9` which no longer exists on Atmosphere (only `0.0.5` is available):

```bash
cd /app/meteor-famous-views
sed -i "s/jag:pince@0.0.9/jag:pince@0.0.5/" package.js
```


```bash
curl https://install.meteor.com/ | sh
export PATH="/root/.meteor:$PATH"
export METEOR_ALLOW_SUPERUSER=1
```

## Test Steps

```bash
export METEOR_ALLOW_SUPERUSER=1
cd /app/meteor-famous-views
meteor test-packages ./ --once --driver-package test-in-console
```

## Unexpected Issues

- **Atmosphere package version conflict**: `jag:pince@0.0.9` is required but only `0.0.5` is available - must relax the version constraint
- Without the version fix, `meteor test-packages` fails with `Constraint jag:pince@0.0.9 is not satisfied by jag:pince 0.0.5`
- The `--once` flag is critical - without it, Meteor enters watch mode and hangs forever
- The project is deprecated/unmaintained - its Atmosphere dependencies have been removed/downgraded
- The `.travis.yml` references an external CI script (`curl -L http://git.io/ejPSng | /bin/sh`) from 2015 that installed a specific old Meteor version
- Using an older Meteor version (e.g., 1.2.x) might resolve additional Atmosphere package availability issues
