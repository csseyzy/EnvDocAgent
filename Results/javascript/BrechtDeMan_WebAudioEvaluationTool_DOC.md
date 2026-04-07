# WebAudioEvaluationTool Deployment Document

## Platform

- Base image: `php:8-apache`
- Python: 3.x (for analysis scripts)

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7 python3=3.12.3-0ubuntu2 python3-pip=24.0+dfsg-1ubuntu1.1 python3-matplotlib python3-numpy python3-scipy
```

## Build Steps

```bash
cd /app/WebAudioEvaluationTool
cp -r . /var/www/html/
a2enmod rewrite
mv "$PHP_INI_DIR/php.ini-development" "$PHP_INI_DIR/php.ini"
chown -R www-data:www-data /var/www/html
```

## Test Steps


Smoke tests:

```bash
# Verify Apache serves the app
apache2-foreground &
sleep 3
curl -s -o /dev/null -w "%{http_code}" http://localhost/test.html

# Verify Python analysis scripts are importable
python3 -c "import sys; sys.path.insert(0, 'python'); import score_parser; print('OK')"

# Verify XML configs are valid
python3 -c "import xml.etree.ElementTree as ET; ET.parse('tests/examples/mushra_example.xml'); print('XML OK')"
```

## Unexpected Issues

- The `tests/` directory is misleading - it contains XML configs for audio evaluation experiments, NOT automated tests
- No `package.json`, `composer.json`, `phpunit.xml`, `pytest.ini`, or CI workflows exist
- The project is a web application for human-conducted audio experiments
- The best achievable verification is smoke tests (HTTP 200 + Python import + XML validation)
