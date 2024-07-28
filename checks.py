# -*- coding: utf-8 -*-
"""
Created on Sun Jul 28 14:55:13 2024

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


df = pd.read_csv(wd2+"\Clean_Supply_Chain_data.csv")
df['item_description'].unique()

df = df[df['country']=='Vietnam']
print(df['item_description'])
#%%