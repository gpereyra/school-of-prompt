# youtube_age_rating_pipeline.py
"""
Automated enrichment script for the YouTube channel ground‑truth dataset.

It augments each channel with structured evidence drawn from:
  • YouTube Data API        – madeForKids flag, age‑restricted videos, regional board ratings
  • Common Sense Media      – expert age recommendation if a matching review exists
  • kidSAFE Seal Program    – independent COPPA‑plus certification list
  • (Optional) App‑store IARC – can be wired in later using Google Play / iTunes look‑ups

The adjudication rule‑set maps those signals into a single Minimum_Age, notes the source
with highest confidence, and stores a JSON blob of raw evidence for later auditing.

Prerequisites
-------------
• Python 3.10+
• `pip install google-api-python-client google-auth requests beautifulsoup4 pandas`
• Export an environment variable YT_API_KEY with a valid YouTube Data API v3 key.

Usage
-----
$ python youtube_age_rating_pipeline.py  # defaults to the CSV produced earlier

Outputs a new file: youtube_channel_ground_truth_enriched.csv
"""

from __future__ import annotations
import os
import json
import time
import logging
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
import random

import pandas as pd
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# API Throttling Configuration
API_CALLS_MADE = 0
DAILY_CALLS_MADE = 0
MAX_CALLS_PER_DAY = 9000  # Conservative limit (YouTube allows 10,000/day)
MAX_CALLS_PER_MINUTE = 2500  # Conservative limit (YouTube allows 180,000/min per user)
QUOTA_EXCEEDED = False
LAST_CALL_TIME = 0
DAILY_RESET_TIME = 0

# API Response Caching
CACHE_DIR = Path("cache/youtube_api")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def get_cache_key(endpoint: str, params: dict) -> str:
    """Generate cache key for API request."""
    # Create deterministic key from endpoint and parameters
    param_str = json.dumps(params, sort_keys=True)
    cache_input = f"{endpoint}:{param_str}"
    return hashlib.md5(cache_input.encode()).hexdigest()

# Cache statistics
CACHE_HITS = 0
CACHE_MISSES = 0

def get_cached_response(cache_key: str) -> Optional[dict]:
    """Retrieve cached API response if available."""
    global CACHE_HITS, CACHE_MISSES
    
    cache_file = CACHE_DIR / f"{cache_key}.json"
    if cache_file.exists():
        try:
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            # Check if cache is still fresh (24 hours)
            cache_time = cached_data.get('cached_at', 0)
            if time.time() - cache_time < 86400:  # 24 hours
                CACHE_HITS += 1
                logging.debug(f"Cache hit for {cache_key}")
                return cached_data.get('response')
            else:
                logging.debug(f"Cache expired for {cache_key}")
                cache_file.unlink()  # Remove expired cache
        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            pass
    
    CACHE_MISSES += 1
    return None

def cache_response(cache_key: str, response: dict):
    """Cache API response for future use."""
    cache_file = CACHE_DIR / f"{cache_key}.json"
    try:
        cache_data = {
            'cached_at': time.time(),
            'response': response
        }
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
        logging.debug(f"Cached response for {cache_key}")
    except Exception as e:
        logging.warning(f"Failed to cache response: {e}")

def load_config():
    """Load API key from config.json file."""
    config_path = Path("config/api_keys.json")
    if not config_path.exists():
        raise SystemExit("config.json not found. Make sure you have your API keys configured.")
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        raise SystemExit(f"Invalid JSON in config.json: {e}")

config = load_config()
API_KEY = config.get("youtube_api_key")
SERVICE_NAME = "youtube"
API_VERSION = "v3"

if not API_KEY:
    raise SystemExit("youtube_api_key not found in config.json")

# ---------------------------------------------------------------------------
# API Throttling helpers
# ---------------------------------------------------------------------------

def throttle_api_call():
    """Implement intelligent rate limiting for YouTube API calls."""
    global API_CALLS_MADE, DAILY_CALLS_MADE, LAST_CALL_TIME, DAILY_RESET_TIME, QUOTA_EXCEEDED
    
    if QUOTA_EXCEEDED:
        logging.warning("Quota exceeded, skipping API calls")
        return False
    
    current_time = time.time()
    
    # Reset daily counter (approximately every 24 hours)
    if current_time - DAILY_RESET_TIME > 86400:  # 24 hours
        DAILY_CALLS_MADE = 0
        DAILY_RESET_TIME = current_time
        logging.info("Daily quota counter reset")
    
    # Check daily quota
    if DAILY_CALLS_MADE >= MAX_CALLS_PER_DAY:
        logging.warning(f"Daily quota limit reached ({MAX_CALLS_PER_DAY} calls)")
        QUOTA_EXCEEDED = True
        return False
    
    # Reset minute counter
    if current_time - LAST_CALL_TIME > 60:
        API_CALLS_MADE = 0
        LAST_CALL_TIME = current_time
    
    # Check per-minute rate limit
    if API_CALLS_MADE >= MAX_CALLS_PER_MINUTE:
        wait_time = 60 - (current_time - LAST_CALL_TIME)
        if wait_time > 0:
            logging.info(f"Per-minute rate limit reached, waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
            API_CALLS_MADE = 0
            LAST_CALL_TIME = time.time()
    
    # Minimal delay for burst protection (much smaller now given higher limits)
    time.sleep(0.1)  # 100ms between calls
    
    API_CALLS_MADE += 1
    DAILY_CALLS_MADE += 1
    return True

def handle_api_error(error, operation):
    """Handle API errors and update throttling state."""
    global QUOTA_EXCEEDED
    
    if error.resp.status == 403 and "quotaExceeded" in str(error):
        QUOTA_EXCEEDED = True
        logging.warning(f"YouTube API quota exceeded during {operation}")
        return None
    elif error.resp.status == 429:  # Rate limit
        wait_time = random.uniform(30, 60)
        logging.warning(f"Rate limited, waiting {wait_time:.1f}s...")
        time.sleep(wait_time)
        return "retry"
    else:
        logging.warning(f"API error during {operation}: {error}")
        return None

# ---------------------------------------------------------------------------
# YouTube helpers
# ---------------------------------------------------------------------------

def get_youtube_client():
    """Return a cached YouTube Data API client."""
    return build(SERVICE_NAME, API_VERSION, developerKey=API_KEY, cache_discovery=False)


def resolve_channel_id(youtube, channel_name: str) -> Optional[str]:
    """Resolve a human channel name → canonical channelId (via search endpoint)."""
    # Check cache first
    params = {"q": channel_name, "type": "channel", "part": "snippet", "maxResults": 1}
    cache_key = get_cache_key("search", params)
    cached_response = get_cached_response(cache_key)
    
    if cached_response:
        items = cached_response.get("items", [])
        return items[0]["snippet"]["channelId"] if items else None
    
    # Make API call if not cached
    if not throttle_api_call():
        return None
    
    try:
        req = youtube.search().list(**params)
        res = req.execute()
        
        # Cache the response
        cache_response(cache_key, res)
        
        items = res.get("items", [])
        return items[0]["snippet"]["channelId"] if items else None
    except HttpError as e:
        result = handle_api_error(e, "resolve_channel_id")
        if result == "retry":
            return resolve_channel_id(youtube, channel_name)  # Retry once
        return None


def get_channel_status(youtube, channel_id: str) -> Dict[str, Any]:
    # Check cache first
    params = {"id": channel_id, "part": "status"}
    cache_key = get_cache_key("channels_status", params)
    cached_response = get_cached_response(cache_key)
    
    if cached_response:
        items = cached_response.get("items", [])
        return items[0]["status"] if items else {}
    
    # Make API call if not cached
    if not throttle_api_call():
        return {}
    
    try:
        req = youtube.channels().list(**params)
        res = req.execute()
        
        # Cache the response
        cache_response(cache_key, res)
        
        items = res.get("items", [])
        return items[0]["status"] if items else {}
    except HttpError as e:
        result = handle_api_error(e, "get_channel_status")
        if result == "retry":
            return get_channel_status(youtube, channel_id)
        return {}


def get_channel_meta(youtube, channel_id: str) -> Dict[str, Any]:
    # Check cache first
    params = {"id": channel_id, "part": "snippet,topicDetails,statistics"}
    cache_key = get_cache_key("channels_meta", params)
    cached_response = get_cached_response(cache_key)
    
    if cached_response:
        if not cached_response.get("items"):
            return {}
        channel = cached_response["items"][0]
        return {
            "description": channel["snippet"]["description"],
            "topics": channel.get("topicDetails", {}).get("topicCategories", []),
            "created_year": channel["snippet"]["publishedAt"][:4],
            "video_count": channel["statistics"].get("videoCount", "0"),
            "subscriber_count": channel["statistics"].get("subscriberCount", "0"),
            "youtube_category": channel["snippet"].get("categoryId", "Unknown")
        }
    
    # Make API call if not cached
    if not throttle_api_call():
        return {}
    
    try:
        req = youtube.channels().list(**params)
        res = req.execute()
        
        # Cache the response
        cache_response(cache_key, res)
        
        if not res.get("items"):
            return {}
        
        channel = res["items"][0]
        return {
            "description": channel["snippet"]["description"],
            "topics": channel.get("topicDetails", {}).get("topicCategories", []),
            "created_year": channel["snippet"]["publishedAt"][:4],
            "video_count": channel["statistics"].get("videoCount", "0"),
            "subscriber_count": channel["statistics"].get("subscriberCount", "0"),
            "youtube_category": channel["snippet"].get("categoryId", "Unknown")
        }
    except HttpError as e:
        result = handle_api_error(e, "get_channel_meta")
        if result == "retry":
            return get_channel_meta(youtube, channel_id)
        return {}


def list_recent_videos(youtube, channel_id: str, limit: int = 10) -> List[str]:
    # Check cache first
    params = {"channelId": channel_id, "order": "date", "type": "video", "part": "id", "maxResults": limit}
    cache_key = get_cache_key("search_videos", params)
    cached_response = get_cached_response(cache_key)
    
    if cached_response:
        return [it["id"]["videoId"] for it in cached_response.get("items", [])]
    
    # Make API call if not cached
    if not throttle_api_call():
        return []
    
    try:
        req = youtube.search().list(**params)
        res = req.execute()
        
        # Cache the response
        cache_response(cache_key, res)
        
        return [it["id"]["videoId"] for it in res.get("items", [])]
    except HttpError as e:
        result = handle_api_error(e, "list_recent_videos")
        if result == "retry":
            return list_recent_videos(youtube, channel_id, limit)
        return []


def get_video_content_rating(youtube, video_id: str) -> Dict[str, Any]:
    # Check cache first
    params = {"id": video_id, "part": "contentDetails"}
    cache_key = get_cache_key("videos_rating", params)
    cached_response = get_cached_response(cache_key)
    
    if cached_response:
        items = cached_response.get("items", [])
        return items[0]["contentDetails"].get("contentRating", {}) if items else {}
    
    # Make API call if not cached
    if not throttle_api_call():
        return {}
    
    try:
        req = youtube.videos().list(**params)
        res = req.execute()
        
        # Cache the response
        cache_response(cache_key, res)
        
        items = res.get("items", [])
        return items[0]["contentDetails"].get("contentRating", {}) if items else {}
    except HttpError as e:
        result = handle_api_error(e, "get_video_content_rating")
        if result == "retry":
            return get_video_content_rating(youtube, video_id)
        return {}

# ---------------------------------------------------------------------------
# Third‑party sources (scraping proxies – upgrade to official feeds if available)
# ---------------------------------------------------------------------------

CSM_BASE = "https://www.commonsensemedia.org/search/"
KIDSAFE_URL = "https://www.kidsafeseal.com/certifiedproducts.html"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; GroundTruthBot/1.0)"}


def get_common_sense_age(channel_name: str) -> Optional[int]:
    """Return the recommended minimum age from Common Sense Media, if any."""
    url = f"{CSM_BASE}{channel_name.replace(' ', '%20')}"
    try:
        html = requests.get(url, timeout=15, headers=HEADERS).text
    except requests.RequestException:
        return None
    soup = BeautifulSoup(html, "html.parser")
    badge = soup.find("span", class_=lambda c: c and "csm-green" in c)
    if badge and badge.text.strip().isdigit():
        return int(badge.text.strip())
    return None


def is_kidsafe_listed(channel_name: str) -> bool:
    """Heuristic: presence of the channel name on kidSAFE certification list."""
    try:
        html = requests.get(KIDSAFE_URL, timeout=15, headers=HEADERS).text.lower()
    except requests.RequestException:
        return False
    return channel_name.lower() in html


def analyze_content_maturity(videos: List[Dict[str, Any]], channel_description: str = "") -> Dict[str, Any]:
    """Analyze video content and channel for maturity indicators based on criteria."""
    
    # Educational indicators
    educational_keywords = {
        "tutorial", "learn", "education", "lesson", "course", "study", "school", "university",
        "science", "history", "math", "physics", "chemistry", "biology", "geography",
        "recipe", "cooking", "how to", "diy", "instructions", "guide", "explained",
        "documentary", "facts", "research", "analysis", "academic", "scholarly"
    }
    
    # Explicit adult content indicators  
    explicit_adult_keywords = {
        "porn", "sex", "nude", "naked", "explicit", "nsfw", "adult only", "18+",
        "onlyfans", "escort", "prostitute", "stripper", "cam girl", "xxx", "sexy",
        "bikini", "underwear", "lingerie", "fetish", "erotic", "seduction"
    }
    
    # Drama/controversy indicators (stronger adult content signals)
    drama_keywords = {
        "drama", "exposed", "controversy", "scandal", "beef", "calling out", "destroyed", 
        "roasted", "cancelled", "toxic", "problematic", "allegations", "lawsuit",
        "predator", "grooming", "harassment", "abuse", "assault", "criminal", "arrest",
        "court", "police", "investigation", "victim", "stalking", "threatening"
    }
    
    # Adult personality/behavior indicators
    adult_personality_keywords = {
        "drunk", "drinking", "alcohol", "party", "club", "bar", "wasted", "hangover",
        "smoking", "vape", "weed", "drugs", "high", "stoned", "pills", "cocaine",
        "gambling", "casino", "bet", "poker", "strip club", "hookup", "dating app",
        "tinder", "bumble", "relationship drama", "cheating", "affair", "breakup"
    }
    
    # Mature content themes
    mature_themes_keywords = {
        "depression", "suicide", "self harm", "cutting", "mental health crisis",
        "eating disorder", "anorexia", "bulimia", "addiction", "rehab", "therapy",
        "violence", "fight", "beating", "blood", "gore", "murder", "death", "kill"
    }
    
    # Mature gaming indicators
    mature_gaming_keywords = {
        "call of duty", "grand theft auto", "gta", "mortal kombat", "resident evil",
        "doom", "battlefield", "dead space", "outlast", "horror game", "rated m",
        "mature rating", "violent game", "shooter", "fps"
    }
    
    # Profanity detection
    profanity_keywords = {
        "fuck", "shit", "damn", "hell", "ass", "bitch", "bastard", "piss", "crap"
    }
    
    # Count occurrences across all content
    educational_count = 0
    explicit_count = 0
    drama_count = 0
    mature_gaming_count = 0
    profanity_count = 0
    adult_personality_count = 0
    mature_themes_count = 0
    
    # Analyze channel description
    channel_text = channel_description.lower()
    for keyword in educational_keywords:
        if keyword in channel_text:
            educational_count += 2  # Channel description gets double weight
    
    # Check channel description for adult indicators
    for keyword in explicit_adult_keywords:
        if keyword in channel_text:
            explicit_count += 3  # High weight for channel description
    for keyword in drama_keywords:
        if keyword in channel_text:
            drama_count += 2
    for keyword in adult_personality_keywords:
        if keyword in channel_text:
            adult_personality_count += 2
    for keyword in mature_themes_keywords:
        if keyword in channel_text:
            mature_themes_count += 2
    
    # Analyze video content
    for video in videos:
        title = video.get("title", "").lower()
        description = video.get("description", "").lower()[:500]  # Limit description length
        tags = " ".join(video.get("tags", [])).lower()
        
        video_text = f"{title} {description} {tags}"
        
        # Count different content types
        for keyword in educational_keywords:
            if keyword in video_text:
                educational_count += 1
                
        for keyword in explicit_adult_keywords:
            if keyword in video_text:
                explicit_count += 1
                
        for keyword in drama_keywords:
            if keyword in video_text:
                drama_count += 1
                
        for keyword in mature_gaming_keywords:
            if keyword in video_text:
                mature_gaming_count += 1
                
        for keyword in profanity_keywords:
            if keyword in video_text:
                profanity_count += 1
                
        for keyword in adult_personality_keywords:
            if keyword in video_text:
                adult_personality_count += 1
                
        for keyword in mature_themes_keywords:
            if keyword in video_text:
                mature_themes_count += 1
    
    video_count = len(videos) if videos else 1
    
    # Calculate comprehensive adult content score
    adult_content_score = explicit_count + (adult_personality_count * 0.5) + (mature_themes_count * 0.7)
    
    return {
        # Content category flags
        "is_educational_content": educational_count >= max(3, video_count * 0.4),
        "is_explicit_adult_content": explicit_count >= 1 or adult_content_score >= 2,
        "is_drama_controversy_heavy": drama_count >= max(2, video_count * 0.3),
        "is_mature_gaming_focused": mature_gaming_count >= max(2, video_count * 0.3),
        "is_adult_personality_heavy": adult_personality_count >= max(2, video_count * 0.2),
        "is_mature_themes_heavy": mature_themes_count >= max(2, video_count * 0.2),
        
        # Legacy flags with improved thresholds
        "mature_language_detected": profanity_count >= 1,
        "adult_keywords_detected": explicit_count >= 1 or adult_content_score >= 2,
        "gaming_mature_rating": mature_gaming_count >= 1,
        
        # Frequency counts for threshold-based decisions
        "profanity_frequency": profanity_count,
        "adult_keyword_frequency": explicit_count,
        "mature_game_count": mature_gaming_count,
        "educational_score": educational_count,
        "drama_score": drama_count,
        "adult_personality_score": adult_personality_count,
        "mature_themes_score": mature_themes_count,
        "total_adult_content_score": adult_content_score
    }

# ---------------------------------------------------------------------------
# Adjudication logic – adjust weights or precedence as your policy evolves
# ---------------------------------------------------------------------------

def adjudicate_evidence(evidence: Dict[str, Any], channel_name: str = "") -> Tuple[int, str, str]:
    """Condense raw evidence → (min_age, source_label, short_note)."""
    # Highest confidence sources first - Official API data
    if evidence.get("made_for_kids"):
        return 3, "YouTube_madeForKids", "Channel flagged Made for Kids in YouTube Data API"
    if (age := evidence.get("common_sense_age")):
        return age, "CommonSenseMedia", "CSM recommended age"
    if evidence.get("kidsafe"):
        return 4, "kidSAFE", "Listed as kidSAFE certified"
    if evidence.get("yt_agerestricted"):
        return 18, "YouTube_AgeRestricted", "Majority content age‑restricted"
    if (age := evidence.get("video_board_max_age")):
        return age, "RegionalBoardMax", "Max rating across recent uploads"
    
    # Content category analysis - HIGH PRIORITY
    if evidence.get("is_educational_content"):
        return 13, "EducationalContent", "Educational/instructional content detected"
    if evidence.get("is_explicit_adult_content"):
        return 18, "ExplicitContent", "Explicit adult content detected"
    if evidence.get("is_drama_controversy_heavy"):
        return 18, "DramaContent", "Heavy drama/controversy content detected"
    if evidence.get("is_adult_personality_heavy"):
        return 18, "AdultPersonality", "Adult lifestyle/personality content detected"
    if evidence.get("is_mature_themes_heavy"):
        return 17, "MatureThemes", "Mature themes (violence, mental health) detected"
    if evidence.get("is_mature_gaming_focused"):
        return 17, "MatureGaming", "Mature gaming content focus detected"
    
    # Comprehensive adult content scoring
    total_adult_score = evidence.get("total_adult_content_score", 0)
    if total_adult_score >= 3:
        return 18, "AdultContentScore", f"High adult content score: {total_adult_score:.1f}"
    
    # Content-based detection with thresholds
    if evidence.get("adult_keywords_detected") and evidence.get("adult_keyword_frequency", 0) >= 2:
        return 18, "AdultKeywords", "Multiple adult-oriented keywords detected"
    if evidence.get("mature_language_detected") and evidence.get("profanity_frequency", 0) >= 3:
        return 17, "MatureLanguage", "Frequent mature language detected"
    if evidence.get("gaming_mature_rating") and evidence.get("mature_game_count", 0) >= 3:
        return 17, "MatureGaming", "Multiple mature-rated games detected"
    
    # Fallback per YouTube policy
    return 13, "Default", "Fallback to YouTube minimum age per policy"

# ---------------------------------------------------------------------------
# ETL driver
# ---------------------------------------------------------------------------

def enrich_dataset(csv_path: str, out_path: str, limit_rows: int = None, test_random: bool = False) -> str:
    youtube = get_youtube_client()
    df = pd.read_csv(csv_path)
    
    if limit_rows:
        if test_random:
            # Get first 5 + random 5 from different sections
            first_5 = df.head(5)
            # Sample from different sections: adult content, children's content, educational, etc.
            random_indices = [25, 60, 96, 136, 190]  # Spread across categories
            random_5 = df.iloc[random_indices]
            df = pd.concat([first_5, random_5]).reset_index(drop=True)
            logging.info(f"Processing first 5 rows + 5 random rows from different categories")
        else:
            df = df.head(limit_rows)
            logging.info(f"Processing only first {limit_rows} rows for testing")
    
    for idx, row in df.iterrows():
        chan = row["YouTube_Channel"]
        evidence: Dict[str, Any] = {}
        # YouTube API data collection (with throttling)
        cid = resolve_channel_id(youtube, chan)
        if cid:
            status = get_channel_status(youtube, cid)
            evidence["made_for_kids"] = status.get("madeForKids", False)
            # recent uploads – may be fewer than 10 if new/sparse channel
            vids = list_recent_videos(youtube, cid, limit=15)
            ratings = [get_video_content_rating(youtube, v) for v in vids if v]
            evidence["yt_agerestricted"] = any(r.get("ytRating") == "ytAgeRestricted" for r in ratings)
            # simple numeric extraction from regional rating strings (e.g., "7", "16", etc.)
            board_ages: List[int] = []
            for r in ratings:
                for val in r.values():
                    if isinstance(val, str) and val.isdigit():
                        board_ages.append(int(val))
            evidence["video_board_max_age"] = max(board_ages) if board_ages else None
        
        # Third‑party sources
        evidence["common_sense_age"] = get_common_sense_age(chan)
        evidence["kidsafe"] = is_kidsafe_listed(chan)
        
        # Content maturity analysis
        channel_description = ""
        if cid:  # Only if we successfully got channel data
            # Get channel description
            channel_meta = get_channel_meta(youtube, cid)
            channel_description = channel_meta.get("description", "")
            
            # Get video details for content analysis (cached)
            recent_videos = list_recent_videos(youtube, cid, limit=10)
            video_details = []
            for vid_id in recent_videos:
                # Check cache first
                params = {"id": vid_id, "part": "snippet"}
                cache_key = get_cache_key("videos_snippet", params)
                cached_response = get_cached_response(cache_key)
                
                if cached_response:
                    if cached_response.get("items"):
                        video_details.append({
                            "title": cached_response["items"][0]["snippet"]["title"],
                            "description": cached_response["items"][0]["snippet"]["description"],
                            "tags": cached_response["items"][0]["snippet"].get("tags", [])
                        })
                else:
                    # Make API call if not cached
                    if not throttle_api_call():
                        break  # Stop if quota exceeded
                    try:
                        vid_req = youtube.videos().list(**params)
                        vid_res = vid_req.execute()
                        
                        # Cache the response
                        cache_response(cache_key, vid_res)
                        
                        if vid_res.get("items"):
                            video_details.append({
                                "title": vid_res["items"][0]["snippet"]["title"],
                                "description": vid_res["items"][0]["snippet"]["description"],
                                "tags": vid_res["items"][0]["snippet"].get("tags", [])
                            })
                    except HttpError as e:
                        handle_api_error(e, "video_details")
                        break  # Stop on error
            
            maturity_analysis = analyze_content_maturity(video_details, channel_description)
            evidence.update(maturity_analysis)

        min_age, src, note = adjudicate_evidence(evidence, chan)
        df.at[idx, "enriched_age"] = min_age
        df.at[idx, "evidence_source"] = src
        df.at[idx, "evidence_timestamp"] = datetime.now(timezone.utc).isoformat()
        df.at[idx, "evidence_details"] = json.dumps(evidence, ensure_ascii=False)
        time.sleep(0.2)  # politeness delay – tweak depending on quota & crawl etiquette

        # Progress logging
        if (idx + 1) % 5 == 0:
            logging.info(f"Processed {idx + 1}/{len(df)} channels, Daily API calls: {DAILY_CALLS_MADE}/{MAX_CALLS_PER_DAY}")

    df.to_csv(out_path, index=False)
    logging.info("Enriched dataset written → %s", out_path)
    logging.info(f"Total API calls made today: {DAILY_CALLS_MADE}/{MAX_CALLS_PER_DAY}")
    logging.info(f"Cache performance: {CACHE_HITS} hits, {CACHE_MISSES} misses ({CACHE_HITS/(CACHE_HITS+CACHE_MISSES)*100:.1f}% hit rate)")
    return out_path

# ---------------------------------------------------------------------------
# Script entry‑point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    INPUT_CSV = "05_artifacts/datasets/youtube_channel_ground_truth.csv"
    OUTPUT_CSV = "05_artifacts/datasets/youtube_channel_ground_truth_enriched.csv"
    
    # Reset quota state for new run (modify module-level variables)
    import sys
    current_module = sys.modules[__name__]
    current_module.QUOTA_EXCEEDED = False
    current_module.DAILY_CALLS_MADE = 0
    current_module.DAILY_RESET_TIME = time.time()
    
    # Test with first 10 + random 10 from different categories
    enrich_dataset(INPUT_CSV, OUTPUT_CSV, limit_rows=20, test_random=True)
