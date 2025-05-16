import streamlit as st
import modules.youtube_utils as youtube_utils
import modules.news_retriever as news_retriever


# --- Mock Data ---
news_data = {
    "National": [
        {"title": "Parliament Passes New Data Law", "summary": "India's new Digital Personal Data Protection Bill regulates data usage and introduces consent-driven frameworks to protect citizens' privacy."},
        {"title": "Monsoon Hits Kerala", "summary": "IMD confirms early monsoon in Kerala, signalling a positive start to the cropping season."},
        {"title": "Supreme Court Rules on Electoral Bonds", "summary": "The Supreme Court invalidated electoral bonds, calling them unconstitutional. This is seen as a win for transparency in political funding."},
        {"title": "Delhi Air Quality Remains 'Severe'", "summary": "With AQI crossing 450, Delhi's pollution crisis worsens. Emergency measures are being enforced."},
        {"title": "Delhi Air Quality Remains 'Severe'", "summary": "With AQI crossing 450, Delhi's pollution crisis worsens. Emergency measures are being enforced."}
    ],
    "World": [
        {"title": "UN Climate Conference Concludes", "summary": "The latest UN climate conference ended with nations agreeing to new carbon reduction targets amidst calls for more urgent action."},
        {"title": "Peace Talks Resume in Middle East", "summary": "Peace negotiations have resumed after a six-month hiatus, bringing cautious optimism to the long-standing conflict."}
    ],
    "Sports": [
        {"title": "India Wins Cricket World Cup", "summary": "Team India lifted the trophy after a thrilling final match that went down to the last over."},
        {"title": "Olympics Preparation in Full Swing", "summary": "Athletes across the country intensify training as the Olympic Games approach in less than six months."}
    ],
    "Business": [
        {"title": "Startup Funding Reaches New High", "summary": "Venture capital investments in Indian startups reached $42 billion this quarter, setting a new record."},
        {"title": "Sensex Crosses 70,000 Mark", "summary": "The benchmark index reached an all-time high amid strong foreign investment and positive economic indicators."}
    ],
    "Miscellaneous": [
        {"title": "New Space Telescope Discovers Exoplanet", "summary": "Scientists have identified a potentially habitable planet 40 light years away using the latest space telescope technology."},
        {"title": "AI Art Competition Sparks Debate", "summary": "The inclusion of AI-generated artworks in a major competition has raised questions about creativity and authorship in the digital age."}
    ]
}

# --- Rendering Function ---
def render_category(category, articles):
    st.markdown(f"### {category}")
    html = '<div class="scroll-container">'
    for a in articles:
        html += f'<div class="news-card"><h4>{a["title"]}</h4><p>{a["summary"]}</p></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def ShortNewsPage():
    st.title("📰 Categorised News Stream")

    # --- Custom CSS ---
    st.markdown("""
    <style>
    .scroll-container {
        display: flex;
        overflow-x: auto;
        padding-bottom: 1rem;
        width: 100%;
        min-width: 100%;
        gap: 16px;
        scrollbar-width: thin;
        scrollbar-color: #888 #f1f1f1;
    }
    .scroll-container::-webkit-scrollbar {
        height: 8px;
    }
    .scroll-container::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    .scroll-container::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }
    .news-card {
        flex: 0 0 auto;
        width: 320px;
        background-color: #E8F5E9;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        word-wrap: break-word;
        overflow-wrap: anywhere;
        white-space: normal;
    }
    .news-card h4 {
        margin-top: 0;
        margin-bottom: 10px;
        font-size: 16px;
        font-weight: bold;
    }
    .news-card p {
        margin: 0;
        font-size: 14px;
        color: #444;
    }
    </style>
""", unsafe_allow_html=True)

    with st.spinner("Fetching news data..."):
        # --- Fetch News Data from YouTube ---
        news_data = news_retriever.generate_youtube_news_data()

    # --- Display Each Category ---
    for category, articles in news_data.items():
        render_category(category, articles)
