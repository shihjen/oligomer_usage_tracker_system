# load the required dependencies
import streamlit as st
import pandas as pd
import helper
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from navigation import make_sidebar


# Streamlit page configuration
st.set_page_config(
    page_title='BCEAD Oligomer Usage Tracker System',
    page_icon=':chart_with_upwards_trend:',
    layout='wide',
    initial_sidebar_state='expanded'
)

make_sidebar()

st.subheader(':blue[BCEAD Oligomers Usage Tracker System]', divider='gray')
st.sidebar.image('image/BCEAD.png')
st.sidebar.subheader(':blue[Welcome to the BCEAD Oligomers Usage Tracker System]', divider='gray')
st.sidebar.write('''
This dashboard provides a comprehensive overview of the BCEAD lab's research funding usage on oligomers. 
You can view expenses by year using the year selection box. 
Additionally, the PO Analysis section offers detailed insights into each purchase order (PO), 
including associated invoices, delivery orders (DOs), and sales orders. 
For your convenience, you can download a summary of this data in CSV format.
''')

################################################################################################################
# function to authenticate and open the Google Sheet
def authenticate_google_sheets_from_secrets():
    secrets = st.secrets["gcp_service_account"]
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(secrets, scope)
    return credentials

# function to open the Google spreadsheet
def open_sheet(credentials, spreadsheet_name, sheet_name):
    client = gspread.authorize(credentials)
    spreadsheet = client.open(spreadsheet_name)
    sheet = spreadsheet.worksheet(sheet_name)
    return sheet

# function to convert the Google spreadsheet into pandas dataframe
def sheet_to_dataframe(sheet):
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

# function to convert Google Sheet data to a pandas DataFrame
def sheet_to_dataframe2(sheet, worksheet_name):
    worksheet = sheet.worksheet(worksheet_name)
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    return df
#################################################################################################################


# connect to Google account and get the spreadhseets
credentials = authenticate_google_sheets_from_secrets()
spreadsheet_name = 'IDT_Invoice_Record'
sheet1 = open_sheet(credentials, spreadsheet_name, 'Sheet1')
sheet2 = open_sheet(credentials, spreadsheet_name, 'Sheet2')
df_sheet1 = sheet_to_dataframe(sheet1)
df_sheet2 = sheet_to_dataframe(sheet2)

# data cleaning
cleaned_df = helper.clean_df(df_sheet1)
cleaned_df_sorted = cleaned_df.sort_values(by='Invoice_Date')

# PO list with WBS number
po_list = df_sheet2['PO_Number']
wbs_list = df_sheet2['WBS_Number']
po_option = dict(zip(po_list, wbs_list))


# divide the body into 3 columns
col1, col2, col3 = st.columns([1.25, 3, 2.75], gap='large')

#################################################################################################################
# container 1 --- select year and display key metrics
cont1 = col1.container(border=False)
cont1.markdown('#### :blue[Year]')
year = cont1.selectbox('Select year:', ['All Years', 2021, 2022, 2023, 2024])
cont1.markdown('### ')
cont1.markdown('#### :blue[Usage Summary]')

# obtain the key metrics
# key metrics list - [total_expenses_notax, total_expenses, total_number_order, average_order, average_lead_time, total_base]
key_metrics = helper.display_key_metrics(year, cleaned_df_sorted)

# define a custom css script
custom_css = """
<style>
/* Define a custom class with the desired background color */
.custom-metric-card {
    background-color: #9cc9e1; /* Change the color code to your desired background color */
    color: #08336f; /* Change the text color code to your desired color */
    padding: 8px; /* Optional: Adjust padding as needed */
}
</style>
"""

# key metric card 1 --- total expenses (with and without GST)
# display the custom CSS
cont1.markdown(custom_css, unsafe_allow_html=True)
# display the metric card with the custom class using HTML
cont1.markdown(f"""
<div class="custom-metric-card">
    <p style="font-size: 18px;">Total Expenses</p>
    <p style="font-size: 22px; font-weight: bold; margin: 0;">S$ {key_metrics[0]} <br> S$ {key_metrics[1]} (GST)</p>
</div>
""", unsafe_allow_html=True)

# key metric card 2 --- total number of orders
# display the custom CSS
cont1.markdown(custom_css, unsafe_allow_html=True)
# display the metric card with the custom class using HTML
cont1.markdown(f"""
<div class="custom-metric-card">
    <p style="font-size: 18px;">Total Number of Order</p>
    <p style="font-size: 22px; font-weight: bold; margin: 0;">{key_metrics[2]}</p>
</div>
""", unsafe_allow_html=True)

# key metric card 3 --- average cost per order
# display the custom CSS
cont1.markdown(custom_css, unsafe_allow_html=True)
# display the metric card with the custom class using HTML
cont1.markdown(f"""
<div class="custom-metric-card">
    <p style="font-size: 18px;">Average Cost per Order</p>
    <p style="font-size: 22px; font-weight: bold; margin: 0;">$S {key_metrics[3]}</p>
</div>
""", unsafe_allow_html=True)

# key metric card 4 --- average lead time
# display the custom CSS
cont1.markdown(custom_css, unsafe_allow_html=True)
# display the metric card with the custom class using HTML
cont1.markdown(f"""
<div class="custom-metric-card">
    <p style="font-size: 18px;">Average Lead Time</p>
    <p style="font-size: 22px; font-weight: bold; margin: 0;">{key_metrics[4]} days</p>
</div>
""", unsafe_allow_html=True)
    
# key metric card 5 - total nucleotide ordered
# display the custom CSS
cont1.markdown(custom_css, unsafe_allow_html=True)
# display the metric card with the custom class using HTML
cont1.markdown(f"""
<div class="custom-metric-card">
    <p style="font-size: 18px;">Total Nucleotide Ordered</p>
    <p style="font-size: 22px; font-weight: bold; margin: 0;">{key_metrics[5]} bases</p>
</div>
""", unsafe_allow_html=True)



##########################################################################################################
# container 2 --- heatmap and bar chart
cont2 = col2.container(border=False)
heatmap = helper.plot_heatmap(cleaned_df)
cont2.markdown('#### :blue[Total Expenses by Month]')
cont2.plotly_chart(heatmap, theme='streamlit', use_container_width=True)

if year == 'All Years':
    cont2.markdown('#### :blue[Number of Orders from 2021 to 2024]')
    bar = helper.plot_bar(cleaned_df_sorted)
    cont2.plotly_chart(bar, theme='streamlit', use_container_width=True)
else:
    cont2.markdown(f'#### :blue[Number of Orders in {year}]')
    bar = helper.plot_bar_month(cleaned_df_sorted, year)
    cont2.plotly_chart(bar, theme='streamlit', use_container_width=True)
###########################################################################################################



###########################################################################################################
# container 3 --- analysis by PO
cont3 = col3.container(border=False)
cont3.markdown('#### :blue[Analysis for Purchase Order (PO)]')
user_option = cont3.selectbox('Select a purchase order (PO)', list(po_option.keys()))
selected_df = cleaned_df_sorted[cleaned_df_sorted['PO_Number'] == str(user_option)]
selected_df_subset = selected_df[['Invoice_Date','Invoice_Number','DO_Number','Sale_Order','Invoice_Total']]

# display the metric card with the custom class using HTML
cont3.markdown(f"""
<div class="custom-metric-card">Funding Source:
    <p style="font-size: 20px; font-weight: bold; margin: 0;"> {po_option[user_option]}</p>
</div>
""", unsafe_allow_html=True)

# display the selected data based on PO
cont3.dataframe(selected_df_subset, use_container_width=True)

# donut chart
total_spending  = cleaned_df_sorted['Invoice_Total'].sum()
po_spending = cleaned_df_sorted[cleaned_df_sorted['PO_Number'] == str(user_option)]['Invoice_Total'].sum()
cont3.markdown(f'#### :blue[Purchase Order (PO) Value: S$ {po_spending}]')
donut = helper.plot_donut(po_spending, total_spending)
cont3.plotly_chart(donut)
############################################################################################################


