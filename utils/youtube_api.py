from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import isodate
import functools

# Create cached functions outside of the class to avoid the self parameter issue
@st.cache_data(ttl=3600)
def cached_channel_info(api_key, channel_id):
    """Cached wrapper for channel info"""
    youtube = build('youtube', 'v3', developerKey=api_key)
    try:
        response = youtube.channels().list(
            part="snippet,statistics",
            id=channel_id
        ).execute()
        return response
    except HttpError as e:
        st.error(f"Error fetching channel information: {e}")
        return None

@st.cache_data(ttl=3600)
def cached_channel_videos(api_key, channel_id, published_after=None, max_results=50):
    """Cached wrapper for channel videos"""
    youtube = build('youtube', 'v3', developerKey=api_key)
    try:
        request_params = {
            "part": "snippet",
            "channelId": channel_id,
            "maxResults": max_results,
            "order": "date",
            "type": "video"
        }
        
        if published_after:
            request_params["publishedAfter"] = published_after
            
        response = youtube.search().list(**request_params).execute()
        return response
    except HttpError as e:
        st.error(f"Error fetching channel videos: {e}")
        return None

@st.cache_data(ttl=3600)
def cached_videos_statistics(api_key, video_ids):
    """Cached wrapper for videos statistics"""
    youtube = build('youtube', 'v3', developerKey=api_key)
    try:
        if not video_ids:
            return {"items": []}
            
        # YouTube API accepts a maximum of 50 video IDs per request
        chunks = [video_ids[i:i+50] for i in range(0, len(video_ids), 50)]
        all_items = []
        
        for chunk in chunks:
            response = youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=','.join(chunk)
            ).execute()
            all_items.extend(response.get("items", []))
        
        return {"items": all_items}
    except HttpError as e:
        st.error(f"Error fetching video statistics: {e}")
        return None

class YouTubeAPI:
    """
    A class to handle YouTube Data API interactions
    """
    def __init__(self, api_key):
        """
        Initialize the YouTube API client
        
        Args:
            api_key (str): YouTube Data API key
        """
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)
    
    def get_channel_info(self, channel_id):
        """
        Get channel information
        
        Args:
            channel_id (str): YouTube channel ID
            
        Returns:
            dict: Channel information
        """
        return cached_channel_info(self.api_key, channel_id)
    
    def get_channel_videos(self, channel_id, published_after=None, max_results=50):
        """
        Get videos from a channel
        
        Args:
            channel_id (str): YouTube channel ID
            published_after (str): ISO 8601 timestamp for filtering videos published after this date
            max_results (int): Maximum number of results to return
            
        Returns:
            dict: Videos information
        """
        return cached_channel_videos(self.api_key, channel_id, published_after, max_results)
    
    def get_videos_statistics(self, video_ids):
        """
        Get statistics for a list of videos
        
        Args:
            video_ids (list): List of YouTube video IDs
            
        Returns:
            dict: Video statistics
        """
        return cached_videos_statistics(self.api_key, video_ids)
            
    def get_video_comments(self, video_id, max_results=100):
        """
        Get comments for a video
        
        Args:
            video_id (str): YouTube video ID
            max_results (int): Maximum number of comments to return
            
        Returns:
            dict: Video comments
        """
        try:
            response = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=max_results,
                textFormat="plainText"
            ).execute()
            return response
        except HttpError as e:
            # Some videos might have comments disabled
            if e.resp.status == 403:
                return {"items": []}
            st.error(f"Error fetching video comments: {e}")
            return None
