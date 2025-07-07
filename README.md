# Prompt Optimizer

**Simple, powerful prompt optimization with minimal boilerplate.**

Stop writing complex YAML configs. Start optimizing prompts in 3 lines of code.

## Quick Start

```python
from prompt_optimizer import optimize

# That's it! One function call to optimize prompts
results = optimize(
    data="reviews.csv",
    task="classify sentiment", 
    prompts=["Is this positive?", "Rate the sentiment: positive/negative"],
    api_key="sk-..."
)

print(f"Best prompt: {results['best_prompt']}")
print(f"Accuracy: {results['best_score']:.2f}")
```

## Installation

```bash
pip install prompt-optimizer
```

## Why Prompt Optimizer?

**Before** (complex frameworks):
```yaml
# 50+ lines of YAML config
task:
  name: "sentiment_classification"
  type: "classification"
  classes: ["positive", "negative"]
  
data_source:
  type: "csv_file"
  path: "reviews.csv"
  preprocessing:
    - normalize_text
    - remove_duplicates
    
evaluation:
  metrics:
    - name: "accuracy"
      config: {...}
    - name: "f1_score"
      config: {...}
  cross_validation:
    folds: 5
    
llm:
  provider: "openai"
  model: "gpt-3.5-turbo"
  parameters:
    temperature: 0.0
    max_tokens: 50
    
# ... dozens more lines
```

**After** (Prompt Optimizer):
```python
# 5 lines, done!
results = optimize(
    data="reviews.csv",
    task="classify sentiment",
    prompts=["Is this positive?", "Rate sentiment"],
    api_key="sk-..."
)
```

## Features

### 🚀 **Level 0: Dead Simple**
Perfect for quick experiments and getting started.

```python
results = optimize(
    data="data.csv",
    task="classify sentiment",
    prompts=["Is this positive?", "Analyze sentiment"],
    api_key="sk-..."
)
```

### 🎛️ **Level 1: More Control**
Add configuration without complexity.

```python
results = optimize(
    data="reviews.csv",
    task="classify sentiment",
    prompts="prompts/sentiment_variants.txt",  # Read from file
    model={
        "name": "gpt-4", 
        "temperature": 0.1,
        "max_tokens": 50
    },
    metrics=["accuracy", "f1", "precision"],
    sample_size=1000,
    api_key="sk-..."
)
```

### 🔧 **Level 2: Full Extension**
Custom everything for advanced use cases.

```python
from prompt_optimizer import optimize, CustomMetric, CustomDataSource

class BusinessMetric(CustomMetric):
    name = "business_value"
    
    def calculate(self, predictions, actuals):
        # Your domain-specific metric
        return calculate_business_impact(predictions, actuals)

results = optimize(
    data=CustomDataSource(my_database),
    task=MyCustomTask(),
    prompts=dynamic_prompt_generator,
    model=my_llm_wrapper,
    metrics=[BusinessMetric(), "accuracy"],
    api_key="sk-..."
)
```

## Smart Defaults

The framework automatically handles common scenarios:

### 📊 **Auto Data Loading**
- **CSV files**: `data="reviews.csv"`
- **JSONL files**: `data="data.jsonl"`
- **DataFrames**: `data=my_dataframe`
- **Custom sources**: `data=MyDataSource()`

### 🎯 **Auto Task Detection**
- **"classify sentiment"** → Sentiment classification
- **"rate from 1-10"** → Regression task  
- **"categorize content"** → Multi-class classification
- **"generate summary"** → Text generation

### 📏 **Auto Metrics Selection**
- **Classification** → Accuracy, F1-score
- **Regression** → MAE, RMSE
- **Generation** → BLEU, ROUGE (coming soon)

### 🤖 **Auto Model Setup**
- **String**: `model="gpt-4"` 
- **Config**: `model={"name": "gpt-4", "temperature": 0.1}`
- **Custom**: `model=MyModel()`

## Examples

### Sentiment Analysis
```python
results = optimize(
    data="movie_reviews.csv",
    task="classify sentiment",
    prompts=[
        "Is this movie review positive or negative?",
        "Sentiment: {text}",
        "Rate this review as positive, negative, or neutral: {text}"
    ],
    api_key=os.getenv("OPENAI_API_KEY")
)
```

### Content Moderation
```python
results = optimize(
    data="user_posts.csv", 
    task="classify safety level",
    prompts=[
        "Is this content safe for work?",
        "Rate content safety: safe/unsafe",
        "Does this violate community guidelines?"
    ],
    model="gpt-4",
    metrics=["accuracy", "precision", "recall"]
)
```

### Document Classification
```python
results = optimize(
    data="legal_docs.jsonl",
    task="categorize document type", 
    prompts="prompts/legal_classification.txt",
    model={
        "name": "gpt-4",
        "temperature": 0.0,
        "max_tokens": 20
    },
    sample_size=500
)
```

### Age Rating (Original Use Case)
```python
results = optimize(
    data="youtube_videos.csv",
    task="rate appropriate age from 0-18",
    prompts=[
        "What age is appropriate for: {title} - {description}",
        "Age rating for: {title}. Content: {description}",
        "Minimum age for this content: {title}"
    ],
    model="gpt-3.5-turbo",
    metrics=["mae", "accuracy"]
)
```

## API Reference

### `optimize()`

The main optimization function.

**Parameters:**
- **`data`** *(str|DataFrame|CustomDataSource)*: Your dataset
- **`task`** *(str|CustomTask)*: Task description or custom task
- **`prompts`** *(str|List[str]|Path)*: Prompt variants to test
- **`model`** *(str|dict|CustomModel)*: Model configuration
- **`metrics`** *(List[str]|List[CustomMetric])*: Evaluation metrics
- **`api_key`** *(str)*: API key (or set `OPENAI_API_KEY` env var)
- **`sample_size`** *(int)*: Limit evaluation to N samples
- **`random_seed`** *(int)*: For reproducible sampling
- **`output_dir`** *(str)*: Save detailed results
- **`verbose`** *(bool)*: Print progress

**Returns:**
```python
{
    "best_prompt": "Is this positive?",
    "best_score": 0.892,
    "prompts": {
        "prompt_1": {"scores": {"accuracy": 0.856, "f1_score": 0.834}},
        "prompt_2": {"scores": {"accuracy": 0.892, "f1_score": 0.889}}
    },
    "summary": {"metrics": {...}},
    "details": [...]
}
```

## Environment Setup

```bash
# Set your API key
export OPENAI_API_KEY="sk-your-key-here"

# Or pass directly
results = optimize(..., api_key="sk-your-key-here")
```

## Data Format

Your data should have:
- **Input columns**: Text or features to analyze
- **Label column**: Ground truth (named `label`, `target`, `class`, etc.)

**CSV Example:**
```csv
text,label
"Great movie!",positive
"Terrible film.",negative
"It was okay.",neutral
```

**JSONL Example:**
```json
{"text": "Great movie!", "label": "positive"}
{"text": "Terrible film.", "label": "negative"}
```

## Extension Points

For advanced users who need custom behavior:

```python
from prompt_optimizer import CustomMetric, CustomDataSource, CustomModel, CustomTask

class MyMetric(CustomMetric):
    name = "my_metric"
    def calculate(self, predictions, actuals):
        return my_calculation(predictions, actuals)

class MyDataSource(CustomDataSource):
    def load(self):
        return load_from_database()

class MyModel(CustomModel):
    def generate(self, prompt):
        return my_llm_call(prompt)

class MyTask(CustomTask):
    def format_prompt(self, template, sample):
        return template.format(**sample)
    
    def extract_prediction(self, response):
        return parse_response(response)
    
    def get_ground_truth(self, sample):
        return sample["label"]
```

## Roadmap

- **More Models**: Anthropic Claude, local models, Azure OpenAI
- **More Metrics**: BLEU, ROUGE, custom domain metrics  
- **Auto Optimization**: Genetic algorithms, Bayesian optimization
- **Batch Processing**: Handle large datasets efficiently
- **Caching**: Speed up repeated evaluations

## Contributing

We'd love your help! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License. See [LICENSE](LICENSE) for details.

---

**Stop configuring. Start optimizing.** 🚀