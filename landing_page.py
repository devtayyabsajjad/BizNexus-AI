import streamlit as st

# Configure the page with dark mode defaults
st.set_page_config(
    page_title="BizNexus",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark mode with attractive dark gradient hero
st.markdown("""
    <style>
        /* Global Reset */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        /* Dark Mode Background */
        [data-testid="stAppViewContainer"] {
            background: #121212;
            color: #E0E0E0;
        }
        section {
            margin: 2rem auto;
            max-width: 1400px;
            padding: 0 2rem;
        }
        /* Navigation Bar */
        .nav-container {
            background: #1E1E1E;
            padding: 1rem 2rem;
            box-shadow: 0 2px 10px rgba(255,255,255,0.1);
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
        }
        .nav-logo {
            font-size: 1.5rem;
            font-weight: 700;
            color: #BB86FC;
        }
        /* Hero Section with Dark Gradient */
        .hero-container {
            background: linear-gradient(145deg, #1F1C2C, #928DAB);
            border-radius: 20px;
            padding: 4rem 2rem;
            text-align: center;
            color: white;
            margin-top: 2rem;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        }
        .hero-title {
            font-size: 3.5rem;
            font-weight: 800;
            margin-bottom: 1.5rem;
            background: linear-gradient(to right, #BB86FC, #3700B3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .hero-subtitle {
            font-size: 1.5rem;
            line-height: 1.7;
            max-width: 800px;
            margin: 0 auto;
            opacity: 0.9;
        }
        /* Feature Cards */
        .card-container {
            background: #1E1E1E;
            border-radius: 16px;
            padding: 2rem;
            height: 100%;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            transition: transform 0.3s ease;
            border: 1px solid #333;
        }
        .card-container:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.7);
        }
        .card-icon {
            font-size: 2.5rem;
            margin-bottom: 1.5rem;
            display: inline-block;
            padding: 1rem;
            background: #333;
            border-radius: 12px;
        }
        .card-title {
            font-size: 1.8rem;
            font-weight: 700;
            color: #BB86FC;
            margin-bottom: 1rem;
        }
        .card-description {
            color: #B0B0B0;
            font-size: 1.1rem;
            line-height: 1.6;
            margin-bottom: 1.5rem;
        }
        /* Action Buttons */
        .btn-primary {
            display: inline-block;
            padding: 0.8rem 1.8rem;
            font-size: 1.1rem;
            font-weight: 600;
            color: white;
            background: linear-gradient(to right, #BB86FC, #3700B3);
            border-radius: 8px;
            text-decoration: none;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(187,134,252,0.5);
        }
        /* Stats Section */
        .stats-container {
            background: #1E1E1E;
            border-radius: 16px;
            padding: 3rem 2rem;
            margin-top: 3rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            border: 1px solid #333;
        }
        .stat-box {
            text-align: center;
            padding: 1.5rem;
            background: #121212;
            border-radius: 12px;
            transition: transform 0.3s ease;
        }
        .stat-box:hover {
            transform: translateY(-5px);
        }
        .stat-number {
            font-size: 2.8rem;
            font-weight: 800;
            color: #BB86FC;
            margin-bottom: 0.5rem;
        }
        .stat-label {
            color: #B0B0B0;
            font-size: 1.2rem;
            font-weight: 500;
        }
        /* Responsive Design */
        @media screen and (max-width: 768px) {
            .hero-title {
                font-size: 2.5rem;
            }
            .hero-subtitle {
                font-size: 1.2rem;
            }
            .card-container {
                margin-bottom: 1.5rem;
            }
        }
    </style>
""", unsafe_allow_html=True)

# Navigation
st.markdown("""
    <div class="nav-container">
        <div class="nav-logo">BizNexus</div>
    </div>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
    <section>
        <div class="hero-container">
            <h1 class="hero-title">BizNexus AI Analytics Platform</h1>
            <p class="hero-subtitle">
                Transform your business with dark mode powered analytics, real-time insights, 
                and intelligent decision-making tools.
            </p>
        </div>
    </section>
""", unsafe_allow_html=True)

# Feature Cards Section with updated order (Business Intelligence, E-commerce, HRMS)
st.markdown("<section>", unsafe_allow_html=True)
cols = st.columns(3)

# Business Intelligence Card
with cols[0]:
    st.markdown("""
        <div class="card-container">
            <div class="card-icon">📊</div>
            <h2 class="card-title">Business Intelligence</h2>
            <p class="card-description">
                Access powerful business insights instantly. Create custom reports,
                analyze market trends, and make informed decisions with real-time analytics.
            </p>
            <a href="./2_Business_Intelligence_Suite" class="btn-primary">
                Explore BI Suite →
            </a>
        </div>
    """, unsafe_allow_html=True)

# E-commerce Analytics Card
with cols[1]:
    st.markdown("""
        <div class="card-container">
            <div class="card-icon">🛒</div>
            <h2 class="card-title">E-commerce Analytics</h2>
            <p class="card-description">
                Optimize your online business with advanced analytics. Monitor sales,
                track customer behavior, and maximize revenue with data-driven strategies.
            </p>
            <a href="./3_Ecommerce_Analytics_Dashboard" class="btn-primary">
                E-commerce Hub →
            </a>
        </div>
    """, unsafe_allow_html=True)

# HR Analytics Card
with cols[2]:
    st.markdown("""
        <div class="card-container">
            <div class="card-icon">👥</div>
            <h2 class="card-title">HR Analytics</h2>
            <p class="card-description">
                Revolutionize your HR operations with AI-powered analytics. Track employee performance,
                streamline recruitment, and boost engagement through data-driven insights.
            </p>
            <a href="./1_HRMS_Dashboard" class="btn-primary">
                Launch HR Dashboard →
            </a>
        </div>
    """, unsafe_allow_html=True)

st.markdown("</section>", unsafe_allow_html=True)

# Stats Section
st.markdown("""
    <section>
        <div class="stats-container">
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 2rem;">
                <div class="stat-box">
                    <div class="stat-number">99.9%</div>
                    <div class="stat-label">Platform Uptime</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">50M+</div>
                    <div class="stat-label">Data Points Analyzed</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">500+</div>
                    <div class="stat-label">Enterprise Clients</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">24/7</div>
                    <div class="stat-label">Expert Support</div>
                </div>
            </div>
        </div>
    </section>
""", unsafe_allow_html=True)
