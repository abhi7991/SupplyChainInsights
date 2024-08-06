# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 12:04:17 2024

@author: abhis
"""
import os 
wd = os.getcwd()
import pandas as pd
import json
'''
csv_file_path should contain a CSV which with columns 
1 - Questions
2 - Answers
'''
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