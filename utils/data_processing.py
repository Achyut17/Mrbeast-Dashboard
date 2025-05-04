import pandas as pd
import numpy as np
from datetime import datetime
import isodate

def process_channel_statistics(videos, video_statistics):
    """
    Process channel statistics from video data
    
    Args:
        videos (dict): YouTube search results containing video metadata
        video_statistics (dict): Statistics for the videos
        
    Returns:
        dict: Processed channel statistics
    """
    video_count = len(videos.get("items", []))
    
    if video_count == 0 or not video_statistics.get("items"):
        return {
            "video_count": 0,
            "avg_views": 0,
            "avg_likes": 0,
            "avg_comments": 0,
            "avg_duration_seconds": 0,
            "total_views": 0,
            "total_likes": 0,
            "total_comments": 0
        }
    
    total_views = 0
    total_likes = 0
    total_comments = 0
    total_duration_seconds = 0
    
    for video in video_statistics.get("items", []):
        total_views += int(video.get("statistics", {}).get("viewCount", 0))
        total_likes += int(video.get("statistics", {}).get("likeCount", 0))
        total_comments += int(video.get("statistics", {}).get("commentCount", 0))
        
        # Parse duration from ISO 8601 format
        duration_iso = video.get("contentDetails", {}).get("duration", "PT0S")
        duration = isodate.parse_duration(duration_iso)
        total_duration_seconds += duration.total_seconds()
    
    return {
        "video_count": video_count,
        "avg_views": total_views / video_count if video_count > 0 else 0,
        "avg_likes": total_likes / video_count if video_count > 0 else 0,
        "avg_comments": total_comments / video_count if video_count > 0 else 0,
        "avg_duration_seconds": total_duration_seconds / video_count if video_count > 0 else 0,
        "total_views": total_views,
        "total_likes": total_likes,
        "total_comments": total_comments
    }

def process_video_statistics(videos, video_statistics):
    """
    Process statistics for individual videos
    
    Args:
        videos (dict): YouTube search results containing video metadata
        video_statistics (dict): Statistics for the videos
        
    Returns:
        pandas.DataFrame: Processed video statistics
    """
    if not videos.get("items") or not video_statistics.get("items"):
        return pd.DataFrame()
    
    # Create a mapping from video ID to search results
    video_search_data = {}
    for item in videos.get("items", []):
        video_id = item.get("id", {}).get("videoId")
        if video_id:
            video_search_data[video_id] = item
    
    # Process video statistics
    video_data = []
    for video in video_statistics.get("items", []):
        video_id = video.get("id")
        
        # Get data from search results
        search_data = video_search_data.get(video_id, {})
        
        # Get video statistics
        statistics = video.get("statistics", {})
        
        # Get video content details
        content_details = video.get("contentDetails", {})
        
        # Parse duration from ISO 8601 format
        duration_iso = content_details.get("duration", "PT0S")
        duration = isodate.parse_duration(duration_iso)
        duration_seconds = duration.total_seconds()
        
        # Format duration for display
        minutes, seconds = divmod(duration_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        duration_formatted = ""
        if hours > 0:
            duration_formatted = f"{int(hours)}:{int(minutes):02d}:{int(seconds):02d}"
        else:
            duration_formatted = f"{int(minutes)}:{int(seconds):02d}"
        
        # Parse published date
        published_at = video.get("snippet", {}).get("publishedAt")
        if published_at:
            published_date = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
            published_date_formatted = published_date.strftime("%b %d, %Y")
        else:
            published_date_formatted = "Unknown"
        
        video_data.append({
            "id": video_id,
            "title": video.get("snippet", {}).get("title", "Unknown"),
            "description": video.get("snippet", {}).get("description", ""),
            "published_at": published_at,
            "published_date": published_date_formatted,
            "views": int(statistics.get("viewCount", 0)),
            "likes": int(statistics.get("likeCount", 0)),
            "comments": int(statistics.get("commentCount", 0)),
            "duration_seconds": duration_seconds,
            "duration": duration_formatted,
            "thumbnail": video.get("snippet", {}).get("thumbnails", {}).get("medium", {}).get("url", "")
        })
    
    df = pd.DataFrame(video_data)
    
    # Sort by publication date (most recent first)
    if not df.empty and "published_at" in df.columns:
        df["published_at"] = pd.to_datetime(df["published_at"])
        df = df.sort_values(by="published_at", ascending=False)
    
    return df

def format_duration(seconds):
    """
    Format seconds into a human-readable duration
    
    Args:
        seconds (float): Duration in seconds
        
    Returns:
        str: Formatted duration
    """
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    elif minutes > 0:
        return f"{int(minutes)}m {int(seconds)}s"
    else:
        return f"{int(seconds)}s"
