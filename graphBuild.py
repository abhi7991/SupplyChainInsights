# -*- coding: utf-8 -*-
"""
Created on Sun Jul 14 16:36:06 2024

@author: abhis
"""

import re
import os
import pandas as pd
wd = os.getcwd()
import random
import numpy as np
import base64
from neo4j import GraphDatabase
import os
from tqdm import tqdm
import time
import pickle
import warnings
from dotenv import load_dotenv
warnings.filterwarnings("ignore")

load_dotenv()

wd = os.getcwd()
np.random.seed(20)

limit2 = 1000 #This is for Other nodes outside the class

def read_params_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        return [line.strip() for line in lines]   

def read_params_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        return [line.strip() for line in lines]   

class createGraph:

    def __init__(self, uri, user, password,database):
        # database = 'movies.main'
        self.driver = GraphDatabase.driver(uri, auth=(user, password), database = database, max_connection_lifetime=200)

    def close(self):
        self.driver.close()

    def createConstraint(self):
        query1 = "CREATE CONSTRAINT unique_product_id IF NOT EXISTS FOR (p:Product) REQUIRE (p.pid) IS NODE KEY;"
        query2 = "CREATE CONSTRAINT unique_country_id IF NOT EXISTS FOR (p:Country) REQUIRE (p.name) IS NODE KEY;"
        query3 = "CREATE CONSTRAINT unique_vendor_id IF NOT EXISTS FOR (p:Vendor) REQUIRE (p.name) IS NODE KEY;"
        query4 = "CREATE CONSTRAINT unique_brand_id IF NOT EXISTS FOR (p:Brand) REQUIRE (p.name) IS NODE KEY;"
        query5 = "CREATE CONSTRAINT unique_pg_id IF NOT EXISTS FOR (p:Product_Group) REQUIRE (p.name) IS NODE KEY;"
        query6 = "CREATE CONSTRAINT unique_class_id IF NOT EXISTS FOR (p:Sub_Class) REQUIRE (p.name) IS NODE KEY;"
        query7 = "CREATE CONSTRAINT unique_office_id IF NOT EXISTS FOR (p:Office) REQUIRE (p.name) IS NODE KEY;"

        with self.driver.session() as session:
            session.run(query1)
            session.run(query2)
            session.run(query3)
            session.run(query4)
            session.run(query5)
            session.run(query6)
            session.run(query7)
    def load_products_from_csv(self, csv_file):
        
        '''
        
        Ensure the 'csv' file is in the import folder 
        linked to Neo4j
        
        '''
        print(f"LIMIT {self.limit}" if self.limit is not None else "No LIMIT set")
        with self.driver.session() as session:
            # Cypher query to load products from CSV
            query = (
                "LOAD CSV WITH HEADERS FROM $csvFile AS row "
                "WITH row WHERE row.id IS NOT NULL "  # Filter out rows with null id
                + (f"LIMIT {self.limit} " if self.limit is not None else "") +
                "MERGE (m:Product {pid: toInteger(row.id)}) "
                "ON CREATE SET m.project_code = row.project_code, "
                "m.price_quote = row.pq, "
                "m.molecule_test_type = row.molecule_test_type, "
                "m.unit_of_measure_per_pack = row.unit_of_measure_per_pack, "
                "m.line_item_quantity = row.line_item_quantity, "
                "m.pack_price = row.pack_price, "
                "m.molecule_test_type = row.molecule_test_type, "                                
                "m.item_description = row.item_description, "                
                "m.shipment_number = row.asn_dn" 
            )



            session.run(query, csvFile=f'file:///{csv_file}', limit=self.limit)
            print(f"Data Uploaded to Neo4j desktop for the first {self.limit} rows")

            
    limit = None            
    def drop_data(self):
        with self.driver.session() as session:
            # Check if data exists before attempting to delete
            check_query = "MATCH (n) RETURN count(n) AS count"
            result = session.run(check_query)
            count = result.single()["count"]

            if count > 0:
                # Data exists, proceed with dropping indices and deleting data
                    
                try: 
                    session.run("DROP CONSTRAINT unique_product_id IF EXISTS;")
                except:
                    print("No constraint to drop : unique_movie_id")

                try: 
                    session.run("DROP CONSTRAINT unique_country_id IF EXISTS;")
                except:
                    print("No constraint to drop : unique_country_id")

                try: 
                    session.run("DROP CONSTRAINT unique_vendor_id IF EXISTS;")
                except:
                    print("No constraint to drop : unique_vendor_id")      
                try: 
                    session.run("DROP CONSTRAINT unique_brand_id IF EXISTS;")
                except:
                    print("No constraint to drop : unique_brand_id")              

                try: 
                    session.run("DROP CONSTRAINT unique_pg_id IF EXISTS;")
                except:
                    print("No constraint to drop : unique_pg_id")       

                try: 
                    session.run("DROP CONSTRAINT unique_class_id IF EXISTS;")
                except:
                    print("No constraint to drop : unique_class_id")                  

                try: 
                    session.run("DROP CONSTRAINT unique_office_id IF EXISTS;")
                except:
                    print("No constraint to drop : unique_office_id")                      
#                delete_data_query = (
#                        "CALL apoc.periodic.iterate("
#                        '"MATCH (n) RETURN n", "DETACH DELETE n", {batchSize: 10000});'
#                    )
#                session.run(delete_data_query)
                try:    
                    query = "MATCH (n) with n limit 30000 DETACH DELETE n;"
                    for i in range(1,100):
                        session.run(query)              
                except:
                    query = """CALL apoc.periodic.iterate(
                        "MATCH (n) RETURN n", "DETACH DELETE n", {batchSize: 100});"""
                    session.run(query)
                print("All indices dropped and data deleted")
            else:
                print("No data to delete")
                
    def load_countries(self):
        
        with self.driver.session() as session:        

                
            create_country_node = """CALL apoc.periodic.iterate(
                    'LOAD CSV WITH HEADERS FROM "file:///Clean_Supply_Chain_data.csv" AS row RETURN row', 
                    'MERGE (pc:Country {name: row.country})', 
                    { batchSize: 100}
                ) YIELD batches, total, errorMessages;
                """
            create_country_relay = """CALL apoc.periodic.iterate(
                    'LOAD CSV WITH HEADERS FROM "file:///Clean_Supply_Chain_data.csv" AS row RETURN row', 
                        'MATCH (m:Product {pid: TOINTEGER(row.id)}) ' +
                        'MATCH (pc:Country {name: row.country}) ' +
                        'MERGE (m)-[r:WEIGHT { weight: toFloat(coalesce(row.wight_kilograms, 0.0)) }]->(pc) ', 
                        { batchSize: 100}
                    ) YIELD batches, total, errorMessages;
                    """   
            session.run(create_country_node)        
            session.run(create_country_relay)
        print("Countries Uploaded")        

    def load_vendor(self):
        
        with self.driver.session() as session:        

                
            create_vendor_node = """CALL apoc.periodic.iterate(
                    'LOAD CSV WITH HEADERS FROM "file:///Clean_Supply_Chain_data.csv" AS row RETURN row', 
                    'MERGE (pc:Vendor {name: row.vendor})', 
                    { batchSize: 100}
                ) YIELD batches, total, errorMessages;
                """
            create_vendor_relay = """CALL apoc.periodic.iterate(
                    'LOAD CSV WITH HEADERS FROM "file:///Clean_Supply_Chain_data.csv" AS row RETURN row', 
                        'MATCH (m:Product {pid: TOINTEGER(row.id)}) ' +
                        'MATCH (pc:Vendor {name: row.vendor}) ' +
                        'MERGE (pc)-[r:VENDOR]->(m) ', 
                        { batchSize: 100}
                    ) YIELD batches, total, errorMessages;
                    """   
            session.run(create_vendor_node)        
            session.run(create_vendor_relay)
        print("Vendors Uploaded")        
        

    def load_brand(self):
        
        with self.driver.session() as session:        

                
            create_brand_node = """CALL apoc.periodic.iterate(
                    'LOAD CSV WITH HEADERS FROM "file:///Clean_Supply_Chain_data.csv" AS row RETURN row', 
                    'MERGE (pc:Brand {name: row.brand})', 
                    { batchSize: 100}
                ) YIELD batches, total, errorMessages;
                """
            create_brand_relay = """CALL apoc.periodic.iterate(
                    'LOAD CSV WITH HEADERS FROM "file:///Clean_Supply_Chain_data.csv" AS row RETURN row', 
                        'MATCH (m:Product {pid: TOINTEGER(row.id)}) ' +
                        'MATCH (pc:Brand {name: row.brand}) ' +
                        'MERGE (m)-[r:BRAND]->(pc) ', 
                        { batchSize: 100}
                    ) YIELD batches, total, errorMessages;
                    """   
            session.run(create_brand_node)        
            session.run(create_brand_relay)
        print("Brand Uploaded")        

    def load_product_group(self):
        
        with self.driver.session() as session:        

                
            create_pg_node = """CALL apoc.periodic.iterate(
                    'LOAD CSV WITH HEADERS FROM "file:///Clean_Supply_Chain_data.csv" AS row RETURN row', 
                    'MERGE (pc:Product_Group {name: row.product_group})', 
                    { batchSize: 100}
                ) YIELD batches, total, errorMessages;
                """
            create_pg_relay = """CALL apoc.periodic.iterate(
                    'LOAD CSV WITH HEADERS FROM "file:///Clean_Supply_Chain_data.csv" AS row RETURN row', 
                        'MATCH (m:Product {pid: TOINTEGER(row.id)}) ' +
                        'MATCH (pc:Product_Group {name: row.product_group}) ' +
                        'MERGE (m)-[r:GROUP]->(pc) ', 
                        { batchSize: 100}
                    ) YIELD batches, total, errorMessages;
                    """   
            session.run(create_pg_node)        
            session.run(create_pg_relay)
        print("Product Group Uploaded")             

    def load_sub_class(self):
        
        with self.driver.session() as session:        

                
            create_class_node = """CALL apoc.periodic.iterate(
                    'LOAD CSV WITH HEADERS FROM "file:///Clean_Supply_Chain_data.csv" AS row RETURN row', 
                    'MERGE (pc:Sub_Class {name: row.sub_classification})', 
                    { batchSize: 100}
                ) YIELD batches, total, errorMessages;
                """
            create_class_relay = """CALL apoc.periodic.iterate(
                    'LOAD CSV WITH HEADERS FROM "file:///Clean_Supply_Chain_data.csv" AS row RETURN row', 
                        'MATCH (m:Product {pid: TOINTEGER(row.id)}) ' +
                        'MATCH (pc:Sub_Class {name: row.sub_classification}) ' +
                        'MERGE (m)-[r:SUB_CLASS]->(pc) ', 
                        { batchSize: 100}
                    ) YIELD batches, total, errorMessages;
                    """   
            session.run(create_class_node)        
            session.run(create_class_relay)
        print("Sub Class Uploaded")   

    def load_office(self):
        
        with self.driver.session() as session:        

                
            create_office_node = """CALL apoc.periodic.iterate(
                    'LOAD CSV WITH HEADERS FROM "file:///Clean_Supply_Chain_data.csv" AS row RETURN row', 
                    'MERGE (pc:Office {name: row.managed_by})', 
                    { batchSize: 100}
                ) YIELD batches, total, errorMessages;
                """
            create_office_relay = """CALL apoc.periodic.iterate(
                    'LOAD CSV WITH HEADERS FROM "file:///Clean_Supply_Chain_data.csv" AS row RETURN row', 
                        'MATCH (m:Product {pid: TOINTEGER(row.id)}) ' +
                        'MATCH (pc:Office {name: row.managed_by}) ' +
                        'MERGE (pc)-[r:MANAGED_BY]->(m) ', 
                        { batchSize: 100}
                    ) YIELD batches, total, errorMessages;
                    """   
            session.run(create_office_node)        
            session.run(create_office_relay)
        print("Sub Class Uploaded")          

def create_movie_graph():
    start = time.time()
    database = os.getenv('NEO4J_DATABASE')
    uri, user, password = os.getenv('NEO4J_URI'), os.getenv('NEO4J_USER'),'@PromptEngg'
    supplyChain = createGraph(uri, user, password,database)
    del password
    
    reCreate = True
    if reCreate:

        supplyChain.drop_data()
        supplyChain.createConstraint()
        supplyChain.load_products_from_csv("Clean_Supply_Chain_data.csv")#Linked to Import Folder of neo4j
        supplyChain.load_countries()        
        supplyChain.load_vendor() 
        supplyChain.load_brand()
        supplyChain.load_product_group()
        supplyChain.load_sub_class()           
        supplyChain.load_office()
    end = time.time()
    print("Elapsed Time : ", end - start)
    
    
if __name__ == "__main__":
    create_movie_graph()  
    
    