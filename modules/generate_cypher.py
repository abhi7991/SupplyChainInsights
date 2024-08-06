import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from dotenv import load_dotenv
from langchain.prompts.prompt import PromptTemplate
from langchain.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI
from langchain.chains import GraphCypherQAChain
from langchain.chains import LLMChain
from graphdatascience import GraphDataScience
import json
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field
import re
#uri, user, password = os.getenv('NEO4J_URI'), os.getenv('NEO4J_USER'),'@PromptEngg'
load_dotenv()# username is neo4j by default
from openai import OpenAI
client = OpenAI()

NEO4J_USERNAME = os.getenv('NEO4J_USER')
NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_PASSWORD = '@PromptEngg'



graph = Neo4jGraph(
    url=NEO4J_URI, 
    username=NEO4J_USERNAME, 
    password=NEO4J_PASSWORD,
    database = 'neo4j'
)

gds = GraphDataScience(
    NEO4J_URI,
    auth = (NEO4J_USERNAME, NEO4J_PASSWORD), database='neo4j'
)       


class SearchInput(BaseModel):
    que: str = Field(...,description="this would be question by the user about writing a Cypher query, about accessing the database or just what type of query to write")


    
@tool(args_schema=SearchInput)
def finetuned(que:str)->str:    
    """Conversing with the knowledge graph after teaching GPT to create Cypher Querie"""


    myschema = graph.schema

    system_message = ("Based on the Neo4j graph schema below, write a Cypher query that would answer the user's question and: "
                          "\n{schema}").format(schema=myschema)

    completion = client.chat.completions.create(
      model="ft:gpt-3.5-turbo-1106:personal:prompt-finetuning:9t5kHnz9",
      messages=[
        {"role": "system", "content": system_message},
        {"role": "user", "content": que}
      ]
    )


    output = completion.choices[0].message.content

    return output
