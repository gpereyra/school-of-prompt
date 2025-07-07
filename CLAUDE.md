# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Testing
- **Run framework tests**: `python test_framework.py`
- **Run live API tests**: `python test_examples_live.py` (requires OPENAI_API_KEY)
- **Run specific example**: `python examples/simple_examples/band_sentiment_analysis.py`

### Build and Package
- **Build package**: `python setup.py sdist bdist_wheel`
- **Install in development**: `pip install -e .`
- **Install with dev dependencies**: `pip install -e .[dev]`

### Linting (if available)
- **Format code**: `black .` (if installed via dev dependencies)
- **Check code style**: `flake8 .` (if installed via dev dependencies)

## Architecture Overview

**School of Prompt** is a prompt optimization framework with three levels of API complexity:

### Core Architecture
- **Main API**: `optimize()` function in `school_of_prompt/optimize.py`
- **Auto-detection modules**: Automatically detect tasks, metrics, models, and data formats
- **Extension system**: Custom interfaces for advanced users

### Key Components
1. **Data Layer** (`school_of_prompt/data/`)
   - `auto_loader.py`: Automatically loads CSV, JSONL, DataFrames
   
2. **Model Layer** (`school_of_prompt/models/`)
   - `auto_model.py`: Auto-creates OpenAI models with configuration
   
3. **Task Layer** (`school_of_prompt/tasks/`)
   - `auto_task.py`: Auto-detects classification, regression, generation tasks
   
4. **Metrics Layer** (`school_of_prompt/metrics/`)
   - `auto_metrics.py`: Auto-selects appropriate metrics (accuracy, F1, MAE, etc.)

5. **Core Interfaces** (`school_of_prompt/core/`)
   - `simple_interfaces.py`: Abstract base classes for extensibility
   - `config.py`: Configuration management

### API Levels
- **Level 0**: Single function call with minimal parameters
- **Level 1**: More control over model, metrics, sampling
- **Level 2**: Full extension with custom classes

### Data Format Requirements
- Input data needs text columns for processing
- Ground truth column can be named: `label`, `target`, `class`, `sentiment`, etc.
- Supports CSV, JSONL, and pandas DataFrames

## Development Notes

### Testing Strategy
- Framework tests in `test_framework.py` (offline, no API calls)
- Live API tests in `test_examples_live.py` (requires OpenAI API key)
- Example scripts in `examples/simple_examples/` demonstrate real usage

### Package Structure
- Python package with setuptools
- Dependencies: pandas>=1.3.0, openai>=1.0.0
- Optional dev dependencies: pytest, black, flake8
- Optional anthropic support: anthropic>=0.3.0

### API Key Handling
- Accepts `api_key` parameter or `OPENAI_API_KEY` environment variable
- All examples check for API key before running

### Advanced Features (NEW)

#### Enhanced Metrics System
- **Tolerance-based metrics**: `within_1`, `within_2`, `within_3`, `within_5`
- **Domain-specific metrics**: `valid_rate`, `token_efficiency`, `response_quality`
- **Statistical metrics**: `r2_score`, `prediction_confidence`, `error_std`, `median_error`

#### Configuration-Driven Approach
- **YAML configuration files**: Full enterprise-grade configuration support
- **Multi-dataset support**: Training/validation/test dataset workflows
- **Advanced sampling**: Stratified, balanced, and random sampling strategies

#### Production Features
- **Intelligent caching**: Hash-based caching with expiry and size management
- **Batch processing**: Parallel evaluation with progress tracking and error recovery
- **Error handling**: Retry logic, circuit breakers, and graceful degradation

#### Advanced Analysis
- **Statistical significance testing**: Paired t-tests between prompt variants
- **Comprehensive error analysis**: Pattern detection and bias analysis
- **Cross-validation**: K-fold cross-validation support
- **Performance breakdown**: Analysis by category, difficulty, and content length

### New API Levels

#### Level 0: Dead Simple (Unchanged)
```python
results = optimize(data="data.csv", task="classify sentiment", prompts=["prompt1", "prompt2"])
```

#### Level 1: Configuration-Driven
```python
results = optimize(config="config.yaml")  # YAML configuration file
```

#### Level 2: Advanced Features
```python
results = optimize(
    data={"train": "train.csv", "test": "test.csv"},
    task="regression",
    prompts=["prompt1", "prompt2"],
    metrics=["mae", "within_1", "within_2", "valid_rate"],
    cross_validation=True,
    k_fold=5,
    enrichers=["text_length", "readability"],
    sampling_strategy="stratified",
    comprehensive_analysis=True,
    cache_enabled=True,
    parallel_evaluation=True
)
```

### Extension Points
Developers can extend the framework by implementing:
- `CustomMetric`: Custom evaluation metrics
- `CustomDataSource`: Custom data loading (now with registry system)
- `CustomModel`: Custom LLM integrations
- `CustomTask`: Custom task types
- **Data enrichers**: Custom data enrichment functions
- **Preprocessors**: Custom data preprocessing pipelines