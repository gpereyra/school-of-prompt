# Examples

This directory contains examples and legacy code from the framework's development.

## 📁 Directory Structure

### `simple_examples/`
Simple examples using the new `optimize()` API - **start here**!

### `legacy-pipeline/` 
Original YouTube age rating implementation (complex, for reference only)

### `cache/`
Shared API response cache (YouTube API responses)

### `config/`
Example configuration files:
- `api_keys.json.example` - Template for API keys
- `*.yaml` - Legacy YAML configs (complex, avoid for new projects)

### `04_experiments/` & `05_artifacts/`
Historical experimental results and datasets from development

## 🚀 Quick Start

For new projects, check out `simple_examples/` which demonstrate the new simple API:

```python
from prompt_optimizer import optimize

results = optimize(
    data="data.csv",
    task="classify sentiment",
    prompts=["Is this positive?", "Rate sentiment"],
    api_key="sk-..."
)
```

## ⚠️ Security Note

**Never commit API keys!** Use the `.example` files as templates and create your own `api_keys.json` locally.

## Legacy Code

The `legacy-pipeline/` contains the original complex implementation. It's preserved for:
- Understanding the framework's evolution
- Reference for advanced features
- Comparison with the new simple API

**For new projects, use the simple `optimize()` function instead.**