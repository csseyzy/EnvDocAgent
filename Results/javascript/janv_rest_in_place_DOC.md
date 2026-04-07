# rest_in_place Deployment Document

## Platform

- Base image: `ruby:2.3`
- Ruby: 2.3 (included in image)
- Rails: ~> 3.2

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7
apt-get update && apt-get install -y --no-install-recommends tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 curl=8.5.0-2ubuntu10.8 wget=1.21.4-1ubuntu4 sqlite3 libsqlite3-dev=3.45.1-1ubuntu2 build-essential=12.10ubuntu1 nodejs
```


```bash
apt-get update && apt-get install -y chromium chromium-driver xvfb=2:21.1.12-1ubuntu1
```

## Build Steps

```bash
cd /app/rest_in_place/testapp
gem install bundler -v 1.17.3
bundle install
bundle exec rake db:setup
```

## Test Steps

Start the Rails test server:

```bash
cd /app/rest_in_place/testapp
bundle exec rails server -b 0.0.0.0 -p 3000 &
sleep 10
```

Run Jasmine tests using headless Chromium:

```bash
xvfb-run chromium --headless --disable-gpu --no-sandbox --virtual-time-budget=30000 --dump-dom http://localhost:3000/jasmine
```

Optionally install selenium-webdriver for more comprehensive testing:

```bash
gem install selenium-webdriver
```

## Unexpected Issues

- This is a Ruby/Rails project, not a JavaScript project — uses Bundler + Rails 3.2
- Requires `ruby:2.3` base image; newer Ruby versions may be incompatible with Rails 3.2 and older gems
- Jasmine tests require a browser environment (Chromium + Xvfb)
- Dependencies in `testapp/Gemfile` are outdated; `bundle install` may require multiple attempts
- Bundler version must be 1.17.x; incompatible with Bundler 2.x
