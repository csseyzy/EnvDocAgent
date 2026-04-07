# hypergrad Deployment Document

## Platform

- Base image: `ubuntu:20.04` (ships Python 2.7 via `python2` package)
- This is a Python 2 project. It uses `print` statements, `xrange`, `dict.iteritems()`, long integer literals (`0L`), relative imports (`from exact_rep import ExactRep`), and `reduce` as a builtin. It will NOT run on Python 3 without extensive porting.
- Depends on `funkyyak`, the original name for the [autograd](https://github.com/HIPS/autograd) library at a specific old revision (`be470d5b8d6c84bfa74074b238d43755f6f2c55c`).

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.25.1-1ubuntu3

apt-get update && apt-get install -y --no-install-recommends \
    tzdata bash ca-certificates=20230311ubuntu0.20.04.1 \
    python2 python2-dev \
    build-essential=12.8ubuntu1 \
    curl=7.68.0-1ubuntu2
```


Python 2 pip is not available via apt on Ubuntu 20.04. Install via `get-pip.py`:

```bash
curl https://bootstrap.pypa.io/pip/2.7/get-pip.py -o /tmp/get-pip.py
python2 /tmp/get-pip.py
```


```bash
python2 -m pip install numpy scipy matplotlib pytest
```


The project imports `from funkyyak import grad, Differentiable, kylist, getval`. This is the old name for the `autograd` package. Must install from the exact commit specified in the README:

```bash
cd /tmp
git clone https://github.com/HIPS/autograd.git
cd autograd
git checkout be470d5b8d6c84bfa74074b238d43755f6f2c55c
```

This revision predates `setup.py`, so install by adding to PYTHONPATH:

```bash
export PYTHONPATH=/tmp/autograd:$PYTHONPATH
```


## Build Steps

```bash
cd /app/project
export PYTHONPATH=/app/project:$PYTHONPATH
```


## Test Steps

```bash
cd /app/project
python2 -m pytest -q tests/test_bitstore.py tests/test_exact_rep.py tests/test_logit.py tests/test_nn_utils.py
```

test files, covering `BitStore`, `ExactRep`, `logit`/`inv_logit`, and `VectorParser`.

Full tests (require funkyyak):

```bash
cd /app/project
python2 -m pytest -q tests/test_grads.py
```

## Unexpected Issues

- **Python 2 only.** The codebase uses `print` statements, `xrange`, `dict.iteritems()`, long integer literals (`0L`), relative imports, and builtin `reduce`. Python 3 will fail on syntax errors alone.
- **funkyyak is autograd at a specific old commit.** The README specifies commit `be470d5b8d6c84bfa74074b238d43755f6f2c55c` (Feb 2, 2015). Modern autograd is completely incompatible -- the API has changed significantly (`Differentiable`, `kylist` no longer exist).
- **No setup.py.** The project and funkyyak must both be added to `PYTHONPATH` manually.
- **Relative imports in `hypergrad/` package.** Files like `optimizers.py` use `from exact_rep import ExactRep` and `from nn_utils import fill_parser` (Python 2 implicit relative imports). These fail on Python 3 which requires explicit relative imports (`from .exact_rep import ...`).
- **`exact_rep.py` uses `0L` long literal.** Line 60: `np.array([0L] * length, dtype=object)`. This is a `SyntaxError` in Python 3.
- **`optimizers.py` uses `xrange` and `reduce`.** Both are Python 2 builtins removed in Python 3.
- **`nn_utils.py` imports `matplotlib`.** Install `matplotlib` or tests that import `nn_utils` will fail with `ImportError`.
- **`data.py` expects MNIST data at `~/repos/hypergrad/data/mnist/`.** The experiments that use MNIST require downloading the data separately. The basic tests do not need MNIST data.
- **`tests/test_odyssey.py`** requires Harvard Odyssey cluster configuration (`odyssey_config.py`) and should be skipped.
- **Integer division semantics.** Several files use `/` for integer division (e.g., `N_iter/len(batches)`), which behaves differently in Python 3 (returns float).
