import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Load Data (use st.cache_data for better performance)
@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)

# Sidebar for file upload (you can also directly link to your data)
st.sidebar.header("Upload Your Data")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type='csv')

if uploaded_file is not None:
    # Load the uploaded file
    df = load_data(uploaded_file)

    # Display the DataFrame
    st.write("### Data Overview")
    st.dataframe(df)

    # Display basic statistics
    st.write("### Data Statistics")
    st.write(df.describe())

    # Visualization Options
    st.write("### Visualizations")

    # Bar chart example
    fig, ax = plt.subplots()
    ax.bar(df['column_name'], df['another_column'])
    st.pyplot(fig)

    # Interactive plot (Plotly)
    fig = px.scatter(df, x='column_name', y='another_column', title="Scatter Plot")
    st.plotly_chart(fig)
else:
    st.write("Please upload a CSV file.")
