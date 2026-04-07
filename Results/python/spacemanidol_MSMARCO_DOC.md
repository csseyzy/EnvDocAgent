# MSMARCO Deployment Document

## Platform

- **Base Image:** python:3.9.21-bookworm
- **Python Version:** 3.9

## Prerequisites

```bash
apt-get update && apt-get install -y --no-install-recommends \
    build-essential=12.9
```

## Build Steps

If spacy 3.x is required instead of 2.x:
- `ms_marco_eval.py` line 42: Change `NLP = NlpEnglish(parser=False)` to `NLP = NlpEnglish()`
- `ms_marco_eval.py` lines 44-46: Change `n_threads=p_thread_count` to `n_process=p_thread_count`
- Update test expectations in `ms_marco_eval_test.py` to match spacy 3.x tokenization output

With spacy==2.3.9 + en_core_web_lg==2.3.1, no modifications are needed.


```bash
cd /app/project
pip install spacy==2.3.9
pip install numpy==1.26.4
python -m spacy download en_core_web_lg==2.3.1
```

## Test Steps

```bash
cd /app/project/Q+A/Evaluation
PYTHONPATH=./bleu python -m pytest ms_marco_eval_test.py -v 2>&1 | tee /app/project/TEST_RESULTS.txt
```

## Unexpected Issues

- The `test_no_answer` test has a bug in the test data: `no_answer_test_references.json` has `"answers": []` (empty list) for query_id 1, but the code checks for `'No Answer Present.'` string
- The `en_core_web_lg` model must match the spacy version exactly
- The `test_dev_set` BLEU score is very close (`0.17637` vs `0.17634`) — a floating point precision difference from different spacy/numpy versions
