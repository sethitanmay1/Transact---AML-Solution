import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

def display_enterprise_analysis(df):
    """
    Display enterprise-level analyses and visualizations. 
    Covers high-risk industries, fraud patterns, business legitimacy, and more.
    Now arranged in two-column rows for side-by-side charts.
    """
    st.header("🏢 Enterprise Analysis")
    
    # Ensure transaction_date is datetime, create day-of-week if needed
    if 'transaction_date' in df.columns:
        df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
        df['weekday'] = df['transaction_date'].dt.day_name()
        df['txn_hour'] = df['transaction_date'].dt.hour

    # Pre-calculate some aggregates used across multiple charts
    outlier_by_industry = df.groupby('industry')['high_txn_outlier'].sum().reset_index(name='Outliers')
    cust_risk = df.groupby('customer_id')['high_txn_outlier'].sum().reset_index(name='outlier_sum')
    high_risk_cust = cust_risk[cust_risk['outlier_sum'] > 5]['customer_id']
    df_high_risk = df[df['customer_id'].isin(high_risk_cust)]

    # -----------------------
    # Row 1: (1) Industries with Most Outliers | (2) Industries with Most Large Cash Transactions
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Industries with Most Outliers")
        chart1 = alt.Chart(outlier_by_industry).mark_bar().encode(
            x=alt.X('Outliers:Q', title='Outlier Transactions'),
            y=alt.Y('industry:N', sort='-x', title='Industry'),
            tooltip=['industry', 'Outliers']
        ).properties(width=600, height=300)
        st.altair_chart(chart1, use_container_width=True)
    with col2:
        st.markdown("### Top 10 Industries with High-Risk Customers")
        dist_industries = df_high_risk.groupby('industry')['customer_id'].nunique().reset_index(name='HighRiskCustCount')
        top10_hr = dist_industries.nlargest(10, 'HighRiskCustCount')
        chart6 = alt.Chart(top10_hr).mark_bar().encode(
            x=alt.X('HighRiskCustCount:Q', title='High-Risk Customers'),
            y=alt.Y('industry:N', sort='-x', title='Industry'),
            tooltip=['industry', 'HighRiskCustCount']
        ).properties(width=600, height=300)
        st.altair_chart(chart6, use_container_width=True)

    # -----------------------
    # Row 2: (3) Top 10 Industries w/ Most Outlier Tx | (4) Industry-wise Outlier by Hour
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Top 10 Industries with Most Outlier Transactions")
        top10_outliers = outlier_by_industry.nlargest(10, 'Outliers')
        chart3 = alt.Chart(top10_outliers).mark_bar().encode(
            x=alt.X('Outliers:Q', title='Outlier Transactions'),
            y=alt.Y('industry:N', sort='-x', title='Industry'),
            tooltip=['industry', 'Outliers']
        ).properties(width=600, height=300)
        st.altair_chart(chart3, use_container_width=True)
    with col2:
        st.markdown("### Industry-wise Outlier by Hour")
        if 'txn_hour' in df.columns:
            hour_outliers = df[df['high_txn_outlier'] == 1].groupby(['industry','txn_hour']).size().reset_index(name='count')
            heatmap = alt.Chart(hour_outliers).mark_rect().encode(
                x=alt.X('txn_hour:O', title='Hour'),
                y=alt.Y('industry:N', title='Industry'),
                color=alt.Color('count:Q', scale=alt.Scale(scheme='blues'), title='Outlier Count'),
                tooltip=['industry', 'txn_hour', 'count']
            ).properties(width=600, height=300)
            st.altair_chart(heatmap, use_container_width=True)
        else:
            st.write("No txn_hour column available for hour-based analysis.")

    # -----------------------
    # Row 3: (5) Dist. of Industries Among High-Risk Cust. | (6) Top 10 Industries w/ High-Risk Cust.
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Distribution of Industries Among High-Risk Customers")
        dist_industries = df_high_risk.groupby('industry')['customer_id'].nunique().reset_index(name='HighRiskCustCount')
        chart5 = alt.Chart(dist_industries).mark_bar().encode(
            x=alt.X('HighRiskCustCount:Q', title='High-Risk Customers'),
            y=alt.Y('industry:N', sort='-x', title='Industry'),
            tooltip=['industry', 'HighRiskCustCount']
        ).properties(width=600, height=300)
        st.altair_chart(chart5, use_container_width=True)
    with col2:
        st.markdown("### Top Fraud Prone Industries by High-Risk Customers")
        # Reuse chart6 for demonstration
        st.altair_chart(chart6, use_container_width=True)


    # -----------------------
    # Row 4: (7) Top Fraud Prone Ind. by High Risk Cust. | (8) Fraud Patterns: Wholesale vs. Retail
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Fraud Patterns by Business Category (Wholesale vs. Retail)")
        if 'merchant_category' in df.columns:
            cat_agg = df.groupby('merchant_category')['high_txn_outlier'].sum().reset_index(name='Outliers')
            chart8 = alt.Chart(cat_agg).mark_bar().encode(
                x=alt.X('Outliers:Q', title='Outlier Transactions'),
                y=alt.Y('merchant_category:N', sort='-x', title='Business Category'),
                tooltip=['merchant_category', 'Outliers']
            ).properties(width=600, height=300)
            st.altair_chart(chart8, use_container_width=True)
        else:
            st.write("No 'merchant_category' column available for Wholesale vs. Retail analysis.")
    with col2:
        # fix this - why are some values zero?
        st.markdown("### Industries with Most Large Cash Transactions")
        cash_by_industry = df.groupby('industry')['large_cash_txn'].sum().reset_index(name='LargeCash')
        chart2 = alt.Chart(cash_by_industry).mark_bar().encode(
            x=alt.X('LargeCash:Q', title='Large Cash Transactions'),
            y=alt.Y('industry:N', sort='-x', title='Industry'),
            tooltip=['industry', 'LargeCash']
        ).properties(width=600, height=300)
        st.altair_chart(chart2, use_container_width=True)

    # -----------------------
    # Row 5: (9) Recurring Tx by Day of Week | (10) High-Risk Cust. w/ Suspicious Business Legitimacy
    # col1, col2 = st.columns(2)
    # with col1:
    st.markdown("### Recurring Transactions by Day of the Week")
    if 'weekday' in df.columns:
        # Example approach for 'recurring'
        recurring = df.groupby(['weekday', 'customer_id']).size().reset_index(name='count')
        recurring_agg = recurring.groupby('weekday')['count'].sum().reset_index()
        weekday_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        recurring_agg['weekday'] = pd.Categorical(recurring_agg['weekday'], categories=weekday_order, ordered=True)
        chart9 = alt.Chart(recurring_agg).mark_bar().encode(
            x=alt.X('weekday:N', sort=weekday_order, title='Day of Week'),
            y=alt.Y('count:Q', title='Recurring Transaction Count'),
            tooltip=['weekday', 'count']
        ).properties(width=600, height=300)
        st.altair_chart(chart9, use_container_width=True)
    else:
        st.write("No 'weekday' data to analyze recurring transactions by day of the week.")
    # with col2:
    #     st.markdown("### High-Risk Customers with Suspicious Business Legitimacy")
    #     if 'employee_count' in df.columns:
    #         cust_legit = df.groupby('customer_id').agg(
    #             total_outliers=('high_txn_outlier','sum'),
    #             avg_spent=('amount_cad','mean'),
    #             employee_count=('employee_count','first')
    #         ).reset_index()
    #         median_spent = cust_legit['avg_spent'].median()
    #         median_emp = cust_legit['employee_count'].median()
    #         suspicious = cust_legit[(cust_legit['total_outliers']>5) & 
    #                                 (cust_legit['avg_spent']>median_spent) & 
    #                                 (cust_legit['employee_count']<median_emp)]
    #         chart10 = alt.Chart(suspicious).mark_circle(size=100, color='red').encode(
    #             x=alt.X('employee_count:Q', title='Employee Count'),
    #             y=alt.Y('avg_spent:Q', title='Avg Spent (CAD)'),
    #             tooltip=['customer_id', 'total_outliers','avg_spent','employee_count']
    #         ).properties(width=600, height=300)
    #         st.altair_chart(chart10, use_container_width=True)
    #         st.write(f"Found {len(suspicious)} suspicious customers.")
    #     else:
    #         st.write("No 'employee_count' column to evaluate business legitimacy.")

    # -----------------------
    # Row 6: (11) Fraud Patterns by Bus. Category (Detailed) | (12) Fraud-Prone Business Categories
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Fraud Patterns by Business Category (Detailed)")
        if 'merchant_category' in df.columns:
            bc_agg = df.groupby('merchant_category').agg(
                outliers=('high_txn_outlier','sum'),
                large_cash=('large_cash_txn','sum'),
                total_txn=('transaction_id','count')
            ).reset_index()
            chart11 = alt.Chart(bc_agg).mark_bar().encode(
                x=alt.X('outliers:Q', title='Outliers'),
                y=alt.Y('merchant_category:N', sort='-x', title='Business Category'),
                color=alt.Color('large_cash:Q', title='Large Cash Txns', scale=alt.Scale(scheme='reds')),
                tooltip=['merchant_category','outliers','large_cash','total_txn']
            ).properties(width=600, height=300)
            st.altair_chart(chart11, use_container_width=True)
        else:
            st.write("No 'merchant_category' column available.")
    with col2:
        st.markdown("### Fraud-Prone Business Categories")
        if 'merchant_category' in df.columns:
            # Reuse bc_agg from above
            bc_agg['fraud_score'] = bc_agg['outliers'] / bc_agg['total_txn'].replace(0,1)
            chart12 = alt.Chart(bc_agg.nlargest(10,'fraud_score')).mark_bar().encode(
                x=alt.X('fraud_score:Q', title='Fraud Score'),
                y=alt.Y('merchant_category:N', sort='-x', title='Business Category'),
                tooltip=['merchant_category','fraud_score','outliers','total_txn']
            ).properties(width=600, height=300)
            st.altair_chart(chart12, use_container_width=True)

    # -----------------------
    # Row 7: (13) High Risk Tx by Industry | (14) Industries w/ Tx Exceeding Sales
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### High Risk Customer Transactions by Industry")
        hr_transactions = df[df['high_txn_outlier'] == 1]
        hr_industry_agg = hr_transactions.groupby('industry')['transaction_id'].count().reset_index(name='HighRiskTxCount')
        chart13 = alt.Chart(hr_industry_agg).mark_bar().encode(
            x=alt.X('HighRiskTxCount:Q', title='High-Risk Transactions'),
            y=alt.Y('industry:N', sort='-x', title='Industry'),
            tooltip=['industry','HighRiskTxCount']
        ).properties(width=600, height=300)
        st.altair_chart(chart13, use_container_width=True)
    with col2:
        st.markdown("### Industries with Transactions Exceeding Reported Sales")
        if 'sales' in df.columns:
            sales_agg = df.groupby('industry').agg(
                total_amount=('amount_cad','sum'),
                reported_sales=('sales','max')
            ).reset_index()
            exceeding = sales_agg[sales_agg['total_amount'] > sales_agg['reported_sales']]
            chart14 = alt.Chart(exceeding).mark_bar().encode(
                x=alt.X('total_amount:Q', title='Total Transaction Amount'),
                y=alt.Y('industry:N', sort='-x', title='Industry'),
                color=alt.Color('reported_sales:Q', title='Reported Sales', scale=alt.Scale(scheme='blues')),
                tooltip=['industry','total_amount','reported_sales']
            ).properties(width=600, height=300)
            st.altair_chart(chart14, use_container_width=True)
            st.write(f"{len(exceeding)} industries exceed reported sales.")
        else:
            st.write("No 'sales' column to compare reported sales vs. transaction amounts.")

    # -----------------------
    # Row 8: (15) Industries Dominating Fraud Prone Loc. | (16) Flagged Cust. Linked to Fraud Ind.
    # col1, col2 = st.columns(2)
    # with col1:
    #     st.markdown("### Industries Dominating Fraud Prone Locations")
    #     if 'fraud_prone_location' in df.columns:
    #         fpl_agg = df[df['fraud_prone_location'] == 1].groupby('industry')['transaction_id'].count().reset_index(name='TxCount')
    #         chart15 = alt.Chart(fpl_agg).mark_bar().encode(
    #             x=alt.X('TxCount:Q', title='Transactions in Fraud Prone Locations'),
    #             y=alt.Y('industry:N', sort='-x', title='Industry'),
    #             tooltip=['industry','TxCount']
    #         ).properties(width=600, height=300)
    #         st.altair_chart(chart15, use_container_width=True)
    #     else:
    #         st.write("No 'fraud_prone_location' column available.")
    # with col2:
    st.markdown("### Flagged Customers Linked to Fraud Prone Industries")
    flagged_customers = cust_risk[cust_risk['outlier_sum']>5]['customer_id']
    flagged_df = df[df['customer_id'].isin(flagged_customers)]
    flagged_ind = flagged_df.groupby('industry')['customer_id'].nunique().reset_index(name='FlaggedCustCount')
    chart16 = alt.Chart(flagged_ind).mark_bar().encode(
        x=alt.X('FlaggedCustCount:Q', title='Flagged Customers'),
        y=alt.Y('industry:N', sort='-x', title='Industry'),
        tooltip=['industry','FlaggedCustCount']
    ).properties(width=600, height=300)
    st.altair_chart(chart16, use_container_width=True)

    # -----------------------
    # Row 9: (17) Industries w/ Most Shared Cust. Tx | (Extra) High Transaction Merchant Categories
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Industries with the Most Shared Customer Transactions")
        cust_per_ind = df.groupby('industry')['customer_id'].nunique().reset_index(name='UniqueCust')
        chart17 = alt.Chart(cust_per_ind.nlargest(10,'UniqueCust')).mark_bar().encode(
            x=alt.X('UniqueCust:Q', title='Number of Unique Customers'),
            y=alt.Y('industry:N', sort='-x', title='Industry'),
            tooltip=['industry','UniqueCust']
        ).properties(width=600, height=300)
        st.altair_chart(chart17, use_container_width=True)
    with col2:
        st.markdown("### High Transaction Merchant Categories")
        high_merch = df[df['high_txn_outlier'] == 1].groupby('merchant_category').size().reset_index(name='count')
        high_merch_chart = alt.Chart(high_merch).mark_bar().encode(
            x=alt.X('count:Q', title="Count"),
            y=alt.Y('merchant_category:N', sort='-x', title="Merchant Category"),
            tooltip=['merchant_category', 'count']
        ).properties(width=600, height=300)
        st.altair_chart(high_merch_chart, use_container_width=True)
