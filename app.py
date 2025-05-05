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

# Add dark/light mode toggle in sidebar
with st.sidebar:
    st.title("Settings")
    
    # Dark/Light mode toggle
    theme_mode = st.radio("Theme", ["Light", "Dark"])
    
    # Apply theme selection using custom CSS
    if theme_mode == "Dark":
        # Apply dark theme
        st.markdown("""
            <style>
                .stApp {
                    background-color: #0E1117;
                    color: #FAFAFA;
                }
                .stTabs [data-baseweb="tab-list"] {
                    background-color: #262730;
                }
                .stTabs [data-baseweb="tab"] {
                    color: #FAFAFA;
                }
                div[data-testid="stSidebar"] {
                    background-color: #262730;
                    color: #FAFAFA;
                }
                .stRadio label, .stCheckbox label {
                    color: #FAFAFA !important;
                }
                div.stSelectbox label {
                    color: #FAFAFA !important;
                }
                div.stSelectbox div[data-baseweb="select"] {
                    background-color: #262730;
                }
                .streamlit-expanderHeader {
                    color: #FAFAFA !important;
                }
                button[kind="secondary"] {
                    background-color: #262730;
                    color: #FAFAFA;
                }
                .stDateInput > div {
                    color: #FAFAFA;
                }
                .css-ch5dnh {
                    color: #FAFAFA !important;
                }
                .css-1d0aukl {
                    color: #FAFAFA !important;
                }
            </style>
       """, unsafe_allow_html=True)
    else:
        # Reset to light theme (default)
        st.markdown("""
            <style>
                .stApp {
                    background-color: #FFFFFF;
                    color: #262730;
                }
                .stTabs [data-baseweb="tab-list"] {
                    background-color: #F0F2F6;
                }
                .stTabs [data-baseweb="tab"] {
                    color: #262730;
                }
                div[data-testid="stSidebar"] {
                    background-color: #F0F2F6;
                }
                .stRadio label, .stCheckbox label {
                    color: #262730 !important;
                }
                div.stSelectbox label {
                    color: #262730 !important;
                }
                .streamlit-expanderHeader {
                    color: #262730 !important;
                }
                button[kind="secondary"] {
                    background-color: #F0F2F6;
                    color: #262730;
                }
            </style>
        """, unsafe_allow_html=True)

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
    
    # Sidebar filters
    st.sidebar.header("Filter Options")
    
    # Filter Type
    filter_type = st.sidebar.radio("Filter Type", ["Preset Periods", "Custom Date Range"])
    
    if filter_type == "Preset Periods":
        # Time period filter
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
     else:
        # Custom date range picker
        min_date = datetime.now() - timedelta(days=365*2)  # 2 years ago
        max_date = datetime.now()
        
        start_date = st.sidebar.date_input(
            "Start Date",
            min_date,
            min_value=min_date,
            max_value=max_date
        )
        
        end_date = st.sidebar.date_input(
            "End Date",
             max_date,
            min_value=start_date,
            max_value=max_date
        )
        
        # Convert to datetime for API
        start_date = datetime.combine(start_date, datetime.min.time())
        end_date = datetime.combine(end_date, datetime.max.time())
    
    # Format for YouTube API
    published_after = start_date.isoformat("T") + "Z"
    
    # Get videos based on time period
    videos = youtube_api.get_channel_videos(MR_BEAST_CHANNEL_ID, published_after=published_after)
    
     if not videos["items"]:
        if filter_type == "Preset Periods":
            st.warning(f"No videos found in the selected time period ({time_period})")
        else:
            st.warning(f"No videos found between {start_date.strftime('%b %d, %Y')} and {end_date.strftime('%b %d, %Y')}")
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
