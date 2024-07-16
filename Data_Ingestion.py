# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 08:38:55 2024

@author: abhis
"""

import re
import os
import pandas as pd
wd = os.getcwd()
import random
import numpy as np
import base64
from neo4j import GraphDatabase
import os
from tqdm import tqdm
import time
import pickle
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv
load_dotenv()

wd = os.getcwd()
np.random.seed(20)
wd2 = r"C:\Users\abhis\.Neo4jDesktop\relate-data\dbmss\dbms-4572405c-e975-4a55-a4f9-6cadbed1118c\import"
limit = None #This is for Other nodes outside the class
#%%

df = pd.read_csv(wd+"\\Supply_Chain_Shipment_Pricing_Dataset.csv").head(limit)

#%%

api_field_names = [
    "id",
    "project_code",
    "pq",
    "po_so",
    "asn_dn",
    "country",
    "managed_by",
    "fulfill_via",
    "vendor_inco_term",
    "shipment_mode",
    "pq_first_sent_to_client_date",
    "po_sent_to_vendor_date",
    "scheduled_delivery_date",
    "delivered_to_client_date",
    "delivery_recorded_date",
    "product_group",
    "sub_classification",
    "vendor",
    "item_description",
    "molecule_test_type",
    "brand",
    "dosage",
    "dosage_form",
    "unit_of_measure_per_pack",
    "line_item_quantity",
    "line_item_value",
    "pack_price",
    "unit_price",
    "manufacturing_site",
    "first_line_designation",
    "weight_kilograms",
    "freight_cost_usd",
    "line_item_insurance_usd"
]

df.columns = api_field_names
df.isna().sum()[df.isna().sum()>0].plot(kind='bar')
df['weight_kilograms'] = pd.to_numeric(df['weight_kilograms'],errors='coerce').fillna(0)
df['freight_cost_usd'] = pd.to_numeric(df['freight_cost_usd'],errors='coerce').fillna(0)
df = df[df['shipment_mode'].notna()]
#%%

def plotUniqueValues(data,title,cols,output_file_name):
    # List of columns to analyze
    columns_to_analyze = cols

    # Calculate the number of unique values in each column
    unique_counts = data[columns_to_analyze].nunique()
    
    # Create a seaborn bar plot
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    bar_plot = sns.barplot(x=[x.title() for x in unique_counts.index], y=unique_counts.values, palette="viridis")
    
    # Add labels and title
    bar_plot.set_ylabel('Values')
    bar_plot.set_title(title)
    plt.savefig(output_file_name+'.png')
    # Show the plot
    
    plt.show()
    
plotUniqueValues(df,"Dataset Overview",['project_code','country','vendor','brand','molecule_test_type','managed_by'],'dataset_overview')    
#plotUniqueValues(df,"Product Overview",['managed_by','shipment_mode','fulfill_via'],'product_overview')    
#%%
import textwrap
import squarify
# Calculate the size of each column
column_sizes = df.count().reset_index()
column_sizes.columns = ['Column', 'Count']

# Create a tree map
plt.figure(figsize=(12, 8))
squarify.plot(sizes=column_sizes['Count'], label=[textwrap.fill(x.replace("_"," ").title(),8) for x in column_sizes['Column']], alpha=0.8, color=sns.color_palette("viridis", len(column_sizes)))

# Add title
plt.title('Dataset Treemap')
plt.axis('off')  # Remove axes

# Save the plot to a file
plt.savefig('About_Dataset.png')

# Show the plot
plt.show()
#%%
df.to_csv("Clean_Supply_Chain_data.csv",index=False)
df.to_csv(wd2+"\Clean_Supply_Chain_data.csv",index=False)