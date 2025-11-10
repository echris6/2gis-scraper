"""
2GIS Business Scraper - Web Interface
"""

import streamlit as st
import sys
import os
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / '2gis_scraper'))
from scraper_wrapper import scrape_with_progress, get_city_list

st.set_page_config(
    page_title="2GIS Lead Scraper",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    * {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    .main {
        padding: 2rem;
    }

    .block-container {
        max-width: 1100px;
        padding: 2rem 1rem;
    }

    /* Main card */
    .main-card {
        background: white;
        border-radius: 16px;
        padding: 3rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.15);
    }

    /* Header */
    h1 {
        color: white !important;
        font-size: 2.5rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
        text-align: center;
    }

    .subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* Labels */
    label {
        color: #1a1a1a !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
        display: block !important;
    }

    /* Inputs */
    .stTextInput input, .stSelectbox select, .stNumberInput input {
        border: 2px solid #e0e0e0 !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        background: white !important;
        color: #1a1a1a !important;
        transition: all 0.2s !important;
    }

    .stTextInput input:focus, .stSelectbox select:focus, .stNumberInput input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }

    .stSelectbox > div > div {
        background: white !important;
    }

    /* Checkboxes */
    .stCheckbox {
        padding: 0.5rem 0;
    }

    .stCheckbox label {
        font-weight: 500 !important;
        color: #2a2a2a !important;
    }

    /* Primary button */
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.875rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        transition: all 0.3s !important;
    }

    .stButton button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.5) !important;
    }

    /* Download buttons */
    .stDownloadButton button {
        background: white !important;
        color: #667eea !important;
        border: 2px solid #667eea !important;
        border-radius: 8px !important;
        padding: 0.625rem 1.25rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.2s !important;
    }

    .stDownloadButton button:hover {
        background: #667eea !important;
        color: white !important;
    }

    /* Stats cards */
    .stat-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px;
        padding: 1.75rem;
        text-align: center;
        border: none;
    }

    .stat-label {
        color: #5a5a5a;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.75rem;
    }

    .stat-value {
        font-size: 2.75rem;
        font-weight: 700;
        color: #1a1a1a;
        line-height: 1;
    }

    .stat-subtitle {
        color: #7a7a7a;
        font-size: 0.9rem;
        margin-top: 0.5rem;
        font-weight: 500;
    }

    /* Table */
    .stDataFrame {
        border: 2px solid #e0e0e0 !important;
        border-radius: 12px !important;
    }

    /* Progress */
    .stProgress > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border-radius: 10px !important;
    }

    /* Messages */
    .stSuccess {
        background: #d4edda !important;
        border: 2px solid #28a745 !important;
        border-radius: 8px !important;
        color: #155724 !important;
        font-weight: 500 !important;
    }

    .stError {
        background: #f8d7da !important;
        border: 2px solid #dc3545 !important;
        border-radius: 8px !important;
        color: #721c24 !important;
        font-weight: 500 !important;
    }

    .stInfo {
        background: #d1ecf1 !important;
        border: 2px solid #17a2b8 !important;
        border-radius: 8px !important;
        color: #0c5460 !important;
        font-weight: 500 !important;
    }

    /* Hide streamlit stuff */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1a1a1a;
        margin: 2.5rem 0 1.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("2GIS Lead Scraper")
st.markdown('<p class="subtitle">Extract business leads from 2GIS directory</p>', unsafe_allow_html=True)

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None

# Main form
st.markdown('<div class="main-card">', unsafe_allow_html=True)

with st.form("scraper_form"):
    st.markdown("### Configuration")
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        cities = get_city_list()
        city = st.selectbox(
            "City",
            cities,
            index=cities.index('moscow') if 'moscow' in cities else 0
        )

    with col2:
        query = st.text_input(
            "Search Query",
            value="автомойка"
        )

    with col3:
        pages = st.number_input(
            "Pages",
            min_value=1,
            max_value=50,
            value=2
        )

    st.markdown("<br>", unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)

    with col4:
        enrich_contacts = st.checkbox(
            "Enrich with phone/website",
            value=True
        )

    with col5:
        no_website_only = st.checkbox(
            "Only businesses without website",
            value=False
        )

    with col6:
        require_phone = st.checkbox(
            "Only businesses with phone",
            value=False
        )

    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button("Start Scraping", type="primary")

st.markdown('</div>', unsafe_allow_html=True)

# Handle submission
if submitted:
    if not query.strip():
        st.error("Please enter a search query")
    else:
        st.session_state.results = None

        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            for update in scrape_with_progress(
                city=city,
                query=query,
                max_pages=pages,
                enrich_contacts=enrich_contacts,
                min_rating=None,
                min_reviews=None,
                no_website_only=no_website_only,
                require_phone=require_phone
            ):
                if 'progress' in update:
                    progress_bar.progress(update['progress'])

                if 'status' in update:
                    status_text.info(update['status'])

                if 'businesses' in update:
                    st.session_state.results = update['businesses']

        except Exception as e:
            st.error(f"Error: {str(e)}")

        finally:
            progress_bar.empty()
            status_text.empty()

# Display results
if st.session_state.results:
    businesses = st.session_state.results

    st.markdown('<p class="section-header">Results</p>', unsafe_allow_html=True)

    # Stats
    col1, col2, col3, col4 = st.columns(4)

    with_phone = sum(1 for b in businesses if b.get('phone'))
    with_website = sum(1 for b in businesses if b.get('website'))
    no_website = len(businesses) - with_website
    ratings = [b['rating'] for b in businesses if b.get('rating')]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0

    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Total Leads</div>
            <div class="stat-value">{len(businesses)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">With Phone</div>
            <div class="stat-value">{with_phone}</div>
            <div class="stat-subtitle">{with_phone/len(businesses)*100:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">No Website</div>
            <div class="stat-value">{no_website}</div>
            <div class="stat-subtitle">{no_website/len(businesses)*100:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Avg Rating</div>
            <div class="stat-value">{avg_rating:.1f}</div>
            <div class="stat-subtitle">out of 5.0</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Table
    if businesses:
        df_display = pd.DataFrame(businesses)
        display_cols = ['name', 'address', 'phone', 'website', 'rating', 'review_count']
        display_cols = [col for col in display_cols if col in df_display.columns]

        st.dataframe(
            df_display[display_cols],
            use_container_width=True,
            height=450
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # Downloads
        col1, col2, col3 = st.columns(3)

        with col1:
            from exporter import DataExporter
            import json

            exporter = DataExporter()
            df = exporter.to_dataframe(businesses)
            csv_bytes = ('\ufeff' + df.to_csv(index=False)).encode('utf-8')

            st.download_button(
                label="Download CSV",
                data=csv_bytes,
                file_name=f"{city}_{query}_leads.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col2:
            json_data = json.dumps(businesses, ensure_ascii=False, indent=2)

            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=f"{city}_{query}_leads.json",
                mime="application/json",
                use_container_width=True
            )

        with col3:
            qualified = [b for b in businesses if not b.get('website')]
            if qualified:
                df_q = exporter.to_dataframe(qualified)
                csv_q = ('\ufeff' + df_q.to_csv(index=False)).encode('utf-8')

                st.download_button(
                    label=f"Qualified Leads ({len(qualified)})",
                    data=csv_q,
                    file_name=f"{city}_{query}_qualified.csv",
                    mime="text/csv",
                    use_container_width=True
                )
