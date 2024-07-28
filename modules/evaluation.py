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
from modules import plot_vector_search
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
uri, user, password = os.getenv('NEO4J_URI'), os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD')
gds = GraphDataScience(
    uri,
    auth = (user, password), database=database
)       

def graph_init():
     '''
     One time process - Incase starting from scratch use this to create graph, and embeddings for plot
     '''
#     graph_build.create_movie_graph()
#     create_plot_embeddings.create_plot_embeddings()
    
def chat_bot(query):
    '''
    Chatbot with functions to answer questions related to the movies
    '''
    tools=[plot_vector_search.vectorSearch]
    functions = [format_tool_to_openai_function(f) for f in tools]
    model = ChatOpenAI(temperature=0).bind(functions=functions)
    memory = ConversationBufferMemory(return_messages=True,memory_key="chat_history")

    promptengg = "You are a helpful assistant and you shouldnt talk about anything except World Cinema. Only respond to queries related to movies, movie recommendations, or movie genres"

    prompt = ChatPromptTemplate.from_messages([
        ("system", promptengg),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    chain = RunnablePassthrough.assign(
        agent_scratchpad = lambda x: format_to_openai_functions(x["intermediate_steps"])
    ) | prompt | model | OpenAIFunctionsAgentOutputParser()
    qa = AgentExecutor(agent=chain, tools=tools, verbose=False, memory=memory,return_intermediate_steps=True)
    result = qa.invoke({"input": query})
    answer = result#['output']  # The chatbot's answer
    return answer  