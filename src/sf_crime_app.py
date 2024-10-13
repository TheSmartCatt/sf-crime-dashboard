import streamlit as st
import pandas as pd
import pydeck as pdk

# Streamlit dark theme configuration
st.set_page_config(page_title="Police Incidents Dashboard", page_icon=":police_car:", layout="wide")
st.markdown("""
    <style>
        body {
            background-color: #FFFFFF;
            color: #f8f9fa;
        }
        .title {
            text-align: center;
            color: #000000;
            font-size: 36px;
            margin-top: 20px;
        }
        .sidebar .sidebar-content {
            background-color: #343a40;
            border-radius: 5px;
            padding: 10px;
        }
        .sidebar .sidebar-content h1 {
            color: #f8f9fa;
        }
    </style>
""", unsafe_allow_html=True)

# Load the dataset
file_path = 'Police_Department_Incidents_Previous_Year_2016.csv'
data = pd.read_csv(file_path)
data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
data['Time'] = pd.to_datetime(data['Time'], format='%H:%M', errors='coerce').dt.hour

# Centered Title
st.markdown('<h1 class="title">Police Department Incidents Data (2016)</h1>', unsafe_allow_html=True)

# Sidebar filters
st.sidebar.title("Filters")

# # Display the data in the app
# st.write("Police Department Incidents Data (2016) - Before Applying Filters", data.head())

# Category selection
unique_categories = data['Category'].unique()
selected_category = st.sidebar.selectbox("Select a category:", ["Select"] + list(unique_categories))
if selected_category != "Select":
    filtered_data = data[data['Category'] == selected_category]
else:
    filtered_data = pd.DataFrame()

# Month selection
if 'Date' in data.columns and not filtered_data.empty:
    filtered_data['Month'] = filtered_data['Date'].dt.month
    month_mapping = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
    unique_months = sorted(filtered_data['Month'].dropna().unique())
    selected_month = st.sidebar.selectbox("Select a month:", ["Select"] + [month_mapping[m] for m in unique_months])
    if selected_month != "Select":
        month_number = {v: k for k, v in month_mapping.items()}[selected_month]
        filtered_data = filtered_data[filtered_data['Month'] == month_number]

# Day selection
if 'DayOfWeek' in data.columns and not filtered_data.empty:
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    filtered_data['DayOfWeek'] = pd.Categorical(filtered_data['DayOfWeek'], categories=day_order, ordered=True)
    selected_day = st.sidebar.selectbox("Select a day of the week:", ["Select"] + day_order)
    if selected_day != "Select":
        filtered_data = filtered_data[filtered_data['DayOfWeek'] == selected_day]

if not filtered_data.empty:
    st.write("Police Department Incidents Data (2016) - After Applying Filters on the left (Top 5 Rows)", filtered_data.head())
else:
    st.error("No data to display in the table. Please adjust the filters.")
st.markdown("""---""")

# Display the map
if not filtered_data.empty and 'X' in filtered_data.columns and 'Y' in filtered_data.columns:
    filtered_data = filtered_data[(filtered_data['X'] != 0) & (filtered_data['Y'] != 0)]
    filtered_data = filtered_data.rename(columns={'X': 'LONGITUDE', 'Y': 'LATITUDE'})
    latitude, longitude = 37.7749, -122.4194
    midpoint = (latitude, longitude)
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/streets-v12",
        initial_view_state={"latitude": midpoint[0], "longitude": midpoint[1], "zoom": 11, "pitch": 50},
        layers=[pdk.Layer("HexagonLayer", data=filtered_data[['Date', 'LATITUDE', 'LONGITUDE']], get_position=["LONGITUDE", "LATITUDE"], auto_highlight=True, radius=100, extruded=True, pickable=True, elevation_scale=4, elevation_range=[0, 1000])]
    ))
else:
    st.error("No data to display on the map. Please adjust the filters.")