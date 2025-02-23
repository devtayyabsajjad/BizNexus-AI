import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
from groq import Groq
import json
from datetime import datetime, timedelta
import requests
import yfinance as yf

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize Groq client
client = Groq(api_key=groq_api_key)

if 'competitor_data' not in st.session_state:
    st.session_state.competitor_data = pd.DataFrame(columns=['Name', 'Product', 'Price', 'Market_Share', 'Date_Added'])
if 'customer_data' not in st.session_state:
    st.session_state.customer_data = pd.DataFrame()

# Configure dark mode settings
st.set_page_config(page_title="E-commerce Analytics Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] { background-color: #121212; color: #E0E0E0; }
        .stButton>button { background-color: #BB86FC; color: white; border-radius: 5px; }
        .stButton>button:hover { background-color: #3700B3; }
        .st-emotion-cache-1v0mbdj { background-color: #1E1E1E; border-radius: 10px; padding: 1.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.5); }\n
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def fetch_market_data():
    tickers = ["AMZN", "SHOP", "ETSY", "WMT", "TGT"]
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    market_data = pd.DataFrame()
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date)
        if market_data.empty:
            market_data = hist['Close'].rename(ticker)
        else:
            market_data = pd.concat([market_data, hist['Close'].rename(ticker)], axis=1)
    market_data['Market_Index'] = market_data.mean(axis=1)
    return market_data

@st.cache_data(ttl=1800)
def fetch_pricing_data():
    categories = ['Electronics', 'Fashion', 'Home', 'Beauty', 'Sports']
    pricing_data = []
    for category in categories:
        products = fetch_category_products(category)
        pricing_data.extend(products)
    return pd.DataFrame(pricing_data)

def fetch_category_products(category):
    category_ranges = {
        'Electronics': (100, 1000),
        'Fashion': (20, 200),
        'Home': (50, 500),
        'Beauty': (10, 100),
        'Sports': (30, 300)
    }
    price_range = category_ranges[category]
    products = []
    for i in range(5):
        base_price = np.random.uniform(price_range[0], price_range[1])
        margin = np.random.uniform(0.2, 0.4)
        cost = base_price * (1 - margin)
        products.append({
            'Category': category,
            'Product': f'{category} Product {i+1}',
            'Cost': round(cost, 2),
            'Current_Price': round(base_price, 2),
            'Margin': round(margin * 100, 1)
        })
    return products

def get_ai_analysis(prompt, context=""):
    try:
        full_prompt = f"""Context: {context}

        Task: {prompt}

        Please provide a detailed analysis focusing on actionable insights."""
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.7,
            max_tokens=500
        )
        return completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error in AI analysis: {str(e)}")
        return "AI analysis temporarily unavailable. Please try again later."

def analyze_market_trends():
    st.subheader("📈 Market Trends Analysis")
    with st.spinner("Fetching market data..."):
        market_data = fetch_market_data()
        col1, col2 = st.columns(2)
        with col1:
            fig = px.line(market_data, title='E-commerce Sector Trends', template="plotly_dark")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            returns = market_data.pct_change()
            fig = px.box(returns, title='Daily Returns Distribution', template="plotly_dark")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        analysis = get_ai_analysis(
            "Analyze the e-commerce sector trends and provide strategic insights",
            f"Market data for last 30 days shows following trends:\n{market_data.describe().to_string()}"
        )
        st.info("💡 AI Analysis\n\n" + analysis)

def optimize_pricing():
    st.subheader("💰 Price Optimization")
    with st.spinner("Analyzing pricing data..."):
        pricing_data = fetch_pricing_data()
        selected_category = st.selectbox("Select Category", pricing_data['Category'].unique())
        category_data = pricing_data[pricing_data['Category'] == selected_category]
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(category_data, x='Product', y=['Current_Price', 'Cost'], barmode='group', template="plotly_dark",
                         title='Price vs Cost Analysis')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.scatter(category_data, x='Current_Price', y='Margin', template="plotly_dark",
                             title='Price-Margin Relationship', size='Current_Price')
            st.plotly_chart(fig, use_container_width=True)
        analysis = get_ai_analysis(
            f"Provide pricing optimization recommendations for {selected_category} category",
            f"Current pricing data:\n{category_data.to_string()}"
        )
        st.info("💡 Pricing Recommendations\n\n" + analysis)

def predict_purchase_probability():
    st.subheader("🎯 Purchase Probability Prediction")
    col1, col2 = st.columns(2)
    with col1:
        price = st.slider("Product Price ($)", 10, 1000, 100)
        customer_rating = st.slider("Customer Rating", 1.0, 5.0, 4.0)
    with col2:
        stock_level = st.slider("Stock Level", 0, 100, 50)
        season = st.selectbox("Season", ["Spring", "Summer", "Fall", "Winter"])
    if st.button("Calculate Probability"):
        with st.spinner("Calculating purchase probability..."):
            context = f"""
            Product Details:
            - Price: ${price}
            - Customer Rating: {customer_rating}/5
            - Stock Level: {stock_level}%
            - Season: {season}
            """
            analysis = get_ai_analysis(
                "Predict purchase probability and provide reasoning",
                context
            )
            try:
                probability = float(analysis.split('%')[0]) / 100
            except:
                probability = 0.5
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = probability * 100,
                title = {'text': "Purchase Probability"},
                gauge = {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 30], 'color': "lightgray"},
                        {'range': [30, 70], 'color': "gray"},
                        {'range': [70, 100], 'color': "darkgray"}
                    ]
                }
            ))
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            st.info("💡 Analysis\n\n" + analysis)

def add_competitor_product():
    st.subheader("🏢 Competitor Product Analysis")
    col1, col2 = st.columns(2)
    with col1:
        competitor_name = st.text_input("Competitor Name")
        product_name = st.text_input("Product Name")
    with col2:
        price = st.number_input("Price ($)", min_value=0.0, value=99.9)
        market_share = st.number_input("Market Share (%)", min_value=0.0, max_value=100.0, value=15.0)
    if st.button("Add Competitor Product"):
        new_competitor = pd.DataFrame({
            'Name': [competitor_name],
            'Product': [product_name],
            'Price': [price],
            'Market_Share': [market_share],
            'Date_Added': [datetime.now()]
        })
        st.session_state.competitor_data = pd.concat([st.session_state.competitor_data, new_competitor], ignore_index=True)
        st.success("Competitor product added successfully!")
    if not st.session_state.competitor_data.empty:
        st.subheader("Competitor Analysis")
        col1, col2 = st.columns(2)
        with col1:
            fig = px.scatter(st.session_state.competitor_data, 
                             x='Price', y='Market_Share',
                             size='Market_Share', color='Name',
                             title='Price vs Market Share Analysis', template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.bar(st.session_state.competitor_data, x='Name', y='Price',
                         title='Price Comparison', template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        analysis = get_ai_analysis(
            "Analyze competitor positioning and provide strategic recommendations",
            f"Competitor data:\n{st.session_state.competitor_data.to_string()}"
        )
        st.info("💡 Competitive Analysis\n\n" + analysis)

def analyze_customer_segments():
    st.subheader("👥 Customer Segment Analysis")
    segments = {
        'Premium': {'avg_order': 200, 'frequency': 3.5, 'loyalty': 85},
        'Regular': {'avg_order': 100, 'frequency': 2.0, 'loyalty': 65},
        'Occasional': {'avg_order': 50, 'frequency': 1.0, 'loyalty': 40},
        'New': {'avg_order': 75, 'frequency': 1.5, 'loyalty': 30}
    }
    segment_df = pd.DataFrame(segments).T
    segment_df['CLV'] = segment_df['avg_order'] * segment_df['frequency'] * (segment_df['loyalty']/100)
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(segment_df, y=['avg_order', 'CLV'], template="plotly_dark",
                     title='Average Order Value & Customer Lifetime Value by Segment')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.scatter(segment_df, x='frequency', y='loyalty', template="plotly_dark",
                         size='CLV', text=segment_df.index,
                         title='Segment Analysis')
        st.plotly_chart(fig, use_container_width=True)
    analysis = get_ai_analysis(
        "Analyze customer segments and provide targeting recommendations",
        f"Segment data:\n{segment_df.to_string()}"
    )
    st.info("💡 Segment Insights\n\n" + analysis)

def generate_comprehensive_report():
    st.subheader("📊 Comprehensive Report")
    report_date = datetime.now().strftime("%Y-%m-%d")
    with st.spinner("Generating comprehensive report..."):
        market_data = fetch_market_data()
        pricing_data = fetch_pricing_data()
        market_analysis = get_ai_analysis(
            "Generate comprehensive market analysis section",
            f"Market data:\n{market_data.describe().to_string()}"
        )
        pricing_analysis = get_ai_analysis(
            "Generate pricing strategy analysis section",
            f"Pricing data:\n{pricing_data.describe().to_string()}"
        )
        if not st.session_state.competitor_data.empty:
            competitor_analysis = get_ai_analysis(
                "Generate competitor analysis section",
                f"Competitor data:\n{st.session_state.competitor_data.to_string()}"
            )
        else:
            competitor_analysis = "No competitor data available for analysis."
        st.markdown(f"""
        # E-commerce Analytics Report
        **Generated on: {report_date}**
        
        ## 1. Market Analysis
        {market_analysis}
        
        ## 2. Pricing Strategy
        {pricing_analysis}
        
        ## 3. Competitor Analysis
        {competitor_analysis}
        """)
        col1, col2 = st.columns(2)
        with col1:
            fig = px.line(market_data['Market_Index'], title='Market Index Trend', template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.box(pricing_data, x='Category', y='Margin', title='Margin Distribution by Category', template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

st.sidebar.title("E-commerce Analytics")
page = st.sidebar.selectbox(
    "Choose a feature",
    ["Market Trends", "Price Optimization", "Purchase Probability", "Competitor Analysis", "Customer Segments", "Generate Report"]
)

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.success("Data refreshed successfully!")

st.sidebar.markdown("""
---
### Data Sources
- Market data: Real-time stock market data
- Pricing data: Current product database
- Customer data: Live customer analytics
""")
st.sidebar.markdown(f"""
---
Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")

if page == "Market Trends":
    analyze_market_trends()
elif page == "Price Optimization":
    optimize_pricing()
elif page == "Purchase Probability":
    predict_purchase_probability()
elif page == "Competitor Analysis":
    add_competitor_product()
elif page == "Customer Segments":
    analyze_customer_segments()
else:
    generate_comprehensive_report()

st.markdown("""
---
📊 E-commerce Analytics Dashboard | Real-time Data Analysis
""")
