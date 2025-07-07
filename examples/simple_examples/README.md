# School of Prompt Examples 🎸

Rock your prompts with these School of Rock themed examples! Each is a complete, runnable example that demonstrates the `optimize()` API.

## 🚀 Quick Start

1. **Set your API key:**
   ```bash
   export OPENAI_API_KEY="sk-your-key-here"
   ```

2. **Rock any example:**
   ```bash
   python band_sentiment_analysis.py
   python student_performance_rating.py
   python rock_content_safety.py
   ```

## 🎵 Examples

### 🎸 `band_sentiment_analysis.py`
**Analyze fan reviews of the School of Rock band performances**
- Demonstrates basic sentiment classification
- School of Rock themed review data
- Multiple prompt variants for fan sentiment analysis
- Uses default metrics (accuracy, F1)

### 🥁 `student_performance_rating.py` 
**Rate student performances like Dewey would** 
- Regression task (rating performances 1-10)
- Custom performance evaluation data
- MAE (Mean Absolute Error) metric for rating accuracy
- Shows prediction vs actual comparison

### 🛡️ `rock_content_safety.py`
**Keep content school-appropriate for young rockers**
- Content safety classification with custom metrics
- Custom `RockSafetyPrecision` metric prioritizes catching inappropriate content
- Model configuration (temperature=0.0 for consistency)
- Safety-focused prompting for school environments

## 🆚 Compare with Before

Each example replaces 50+ lines of YAML config with ~5 lines of Python:

**Before (complex frameworks):**
```yaml
# band_sentiment_analysis.yaml - 60+ lines
task:
  name: "band_review_sentiment"
  type: "classification"
  classes: ["positive", "negative", "neutral"]
  
data_source:
  type: "csv_file"
  path: "data/band_reviews.csv"
  
evaluation:
  metrics:
    - name: "accuracy"
      config: {}
  variants:
    - "fan_feedback_prompt"
    - "review_analysis_prompt"
    
llm:
  provider: "openai"
  model: "gpt-3.5-turbo"
  
# ... 40 more lines
```

**After (School of Prompt):**
```python
results = optimize(
    data="band_reviews.csv",
    task="classify sentiment",
    prompts=["How does this fan feel about our band?"],
    api_key="sk-..."
)
```

## 🔧 Extension Points

See `rock_content_safety.py` for examples of:
- **Custom metrics**: `RockSafetyPrecision` for domain-specific evaluation
- **Model configuration**: Temperature, max_tokens for consistent safety decisions
- **Multiple metrics**: Accuracy + precision + custom safety metric

## 💡 Tips for Rockers

- Start with `band_sentiment_analysis.py` for the simplest example
- Use `verbose=True` to see the optimization progress
- Add `sample_size=100` to limit evaluation on large datasets
- Set `output_dir="results"` to save detailed results for later analysis

## 🎸 Rock On!

Each example demonstrates that **you don't need to be a prompt engineering expert** to get great results. The School of Prompt framework handles the complexity so you can focus on rocking your specific use case!

*"You're not hardcore unless you optimize hardcore!"* 🤘