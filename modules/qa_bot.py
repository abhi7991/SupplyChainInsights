import os
from dotenv import load_dotenv
from langchain.prompts.prompt import PromptTemplate
from langchain.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI
from langchain.chains import GraphCypherQAChain
from langchain.chains import LLMChain
import json
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field

#uri, user, password = os.getenv('NEO4J_URI'), os.getenv('NEO4J_USER'),'@PromptEngg'
load_dotenv()# username is neo4j by default


NEO4J_USERNAME = os.getenv('NEO4J_USER')
NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_PASSWORD = '@PromptEngg'

CYPHER_GENERATION_TEMPLATE = """You are an expert Neo4j Cypher translator specializing in supply chain analysis. Your task is to convert English questions into Cypher queries, strictly following the schema and instructions below:

<instructions>
* Use aliases to refer to nodes or relationships in the generated Cypher query.
* Generate Cypher queries compatible ONLY with Neo4j Version 5.
* Do not use `EXISTS` or `SIZE` keywords in the Cypher queries. Use aliases when using the `WITH` keyword.
* Use only the nodes and relationships mentioned in the provided schema.
* Always enclose the Cypher output inside three backticks (```)
* If no limit is specified give all the answers 
* Always perform a case-insensitive and fuzzy search for any property-related searches. For example, to search for a brand name, use `toLower(b.name) contains 'brandname'`.
* Cypher is NOT SQL, so do not mix and match the syntaxes.
</instructions>
Strictly use this schema for Cypher generation:

<schema>
{schema}
</schema>
Follow the samples below as they adhere to the instructions and schema provided:

<samples>
Human: What are the top 5 countries receiving the highest volume of shipments?
Assistant: ```MATCH (c:Country)<-[:DELIVERED_TO]-(s:Shipment) WITH c.name as Country, sum(s.volume) as TotalVolume RETURN Country, TotalVolume ORDER BY TotalVolume DESC LIMIT 5```
Human: Which vendors supply ARV products?
Assistant: MATCH (v:Vendor)-[:VENDOR]->(p:Product)-[:BELONGS_TO]->(:Product_Group {{name: 'ARV'}}) RETURN DISTINCT v.name as Vendor

Human: Give me the countries which Aurobindo Pharma Limited supplies to ?
Assistant: MATCH (c:Country)<-[:WEIGHT]-(p:Product)<-[:VENDOR]-(v:Vendor {{name: 'Aurobindo Pharma Limited'}}) RETURN DISTINCT c.name as Country;

Human: What are the average prices of ARV products in different countries?
Assistant: MATCH (p:Product)-[:BELONGS_TO]->(:Product_Group {{name: 'ARV'}})-[:HAS_PRICE]->(price:Price)-[:IN_COUNTRY]->(c:Country) RETURN c.name as Country, avg(price.value) as AveragePrice ORDER BY AveragePrice DESC

Human: Which product groups are most frequently shipped?
Assistant: MATCH (pg:Product_Group)<-[:BELONGS_TO]-(p:Product)<-[:CONTAINS]-(s:Shipment) RETURN pg.name as ProductGroup, count(s) as ShipmentCount ORDER BY ShipmentCount DESC LIMIT 5

Human: What is the total cost of shipments managed by a specific office?
Assistant: MATCH (o:Office {{name: 'SpecificOffice'}})<-[:MANAGED_BY]-(s:Shipment) RETURN o.name as Office, sum(s.cost) as TotalCost

Human: List all brands available for HIV lab shipments.
Assistant: MATCH (b:Brand)<-[:BELONGS_TO]-(p:Product)-[:BELONGS_TO]->(:Product_Group {{name: 'HIV Lab'}}) RETURN DISTINCT b.name as Brand
</samples>

Human: {question}
Assistant:
"""


CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=['schema','question'], validate_template=True, template=CYPHER_GENERATION_TEMPLATE
)



graph = Neo4jGraph(
    url=NEO4J_URI, 
    username=NEO4J_USERNAME, 
    password=NEO4J_PASSWORD,
    database = 'neo4j'
)

llm = ChatOpenAI(temperature=0,openai_api_key=os.getenv('OPENAI_API_KEY'))

chain = GraphCypherQAChain.from_llm(
    llm,
    graph=graph,
    cypher_prompt=CYPHER_GENERATION_PROMPT,
    verbose=True,
    return_direct=True
)

class SearchInput(BaseModel):
    que: str = Field(...,description="this would be question by the user about countries,vendors,Brands,and other attributres related to Products it will be used to query but not for recommendation")
    
    
    
@tool(args_schema=SearchInput)
def chat(que:str)->str:
    
    """Conversing with the Knowledge graph of Supply Chain, and will generate cypher queries to get answers"""
    
    r = chain.invoke(que)
    # print(r)
    summary_prompt = """Human: 
    Fact: {result}

    * Summarise the above fact as if you are answering this question "{query}"
    * When the fact is not empty, assume the question is valid and the answer is true
    * Do not return helpful or extra text or apologies
    * Just return summary to the user. DO NOT start with Here is a summary
    * List the results in rich text format if there are more than one results
    Assistant:
    """
    summary_prompt_template = PromptTemplate(input_variables=['query','result'], validate_template=True, template=summary_prompt)
    llmchain = LLMChain(llm=llm, prompt=summary_prompt_template)
    summary = llmchain.invoke({'query':r['query'],'result':json.dumps(r['result'])})
    
    return summary['text']

## Need to add output parsers