"""
Simple sentiment analysis example using the new optimize() API.
"""

import os
from prompt_optimizer import optimize

def main():
    # Example data - in practice, load from CSV/JSONL
    # This would typically be: data="movie_reviews.csv"
    sample_data = [
        {"text": "This movie was amazing!", "label": "positive"},
        {"text": "Terrible film, waste of time.", "label": "negative"},
        {"text": "It was okay, nothing special.", "label": "neutral"},
        {"text": "Best movie I've ever seen!", "label": "positive"},
        {"text": "Boring and predictable.", "label": "negative"},
    ]
    
    # Save sample data to CSV for demo
    import pandas as pd
    df = pd.DataFrame(sample_data)
    df.to_csv("movie_reviews.csv", index=False)
    
    # Simple optimization
    results = optimize(
        data="movie_reviews.csv",
        task="classify sentiment",
        prompts=[
            "Is this movie review positive, negative, or neutral? {text}",
            "Sentiment analysis: {text}",
            "Rate the sentiment of this review: {text}",
            "What's the emotional tone? {text}"
        ],
        api_key=os.getenv("OPENAI_API_KEY"),
        verbose=True
    )
    
    print("\\n" + "="*50)
    print("RESULTS SUMMARY")
    print("="*50)
    print(f"Best prompt: {results['best_prompt']}")
    print(f"Best accuracy: {results['best_score']:.3f}")
    
    # Clean up demo file
    os.remove("movie_reviews.csv")

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set OPENAI_API_KEY environment variable")
        print("export OPENAI_API_KEY='sk-your-key-here'")
    else:
        main()