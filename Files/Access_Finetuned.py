# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 20:46:53 2024

@author: abhis
"""

import requests
import json

r = requests.get("http://localhost:1234/v1/models")
vals = json.loads(r.text)

#myModel = [x for x in vals['data'] if x['id']=='unsloth.Q4_K_M-2']
#%%
#%%
import time
t0 = time.time()
data = { 
  "messages": [ 
    { "role": "system", "content": "Given an input question, convert it to a Cypher query. No pre-amble." },
    { "role": "human", "content": "Based on the Neo4j graph schema below, write a Cypher query that would answer the user's question: \n{schema} \nQuestion: {question} \nCypher query:" }
  ], 
  "temperature": 0.7, 
  "max_tokens": 512,
  "stream": False
}

headers = {'Content-Type': 'application/json'}
      
r= requests.post("http://localhost:1234/v1/chat/completions",json = data,headers=headers)

t1 = time.time()
total = t1-t0
print("Training Time : ", total)
#%%
import os 
wd = os.getcwd()
import pandas as pd

# Print the loaded data (optional)
df = pd.read_json(wd + "/fine_tuning/datasets/text2cypher_batch_output.jsonl", lines=True)

import pandas as pd
import json

def convert_csv_to_jsonl(csv_file_path, jsonl_file_path):
    # Read the CSV file
    df = pd.read_csv(csv_file_path)
    
    # Define the base template for each message set
    base_template = {
        "messages": [
            {"role": "system", "content": "You are an assistant that helps convert user questions to Cypher queries."},
            {"role": "user", "content": ""},
            {"role": "assistant", "content": ""}
        ]
    }
    
    # List to hold the JSON lines
    json_lines = []
    
    # Iterate through the DataFrame rows
    for index, row in df.iterrows():
        # Copy the base template
        message_set = base_template.copy()
        # Set the user content to the question
        message_set["messages"][1]["content"] = row["question"]
        # Set the assistant content to the Cypher query
        message_set["messages"][2]["content"] = row["cypher"]
        
        # Convert the message set to a JSON line
        json_line = json.dumps(message_set)
        json_lines.append(json_line)
    
    # Write the JSON lines to a file
    with open(jsonl_file_path, 'w') as jsonl_file:
        for line in json_lines:
            jsonl_file.write(line + '\n')

# Example usage
csv_file_path = wd + "/fine_tuning/datasets/text2cypher_gpt3.5turbo.csv"
jsonl_file_path = wd + "/fine_tuning/datasets/GPT3.5_Training_Data.jsonl"
convert_csv_to_jsonl(csv_file_path, jsonl_file_path)
#%%
#df = pd.read_json(wd + "/fine_tuning/datasets/GPT3.5_Training_Data.jsonl", lines =True)
