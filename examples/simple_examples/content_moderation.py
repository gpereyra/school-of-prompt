"""
Content moderation example with custom metrics.
"""

import os
import pandas as pd
from prompt_optimizer import optimize, CustomMetric

class SafetyPrecision(CustomMetric):
    """Custom metric that heavily weights catching unsafe content."""
    
    @property
    def name(self):
        return "safety_precision"
    
    def calculate(self, predictions, actuals):
        # Convert to binary: unsafe=1, safe=0
        pred_unsafe = [1 if 'unsafe' in str(p).lower() else 0 for p in predictions]
        actual_unsafe = [1 if 'unsafe' in str(a).lower() else 0 for a in actuals]
        
        # Calculate precision for "unsafe" class
        tp = sum(p and a for p, a in zip(pred_unsafe, actual_unsafe))
        fp = sum(p and not a for p, a in zip(pred_unsafe, actual_unsafe))
        
        return tp / (tp + fp) if (tp + fp) > 0 else 0.0

def main():
    # Sample content moderation data
    sample_data = [
        {"content": "Great tutorial on cooking!", "safety": "safe"},
        {"content": "How to build explosives at home", "safety": "unsafe"},
        {"content": "Lovely family photo", "safety": "safe"},
        {"content": "Violence and graphic content warning", "safety": "unsafe"},
        {"content": "Educational math video", "safety": "safe"},
    ]
    
    df = pd.DataFrame(sample_data)
    df.to_csv("content_posts.csv", index=False)
    
    results = optimize(
        data="content_posts.csv",
        task="classify safety level", 
        prompts=[
            "Is this content safe or unsafe? {content}",
            "Content safety assessment: {content}",
            "Does this violate safety guidelines? {content}",
            "Safe for general audience? {content}"
        ],
        model={
            "name": "gpt-4",
            "temperature": 0.0,  # More deterministic for safety
            "max_tokens": 10
        },
        metrics=[
            "accuracy", 
            "precision", 
            SafetyPrecision()  # Custom metric
        ],
        api_key=os.getenv("OPENAI_API_KEY"),
        verbose=True
    )
    
    print("\\n" + "="*50)
    print("CONTENT MODERATION RESULTS")
    print("="*50)
    print(f"Best prompt: {results['best_prompt']}")
    print(f"Accuracy: {results['best_score']:.3f}")
    
    # Show all metrics for best prompt
    best_prompt_key = list(results['prompts'].keys())[0]  # First is best
    scores = results['prompts'][best_prompt_key]['scores']
    for metric, score in scores.items():
        print(f"{metric}: {score:.3f}")
    
    os.remove("content_posts.csv")

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set OPENAI_API_KEY environment variable")
    else:
        main()