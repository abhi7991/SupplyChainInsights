# -*- coding: utf-8 -*-
"""
Created on Sun Jul 28 13:50:39 2024

@author: abhis
"""

import os
import sys
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
from modules import utils,ragas_eval
import pandas as pd


#a = pd.read_csv(os.getcwd()+"/evaluation_results.csv")
#utils.graph_init()
#print(ragas_eval.getEval(a))
print(utils.chat_bot("Help me construct a cypher query to access the count of products per country ??"))