
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urlparse

st.set_page_config(page_title="ONE FC Country Extractor", page_icon="🌍")

st.title("🌍 ONE FC Athlete Country Extractor")
url = st.text_input("Paste the ONE FC athlete URL:", "https://www.onefc.com/athletes/jonathan-haggerty/")

def extract_country(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, "html.parser")

        # Extract name
        h1 = soup.find("h1") or soup.find("h1", {"class": "use-letter-spacing-hint my-4"})
        name = h1.get_text(strip=True) if h1 else "Name not found"

        # Extract COUNTRY field only
        label_div = soup.find("div", string=lambda text: text and text.strip().upper() == "COUNTRY")
        if label_div:
            value_div = label_div.find_next_sibling("div")
            country = value_div.get_text(strip=True) if value_div else "Not found"
        else:
            country = "Not found"

        return {"Name": name, "Country": country}
    except Exception as e:
        return {"Error": str(e)}

if "/athletes/" in url:
    with st.spinner("Extracting..."):
        result = extract_country(url)

    if "Error" in result:
        st.error(result["Error"])
    else:
        df = pd.DataFrame(result.items(), columns=["Field", "Value"])
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", data=csv, file_name="onefc_country.csv", mime="text/csv")
