
import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd

st.set_page_config(page_title="ONE FC Name + Country", page_icon="🌍")
st.title("🌍 ONE Athlete Name Translator + Country (Mapped)")

url = st.text_input("Paste the ONE athlete URL:", "https://www.onefc.com/athletes/rodtang/")

# Slug-to-country mapping (manually maintained)
country_map = {
    "rodtang": "Thailand",
    "jonathan-haggerty": "United Kingdom",
    "stamp-fairtex": "Thailand",
    "alaverdi-ramazanov": "Russia",
    "liam-harrison": "United Kingdom",
    "superlek-kiatmoo9": "Thailand",
    "jackie-buntan": "United States"
    # Add more as needed
}

def fetch_name(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, 'html.parser')
        h1 = soup.find('h1', {'class': 'use-letter-spacing-hint my-4'}) or soup.find('h1')
        return h1.get_text(strip=True) if h1 else "Name not found"
    except Exception as e:
        return f"Error: {e}"

if "/athletes/" in url:
    parsed = urlparse(url)
    slug = parsed.path.strip('/').split('/')[-1]

    langs = {
        "English": f"https://www.onefc.com/athletes/{slug}/",
        "Thai": f"https://www.onefc.com/th/athletes/{slug}/",
        "Japanese": f"https://www.onefc.com/jp/athletes/{slug}/",
        "Chinese": f"https://www.onefc.com/cn/athletes/{slug}/"
    }

    with st.spinner("Fetching names..."):
        results = {lang: fetch_name(link) for lang, link in langs.items()}
        country = country_map.get(slug.lower(), "Not found")

    st.markdown(f"**🌍 Country:** `{country}`")
    df = pd.DataFrame(results.items(), columns=["Language", "Name"])
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", data=csv, file_name="onefc_names_country_mapped.csv", mime="text/csv")
