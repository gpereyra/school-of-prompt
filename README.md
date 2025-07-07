# AgeRate Prompt Evaluation Pipeline

A structured MLOps pipeline for evaluating and optimizing YouTube channel age rating prompts using real YouTube API data and automated content analysis.

## 🏗️ Pipeline Structure

```
📁 agerate-prompt-evals/
├── 📁 01_data_collection/           # YouTube API integration (future)
├── 📁 02_data_preparation/          # Data enrichment & content analysis
│   └── enrichment_pipeline.py      # Automated content labeling
├── 📁 03_evaluation/               # Prompt evaluation system
│   ├── prompt_evaluator.py        # Core evaluation engine
│   └── prompts/
│       └── variants.py            # 13 prompt variants (v1-v13)
├── 📁 04_experiments/              # Experiment tracking & results
│   └── benchmarks/                # Benchmark outputs
├── 📁 05_artifacts/                # Generated datasets & reports
│   └── datasets/                  # Ground truth & enriched data
├── 📁 cache/                       # Persistent API response cache
├── 📁 config/                      # Configuration management
└── 📁 scripts/                     # Utility scripts
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys
```bash
cp config/api_keys.json.example config/api_keys.json
# Edit with your YouTube Data API v3 and OpenAI API keys
```

### 3. Run Complete Pipeline
```bash
# Full pipeline: data enrichment + evaluation
python run_pipeline.py full --variant v11_enriched

# Just data enrichment (first time setup)
python run_pipeline.py enrich --limit-rows 10 --test-random

# Just prompt evaluation (using cached data)
python run_pipeline.py evaluate --variant v12_criteria_based
```

## 📊 Available Prompt Variants

| Variant | Description | Token Usage | Best For |
|---------|-------------|-------------|----------|
| `v1_baseline` | Original user prompt | Medium | Baseline comparison |
| `v11_enriched` | Uses automated content analysis | Medium | Balanced accuracy |
| `v12_criteria_based` | Logic-driven evaluation | Medium | Consistent results |
| `v13_token_optimized` | Minimal token usage | Very Low | Cost optimization |

## 🔧 Key Features

✅ **Zero-quota evaluation**: Leverages comprehensive API response caching  
✅ **Enriched content analysis**: 10+ automated content safety criteria  
✅ **Token optimization**: Variants from 100-600 tokens per evaluation  
✅ **Real YouTube data**: Uses live API data with intelligent caching  
✅ **Structured methodology**: MLOps pipeline with clear separation of concerns  

## 📈 Pipeline Stages

### Stage 1: Data Preparation
```bash
cd 02_data_preparation
python enrichment_pipeline.py
```
- Fetches YouTube channel metadata
- Analyzes content for safety indicators
- Generates maturity scores and content flags
- Caches all API responses (24h expiry)

### Stage 2: Prompt Evaluation  
```bash
cd 03_evaluation
python prompt_evaluator.py
```
- Leverages cached enriched data
- Tests multiple prompt variants
- Calculates MAE and accuracy metrics
- Generates comparison reports

## 🎯 Results

Recent benchmark (10 channels, cached data):
- **v11_enriched**: 0.8 MAE, 60% accuracy, 666 tokens
- **v12_criteria_based**: 1.2 MAE, 40% accuracy, 450 tokens  
- **v13_token_optimized**: 8.3 MAE, 10% accuracy, 105 tokens

## 🛠️ Cache Management

```bash
# Cache statistics
python scripts/cleanup.py stats

# Clear expired cache
python scripts/cleanup.py clean --expired

# Full cache reset (use carefully - costs API quota)
python scripts/cleanup.py clean --all
```

## 🔑 API Requirements

- **YouTube Data API v3**: Channel metadata, video details
- **OpenAI API**: GPT-3.5-turbo-instruct for age predictions

## 📋 Dataset Format

Ground truth CSV format:
```csv
YouTube_Channel,Minimum_Age,ESRB_Category,Description,Inclusion_Criteria,Source
KSI,18,AO,Gaming and entertainment,Adult,Manual
Little Angel,3,E,Children's content,Children,Manual
```

Enriched data includes automated analysis:
```json
{
  "is_educational_content": true,
  "is_explicit_adult_content": false,
  "maturity_score": 2.5,
  "total_adult_content_score": 1.0
}
```

## 🔬 Methodology

Based on modern MLOps practices:
1. **Data Collection**: Automated YouTube API integration
2. **Data Preparation**: Content analysis and safety scoring  
3. **Model Evaluation**: Multi-variant prompt testing
4. **Experiment Tracking**: Structured result comparison
5. **Artifact Management**: Versioned datasets and models

---

*Built for optimizing AI safety in content moderation through systematic prompt engineering.*