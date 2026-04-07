# amazon-neptune-samples (pg-schema-for-rdf) Deployment Document

## Platform

- Base image: `python:3.12-slim`
- Python: 3.12

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7
```

## Build Steps


Fix import path in `src/rdfpgschema.py`:

```bash
sed -i 's/from rdfhelpers import Constructor/from rdfhelpers.experimental.constructor import Constructor/' src/rdfpgschema.py
```

Ensure test `__init__.py` exists:

```bash
touch test/__init__.py
```


The testable component is in the `pg-schema-for-rdf` subdirectory:

```bash
cd /app/amazon-neptune-samples/pg-schema-for-rdf
python -m venv venv
venv/bin/pip install --no-cache-dir -r requirements.txt pytest
```

## Test Steps

```bash
cd /app/amazon-neptune-samples/pg-schema-for-rdf
export PYTHONPATH=/app/amazon-neptune-samples/pg-schema-for-rdf/src
venv/bin/python -m pytest test/tests.py -v
```

## Unexpected Issues

- This is a **Python project** within a large AWS samples monorepo, not a JavaScript project
- The `rdfhelpers` package moved `Constructor` to `rdfhelpers.experimental.constructor` - the import in `src/rdfpgschema.py` must be updated
- Only the `pg-schema-for-rdf` subdirectory has tests (8 pytest tests)
- The monorepo contains many other samples (Neptune notebooks, GraphQL resolvers, etc.) that are not testable in isolation
- With the import fix, all 8 tests pass (100%)
