import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from extract_data_html import extract_data_int
from create_download_link import create_download_link

# Function to process the uploaded XLSX file
def process_xlsx_file(xlsx_file):
    df_import = pd.read_excel(xlsx_file, usecols=['id', 'IPR', 'IPR_TYPE', 'IPR_TRADEMARK_TYPE', 'IPR_JURISDICTION', 'IPR_NICE_CLASS', 'NOTES'])  # Read only selected columns
    # Remove duplicates based on the 'IPR' column
    df_import = df_import.drop_duplicates(subset='IPR')
    # Reset the index of the  DataFrame
    df_import = df_import.reset_index(drop=True)
    df_import['IPR_REGISTRATION_NUMBER'] = df_import['IPR'].str.split(r' - ').str[0]
    df_import['IPR_REGISTRATION_NUMBER'] = df_import['IPR_REGISTRATION_NUMBER'].str.split(r'n. ').str[1]


    # Create 'IPR_LINK_TO_ONLINE_DATABASE' for trademarks based on 'IPR_JURISDICTION' and 'IPR_REGISTRATION_NUMBER'
    def create_ipr_url(row):
        if row['IPR_TYPE'] == 'TRADEMARK':
            if row['IPR_JURISDICTION'] == 'EUROPE':
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://www.tmdn.org/tmview/welcome#/tmview/detail/EM5000000{row["IPR_REGISTRATION_NUMBER"]}'
            elif row['IPR_JURISDICTION'] == 'UNITED STATES OF AMERICA':
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://tsdr.uspto.gov/#caseNumber={row["IPR_REGISTRATION_NUMBER"]}&caseSearchType=US_APPLICATION&caseType=SERIAL_NO&searchType=statusSearch'
            elif row['IPR_JURISDICTION'] == "PEOPLE'S REPUBLIC OF CHINA":
                iprclass = row['IPR_NICE_CLASS']
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://cloud.baidu.com/product/tms/detail?keyword={row["IPR_REGISTRATION_NUMBER"]}&keywordType=registrationNumber&registrationNumber={row["IPR_REGISTRATION_NUMBER"]}&firstCode={iprclass}'
            elif row['IPR_JURISDICTION'] == 'INDONESIA':
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://www.jumbomark.com/indonesia/trademark-registration/{row["IPR_REGISTRATION_NUMBER"]}'
            elif row['IPR_JURISDICTION'] == 'INTERNATIONAL':
                row['IPR_LINK_TO_ONLINE_DATABASE'] = r'https://www3.wipo.int/madrid/monitor/en/showData.jsp?ID=ROM.' + row["IPR_REGISTRATION_NUMBER"]
            else:
                row['IPR_LINK_TO_ONLINE_DATABASE'] = None  # Handle other jurisdictions if needed
            return row
        elif row['IPR_TYPE'] == 'DESIGN PATENT':
            if row['IPR_JURISDICTION'] == 'EUROPE':
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://www.tmdn.org/tmview/welcome#/tmview/detail/EM5000000{row["IPR_REGISTRATION_NUMBER"]}'
            elif row['IPR_JURISDICTION'] == 'UNITED STATES OF AMERICA':
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://tsdr.uspto.gov/#caseNumber={row["IPR_REGISTRATION_NUMBER"]}&caseSearchType=US_APPLICATION&caseType=SERIAL_NO&searchType=statusSearch'
            elif row['IPR_JURISDICTION'] == "PEOPLE'S REPUBLIC OF CHINA":
                iprclass = row['IPR_NICE_CLASS']
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://cloud.baidu.com/product/tms/detail?keyword=45059080&keywordType=registrationNumber&registrationNumber={row["IPR_REGISTRATION_NUMBER"]}&firstCode={iprclass}'
            elif row['IPR_JURISDICTION'] == 'INDONESIA':
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://www.jumbomark.com/indonesia/trademark-registration/{row["IPR_REGISTRATION_NUMBER"]}'
            else:
                row['IPR_LINK_TO_ONLINE_DATABASE'] = None  # Handle other jurisdictions if needed
            return row

    # # Create 'trademarks_df' and 'nottrademarks_df'
    # trademarks_df = df_import[df_import['IPR_TYPE'] == 'TRADEMARK']
    # copyright_df = df_import[df_import['IPR_TYPE'] == 'COPYRIGHT']
    # otheripr_df = df_import[df_import['IPR_TYPE'] == 'OTHER IPR']
    # design_patents_df = df_import[df_import['IPR_TYPE'] == 'DESIGN PATENT']


    # Apply the function to create 'IPR_LINK_TO_ONLINE_DATABASE' column
    df_combined = df_import.apply(create_ipr_url, axis=1)
    # st.write('DF IPR_LINK_TO_ONLINE_DATABASE GENERATOR')
    # st.write(df_combined)
 
    # Function to fetch HTML content and extract a specific section
    def cn_extract_section_from_url(url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                section = soup.find('div', {'class': 'Q0hossWj'})
                if section:
                    return str(section)  # Return the HTML content as a string
                else:
                    return "Section not found on the page."
            else:
                return f"Failed to fetch HTML content from {url}"
        except requests.exceptions.RequestException as e:
            return f"An error occurred: {e}"

    # Function to fetch and return HTML content with a timeout
    def fetch_html_content(url, timeout=50):
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                return response.text  # Return the HTML content as a string
            else:
                return f"Failed to fetch HTML content from {url}"
        except requests.exceptions.RequestException as e:
            return f"An error occurred: {e}"



    # Function to fetch HTML content and extract a specific section
    def int_extract_section_from_url(url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                section = soup.find('div', {'class': 'fragment box_content'})
                if section:
                    return str(section)  # Return the HTML content as a string
                else:
                    return "Section not found on the page."
            else:
                return f"Failed to fetch HTML content from {url}"
        except requests.exceptions.RequestException as e:
            return f"An error occurred: {e}"


    def indo_extract_section_from_url(url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                section = soup.find('div', {'class': 'fragment box_content'})
                if section:
                    return str(section)  # Return the HTML content as a string
                else:
                    return "Section not found on the page."
            else:
                return f"Failed to fetch HTML content from {url}"
        except requests.exceptions.RequestException as e:
            return f"An error occurred: {e}"
        

    df_combined['HTML'] = ""
    
    urlcount = 0
    for index, row in df_combined.iterrows():
        url = row['IPR_LINK_TO_ONLINE_DATABASE']
        jurisdiction = row['IPR_JURISDICTION']
        if pd.notna(url):
            # st.header(f"URL: {url}")
            urlcount += 1
            if "REPUBLIC OF CHINA" in jurisdiction:
                html_content = cn_extract_section_from_url(url)
            elif 'INTERNATIONAL' in jurisdiction:
                html_content = int_extract_section_from_url(url)
            elif 'INDONESIAN' in jurisdiction:
                html_content = indo_extract_section_from_url(url)

                # st.write(html_content)

            else:
                html_content = fetch_html_content(url, timeout=50)
            if html_content:
                # Assign the HTML content to df_combined['HTML']
                df_combined.at[index, 'HTML'] = html_content
    st.header(f"IPRs Analyzed: {urlcount}")
    trademarks_df = df_combined[df_combined['IPR_TYPE'] == 'TRADEMARK']
    copyright_df = df_combined[df_combined['IPR_TYPE'] == 'COPYRIGHT']
    design_patents_df = df_combined[df_combined['IPR_TYPE'] == 'DESIGN PATENT']
    invention_patents_df = df_combined[df_combined['IPR_TYPE'] == 'INVENTION PATENT']
    

    # st.write(trademarks_df)


    # Filter rows where 'IPR_JURISDICTION' is equal to 'INDONESIA'
    trademarks_df_indo_rows = trademarks_df[trademarks_df['IPR_JURISDICTION'] == "INDONESIA"]
    trademarks_df_indo_rows['IPR_HOLDER'] = trademarks_df_indo_rows['HTML'].str.split(r'<dt class="col-lg-3 col-md-4">Applicant</dt>').str[1]
    trademarks_df_indo_rows['IPR_HOLDER'] = trademarks_df_indo_rows['IPR_HOLDER'].str.split(r'</dd>').str[0]
    trademarks_df_indo_rows['IPR_HOLDER'] = trademarks_df_indo_rows['IPR_HOLDER'].str.split(r'>').str[1]
   
    trademarks_df_indo_rows['IPR_REGISTRATION_DATE'] = trademarks_df_indo_rows['HTML'].str.split(r'<dt class="col-md-4 col-lg-3">Registration Date</dt>').str[1]
    trademarks_df_indo_rows['IPR_REGISTRATION_DATE'] = trademarks_df_indo_rows['IPR_REGISTRATION_DATE'].str.split(r'</dd>').str[0]
    trademarks_df_indo_rows['IPR_REGISTRATION_DATE'] = trademarks_df_indo_rows['IPR_REGISTRATION_DATE'].str.split(r'>').str[1]
   
    trademarks_df_indo_rows['IPR_EXPIRATION_DATE'] = trademarks_df_indo_rows['HTML'].str.split(r'Expiration Date</dt>').str[1]
    trademarks_df_indo_rows['IPR_EXPIRATION_DATE'] = trademarks_df_indo_rows['IPR_EXPIRATION_DATE'].str.split(r'</dd>').str[0]
    trademarks_df_indo_rows['IPR_EXPIRATION_DATE'] = trademarks_df_indo_rows['IPR_EXPIRATION_DATE'].str.split(r'>').str[1]

    from datetime import datetime
    # Convert the dates in the column to a more standard date format
    trademarks_df_indo_rows['IPR_EXPIRATION_DATE'] = trademarks_df_indo_rows['IPR_EXPIRATION_DATE'].apply(lambda x: datetime.strptime(x, '%a, %d %b %Y').strftime('%Y-%m-%d'))
    trademarks_df_indo_rows['IPR_REGISTRATION_DATE'] = trademarks_df_indo_rows['IPR_REGISTRATION_DATE'].apply(lambda x: datetime.strptime(x, '%a, %d %b %Y').strftime('%Y-%m-%d'))
    
    trademarks_df_indo_rows['IPR_IMAGE_URL'] = trademarks_df_indo_rows['HTML'].str.split(r'itemprop="image" content="').str[1]
    trademarks_df_indo_rows['IPR_IMAGE_URL'] = trademarks_df_indo_rows['IPR_IMAGE_URL'].str.split(r'">').str[0]

    trademarks_df_indo_rows['IPR_REG_NAME'] = trademarks_df_indo_rows['HTML'].str.split(r'<div class="text-smaller text-uppercase">Trademark</div>').str[1]
    trademarks_df_indo_rows['IPR_REG_NAME'] = trademarks_df_indo_rows['IPR_REG_NAME'].str.split(r'</h2>').str[0]
    trademarks_df_indo_rows['IPR_REG_NAME'] = trademarks_df_indo_rows['IPR_REG_NAME'].str.split(r'<h2>').str[1]

    trademarks_df_indo_rows['IPR_STATUS'] = trademarks_df_indo_rows['HTML'].str.split(r'<span class="tag bg-light text-dark rounded-right border px-2">').str[1]
    trademarks_df_indo_rows['IPR_STATUS'] = trademarks_df_indo_rows['IPR_STATUS'].str.split(r'&nbsp;').str[0]

    # Function to extract elements within <dt> tags from HTML code
    def extract_nice_classes(html_code):
        soup = BeautifulSoup(html_code, 'html.parser')
        dt_elements = soup.find_all('dt')
        return ' '.join([dt.get_text() for dt in dt_elements])

    # Apply the function to the 'HTML' column and store the result in a new column 'IPR_NICE_CLASSES_ALL'
    trademarks_df_indo_rows['IPR_NICE_CLASSES_ALL'] = trademarks_df_indo_rows['HTML'].apply(extract_nice_classes)
    trademarks_df_indo_rows['IPR_NICE_CLASSES_ALL'] = trademarks_df_indo_rows['IPR_NICE_CLASSES_ALL'].str.split(r'Class & Goods/Services ').str[1]
    trademarks_df_indo_rows['IPR_NICE_CLASSES_ALL'] = trademarks_df_indo_rows['IPR_NICE_CLASSES_ALL'].str.split(r' Applicant').str[0]
    trademarks_df_indo_rows['IPR_NICE_CLASSES_ALL'] = trademarks_df_indo_rows['IPR_NICE_CLASSES_ALL'].str.replace(r' ', ', ', regex=False)

    # st.write('INDONESIA ROWS')
    # st.write(trademarks_df_indo_rows)

    # Filter rows where 'IPR_JURISDICTION' is equal to 'PEOPLE'S REPUBLIC OF CHINA'
    trademarks_df_cn_rows = trademarks_df[(trademarks_df['IPR_JURISDICTION'] == "PEOPLE'S REPUBLIC OF CHINA") | (trademarks_df['IPR_JURISDICTION'] == "PEOPLE`S REPUBLIC OF CHINA")]

    trademarks_df_cn_rows['IPR_IMAGE_URL'] = trademarks_df_cn_rows['HTML'].str.split(r'<img class=').str[1]
    trademarks_df_cn_rows['IPR_IMAGE_URL'] = trademarks_df_cn_rows['IPR_IMAGE_URL'].fillna("-")
    trademarks_df_cn_rows['IPR_IMAGE_URL'] = trademarks_df_cn_rows['IPR_IMAGE_URL'].str.split(r'" src="').str[1]
    trademarks_df_cn_rows['IPR_IMAGE_URL'] = trademarks_df_cn_rows['IPR_IMAGE_URL'].fillna("-")
    trademarks_df_cn_rows['IPR_IMAGE_URL'] = trademarks_df_cn_rows['IPR_IMAGE_URL'].str.split(r'"/>').str[0]
    
    trademarks_df_cn_rows['IPR_REG_NAME'] = trademarks_df_cn_rows['HTML'].str.split(r'商标名称').str[1]
    trademarks_df_cn_rows['IPR_REG_NAME'] = trademarks_df_cn_rows['IPR_REG_NAME'].fillna("-")
    trademarks_df_cn_rows['IPR_REG_NAME'] = trademarks_df_cn_rows['IPR_REG_NAME'].str.split(r'商标分类').str[0]
    trademarks_df_cn_rows['IPR_REG_NAME'] = trademarks_df_cn_rows['IPR_REG_NAME'].str.split(r'</div><div class="').str[1]
    trademarks_df_cn_rows['IPR_REG_NAME'] = trademarks_df_cn_rows['IPR_REG_NAME'].fillna("-")
    trademarks_df_cn_rows['IPR_REG_NAME'] = trademarks_df_cn_rows['IPR_REG_NAME'].str.split(r'">').str[1]
    trademarks_df_cn_rows['IPR_REG_NAME'] = trademarks_df_cn_rows['IPR_REG_NAME'].fillna("-")
    trademarks_df_cn_rows['IPR_REG_NAME'] = trademarks_df_cn_rows['IPR_REG_NAME'].str.split(r'</div>').str[0]

    trademarks_df_cn_rows['IPR_NICE_CLASSES_ALL'] = trademarks_df_cn_rows['HTML'].str.split(r'商标分类').str[1]
    trademarks_df_cn_rows['IPR_NICE_CLASSES_ALL'] = trademarks_df_cn_rows['IPR_NICE_CLASSES_ALL'].fillna("-")
    trademarks_df_cn_rows['IPR_NICE_CLASSES_ALL'] = trademarks_df_cn_rows['IPR_NICE_CLASSES_ALL'].str.split(r'商标状态').str[0]
    trademarks_df_cn_rows['IPR_NICE_CLASSES_ALL'] = trademarks_df_cn_rows['IPR_NICE_CLASSES_ALL'].str.split(r'</div><div class="').str[1]
    trademarks_df_cn_rows['IPR_NICE_CLASSES_ALL'] = trademarks_df_cn_rows['IPR_NICE_CLASSES_ALL'].fillna("-")
    trademarks_df_cn_rows['IPR_NICE_CLASSES_ALL'] = trademarks_df_cn_rows['IPR_NICE_CLASSES_ALL'].str.split(r'">').str[1]
    trademarks_df_cn_rows['IPR_NICE_CLASSES_ALL'] = trademarks_df_cn_rows['IPR_NICE_CLASSES_ALL'].fillna("-")

    trademarks_df_cn_rows['IPR_NICE_CLASSES_ALL'] = trademarks_df_cn_rows['IPR_NICE_CLASSES_ALL'].str.split(r'</div>').str[0]

    trademarks_df_cn_rows['IPR_STATUS'] = trademarks_df_cn_rows['HTML'].str.split(r'商标状态').str[1]
    trademarks_df_cn_rows['IPR_STATUS'] = trademarks_df_cn_rows['IPR_STATUS'].fillna("-")
    trademarks_df_cn_rows['IPR_STATUS'] = trademarks_df_cn_rows['IPR_STATUS'].str.split(r'注册号').str[0]
    trademarks_df_cn_rows['IPR_STATUS'] = trademarks_df_cn_rows['IPR_STATUS'].str.split(r'</div><div class="').str[1]
    trademarks_df_cn_rows['IPR_STATUS'] = trademarks_df_cn_rows['IPR_STATUS'].fillna("-")
    trademarks_df_cn_rows['IPR_STATUS'] = trademarks_df_cn_rows['IPR_STATUS'].str.split(r'"><div').str[1]
    trademarks_df_cn_rows['IPR_STATUS'] = trademarks_df_cn_rows['IPR_STATUS'].fillna("-")
    trademarks_df_cn_rows['IPR_STATUS'] = trademarks_df_cn_rows['IPR_STATUS'].str.split(r'">').str[1]
    trademarks_df_cn_rows['IPR_STATUS'] = trademarks_df_cn_rows['IPR_STATUS'].fillna("-")
    trademarks_df_cn_rows['IPR_STATUS'] = trademarks_df_cn_rows['IPR_STATUS'].str.split(r'</div>').str[0]
    
    trademarks_df_cn_rows['IPR_REGISTRATION_DATE'] = trademarks_df_cn_rows['HTML'].str.split(r'注册公告日期</div><div class="').str[1]
    trademarks_df_cn_rows['IPR_REGISTRATION_DATE'] = trademarks_df_cn_rows['IPR_REGISTRATION_DATE'].fillna("-")
    trademarks_df_cn_rows['IPR_REGISTRATION_DATE'] = trademarks_df_cn_rows['IPR_REGISTRATION_DATE'].str.split(r'专用权期限').str[0]
    trademarks_df_cn_rows['IPR_REGISTRATION_DATE'] = trademarks_df_cn_rows['IPR_REGISTRATION_DATE'].str.split(r'">').str[1]
    trademarks_df_cn_rows['IPR_REGISTRATION_DATE'] = trademarks_df_cn_rows['IPR_REGISTRATION_DATE'].fillna("-")
    trademarks_df_cn_rows['IPR_REGISTRATION_DATE'] = trademarks_df_cn_rows['IPR_REGISTRATION_DATE'].str.split(r'</div>').str[0]

    trademarks_df_cn_rows['IPR_EXPIRATION_DATE'] = trademarks_df_cn_rows['HTML'].str.split(r'专用权期限</div><div class="').str[1]
    trademarks_df_cn_rows['IPR_EXPIRATION_DATE'] = trademarks_df_cn_rows['IPR_EXPIRATION_DATE'].fillna("-")
    trademarks_df_cn_rows['IPR_EXPIRATION_DATE'] = trademarks_df_cn_rows['IPR_EXPIRATION_DATE'].str.split(r'商标类型').str[0]
    trademarks_df_cn_rows['IPR_EXPIRATION_DATE'] = trademarks_df_cn_rows['IPR_EXPIRATION_DATE'].str.split(r'">').str[1]
    trademarks_df_cn_rows['IPR_EXPIRATION_DATE'] = trademarks_df_cn_rows['IPR_EXPIRATION_DATE'].str.split(r'</div>').str[0]
    trademarks_df_cn_rows['IPR_EXPIRATION_DATE'] = trademarks_df_cn_rows['IPR_EXPIRATION_DATE'].str.split(r'至').str[1]
    
    trademarks_df_cn_rows['IPR_TYPEhtml'] = trademarks_df_cn_rows['HTML'].str.split(r'商标类型').str[1]
    trademarks_df_cn_rows['IPR_TYPEhtml'] = trademarks_df_cn_rows['IPR_TYPEhtml'].fillna("-")
    trademarks_df_cn_rows['IPR_TYPEhtml'] = trademarks_df_cn_rows['IPR_TYPEhtml'].str.split(r'类似群组').str[0]
    trademarks_df_cn_rows['IPR_TYPEhtml'] = trademarks_df_cn_rows['IPR_TYPEhtml'].str.split(r'">').str[1]
    trademarks_df_cn_rows['IPR_TYPEhtml'] = trademarks_df_cn_rows['IPR_TYPEhtml'].str.split(r'</div>').str[0]

    trademarks_df_cn_rows['IPR_SUBCLASSES'] = trademarks_df_cn_rows['HTML'].str.split(r'类似群组').str[1]
    trademarks_df_cn_rows['IPR_SUBCLASSES'] = trademarks_df_cn_rows['IPR_SUBCLASSES'].fillna("-")
    trademarks_df_cn_rows['IPR_SUBCLASSES'] = trademarks_df_cn_rows['IPR_SUBCLASSES'].str.split(r'适用商品服务').str[0]
    trademarks_df_cn_rows['IPR_SUBCLASSES'] = trademarks_df_cn_rows['IPR_SUBCLASSES'].str.split(r'FvDQAhY').str[1]
    trademarks_df_cn_rows['IPR_SUBCLASSES'] = trademarks_df_cn_rows['IPR_SUBCLASSES'].str.split(r'<').str[0]
    trademarks_df_cn_rows['IPR_SUBCLASSES'] = trademarks_df_cn_rows['IPR_SUBCLASSES'].str.replace(r'">', '', regex=False)

    trademarks_df_cn_rows['IPR_SUBCLASSESdetails'] = trademarks_df_cn_rows['HTML'].str.split(r'适用商品服务').str[1]
    trademarks_df_cn_rows['IPR_SUBCLASSESdetails'] = trademarks_df_cn_rows['IPR_SUBCLASSESdetails'].fillna("-")
    trademarks_df_cn_rows['IPR_SUBCLASSESdetails'] = trademarks_df_cn_rows['IPR_SUBCLASSESdetails'].str.split(r'<div class=""liYyg7LN"">').str[0]
    trademarks_df_cn_rows['IPR_SUBCLASSESdetails'] = trademarks_df_cn_rows['IPR_SUBCLASSESdetails'].str.replace(r'</div><div class="aFvDQAhY">', '; ', regex=False)
    trademarks_df_cn_rows['IPR_SUBCLASSESdetails'] = trademarks_df_cn_rows['IPR_SUBCLASSESdetails'].str.replace(r'<!-- -->-<!-- -->', ': ', regex=False)
    trademarks_df_cn_rows['IPR_SUBCLASSESdetails'] = trademarks_df_cn_rows['IPR_SUBCLASSESdetails'].str.split(r'"aFvDQAhY">').str[1]
    trademarks_df_cn_rows['IPR_SUBCLASSESdetails'] = trademarks_df_cn_rows['IPR_SUBCLASSESdetails'].str.split(r'<div').str[0]
    trademarks_df_cn_rows['IPR_SUBCLASSESdetails'] = trademarks_df_cn_rows['IPR_SUBCLASSESdetails'].str.split(r'</div></div></div>').str[0]
    
    trademarks_df_cn_rows['IPR_HOLDER'] = trademarks_df_cn_rows['HTML'].str.split(r'申请人</div><div class="').str[1]
    trademarks_df_cn_rows['IPR_HOLDER'] = trademarks_df_cn_rows['IPR_HOLDER'].fillna("-")
    trademarks_df_cn_rows['IPR_HOLDER'] = trademarks_df_cn_rows['IPR_HOLDER'].str.split(r'申请人地址</div>').str[0]
    trademarks_df_cn_rows['IPR_HOLDER'] = trademarks_df_cn_rows['IPR_HOLDER'].str.split(r'</div>').str[0]
    trademarks_df_cn_rows['IPR_HOLDER'] = trademarks_df_cn_rows['IPR_HOLDER'].str.split(r'">').str[1]


#------------------ FUNZIONA! ----------------

    # def extract_trademarks_df_cn_rows(url, item_class):
    #     try:
    #         response = requests.get(url)
    #         if response.status_code == 200:
    #             soup = BeautifulSoup(response.text, 'html.parser')
    #             section = soup.find('div', {'class': item_class})
    #             if section:
    #                 return str(section)  # Return the HTML content as a string
    #             else:
    #                 return "Section not found on the page."
    #         else:
    #             return f"Failed to fetch HTML content from {url}"
    #     except requests.exceptions.RequestException as e:
    #         return f"An error occurred: {e}"
    
    # # search for IPR_STATUS in html
    # for index, row in trademarks_df_cn_rows.iterrows():
    #     url = row['IPR_URL']
    #     item_class = 'UR3VDgzg SbZoKhMs'
    #     if pd.notna(url):
    #         st.header(f"URL: {url}")
    #         html_content = extract_trademarks_df_cn_rows(url, item_class)
    #         if html_content:
    #             # Assign the HTML content to df_combined['HTML']
    #             trademarks_df_cn_rows.at[index, 'TEST'] = html_content
   
  

    # Display the updated DataFrame
    # st.write('TRADEMARK CN ROWS')
    # st.write(trademarks_df_cn_rows)




    # Filter rows where 'IPR_JURISDICTION' is equal to 'INT'
    trademarks_df_int_rows = trademarks_df[trademarks_df['IPR_JURISDICTION'] == 'INTERNATIONAL']

    # Iterate through the URLs and extract data
    for index, row in trademarks_df_int_rows.iterrows():
        url = row['IPR_LINK_TO_ONLINE_DATABASE']
        # st.write('URLS DA PARSARE:')
        # st.write(url)
        df_data = extract_data_int(url)
        # st.write(df_data)
        if df_data is not None:
            # Assuming the extracted data is a DataFrame with one row
            for column in df_data.columns:
                trademarks_df_int_rows.loc[index, column] = df_data[column].iloc[0]


    def extract_country_codes(html_content):
        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')
        # Find all spans with class 'hasTip country'
        spans = soup.find_all('span', class_='hasTip country')
        # Use a set to store unique country codes
        unique_country_codes = set()
        for span in spans:
            unique_country_codes.add(span.text.strip())
        # Join the country codes into a comma-separated string
        return ', '.join(unique_country_codes)



    def extract_dates(html_content):
        # Regular expression pattern to match dates
        date_pattern = r'\b\d{2}/\d{2}/\d{4}\b'
        # Find all matches of dates in the HTML content
        dates = re.findall(date_pattern, html_content)
        # Ensure at least two dates are found
        if len(dates) >= 2:
            # Extract the first and second dates
            first_date = dates[0]
            second_date = dates[1]
            return first_date, second_date
        else:
            return None, None

    
    # Function to extract the img src from the HTML content
    def extract_img_src_from_html(html_content):
        # Parse the HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the img tag
        img_tag = soup.find('img')
        
        # If img tag is found, extract src attribute
        if img_tag:
            return img_tag['src']
        else:
            return None

    # Apply the function to extract img src from HTML column
    trademarks_df_int_rows['IPR_IMAGE_URL'] = trademarks_df_int_rows['HTML'].apply(extract_img_src_from_html)


    # Rename columns
    trademarks_df_int_rows = trademarks_df_int_rows.rename(columns={'Trademark': 'IPR_REG_NAME2',
                                                                    'Holder': 'IPR_HOLDER',
                                                                    'Nice': 'IPR_NICE_CLASSES_ALL',
                                                                    'Registration Date': 'IPR_REGISTRATION_DATE', 
                                                                    'Expiration Date': 'IPR_EXPIRATION_DATE'})

    # Now, trademarks_df_int_rows will have the columns renamed

    # Apply the function to extract country codes and populate 'IPR_DESIGNATIONS' column
    trademarks_df_int_rows['IPR_DESIGNATIONS'] = trademarks_df_int_rows['HTML'].apply(extract_country_codes)



    trademarks_df_int_rows['IPR_IMAGE_URL'] = trademarks_df_int_rows['HTML'].str.split(r'<img alt="').str[1]

    trademarks_df_int_rows['IPR_IMAGE_URL'] = trademarks_df_int_rows['IPR_IMAGE_URL'].str.split(r'" src="..').str[1]
    trademarks_df_int_rows['IPR_IMAGE_URL'] = trademarks_df_int_rows['IPR_IMAGE_URL'].str.split(r'" style').str[0]
    trademarks_df_int_rows['IPR_IMAGE_URL'] = trademarks_df_int_rows['IPR_IMAGE_URL'].str.replace(r'/jsp/', 'https://www3.wipo.int/madrid/monitor/jsp/', regex=False)
    trademarks_df_int_rows['IPR_IMAGE_URL'] = trademarks_df_int_rows['IPR_IMAGE_URL'].str.replace(r'amp;', '', regex=False)

    trademarks_df_int_rows['IPR_REG_NAME'] = trademarks_df_int_rows['HTML'].str.split(r'markname"').str[1]
    trademarks_df_int_rows['IPR_REG_NAME'] = trademarks_df_int_rows['IPR_REG_NAME'].str.split(r'</h3> </td> <td> <div class').str[0]
    trademarks_df_int_rows['IPR_REG_NAME'] = trademarks_df_int_rows['IPR_REG_NAME'].str.split(r'-').str[1]
    trademarks_df_int_rows['IPR_REG_NAME'] = trademarks_df_int_rows['IPR_REG_NAME'].str.split(r'<').str[0]

    # # Find the ul element within the specified class
    # target_ul = html.find('ul', class_='your-class')
    # # Extract the text from all li elements within the ul
    # elements = target_ul.find_all('li')

    # trademarks_df_int_rows['IPR_CLASSEShtml'] = trademarks_df_int_rows['HTML'].str.split(r'class=""nice').str[1]
    # trademarks_df_int_rows['IPR_CLASSEShtml'] = trademarks_df_int_rows['IPR_CLASSEShtml'].str.split(r'</div> </td> </tr> </tbody').str[0]

    trademarks_df_int_rows['IPR_STATUS'] = trademarks_df_int_rows['HTML'].str.split(r'status="').str[1]
    trademarks_df_int_rows['IPR_STATUS'] = trademarks_df_int_rows['IPR_STATUS'].str.split(r'">  </div> </td').str[0]
    trademarks_df_int_rows['IPR_STATUS'] = trademarks_df_int_rows['IPR_STATUS'].str.split(r'">').str[0]
    
    
    # trademarks_df_cn_rows['IPR_REG_DATE'] = trademarks_df_cn_rows['HTML'].str.split(r'注册公告日期</div><div class="').str[1]
    # trademarks_df_cn_rows['IPR_REG_DATE'] = trademarks_df_cn_rows['IPR_REG_DATE'].str.split(r'专用权期限').str[0]
    # trademarks_df_cn_rows['IPR_REG_DATE'] = trademarks_df_cn_rows['IPR_REG_DATE'].str.split(r'">').str[1]
    # trademarks_df_cn_rows['IPR_REG_DATE'] = trademarks_df_cn_rows['IPR_REG_DATE'].str.split(r'</div>').str[0]

    # trademarks_df_cn_rows['IPR_EXPIRATION_DATE'] = trademarks_df_cn_rows['HTML'].str.split(r'专用权期限</div><div class="').str[1]
    # trademarks_df_cn_rows['IPR_EXPIRATION_DATE'] = trademarks_df_cn_rows['IPR_EXPIRATION_DATE'].str.split(r'商标类型').str[0]
    # trademarks_df_cn_rows['IPR_EXPIRATION_DATE'] = trademarks_df_cn_rows['IPR_EXPIRATION_DATE'].str.split(r'">').str[1]
    # trademarks_df_cn_rows['IPR_EXPIRATION_DATE'] = trademarks_df_cn_rows['IPR_EXPIRATION_DATE'].str.split(r'</div>').str[0]
    # trademarks_df_cn_rows['IPR_EXPIRATION_DATE'] = trademarks_df_cn_rows['IPR_EXPIRATION_DATE'].str.split(r'至').str[1]

    # trademarks_df_cn_rows['IPR_APPLICANT'] = trademarks_df_cn_rows['HTML'].str.split(r'申请人</div><div class="').str[1]
    # trademarks_df_cn_rows['IPR_APPLICANT'] = trademarks_df_cn_rows['IPR_APPLICANT'].str.split(r'申请人地址</div>').str[0]
    # trademarks_df_cn_rows['IPR_APPLICANT'] = trademarks_df_cn_rows['IPR_APPLICANT'].str.split(r'</div>').str[0]
    # trademarks_df_cn_rows['IPR_APPLICANT'] = trademarks_df_cn_rows['IPR_APPLICANT'].str.split(r'">').str[1]

    # st.write(trademarks_df_int_rows)


    trademarks_df_eu_rows = trademarks_df[trademarks_df['IPR_JURISDICTION'] == "EUROPE"]



    trademarks_df = pd.concat([trademarks_df_int_rows, trademarks_df_cn_rows, trademarks_df_indo_rows, trademarks_df_eu_rows], ignore_index=True)
    # st.write(trademarks_df)

    # Re-concatenate the DataFrames to create df_combined
    df_combined = pd.concat([trademarks_df, design_patents_df, copyright_df, invention_patents_df], ignore_index=True)
    # Reset the index of the combined DataFrame
    df_combined = df_combined.reset_index(drop=True)

    # Replace null values in 'IPR_IMAGE_URL' column with '-'
    df_combined['IPR_HOLDER'] = df_combined['IPR_HOLDER'].fillna('-')
    df_combined['IPR_REGISTRATION_DATE'] = df_combined['IPR_REGISTRATION_DATE'].fillna('-')
    df_combined['IPR_EXPIRATION_DATE'] = df_combined['IPR_EXPIRATION_DATE'].fillna('-')
    df_combined['IPR_NICE_CLASSES_ALL'] = df_combined['IPR_NICE_CLASSES_ALL'].fillna('-')
    df_combined['IPR_IMAGE_URL'] = df_combined['IPR_IMAGE_URL'].fillna('-')
    df_combined['IPR_DESIGNATIONS'] = df_combined['IPR_DESIGNATIONS'].fillna('-')
    df_combined['IPR_EXPIRATION_DATE'] = df_combined['IPR_EXPIRATION_DATE'].fillna('-')
    # Replace all null values in df_combined columns with '-'
    df_combined.fillna('-', inplace=True)

    # Duplicate df_combined
    df_combined_copy = df_combined.copy()

    # Drop the 'HTML' column
    df_combined.drop(columns=['HTML'], inplace=True)

    # Reorder the columns
    new_column_order = ['id', 'IPR', 'IPR_TYPE', 'IPR_TRADEMARK_TYPE', 'IPR_IMAGE_URL', 'IPR_JURISDICTION', 
                        'IPR_NICE_CLASS', 'IPR_REGISTRATION_DATE', 'IPR_EXPIRATION_DATE', 'IPR_LINK_TO_ONLINE_DATABASE', 
                        'IPR_REGISTRATION_NUMBER', 'IPR_DESIGNATIONS', 'NOTES', 'IPR_REG_NAME2', 'IPR_REG_NAME', 
                        'IPR_STATUS', 'IPR_TYPEhtml', 'IPR_HOLDER', 'IPR_NICE_CLASSES_ALL', 'IPR_SUBCLASSES', 
                        'IPR_SUBCLASSESdetails']

    df_combined = df_combined.reindex(columns=new_column_order)

    st.title("Data Analysis")
    st.write(df_combined)


    # Add a download link for df_combined
    st.sidebar.markdown("### Download Processed Data")
    xlsx_download_link = create_download_link(df_combined, "IPR Info Export.xlsx", "-> Download Excel <-")
    st.markdown(xlsx_download_link, unsafe_allow_html=True)



# Streamlit UI
st.title("Trademark Data Analysis")

# Upload an XLSX file
xlsx_file = st.sidebar.file_uploader("Upload an XLSX file", type=["xlsx"], accept_multiple_files=False)

if xlsx_file:
    df_import = process_xlsx_file(xlsx_file)
    # st.dataframe(df_import)
