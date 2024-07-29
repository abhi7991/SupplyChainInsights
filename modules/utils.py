# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 10:16:16 2024

@author: abhis
"""

import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir) 
import pandas as pd
from neo4j import GraphDatabase
import os
import requests
import json
import requests
import numpy as np
from graphdatascience import GraphDataScience
wd = os.getcwd()
from dotenv import load_dotenv
import graph_build,create_plot_embeddings
from modules import plot_vector_search,qa_bot,visualiser
import openai
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.tools.render import format_tool_to_openai_function
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.prompts import MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.agent import AgentFinish
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents import AgentExecutor


load_dotenv()

#openai.api_key = os.environ['OPENAI_API_KEY']
database = os.getenv('NEO4J_DATABASE')
uri, user, password = os.getenv('NEO4J_URI'), os.getenv('NEO4J_USER'),'@PromptEngg'
gds = GraphDataScience(
    uri,
    auth = (user, password), database=database
)       

def graph_init():
     '''
     One time process - Incase starting from scratch use this to create graph, and embeddings for plot
     '''
     print("Graph and Embeddings already Created - Check modules.utils to enable")
     #graph_build.create_logistics_graph()
     #create_plot_embeddings.create_plot_embeddings()
    
def chat_bot(query):
    '''
    Chatbot with functions to answer questions related to the movies
    '''
    tools=[plot_vector_search.vectorSearch,qa_bot.chat,visualiser.visualise]
    functions = [format_tool_to_openai_function(f) for f in tools]
    model = ChatOpenAI(temperature=0).bind(functions=functions)
    memory = ConversationBufferMemory(return_messages=True,memory_key="chat_history",run_intermediate_steps=True,return_direct=True)

    promptengg = """You are a helpful assistant specialized in providing insights and information related to supply chains, specifically focusing on the SupplyChainInsights application. Your expertise includes understanding and explaining the intricacies of supply chain data, including commodity shipments, pricing trends, and logistics. You should only respond to queries related to:

                Analyzing trends and ranges in the pricing of health commodities.
                Understanding the volume and movement of Antiretroviral (ARV) and HIV lab shipments.
                Insights into the supply chain logistics, including costs and lead times by product and country.
                Comparing and contrasting data from the SupplyChainInsights application with the Global Fund's Price, Quality, and Reporting (PQR) data.
                Any other questions related to understanding supply chain concepts, data, and insights within the context of the provided dataset.
                Please refrain from discussing topics outside of these areas. Your responses should be concise, informative, and tailored to help users make better data-driven decisions regarding supply chain management."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", promptengg),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    chain = RunnablePassthrough.assign(
        agent_scratchpad = lambda x: format_to_openai_functions(x["intermediate_steps"])
    ) | prompt | model | OpenAIFunctionsAgentOutputParser()
    qa = AgentExecutor(agent=chain, tools=tools, verbose=True, memory=memory,return_intermediate_steps=True)
    result = qa.invoke({"input": query})
    if result['intermediate_steps'][0][0].tool=='visualise':
        answer = result['intermediate_steps'][0][-1]
        answer['Tool'] = 'visualise'
    else:
        answer = result['output'] 
    return answer   