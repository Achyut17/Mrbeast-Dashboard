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
        
        # Add trend forecast
        show_forecast = st.checkbox("Show Trend Forecast", value=False)
        
        if show_forecast and len(time_df) >= 5:  # Need enough data for forecasting
            import statsmodels.api as sm
            from statsmodels.tsa.arima.model import ARIMA
            from pandas.tseries.offsets import DateOffset
            
            st.subheader(f"Forecast for Future {trend_metric}")
            
            # Resample data to get an evenly spaced time series (needed for ARIMA)
            forecast_method = st.radio("Forecast Method", ["Linear Regression", "ARIMA Model"])
            
            if forecast_method == "Linear Regression":
                # Simple linear regression for forecasting
                X = np.array(range(len(time_df))).reshape(-1, 1)
                y = time_df[y_column].values
                
                model = sm.OLS(y, sm.add_constant(X)).fit()
                
                # Create future dates for prediction
                future_periods = 5  # Predict next 5 videos
                future_X = np.array(range(len(time_df), len(time_df) + future_periods)).reshape(-1, 1)
                
                # Predict future values
                future_y = model.predict(sm.add_constant(future_X))
                
                # Create a dataframe for forecasted values
                last_date = time_df.index[-1]
                future_dates = [last_date + DateOffset(days=30*i) for i in range(1, future_periods+1)]
                
                forecast_df = pd.DataFrame({
                    'date': future_dates,
                    y_column: future_y
                })
                
                # Plot original data with forecast
                combined_df = pd.DataFrame({
                    'date': time_df.index,
                    y_column: time_df[y_column],
                    'type': 'Historical'
                })
                
                forecast_plot_df = pd.DataFrame({
                    'date': future_dates,
                    y_column: future_y,
                    'type': 'Forecast'
                })
                
                plot_df = pd.concat([combined_df, forecast_plot_df])
                
                fig = px.scatter(
                    plot_df,
                    x='date',
                    y=y_column,
                    color='type',
                    title=f"{trend_metric} Forecast (Next {future_periods} Videos)",
                    color_discrete_map={
                        'Historical': 'blue',
                        'Forecast': 'red'
                    }
                )
                
                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title=y_axis_title,
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show forecast statistics
                st.write("Forecast Statistics:")
                for i, (date, value) in enumerate(zip(future_dates, future_y)):
                    st.write(f"Video {i+1} (est. {date.strftime('%b %Y')}): {int(value):,} {y_axis_title.lower()}")
                
            else:  # ARIMA Model
                try:
                    # Prepare time series data
                    ts_data = time_df[y_column].resample('M').mean().fillna(method='ffill')
                    
                    # ARIMA model (p,d,q) = (1,1,1) for simplicity
                    model = ARIMA(ts_data, order=(1,1,1))
                    model_fit = model.fit()
                    
                    # Forecast future periods
                    future_periods = 5
                    forecast = model_fit.forecast(steps=future_periods)
                    
                    # Create future dates
                    last_date = ts_data.index[-1]
                    future_dates = [last_date + DateOffset(months=i) for i in range(1, future_periods+1)]
                    
                    # Create forecast dataframe
                    forecast_df = pd.DataFrame({
                        'date': future_dates,
                        y_column: forecast,
                        'type': 'Forecast'
                    })
                    
                    # Plot historical and forecast data
                    historical_df = pd.DataFrame({
                        'date': ts_data.index,
                        y_column: ts_data.values,
                        'type': 'Historical'
                    })
                    
                    plot_df = pd.concat([historical_df, forecast_df])
                    
                    fig = px.line(
                        plot_df,
                        x='date',
                        y=y_column,
                        color='type',
                        title=f"{trend_metric} Forecast (Next {future_periods} Months)",
                        color_discrete_map={
                            'Historical': 'blue',
                            'Forecast': 'red'
                        }
                    )
                    
                    fig.update_layout(
                        xaxis_title="Date",
                        yaxis_title=y_axis_title,
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show forecast statistics
                    st.write("Monthly Forecast Statistics:")
                    for i, (date, value) in enumerate(zip(future_dates, forecast)):
                        st.write(f"Month {i+1} ({date.strftime('%b %Y')}): {int(value):,} {y_axis_title.lower()}")
                        
                except Exception as e:
                    st.error(f"Could not generate ARIMA forecast: {str(e)}")
                    st.info("Try using Linear Regression instead, or select a different time period with more data points.")
        
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
