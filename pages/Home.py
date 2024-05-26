import streamlit as st
from streamlit_lottie import st_lottie
import json
import pandas as pd
import pymupdf
import fitz 
import helper
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv
from navigation import make_sidebar



load_dotenv()
credentials = os.getenv('credentials')

# Streamlit page configuration
st.set_page_config(
    page_title='BCEAD Oligomer Usage Tracker System',
    page_icon=':chart_with_upwards_trend:',
    layout='wide',
    initial_sidebar_state='expanded'
)


make_sidebar()

################################################################################################################
# function to load the lottie file
def load_lottiefile(filepath: str):
    with open(filepath, 'r') as f:
        return json.load(f)
    
# function to authenticate and open the Google Sheet
def authenticate_google_sheets(json_keyfile_path, spreadsheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile_path, scope)
    client = gspread.authorize(credentials)
    sheet = client.open(spreadsheet_name)
    return sheet

# function to convert Google Sheet data to a pandas DataFrame
def sheet_to_dataframe(sheet, worksheet_name):
    worksheet = sheet.worksheet(worksheet_name)
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    return df

# function to update Google Sheet with DataFrame
def update_google_sheet(worksheet, data):
    # worksheet.clear()
    worksheet.update([data.columns.values.tolist()] + data.values.tolist())
#################################################################################################################


    
lottie_cover = load_lottiefile('image/animation.json')

st.title(':blue[BCEAD Oligomers Usage Tracker]')
st.lottie(lottie_cover, speed=1, reverse=False, loop=True, quality='low', height=800, key='first_animate')
st.sidebar.image('image/BCEAD.png')
st.sidebar.subheader(':blue[Welcome to the BCEAD Oligomers Usage Tracker System]', divider='gray')
st.sidebar.write('''
This application is designed to automate data extraction from invoices received from Integrated DNA Technologies for oligomer orders in the BCEAD laboratory. 
Simply upload the invoices, and the application will extract key information, including invoice number, invoice date, 
invoice values, delivery order number (DO), purchase order number (PO), sales order number (SO), order date, and delivery date. 
You can choose to export this data in CSV format or push the extracted data directly into the database. 
For an overview of oligomer usage, please visit the dashboard page.
''')
st.sidebar.title('Upload File')
uploaded_files = st.sidebar.file_uploader('Upload the invoice', type='pdf', accept_multiple_files=True)


################################################################################################################
# container - table display data extracted from the uploaded invoice(s)
container = st.container(border=True)
container.markdown('### Data Extracted from Uploaded Invoice(s)')

if uploaded_files is not None:
    documents = []
    for uploaded_file in uploaded_files:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        documents.append(doc)

    df = helper.process_pdf_directory(documents)
    data = pd.DataFrame(df)

if data.shape[0] >= 1:
    container.dataframe(data, use_container_width=True)
    container.download_button(
    label=':floppy_disk: Download Dataset',
    data=data.to_csv().encode('utf-8'),
    file_name=f'Invoice_Record.csv',
    mime='text/csv')
else:
    container.write('Upload invoice to extract information')



# path to the JSON key file
json_keyfile_path = '.streamlit/secrets.toml'
# name of the Google Sheet
spreadsheet_name = 'IDT_Invoice_Record'
# name of the worksheet to convert to DataFrame
worksheet_name = 'Sheet1'

# authenticate and get the sheet
sheet = authenticate_google_sheets(json_keyfile_path, spreadsheet_name)
worksheet = sheet.worksheet(worksheet_name)

# convert the worksheet to DataFrame
def get_db_data():
    return sheet_to_dataframe(sheet, worksheet_name)

df = get_db_data()

if data.shape[0] >= 1:
    button = st.sidebar.button('Push extracted data to the database')
    if button:
        with st.spinner('Upload data to the database...'):
            merged_df = pd.concat([df, data], axis=0)
            # update Google Sheet with combined DataFrame
            update_google_sheet(worksheet, merged_df)
            st.success('Data successfully updated in the database!')
else:
    pass

st.session_state.df = get_db_data()

