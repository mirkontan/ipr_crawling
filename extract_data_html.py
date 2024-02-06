import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

def extract_data_int(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
        html_code = r.text
        # st.write(html_code)
        soup = BeautifulSoup(html_code, 'html.parser')
        table = soup.find('table', class_='markInformation')
        header = table.find('thead')
        header_row = header.find('tr')
        header_cols = header_row.find_all('th')
        header_data = [col.text.strip() for col in header_cols]
        data = []
        print(table.find('tbody').find_all('tr'))
        for row in table.find('tbody').find_all('tr'):
            cols = row.find_all('td')
            cols_data = [col.text.strip() for col in cols]
            data.append(cols_data)
        df_data = pd.DataFrame(data, columns=header_data)
        df_data['IPR_URL'] = url
        # st.write('DF DATA')
        # st.write(df_data)

        return df_data
    except Exception as e:
        print(f"Error extracting data from {url}: {e}")
        return None

