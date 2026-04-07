# chatgpt-subtitle-translator Deployment Document

## Platform

- Base image: `node:20-slim`
- Node.js: 20.x

## Prerequisites

```bash
apt-get update && apt-get install -y git=1:2.43.0-1ubuntu7
```

## Build Steps

```bash
cd /app/chatgpt-subtitle-translator
npm install
```

## Test Steps

The project uses Node.js built-in `node:test` runner. Integration tests require a real OpenAI API key.


```bash
node --test test/cooldown.test.mjs test/subtitle.test.mjs
```

### Option B: Run all tests (requires real OpenAI API key)

```bash
export OPENAI_API_KEY=<your-real-key>
npm test
```

### Option C: Run all tests with dummy key (integration tests will fail with 401)

```bash
export OPENAI_API_KEY=sk-dummy
npm test
```

## Unexpected Issues

- 3-4 test files (`openai.test.mjs`, `translator.test.mjs`, `translatorAgent.test.mjs`) are integration tests that call the real OpenAI API at module-load time
- Without a valid API key: `OpenAIError: Missing credentials`; with a dummy key: `401 Incorrect API key`
- The 4 passing tests are pure unit tests: 3 CooldownContext tests + 1 SRT parsing test
- Use `node --test test/cooldown.test.mjs test/subtitle.test.mjs` to run only unit tests (4/4 = 100%)
