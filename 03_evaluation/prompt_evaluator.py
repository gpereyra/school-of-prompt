#!/usr/bin/env python3
"""
Simple standalone evaluation for agerate prompts.
"""

import re
import os
import json
import hashlib
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
import openai

# Import prompts
from prompts.variants import PROMPTS

class SimpleAgerateEval:
    def __init__(self, variant="v1_baseline"):
        self.variant = variant
        if variant not in PROMPTS:
            raise ValueError(f"Unknown variant: {variant}")
        self.prompt_template = PROMPTS[variant]
        
        # Load config from file
        config = self._load_config()
        self.youtube_key = config.get("youtube_api_key")
        if not self.youtube_key:
            raise ValueError("youtube_api_key not found in config.json")
        
        # Set OpenAI API key
        openai.api_key = config.get("openai_api_key")
        if not openai.api_key:
            raise ValueError("openai_api_key not found in config.json")
        
        # Use shared cache directory from ground truth pipeline
        self.cache_dir = Path("cache/youtube_api")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> dict:
        """Load configuration from config.json file."""
        config_path = Path("config/api_keys.json")
        if not config_path.exists():
            raise ValueError(
                "api_keys.json not found. Copy config/api_keys.json.example to config/api_keys.json and add your API keys."
            )
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config.json: {e}")
        except Exception as e:
            raise ValueError(f"Error reading config.json: {e}")
    
    def eval_sample(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single sample."""
        channel_name = sample["input"]
        expected_age = int(sample["ideal"])
        
        # Get enriched data (leverages existing cache)
        try:
            channel_data = self._get_enriched_data(channel_name)
        except Exception as e:
            print(f"Error fetching enriched data for {channel_name}: {e}")
            return {
                "prompt": "",
                "response": "",
                "expected_age": expected_age,
                "predicted_age": None,
                "mae": 999,
                "exact_match": 0,
                "valid_response": False,
                "error": str(e)
            }
        
        # Format prompt with enriched data
        prompt = self.prompt_template.format(
            channel_name=channel_name,
            description=channel_data["description"],
            topics=", ".join(channel_data["topics"]) if channel_data["topics"] else "Unknown",
            created_year=channel_data["created_year"],
            video_count=channel_data["video_count"],
            subscriber_count=channel_data["subscriber_count"],
            video_sample=channel_data["video_sample"],
            content_categories=channel_data.get("content_categories", "Unknown"),
            maturity_score=channel_data.get("maturity_score", 0),
            safety_flags=channel_data.get("safety_flags", {})
        )
        
        # Get OpenAI completion
        try:
            response = openai.Completion.create(
                engine="gpt-3.5-turbo-instruct",
                prompt=prompt,
                max_tokens=300
            )
            response_text = response.choices[0].text.strip()
        except Exception as e:
            print(f"OpenAI API error: {e}")
            response_text = ""
        
        # Extract age from response
        predicted_age = self._extract_age(response_text)
        
        # Calculate metrics
        mae = abs(predicted_age - expected_age) if predicted_age is not None else 999
        exact_match = 1 if predicted_age == expected_age else 0
        
        return {
            "prompt": prompt,
            "response": response_text,
            "expected_age": expected_age,
            "predicted_age": predicted_age,
            "mae": mae,
            "exact_match": exact_match,
            "valid_response": predicted_age is not None
        }
    
    def _extract_age(self, response: str) -> Optional[int]:
        """Extract age number from response."""
        # Look for patterns like "Minimum Age: 13" or "Age: 13"
        patterns = [
            r"Minimum Age:\s*(\d+)",
            r"Age:\s*(\d+)",
            r"(\d+)\s*years?",
            r"(\d+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                age = int(match.group(1))
                if 0 <= age <= 18:
                    return age
        
        return None
    
    def _get_cache_key(self, endpoint: str, params: dict) -> str:
        """Generate cache key for API request."""
        param_str = json.dumps(params, sort_keys=True)
        cache_input = f"{endpoint}:{param_str}"
        return hashlib.md5(cache_input.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[dict]:
        """Retrieve cached API response if available."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                # Check if cache is still fresh (24 hours)
                cache_time = cached_data.get('cached_at', 0)
                if time.time() - cache_time < 86400:  # 24 hours
                    return cached_data.get('response')
            except (json.JSONDecodeError, KeyError, FileNotFoundError):
                pass
        return None
    
    def _get_enriched_data(self, channel_name: str) -> Dict[str, Any]:
        """Get enriched data from ground truth pipeline cache or fall back to basic data."""
        # First try to get data from enriched dataset
        enriched_path = Path("05_artifacts/datasets/youtube_channel_ground_truth_enriched.csv")
        if enriched_path.exists():
            try:
                import pandas as pd
                df = pd.read_csv(enriched_path)
                match = df[df['YouTube_Channel'].str.lower() == channel_name.lower()]
                if not match.empty:
                    row = match.iloc[0]
                    evidence = json.loads(row['evidence_details'])
                    return self._format_enriched_data(channel_name, evidence)
            except Exception as e:
                print(f"Failed to load enriched data for {channel_name}: {e}")
        
        # Fall back to cached API data
        return self._get_cached_api_data(channel_name)
    
    def _format_enriched_data(self, channel_name: str, evidence: dict) -> Dict[str, Any]:
        """Format enriched evidence data for prompt evaluation."""
        # Get basic channel data from cache
        basic_data = self._get_cached_api_data(channel_name)
        
        # Add enriched criteria with token-efficient formatting
        content_flags = []
        if evidence.get("is_educational_content"):
            content_flags.append("Educational")
        if evidence.get("is_explicit_adult_content"):
            content_flags.append("Adult Content")
        if evidence.get("is_drama_controversy_heavy"):
            content_flags.append("Drama/Controversy")
        if evidence.get("is_mature_gaming_focused"):
            content_flags.append("Mature Gaming")
        if evidence.get("mature_language_detected"):
            content_flags.append("Mature Language")
        if evidence.get("made_for_kids"):
            content_flags.append("Made for Kids")
        
        # Compact content summary
        content_summary = ", ".join(content_flags) if content_flags else "General Content"
        
        # Add enriched data to basic structure
        basic_data.update({
            "content_categories": content_summary,
            "maturity_score": evidence.get("total_adult_content_score", 0),
            "safety_flags": {
                "kid_safe": evidence.get("made_for_kids", False),
                "age_restricted": evidence.get("yt_agerestricted", False),
                "adult_content": evidence.get("is_explicit_adult_content", False)
            }
        })
        
        return basic_data
    
    def _get_cached_api_data(self, channel_name: str) -> Dict[str, Any]:
        """Get basic channel data from shared API cache."""
        # Try to find cached channel data using the same approach as ground truth pipeline
        channel_id = self._find_cached_channel_id(channel_name)
        if not channel_id:
            return self._get_fallback_data(channel_name)
        
        # Get cached channel metadata
        meta_params = {"id": channel_id, "part": "snippet,topicDetails,statistics"}
        meta_cache_key = self._get_cache_key("channels_meta", meta_params)
        meta_data = self._get_cached_response(meta_cache_key)
        
        if not meta_data or not meta_data.get("items"):
            return self._get_fallback_data(channel_name)
        
        channel = meta_data["items"][0]
        
        # Get recent videos (limit to 3 for token efficiency)
        video_sample = self._get_cached_video_sample(channel_id, limit=3)
        
        return {
            "description": channel["snippet"]["description"][:300] + "..." if len(channel["snippet"]["description"]) > 300 else channel["snippet"]["description"],
            "topics": channel.get("topicDetails", {}).get("topicCategories", [])[:3],  # Limit topics
            "created_year": channel["snippet"]["publishedAt"][:4],
            "video_count": channel["statistics"].get("videoCount", "0"),
            "subscriber_count": channel["statistics"].get("subscriberCount", "0"),
            "video_sample": video_sample,
            "youtube_category": channel["snippet"].get("categoryId", "Unknown")
        }
    
    def _find_cached_channel_id(self, channel_name: str) -> Optional[str]:
        """Find channel ID from cached search results."""
        search_params = {"q": channel_name, "type": "channel", "part": "snippet", "maxResults": 1}
        cache_key = self._get_cache_key("search", search_params)
        cached_response = self._get_cached_response(cache_key)
        
        if cached_response and cached_response.get("items"):
            return cached_response["items"][0]["snippet"]["channelId"]
        return None
    
    def _get_cached_video_sample(self, channel_id: str, limit: int = 3) -> str:
        """Get cached video sample with token optimization."""
        # Get recent video IDs from cache
        search_params = {"channelId": channel_id, "order": "date", "type": "video", "part": "id", "maxResults": limit}
        cache_key = self._get_cache_key("search_videos", search_params)
        video_search = self._get_cached_response(cache_key)
        
        if not video_search or not video_search.get("items"):
            return "No recent videos available"
        
        video_titles = []
        for item in video_search["items"][:limit]:
            video_id = item["id"]["videoId"]
            # Get video snippet from cache
            snippet_params = {"id": video_id, "part": "snippet"}
            snippet_key = self._get_cache_key("videos_snippet", snippet_params)
            snippet_data = self._get_cached_response(snippet_key)
            
            if snippet_data and snippet_data.get("items"):
                title = snippet_data["items"][0]["snippet"]["title"]
                video_titles.append(title[:80] + "..." if len(title) > 80 else title)  # Truncate long titles
        
        return "; ".join(video_titles) if video_titles else "No recent videos available"
    
    def _get_fallback_data(self, channel_name: str) -> Dict[str, Any]:
        """Fallback data when no cache is available."""
        return {
            "description": f"Channel: {channel_name}",
            "topics": [],
            "created_year": "Unknown",
            "video_count": "Unknown",
            "subscriber_count": "Unknown",
            "video_sample": "No video data available",
            "youtube_category": "Unknown",
            "content_categories": "Unknown",
            "maturity_score": 0,
            "safety_flags": {
                "kid_safe": False,
                "age_restricted": False,
                "adult_content": False
            }
        }
    

def load_samples(file_path):
    """Load samples from JSONL file."""
    samples = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip():
                samples.append(json.loads(line))
    return samples

def main():
    print("Testing agerate evaluation system...")
    
    # Load samples
    try:
        samples = load_samples('data/gold_dataset.jsonl')
        print(f"✓ Loaded {len(samples)} samples")
    except Exception as e:
        print(f"✗ Sample loading error: {e}")
        return
    
    # Test one variant
    try:
        evaluator = SimpleAgerateEval(variant="v1_baseline")
        print("✓ Evaluator created")
        
        # Test with first sample
        sample = samples[0]
        print(f"Testing with: {sample['input']}")
        
        result = evaluator.eval_sample(sample)
        print("✓ Evaluation completed")
        print(f"Expected age: {result['expected_age']}")
        print(f"Predicted age: {result['predicted_age']}")
        print(f"MAE: {result['mae']}")
        
        if result['response']:
            print(f"Response: {result['response'][:200]}...")
        
    except Exception as e:
        print(f"✗ Evaluation error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()