from modules.relationship import getRelationship
import os
from graphdatascience import GraphDataScience
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field
from dotenv import load_dotenv
load_dotenv()


        
database = 'neo4j'    

# uri, user, password = read_params_from_file(wd+"\\params.txt") 
uri, user, password = os.getenv('NEO4J_URI'), os.getenv('NEO4J_USER'),'@PromptEngg'
gds = GraphDataScience(
    uri,
    auth = (user, password), database=database
)       
class SearchInput(BaseModel):
    question: str = Field(...,description="The question asked by the user related to the product and its features. It essentially would not have countries, brands or vendors, but just a general statement or question about the product")
        
@tool(args_schema=SearchInput)
def vectorSearch(question: str) -> list:
    """
    Find movies based on the plot or genre of the movie using vector search on the question asked by the user on the plot or genre of the movie.
    """
    
    relationship = getRelationship(question)
    params={"openAiApiKey":os.getenv('OPENAI_API_KEY'),
            "openAiEndpoint": 'https://api.openai.com/v1/embeddings',
            "question": question,
            "top_k": 2}
    query = """
        WITH genai.vector.encode(
            $question, 
            "OpenAI", 
            {
              token: $openAiApiKey,
              endpoint: $openAiEndpoint
            }) AS question_embedding
        CALL db.index.vector.queryNodes(
            'product_embeddings2', 
            $top_k, 
            question_embedding
        ) YIELD node AS pdt, score
        WHERE pdt.pid IS NOT NULL """ + relationship + """
        RETURN pdt.pid as pid, pdt.molecule_test_type as molecule_test_type,pdt.item_description as item_description, score
        """
    
    # print(query)
    df = gds.run_cypher(query, 
        params = params)
    
    df['output'] = df['pid'].astype(str) + " " + df['molecule_test_type'] + " " + df['item_description']

    output = df['output'].to_list()

    return output
    