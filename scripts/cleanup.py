#!/usr/bin/env python3
"""
Clean YouTube data cache.
"""

import os
import shutil
from pathlib import Path

def clean_cache():
    """Remove all cached YouTube data."""
    cache_dir = Path("cache/youtube")
    
    if not cache_dir.exists():
        print("No cache directory found.")
        return
    
    # Count files before deletion
    cache_files = list(cache_dir.glob("*.json"))
    file_count = len(cache_files)
    
    if file_count == 0:
        print("Cache is already empty.")
        return
    
    # Remove all cache files
    try:
        shutil.rmtree(cache_dir)
        print(f"Removed {file_count} cached files.")
        
        # Recreate empty directory
        cache_dir.mkdir(parents=True, exist_ok=True)
        print("Cache directory cleaned.")
        
    except Exception as e:
        print(f"Error cleaning cache: {e}")

def list_cache():
    """List all cached files."""
    cache_dir = Path("cache/youtube")
    
    if not cache_dir.exists():
        print("No cache directory found.")
        return
    
    cache_files = list(cache_dir.glob("*.json"))
    
    if not cache_files:
        print("Cache is empty.")
        return
    
    print(f"Found {len(cache_files)} cached files:")
    
    for cache_file in cache_files:
        try:
            # Get file size
            size_bytes = cache_file.stat().st_size
            size_kb = size_bytes / 1024
            
            # Try to read channel name from cached data
            import json
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    # The cached data doesn't contain channel name, so we'll use filename
                    print(f"  {cache_file.name} ({size_kb:.1f} KB)")
            except:
                print(f"  {cache_file.name} ({size_kb:.1f} KB) - corrupted")
                
        except Exception as e:
            print(f"  {cache_file.name} - error reading file")

def main():
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "list":
            list_cache()
        elif command == "clean":
            clean_cache()
        else:
            print("Usage: python clean_cache.py [list|clean]")
            print("  list  - List cached files")
            print("  clean - Remove all cached files")
    else:
        print("Usage: python clean_cache.py [list|clean]")
        print("  list  - List cached files") 
        print("  clean - Remove all cached files")

if __name__ == "__main__":
    main()