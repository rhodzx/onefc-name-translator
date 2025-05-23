import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse
import pandas as pd
import time

# Page setup
st.set_page_config(page_title="ONE FC Name Translator (Selenium)", page_icon="🥋")
st.title("🥋 ONE Athlete Name Translator + Country (Selenium)")

url = st.text_input("Paste the ONE athlete URL:", "https://www.onefc.com/athletes/rodtang/")

# Set up browser (headless mode optional)
@st.cache_resource
def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in background
    options.add_argument('--disable-gpu')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver = create_driver()

def fetch_name_and_country(url):
    try:
        driver.get(url)
        time.sleep(2)  # Wait for JS to render

        # Fetch athlete name
        name = driver.find_element(By.TAG_NAME, "h1").text

        # Fetch country from the block (example uses "COUNTRY" as label)
        country_element = driver.find_element(By.XPATH, "//div[contains(text(), 'COUNTRY')]/following-sibling::div")
        country = country_element.text

        return name, country

    except Exception as e:
        return f"Error: {e}", "Not found"

def fetch_translations(slug):
    base = f"https://www.onefc.com"
    langs = {
        "English": f"{base}/athletes/{slug}/",
        "Thai": f"{base}/th/athletes/{slug}/",
        "Japanese": f"{base}/jp/athletes/{slug}/",
        "Chinese": f"{base}/cn/athletes/{slug}/"
    }
    names = {}
    for lang, link in langs.items():
        try:
            driver.get(link)
            time.sleep(2)
            h1 = driver.find_element(By.TAG_NAME, "h1").text
            names[lang] = h1
        except:
            names[lang] = "Name not found"
    return names

if "/athletes/" in url:
    slug = urlparse(url).path.strip("/").split("/")[-1]

    with st.spinner("Fetching data..."):
        name, country = fetch_name_and_country(url)
        translations = fetch_translations(slug)

    st.markdown(f"**🌍 Country:** `{country}`")

    df = pd.DataFrame(translations.items(), columns=["Language", "Name"])
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", data=csv, file_name="onefc_names_country_selenium.csv", mime="text/csv")
