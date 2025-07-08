# Contributing to School of Prompt

Thank you for your interest in contributing! This guide provides development setup, architecture overview, and contribution guidelines.

## Development Setup

### Prerequisites
- Python 3.9+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/school-of-prompt.git
   cd school-of-prompt
   ```

2. **Set up development environment**
   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install in development mode
   pip install -e .
   pip install -e .[dev]  # Install dev dependencies
   ```

3. **Set up API key for testing**
   ```bash
   export OPENAI_API_KEY="sk-your-key-here"
   ```

## Development Commands

### Testing
- **Run framework tests**: `python test_framework.py`
- **Run live API tests**: `python test_examples_live.py` (requires OPENAI_API_KEY)
- **Run specific example**: `python examples/simple_examples/band_sentiment_analysis.py`
- **Run all tests**: `pytest tests/ -v`

### Build and Package
- **Build package**: `python setup.py sdist bdist_wheel`
- **Install in development**: `pip install -e .`
- **Check local CI**: `./check_ci.sh`

### Code Quality
- **Check syntax**: `flake8 school_of_prompt/ --count --select=E9,F63,F7,F82`
- **Security scan**: `bandit -r school_of_prompt/ --severity-level medium`

## Architecture Overview

**School of Prompt** is a prompt optimization framework with three levels of API complexity:

### Core Architecture
- **Main API**: `optimize()` function in `school_of_prompt/optimize.py`
- **Auto-detection modules**: Automatically detect tasks, metrics, models, and data formats
- **Extension system**: Custom interfaces for advanced users

### Key Components

1. **Data Layer** (`school_of_prompt/data/`)
   - `auto_loader.py`: Automatically loads CSV, JSONL, DataFrames
   - `registry.py`: Data source and enrichment registry
   
2. **Model Layer** (`school_of_prompt/models/`)
   - `auto_model.py`: Auto-creates OpenAI models with configuration
   
3. **Task Layer** (`school_of_prompt/tasks/`)
   - `auto_task.py`: Auto-detects classification, regression, generation tasks
   
4. **Metrics Layer** (`school_of_prompt/metrics/`)
   - `auto_metrics.py`: Auto-selects appropriate metrics (accuracy, F1, MAE, etc.)

5. **Core Interfaces** (`school_of_prompt/core/`)
   - `simple_interfaces.py`: Abstract base classes for extensibility
   - `config.py`: Configuration management

6. **Production Features** (`school_of_prompt/production/`)
   - `cache.py`: Intelligent caching system
   - `batch.py`: Parallel evaluation and batch processing
   - `error_handling.py`: Retry logic and circuit breakers

7. **Analysis** (`school_of_prompt/analysis/`)
   - `results_analyzer.py`: Statistical analysis and comprehensive reporting

### API Levels
- **Level 0**: Single function call with minimal parameters
- **Level 1**: More control over model, metrics, sampling
- **Level 2**: Full extension with custom classes

### Data Format Requirements
- Input data needs text columns for processing
- Ground truth column can be named: `label`, `target`, `class`, `sentiment`, etc.
- Supports CSV, JSONL, and pandas DataFrames

## Testing Strategy

### Framework Tests (`test_framework.py`)
- Offline tests, no API calls
- Package structure validation
- Import and basic functionality tests
- Example file syntax validation

### Live API Tests (`test_examples_live.py`)
- Requires OpenAI API key
- Tests actual API integration
- Validates example scripts with real data

### Basic Tests (`tests/test_basic.py`)
- Core functionality tests
- Registry and configuration tests
- Metrics and caching tests

## Package Structure

```
school_of_prompt/
├── __init__.py              # Main exports
├── optimize.py              # Core optimize() function
├── core/
│   ├── simple_interfaces.py # Base classes
│   └── config.py           # Configuration management
├── data/
│   ├── auto_loader.py      # Data loading with smart defaults
│   └── registry.py         # Data source registry
├── models/
│   └── auto_model.py       # Model auto-detection
├── tasks/
│   └── auto_task.py        # Task auto-detection
├── metrics/
│   └── auto_metrics.py     # Metrics auto-selection
├── production/
│   ├── cache.py            # Caching system
│   ├── batch.py            # Batch processing
│   └── error_handling.py   # Error handling
└── analysis/
    └── results_analyzer.py # Results analysis
```

## API Key Handling
- Accepts `api_key` parameter or `OPENAI_API_KEY` environment variable
- All examples check for API key before running
- Test framework uses fake keys for CI/CD

## Advanced Features (v0.3.0)

### Enhanced Metrics System
- **Tolerance-based metrics**: `within_1`, `within_2`, `within_3`, `within_5`
- **Domain-specific metrics**: `valid_rate`, `token_efficiency`, `response_quality`
- **Statistical metrics**: `r2_score`, `prediction_confidence`, `error_std`, `median_error`

### Configuration-Driven Approach
- **YAML configuration files**: Full enterprise-grade configuration support
- **Multi-dataset support**: Training/validation/test dataset workflows
- **Advanced sampling**: Stratified, balanced, and random sampling strategies

### Production Features
- **Intelligent caching**: Hash-based caching with expiry and size management
- **Batch processing**: Parallel evaluation with progress tracking and error recovery
- **Error handling**: Retry logic, circuit breakers, and graceful degradation

### Advanced Analysis
- **Statistical significance testing**: Paired t-tests between prompt variants
- **Comprehensive error analysis**: Pattern detection and bias analysis
- **Cross-validation**: K-fold cross-validation support
- **Performance breakdown**: Analysis by category, difficulty, and content length

## Extension Points

Developers can extend the framework by implementing:

### Custom Metrics
```python
from school_of_prompt.core.simple_interfaces import CustomMetric

class MyMetric(CustomMetric):
    name = "my_metric"
    
    def calculate(self, predictions, actuals):
        # Implementation
        return score
```

### Custom Data Sources
```python
from school_of_prompt.core.simple_interfaces import CustomDataSource

class MyDataSource(CustomDataSource):
    def load(self):
        # Implementation
        return data_samples
```

### Custom Models
```python
from school_of_prompt.core.simple_interfaces import CustomModel

class MyModel(CustomModel):
    def generate(self, prompt, **kwargs):
        # Implementation
        return response
```

### Data Enrichers
```python
from school_of_prompt.data.registry import get_data_registry

def my_enricher(data):
    # Add features to data
    return enriched_data

registry = get_data_registry()
registry.register_enricher("my_enricher", my_enricher)
```

## Contribution Guidelines

### Code Style
- Follow PEP 8
- Use type hints where appropriate
- Add docstrings for public functions and classes
- Keep functions focused and testable

### Testing
- Add tests for new features
- Ensure all tests pass before submitting PR
- Include both unit tests and integration tests
- Test with different data formats and configurations

### Documentation
- Update README.md for user-facing changes
- Update CONTRIBUTING.md for development changes
- Add examples for new features
- Keep CLAUDE.md updated with development commands

### Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add/update tests
5. Run local CI checks: `./check_ci.sh`
6. Submit pull request with clear description

### CI/CD Pipeline
The project uses GitHub Actions for:
- **Testing**: Python 3.9 and 3.12 on Ubuntu
- **Security**: Bandit security scanning
- **Build**: Package building and validation

### Release Process
See `docs/RELEASE_PROCESS.md` for detailed release procedures.

## Dependencies

### Core Dependencies
- `pandas>=1.3.0`: Data manipulation
- `openai>=1.0.0`: OpenAI API integration

### Optional Dependencies
- `anthropic>=0.3.0`: Anthropic Claude support
- `pytest`: Testing framework
- `flake8`: Code linting
- `bandit`: Security scanning

### Development Dependencies
- `pytest`: Testing
- `pytest-cov`: Coverage reporting
- `flake8`: Linting
- `bandit`: Security scanning

## Getting Help

- **Issues**: Create GitHub issues for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Development**: Check CLAUDE.md for quick development commands

## License

MIT License - see LICENSE file for details.