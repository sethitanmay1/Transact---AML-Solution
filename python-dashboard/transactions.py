# transactions.py
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

def display_transactions_analysis(df):
    """
    Display a comprehensive transaction analysis dashboard. Users can:
      - Filter by a location field (province, city, or country) via dropdowns.
      - Filter by transaction type using a multiselect (from the 'source' column).
      - Then see various charts arranged into rows/columns.
    """
    st.header("📈 Transaction Analysis")
    
    # Prepare date/time columns
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    df['month'] = df['transaction_date'].dt.month_name()
    df['day_of_month'] = df['transaction_date'].dt.day
    df['weekday'] = df['transaction_date'].dt.day_name()
    df['is_weekend'] = df['transaction_date'].dt.weekday >= 5

    # -------------------------
    # LOCATION FILTERS (Single Field)
    st.subheader("Location Filter")
    # Choose the location field: Province, City, or Country
    location_field = st.selectbox(
        "Select Location Field",
        options=["trans_province", "trans_city", "trans_country"],
        index=0  # default: trans_province
    )
    # Determine default value based on the selected field
    default_value = None
    if location_field == "trans_province":
        default_value = "ON"
    elif location_field == "trans_city":
        default_value = "TORONTO"
    elif location_field == "trans_country":
        default_value = "Canada"
    unique_vals = sorted(df[location_field].dropna().unique())
    # Use the default if present; otherwise, the first available value.
    if default_value in unique_vals:
        default_index = unique_vals.index(default_value)
    else:
        default_index = 0
    selected_location = st.selectbox(
        f"Select {location_field}",
        options=unique_vals,
        index=default_index
    )
    filtered_df = df[df[location_field] == selected_location]

    # -------------------------
    # TRANSACTION TYPE FILTER (Multi-select)
    st.subheader("Transaction Type Filter")
    # 'source' holds the transaction type in all small caps.
    transaction_types = ["eft", "emt", "wire", "abm", "card", "cheque"]
    # Allow selecting multiple types, defaulting to all.
    selected_types = st.multiselect(
        "Select Transaction Types",
        options=transaction_types,
        default=transaction_types
    )
    if selected_types:
        filtered_df = filtered_df[filtered_df['source'].isin(selected_types)]
    
    # --------------------------------------
    # Now proceed with the same charts using filtered_df
    # --------------------------------------
    
    # Row 1: Monthly Trend & Outlier Transactions by Day of Month
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Monthly Trend of Outlier Transactions")
        monthly_outliers = (
            filtered_df[filtered_df['high_txn_outlier'] == 1]
            .groupby('month').size().reset_index(name='count')
        )
        month_order = ["January", "February", "March", "April", "May", "June",
                       "July", "August", "September", "October", "November", "December"]
        monthly_outliers['month'] = pd.Categorical(monthly_outliers['month'], categories=month_order, ordered=True)
        monthly_chart = alt.Chart(monthly_outliers).mark_line(point=True).encode(
            x=alt.X('month:N', sort=month_order, title="Month"),
            y=alt.Y('count:Q', title="Outlier Transactions"),
            tooltip=['month', 'count']
        ).properties(width=300, height=300)
        st.altair_chart(monthly_chart, use_container_width=True)
    with col2:
        st.markdown("### Outlier Transactions by Day of the Month")
        daily_outliers = (
            filtered_df[filtered_df['high_txn_outlier'] == 1]
            .groupby('day_of_month').size().reset_index(name='count')
        )
        daily_chart = alt.Chart(daily_outliers).mark_bar().encode(
            x=alt.X('day_of_month:O', title="Day of Month"),
            y=alt.Y('count:Q', title="Outlier Transactions"),
            tooltip=['day_of_month', 'count']
        ).properties(width=300, height=300)
        st.altair_chart(daily_chart, use_container_width=True)

    # Row 2: Outlier Transactions by Weekday & Hourly Trend
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Outlier Transactions by Day of the Week")
        weekday_outliers = (
            filtered_df[filtered_df['high_txn_outlier'] == 1]
            .groupby('weekday').size().reset_index(name='count')
        )
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekday_outliers['weekday'] = pd.Categorical(weekday_outliers['weekday'], categories=weekday_order, ordered=True)
        weekday_chart = alt.Chart(weekday_outliers).mark_bar().encode(
            x=alt.X('weekday:N', sort=weekday_order, title="Day of Week"),
            y=alt.Y('count:Q', title="Outlier Transactions"),
            tooltip=['weekday', 'count']
        ).properties(width=300, height=300)
        st.altair_chart(weekday_chart, use_container_width=True)
    with col2:
        st.markdown("### Hourly Trend of Outlier Transactions")
        hourly_outliers = (
            filtered_df[filtered_df['high_txn_outlier'] == 1]
            .groupby('txn_hour').size().reset_index(name='count')
        )
        hourly_chart = alt.Chart(hourly_outliers).mark_line(point=True).encode(
            x=alt.X('txn_hour:O', title="Hour of Day"),
            y=alt.Y('count:Q', title="Outlier Transactions"),
            tooltip=['txn_hour', 'count']
        ).properties(width=300, height=300)
        st.altair_chart(hourly_chart, use_container_width=True)

    # Row 3: Weekday vs. Weekend Outlier Trends (full width)
    st.markdown("### Weekday vs. Weekend Outlier Trends")
    weekend_outliers = (
        filtered_df[filtered_df['high_txn_outlier'] == 1]
        .groupby('is_weekend').size().reset_index(name='count')
    )
    weekend_outliers['is_weekend'] = weekend_outliers['is_weekend'].map({True: "Weekend", False: "Weekday"})
    weekend_chart = alt.Chart(weekend_outliers).mark_bar().encode(
        x=alt.X('is_weekend:N', title="Day Type"),
        y=alt.Y('count:Q', title="Outlier Transactions"),
        tooltip=['is_weekend', 'count']
    ).properties(width=600, height=300)
    st.altair_chart(weekend_chart, use_container_width=True)

    # Row 4: High vs. Low Transaction Outliers Summary (metrics)
    col1, col2 = st.columns(2)
    with col1:
        high_outliers_count = filtered_df['high_txn_outlier'].sum()
        st.metric("Total High Outlier Transactions", f"{int(high_outliers_count):,}")
    with col2:
        low_outliers_count = filtered_df['low_txn_outlier'].sum() if 'low_txn_outlier' in filtered_df.columns else 0
        st.metric("Total Low Outlier Transactions", f"{int(low_outliers_count):,}")

    # Row 6: Transaction Trends Over Time (full width)
    st.markdown("### Transaction Trends Over Time")
    time_trend = filtered_df.groupby('transaction_date').size().reset_index(name='count')
    time_chart = alt.Chart(time_trend).mark_line().encode(
        x=alt.X('transaction_date:T', title="Date"),
        y=alt.Y('count:Q', title="Total Transactions"),
        tooltip=['transaction_date', 'count']
    ).properties(width=600, height=300)
    st.altair_chart(time_chart, use_container_width=True)

    # Row 7: Transaction Activity by Hour of the Day (full width)
    st.markdown("### Transaction Activity by Hour of the Day")
    hour_activity = filtered_df.groupby('txn_hour').size().reset_index(name='count')
    hour_activity_chart = alt.Chart(hour_activity).mark_bar().encode(
        x=alt.X('txn_hour:O', title="Hour of Day"),
        y=alt.Y('count:Q', title="Transaction Count"),
        tooltip=['txn_hour', 'count']
    ).properties(width=600, height=300)
    st.altair_chart(hour_activity_chart, use_container_width=True)

    # Row 8: Transaction Amount Distribution (full width)
    st.markdown("### Transaction Amount Distribution")
    amount_chart = (
        alt.Chart(filtered_df)
        .mark_bar()
        .encode(
            x=alt.X('amount_cad:Q', bin=alt.Bin(maxbins=30), title="Transaction Amount (CAD)"),
            y=alt.Y('count()', title="Frequency"),
            tooltip=['count()']
        )
        .properties(width=600, height=300)
    )
    st.altair_chart(amount_chart, use_container_width=True)

    # Row 9: Flagged Transactions by Payment Method (full width)
    st.markdown("### Flagged Transactions by Payment Method")
    if 'debit_credit' in filtered_df.columns:
        payment_flag = filtered_df.groupby('debit_credit').agg(
            flagged_transactions=('high_txn_outlier', 'sum')
        ).reset_index()
        payment_chart = alt.Chart(payment_flag).mark_bar().encode(
            x=alt.X('debit_credit:N', title="Payment Method"),
            y=alt.Y('flagged_transactions:Q', title="Flagged Transactions"),
            tooltip=['debit_credit', 'flagged_transactions']
        ).properties(width=600, height=300)
        st.altair_chart(payment_chart, use_container_width=True)
