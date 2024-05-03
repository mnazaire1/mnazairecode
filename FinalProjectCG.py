""" Name: Marvens Nazaire CS230: Section 6 Data: Which data set you used URL: Starbucks_10000_sample

Description: This program allows users to select varies starbucks locations around the world and displays a map and
graphs that the user can compare to make different analysis.

"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static

# Load data
data = pd.read_csv('starbucks_10000_sample 2.csv')

# Clean the data by removing rows with missing 'Latitude' or 'Longitude' [DA1]
data.dropna(subset=['Latitude', 'Longitude'], inplace=True)

# Display Starbucks Logo [ST4 - Page design feature]
st.image('strbucks.png', width=200)

# Streamlit sidebar setup for navigation [ST4 - Page design feature]
menu = ["Home", "Data Analysis", "Map View"]
choice = st.sidebar.selectbox("Menu", menu)  # [ST1]

if choice == "Home":
    st.write('## Welcome to the Starbucks Database!')
    # Display a detailed table of the data [ST4 - Page design feature]
    st.dataframe(data)  # Displaying the full dataframe for detailed view

# Function to filter data based on multiple conditions [PY1 - multiple default params, PY3 - used in multiple places]
def filter_data(country_code, subdivision_code=None, store_type=None, city_name=None):  # [DA5]
    filtered_data = data[data['CountryCode'] == country_code.upper()]
    if subdivision_code:
        filtered_data = filtered_data[filtered_data['CountrySubdivisionCode'] == subdivision_code.upper()]
    if store_type and store_type != 'All':
        filtered_data = filtered_data[filtered_data['OwnershipType'] == store_type]
    if city_name:
        filtered_data = filtered_data[filtered_data['City'].str.upper() == city_name.upper()]
    return filtered_data

# Function to create a map from filtered data [PY3 - used in multiple places, VIZ4]
def create_map(data_frame):
    if not data_frame.empty and {'Latitude', 'Longitude'}.issubset(data_frame.columns):
        start_lat = data_frame['Latitude'].mean()
        start_lon = data_frame['Longitude'].mean()
        map = folium.Map(location=[start_lat, start_lon], zoom_start=11)
        heatmap_data = data_frame[['Latitude', 'Longitude']].values.tolist()  # [PY4 - List comprehension]
        HeatMap(heatmap_data).add_to(map)
        for idx, row in data_frame.iterrows():  # [DA8]
            folium.Marker([row['Latitude'], row['Longitude']], popup=row['Name']).add_to(map)
        return map
    else:
        return folium.Map(location=[0, 0], zoom_start=2)  # Return a default map if no data

if choice == "Data Analysis":
    st.title("Starbucks Store Analysis")
    country = st.selectbox('Select a country for analysis:', data['CountryCode'].unique(), key='country_analysis')  # [ST1]
    selected_states = st.multiselect('Select states for analysis:',
                                     data[data['CountryCode'] == country]['CountrySubdivisionCode'].unique(),
                                     key='states_analysis')  # [ST1]
    store_type = st.selectbox('Select store type for analysis:', ['All'] + list(data['OwnershipType'].unique()),
                              key='store_type_analysis')  # [ST1]

    if selected_states:
        filtered_stores = pd.concat([filter_data(country, state, store_type) for state in selected_states])  # [PY4 - List comprehension]
    else:
        filtered_stores = pd.DataFrame()

    if not filtered_stores.empty:
        comparison_data = filtered_stores['CountrySubdivisionCode'].value_counts().reset_index()
        comparison_data.columns = ['State', 'Number of Stores']
        chart_type = st.radio("Select chart type for analysis:", ('Bar Chart', 'Pie Chart', 'Scatter Plot'), key='chart_type')  # [ST1]

        fig, ax = plt.subplots()
        if chart_type == 'Bar Chart':  # [VIZ1]
            ax.bar(comparison_data['State'], comparison_data['Number of Stores'])
            plt.xlabel('State')
            plt.ylabel('Number of Stores')
            plt.title('Comparison of Starbucks Stores by State')
        elif chart_type == 'Pie Chart':  # [VIZ2]
            ax.pie(comparison_data['Number of Stores'], labels=comparison_data['State'], autopct='%1.1f%%')
            plt.title('Market Share of Starbucks Stores by State')
        elif chart_type == 'Scatter Plot':  # [VIZ3]
            ax.scatter(comparison_data['State'], comparison_data['Number of Stores'])
            plt.xlabel('State')
            plt.ylabel('Number of Stores')
            plt.title('Scatter Plot of Starbucks Stores by State')
        st.pyplot(fig)

elif choice == "Map View":
    st.title("Starbucks Store Map View")
    country = st.selectbox('Select a country for map:', data['CountryCode'].unique(), key='country_map')  # [ST1]
    state_options = data[data['CountryCode'] == country]['CountrySubdivisionCode'].unique()
    selected_states = st.multiselect('Select state(s) for map:', options=state_options, key='state_map')  # [ST1]
    store_type = st.selectbox('Select store type for map:', ['All'] + list(data['OwnershipType'].unique()),
                              key='store_map')  # [ST1]

    if selected_states:
        filtered_stores = pd.concat([filter_data(country, state, store_type) for state in selected_states])  # [PY4 - List comprehension]
    else:
        filtered_stores = pd.DataFrame()

    if not filtered_stores.empty:
        starbucks_map = create_map(filtered_stores)  # [VIZ4]
        folium_static(starbucks_map)
    else:
        st.error("Select the following options to display the map: a country, one or more states, and a store type.")  # [ST4 - Page design feature]
