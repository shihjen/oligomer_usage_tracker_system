# function to extract and parse the text from the PDF
def extract_pdf_data(document):
    import pymupdf
    import fitz 
    text = ""
    
    # Iterate through all the pages and extract text
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text += page.get_text()
    
    # Parse the text to extract relevant data
    data = {}
    lines = text.split('\n')
    
    # Define the keywords to search for and their corresponding field names
    keywords = {
        "Invoice Nbr:": "Invoice_Number",
        "Invoice Date:": "Invoice_Date",
        "Order Total:": "Order_Total",
        "Tax:": "Tax",
        "Invoice Total:": "Invoice_Total",
        "Package Ids:": "DO_Number",
        "P.O. #": "PO_Number",
        "Order Date" : "Order_Date",
        "Sales Order #": "Sale_Order",
        "Ship Date": "Delivery_Date"
    }
    # Initialize variables to keep track of parsing state
    key = None
    
    for i, line in enumerate(lines):
        # Remove leading and trailing whitespace from the line
        line = line.strip()
        
        if key:
            # Assign the value to the corresponding key in the data dictionary
            data[key] = line
            key = None
            continue

        for keyword, field in keywords.items():
            if keyword in line:
                # Special handling for "Sales Order #"
                if keyword == "P.O. #":
                    # Extract the second line after "Sales Order #"
                    if i + 6 < len(lines):
                        data[field] = lines[i + 6].strip()
                    break
                elif keyword == "Order Date":
                    if i + 6 < len(lines):
                        data[field] = lines[i + 6].strip()
                    break
                elif keyword == "Sales Order #":
                    if i + 6 < len(lines):
                        data[field] = lines[i + 6].strip()
                    break
                elif keyword == "Ship Date":
                    if i + 6 < len(lines):
                        data[field] = lines[i + 6].strip()
                    break
                
                # Extract the value directly if it's in the same line
                value = line.split(keyword)[1].strip()
                if value:
                    data[field] = value
                else:
                    key = field
                break
    
    # Standardize output based on the order of keywords
    standardized_data = {field: data.get(field, "") for field in keywords.values()}
    return standardized_data

########################################################################################################
# function to process all PDF files in a directory
def process_pdf_directory(documents):
    import pymupdf
    import fitz 
    import os
    # List all PDF files in the directory
    # pdf_files = [f for f in os.listdir(directory_path) if f.endswith('.pdf')]
    
    all_extracted_data = []
    
    for pdf_file in documents:
        #pdf_path = os.path.join(directory_path, pdf_file)
        #document = fitz.open(pdf_path)
        extracted_data = extract_pdf_data(pdf_file)
        all_extracted_data.append(extracted_data)
    
    return all_extracted_data
########################################################################################################


########################################################################################################
# function to clean the imported dataframe from DB
def clean_df(df):
    import pandas as pd
    month_mapping = {1:'Jan', 2:'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
    df_deduped = df.drop_duplicates(subset=['Invoice_Number'])
    df_deduped['Invoice_Date'] = df_deduped['Invoice_Date'].apply(lambda x: pd.to_datetime(x, format='%d %b %Y'))
    df_deduped['Order_Date'] = df_deduped['Order_Date'].apply(lambda x: pd.to_datetime(x, format='%d %b %Y'))
    df_deduped['Delivery_Date'] = df_deduped['Delivery_Date'].apply(lambda x: pd.to_datetime(x, format='%d %b %Y'))
    df_deduped['Order_Total'] = df_deduped['Order_Total'].apply(lambda x: float(x.strip('S$ ')))
    df_deduped['Tax'] = df_deduped['Tax'].apply(lambda x: float(x.strip('S$ ')))
    df_deduped['PO_Number'] = df_deduped['PO_Number'].astype(str)
    df_deduped['Delivery_Leadtime'] = (df_deduped['Delivery_Date'] - df_deduped['Order_Date']).dt.days
    df_deduped['Invoice_Number'] = df_deduped['Invoice_Number'].astype(str)
    df_deduped['Sale_Order'] = df_deduped['Sale_Order'].astype(str)
    df_deduped['DO_Number'] = df_deduped['DO_Number'].astype(str)
    df_deduped['Invoice_Total'] = df_deduped['Invoice_Total'].apply(lambda x: float(x.strip('S$ ')))
    df_deduped['Invoice_Year'] = df_deduped['Invoice_Date'].dt.year
    df_deduped['Invoice_Month'] = df_deduped['Invoice_Date'].dt.month
    df_deduped['Invoice_Month'] = df_deduped['Invoice_Month'].map(month_mapping)
    return df_deduped
#########################################################################################################


#########################################################################################################
# function to extract key metrics
def display_key_metrics(year, data):
    import pandas as pd
    if year == 'All Years':
        fil_data = data
    else:
        fil_data = data[data['Invoice_Year'] == year]
    
    total_expenses_notax = round(sum(fil_data['Order_Total']),2)
    total_expenses = round(sum(fil_data['Invoice_Total']),2)
    total_number_order = fil_data.shape[0]
    average_order = round(total_expenses/total_number_order, 2)
    total_base = int(sum(fil_data['Order_Total']) / 0.2)
    average_lead_time = round((sum(fil_data['Delivery_Leadtime'] / fil_data.shape[0])),2)
    
    return [total_expenses_notax, total_expenses, total_number_order, average_order, average_lead_time, total_base]
#############################################################################################################


#############################################################################################################
# function to plot the heatmap
def plot_heatmap(data):
    import pandas as pd
    import plotly.graph_objects as go
    # aggregate the data to get total invoice amount per month per year
    monthly_totals = data.groupby(['Invoice_Year', 'Invoice_Month'])['Invoice_Total'].sum().reset_index()

    # pivot the data to create a matrix suitable for heatmap
    pivot_table = monthly_totals.pivot(index='Invoice_Year', columns='Invoice_Month', values='Invoice_Total').fillna(0)

    # create the heatmap using Plotly Graph Objects
    fig = go.Figure(data=go.Heatmap(
        z=pivot_table.values,
        x=pivot_table.columns,
        y=pivot_table.index,
        colorscale='blues',
        showscale=False,
        hovertemplate='Year: %{y}<br>Month: %{x}<br>Total: S$%{z}<extra></extra>',
    ))

    # add border lines by drawing rectangles around each cell
    shapes = []
    for i, row in enumerate(pivot.index):
        for j, col in enumerate(pivot.columns):
            shapes.append(
                go.layout.Shape(
                    type="rect",
                    x0=col - 0.5, x1=col + 0.5,
                    y0=row - 0.5, y1=row + 0.5,
                    line=dict(color='grey', width=1)
                )
            )

    fig.update_layout(
        #title='Expenses by Month',
        xaxis_title='Month',
        yaxis_title='Year',
        xaxis=dict(
            type='category',
            categoryorder='array',
            categoryarray=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        ),
        yaxis=dict(
            tickmode='array',
            tickvals=pivot_table.index.tolist(),
            ticktext=pivot_table.index.tolist(),
        ),
        height=500
    )
    return fig
###############################################################################################################


###############################################################################################################
# function to plot bar chart (orders by year)
def plot_bar(data):
    import pandas as pd
    import plotly.graph_objects as go
    colors = ['#d0e1f2','#9cc9e1','#1f6eb3','#08336f']
    grouped_data = data.groupby('Invoice_Year')
    agg_data = grouped_data['Sale_Order'].count()

    fig = go.Figure(data=[go.Bar(
        x=agg_data.index,
        y=agg_data.values,
        text=agg_data.values,
        textposition='outside',
        hovertemplate='Year: %{x}<br>Number of orders: %{y}<br> <extra></extra>',
        marker_color=colors # marker color can be a single color value or an iterable
    )])

    fig.update_layout(
        #title='Number of Order from 2021 to 2024',
        #xaxis_title='Year',
        yaxis_title='Number of Order',
        xaxis=dict(
            tickmode='array',
            tickvals=agg_data.index.tolist(),  # Set tick values to the index of agg_data
            ticktext=agg_data.index.astype(str).tolist(),  # Set tick text to the index values converted to string
        ),
        height=500
    )
    return fig
#################################################################################################################


#################################################################################################################
# function to plot bar chart by month
def plot_bar_month(data, year):
    import pandas as pd
    import plotly.graph_objects as go
    custom_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    #colors = ['#d0e1f2','#9cc9e1','#1f6eb3','#08336f']
    selected_data = data[data['Invoice_Year']==year]
    grouped_data = selected_data.groupby('Invoice_Month')
    agg_data = grouped_data['Sale_Order'].count()
    agg_data_sorted = agg_data.reindex(custom_order)

    fig = go.Figure(data=[go.Bar(
        x=agg_data_sorted.index,
        y=agg_data_sorted.values,
        text=agg_data_sorted.values,
        textposition='outside',
        hovertemplate='Month: %{x}<br>Number of orders: %{y}<br> <extra></extra>',
        marker_color='#1f6eb3' # marker color can be a single color value or an iterable
    )])

    fig.update_layout(
        #title='Number of Order from 2021 to 2024',
        #xaxis_title='Month',
        yaxis_title='Number of Order',
        xaxis=dict(
            tickmode='array',
            tickvals=agg_data_sorted.index.tolist(),  # Set tick values to the index of agg_data
            ticktext=agg_data_sorted.index.astype(str).tolist(),  # Set tick text to the index values converted to string
        ),
        height=500
    )
    return fig
#################################################################################################################



##################################################################################################################
# function to plot donut chart
def plot_donut(po_spending, total_spending):
    import plotly.graph_objects as go
    fig = go.Figure(data=[go.Pie(labels=['Selected PO', 'Other POs'],
                                values=[po_spending, total_spending - po_spending],
                                hole=.5)])
    return fig
###################################################################################################################