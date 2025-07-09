# customer.py
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

def display_customer_analysis(df):
    """
    Main function to display the customer risk analysis dashboard.
    """
    st.header("💰 Customer Risk Analysis")
    df = calculate_features(df)
    
    # Top-level metrics and core visualizations
    display_top_metrics(df)
    display_transaction_patterns(df)
    display_risky_customers_table(df)
    display_customer_anomaly_heatmap(df)
    
    # Additional Visualizations (existing)
    display_high_odd_hour_customers(df)
    display_customer_clusters_spending_txn(df)
    # display_high_spending_low_legitimacy(df)
    display_txn_amount_distribution(df)
    display_customer_clusters_spending_behavior(df)
    display_high_risk_frequent_txn(df)
    display_customers_same_amount(df)
    display_common_txn_amount_high_risk(df)
    display_customers_same_merchant(df)
    
    # --------------------------------------------
    # Additional Analysis (new functions)
    st.markdown("## Additional Analysis")
    colA, colB = st.columns(2)
    with colA:
        display_customers_most_outliers(df)
    with colB:
        display_customers_most_large_cash(df)
        
    colC, colD = st.columns(2)
    with colC:
        display_high_frequency_txn_customers(df)
    with colD:
        display_flagged_customers_by_industry(df)
    
    # Full-width visualizations for more complex charts
    display_customers_outlier_txn_by_hour(df)
    display_recurring_txn_diff_distribution(df)


def calculate_features(df):
    """
    Function to calculate new features for the analysis.
    """
    if 'txn_hour' in df.columns:
        df['midnight_txn_count'] = df['txn_hour'].between(0, 5).astype(int)
    return df


def display_top_metrics(df):
    """
    Function to display top metrics as cards.
    """
    customer_stats = df.groupby('customer_id').agg(
        total_transactions=('transaction_id', 'count'),
        outlier_count=('high_txn_outlier', 'sum'),
        cash_tnx=('large_cash_txn', 'sum'),
        avg_spending=('amount_cad', 'mean'),
        midnight_txns=('midnight_txn_count', 'sum')
    ).reset_index()

    st.subheader("📊 Top Risk Metrics")
    
    # Define flagged customers as those with any high risk metric above a threshold.
    flagged = customer_stats[(customer_stats['outlier_count'] > 5) |
                             (customer_stats['cash_tnx'] > 3) |
                             (customer_stats['midnight_txns'] > 10)]
    flagged_count = flagged.shape[0]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        # Metric: Most outliers
        top_outlier = customer_stats.nlargest(1, 'outlier_count')
        st.metric(
            "Most Outliers",
            f"{top_outlier['customer_id'].values[0]}",
            f"{int(top_outlier['outlier_count'].values[0]):,} transactions"
        )
    with col2:
        # Metric: Midnight transactions
        top_midnight = customer_stats.nlargest(1, 'midnight_txns')
        st.metric(
            "Midnight Transactions",
            f"{int(top_midnight['midnight_txns'].values[0]):,}",
            f"{top_midnight['customer_id'].values[0]}"
        )
    with col3:
        st.metric(
            "Flagged Customers",
            f"{flagged_count}",
            f"{(flagged_count / customer_stats.shape[0] * 100):.1f}% flagged"
        )
    
    # Risk distribution donut charts
    st.subheader("📈 Risk Distributions")
    col4, col5 = st.columns(2)
    with col4:
        st.altair_chart(
            make_donut_chart(
                (customer_stats['outlier_count'] > 5).mean() * 100,
                "High Outliers",
                "red"
            ),
            use_container_width=True
        )
    with col5:
        st.altair_chart(
            make_donut_chart(
                (customer_stats['cash_tnx'] > 3).mean() * 100,
                "Frequent Cash Txns",
                "orange"
            ),
            use_container_width=True
        )


def display_transaction_patterns(df):
    """
    Function to display transaction patterns as a heatmap.
    """
    st.subheader("📅 Transaction Patterns")
    heatmap_data = df.groupby(['txn_hour', 'trans_province']).size().reset_index(name='counts')
    heatmap = alt.Chart(heatmap_data).mark_rect().encode(
        x='txn_hour:O',
        y='trans_province:N',
        color='counts:Q',
        tooltip=['txn_hour', 'trans_province', 'counts']
    ).properties(width=700, height=300)
    
    st.altair_chart(heatmap, use_container_width=True)


def display_risky_customers_table(df):
    """
    Function to display a table of top risky customers.
    """
    customer_stats = df.groupby('customer_id').agg(
        total_transactions=('transaction_id', 'count'),
        outlier_count=('high_txn_outlier', 'sum'),
        cash_tnx=('large_cash_txn', 'sum'),
        avg_spending=('amount_cad', 'mean'),
        midnight_txns=('midnight_txn_count', 'sum')
    ).reset_index()

    st.subheader("📋 Top 10 Risky Customers")
    st.dataframe(
        customer_stats.sort_values('outlier_count', ascending=False)
        .head(10)
        [['customer_id', 'outlier_count', 'cash_tnx', 'avg_spending', 'midnight_txns']]
        .style.background_gradient(cmap='Reds', subset=['outlier_count']),
        height=400
    )


def make_donut_chart(value, title, color_scheme):
    """
    Function to create a donut chart with percentage text in the center.
    """
    # Define color ranges based on the color scheme.
    if color_scheme == 'red':
        colors = ['#E74C3C', '#781F16']
    elif color_scheme == 'orange':
        colors = ['#F39C12', '#875A12']
    else:
        colors = ['#29b5e8', '#155F7A']
    
    # Create source data for the donut segments.
    source = pd.DataFrame({
        "category": [title, "Other"],
        "value": [value, 100 - value]
    })
    
    # Create the donut chart.
    donut = alt.Chart(source).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field="value", type="quantitative"),
        color=alt.Color(field="category", type="nominal",
                        scale=alt.Scale(domain=[title, "Other"], range=colors),
                        legend=None)
    ).properties(width=150, height=150)
    
    # Overlay text in the center showing the percentage.
    text = alt.Chart(pd.DataFrame({
        'x': [75],
        'y': [75],
        'text': [f"{value:.1f}%"]
    })).mark_text(
        align='center',
        baseline='middle',
        fontSize=14,
        fontWeight='bold',
        color='white'
    ).encode(
        x=alt.value(75),
        y=alt.value(75),
        text='text:N'
    ).properties(width=150, height=150)
    
    return alt.layer(donut, text)


def display_customer_anomaly_heatmap(df):
    """
    Function to display a customer-wise heatmap of anomaly factors.
    This heatmap shows, for the top 10 customers (by total anomalies), 
    the counts of different anomaly types.
    """
    st.markdown("### Customer-wise Heatmap of Anomaly Factors (Top 10 Customers)")
    
    anomaly_df = df.groupby('customer_id').agg(
        outlier_count=('high_txn_outlier', 'sum'),
        cash_tnx=('large_cash_txn', 'sum'),
        midnight_txns=('midnight_txn_count', 'sum')
    ).reset_index()
    
    # Calculate total anomaly factors
    anomaly_df['total_anomalies'] = anomaly_df['outlier_count'] + anomaly_df['cash_tnx'] + anomaly_df['midnight_txns']
    top10 = anomaly_df.nlargest(10, 'total_anomalies')
    
    # Melt the data to long format.
    anomaly_long = top10.melt(id_vars='customer_id', 
                              var_name='anomaly_factor', 
                              value_name='count')
    
    # Visualization: Heatmap
    heatmap = alt.Chart(anomaly_long).mark_rect().encode(
        x=alt.X('customer_id:N', title='Customer'),
        y=alt.Y('anomaly_factor:N', title='Anomaly Factor'),
        color=alt.Color('count:Q', title='Count', scale=alt.Scale(scheme='blues')),
        tooltip=['customer_id', 'anomaly_factor', 'count']
    ).properties(width=600, height=300)
    
    st.altair_chart(heatmap, use_container_width=True)


def display_high_odd_hour_customers(df):
    """
    Bar graph: Top 10 customers with the highest odd-hour transactions.
    """
    st.markdown("### Top 10 High Odd-Hour Transaction Customers")
    odd_df = df.groupby('customer_id').agg(
        total_odd_hour=('odd_hour_txn', 'sum')
    ).reset_index()
    top10 = odd_df.nlargest(10, 'total_odd_hour')
    chart = alt.Chart(top10).mark_bar().encode(
        x=alt.X('total_odd_hour:Q', title='Odd-Hour Transactions'),
        y=alt.Y('customer_id:N', title='Customer', sort='-x'),
        tooltip=['customer_id', 'total_odd_hour']
    ).properties(width=600, height=300)
    st.altair_chart(chart, use_container_width=True)


def display_customer_clusters_spending_txn(df):
    """
    Scatter plot: Customer clusters based on total spending and transaction count.
    """
    st.markdown("### Customer Clusters Based on Spending & Transaction Count")
    clusters = df.groupby('customer_id').agg(
        total_spent=('amount_cad', 'sum'),
        txn_count=('transaction_id', 'count')
    ).reset_index()
    chart = alt.Chart(clusters).mark_circle(size=100).encode(
        x=alt.X('txn_count:Q', title='Transaction Count'),
        y=alt.Y('total_spent:Q', title='Total Spent (CAD)'),
        tooltip=['customer_id', 'txn_count', 'total_spent']
    ).properties(width=600, height=400)
    st.altair_chart(chart, use_container_width=True)


def display_high_spending_low_legitimacy(df):
    """
    Scatter plot: High-spending customers with low business legitimacy.
    Here, we use employee_count as a proxy for business legitimacy.
    """
    st.markdown("### High-Spending Customers with Low Business Legitimacy")
    clusters = df.groupby('customer_id').agg(
        total_spent=('amount_cad', 'sum'),
        employee_count=('employee_count', 'first')
    ).reset_index()
    median_spent = clusters['total_spent'].median()
    median_emp = clusters['employee_count'].median()
    filtered = clusters[(clusters['total_spent'] > median_spent) & (clusters['employee_count'] < median_emp)]
    chart = alt.Chart(filtered).mark_circle(size=100, color='red').encode(
        x=alt.X('employee_count:Q', title='Employee Count'),
        y=alt.Y('total_spent:Q', title='Total Spent (CAD)'),
        tooltip=['customer_id', 'employee_count', 'total_spent']
    ).properties(width=600, height=400)
    st.altair_chart(chart, use_container_width=True)


def display_txn_amount_distribution(df):
    """
    Boxplot: Transaction amount distribution for top 10 customers by transaction count.
    """
    st.markdown("### Transaction Amount Distribution per Customer")
    txn_counts = df.groupby('customer_id').agg(
        txn_count=('transaction_id', 'count')
    ).reset_index()
    top10_customers = txn_counts.nlargest(10, 'txn_count')['customer_id']
    filtered = df[df['customer_id'].isin(top10_customers)]
    chart = alt.Chart(filtered).mark_boxplot().encode(
        x=alt.X('customer_id:N', title='Customer'),
        y=alt.Y('amount_cad:Q', title='Transaction Amount (CAD)'),
        tooltip=['customer_id', 'amount_cad']
    ).properties(width=600, height=400)
    st.altair_chart(chart, use_container_width=True)


def display_customer_clusters_spending_behavior(df):
    """
    Scatter plot: Customer clusters based on spending behavior.
    Using average spending and standard deviation of monthly transaction amounts.
    """
    st.markdown("### Customer Clusters Based on Spending Behavior")
    clusters = df.groupby('customer_id').agg(
        avg_spent=('avg_spent', 'mean'),
        std_txn_amount_per_month=('std_txn_amount_per_month', 'mean')
    ).reset_index()
    chart = alt.Chart(clusters).mark_circle(size=100).encode(
        x=alt.X('avg_spent:Q', title='Average Spending (CAD)'),
        y=alt.Y('std_txn_amount_per_month:Q', title='STD of Transaction Amount per Month'),
        tooltip=['customer_id', 'avg_spent', 'std_txn_amount_per_month']
    ).properties(width=600, height=400)
    st.altair_chart(chart, use_container_width=True)


def display_high_risk_frequent_txn(df):
    """
    Bar chart: High-risk customers (by outlier count) with their total transaction counts.
    """
    st.markdown("### High-Risk Customers with Frequent Transactions")
    customer_stats = df.groupby('customer_id').agg(
        total_transactions=('transaction_id', 'count'),
        outlier_count=('high_txn_outlier', 'sum')
    ).reset_index()
    top10 = customer_stats.nlargest(10, 'outlier_count')
    chart = alt.Chart(top10).mark_bar().encode(
        x=alt.X('outlier_count:Q', title='High Txn Outliers'),
        y=alt.Y('customer_id:N', title='Customer', sort='-x'),
        tooltip=['customer_id', 'total_transactions', 'outlier_count']
    ).properties(width=600, height=300)
    st.altair_chart(chart, use_container_width=True)


def display_customers_same_amount(df):
    """
    Bar chart: Customers frequently transacting the same amount.
    Calculated as the highest frequency of any amount divided by total transactions.
    """
    st.markdown("### Customers Frequently Transacting the Same Amount")
    freq = df.groupby(['customer_id', 'amount_cad']).size().reset_index(name='count')
    max_freq = freq.groupby('customer_id')['count'].max().reset_index(name='max_count')
    txn_count = df.groupby('customer_id').agg(total_txn=('transaction_id', 'count')).reset_index()
    merged = pd.merge(max_freq, txn_count, on='customer_id')
    merged['repeat_pct'] = merged['max_count'] / merged['total_txn'] * 100
    top10 = merged.nlargest(10, 'repeat_pct')
    chart = alt.Chart(top10).mark_bar().encode(
        x=alt.X('repeat_pct:Q', title='Repeated Transaction (%)'),
        y=alt.Y('customer_id:N', title='Customer', sort='-x'),
        tooltip=['customer_id', 'max_count', 'total_txn', 'repeat_pct']
    ).properties(width=600, height=300)
    st.altair_chart(chart, use_container_width=True)


def display_common_txn_amount_high_risk(df):
    """
    Bar chart: Most common transaction amounts among high-risk customers.
    Filters transactions where high_txn_outlier is flagged.
    """
    st.markdown("### Most Common Transaction Amounts Among High-Risk Customers")
    high_risk_df = df[df['high_txn_outlier'] == 1]
    if high_risk_df.empty:
        st.write("No high-risk transactions available.")
        return
    common_amounts = high_risk_df.groupby('amount_cad').size().reset_index(name='count')
    top10 = common_amounts.nlargest(10, 'count')
    chart = alt.Chart(top10).mark_bar().encode(
        x=alt.X('amount_cad:Q', title='Transaction Amount (CAD)'),
        y=alt.Y('count:Q', title='Frequency'),
        tooltip=['amount_cad', 'count']
    ).properties(width=600, height=300)
    st.altair_chart(chart, use_container_width=True)


def display_customers_same_merchant(df):
    """
    Bar chart: Customers repeatedly transacting with the same merchants.
    Calculated as the highest frequency of a merchant per customer divided by total transactions.
    """
    st.markdown("### Customers Repeatedly Transacting with the Same Merchants")
    freq = df.groupby(['customer_id', 'merchant_category']).size().reset_index(name='count')
    max_freq = freq.groupby('customer_id')['count'].max().reset_index(name='max_count')
    txn_count = df.groupby('customer_id').agg(total_txn=('transaction_id', 'count')).reset_index()
    merged = pd.merge(max_freq, txn_count, on='customer_id')
    merged['repeat_pct'] = merged['max_count'] / merged['total_txn'] * 100
    top10 = merged.nlargest(10, 'repeat_pct')
    chart = alt.Chart(top10).mark_bar().encode(
        x=alt.X('repeat_pct:Q', title='Same Merchant Transactions (%)'),
        y=alt.Y('customer_id:N', title='Customer', sort='-x'),
        tooltip=['customer_id', 'max_count', 'total_txn', 'repeat_pct']
    ).properties(width=600, height=300)
    st.altair_chart(chart, use_container_width=True)


# -------------------------
# New Functions for Additional Analysis

def display_customers_most_outliers(df):
    """
    Horizontal bar chart: Top 10 customers with the most outlier transactions.
    """
    st.markdown("### Customers with Most Outlier Transactions")
    cust_outliers = df.groupby('customer_id')['high_txn_outlier'].sum().reset_index()
    top10 = cust_outliers.nlargest(10, 'high_txn_outlier')
    chart = alt.Chart(top10).mark_bar().encode(
        y=alt.Y('customer_id:N', title='Customer', sort='-x'),
        x=alt.X('high_txn_outlier:Q', title='Outlier Transactions'),
        tooltip=['customer_id', 'high_txn_outlier']
    ).properties(width=300, height=300)
    st.altair_chart(chart, use_container_width=True)


def display_customers_most_large_cash(df):
    """
    Horizontal bar chart: Top 10 customers with the most large cash transactions.
    """
    st.markdown("### Customers with Most Large Cash Transactions")
    cust_cash = df.groupby('customer_id')['large_cash_txn'].sum().reset_index()
    top10 = cust_cash.nlargest(10, 'large_cash_txn')
    chart = alt.Chart(top10).mark_bar().encode(
        y=alt.Y('customer_id:N', title='Customer', sort='-x'),
        x=alt.X('large_cash_txn:Q', title='Large Cash Transactions'),
        tooltip=['customer_id', 'large_cash_txn']
    ).properties(width=300, height=300)
    st.altair_chart(chart, use_container_width=True)


def display_high_frequency_txn_customers(df):
    """
    Horizontal bar chart: Top 10 customers by transaction count.
    """
    st.markdown("### High Frequency Transaction Customers")
    freq = df.groupby('customer_id')['transaction_id'].count().reset_index().rename(columns={'transaction_id': 'txn_count'})
    top10 = freq.nlargest(10, 'txn_count')
    chart = alt.Chart(top10).mark_bar().encode(
        y=alt.Y('customer_id:N', title='Customer', sort='-x'),
        x=alt.X('txn_count:Q', title='Transaction Count'),
        tooltip=['customer_id', 'txn_count']
    ).properties(width=300, height=300)
    st.altair_chart(chart, use_container_width=True)


def display_customers_outlier_txn_by_hour(df):
    """
    Grouped bar chart: For the top 10 customers (by outlier count), show outlier transactions by hour.
    """
    st.markdown("### Top 10 Customers' Outlier Transactions by Hour")
    cust_outliers = df.groupby('customer_id')['high_txn_outlier'].sum().reset_index()
    top10_customers = cust_outliers.nlargest(10, 'high_txn_outlier')['customer_id']
    data = df[df['customer_id'].isin(top10_customers)]
    grouped = data.groupby(['customer_id', 'txn_hour'])['high_txn_outlier'].sum().reset_index()
    chart = alt.Chart(grouped).mark_bar().encode(
        x=alt.X('txn_hour:O', title='Transaction Hour'),
        y=alt.Y('high_txn_outlier:Q', title='Outlier Transactions'),
        color=alt.Color('customer_id:N', legend=alt.Legend(title="Customer")),
        tooltip=['customer_id', 'txn_hour', 'high_txn_outlier']
    ).properties(width=600, height=300)
    st.altair_chart(chart, use_container_width=True)


def display_flagged_customers_by_industry(df):
    """
    Horizontal bar chart: Group flagged high-risk customers by industry.
    """
    st.markdown("### Flagged High-Risk Customers by Industry")
    flagged = df.groupby('customer_id').agg(
         outlier_count=('high_txn_outlier', 'sum'),
         cash_tnx=('large_cash_txn', 'sum'),
         midnight_txns=('midnight_txn_count', 'sum'),
         industry=('industry', 'first')
    ).reset_index()
    flagged = flagged[(flagged['outlier_count'] > 5) | (flagged['cash_tnx'] > 3) | (flagged['midnight_txns'] > 10)]
    industry_group = flagged.groupby('industry').size().reset_index(name='flagged_count')
    chart = alt.Chart(industry_group).mark_bar().encode(
         y=alt.Y('industry:N', title='Industry', sort='-x'),
         x=alt.X('flagged_count:Q', title='Flagged Customers'),
         tooltip=['industry', 'flagged_count']
    ).properties(width=300, height=300)
    st.altair_chart(chart, use_container_width=True)


def display_recurring_txn_diff_distribution(df):
    """
    Histogram: Distribution of recurring transaction differences among high-risk customers.
    Uses the 'txn_gap' column if available, otherwise 'avg_gap_between_txns_month'.
    """
    st.markdown("### Distribution of Recurring Transaction Differences Among High-Risk Customers")
    column = None
    if 'txn_gap' in df.columns:
        column = 'txn_gap'
    elif 'avg_gap_between_txns_month' in df.columns:
        column = 'avg_gap_between_txns_month'
    if column:
        high_risk = df[df['high_txn_outlier'] == 1]
        chart = alt.Chart(high_risk).mark_bar().encode(
            x=alt.X(f'{column}:Q', bin=alt.Bin(maxbins=30), title=column),
            y=alt.Y('count()', title='Frequency'),
            tooltip=[f'{column}', 'count()']
        ).properties(width=600, height=300)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.write("No recurring transaction difference data available.")
