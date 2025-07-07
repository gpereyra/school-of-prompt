# Examples

This directory contains examples for the School of Prompt framework.

## 📁 Directory Structure

### `simple_examples/`
Complete, runnable examples using the `optimize()` API - **start here**!

## 🚀 Quick Start

```python
from school_of_prompt import optimize

results = optimize(
    data="data.csv",
    task="classify sentiment",
    prompts=["Is this positive?", "Rate sentiment"],
    api_key="sk-..."
)
```

## ⚠️ Security Note

**Never commit API keys!** Use environment variables:

```bash
export OPENAI_API_KEY="sk-your-key-here"
```