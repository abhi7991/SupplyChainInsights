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