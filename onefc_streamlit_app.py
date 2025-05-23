# ONE FC Athlete Name Translator (Selenium + Streamlit)

import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
from urllib.parse import urlparse

st.set_page_config(page_title="ONE FC Name Translator (Selenium)", page_icon="🏋️")
st.title("🏋️ ONE FC Athlete Name Translator with Country")

url = st.text_input("Paste the ONE athlete URL:", "https://www.onefc.com/athletes/rodtang/")

@st.cache_resource
def create_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    return driver

def fetch_name_and_country(url):
    driver = create_driver()
    driver.get(url)
    time.sleep(2)

    try:
        name = driver.find_element(By.TAG_NAME, "h1").text
    except:
        name = "Name not found"

    try:
        country = driver.find_element(By.XPATH, "//div[contains(text(),'COUNTRY')]/following-sibling::div").text
    except:
        country = "Country not found"

    driver.quit()
    return name, country

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
        main_name, country = fetch_name_and_country(langs["English"])
        results = {lang: fetch_name_and_country(link)[0] for lang, link in langs.items()}

    st.markdown(f"**🌍 Country:** `{country}`")
    df = pd.DataFrame(results.items(), columns=["Language", "Name"])
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "onefc_names_country.csv", "text/csv")
