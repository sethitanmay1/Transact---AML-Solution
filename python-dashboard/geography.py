# geography.py
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

def display_geography_analysis(df):
    """
    Function to display geographical insights.
    The page is split into two columns where possible, with full-width charts for bigger graphs.
    """
    st.header("🌍 Geographical Insights")
    
    # ----------------------------------------------------
    # Metrics: Top 3 High-Risk Provinces
    province_stats = df.groupby('trans_province').agg(
        Outlier_Count=('high_txn_outlier', 'sum'),
        Cash_Transactions=('large_cash_txn', 'sum'),
        Late_Night=('odd_hour_txn', 'sum')
    ).reset_index().rename(columns={'trans_province': 'Province_Name'})
    
    if not province_stats.empty:
        top_provinces = province_stats.nlargest(3, 'Outlier_Count')
        st.markdown("#### Top 3 High-Risk Provinces")
        prov_cols = st.columns(3)
        for i, col in enumerate(prov_cols):
            province = top_provinces.iloc[i]
            col.metric(
                label=f"Rank {i+1}",
                value=province['Province_Name'],
                delta=f"{int(province['Outlier_Count'])} outliers"
            )
    
    # ----------------------------------------------------
    # Two-column layout for top high-risk cities and province analysis
    col1, col2 = st.columns(2)
    
    with col2:
        st.markdown("### Top High-Risk Cities")
        # Add metrics for top 3 high-risk cities
        city_risk = df.groupby('trans_city').agg(
            Transactions=('transaction_id', 'count'),
            Outliers=('high_txn_outlier', 'sum')
        ).reset_index()
        top_cities = city_risk.nlargest(3, 'Outliers')
        st.markdown("#### Top 3 High-Risk Cities")
        city_cols = st.columns(3)
        for i, col in enumerate(city_cols):
            city = top_cities.iloc[i]
            col.metric(
                label=f"Rank {i+1}",
                value=city['trans_city'],
                delta=f"{int(city['Outliers'])} outliers"
            )
        # Now display the chart (top 10 cities)
        city_chart = alt.Chart(city_risk.nlargest(10, 'Outliers')).mark_bar().encode(
            x=alt.X('Outliers:Q', title='High-Risk Transactions'),
            y=alt.Y('trans_city:N', sort='-x', title='City'),
            color=alt.Color('Transactions:Q', scale=alt.Scale(scheme='reds')),
            tooltip=['trans_city', 'Outliers', 'Transactions']
        ).properties(height=300)
        st.altair_chart(city_chart, use_container_width=True)
    
    # Province detailed analysis using a three-column layout (with middle spacer)
    cols = st.columns([1, 0.1, 1])
    with cols[0]:
        st.markdown("### Province Selection for Detailed Analysis")
        if not province_stats.empty:
            selected_province = st.selectbox(
                "Select Province for Detailed Analysis",
                options=province_stats['Province_Name'],
                index=province_stats['Outlier_Count'].idxmax()
            )
        else:
            selected_province = None
    with cols[2]:
        if selected_province:
            province_data = province_stats[province_stats['Province_Name'] == selected_province].melt(
                id_vars=['Province_Name'],
                value_vars=['Outlier_Count', 'Cash_Transactions', 'Late_Night'],
                var_name='Metric',
                value_name='Count'
            )
            st.markdown(f"### {selected_province} Anomaly Factors")
            bar_chart = alt.Chart(province_data).mark_bar().encode(
                x=alt.X('Metric:N', title='Metric'),
                y=alt.Y('Count:Q', title='Count'),
                color=alt.Color('Metric:N', scale=alt.Scale(scheme='set2')),
                tooltip=['Metric', 'Count']
            ).properties(height=300)
            st.altair_chart(bar_chart, use_container_width=True)
    
    # ----------------------------------------------------
    # Full-width visualization: Province-wise Heatmap of Anomaly Factors
    st.markdown("### Province-wise Heatmap of Anomaly Factors")
    province_heat = province_stats.melt(
        id_vars=['Province_Name'], 
        value_vars=['Outlier_Count', 'Cash_Transactions', 'Late_Night'],
        var_name='Metric', 
        value_name='Count'
    )
    heatmap = alt.Chart(province_heat).mark_rect().encode(
        x=alt.X('Province_Name:N', title='Province'),
        y=alt.Y('Metric:N', title='Anomaly Metric'),
        color=alt.Color('Count:Q', scale=alt.Scale(scheme='blues')),
        tooltip=['Province_Name', 'Metric', 'Count']
    ).properties(height=300)
    st.altair_chart(heatmap, use_container_width=True)
    
    # ----------------------------------------------------
    # Full-width visualization: Province-wise Outlier Transactions by Hour
    st.markdown("### Province-wise Outlier Transactions by Hour")
    province_hour = df.groupby(['trans_province', 'txn_hour']).agg(
        Outliers=('high_txn_outlier', 'sum')
    ).reset_index()
    hour_chart = alt.Chart(province_hour).mark_bar().encode(
        x=alt.X('txn_hour:O', title='Transaction Hour'),
        y=alt.Y('Outliers:Q', title='Outlier Transactions'),
        color=alt.Color('trans_province:N', legend=alt.Legend(title="Province")),
        tooltip=['trans_province', 'txn_hour', 'Outliers']
    ).properties(height=300)
    st.altair_chart(hour_chart, use_container_width=True)
    
    # ----------------------------------------------------
    # New Addition: Aggregate High and Low Transactions by Country
    st.markdown("### Aggregate High and Low Transactions by Country")
    country_agg = df.groupby('trans_country').agg(
        high_outliers=('high_txn_outlier', 'sum'),
        low_outliers=('low_txn_outlier', 'sum') if 'low_txn_outlier' in df.columns else ('low_txn_outlier', 'sum')
    ).reset_index()
    country_agg_chart = alt.Chart(country_agg).mark_bar().encode(
        x=alt.X('trans_country:N', title="Country"),
        y=alt.Y('high_outliers:Q', title="High Outlier Transactions"),
        color=alt.Color('low_outliers:Q', title="Low Outlier Transactions", scale=alt.Scale(scheme='blues')),
        tooltip=['trans_country', 'high_outliers', 'low_outliers']
    ).properties(width=600, height=300)
    st.altair_chart(country_agg_chart, use_container_width=True)
    
    # ----------------------------------------------------
    # Continue with existing full-width visualizations
    st.markdown("### Riskiest Provinces, Cities, and Countries")
    # Riskiest Provinces
    riskiest_provinces = df.groupby('trans_province').agg(
        Outliers=('high_txn_outlier', 'sum')
    ).nlargest(5, 'Outliers').reset_index().rename(columns={'trans_province':'Region'})
    riskiest_provinces['Type'] = 'Province'
    # Riskiest Cities
    riskiest_cities = df.groupby('trans_city').agg(
        Outliers=('high_txn_outlier', 'sum')
    ).nlargest(5, 'Outliers').reset_index().rename(columns={'trans_city':'Region'})
    riskiest_cities['Type'] = 'City'
    # Riskiest Countries
    riskiest_countries = df.groupby('trans_country').agg(
        Outliers=('high_txn_outlier', 'sum')
    ).nlargest(5, 'Outliers').reset_index().rename(columns={'trans_country':'Region'})
    riskiest_countries['Type'] = 'Country'
    combined = pd.concat([riskiest_provinces, riskiest_cities, riskiest_countries])
    risk_chart = alt.Chart(combined).mark_bar().encode(
        x=alt.X('Outliers:Q', title='Outlier Transactions'),
        y=alt.Y('Region:N', sort='-x', title='Region'),
        color=alt.Color('Type:N', scale=alt.Scale(scheme='category10')),
        tooltip=['Region', 'Type', 'Outliers']
    ).properties(height=300)
    st.altair_chart(risk_chart, use_container_width=True)
    
    st.markdown("### Comprehensive Province Analysis")
    comp_prov = province_stats.copy()
    prov_chart = alt.Chart(comp_prov).mark_circle(size=100).encode(
        x=alt.X('Cash_Transactions:Q', title='Cash Transactions'),
        y=alt.Y('Outlier_Count:Q', title='Outlier Transactions'),
        color=alt.Color('Province_Name:N', legend=None),
        tooltip=['Province_Name', 'Cash_Transactions', 'Outlier_Count']
    ).properties(height=300)
    st.altair_chart(prov_chart, use_container_width=True)
    
    st.markdown("### Comprehensive City Analysis")
    city_stats = df.groupby('trans_city').agg(
        Outlier_Count=('high_txn_outlier', 'sum'),
        Transactions=('transaction_id', 'count')
    ).reset_index()
    city_chart = alt.Chart(city_stats).mark_circle(size=100).encode(
        x=alt.X('Transactions:Q', title='Total Transactions'),
        y=alt.Y('Outlier_Count:Q', title='Outlier Transactions'),
        color=alt.Color('trans_city:N', legend=None),
        tooltip=['trans_city', 'Transactions', 'Outlier_Count']
    ).properties(height=300)
    st.altair_chart(city_chart, use_container_width=True)
    
    st.markdown("### Comprehensive Country Analysis")
    country_stats = df.groupby('trans_country').agg(
        Outlier_Count=('high_txn_outlier', 'sum'),
        Transactions=('transaction_id', 'count')
    ).reset_index()
    country_chart = alt.Chart(country_stats).mark_circle(size=100).encode(
        x=alt.X('Transactions:Q', title='Total Transactions'),
        y=alt.Y('Outlier_Count:Q', title='Outlier Transactions'),
        color=alt.Color('trans_country:N', legend=None),
        tooltip=['trans_country', 'Transactions', 'Outlier_Count']
    ).properties(height=300)
    st.altair_chart(country_chart, use_container_width=True)
    
    st.markdown("### Comparison of Anomaly Factors by Province")
    comp_prov_melt = province_stats.melt(
        id_vars=['Province_Name'], 
        value_vars=['Outlier_Count', 'Cash_Transactions', 'Late_Night'], 
        var_name='Metric', 
        value_name='Count'
    )
    comp_prov_chart = alt.Chart(comp_prov_melt).mark_bar().encode(
        x=alt.X('Province_Name:N', title='Province'),
        y=alt.Y('Count:Q', title='Count'),
        color=alt.Color('Metric:N', scale=alt.Scale(scheme='set2')),
        tooltip=['Province_Name', 'Metric', 'Count']
    ).properties(height=300)
    st.altair_chart(comp_prov_chart, use_container_width=True)
    
    st.markdown("### Comparison of Anomaly Factors by City (Top 15)")
    comp_city = city_stats.nlargest(15, 'Outlier_Count')
    comp_city_melt = comp_city.melt(
        id_vars=['trans_city'], 
        value_vars=['Outlier_Count', 'Transactions'], 
        var_name='Metric', 
        value_name='Count'
    )
    comp_city_chart = alt.Chart(comp_city_melt).mark_bar().encode(
        x=alt.X('trans_city:N', title='City'),
        y=alt.Y('Count:Q', title='Count'),
        color=alt.Color('Metric:N', scale=alt.Scale(scheme='set2')),
        tooltip=['trans_city', 'Metric', 'Count']
    ).properties(height=300)
    st.altair_chart(comp_city_chart, use_container_width=True)
    
    st.markdown("### Comparison of Anomaly Factors by Country")
    comp_country = country_stats.melt(
        id_vars=['trans_country'], 
        value_vars=['Outlier_Count', 'Transactions'], 
        var_name='Metric', 
        value_name='Count'
    )
    comp_country_chart = alt.Chart(comp_country).mark_bar().encode(
        x=alt.X('trans_country:N', title='Country'),
        y=alt.Y('Count:Q', title='Count'),
        color=alt.Color('Metric:N', scale=alt.Scale(scheme='set2')),
        tooltip=['trans_country', 'Metric', 'Count']
    ).properties(height=300)
    st.altair_chart(comp_country_chart, use_container_width=True)
    
    st.markdown("### Geographic Distribution of High-Risk Transactions")
    geo_dist = df.groupby('trans_province').agg(
        High_Risk_Transactions=('high_txn_outlier', 'sum')
    ).reset_index().rename(columns={'trans_province': 'Region'})
    geo_chart = alt.Chart(geo_dist).mark_bar().encode(
        x=alt.X('Region:N', title='Province'),
        y=alt.Y('High_Risk_Transactions:Q', title='High-Risk Transactions'),
        color=alt.Color('High_Risk_Transactions:Q', scale=alt.Scale(scheme='reds')),
        tooltip=['Region', 'High_Risk_Transactions']
    ).properties(height=300)
    st.altair_chart(geo_chart, use_container_width=True)
    
    st.markdown("### Cities with the Most High Risk Transactions")
    city_dist = df.groupby('trans_city').agg(
        High_Risk_Transactions=('high_txn_outlier', 'sum')
    ).reset_index()
    city_dist_chart = alt.Chart(city_dist).mark_bar().encode(
        x=alt.X('High_Risk_Transactions:Q', title='High-Risk Transactions'),
        y=alt.Y('trans_city:N', sort='-x', title='City'),
        color=alt.Color('High_Risk_Transactions:Q', scale=alt.Scale(scheme='reds')),
        tooltip=['trans_city', 'High_Risk_Transactions']
    ).properties(height=300)
    st.altair_chart(city_dist_chart, use_container_width=True)
    
    st.markdown("### Cities with Suspicious Customer Transactions")
    city_total = df.groupby('trans_city').agg(
        Total_Transactions=('transaction_id', 'count'),
        Outliers=('high_txn_outlier', 'sum')
    ).reset_index()
    city_total['Suspicious_Ratio'] = city_total['Outliers'] / city_total['Total_Transactions'] * 100
    top_cities = city_total.nlargest(10, 'Suspicious_Ratio')
    suspicious_chart = alt.Chart(top_cities).mark_bar().encode(
        x=alt.X('Suspicious_Ratio:Q', title='Suspicious Transaction Ratio (%)'),
        y=alt.Y('trans_city:N', sort='-x', title='City'),
        color=alt.Color('Suspicious_Ratio:Q', scale=alt.Scale(scheme='reds')),
        tooltip=['trans_city', 'Suspicious_Ratio', 'Total_Transactions', 'Outliers']
    ).properties(height=300)
    st.altair_chart(suspicious_chart, use_container_width=True)
