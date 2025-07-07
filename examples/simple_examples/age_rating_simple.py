"""
Simplified age rating example - the original use case made simple.
"""

import os
import pandas as pd
from prompt_optimizer import optimize

def main():
    # Sample YouTube-style content data
    sample_data = [
        {
            "title": "Cooking Tutorial: Making Cookies", 
            "description": "Family-friendly baking tutorial",
            "age_rating": 0
        },
        {
            "title": "Action Movie Trailer", 
            "description": "Intense action scenes with explosions",
            "age_rating": 13
        },
        {
            "title": "Educational Science Video", 
            "description": "Learning about the solar system",
            "age_rating": 0
        },
        {
            "title": "Horror Movie Review", 
            "description": "Discussion of scary themes and violence",
            "age_rating": 16
        },
        {
            "title": "Kids Cartoon", 
            "description": "Animated fun for children",
            "age_rating": 0
        }
    ]
    
    df = pd.DataFrame(sample_data)
    df.to_csv("youtube_content.csv", index=False)
    
    results = optimize(
        data="youtube_content.csv",
        task="rate appropriate age from 0-18",
        prompts=[
            "What minimum age is appropriate for: {title} - {description}",
            "Age rating (0-18) for: {title}. Content: {description}",
            "Minimum age for this content: {title}",
            "Rate from 0-18: {title} - {description}"
        ],
        model="gpt-3.5-turbo",
        metrics=["mae", "accuracy"],  # Mean Absolute Error for age ratings
        api_key=os.getenv("OPENAI_API_KEY"),
        verbose=True
    )
    
    print("\\n" + "="*50)
    print("AGE RATING RESULTS")
    print("="*50)
    print(f"Best prompt: {results['best_prompt']}")
    print(f"MAE (lower is better): {results['prompts'][list(results['prompts'].keys())[0]]['scores']['mae']:.2f}")
    
    # Show prediction vs actual for best prompt
    best_details = results['details'][0]  # First is best
    print("\\nPredictions vs Actual:")
    for i, (pred, actual) in enumerate(zip(best_details['predictions'], best_details['actuals'])):
        title = sample_data[i]['title']
        print(f"  {title}: predicted {pred}, actual {actual}")
    
    os.remove("youtube_content.csv")

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set OPENAI_API_KEY environment variable")
    else:
        main()