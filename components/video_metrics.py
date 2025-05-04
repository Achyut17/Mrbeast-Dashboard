import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

def display_video_metrics(video_df):
    """
    Display individual video performance metrics
    
    Args:
        video_df (pandas.DataFrame): Video statistics dataframe
    """
    st.header("Video Performance Analysis")
    
    if video_df.empty:
        st.warning("No video data available for the selected time period.")
        return
    
    # Add additional derived metrics
    video_df["likes_per_view"] = (video_df["likes"] / video_df["views"] * 100).fillna(0)
    video_df["comments_per_view"] = (video_df["comments"] / video_df["views"] * 100).fillna(0)
    
    # Video filtering
    st.subheader("Filter Videos")
    col1, col2 = st.columns(2)
    
    with col1:
        min_views = st.number_input("Minimum Views", min_value=0, value=0, step=1000)
    
    with col2:
        sort_by = st.selectbox(
            "Sort By",
            ["Publication Date (Newest)", "Publication Date (Oldest)", "Views (High to Low)", 
             "Views (Low to High)", "Likes (High to Low)", "Engagement Rate (High to Low)"]
        )
    
    # Apply filters and sorting
    filtered_df = video_df[video_df["views"] >= min_views].copy()
    
    if sort_by == "Publication Date (Newest)":
        filtered_df = filtered_df.sort_values(by="published_at", ascending=False)
    elif sort_by == "Publication Date (Oldest)":
        filtered_df = filtered_df.sort_values(by="published_at", ascending=True)
    elif sort_by == "Views (High to Low)":
        filtered_df = filtered_df.sort_values(by="views", ascending=False)
    elif sort_by == "Views (Low to High)":
        filtered_df = filtered_df.sort_values(by="views", ascending=True)
    elif sort_by == "Likes (High to Low)":
        filtered_df = filtered_df.sort_values(by="likes", ascending=False)
    elif sort_by == "Engagement Rate (High to Low)":
        filtered_df = filtered_df.sort_values(by="likes_per_view", ascending=False)
    
    # Reset index for display
    filtered_df = filtered_df.reset_index(drop=True)
    
    # Display filtered videos
    st.subheader(f"Videos ({len(filtered_df)} results)")
    
    # Display videos in a card-like format
    for index, video in filtered_df.iterrows():
        with st.container():
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.image(video["thumbnail"], use_container_width=True)
            
            with col2:
                st.subheader(video["title"])
                st.write(f"Published on: {video['published_date']} • Duration: {video['duration']}")
                
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                with metric_col1:
                    st.metric("Views", f"{video['views']:,}")
                with metric_col2:
                    st.metric("Likes", f"{video['likes']:,}")
                with metric_col3:
                    st.metric("Comments", f"{video['comments']:,}")
                
                # Engagement metrics
                eng_col1, eng_col2 = st.columns(2)
                with eng_col1:
                    st.metric("Like Ratio", f"{video['likes_per_view']:.2f}%")
                with eng_col2:
                    st.metric("Comment Ratio", f"{video['comments_per_view']:.2f}%")
            
            st.divider()
    
    # Video comparison
    st.subheader("Video Comparison")
    
    # Setup for comparison
    comparison_metric = st.selectbox(
        "Compare videos by",
        ["Views", "Likes", "Comments", "Duration", "Like Ratio", "Comment Ratio"],
        index=0
    )
    
    # Map selection to dataframe column
    metric_map = {
        "Views": "views",
        "Likes": "likes",
        "Comments": "comments",
        "Duration": "duration_seconds",
        "Like Ratio": "likes_per_view",
        "Comment Ratio": "comments_per_view"
    }
    
    selected_metric = metric_map[comparison_metric]
    
    # Top 10 videos by selected metric
    top_videos = filtered_df.sort_values(by=selected_metric, ascending=False).head(10)
    
    # Create horizontal bar chart
    fig = px.bar(
        top_videos,
        y="title",
        x=selected_metric,
        orientation="h",
        title=f"Top 10 Videos by {comparison_metric}",
        text=selected_metric,
        hover_data=["published_date", "views", "likes", "comments"]
    )
    
    # Update layout
    fig.update_layout(
        yaxis_title="",
        xaxis_title=comparison_metric,
        height=600
    )
    
    # Format text based on metric
    if selected_metric in ["views", "likes", "comments"]:
        fig.update_traces(texttemplate='%{x:,.0f}', textposition='outside')
    elif selected_metric == "duration_seconds":
        fig.update_traces(texttemplate='%{x:.0f} sec', textposition='outside')
    else:
        fig.update_traces(texttemplate='%{x:.2f}%', textposition='outside')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Video performance over time
    st.subheader("Video Performance Over Time")
    
    time_metric = st.selectbox(
        "Select metric to track over time",
        ["Views", "Likes", "Comments", "Duration", "Like Ratio"],
        index=0
    )
    
    selected_time_metric = metric_map[time_metric]
    
    # Create time series chart
    time_df = filtered_df.copy()
    time_df = time_df.sort_values(by="published_at")
    
    fig = px.line(
        time_df,
        x="published_at",
        y=selected_time_metric,
        title=f"{time_metric} Trend Over Time",
        markers=True
    )
    
    # Add hover data
    fig.update_traces(
        hovertemplate='<b>%{text}</b><br>Date: %{x|%b %d, %Y}<br>' + f'{time_metric}: ' + '%{y:,.0f}',
        text=time_df["title"]
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title="Publication Date",
        yaxis_title=time_metric,
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
