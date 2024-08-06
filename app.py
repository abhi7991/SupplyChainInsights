# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 13:13:14 2024

@author: abhis
"""

import nest_asyncio
nest_asyncio.apply()
import streamlit as st
import requests
from dotenv import load_dotenv
import os
from datetime import datetime,timedelta
import pandas as pd
from modules import utils,ragas_eval
import numpy as np
from openai import OpenAI
import seaborn as sns
import matplotlib.pyplot as plt
# import numpy as np

load_dotenv()

# # List all files in the current directory
# for file in os.listdir():
#     # Check if the file ends with .csv
#     if file.endswith(".csv"):
#         # Remove the file
#         os.remove(file)
#         print(f"Removed: {file}")

# Initialize session state variables
def initialize_session_state():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "suggested_question_clicked" not in st.session_state:
        st.session_state.suggested_question_clicked = False

# Display images in the sidebar
# def display_images_in_sidebar(image_dir):
#     st.sidebar.image(os.path.join(os.getcwd(), "Images/logo.jpg"), caption=None, use_column_width=True)    
#     st.sidebar.title("MovieMatch Gallery")
#     images = os.listdir(image_dir)
#     for image in images:
#         image_path = os.path.join(image_dir, image)
#         st.sidebar.image(image_path, caption=None, use_column_width=True)

# Display the chat history
def display_chat_history():
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Handle suggested questions
def display_suggested_questions(suggested_questions):
    if not st.session_state.suggested_question_clicked:
        st.subheader("Suggested Questions")
        for question in suggested_questions:
            if st.button(question):
                st.session_state.suggested_question_clicked = True
                handle_user_input(question)
                break
# Handle user input
def handle_user_input(user_input):
    st.chat_message("user").markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    #generate_and_display_response()

def detect_plot_type(query):
    '''
    Detect the type of plot requested in the query.
    '''
    plot_keywords = {
        'Line Plot': ['line plot', 'line chart', 'trend line','line'],
        'Bar Chart': ['bar chart', 'bar plot', 'bar graph','bar'],
        'Scatter Plot': ['scatter plot', 'scatter graph', 'xy plot'],
        'Distribution Plot': ['distribution plot', 'histogram', 'density plot'],
        'Bar Chart': ['count plot', 'count graph', 'frequency plot','count']
    }
    
    query_lower = query.lower()
    
    for plot_type, keywords in plot_keywords.items():
        if any(keyword in query_lower for keyword in keywords):
            return plot_type
    
    return None  # Return None if no plot type is detected

def home_page():
    # Set background image
    st.markdown("# SupplyChainInsights")

# Page to display data table
def data_table_page():
    # st.title("Data Table Page")
    st.markdown("# SupplyChainInsights")
    st.subheader('Performance Metrics')
    st.text('Find out how good the responses were?')    
    # df = pd.read_csv(os.getcwd()+"//evaluation_results.csv")
    # df1 = ragas_eval.getEval(df)
    # print(df1)
    try:
        df = pd.read_csv(os.getcwd()+"//evaluation_results.csv")
        df = ragas_eval.getEval(df)
    except:
        df = pd.DataFrame({"Note : ":"You havent asked any queries yet"},index=[0])

    #st.write("Here is how good the responses were")
    st.dataframe(df)
        
def generatePlot(input_data):
    
    df = input_data['Data']
    query = input_data['Question']
    print("Here is the data , /n",df)
    plot_type = detect_plot_type(query)

    if plot_type==None:
        response = "Please Specify if you would like a specific plot like Line Plot, Bar Chart, Scatter Plot, Distribution Plot"
        st.session_state.messages.append({"role": "assistant", "content": response})
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
    else:

        fig, ax = plt.subplots(figsize=(30, 20))

        x_axis = df.columns[0]
        y_axis = df.columns[1]

        if plot_type == 'Line Plot':
            sns.lineplot(x=df.iloc[:, 0], y=df.iloc[:, 1], ax=ax)
        elif plot_type == 'Bar Chart':
            sns.barplot(x=df.iloc[:, 0], y=df.iloc[:, 1], ax=ax)
        elif plot_type == 'Scatter Plot':
            sns.scatterplot(x=df.iloc[:, 0], y=df.iloc[:, 1], ax=ax)
        elif plot_type == 'Distribution Plot':
            sns.histplot(df.iloc[:, 0], kde=True, ax=ax)
            y_axis='Density'
        elif plot_type == 'Count Plot':
            sns.countplot(x=df.iloc[:, 0], ax=ax)
            y_axis = 'Count'

        # # Plotting a bar chart
        # sns.barplot(x=df.iloc[:, 0], y=df.iloc[:, 1], ax=ax)

        # Rotate x-axis and y-axis labels
        plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels, align right
        plt.yticks(rotation=0)  # Y-axis labels, typically kept at 0 degrees

        # Adjust label sizes
        ax.tick_params(axis='x', labelsize=10)  # Adjust x-axis label size
        ax.tick_params(axis='y', labelsize=10)  # Adjust y-axis label size

        # Adjust title and axis labels with a smaller font size
        plt.title(f'{plot_type} of {y_axis} vs {x_axis}', fontsize=12)
        plt.xlabel(x_axis, fontsize=10)
        plt.ylabel(y_axis, fontsize=10)
        #st.image(fig, caption="Visualization", use_column_width=True)
        
        st.pyplot(fig)
    #.pyplot(fig)   
        
def chat_interface_page():

    initialize_session_state()

    st.title("SupplyChainInsights - Clear Insights into Global Health Commodity Trends")
    st.subheader('Access the World Wide Supply Chain of Antiretroviral (ARV) and HIV lab shipments!')
    # Load and display images from local repository
    image_dir = os.path.join(os.getcwd(), "Files/logo-color.png")
    st.sidebar.image(image_dir, caption=None, use_column_width=True)
    # display_images_in_sidebar(image_dir)

    display_chat_history()

    # List of suggested questions
    # suggested_questions = [
    #     "Can you recommend a good comedy movie?",
    #     "I'm in the mood for a thriller, any suggestions?",
    #     "What's a good classic movie to watch?",
    #     "Can you suggest a movie with a strong female lead?",
    #     "What's a recent release that's worth watching?",
    # ]

    # display_suggested_questions(suggested_questions)

    # Set background image
    # st.markdown(f'<style>body{{background-image: url({page_bg}); background-size: cover;}}</style>', unsafe_allow_html=True)
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

   
    #st.text('Have any questions about our Suppliers, Brands, Customers etc.....')

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What query would you like answered first?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
            
        response = utils.chat_bot(prompt)   
        if response['Tool'] == 'visualise':
            print("RIGHT BEFORE THE IMAGE")
            generatePlot(response)
        else:
            text  = response['output']
            st.session_state.messages.append({"role": "assistant", "content": response['output']})
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(response['output'])
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.experimental_rerun()     

pages = {
        "Home": home_page,
        "Question? Chat it out": chat_interface_page
    }

# Main function to run the Streamlit app
def main():
    st.set_page_config(
        page_title="SupplyChainInsights",page_icon="\U0001F4E6"+"\U0001F30D" ,layout="wide"
    )

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Monitor Performance"])

    # Map the selected page to the corresponding function
    if page == "Home":
        home_page()
        page = pages['Question? Chat it out']
        page()        
    elif page == "Monitor Performance":     
        data_table_page()


if __name__ == "__main__":
    main()                