# AgeRate Prompt Evaluation - Project Structure

## Overview
This project evaluates different prompt variants for YouTube channel age rating using a structured ML pipeline.

## Methodology: MLOps Pipeline Structure

```
📁 agerate-prompt-evals/
├── 📁 01_data_collection/           # Raw data acquisition
│   ├── youtube_api_client.py        # YouTube API integration
│   └── data_collectors/
├── 📁 02_data_preparation/          # Data cleaning & enrichment
│   ├── enrichment_pipeline.py      # Content analysis & labeling
│   └── dataset_builders/
├── 📁 03_evaluation/               # Prompt evaluation system
│   ├── prompt_evaluator.py        # Core evaluation engine
│   ├── prompts/                   # Prompt variants library
│   └── metrics/                   # Evaluation metrics
├── 📁 04_experiments/              # Experiment tracking
│   ├── benchmarks/                # Benchmark results
│   └── configurations/            # Experiment configs
├── 📁 05_artifacts/                # Generated outputs
│   ├── datasets/                  # Processed datasets
│   ├── models/                    # Trained models (future)
│   └── reports/                   # Analysis reports
├── 📁 cache/                       # Persistent cache
│   └── youtube_api/              # API response cache
├── 📁 config/                      # Configuration management
│   ├── api_keys.json             # API credentials
│   └── settings.yaml             # Project settings
└── 📁 scripts/                     # Utility scripts
    ├── cleanup.py                # Cache management
    └── setup.py                  # Environment setup
```

## Current State Issues
1. **Redundant files**: Multiple benchmark scripts doing similar tasks
2. **Mixed concerns**: Data collection and evaluation logic intermixed
3. **Cache duplication**: Two cache directories with overlapping data
4. **Configuration scatter**: API keys and settings in multiple places

## Proposed Cleanup
1. **Consolidate scripts** into clear pipeline stages
2. **Standardize data formats** (prefer JSONL for streaming, CSV for tabular)
3. **Unify cache management** 
4. **Separate concerns** by pipeline stage