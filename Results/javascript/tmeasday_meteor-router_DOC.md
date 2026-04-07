# meteor-router Deployment Document

## Platform

- Base image: `ubuntu:20.04`
- Node.js: 14.x
- Meteor: 1.12.2 (NOT latest - the project is from 2012)

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.25.1-1ubuntu3 curl=7.68.0-1ubuntu2 python2 build-essential=12.8ubuntu1
curl -fsSL https://deb.nodesource.com/setup_14.x | bash -
apt-get install -y nodejs
```

## Build Steps


The `package.js` uses deprecated Meteor 0.5.x APIs that must be updated for Meteor 1.x:

- Replace `Package.on_use` with `Package.onUse`
- Replace `Package.on_test` with `Package.onTest`
- Replace `api.add_files` with `api.addFiles`
- Remove `page-js-ie-support` dependency (doesn't exist)
- Remove `HTML5-History-API` weak dependency (invalid name)

In test files:
- Replace `Meteor.flush()` with `Tracker.flush()` (8+ occurrences in `tests/router_client_tests.js`)
- Replace `Meteor.http.get()` with `HTTP.get()` in server tests


```bash
curl https://install.meteor.com/?release=1.12.2 | sh
```

## Test Steps

```bash
cd /app
METEOR_ALLOW_SUPERUSER=1 meteor test-packages router --once --driver-package=test-in-console
```

## Unexpected Issues

- **12-year version gap**: package designed for Meteor 0.5.x (2012), latest Meteor is 3.4 (2025)
- `meteor test-packages` hung indefinitely on Meteor 3.4 due to unresolvable old package dependencies
- Even with Meteor 1.x, significant source modifications are needed for deprecated APIs
- The README itself says the project is **deprecated** in favor of Iron Router
- This project may be fundamentally untestable on any modern Meteor version without significant rewrites
