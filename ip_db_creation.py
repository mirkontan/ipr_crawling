import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from extract_data_html import extract_data_int
from create_download_link import create_download_link
import time

# Function to process the uploaded XLSX file
def process_xlsx_file(xlsx_file):
    df_import = pd.read_excel(xlsx_file, usecols=['id', 'IPR', 'IPR_TYPE', 'IPR_TRADEMARK_TYPE', 'IPR_JURISDICTION', 'IPR_NICE_CLASS', 'NOTES'])  # Read only selected columns
    # Remove duplicates based on the 'IPR' column
    df_import = df_import.drop_duplicates(subset='IPR')
    # Reset the index of the  DataFrame
    df_import = df_import.reset_index(drop=True)

    df_import['IPR_REGISTRATION_NUMBER'] = df_import['IPR'].str.split(r' - ').str[0]
    df_import['IPR_REGISTRATION_NUMBER'] = df_import['IPR_REGISTRATION_NUMBER'].str.split(r'n. ').str[1]
    df_import['IPR_REGISTRATION_NUMBER'] = df_import['IPR_REGISTRATION_NUMBER'].str.split(r' \(').str[0]
    df_import['IPR_REGISTRATION_NUMBER'] = df_import['IPR_REGISTRATION_NUMBER'].fillna('-')
    df_import['IPR_DATABASE_URL'] = '-'

    not_parsed_tm_jurisdictions = []
    parsed_tm_jurisdictions = []
    parseable_design_jurisdictions = []
    parsed_designs_jurisdictions = []
    

    # Create 'IPR_LINK_TO_ONLINE_DATABASE' for trademarks based on 'IPR_JURISDICTION' and 'IPR_REGISTRATION_NUMBER'
    def create_ipr_url(row):
        jurisdiction = row['IPR_JURISDICTION']
        iprregnum = row['IPR_REGISTRATION_NUMBER']
        if row['IPR_TYPE'] == 'TRADEMARK':
            if row['IPR_JURISDICTION'] == 'EUROPE':
                parsed_tm_jurisdictions.append(jurisdiction)
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://register.dpma.de/DPMAregister/marke/registerhabm?AKZ={row["IPR_REGISTRATION_NUMBER"]}'
                row['IPR_DATABASE_URL'] = f'https://euipo.europa.eu/eSearch/#details/trademarks/{row["IPR_REGISTRATION_NUMBER"]}'
            elif row['IPR_JURISDICTION'] == 'GERMANY':
                parsed_tm_jurisdictions.append(jurisdiction)
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://register.dpma.de/DPMAregister/marke/registerhabm?AKZ={row["IPR_REGISTRATION_NUMBER"]}'
                row['IPR_DATABASE_URL'] = row['IPR_LINK_TO_ONLINE_DATABASE']
            elif row['IPR_JURISDICTION'] == 'UNITED KINGDOM':
                parsed_tm_jurisdictions.append(jurisdiction)
                # Remove 'UK' from iprregnum if present
                iprregnum = iprregnum.replace('UK', '')
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://www.ipo.gov.uk/tmcase/Results/1/{row["IPR_REGISTRATION_NUMBER"]}'
                row['IPR_DATABASE_URL'] = row['IPR_LINK_TO_ONLINE_DATABASE']
            elif row['IPR_JURISDICTION'] == 'ITALY':
                not_parsed_tm_jurisdictions.append(jurisdiction)
                row['IPR_LINK_TO_ONLINE_DATABASE'] = '-'
                row['IPR_DATABASE_URL'] = f'https://branddb.wipo.int/en/advancedsearch/results?sort=score%20desc&strategy=concept&rows=30&asStructure=%7B%22_id%22:%22d36b%22,%22boolean%22:%22AND%22,%22bricks%22:%5B%7B%22_id%22:%22d36e%22,%22key%22:%22office%22,%22strategy%22:%22any_of%22,%22value%22:%5B%7B%22value%22:%22IT%22,%22label%22:%22(IT)%20UIBM%22,%22score%22:99,%22highlighted%22:%22(%3Cem%3EIT%3C%2Fem%3E)%20UIBM%22%7D%5D%7D,%7B%22_id%22:%22d36f%22,%22key%22:%22regNum%22,%22value%22:%22{iprregnum}%22%7D%5D%7D&fg=_void_&_=1707582301537'
            elif row['IPR_JURISDICTION'] == 'UNITED STATES OF AMERICA' or row['IPR_JURISDICTION'] == 'UNITED STATES':
                not_parsed_tm_jurisdictions.append(jurisdiction)
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://tsdr.uspto.gov/#caseNumber={row["IPR_REGISTRATION_NUMBER"]}&caseSearchType=US_APPLICATION&caseType=SERIAL_NO&searchType=statusSearch'
                row['IPR_DATABASE_URL'] = row['IPR_LINK_TO_ONLINE_DATABASE']
            elif row['IPR_JURISDICTION'] == "PEOPLE'S REPUBLIC OF CHINA"  or row['IPR_JURISDICTION'] == "PEOPLE`S REPUBLIC OF CHINA":
                parsed_tm_jurisdictions.append(jurisdiction)
                iprclass = row['IPR_NICE_CLASS']
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://cloud.baidu.com/product/tms/detail?keyword={row["IPR_REGISTRATION_NUMBER"]}&keywordType=registrationNumber&registrationNumber={row["IPR_REGISTRATION_NUMBER"]}&firstCode={iprclass}'
                row['IPR_DATABASE_URL'] = f'https://www.chinatrademarkoffice.com/search/tmdetails/{iprclass}/{row["IPR_REGISTRATION_NUMBER"]}.html'
            elif row['IPR_JURISDICTION'] == "JAPAN":
                not_parsed_tm_jurisdictions.append(jurisdiction)
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://branddb.wipo.int/en/advancedsearch/results?sort=score%20desc&strategy=concept&rows=30&asStructure=%7B%22_id%22:%2278be%22,%22boolean%22:%22AND%22,%22bricks%22:%5B%7B%22_id%22:%2278bf%22,%22key%22:%22office%22,%22strategy%22:%22any_of%22,%22value%22:%5B%7B%22value%22:%22JP%22,%22label%22:%22(JP)%20JPO%22,%22score%22:194,%22highlighted%22:%22(%3Cem%3EJP%3C%2Fem%3E)%20%3Cem%3EJP%3C%2Fem%3EO%22%7D%5D%7D,%7B%22_id%22:%2278c0%22,%22key%22:%22regNum%22,%22value%22:%22{iprregnum}%22%7D%5D%7D&fg=_void_&_=1707743403159'
                row['IPR_DATABASE_URL'] = row['IPR_LINK_TO_ONLINE_DATABASE']
            elif row['IPR_JURISDICTION'] == 'INDONESIA':
                parsed_tm_jurisdictions.append(jurisdiction)
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://www.jumbomark.com/indonesia/trademark-registration/{row["IPR_REGISTRATION_NUMBER"]}'
                row['IPR_DATABASE_URL'] = f'https://branddb.wipo.int/en/quicksearch/brand/US5020060{row["IPR_REGISTRATION_NUMBER"]}'
            elif row['IPR_JURISDICTION'] == 'MALAYSIA':
                not_parsed_tm_jurisdictions.append(jurisdiction)
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://branddb.wipo.int/en/quicksearch/brand/MY5019{row["IPR_REGISTRATION_NUMBER"]}'
                row['IPR_DATABASE_URL'] = row['IPR_LINK_TO_ONLINE_DATABASE']
            elif row['IPR_JURISDICTION'] == 'PHILIPPINES':
                not_parsed_tm_jurisdictions.append(jurisdiction)
                # Split the iprregnum string by '-' and get the last part
                iprregnum_parts = iprregnum.split('-')
                if len(iprregnum_parts) > 1:
                    iprregnum = iprregnum_parts[-1]
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://branddb.wipo.int/en/IPO-PH/quicksearch/brand/PH50004200600{iprregnum}'
                row['IPR_DATABASE_URL'] = row['IPR_LINK_TO_ONLINE_DATABASE']
            elif row['IPR_JURISDICTION'] == 'KOREA':
                not_parsed_tm_jurisdictions.append(jurisdiction)
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://branddb.wipo.int/en/advancedsearch/results?sort=score%20desc&strategy=concept&rows=30&asStructure=%7B%22_id%22:%22d36b%22,%22boolean%22:%22AND%22,%22bricks%22:%5B%7B%22_id%22:%22d36e%22,%22key%22:%22office%22,%22strategy%22:%22any_of%22,%22value%22:%5B%7B%22value%22:%22KR%22,%22label%22:%22(KR)%20KIPO%22,%22score%22:99,%22highlighted%22:%22(%3Cem%3EKR%3C%2Fem%3E)%20KIPO%22%7D%5D%7D,%7B%22_id%22:%22d36f%22,%22key%22:%22regNum%22,%22value%22:%22{iprregnum}%22%7D%5D%7D&_=1707582032071&fg=_void_'            
                row['IPR_DATABASE_URL'] = f'http://engdtj.kipris.or.kr/engdtj/grrt1000a.do?method=biblioTMFrame&masterKey={iprregnum}&index=0&kindOfReq=R&valid_fg='
            elif row['IPR_JURISDICTION'] == 'AUSTRALIA':
                not_parsed_tm_jurisdictions.append(jurisdiction)
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://branddb.wipo.int/en/advancedsearch/results?sort=score%20desc&strategy=concept&rows=30&asStructure=%7B%22_id%22:%2270d0%22,%22boolean%22:%22AND%22,%22bricks%22:%5B%7B%22_id%22:%2270d1%22,%22key%22:%22office%22,%22strategy%22:%22any_of%22,%22value%22:%5B%7B%22value%22:%22AU%22,%22label%22:%22(AU)%20IPA%22,%22score%22:99,%22highlighted%22:%22(%3Cem%3EAU%3C%2Fem%3E)%20IPA%22%7D%5D%7D,%7B%22_id%22:%2270d2%22,%22key%22:%22regNum%22,%22value%22:%22{iprregnum}%22%7D%5D%7D&_=1707838876623&fg=_void_'            
                row['IPR_DATABASE_URL'] = row['IPR_LINK_TO_ONLINE_DATABASE']
            elif row['IPR_JURISDICTION'] == 'INDIA':
                not_parsed_tm_jurisdictions.append(jurisdiction)
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://branddb.wipo.int/en/advancedsearch/results?sort=score%20desc&strategy=concept&rows=30&asStructure=%7B%22_id%22:%2270d0%22,%22boolean%22:%22AND%22,%22bricks%22:%5B%7B%22_id%22:%2270d1%22,%22key%22:%22office%22,%22strategy%22:%22any_of%22,%22value%22:%5B%7B%22value%22:%22IN%22,%22label%22:%22(IN)%20CGDPTM%22,%22score%22:99,%22highlighted%22:%22(%3Cem%3EIN%3C%2Fem%3E)%20CGDPTM%22%7D%5D%7D,%7B%22_id%22:%2270d2%22,%22key%22:%22regNum%22,%22value%22:%22{iprregnum}%22%7D%5D%7D&fg=_void_&_=1707838998374'            
                row['IPR_DATABASE_URL'] = row['IPR_LINK_TO_ONLINE_DATABASE']
            elif row['IPR_JURISDICTION'] == 'NEW ZEALAND':
                not_parsed_tm_jurisdictions.append(jurisdiction)
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://branddb.wipo.int/en/advancedsearch/results?sort=score%20desc&strategy=concept&rows=30&asStructure=%7B%22_id%22:%2270d0%22,%22boolean%22:%22AND%22,%22bricks%22:%5B%7B%22_id%22:%2270d1%22,%22key%22:%22office%22,%22strategy%22:%22any_of%22,%22value%22:%5B%7B%22value%22:%22NZ%22,%22label%22:%22(NZ)%20IPONZ%22,%22score%22:191,%22highlighted%22:%22(%3Cem%3ENZ%3C%2Fem%3E)%20IPO%3Cem%3ENZ%3C%2Fem%3E%22%7D%5D%7D,%7B%22_id%22:%2270d2%22,%22key%22:%22regNum%22,%22value%22:%22{iprregnum}%22%7D%5D%7D&fg=_void_&_=1707839070272'            
                row['IPR_DATABASE_URL'] = row['IPR_LINK_TO_ONLINE_DATABASE']
            elif row['IPR_JURISDICTION'] == 'SINGAPORE':
                not_parsed_tm_jurisdictions.append(jurisdiction)
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://branddb.wipo.int/en/advancedsearch/results?sort=score%20desc&strategy=concept&rows=30&asStructure=%7B%22_id%22:%2270d0%22,%22boolean%22:%22AND%22,%22bricks%22:%5B%7B%22_id%22:%2270d1%22,%22key%22:%22office%22,%22strategy%22:%22any_of%22,%22value%22:%5B%7B%22value%22:%22SG%22,%22label%22:%22(SG)%20IPOS%22,%22score%22:99,%22highlighted%22:%22(%3Cem%3ESG%3C%2Fem%3E)%20IPOS%22%7D%5D%7D,%7B%22_id%22:%2270d2%22,%22key%22:%22regNum%22,%22value%22:%22{iprregnum}%22%7D%5D%7D&fg=_void_&_=1707839110407'            
                row['IPR_DATABASE_URL'] = row['IPR_LINK_TO_ONLINE_DATABASE']
            elif row['IPR_JURISDICTION'] == 'BRAZIL':
                not_parsed_tm_jurisdictions.append(jurisdiction)
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://branddb.wipo.int/en/advancedsearch/results?sort=score%20desc&strategy=concept&rows=30&asStructure=%7B%22_id%22:%2270d0%22,%22boolean%22:%22AND%22,%22bricks%22:%5B%7B%22_id%22:%2270d1%22,%22key%22:%22office%22,%22strategy%22:%22any_of%22,%22value%22:%5B%7B%22value%22:%22BR%22,%22label%22:%22(BR)%20INPI%22,%22score%22:99,%22highlighted%22:%22(%3Cem%3EBR%3C%2Fem%3E)%20INPI%22%7D%5D%7D,%7B%22_id%22:%2270d2%22,%22key%22:%22regNum%22,%22value%22:%22{iprregnum}%22%7D%5D%7D&fg=_void_&_=1707839209172'            
                row['IPR_DATABASE_URL'] = row['IPR_LINK_TO_ONLINE_DATABASE']
            elif row['IPR_JURISDICTION'] == 'MEXICO':
                not_parsed_tm_jurisdictions.append(jurisdiction)
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://branddb.wipo.int/en/advancedsearch/results?sort=score%20desc&strategy=concept&rows=30&asStructure=%7B%22_id%22:%2270d0%22,%22boolean%22:%22AND%22,%22bricks%22:%5B%7B%22_id%22:%2270d1%22,%22key%22:%22office%22,%22strategy%22:%22any_of%22,%22value%22:%5B%7B%22value%22:%22MX%22,%22label%22:%22(MX)%20IMPI%22,%22score%22:99,%22highlighted%22:%22(%3Cem%3EMX%3C%2Fem%3E)%20IMPI%22%7D%5D%7D,%7B%22_id%22:%2270d2%22,%22key%22:%22regNum%22,%22value%22:%22{iprregnum}%22%7D%5D%7D&fg=_void_&_=1707839288899'            
                row['IPR_DATABASE_URL'] = row['IPR_LINK_TO_ONLINE_DATABASE']
            elif row['IPR_JURISDICTION'] == 'THAILAND':
                not_parsed_tm_jurisdictions.append(jurisdiction)
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://branddb.wipo.int/en/advancedsearch/results?sort=score%20desc&strategy=concept&rows=30&asStructure=%7B%22_id%22:%2270d0%22,%22boolean%22:%22AND%22,%22bricks%22:%5B%7B%22_id%22:%2270d1%22,%22key%22:%22office%22,%22strategy%22:%22any_of%22,%22value%22:%5B%7B%22value%22:%22TH%22,%22label%22:%22(TH)%20DIP%22,%22score%22:99,%22highlighted%22:%22(%3Cem%3ETH%3C%2Fem%3E)%20DIP%22%7D%5D%7D,%7B%22_id%22:%2270d2%22,%22key%22:%22regNum%22,%22value%22:%22{iprregnum}%22%7D%5D%7D&fg=_void_&_=1707839400499'            
                row['IPR_DATABASE_URL'] = row['IPR_LINK_TO_ONLINE_DATABASE']
            elif row['IPR_JURISDICTION'] == 'URUGUAY':
                not_parsed_tm_jurisdictions.append(jurisdiction)
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://branddb.wipo.int/en/advancedsearch/results?sort=score%20desc&strategy=concept&rows=30&asStructure=%7B%22_id%22:%2270d0%22,%22boolean%22:%22AND%22,%22bricks%22:%5B%7B%22_id%22:%2270d1%22,%22key%22:%22office%22,%22strategy%22:%22any_of%22,%22value%22:%5B%7B%22value%22:%22UY%22,%22label%22:%22(UY)%20MIEM-DNPI%22,%22score%22:99,%22highlighted%22:%22(%3Cem%3EUY%3C%2Fem%3E)%20MIEM-DNPI%22%7D%5D%7D,%7B%22_id%22:%2270d2%22,%22key%22:%22regNum%22,%22value%22:%22{iprregnum}%22%7D%5D%7D&fg=_void_&_=1707839443642'       
                row['IPR_DATABASE_URL'] = row['IPR_LINK_TO_ONLINE_DATABASE']
            elif row['IPR_JURISDICTION'] == 'VIETNAM':
                not_parsed_tm_jurisdictions.append(jurisdiction)
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://branddb.wipo.int/en/advancedsearch/results?sort=score%20desc&strategy=concept&rows=30&asStructure=%7B%22_id%22:%2270d0%22,%22boolean%22:%22AND%22,%22bricks%22:%5B%7B%22_id%22:%2270d1%22,%22key%22:%22office%22,%22strategy%22:%22any_of%22,%22value%22:%5B%7B%22value%22:%22VN%22,%22label%22:%22(VN)%20IP%20VIET%20NAM%22,%22score%22:99,%22highlighted%22:%22(%3Cem%3EVN%3C%2Fem%3E)%20IP%20VIET%20NAM%22%7D%5D%7D,%7B%22_id%22:%2270d2%22,%22key%22:%22regNum%22,%22value%22:%22{iprregnum}%22%7D%5D%7D&fg=_void_&_=1707839547809'       
                row['IPR_DATABASE_URL'] = row['IPR_LINK_TO_ONLINE_DATABASE']
            elif row['IPR_JURISDICTION'] == 'INTERNATIONAL':
                parsed_tm_jurisdictions.append(jurisdiction)
                row['IPR_LINK_TO_ONLINE_DATABASE'] = r'https://www3.wipo.int/madrid/monitor/en/showData.jsp?ID=ROM.' + row["IPR_REGISTRATION_NUMBER"]
                row['IPR_DATABASE_URL'] = row['IPR_LINK_TO_ONLINE_DATABASE']
            else:
                not_parsed_tm_jurisdictions.append(jurisdiction)
                row['IPR_LINK_TO_ONLINE_DATABASE'] = '-'  # Handle other jurisdictions if needed
            return row        
            
        elif row['IPR_TYPE'] == 'DESIGN PATENT':
            if row['IPR_JURISDICTION'] == 'EUROPE':
                parseable_design_jurisdictions.append(jurisdiction)
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://register.dpma.de/DPMAregister/gsm/registerhabm?DNR={row["IPR_REGISTRATION_NUMBER"]}'
                row['IPR_DATABASE_URL'] = f'https://euipo.europa.eu/eSearch/#details/designs/{row["IPR_REGISTRATION_NUMBER"]}'
            elif row['IPR_JURISDICTION'] == 'GERMANY':
                parseable_design_jurisdictions.append(jurisdiction)
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://register.dpma.de/DPMAregister/gsm/register?DNR={row["IPR_REGISTRATION_NUMBER"]}'
                row['IPR_DATABASE_URL'] = row['IPR_LINK_TO_ONLINE_DATABASE']
            elif row['IPR_JURISDICTION'] == 'UNITED STATES OF AMERICA' or row['IPR_JURISDICTION'] == 'UNITED STATES':
                parseable_design_jurisdictions.append(jurisdiction)
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://designdb.wipo.int/designdb/en/showData.jsp?ID=USID.{row["IPR_REGISTRATION_NUMBER"]}'
                row['IPR_DATABASE_URL'] = row['IPR_LINK_TO_ONLINE_DATABASE']
            elif row['IPR_JURISDICTION'] == "PEOPLE'S REPUBLIC OF CHINA" or row['IPR_JURISDICTION'] == "PEOPLE`S REPUBLIC OF CHINA":
                parseable_design_jurisdictions.append(jurisdiction)
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://designdb.wipo.int/designdb/en/showData.jsp?ID=CNID.{row["IPR_REGISTRATION_NUMBER"]}'
                row['IPR_DATABASE_URL'] = row['IPR_LINK_TO_ONLINE_DATABASE']  
            elif row['IPR_JURISDICTION'] == "INTERNATIONAL":
                parseable_design_jurisdictions.append(jurisdiction)
                iprregnum = iprregnum.replace('DM', 'D')
                row['IPR_LINK_TO_ONLINE_DATABASE'] = f'https://designdb.wipo.int/designdb/en/showData.jsp?ID=HAGUE.{iprregnum}'
                row['IPR_DATABASE_URL'] = row['IPR_LINK_TO_ONLINE_DATABASE']  
            else:
                row['IPR_LINK_TO_ONLINE_DATABASE'] = '-'  # Handle other jurisdictions if needed
            return row
        
        elif row['IPR_TYPE'] not in ['TRADEMARK', 'DESIGN PATENT']:
            return row

            
    # Apply the function to create 'IPR_LINK_TO_ONLINE_DATABASE' column

    
    df_import['IPR_LINK_TO_ONLINE_DATABASE'] = '-'
    df_import['IPR_JURISDICTION'] = df_import['IPR_JURISDICTION'].str.upper()
    df_import['IPR_JURISDICTION'] = df_import['IPR_JURISDICTION'].str.replace('MAINLAND CHINA', "PEOPLE'S REPUBLIC OF CHINA", regex=False)
    df_import['IPR_JURISDICTION'] = df_import['IPR_JURISDICTION'].str.replace('WIPO', 'INTERNATIONAL', regex=False)
    df_import['IPR_JURISDICTION'] = df_import['IPR_JURISDICTION'].str.replace('GLOBAL', 'INTERNATIONAL', regex=False)

    df_combined = df_import.apply(create_ipr_url, axis=1)
    df_combined = df_combined.dropna(subset=['IPR'])

    # st.write('DF IPR_LINK_TO_ONLINE_DATABASE GENERATOR')
    st.write(df_combined)
    
    # Convert parsed_tm_jurisdictions to a set to remove duplicates
    parsed_tm_jurisdictions = set(parsed_tm_jurisdictions)
    # Convert the set back to a list if needed
    parsed_tm_jurisdictions = list(parsed_tm_jurisdictions)
    
    # Convert not_parsed_tm_jurisdictions to a set to remove duplicates
    not_parsed_tm_jurisdictions = set(not_parsed_tm_jurisdictions)
    # Convert the set back to a list if needed
    not_parsed_tm_jurisdictions = list(not_parsed_tm_jurisdictions)
    
    # Convert parseable_design_jurisdictions to a set to remove duplicates
    parseable_design_jurisdictions = set(parseable_design_jurisdictions)
    # Convert the set back to a list if needed
    parseable_design_jurisdictions = list(parseable_design_jurisdictions)

 
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
    def fetch_html_content(url, timeout=500):
   #     try:
    #        response = requests.get(url, timeout=timeout)
    #        if response.status_code == 200:
    #            return response.text  # Return the HTML content as a string
    #        else:
    #            return f"Failed to fetch HTML content from {url}"
    #    except requests.exceptions.RequestException as e:
    #        return f"An error occurred: {e}"

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
            time.sleep(5)  # Delay for 5 seconds

            response = requests.get(url, headers=headers, timeout=timeout)
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

    
    # Function to fetch HTML content and extract a specific section
    def eu_extract_section_from_url(url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                # Parse the HTML content
                soup = BeautifulSoup(response.text, 'html.parser')
                # Find the section containing the table
                section = soup.find('div', id='tbl_Containing')
                if section:
                    return section.prettify()  # Return the entire section with formatting
                else:
                    return None
            else:
                print("Error: Unable to retrieve URL - Status code:", response.status_code)
                return None
        except Exception as e:
            print("Error occurred:", e)
            return None

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
            elif 'INDONESIA' in jurisdiction:
                html_content = fetch_html_content(url, timeout=200)            
            elif 'EUROPE' in jurisdiction:
                html_content = fetch_html_content(url, timeout=200)            
            elif 'GERMANY' in jurisdiction:
                html_content = fetch_html_content(url, timeout=200)      
            elif 'UNITED KINGDOM' in jurisdiction:
                html_content = fetch_html_content(url, timeout=200)            
            else:
                html_content = '-'
            if html_content:
                # Assign the HTML content to df_combined['HTML']
                df_combined.at[index, 'HTML'] = html_content
                
    st.header(f"IPRs Analyzed: {urlcount}")

    
    trademarks_df = df_combined[df_combined['IPR_TYPE'] == 'TRADEMARK']
    copyright_df = df_combined[df_combined['IPR_TYPE'] == 'COPYRIGHT']
    design_patents_df = df_combined[df_combined['IPR_TYPE'] == 'DESIGN PATENT']
    invention_patents_df = df_combined[df_combined['IPR_TYPE'] == 'INVENTION PATENT']    
    
    # Filter df_combined based on the list of exclude_values
    all_others_tm_rows = trademarks_df[trademarks_df['IPR_JURISDICTION'].isin(not_parsed_tm_jurisdictions)]
    all_others_design_rows = design_patents_df[~design_patents_df['IPR_JURISDICTION'].isin(parseable_design_jurisdictions)]
    
    # Combine the unparseable DataFrames
    all_other_iprs = pd.concat([all_others_tm_rows, all_others_design_rows, copyright_df, invention_patents_df])
    # Reset the index of the combined DataFrame
    all_other_iprs.reset_index(drop=True, inplace=True)
    
    st.write('ALL OTHER IPR')
    st.write(all_other_iprs)
    
    design_patents_df_eu_rows = design_patents_df[design_patents_df['IPR_JURISDICTION'].isin(['EUROPE', 'GERMANY'])]
    design_patents_df_us_rows = design_patents_df[design_patents_df['IPR_JURISDICTION'].str.contains('UNITED STATES')]
    design_patents_df_cn_rows = design_patents_df[design_patents_df['IPR_JURISDICTION'].str.contains('CHINA')]
    design_patents_df_int_rows = design_patents_df[design_patents_df['IPR_JURISDICTION'].isin(['INTERNATIONAL'])]
   
    parsed_designs_jurisdictions.append(design_patents_df_eu_rows['IPR_JURISDICTION'])
    st.write(parsed_designs_jurisdictions)
    
    design_patents_df_eu_rows['IPR_REG_NAME'] = design_patents_df_eu_rows['HTML'].str.split(r'<td data-th="Kriterium">Wortlaut der Marke</td>').str[1]
    design_patents_df_eu_rows['IPR_REG_NAME'] = design_patents_df_eu_rows['IPR_REG_NAME'].fillna('-')
    design_patents_df_eu_rows['IPR_REG_NAME'] = design_patents_df_eu_rows['IPR_REG_NAME'].str.split(r'</td></tr><tr><td data-th="INID">').str[0]
    design_patents_df_eu_rows['IPR_REG_NAME'] = design_patents_df_eu_rows['IPR_REG_NAME'].fillna('-')
    design_patents_df_eu_rows['IPR_REG_NAME'] = design_patents_df_eu_rows['IPR_REG_NAME'].str.split(r'"Inhalt">').str[1]

    design_patents_df_eu_rows['IPR_HOLDER'] = design_patents_df_eu_rows['HTML'].str.split(r'<td data-th="Kriterium">Inhaber</td>').str[1]
    design_patents_df_eu_rows['IPR_HOLDER'] = design_patents_df_eu_rows['IPR_HOLDER'].str.split(r'</td></tr><tr><td data-th="INID">').str[0]
    design_patents_df_eu_rows['IPR_HOLDER'] = design_patents_df_eu_rows['IPR_HOLDER'].str.split(r'"Inhalt">').str[1]
    design_patents_df_eu_rows['IPR_HOLDER'] = design_patents_df_eu_rows['IPR_HOLDER'].str.replace(r'&amp;', '&', regex=False)
    
    design_patents_df_eu_rows['IPR_REGISTRATION_DATE'] = design_patents_df_eu_rows['HTML'].str.split(r'<td data-th="Kriterium">Anmeldetag</td>').str[1]
    design_patents_df_eu_rows['IPR_REGISTRATION_DATE'] = design_patents_df_eu_rows['IPR_REGISTRATION_DATE'].str.split(r'</td></tr><tr><td data-th="INID">').str[0]
    design_patents_df_eu_rows['IPR_REGISTRATION_DATE'] = design_patents_df_eu_rows['IPR_REGISTRATION_DATE'].str.split(r'Inhalt">').str[1]
        
    design_patents_df_eu_rows['IPR_EXPIRATION_DATE'] = design_patents_df_eu_rows['HTML'].str.split(r'<td data-th="Kriterium">Ablaufdatum</td>').str[1]
    design_patents_df_eu_rows['IPR_EXPIRATION_DATE'] = design_patents_df_eu_rows['IPR_EXPIRATION_DATE'].str.split(r'</td></tr><tr><td data-th="INID">').str[0]
    design_patents_df_eu_rows['IPR_EXPIRATION_DATE'] = design_patents_df_eu_rows['IPR_EXPIRATION_DATE'].str.split(r'Inhalt">').str[1]

    
    html_snippets = design_patents_df_eu_rows['HTML'].str.split(r'class="dpma-link-galerie-item"><img aria-label=', n=1).str[1]
    # Extract all .jpg images from each HTML snippet using regex
    jpg_images = html_snippets.str.findall(r'src="([^"]+\.jpg)"')
    # Join the lists of images with ';' for each row
    design_patents_df_eu_rows['IPR_IMAGE_URL'] = jpg_images.str.join('; ')

    design_patents_df_eu_rows['IPR_NICE_CLASSES_ALL'] = design_patents_df_eu_rows['HTML'].str.split(r'<td data-th="Kriterium">Anmeldetag</td>').str[1]
    design_patents_df_eu_rows['IPR_NICE_CLASSES_ALL'] = design_patents_df_eu_rows['IPR_NICE_CLASSES_ALL'].str.split('Klasse\(n\)').str[1]
    design_patents_df_eu_rows['IPR_NICE_CLASSES_ALL'] = design_patents_df_eu_rows['IPR_NICE_CLASSES_ALL'].str.split(r'</td></tr><tr><td data-th="INID">').str[0]
    design_patents_df_eu_rows['IPR_NICE_CLASSES_ALL'] = design_patents_df_eu_rows['IPR_NICE_CLASSES_ALL'].str.split(r'Inhalt">').str[1]

    design_patents_df_eu_rows['IPR_STATUS'] = design_patents_df_eu_rows['HTML'].str.split(r'<td data-th="Kriterium">Aktenzustand Unionsmarken</td>').str[1]
    design_patents_df_eu_rows['IPR_STATUS'] = design_patents_df_eu_rows['IPR_STATUS'].fillna('-')
    design_patents_df_eu_rows['IPR_STATUS'] = design_patents_df_eu_rows['IPR_STATUS'].str.split(r'</td></tr><tr><td data-th="INID">').str[0]
    design_patents_df_eu_rows['IPR_STATUS'] = design_patents_df_eu_rows['IPR_STATUS'].str.split(r'Inhalt">').str[1]

    # Filter rows where 'IPR_JURISDICTION' contains 'UNITED STATES'
    trademarks_df_us_rows = trademarks_df[trademarks_df['IPR_JURISDICTION'].str.contains('UNITED STATES')]
   
    # Filter rows where 'IPR_JURISDICTION' contains 'UNITED KINGDOM'
    trademarks_df_uk_rows = trademarks_df[trademarks_df['IPR_JURISDICTION'].str.contains('UNITED KINGDOM')]
    st.write(trademarks_df_uk_rows)   
    
    # Filter rows where 'IPR_JURISDICTION' contains 'EUROPE'
    trademarks_df_eu_rows = trademarks_df[trademarks_df['IPR_JURISDICTION'].isin(['EUROPE', 'GERMANY'])]
    st.write(trademarks_df_eu_rows)   
    # trademarks_df_eu_rows['HTML'] = trademarks_df_eu_rows['HTML'].str.split(r'<td data-th="Kriterium">Markendarstellung</td>').str[1]
        
    trademarks_df_eu_rows['IPR_REG_NAME'] = trademarks_df_eu_rows['HTML'].str.split(r'<td data-th="Kriterium">Wortlaut der Marke</td>').str[1]
    trademarks_df_eu_rows['IPR_REG_NAME'] = trademarks_df_eu_rows['IPR_REG_NAME'].fillna('-')
    trademarks_df_eu_rows['IPR_REG_NAME'] = trademarks_df_eu_rows['IPR_REG_NAME'].str.split(r'</td></tr><tr><td data-th="INID">').str[0]
    trademarks_df_eu_rows['IPR_REG_NAME'] = trademarks_df_eu_rows['IPR_REG_NAME'].fillna('-')
    trademarks_df_eu_rows['IPR_REG_NAME'] = trademarks_df_eu_rows['IPR_REG_NAME'].str.split(r'"Inhalt">').str[1]

    trademarks_df_eu_rows['IPR_HOLDER'] = trademarks_df_eu_rows['HTML'].str.split(r'<td data-th="Kriterium">Inhaber</td>').str[1]
    trademarks_df_eu_rows['IPR_HOLDER'] = trademarks_df_eu_rows['IPR_HOLDER'].fillna('-')
    trademarks_df_eu_rows['IPR_HOLDER'] = trademarks_df_eu_rows['IPR_HOLDER'].str.split(r'</td></tr><tr><td data-th="INID">').str[0]
    trademarks_df_eu_rows['IPR_HOLDER'] = trademarks_df_eu_rows['IPR_HOLDER'].fillna('-')
    trademarks_df_eu_rows['IPR_HOLDER'] = trademarks_df_eu_rows['IPR_HOLDER'].str.split(r'"Inhalt">').str[1]
    trademarks_df_eu_rows['IPR_HOLDER'] = trademarks_df_eu_rows['IPR_HOLDER'].fillna('-')
    trademarks_df_eu_rows['IPR_HOLDER'] = trademarks_df_eu_rows['IPR_HOLDER'].str.replace(r'&amp;', '&', regex=False)
    
    trademarks_df_eu_rows['IPR_REGISTRATION_DATE'] = trademarks_df_eu_rows['HTML'].str.split(r'<td data-th="Kriterium">Anmeldetag</td>').str[1]
    trademarks_df_eu_rows['IPR_REGISTRATION_DATE'] = trademarks_df_eu_rows['IPR_REGISTRATION_DATE'].str.split(r'</td></tr><tr><td data-th="INID">').str[0]
    trademarks_df_eu_rows['IPR_REGISTRATION_DATE'] = trademarks_df_eu_rows['IPR_REGISTRATION_DATE'].str.split(r'Inhalt">').str[1]
        
    trademarks_df_eu_rows['IPR_EXPIRATION_DATE'] = trademarks_df_eu_rows['HTML'].str.split(r'<td data-th="Kriterium">Ablaufdatum</td>').str[1]
    trademarks_df_eu_rows['IPR_EXPIRATION_DATE'] = trademarks_df_eu_rows['IPR_EXPIRATION_DATE'].str.split(r'</td></tr><tr><td data-th="INID">').str[0]
    trademarks_df_eu_rows['IPR_EXPIRATION_DATE'] = trademarks_df_eu_rows['IPR_EXPIRATION_DATE'].str.split(r'Inhalt">').str[1]

    
    trademarks_df_eu_rows['IPR_IMAGE_URL'] = trademarks_df_eu_rows['HTML'].str.split(r'<img src="').str[1]
    trademarks_df_eu_rows['IPR_IMAGE_URL'] = trademarks_df_eu_rows['IPR_IMAGE_URL'].fillna('-')
    trademarks_df_eu_rows['IPR_IMAGE_URL'] = trademarks_df_eu_rows['IPR_IMAGE_URL'].str.split(r'" alt="').str[0]
    
    trademarks_df_eu_rows['IPR_NICE_CLASSES_ALL'] = trademarks_df_eu_rows['HTML'].str.split(r'<td data-th="Kriterium">Anmeldetag</td>').str[1]
    trademarks_df_eu_rows['IPR_NICE_CLASSES_ALL'] = trademarks_df_eu_rows['IPR_NICE_CLASSES_ALL'].str.split('Klasse\(n\)').str[1]
    trademarks_df_eu_rows['IPR_NICE_CLASSES_ALL'] = trademarks_df_eu_rows['IPR_NICE_CLASSES_ALL'].str.split(r'</td></tr><tr><td data-th="INID">').str[0]
    trademarks_df_eu_rows['IPR_NICE_CLASSES_ALL'] = trademarks_df_eu_rows['IPR_NICE_CLASSES_ALL'].str.split(r'Inhalt">').str[1]

    trademarks_df_eu_rows['IPR_STATUS'] = trademarks_df_eu_rows['HTML'].str.split(r'<td data-th="Kriterium">Aktenzustand Unionsmarken</td>').str[1]
    trademarks_df_eu_rows['IPR_STATUS'] = trademarks_df_eu_rows['IPR_STATUS'].str.split(r'</td></tr><tr><td data-th="INID">').str[0]
    trademarks_df_eu_rows['IPR_STATUS'] = trademarks_df_eu_rows['IPR_STATUS'].str.split(r'Inhalt">').str[1]



    # st.write(trademarks_df_eu_rows)    
    
    # Filter rows where 'IPR_JURISDICTION' is equal to 'INDONESIA'
    trademarks_df_indo_rows = trademarks_df[trademarks_df['IPR_JURISDICTION'] == "INDONESIA"]
    st.write(trademarks_df_indo_rows)
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
    # trademarks_df_indo_rows['IPR_EXPIRATION_DATE'] = trademarks_df_indo_rows['IPR_EXPIRATION_DATE'].apply(lambda x: datetime.strptime(x, '%a, %d %b %Y').strftime('%Y-%m-%d'))
    # trademarks_df_indo_rows['IPR_REGISTRATION_DATE'] = trademarks_df_indo_rows['IPR_REGISTRATION_DATE'].apply(lambda x: datetime.strptime(x, '%a, %d %b %Y').strftime('%Y-%m-%d'))
    
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
    trademarks_df_cn_rows['IPR_EXPIRATION_DATE'] = trademarks_df_cn_rows['IPR_EXPIRATION_DATE'].fillna("-")
    trademarks_df_cn_rows['IPR_EXPIRATION_DATE'] = trademarks_df_cn_rows['IPR_EXPIRATION_DATE'].str.split(r'</div>').str[0]
    trademarks_df_cn_rows['IPR_EXPIRATION_DATE'] = trademarks_df_cn_rows['IPR_EXPIRATION_DATE'].str.split(r'至').str[1]
    
    trademarks_df_cn_rows['IPR_TYPEhtml'] = trademarks_df_cn_rows['HTML'].str.split(r'商标类型').str[1]
    trademarks_df_cn_rows['IPR_TYPEhtml'] = trademarks_df_cn_rows['IPR_TYPEhtml'].fillna("-")
    trademarks_df_cn_rows['IPR_TYPEhtml'] = trademarks_df_cn_rows['IPR_TYPEhtml'].str.split(r'类似群组').str[0]
    trademarks_df_cn_rows['IPR_TYPEhtml'] = trademarks_df_cn_rows['IPR_TYPEhtml'].str.split(r'">').str[1]
    trademarks_df_cn_rows['IPR_TYPEhtml'] = trademarks_df_cn_rows['IPR_TYPEhtml'].fillna("-")
    trademarks_df_cn_rows['IPR_TYPEhtml'] = trademarks_df_cn_rows['IPR_TYPEhtml'].str.split(r'</div>').str[0]

    trademarks_df_cn_rows['IPR_SUBCLASSES'] = trademarks_df_cn_rows['HTML'].str.split(r'类似群组').str[1]
    trademarks_df_cn_rows['IPR_SUBCLASSES'] = trademarks_df_cn_rows['IPR_SUBCLASSES'].fillna("-")
    trademarks_df_cn_rows['IPR_SUBCLASSES'] = trademarks_df_cn_rows['IPR_SUBCLASSES'].str.split(r'适用商品服务').str[0]
    trademarks_df_cn_rows['IPR_SUBCLASSES'] = trademarks_df_cn_rows['IPR_SUBCLASSES'].str.split(r'FvDQAhY').str[1]
    trademarks_df_cn_rows['IPR_SUBCLASSES'] = trademarks_df_cn_rows['IPR_SUBCLASSES'].fillna("-")
    trademarks_df_cn_rows['IPR_SUBCLASSES'] = trademarks_df_cn_rows['IPR_SUBCLASSES'].str.split(r'<').str[0]
    trademarks_df_cn_rows['IPR_SUBCLASSES'] = trademarks_df_cn_rows['IPR_SUBCLASSES'].str.replace(r'">', '', regex=False)

    trademarks_df_cn_rows['IPR_SUBCLASSESdetails'] = trademarks_df_cn_rows['HTML'].str.split(r'适用商品服务').str[1]
    trademarks_df_cn_rows['IPR_SUBCLASSESdetails'] = trademarks_df_cn_rows['IPR_SUBCLASSESdetails'].fillna("-")
    trademarks_df_cn_rows['IPR_SUBCLASSESdetails'] = trademarks_df_cn_rows['IPR_SUBCLASSESdetails'].str.split(r'<div class=""liYyg7LN"">').str[0]
    trademarks_df_cn_rows['IPR_SUBCLASSESdetails'] = trademarks_df_cn_rows['IPR_SUBCLASSESdetails'].str.replace(r'</div><div class="aFvDQAhY">', '; ', regex=False)
    trademarks_df_cn_rows['IPR_SUBCLASSESdetails'] = trademarks_df_cn_rows['IPR_SUBCLASSESdetails'].str.replace(r'<!-- -->-<!-- -->', ': ', regex=False)
    trademarks_df_cn_rows['IPR_SUBCLASSESdetails'] = trademarks_df_cn_rows['IPR_SUBCLASSESdetails'].str.split(r'"aFvDQAhY">').str[1]
    trademarks_df_cn_rows['IPR_SUBCLASSESdetails'] = trademarks_df_cn_rows['IPR_SUBCLASSESdetails'].fillna("-")
    trademarks_df_cn_rows['IPR_SUBCLASSESdetails'] = trademarks_df_cn_rows['IPR_SUBCLASSESdetails'].str.split(r'<div').str[0]
    trademarks_df_cn_rows['IPR_SUBCLASSESdetails'] = trademarks_df_cn_rows['IPR_SUBCLASSESdetails'].str.split(r'</div></div></div>').str[0]
    
    trademarks_df_cn_rows['IPR_HOLDER'] = trademarks_df_cn_rows['HTML'].str.split(r'申请人</div><div class="').str[1]
    trademarks_df_cn_rows['IPR_HOLDER'] = trademarks_df_cn_rows['IPR_HOLDER'].fillna("-")
    trademarks_df_cn_rows['IPR_HOLDER'] = trademarks_df_cn_rows['IPR_HOLDER'].str.split(r'申请人地址</div>').str[0]
    trademarks_df_cn_rows['IPR_HOLDER'] = trademarks_df_cn_rows['IPR_HOLDER'].fillna("-")
    trademarks_df_cn_rows['IPR_HOLDER'] = trademarks_df_cn_rows['IPR_HOLDER'].str.split(r'</div>').str[0]
    trademarks_df_cn_rows['IPR_HOLDER'] = trademarks_df_cn_rows['IPR_HOLDER'].str.split(r'">').str[1]
    trademarks_df_cn_rows['IPR_HOLDER'] = trademarks_df_cn_rows['IPR_HOLDER'].fillna("-")
    trademarks_df_cn_rows['IPR_HOLDER'] = trademarks_df_cn_rows['IPR_HOLDER'].str.replace(r'amp;', '')


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
        df_data = extract_data_int(url)
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
    trademarks_df_int_rows['IPR_IMAGE_URL'] = trademarks_df_int_rows['IPR_IMAGE_URL'].fillna('-')

    trademarks_df_int_rows['IPR_IMAGE_URL'] = trademarks_df_int_rows['IPR_IMAGE_URL'].str.split(r'" src="..').str[1]
    trademarks_df_int_rows['IPR_IMAGE_URL'] = trademarks_df_int_rows['IPR_IMAGE_URL'].fillna('-')
    trademarks_df_int_rows['IPR_IMAGE_URL'] = trademarks_df_int_rows['IPR_IMAGE_URL'].str.split(r'" style').str[0]
    trademarks_df_int_rows['IPR_IMAGE_URL'] = trademarks_df_int_rows['IPR_IMAGE_URL'].fillna('-')
    trademarks_df_int_rows['IPR_IMAGE_URL'] = trademarks_df_int_rows['IPR_IMAGE_URL'].str.replace(r'/jsp/', 'https://www3.wipo.int/madrid/monitor/jsp/', regex=False)
    trademarks_df_int_rows['IPR_IMAGE_URL'] = trademarks_df_int_rows['IPR_IMAGE_URL'].fillna('-')
    trademarks_df_int_rows['IPR_IMAGE_URL'] = trademarks_df_int_rows['IPR_IMAGE_URL'].str.replace(r'amp;', '', regex=False)

    trademarks_df_int_rows['IPR_REG_NAME'] = trademarks_df_int_rows['HTML'].str.split(r'markname"').str[1]
    trademarks_df_int_rows['IPR_REG_NAME'] = trademarks_df_int_rows['IPR_REG_NAME'].str.split(r'</h3> </td> <td> <div class').str[0]
    trademarks_df_int_rows['IPR_REG_NAME'] = trademarks_df_int_rows['IPR_REG_NAME'].str.split(r'-').str[1]
    trademarks_df_int_rows['IPR_REG_NAME'] = trademarks_df_int_rows['IPR_REG_NAME'].str.split(r'<').str[0]

    trademarks_df_int_rows['IPR_STATUS'] = trademarks_df_int_rows['HTML'].str.split(r'status="').str[1]
    trademarks_df_int_rows['IPR_STATUS'] = trademarks_df_int_rows['IPR_STATUS'].str.split(r'">  </div> </td').str[0]
    trademarks_df_int_rows['IPR_STATUS'] = trademarks_df_int_rows['IPR_STATUS'].str.split(r'">').str[0]

    

    trademarks_df = pd.concat([trademarks_df_int_rows, trademarks_df_cn_rows, trademarks_df_indo_rows, trademarks_df_eu_rows, trademarks_df_us_rows, trademarks_df_uk_rows], ignore_index=True)
    # st.write(trademarks_df)
    design_patents_df = pd.concat([design_patents_df_eu_rows, design_patents_df_us_rows, design_patents_df_cn_rows, design_patents_df_int_rows], ignore_index=True)
    # st.write(trademarks_df)
    
    # Re-concatenate the DataFrames to create df_combined
    df_combined = pd.concat([trademarks_df, design_patents_df, all_other_iprs], ignore_index=True)
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
    st.write('COPYA DF COMBINED') 
    st.write(df_combined_copy)
    
    # Drop the 'HTML' column
    df_combined.drop(columns=['HTML'], inplace=True)
    
    
    # Reorder the columns
    new_column_order = ['id', 'IPR', 'IPR_TYPE', 'IPR_TRADEMARK_TYPE', 'IPR_IMAGE_URL', 'IPR_JURISDICTION', 
                        'IPR_NICE_CLASS', 'IPR_REGISTRATION_DATE', 'IPR_EXPIRATION_DATE', 'IPR_DATABASE_URL', 'IPR_HOLDER', 'IPR_NICE_CLASSES_ALL',  
                        'IPR_REGISTRATION_NUMBER', 'IPR_DESIGNATIONS', 'NOTES', 'IPR_REG_NAME2', 'IPR_REG_NAME', 
                        'IPR_STATUS', 'IPR_TYPEhtml', 'IPR_SUBCLASSES', 
                        'IPR_SUBCLASSESdetails', 'IPR_LINK_TO_ONLINE_DATABASE']


    df_combined = df_combined.reindex(columns=new_column_order)

    st.title("Data Analysis")
    st.write(df_combined)

    df_import_second = pd.read_excel(xlsx_file)
    df_import_second = df_import_second.drop_duplicates(subset='IPR')
    df_import_second = df_import_second.reset_index(drop=True)
    # Add '_originaldb' suffix to all columns in df_import_second
    df_import_second = df_import_second.add_suffix('_originaldb')
    # Merge combined_df with df_import_second based on the 'IPR' column in the first and 'IPR_originaldb' in the second
    merged_df = pd.merge(df_combined, df_import_second, left_on='IPR', right_on='IPR_originaldb', how='inner')
    st.write(merged_df)

    # Add a download link for df_combined
    st.sidebar.markdown("### Download Processed Data")
    xlsx_download_link = create_download_link(merged_df, "IPR Info Export.xlsx", "-> Download Excel <-")
    st.markdown(xlsx_download_link, unsafe_allow_html=True)



# Streamlit UI
st.title("Trademark Data Analysis")

# Upload an XLSX file
xlsx_file = st.sidebar.file_uploader("Upload an XLSX file", type=["xlsx"], accept_multiple_files=False)

if xlsx_file:
    df_import = process_xlsx_file(xlsx_file)
    # st.dataframe(df_import)
