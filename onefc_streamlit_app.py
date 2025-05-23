
import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd
import difflib

st.set_page_config(page_title="ONE FC Name + Auto Country", page_icon="🌍")
st.title("🌍 ONE Athlete Name Translator + Auto Country")

url = st.text_input("Paste the ONE athlete URL:", "https://www.onefc.com/athletes/rodtang/")

@st.cache_data(ttl=86400)
def fetch_directory():
    headers = {'User-Agent': 'Mozilla/5.0'}
    page = requests.get("https://www.onefc.com/athletes/", headers=headers, timeout=15)
    soup = BeautifulSoup(page.content, "html.parser")

    directory = {}
    cards = soup.select("div.athlete-card")
    for card in cards:
        name = card.select_one("div.athlete-card__name")
        country = card.select_one("div.athlete-card__country")
        if name and country:
            directory[name.get_text(strip=True)] = country.get_text(strip=True)
    return directory

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

def fuzzy_lookup(name, directory):
    matches = difflib.get_close_matches(name, directory.keys(), n=1, cutoff=0.6)
    return directory[matches[0]] if matches else "Not found"

if "/athletes/" in url:
    parsed = urlparse(url)
    slug = parsed.path.strip('/').split('/')[-1]

    langs = {
        "English": f"https://www.onefc.com/athletes/{slug}/",
        "Thai": f"https://www.onefc.com/th/athletes/{slug}/",
        "Japanese": f"https://www.onefc.com/jp/athletes/{slug}/",
        "Chinese": f"https://www.onefc.com/cn/athletes/{slug}/"
    }

    with st.spinner("Fetching name translations..."):
        directory = fetch_directory()
        en_name = fetch_name(langs["English"])
        country = fuzzy_lookup(en_name, directory)

        results = {
            "English": en_name,
            "Thai": fetch_name(langs["Thai"]),
            "Japanese": fetch_name(langs["Japanese"]),
            "Chinese": fetch_name(langs["Chinese"]),
        }

    st.markdown(f"**🌍 Country:** `{country}`")
    df = pd.DataFrame(results.items(), columns=["Language", "Name"])
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", data=csv, file_name="onefc_names_country_fuzzy.csv", mime="text/csv")
