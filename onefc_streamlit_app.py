
import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd

st.set_page_config(page_title="ONE FC Name Translator", page_icon="🥋")

st.title("🥋 ONE FC Athlete Name Translator")
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

        # Final fix: Find div where text is "COUNTRY" and then the next sibling with value
        country = "Not found"
        for label in soup.find_all("div", string=lambda text: text and text.strip().upper() == "COUNTRY"):
            value_div = label.find_next_sibling("div")
            if value_div and value_div.get_text(strip=True):
                country = value_div.get_text(strip=True)
                break

        return name, country
    except Exception as e:
        return f"Error: {e}", "N/A"

def fetch_name_only(url):
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

    with st.spinner("Fetching data..."):
        en_name, country = fetch_name_and_country(langs['English'])
        results = {
            "English": en_name,
            "Thai": fetch_name_only(langs["Thai"]),
            "Japanese": fetch_name_only(langs["Japanese"]),
            "Chinese": fetch_name_only(langs["Chinese"]),
        }

    st.markdown(f"**🌍 Country:** `{country}`")
    df = pd.DataFrame(results.items(), columns=["Language", "Name"])
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", data=csv, file_name="onefc_names.csv", mime="text/csv")
