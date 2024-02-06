import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from extract_data_html import extract_data_int

# Function to process the uploaded XLSX file
def process_xlsx_files(xlsx_files):
    df_import = pd.DataFrame()  # Initialize an empty DataFrame to store the combined data

    for xlsx_file in xlsx_files:
        df = pd.read_excel(xlsx_file, usecols=['IPR', 'PRODUCT_CATEGORY'])  # Read only selected columns
        df_import = pd.concat([df_import, df], ignore_index=True)  # Concatenate the DataFrames

    # Remove duplicates based on the 'IPR' column
    df_import = df_import.drop_duplicates(subset='IPR')
    # Reset the index of the combined DataFrame
    df_import = df_import.reset_index(drop=True)



    # Function to classify IPR_TYPE and modify IPR_fixed
    def classify_ipr(row):
        if 'DESIGN PATENT' in row['IPR']:
            row['IPR_TYPE'] = 'DESIGN PATENT'
            row['IPR_fixed'] = row['IPR'].replace('. N° ', '/').replace(' n. ', '/')
        elif '. N° ' in row['IPR'] or ' n. ' in row['IPR']:
            row['IPR_TYPE'] = 'TRADEMARK'
            row['IPR_fixed'] = row['IPR'].replace('. N° ', '/').replace(' n. ', '/')
        else:
            row['IPR_TYPE'] = 'OTHER IPR'  # Handle other cases if needed
        return row



    # Create 'IPR_URL' for trademarks based on 'IPR_JURISDICTION' and 'IPR_REG_N'
    def create_ipr_url_trademarks(row):
        if row['IPR_JURISDICTION'] == 'EU':
            row['IPR_URL'] = f'https://www.tmdn.org/tmview/welcome#/tmview/detail/EM5000000{row["IPR_REG_N"]}'
        elif row['IPR_JURISDICTION'] == 'US':
            row['IPR_URL'] = f'https://tsdr.uspto.gov/#caseNumber={row["IPR_REG_N"]}&caseSearchType=US_APPLICATION&caseType=SERIAL_NO&searchType=statusSearch'
        elif row['IPR_JURISDICTION'] == 'CN':
            iprclass = row['IPR_NICE_CLASS']
            row['IPR_URL'] = f'https://cloud.baidu.com/product/tms/detail?keyword={row["IPR_REG_N"]}&keywordType=registrationNumber&registrationNumber={row["IPR_REG_N"]}&firstCode={iprclass}'
        elif row['IPR_JURISDICTION'] == 'ID':
            row['IPR_URL'] = f'https://www.jumbomark.com/indonesia/trademark-registration/{row["IPR_REG_N"]}'
        elif row['IPR_JURISDICTION'] == 'INT TM':
            row['IPR_URL'] = r'https://www3.wipo.int/madrid/monitor/en/showData.jsp?ID=ROM.' + row["IPR_REG_N"]
        else:
            row['IPR_URL'] = None  # Handle other jurisdictions if needed
        return row

    # Create 'IPR_URL' for design patents based on 'IPR_JURISDICTION' and 'IPR_REG_N'
    def create_ipr_url_design_patents(row):
        if row['IPR_JURISDICTION'] == 'EU':
            row['IPR_URL'] = f'https://www.tmdn.org/tmview/welcome#/tmview/detail/EM5000000{row["IPR_REG_N"]}'
        elif row['IPR_JURISDICTION'] == 'US':
            row['IPR_URL'] = f'https://tsdr.uspto.gov/#caseNumber={row["IPR_REG_N"]}&caseSearchType=US_APPLICATION&caseType=SERIAL_NO&searchType=statusSearch'
        elif row['IPR_JURISDICTION'] == 'CN':
            iprclass = row['IPR_NICE_CLASS']
            row['IPR_URL'] = f'https://cloud.baidu.com/product/tms/detail?keyword=45059080&keywordType=registrationNumber&registrationNumber={row["IPR_REG_N"]}&firstCode={iprclass}'
        elif row['IPR_JURISDICTION'] == 'ID':
            row['IPR_URL'] = f'https://www.jumbomark.com/indonesia/trademark-registration/{row["IPR_REG_N"]}'
        else:
            row['IPR_URL'] = None  # Handle other jurisdictions if needed
        return row

    # Apply the classification function
    df_import = df_import.apply(classify_ipr, axis=1)
    st.write('DF IMPORT')
    st.write(df_import)
    # Create 'trademarks_df' and 'nottrademarks_df'
    trademarks_df = df_import[df_import['IPR_TYPE'] == 'TRADEMARK']
    nottrademarks_df = df_import[df_import['IPR_TYPE'] == 'OTHER IPR']
    design_patents_df = df_import[df_import['IPR_TYPE'] == 'DESIGN PATENT']


#----------------------------------------------------------------------------
#                                TRADEMARKS
#----------------------------------------------------------------------------
    # Extract 'IPR_JURISDICTION' and 'IPR_REG_N' from 'IPR_fixed'
    trademarks_df['IPR_JURISDICTION'] = trademarks_df['IPR_fixed'].str.split(r'/').str[0]
    trademarks_df['IPR_REG_N'] = trademarks_df['IPR_fixed'].str.split(r'/').str[1]
    trademarks_df['IPR_REG_N'] = trademarks_df['IPR_REG_N'].str.split(r' - ').str[0]
    split_data = trademarks_df['IPR_fixed'].str.split(' - ', n=2, expand=True)
    # Extract 'IPR_NAME' from 'IPR_fixed' between the first and the second ' - '    
    trademarks_df['IPR_NAME'] = split_data[1]
    # Extract 'IPR_Classes' from 'IPR_fixed' after the second ' - '
    trademarks_df['IPR_NICE_CLASS'] = split_data[2]
    trademarks_df['IPR_NICE_CLASS'] = trademarks_df['IPR_NICE_CLASS'].str.split(r'Cl. ').str[1]
    trademarks_df['IPR_NICE_CLASS'] = trademarks_df['IPR_NICE_CLASS'].str.replace(r' ', '', regex=False)

    # Apply the function to create 'IPR_URL' column
    trademarks_df = trademarks_df.apply(create_ipr_url_trademarks, axis=1)
    st.write('DF TRADEMARK - MAIN INFO EXTRACTED FROM EXCEL + IPR_URL GENERATOR')
    st.write(trademarks_df)

#----------------------------------------------------------------------------
#                             DESIGN PATENTS
#----------------------------------------------------------------------------
    # Extract 'IPR_JURISDICTION' and 'IPR_REG_N' from 'IPR_fixed'
    design_patents_df['IPR_JURISDICTION'] = design_patents_df['IPR_fixed'].str.split(r'/').str[0]
    design_patents_df['IPR_REG_N'] = design_patents_df['IPR_fixed'].str.split(r'/').str[1]
    design_patents_df['IPR_REG_N'] = design_patents_df['IPR_REG_N'].str.split(r' -').str[0]
    # Extract 'IPR_NAME' from 'IPR_fixed' between the first and the second ' - '    
    design_patents_df['IPR_NAME'] = design_patents_df['IPR_fixed'].str.split(r'PATENT - ').str[1]
    # Extract 'IPR_Classes' from 'IPR_fixed' after the second ' - '
    design_patents_df['IPR_NICE_CLASS'] = split_data[2]
    # Apply the function to create 'IPR_URL' column
    design_patents_df = design_patents_df.apply(create_ipr_url_design_patents, axis=1)

    st.write('DF DESIGN PATENT - MAIN INFO EXTRACTED FROM EXCEL')
    st.write(design_patents_df)
    st.write('DF OTHER IPRs')
    st.write(nottrademarks_df)

    # Concatenate the DataFrames to create df_combined
    df_combined = pd.concat([trademarks_df, design_patents_df, nottrademarks_df], ignore_index=True)
    # Reset the index of the combined DataFrame
    df_combined = df_combined.reset_index(drop=True)

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



    # Streamlit UI
    st.title("HTML Source Code of IPR URLs")
    df_combined['HTML'] = ""

    for index, row in df_combined.iterrows():
        url = row['IPR_URL']
        jurisdiction = row['IPR_JURISDICTION']
        if pd.notna(url):
            st.header(f"URL: {url}")
            if "PEOPLE'S REPUBLIC OF CHINA" in jurisdiction:  # Check if 'CN' is present in the JURISDICTION
                html_content = cn_extract_section_from_url(url)
            elif 'INTERNATIONAL' in jurisdiction:
                html_content = int_extract_section_from_url(url)
                # st.write(html_content)

            else:
                html_content = fetch_html_content(url, timeout=50)
            if html_content:
                # Assign the HTML content to df_combined['HTML']
                df_combined.at[index, 'HTML'] = html_content

    # Re-create 'trademarks_df', 'design_patents_df' and 'nottrademarks_df'
    trademarks_df = df_combined[df_combined['IPR_TYPE'] == 'TRADEMARK']
    nottrademarks_df = df_combined[df_combined['IPR_TYPE'] == 'OTHER IPR']
    design_patents_df = df_combined[df_combined['IPR_TYPE'] == 'DESIGN PATENT']
    




    # Filter rows where 'IPR_JURISDICTION' is equal to 'CN'
    trademarks_df_cn_rows = trademarks_df[trademarks_df['IPR_JURISDICTION'] == 'CN']
    trademarks_df_cn_rows['IPR_IMAGE'] = trademarks_df_cn_rows['HTML'].str.split(r'<img class=').str[1]
    trademarks_df_cn_rows['IPR_IMAGE'] = trademarks_df_cn_rows['IPR_IMAGE'].str.split(r'" src="').str[1]
    trademarks_df_cn_rows['IPR_IMAGE'] = trademarks_df_cn_rows['IPR_IMAGE'].str.split(r'"/>').str[0]
    
    trademarks_df_cn_rows['IPR_NAMEhtml'] = trademarks_df_cn_rows['HTML'].str.split(r'商标名称').str[1]
    trademarks_df_cn_rows['IPR_NAMEhtml'] = trademarks_df_cn_rows['IPR_NAMEhtml'].str.split(r'商标分类').str[0]
    trademarks_df_cn_rows['IPR_NAMEhtml'] = trademarks_df_cn_rows['IPR_NAMEhtml'].str.split(r'</div><div class="').str[1]
    trademarks_df_cn_rows['IPR_NAMEhtml'] = trademarks_df_cn_rows['IPR_NAMEhtml'].str.split(r'">').str[1]
    trademarks_df_cn_rows['IPR_NAMEhtml'] = trademarks_df_cn_rows['IPR_NAMEhtml'].str.split(r'</div>').str[0]

    trademarks_df_cn_rows['IPR_CLASSEShtml'] = trademarks_df_cn_rows['HTML'].str.split(r'商标分类').str[1]
    trademarks_df_cn_rows['IPR_CLASSEShtml'] = trademarks_df_cn_rows['IPR_CLASSEShtml'].str.split(r'商标状态').str[0]
    trademarks_df_cn_rows['IPR_CLASSEShtml'] = trademarks_df_cn_rows['IPR_CLASSEShtml'].str.split(r'</div><div class="').str[1]
    trademarks_df_cn_rows['IPR_CLASSEShtml'] = trademarks_df_cn_rows['IPR_CLASSEShtml'].str.split(r'">').str[1]
    trademarks_df_cn_rows['IPR_CLASSEShtml'] = trademarks_df_cn_rows['IPR_CLASSEShtml'].str.split(r'</div>').str[0]

    trademarks_df_cn_rows['IPR_STATUS'] = trademarks_df_cn_rows['HTML'].str.split(r'商标状态').str[1]
    trademarks_df_cn_rows['IPR_STATUS'] = trademarks_df_cn_rows['IPR_STATUS'].str.split(r'注册号').str[0]
    trademarks_df_cn_rows['IPR_STATUS'] = trademarks_df_cn_rows['IPR_STATUS'].str.split(r'</div><div class="').str[1]
    trademarks_df_cn_rows['IPR_STATUS'] = trademarks_df_cn_rows['IPR_STATUS'].str.split(r'"><div').str[1]
    trademarks_df_cn_rows['IPR_STATUS'] = trademarks_df_cn_rows['IPR_STATUS'].str.split(r'">').str[1]
    trademarks_df_cn_rows['IPR_STATUS'] = trademarks_df_cn_rows['IPR_STATUS'].str.split(r'</div>').str[0]
    
    trademarks_df_cn_rows['IPR_REG_DATE'] = trademarks_df_cn_rows['HTML'].str.split(r'注册公告日期</div><div class="').str[1]
    trademarks_df_cn_rows['IPR_REG_DATE'] = trademarks_df_cn_rows['IPR_REG_DATE'].str.split(r'专用权期限').str[0]
    trademarks_df_cn_rows['IPR_REG_DATE'] = trademarks_df_cn_rows['IPR_REG_DATE'].str.split(r'">').str[1]
    trademarks_df_cn_rows['IPR_REG_DATE'] = trademarks_df_cn_rows['IPR_REG_DATE'].str.split(r'</div>').str[0]

    trademarks_df_cn_rows['IPR_EXPIRATION_DATE'] = trademarks_df_cn_rows['HTML'].str.split(r'专用权期限</div><div class="').str[1]
    trademarks_df_cn_rows['IPR_EXPIRATION_DATE'] = trademarks_df_cn_rows['IPR_EXPIRATION_DATE'].str.split(r'商标类型').str[0]
    trademarks_df_cn_rows['IPR_EXPIRATION_DATE'] = trademarks_df_cn_rows['IPR_EXPIRATION_DATE'].str.split(r'">').str[1]
    trademarks_df_cn_rows['IPR_EXPIRATION_DATE'] = trademarks_df_cn_rows['IPR_EXPIRATION_DATE'].str.split(r'</div>').str[0]
    trademarks_df_cn_rows['IPR_EXPIRATION_DATE'] = trademarks_df_cn_rows['IPR_EXPIRATION_DATE'].str.split(r'至').str[1]
    
    trademarks_df_cn_rows['IPR_TYPEhtml'] = trademarks_df_cn_rows['HTML'].str.split(r'商标类型').str[1]
    trademarks_df_cn_rows['IPR_TYPEhtml'] = trademarks_df_cn_rows['IPR_TYPEhtml'].str.split(r'类似群组').str[0]
    trademarks_df_cn_rows['IPR_TYPEhtml'] = trademarks_df_cn_rows['IPR_TYPEhtml'].str.split(r'">').str[1]
    trademarks_df_cn_rows['IPR_TYPEhtml'] = trademarks_df_cn_rows['IPR_TYPEhtml'].str.split(r'</div>').str[0]

    trademarks_df_cn_rows['IPR_SUBCLASSES'] = trademarks_df_cn_rows['HTML'].str.split(r'类似群组').str[1]
    trademarks_df_cn_rows['IPR_SUBCLASSES'] = trademarks_df_cn_rows['IPR_SUBCLASSES'].str.split(r'适用商品服务').str[0]
    trademarks_df_cn_rows['IPR_SUBCLASSES'] = trademarks_df_cn_rows['IPR_SUBCLASSES'].str.split(r'FvDQAhY').str[1]
    trademarks_df_cn_rows['IPR_SUBCLASSES'] = trademarks_df_cn_rows['IPR_SUBCLASSES'].str.split(r'<').str[0]
    trademarks_df_cn_rows['IPR_SUBCLASSES'] = trademarks_df_cn_rows['IPR_SUBCLASSES'].str.replace(r'">', '', regex=False)

    trademarks_df_cn_rows['IPR_SUBCLASSESdetails'] = trademarks_df_cn_rows['HTML'].str.split(r'适用商品服务').str[1]
    trademarks_df_cn_rows['IPR_SUBCLASSESdetails'] = trademarks_df_cn_rows['IPR_SUBCLASSESdetails'].str.split(r'<div class=""liYyg7LN"">').str[0]
    trademarks_df_cn_rows['IPR_SUBCLASSESdetails'] = trademarks_df_cn_rows['IPR_SUBCLASSESdetails'].str.replace(r'</div><div class="aFvDQAhY">', '; ', regex=False)
    trademarks_df_cn_rows['IPR_SUBCLASSESdetails'] = trademarks_df_cn_rows['IPR_SUBCLASSESdetails'].str.replace(r'<!-- -->-<!-- -->', ': ', regex=False)
    trademarks_df_cn_rows['IPR_SUBCLASSESdetails'] = trademarks_df_cn_rows['IPR_SUBCLASSESdetails'].str.split(r'"aFvDQAhY">').str[1]
    trademarks_df_cn_rows['IPR_SUBCLASSESdetails'] = trademarks_df_cn_rows['IPR_SUBCLASSESdetails'].str.split(r'<div').str[0]
    trademarks_df_cn_rows['IPR_SUBCLASSESdetails'] = trademarks_df_cn_rows['IPR_SUBCLASSESdetails'].str.split(r'</div></div></div>').str[0]
    
    trademarks_df_cn_rows['IPR_APPLICANT'] = trademarks_df_cn_rows['HTML'].str.split(r'申请人</div><div class="').str[1]
    trademarks_df_cn_rows['IPR_APPLICANT'] = trademarks_df_cn_rows['IPR_APPLICANT'].str.split(r'申请人地址</div>').str[0]
    trademarks_df_cn_rows['IPR_APPLICANT'] = trademarks_df_cn_rows['IPR_APPLICANT'].str.split(r'</div>').str[0]
    trademarks_df_cn_rows['IPR_APPLICANT'] = trademarks_df_cn_rows['IPR_APPLICANT'].str.split(r'">').str[1]


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
    st.write('TRADEMARK CN ROWS')
    st.write(trademarks_df_cn_rows)




    # Filter rows where 'IPR_JURISDICTION' is equal to 'CN'
    trademarks_df_int_rows = trademarks_df[trademarks_df['IPR_JURISDICTION'] == 'INT TM']

    # Create an empty master DataFrame
    master_df = pd.DataFrame()

    # Iterate through the URLs and extract data
    for index, row in trademarks_df_int_rows.iterrows():
        url = row['IPR_URL']
        st.write('URLS DA PARSARE:')
        st.write(url)
        df_data = extract_data_int(url)
        st.write(df_data)
        if df_data is not None:
            master_df = pd.concat([master_df, df_data], ignore_index=True)
    st.write('Master DF')
    st.write(master_df)


    trademarks_df_int_rows['IPR_IMAGE'] = trademarks_df_int_rows['HTML'].str.split(r'<img class=').str[1]
    trademarks_df_int_rows['IPR_IMAGE'] = trademarks_df_int_rows['IPR_IMAGE'].str.split(r'" src="').str[1]
    trademarks_df_int_rows['IPR_IMAGE'] = trademarks_df_int_rows['IPR_IMAGE'].str.split(r'"/>').str[0]
    
    trademarks_df_int_rows['IPR_NAMEhtml'] = trademarks_df_int_rows['HTML'].str.split(r'markname"').str[1]
    trademarks_df_int_rows['IPR_NAMEhtml'] = trademarks_df_int_rows['IPR_NAMEhtml'].str.split(r'</h3> </td> <td> <div class').str[0]
    trademarks_df_int_rows['IPR_NAMEhtml'] = trademarks_df_int_rows['IPR_NAMEhtml'].str.split(r'-').str[1]
    trademarks_df_int_rows['IPR_NAMEhtml'] = trademarks_df_int_rows['IPR_NAMEhtml'].str.split(r'<').str[0]

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

    st.write(trademarks_df_int_rows)



    # Create an empty master DataFrame
    master_df = pd.DataFrame()

    # Iterate through the URLs and extract data
    for index, row in trademarks_df_int_rows.iterrows():
        url = row['IPR_URL']
        df_data = extract_data_int(url)
        if df_data is not None:
            master_df = pd.concat([master_df, df_data], ignore_index=True)

    print(master_df)


    # Re-concatenate the DataFrames to create df_combined
    df_combined = pd.concat([trademarks_df, design_patents_df, nottrademarks_df], ignore_index=True)
    # Reset the index of the combined DataFrame
    df_combined = df_combined.reset_index(drop=True)


    st.title("Data Analysis")
    st.write(df_combined)

# Streamlit UI
st.title("Trademark Data Analysis")

# Upload an XLSX file
xlsx_files = st.sidebar.file_uploader("Upload an XLSX file", type=["xlsx"], accept_multiple_files=True)

if xlsx_files:
    df_import = process_xlsx_files(xlsx_files)
    st.dataframe(df_import)
