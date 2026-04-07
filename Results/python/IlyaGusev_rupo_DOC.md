# rupo Deployment Document

## Platform

- Base image: `ubuntu:24.04`
- Python: **3.8** (via `ppa:deadsnakes/ppa`). README explicitly says "Python 3.9+ is not supported!"

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7

apt-get update && apt-get install -y --no-install-recommends \
    tzdata=2024a-3ubuntu1.1 bash ca-certificates=20240203 gnupg=2.4.4-2ubuntu17 software-properties-common=0.99.48 wget=1.21.4-1ubuntu4 unzip=6.0-28ubuntu4 \
    build-essential=12.10ubuntu1 gfortran libopenblas-dev liblapack-dev libhdf5-dev pkg-config=1.8.1-2build1

add-apt-repository -y ppa:deadsnakes/ppa
apt-get update
apt-get install -y --no-install-recommends python3.8 python3.8-venv python3.8-dev
```


```bash
python3.8 -m venv .venv
. .venv/bin/activate
python -m pip install -U pip setuptools wheel
pip install -e .
```


```bash
. .venv/bin/activate
pip install allennlp==0.9.0 --no-deps
pip install overrides==3.1.0
pip install editdistance conllu==1.3.1 flaky "flask>=1.0.2" "flask-cors>=3.0.7" ftfy \
    "gevent>=1.3.6" "matplotlib>=2.2.3" "numpydoc>=0.8.0" "parsimonious>=0.8.0" \
    "pytorch-pretrained-bert>=0.6.0" "pytorch-transformers==1.1.0" "pytz>=2017.3" \
    "responses>=0.7" "sqlparse>=0.2.4" unidecode "word2number>=1.1"
```


## Build Steps

```bash
. .venv/bin/activate
chmod +x download.sh
./download.sh
```

Downloads ~4 model archives from Dropbox (generator, stress predictor, g2p, dictionaries).


## Test Steps

```bash
. .venv/bin/activate
python -m unittest -v rupo/test_api.py
```


## Unexpected Issues

- **Python 3.8 is mandatory.** The project explicitly does not support Python 3.9+.
- **AllenNLP 0.9.0 + spacy incompatibility on Python 3.8.** AllenNLP 0.9.0 requires `spacy>=2.1.0,<2.2`, but legacy spacy 2.1.x fails to build on Python 3.8. Install allennlp with `--no-deps` and lazily import it.
- **Model download required.** `download.sh` fetches models from Dropbox -- network access needed during build.
- **`test_generate_poem` fails** because it directly invokes allennlp which tries to `import spacy`.
- **Key pinned dependencies:** `rnnmorph==0.2.3`, `russian-tagsets==0.6`, `allennlp==0.9.0`, `overrides==3.1.0`, `conllu==1.3.1`, `pytorch-transformers==1.1.0`.
