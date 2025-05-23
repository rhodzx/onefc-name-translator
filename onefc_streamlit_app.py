import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

def get_athlete_data(url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    time.sleep(2)  # wait for content to load

    try:
        name = driver.find_element(By.TAG_NAME, "h1").text
    except:
        name = "Name not found"

    try:
        country_element = driver.find_element(By.XPATH, "//h6[text()='COUNTRY']/following-sibling::div")
        country = country_element.text
    except:
        country = "Country not found"

    driver.quit()
    return name, country

st.set_page_config(page_title="ONE FC Scraper (Selenium)", page_icon="🌟")
st.title("ONE FC Athlete Info Scraper (Selenium)")

url = st.text_input("Paste the ONE athlete profile URL:", "https://www.onefc.com/athletes/rodtang/")

if st.button("Fetch Info"):
    with st.spinner("Scraping the site..."):
        name, country = get_athlete_data(url)

    st.markdown(f"**Athlete Name:** {name}")
    st.markdown(f"**Country:** {country}")

    df = pd.DataFrame([[name, country]], columns=["Name", "Country"])
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📅 Download CSV", data=csv, file_name="athlete_info.csv", mime="text/csv")
