import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd

st.set_page_config(page_title="ONE FC Name Translator + Country", page_icon="🥋")
st.title("🥋 ONE FC Athlete Name Translator + Country")

url = st.text_input("Paste the ONE FC athlete URL:", "https://www.onefc.com/athletes/rodtang/")

def fetch_name_and_country(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, 'html.parser')

        # Extract name
        h1 = soup.find('h1', {'class': 'use-letter-spacing-hint my-4'}) or soup.find('h1')
        name = h1.get_text(strip=True) if h1 else "Name not found"

        # Extract country
        country_label = soup.find('h6', string="COUNTRY")
        country = country_label.find_next_sibling("div").get_text(strip=True) if country_label else "Not found"

        return name, country
    except Exception as e:
        return f"Error: {e}", "Not found"

if "/athletes/" in url:
    parsed = urlparse(url)
    slug = parsed.path.strip('/').split('/')[-1]
    langs = {
        "English": f"https://www.onefc.com/athletes/{slug}/",
        "Thai": f"https://www.onefc.com/th/athletes/{slug}/",
        "Japanese": f"https://www.onefc.com/jp/athletes/{slug}/",
        "Chinese": f"https://www.onefc.com/cn/athletes/{slug}/"
    }

    with st.spinner("Fetching names and country..."):
        results = {}
        country = "Not found"
        for lang, link in langs.items():
            name, extracted_country = fetch_name_and_country(link)
            results[lang] = name
            if lang == "English":
                country = extracted_country

    st.markdown(f"**🌍 Country:** `{country}`")
    df = pd.DataFrame(results.items(), columns=["Language", "Name"])
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", data=csv, file_name="onefc_names_country.csv", mime="text/csv")
