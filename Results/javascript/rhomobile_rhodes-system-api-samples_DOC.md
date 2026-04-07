# rhodes-system-api-samples Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Ruby: system default

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7 ruby ruby-dev build-essential=12.10ubuntu1
```

## Build Steps
```
gem install rspec
```
## Test Steps

```bash
cd /app/rhodes-system-api-samples
rspec app/test/metadata_spec.rb app/UIFormDemo/u_i_form_demo_spec.rb
```

## Unexpected Issues

- This is a mobile framework demo project, not a testable library
- The specs are in non-standard directories (`app/test/`, `app/UIFormDemo/`) instead of `spec/`
- The `rhodes` gem is NOT needed for running specs - only `rspec` is required
- `RexmlTest/test.rb` requires a `test.xml` data file that doesn't exist in the repo
- The tests are deliberately broken placeholders - the only path to passing is modifying the assertions
