
import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd

st.set_page_config(page_title="ONE FC Name + Country", page_icon="🌍")

st.title("🌍 ONE Athlete Name Translator + Precise Country")

url = st.text_input("Paste the ONE athlete URL:", "https://www.onefc.com/athletes/rodtang/")

def fetch_name_and_country(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, 'html.parser')

        # Extract name
        h1 = soup.find('h1', {'class': 'use-letter-spacing-hint my-4'}) or soup.find('h1')
        name = h1.get_text(strip=True) if h1 else "Name not found"

        # Extract country from COUNTRY label
        country = "Not found"
        label_divs = soup.find_all("div")
        for div in label_divs:
            if div.get_text(strip=True).upper() == "COUNTRY":
                next_div = div.find_next_sibling("div")
                if next_div and next_div.get_text(strip=True):
                    country = next_div.get_text(strip=True)
                    break

        return name, country
    except Exception as e:
        return f"Error: {e}", "Error"

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
        results = {}
        en_name, country = fetch_name_and_country(langs['English'])
        results["English"] = en_name
        results["Thai"] = fetch_name_and_country(langs["Thai"])[0]
        results["Japanese"] = fetch_name_and_country(langs["Japanese"])[0]
        results["Chinese"] = fetch_name_and_country(langs["Chinese"])[0]

    st.markdown(f"**🌍 Country:** `{country}`")
    df = pd.DataFrame(results.items(), columns=["Language", "Name"])
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", data=csv, file_name="onefc_names_with_country.csv", mime="text/csv")
