# -*- coding: utf-8 -*-
"""
Created on Sat Apr 13 11:16:27 2024

@author: abhis
"""

import matplotlib.pyplot as plt    
import pandas as pd
from neo4j import GraphDatabase
import os
import time   
import pandas as pd
from neo4j import GraphDatabase
import os
import time
from graphdatascience import GraphDataScience
from langchain_core.tools import tool
from pydantic.v1 import BaseModel, Field

wd = os.getcwd()

def read_params_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        return [line.strip() for line in lines]   
        
database = 'movies.main'    

# uri, user, password = read_params_from_file(wd+"\\params.txt") 
uri, user, password = os.getenv('NEO4J_URI'), os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD')
driver = GraphDatabase.driver(uri, auth=(user, password), max_connection_lifetime=200)
gds = GraphDataScience(
    uri,
    auth = (user, password), database=database
)       

del1 = "CALL gds.graph.drop('movies2',false);"
del2 = "CALL gds.graph.drop('movies3',false);"


gds.run_cypher(del1)
gds.run_cypher(del2)

## Subgraph1 - All the attributes, incoming towards Movies
query1 = """CALL gds.graph.project('movies2', 
              ['Movie','Genre','User','Person','SpokenLanguage','ProductionCompany','Country'], 
              {RATING:{properties:'rating',orientation:'REVERSE'},
              GENRE:{orientation:'REVERSE'},
              ACTED_IN:{orientation:'REVERSE'},
              CREWED_IN:{orientation:'REVERSE'},
              LANGUAGE:{orientation:'REVERSE'},
              PRODUCED_BY:{orientation:'REVERSE'},
              COUNTRY:{orientation:'REVERSE'}}   
            );"""


a = gds.run_cypher(query1)
print(a)

## Subgraph2 - Outwards from movies, default directions
query2 = """CALL gds.graph.project('movies3', 
              ['Movie','Genre','User','Person','ProductionCompany'], 
              {RATING:{properties:'rating'},
              GENRE:{},
              ACTED_IN:{},
              CREWED_IN:{}, PRODUCED_BY:{}}  
            );"""
            
a = gds.run_cypher(query2)
print(a)

## Entity - To find similar nodes around
## relationship - relationship or basis of recommendation
 #Similar movies based on user rating
    #Similar movies based on Genre
    #Find Movies based on similar actors    
    #Find Similar Personalities to a director 
    #Find Similar Actors      
    #Find Non-Similar Actors  
    #Find Movies based on Production Company   
    #Find Similar Movies by Region   
    #Find Similar Movies by Language   
    #Find a director an actor should work with ? 
    #General if relationship is None 
    
class SearchInput(BaseModel):
    entity: str = Field(...,description="Entity name")
    relationship: str = Field(...,description="Basis of recommendation around which similarity needs to be found. It would be only out of these options - user ratings,actor,genre,director,similar actor,nonsimilar actor,production house,country,language,work or country language")
    
    
    
@tool(args_schema=SearchInput)
def getSimilar(entity: str,relationship:str='') -> list: 
    """
    Recommend similar entities likes Movies, Actors, directors based on some relationship like user ratings, genres, production houses or other similar entities
    """
    
    #Similar movies based on user rating
    if relationship.lower()=='user rating':
        node = """
        MATCH (m:Movie)
        WHERE tolower(m.name) = '"""+entity.lower()+"""'
        WITH id(m) AS sourceNodeId
        CALL gds.nodeSimilarity.filtered.stream('movies2',{
            nodeLabels:['Movie','User','SpokenLanguage'],
            relationshipTypes:['RATING','LANGUAGE'],
            sourceNodeFilter: sourceNodeId,
            targetNodeFilter:'Movie'
        })
        YIELD node1, node2, similarity
        RETURN gds.util.asNode(node1).name AS Entity1, gds.util.asNode(node2).name AS Entity2, similarity
        ORDER BY similarity DESCENDING, Entity1, Entity2
        """        
    #Similar movies based on Genre
    elif relationship.lower()=='genre':
        node = """
        MATCH (m:Movie)
        WHERE tolower(m.name) = '"""+entity.lower()+"""'
        WITH id(m) AS sourceNodeId
        CALL gds.nodeSimilarity.filtered.stream('movies2',{
            nodeLabels:['Movie','Genre'],
            relationshipTypes:['GENRE'],
            sourceNodeFilter: sourceNodeId,
            targetNodeFilter:'Movie'
        })
        YIELD node1, node2, similarity
        RETURN gds.util.asNode(node1).name AS Entity1, gds.util.asNode(node2).name AS Entity2, similarity
        ORDER BY similarity DESCENDING, Entity1, Entity2
        """     
    #Find Movies based on similar actors    
    elif relationship.lower()=='actor':
        node = """
        MATCH (m:Movie)
        WHERE tolower(m.name) = '"""+entity.lower()+"""'
        WITH id(m) AS sourceNodeId
        CALL gds.nodeSimilarity.filtered.stream('movies2',{
            nodeLabels:['Movie','Person'],
            relationshipTypes:['ACTED_IN'],
            sourceNodeFilter: sourceNodeId,
            targetNodeFilter:'Movie'
        })
        YIELD node1, node2, similarity
        RETURN gds.util.asNode(node1).name AS Entity1, gds.util.asNode(node2).name AS Entity2, similarity
        ORDER BY similarity DESCENDING, Entity1, Entity2
        """  
    #Find Similar Personalities to a director    
    elif relationship.lower()=='director':
        node = """
        MATCH (m:Movie)<-[c:CREWED_IN{character:'Directing'}]-(p:Person)
        WHERE tolower(m.name) = '""" + entity.lower() + """'
        WITH id(m) AS sourceNodeId,id(p) as directorNodeId
        CALL gds.nodeSimilarity.filtered.stream('movies3',{
            nodeLabels:['Movie','Person'],
            relationshipTypes:['CREWED_IN','ACTED_IN'],
            sourceNodeFilter: directorNodeId,
            targetNodeFilter: 'Person'
        })
        YIELD node1, node2, similarity
        RETURN gds.util.asNode(node1).name AS Entity1, gds.util.asNode(node2).name AS Entity2, similarity
        ORDER BY similarity DESCENDING, Entity1, Entity2
        """        
    #Find Similar Actors    
    elif relationship.lower()=='similar actor':
        node = """
        MATCH (p:Person)
        WHERE tolower(p.name) = '""" + entity.lower() + """'
        WITH id(p) as actorNodeId
        CALL gds.nodeSimilarity.filtered.stream('movies3',{
            nodeLabels:['Movie','Person'],
            relationshipTypes:['ACTED_IN'],
            sourceNodeFilter: actorNodeId,
            targetNodeFilter: 'Person',
            topk:20
        })
        YIELD node1, node2, similarity
        RETURN gds.util.asNode(node1).name AS Entity1, gds.util.asNode(node2).name AS Entity2, similarity
        ORDER BY similarity DESCENDING, Entity1, Entity2
        """      
    #Find Non-Similar Actors      
    elif relationship.lower()=='nonsimilar actor':
        node = """
        MATCH (p:Person)
        WHERE tolower(p.name) = '""" + entity.lower() + """'
        WITH id(p) as actorNodeId
        CALL gds.nodeSimilarity.filtered.stream('movies3',{
            nodeLabels:['Movie','Person'],
            relationshipTypes:['ACTED_IN'],
            sourceNodeFilter: actorNodeId,
            targetNodeFilter: 'Person',
            bottomk:20
        })
        YIELD node1, node2, similarity
        RETURN gds.util.asNode(node1).name AS Entity1, gds.util.asNode(node2).name AS Entity2, similarity
        ORDER BY similarity DESCENDING, Entity1, Entity2
        """
    #Find Movies based on Production Company   
    elif relationship.lower()=='production house':
        node = """
       MATCH (m:Movie)
        WHERE tolower(m.name) = '"""+entity.lower()+"""'
        WITH id(m) AS sourceNodeId
        CALL gds.nodeSimilarity.filtered.stream('movies2',{
            nodeLabels:['Movie','ProductionCompany'],
            relationshipTypes:['PRODUCED_BY'],
            sourceNodeFilter: sourceNodeId,
            targetNodeFilter: 'Movie'
        })
        YIELD node1, node2, similarity
        RETURN gds.util.asNode(node1).name AS Entity1, gds.util.asNode(node2).name AS Entity2, similarity
        ORDER BY similarity DESCENDING, Entity1, Entity2
        """  
    #Find Similar Movies by Region   
    elif relationship.lower()=='country':
        node = """
       MATCH (m:Movie)
        WHERE tolower(m.name) = '"""+entity.lower()+"""'
        WITH id(m) AS sourceNodeId
        CALL gds.nodeSimilarity.filtered.stream('movies2',{
            nodeLabels:['Movie','Country'],
            relationshipTypes:['COUNTRY'],
            sourceNodeFilter: sourceNodeId,
            targetNodeFilter: 'Movie'
        })
        YIELD node1, node2, similarity
        RETURN gds.util.asNode(node1).name AS Entity1, gds.util.asNode(node2).name AS Entity2, similarity
        ORDER BY similarity DESCENDING, Entity1, Entity2
        """        
    #Find Similar Movies by Language   
    elif relationship.lower()=='language':
        node = """
       MATCH (m:Movie)
        WHERE tolower(m.name) = '"""+entity.lower()+"""'
        WITH id(m) AS sourceNodeId
        CALL gds.nodeSimilarity.filtered.stream('movies2',{
            nodeLabels:['Movie','Country','SpokenLanguage'],
            relationshipTypes:['LANGUAGE'],
            sourceNodeFilter: sourceNodeId,
            targetNodeFilter: 'Movie'
        })
        YIELD node1, node2, similarity
        RETURN gds.util.asNode(node1).name AS Entity1, gds.util.asNode(node2).name AS Entity2, similarity
        ORDER BY similarity DESCENDING, Entity1, Entity2
        """                        
    #Find Similar Movies by Region and Language?   
    elif relationship.lower()=='country language':
        node = """
       MATCH (m:Movie)
        WHERE tolower(m.name) = '"""+entity.lower()+"""'
        WITH id(m) AS sourceNodeId
        CALL gds.nodeSimilarity.filtered.stream('movies2',{
            nodeLabels:['Movie','Country','SpokenLanguage'],
            relationshipTypes:['LANGUAGE','COUNTRY'],
            sourceNodeFilter: sourceNodeId,
            targetNodeFilter: 'Movie'
        })
        YIELD node1, node2, similarity
        RETURN gds.util.asNode(node1).name AS Entity1, gds.util.asNode(node2).name AS Entity2, similarity
        ORDER BY similarity DESCENDING, Entity1, Entity2        
        """
    #Find Actors who have the worked the most with a director?   
    elif relationship.lower()=='work':
        node = """
        MATCH (p:Person)
        WHERE tolower(p.name) = '""" + entity.lower() + """'
        WITH id(p) as actorNodeId
        CALL gds.nodeSimilarity.filtered.stream('movies3',{
            nodeLabels:['Movie','Person'],
            relationshipTypes:['CREWED_IN'],
            sourceNodeFilter: actorNodeId,
            targetNodeFilter: 'Person',
            topk:20
        })
        YIELD node1, node2, similarity
        RETURN gds.util.asNode(node1).name AS Entity1, gds.util.asNode(node2).name AS Entity2, similarity
        ORDER BY similarity DESCENDING, Entity1, Entity2
        """
    #General if relationship is None       
    else:
        node = """
        MATCH (m:Movie)
        WHERE tolower(m.name) = '"""+entity.lower()+"""'
        WITH id(m) AS sourceNodeId
        CALL gds.nodeSimilarity.filtered.stream('movies2',{
            nodeLabels:['Movie','Person','User'],
            relationshipTypes:['CREWED_IN','ACTED_IN','RATING'],
            sourceNodeFilter: sourceNodeId,
            targetNodeFilter:'Movie'      
        })
        YIELD node1, node2, similarity
        RETURN gds.util.asNode(node1).name AS Entity1, gds.util.asNode(node2).name AS Entity2, similarity
        ORDER BY similarity DESCENDING, Entity1, Entity2
        """        
    # print(node)
    
    x = gds.run_cypher(node)
    
    x_list = x['Entity2'].head().tolist()
    
    return x_list


# df1 = getSimilar("harrison ford",'work')