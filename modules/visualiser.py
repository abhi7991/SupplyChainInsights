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


NEO4J_USERNAME = os.getenv('NEO4J_USER')
NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_PASSWORD = '@PromptEngg'

CYPHER_GENERATION_TEMPLATE = """You are an expert Neo4j Cypher translator specializing in generating Cypher queries for visualizations in supply chain analysis. Your task is to convert English questions into Cypher queries, strictly following the schema and instructions below:

<instructions>
* Use aliases to refer to nodes or relationships in the generated Cypher query.
* Generate Cypher queries compatible ONLY with Neo4j Version 5.
* Do not use `EXISTS` or `SIZE` keywords in the Cypher queries. Use aliases when using the `WITH` keyword.
* Use only the nodes and relationships mentioned in the provided schema.
* Always enclose the Cypher output inside three backticks (```)
* If no limit is specified, provide all relevant data points for comprehensive visualization.
* Always perform a case-insensitive and fuzzy search for any property-related searches. For example, to search for a brand name, use `toLower(b.name) contains 'brandname'`.
* Cypher is NOT SQL, so do not mix and match the syntaxes.
* Ensure the query results are suitable for visual representation, such as bar charts, line charts, pie charts, scatter plots, maps, etc.
</instructions>

Strictly use this schema for Cypher generation:

<schema>
{schema}
</schema>

Follow the samples below as they adhere to the instructions and schema provided:

<samples>
Human: Show a bar chart of the top 5 countries by shipment volume.
Assistant: ```MATCH (c:Country)<-[:DELIVERED_TO]-(s:Shipment) WITH c.name as Country, sum(s.volume) as TotalVolume RETURN Country, TotalVolume ORDER BY TotalVolume DESC LIMIT 5```

Human: Visualize the price trends for ARV products by country.
Assistant: ```MATCH (p:Product)-[:BELONGS_TO]->(:Product_Group {{name: 'ARV'}})-[:HAS_PRICE]->(price:Price)-[:IN_COUNTRY]->(c:Country) RETURN c.name as Country, p.name as Product, price.value as Price ORDER BY Country, Product```

Human: Plot the distribution of shipment volumes for different vendors.
Assistant: ```MATCH (v:Vendor)-[:VENDOR]->(p:Product)-[:BELONGS_TO]->(:Product_Group {{name: 'ARV'}})-[:CONTAINS]->(s:Shipment) RETURN v.name as Vendor, sum(s.volume) as TotalVolume ORDER BY TotalVolume DESC```

Human: Show a scatter plot of product prices versus shipment volumes.
Assistant: ```MATCH (p:Product)-[:HAS_PRICE]->(price:Price), (p)-[:CONTAINS]->(s:Shipment) RETURN p.name as Product, price.value as Price, s.volume as Volume```

Human: Create a pie chart of the share of each vendor in the total shipments.
Assistant: ```MATCH (v:Vendor)-[:VENDOR]->(p:Product)-[:CONTAINS]->(s:Shipment) RETURN v.name as Vendor, sum(s.volume) as TotalVolume ORDER BY TotalVolume DESC```

Human: Visualize the number of products available by brand.
Assistant: ```MATCH (b:Brand)<-[:BELONGS_TO]-(p:Product) RETURN b.name as Brand, count(p) as ProductCount ORDER BY ProductCount DESC```

Human: Show the geographical distribution of HIV lab shipments.
Assistant: ```MATCH (c:Country)<-[:DELIVERED_TO]-(p:Product)-[:BELONGS_TO]->(:Product_Group {{name: 'HIV Lab'}}) RETURN c.name as Country, sum(p.volume) as TotalVolume```
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

gds = GraphDataScience(
    NEO4J_URI,
    auth = (NEO4J_USERNAME, NEO4J_PASSWORD), database='neo4j'
)       


llm = ChatOpenAI(temperature=0,openai_api_key=os.getenv('OPENAI_API_KEY'))

chain = GraphCypherQAChain.from_llm(
    llm,
    graph=graph,
    cypher_prompt=CYPHER_GENERATION_PROMPT,
    verbose=False,
    return_direct=True,
    return_intermediate_steps=True
)

class SearchInput(BaseModel):
    que: str = Field(...,description="this would be question by the user about visualaising or plotting the data around countries,vendors,Brands,and other attributres related to Products.")


def detect_plot_type(query):
    '''
    Detect the type of plot requested in the query.
    '''
    plot_keywords = {
        'Line Plot': ['line plot', 'line chart', 'trend line','line'],
        'Bar Chart': ['bar chart', 'bar plot', 'bar graph','bar'],
        'Scatter Plot': ['scatter plot', 'scatter graph', 'xy plot'],
        'Distribution Plot': ['distribution plot', 'histogram', 'density plot'],
        'Count Plot': ['count plot', 'count graph', 'frequency plot','count']
    }
    
    query_lower = query.lower()
    
    for plot_type, keywords in plot_keywords.items():
        if any(keyword in query_lower for keyword in keywords):
            return plot_type
    
    return None  # Return None if no plot type is detected
    
def generatePlot(input_data):
    
    df = input_data['data']
    query = input_data['Question']

    plot_type = detect_plot_type(query)

    if plot_type==None:
        return "Please Specify if you would like a specific plot like Line Plot, Bar Chart, Scatter Plot, Distribution Plot"

    fig, ax = plt.subplots(figsize=(30, 20))

    x_axis = df.columns[0]
    y_axis = df.columns[1]

    if plot_type == 'Line Plot':
        sns.lineplot(x=df.iloc[:, 0], y=df.iloc[:, 1], ax=ax)
    elif plot_type == 'Bar Chart':
        sns.barplot(x=df.iloc[:, 0], y=df.iloc[:, 1], ax=ax)
    elif plot_type == 'Scatter Plot':
        sns.scatterplot(x=df.iloc[:, 0], y=df.iloc[:, 1], ax=ax)
    elif plot_type == 'Distribution Plot':
        sns.histplot(df.iloc[:, 0], kde=True, ax=ax)
        y_axis='Density'
    elif plot_type == 'Count Plot':
        sns.countplot(x=df.iloc[:, 0], ax=ax)
        y_axis = 'Count'

    # # Plotting a bar chart
    # sns.barplot(x=df.iloc[:, 0], y=df.iloc[:, 1], ax=ax)

    # Rotate x-axis and y-axis labels
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels, align right
    plt.yticks(rotation=0)  # Y-axis labels, typically kept at 0 degrees

    # Adjust label sizes
    ax.tick_params(axis='x', labelsize=10)  # Adjust x-axis label size
    ax.tick_params(axis='y', labelsize=10)  # Adjust y-axis label size

    # Adjust title and axis labels with a smaller font size
    plt.title(f'{plot_type} of {y_axis} vs {x_axis}', fontsize=12)
    plt.xlabel(x_axis, fontsize=10)
    plt.ylabel(y_axis, fontsize=10)

    wd = os.getcwd()
    # Save the plot to a file
    image_path = f"plot_{plot_type.lower().replace(' ', '_')}.png"
    image_dir = os.path.join(os.getcwd(), "Saved")
    os.makedirs(image_dir, exist_ok=True)  # Create the directory if it doesn't exis 
    image_dir = image_dir+"//"+image_path  
    plt.savefig(image_dir)
    plt.close(fig)  # Close the figure to free memory    
    return image_dir
    # Show the results
    #plt.show()
    
@tool(args_schema=SearchInput)
def visualise(que:str)->str:    
    """Conversing with the knowledge graph of supply chain data, and will generate Cypher queries to get answers."""
    response = chain.invoke(que)
    cypher_query = response['intermediate_steps'][0]['query']
    data =  gds.run_cypher(cypher_query)
    output = {"Question":que,"Data":data}
    return output
