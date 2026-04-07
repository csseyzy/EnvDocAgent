# mocha-casperjs Deployment Document

## Platform

- OS: Ubuntu 24.04
- Runtime: PhantomJS 2.1.1
- Container: Docker

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7
apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 \
    curl=8.5.0-2ubuntu10.8 wget=1.21.4-1ubuntu4 \
    build-essential=12.10ubuntu1 \
    libfontconfig1 libfreetype6 libssl-dev=3.0.13-0ubuntu3.7 \
    bzip2=1.0.8-5.1build0.1

curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

apt-get update && apt-get install -y python3=3.12.3-0ubuntu2.1 python-is-python3=3.11.4-1
```

Install PhantomJS 2.1.1 binary and OpenSSL 1.1 compatibility library:

```bash
wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
tar xvjf phantomjs-2.1.1-linux-x86_64.tar.bz2
mv phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin/
chmod +x /usr/local/bin/phantomjs
rm -rf phantomjs-2.1.1-linux-x86_64*

wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2_amd64.deb
dpkg -i libssl1.1_1.1.1f-1ubuntu2_amd64.deb

npm install -g phantomjs-prebuilt
```

## Build Steps

```bash
git clone --depth 1 https://github.com/nathanboktae/mocha-casperjs.git /app/project
cd /app/project
npm install --ignore-scripts
```

Create PhantomJS wrapper script at `node_modules/phantomjs/bin/phantomjs`:

```bash
mkdir -p node_modules/phantomjs/bin
cat > node_modules/phantomjs/bin/phantomjs <<'EOF'
#!/usr/bin/env node
var spawn = require('child_process').spawn;
var binPath = '/usr/bin/phantomjs';
var args = process.argv.slice(2);
var child = spawn(binPath, args, { stdio: 'inherit', windowsHide: true });
child.on('exit', function(code, signal) {
  if (signal) { process.kill(process.pid, signal); } else { process.exit(code); }
});
process.on('SIGTERM', function() { child.kill('SIGTERM'); process.exit(128 + 15); });
EOF
chmod +x node_modules/phantomjs/bin/phantomjs
```

Create symbolic link for module path resolution:

```bash
ln -s /app/project /app/mocha-casperjs
```

## Test Steps

```bash
cd /app/project
OPENSSL_CONF=/dev/null npm test
```

## Unexpected Issues

- `npm install` (without `--ignore-scripts`) fails because the `phantomjs` package's install script cannot locate PhantomJS. Use `npm install --ignore-scripts` instead.
- CasperJS requires Python; install `python3` and `python-is-python3` to provide the `python` command.
- PhantomJS 2.1.1 requires OpenSSL 1.1; on Ubuntu 24.04 (OpenSSL 3.x), install `libssl1.1` from the Ubuntu archive and set `OPENSSL_CONF=/dev/null` when running tests.
- CasperJS expects to find `mocha-casperjs` at `/app/mocha-casperjs`; create a symlink from `/app/project` to `/app/mocha-casperjs`.
