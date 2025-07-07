# Simple Examples

These examples demonstrate the new simple `optimize()` API. Each is a complete, runnable example.

## 🚀 Quick Start

1. **Set your API key:**
   ```bash
   export OPENAI_API_KEY="sk-your-key-here"
   ```

2. **Run any example:**
   ```bash
   python sentiment_analysis.py
   python content_moderation.py
   python age_rating_simple.py
   ```

## 📝 Examples

### `sentiment_analysis.py`
**Basic sentiment classification** - the "Hello World" of prompt optimization.
- Demonstrates simple data loading
- Shows prompt variants
- Uses default metrics (accuracy, F1)

### `content_moderation.py` 
**Content safety classification** with custom metrics.
- Custom `SafetyPrecision` metric
- Model configuration (temperature, max_tokens)
- Safety-focused prompting

### `age_rating_simple.py`
**Age rating prediction** - the original use case simplified.
- Regression task (predicting 0-18 age rating)
- MAE (Mean Absolute Error) metric
- Shows prediction vs actual comparison

## 🆚 Compare with Legacy

Each example replaces 50+ lines of YAML config with ~5 lines of Python:

**Before (legacy):**
```yaml
# youtube_age_rating.yaml - 60+ lines
task:
  name: "youtube_age_rating"
  type: "regression"
  target_range: [0, 18]
  
data_source:
  type: "csv_file"
  path: "data/youtube_videos.csv"
  
evaluation:
  metrics:
    - name: "mae"
      config: {}
  variants:
    - "baseline_prompt"
    - "enhanced_prompt"
    
llm:
  provider: "openai"
  model: "gpt-3.5-turbo"
  
# ... 40 more lines
```

**After (simple):**
```python
results = optimize(
    data="youtube_videos.csv",
    task="rate appropriate age from 0-18",
    prompts=["What age is appropriate for: {title}"],
    model="gpt-3.5-turbo"
)
```

## 🔧 Extension Points

See `content_moderation.py` for examples of:
- **Custom metrics**: Domain-specific evaluation
- **Model configuration**: Temperature, max_tokens, etc.
- **Multiple metrics**: Accuracy + precision + custom

## 💡 Tips

- Start with `sentiment_analysis.py` for the simplest example
- Use `verbose=True` to see progress
- Add `sample_size=100` to limit evaluation on large datasets
- Set `output_dir="results"` to save detailed results