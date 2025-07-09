import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
from PIL import Image
from customer import display_customer_analysis
from geography import display_geography_analysis
from transactions import display_transactions_analysis
from enterprise import display_enterprise_analysis
from main_chatbot import chatbot_main, safe_page_config

logo = Image.open("logo.png")

# Page Configuration
st.set_page_config(
    page_title="TransACT",
    # page_icon="🇨🇦",
    page_icon=logo,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling
st.markdown("""
<style>
[data-testid="block-container"] {
    padding: 1rem 3rem;
}
.stMetric {
    background-color: #2b2b2b;
    border-radius: 8px;
    padding: 15px;
}
</style>
""", unsafe_allow_html=True)

# Load Data (Replace with your actual data paths)
df = pd.read_csv('imi_features.csv')

# NEW: Minimal caching function
@st.cache_data
def cache_df(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Caches the loaded DataFrame so that it won't be reloaded on every rerun.
    Note: This does NOT reduce the DataFrame size below 200MB if the data is inherently large.
    """
    return dataframe

# Reassign df to the cached version
df = cache_df(df)

# Sidebar Navigation
with st.sidebar:
    # st.title("🇨🇦 TransACT")
    st.image(logo, width=50)
    st.title("TransACT")
    analysis_type = st.radio("Select Analysis Type", 
        ["Customer Insights", "Geographical Insights", 
                                "Transaction Insights", "Enterprise Insights", "Chatbot"])
    
    # year = st.selectbox("Select Year", [2022, 2023, 2024])
    # risk_threshold = st.slider("Risk Threshold", 0, 100, 75)

# Summary Metrics Function
def render_summary_metrics(df):
    col_stats = st.columns(4)
    with col_stats[0]:
        st.metric("Total Transactions", f"{df.shape[0]:,}")
    with col_stats[1]:
        st.metric("High-Risk Transactions", 
                 f"{df[df['outlier'] == 1].shape[0]:,}",
                 "3.2% of Total")
    with col_stats[2]:
        st.metric("Avg Transaction Amount", 
                 f"${df['amount_cad'].mean():,.2f}")
    with col_stats[3]:
        st.metric("Flagged Customers", 
                 f"{df['customer_id'].nunique():,}", 
                 "12% Increase MoM")

# Filterable Data Table Function  
def render_data_table(df):
    st.subheader("Transaction Details")
    amount_filter = st.slider("Filter by Amount (CAD)", 
                             float(df['amount_cad'].min()),
                             float(df['amount_cad'].max()),
                             (1000.0, 10000.0))
    filtered_df = df[(df['amount_cad'] >= amount_filter[0]) &
                    (df['amount_cad'] <= amount_filter[1])]
    st.dataframe(filtered_df[[
        'customer_id', 'amount_cad', 'province_1', 
        'industry', 'outlier'
    ]].head(20), height=300)

# Risk Analysis Scatter Plot Function
def render_risk_scatter(df, sample_size=1000):
    st.subheader("Transaction Risk Analysis")
    scatter = px.scatter(df.sample(sample_size),
                        x='amount_cad',
                        y='employee_count',
                        color='outlier',
                        hover_data=['industry', 'city_1'],
                        title="Transaction Amount vs Employee Count",
                        log_x=True)
    st.plotly_chart(scatter, use_container_width=True)

# Main Content
def calculate_outliers(df):
    """Calculate outliers using IQR method based on EDA findings"""
    Q1 = df['amount_cad'].quantile(0.25)
    Q3 = df['amount_cad'].quantile(0.75)
    IQR = Q3 - Q1
    return (df['amount_cad'] > (Q3 + 1.5 * IQR)) | (df['amount_cad'] < (Q1 - 1.5 * IQR))


# Router for different analysis types
if analysis_type == "Customer Insights":
    display_customer_analysis(df)
    # render_summary_metrics(df)
    # render_data_table(df) 
    # render_risk_scatter(df)

elif analysis_type == "Geographical Insights":
   display_geography_analysis(df)
    # render_summary_metrics(card_df)
    # render_data_table(card_df) 
    # render_risk_scatter(card_df)
# Add other analysis types similarly

elif analysis_type == "Transaction Insights":
    display_transactions_analysis(df)

elif analysis_type == "Enterprise Insights":
    display_enterprise_analysis(df)

elif analysis_type == "Chatbot":
    # Call the safe config first
    safe_page_config()
    # Then render chatbot components
    chatbot_main()


