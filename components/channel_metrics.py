import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from utils.data_processing import format_duration

def display_channel_metrics(channel_stats, video_df):
    """
    Display channel performance metrics
    
    Args:
        channel_stats (dict): Channel statistics
        video_df (pandas.DataFrame): Video statistics dataframe
    """
    st.header("Channel Performance Overview")
    
    # Display top metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Videos", f"{channel_stats['video_count']:,}")
    with col2:
        st.metric("Total Views", f"{int(channel_stats['total_views']):,}")
    with col3:
        st.metric("Total Likes", f"{int(channel_stats['total_likes']):,}")
    with col4:
        st.metric("Total Comments", f"{int(channel_stats['total_comments']):,}")
    
    # Display average metrics
    st.subheader("Average Performance Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Avg. Views per Video", f"{int(channel_stats['avg_views']):,}")
    with col2:
        st.metric("Avg. Likes per Video", f"{int(channel_stats['avg_likes']):,}")
    with col3:
        st.metric("Avg. Comments per Video", f"{int(channel_stats['avg_comments']):,}")
    with col4:
        avg_duration = format_duration(channel_stats['avg_duration_seconds'])
        st.metric("Avg. Video Duration", avg_duration)
    
    # Engagement rate calculation
    if channel_stats['avg_views'] > 0:
        engagement_rate = (channel_stats['avg_likes'] + channel_stats['avg_comments']) / channel_stats['avg_views'] * 100
        st.metric("Engagement Rate", f"{engagement_rate:.2f}%")
    
    # Display trend charts if we have videos
    if not video_df.empty:
        st.subheader("Performance Trends")
        
        # Create a copy of the dataframe with date as index for time series analysis
        time_df = video_df.copy()
        time_df = time_df.set_index('published_at')
        time_df = time_df.sort_index()
        
        # Select metric for trend analysis
        trend_metric = st.selectbox(
            "Select Metric to Visualize",
            ["Views", "Likes", "Comments", "Duration"],
            index=0
        )
        
        if trend_metric == "Views":
            y_column = "views"
            title = "Views per Video Over Time"
            y_axis_title = "Views"
        elif trend_metric == "Likes":
            y_column = "likes"
            title = "Likes per Video Over Time"
            y_axis_title = "Likes"
        elif trend_metric == "Comments":
            y_column = "comments"
            title = "Comments per Video Over Time"
            y_axis_title = "Comments"
        else:  # Duration
            y_column = "duration_seconds"
            title = "Video Duration Over Time"
            y_axis_title = "Duration (seconds)"
        
        # Create trend chart
        fig = px.scatter(
            time_df, 
            x=time_df.index, 
            y=y_column, 
            size="views",
            hover_name="title",
            trendline="ols",
            title=title
        )
        fig.update_layout(
            xaxis_title="Publication Date",
            yaxis_title=y_axis_title,
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Distribution of views
        st.subheader("Video Performance Distribution")
        
        # Create histogram
        hist_metric = st.selectbox(
            "Select Metric for Distribution Analysis",
            ["Views", "Likes", "Comments"],
            index=0
        )
        
        if hist_metric == "Views":
            hist_column = "views"
            hist_title = "Distribution of Video Views"
            hist_x_title = "Views"
        elif hist_metric == "Likes":
            hist_column = "likes"
            hist_title = "Distribution of Video Likes"
            hist_x_title = "Likes"
        else:  # Comments
            hist_column = "comments"
            hist_title = "Distribution of Video Comments"
            hist_x_title = "Comments"
        
        fig = px.histogram(
            video_df,
            x=hist_column,
            title=hist_title,
            nbins=20,
            opacity=0.8
        )
        fig.update_layout(
            xaxis_title=hist_x_title,
            yaxis_title="Number of Videos",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Correlation analysis
        st.subheader("Metric Correlations")
        
        # Create correlation matrix
        corr_df = video_df[["views", "likes", "comments", "duration_seconds"]].copy()
        correlation = corr_df.corr()
        
        # Plot correlation heatmap
        fig = px.imshow(
            correlation,
            text_auto=True,
            color_continuous_scale='RdBu_r',
            title="Correlation Between Metrics"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Key insights
        st.subheader("Key Insights")
        
        # Most popular video
        most_popular = video_df.loc[video_df["views"].idxmax()]
        st.write(f"📈 Most popular video: **{most_popular['title']}** with **{most_popular['views']:,}** views")
        
        # Most engaging video (highest likes to views ratio)
        video_df["engagement_ratio"] = video_df["likes"] / video_df["views"]
        most_engaging = video_df.loc[video_df["engagement_ratio"].idxmax()]
        engagement_percent = most_engaging["engagement_ratio"] * 100
        st.write(f"👍 Most engaging video: **{most_engaging['title']}** with a **{engagement_percent:.2f}%** like ratio")
        
        # Optimal video length
        video_df["views_per_second"] = video_df["views"] / video_df["duration_seconds"]
        optimal_length = video_df.loc[video_df["views_per_second"].idxmax()]
        st.write(f"⏱️ Optimal video length: **{optimal_length['duration']}** (based on views per second of duration)")
