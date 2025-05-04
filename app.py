import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

from utils.youtube_api import YouTubeAPI
from utils.data_processing import process_channel_statistics, process_video_statistics
from components.channel_metrics import display_channel_metrics
from components.video_metrics import display_video_metrics

# Set page config
st.set_page_config(
    page_title="MrBeast Channel Analytics",
    page_icon="📊",
    layout="wide"
)

# Initialize YouTube API
api_key = os.getenv("YOUTUBE_API_KEY", "")
if not api_key:
    st.error("YouTube API key not found. Please set the YOUTUBE_API_KEY environment variable.")
    st.stop()

youtube_api = YouTubeAPI(api_key)

# MrBeast channel ID
MR_BEAST_CHANNEL_ID = "UCX6OQ3DkcsbYNE6H8uQQuVA"

# App title
st.title("📊 MrBeast Channel Analytics Dashboard")

# Get channel info
try:
    channel_info = youtube_api.get_channel_info(MR_BEAST_CHANNEL_ID)
    channel_name = channel_info["items"][0]["snippet"]["title"]
    channel_thumbnail = channel_info["items"][0]["snippet"]["thumbnails"]["default"]["url"]
    subscriber_count = int(channel_info["items"][0]["statistics"]["subscriberCount"])
    view_count = int(channel_info["items"][0]["statistics"]["viewCount"])
    video_count = int(channel_info["items"][0]["statistics"]["videoCount"])
    
    # Display channel header
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image(channel_thumbnail, width=100)
    with col2:
        st.header(channel_name)
        st.write(f"📈 {subscriber_count:,} subscribers • {video_count:,} videos • {view_count:,} views")
    
    # Time period filter
    st.sidebar.header("Filter Options")
    time_period = st.sidebar.selectbox(
        "Time Period",
        ["Last 7 days", "Last 30 days", "Last 90 days", "Last 365 days"],
        index=1
    )
    
    # Convert time period to days
    days_map = {
        "Last 7 days": 7,
        "Last 30 days": 30,
        "Last 90 days": 90,
        "Last 365 days": 365
    }
    days = days_map[time_period]
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    published_after = start_date.isoformat("T") + "Z"
    
    # Get videos based on time period
    videos = youtube_api.get_channel_videos(MR_BEAST_CHANNEL_ID, published_after=published_after)
    
    if not videos["items"]:
        st.warning(f"No videos found in the selected time period ({time_period})")
    else:
        # Process data
        video_ids = [item["id"]["videoId"] for item in videos["items"]]
        video_statistics = youtube_api.get_videos_statistics(video_ids)
        
        # Process channel and video statistics
        channel_stats = process_channel_statistics(videos, video_statistics)
        video_stats_df = process_video_statistics(videos, video_statistics)
        
        # Create tabs for different views
        tab1, tab2 = st.tabs(["Channel Performance", "Video Performance"])
        
        with tab1:
            display_channel_metrics(channel_stats, video_stats_df)
            
        with tab2:
            display_video_metrics(video_stats_df)
            
except Exception as e:
    st.error(f"An error occurred while fetching data: {str(e)}")
    st.info("Please check your API key and internet connection.")
