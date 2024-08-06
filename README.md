# SupplyChain Insights

![alt text](Files/logo-color.png)

## [Overview](Files/ProjectOverview.pdf)

This repository contains a project focused on analyzing global health commodity supply chains, specifically Antiretroviral (ARV) and HIV lab shipments. The project utilizes neo4j graph databases, advanced graph data science techniques, and retrieval-augmented generation (RAG) for enhanced data exploration and insights. Additionally there is also a Fine tuned model which is produced using Llama3, Unsloth and HuggingFace. Model Fine tuning helps ensure that the data is not compromised by external LLMs and enables to query the data with ease.

## [Dataset](https://catalog.data.gov/dataset/supply-chain-shipment-pricing-data-07d29)
The dataset used in this project provides comprehensive information on supply chain health commodity shipments and pricing. It includes data on ARV and HIV lab shipments to supported countries, along with commodity pricing, supply chain expenses, and volumes delivered by country.

## Key Features

- Neo4j Graph Database: Constructs a graph database to model and analyze supply chain relationships.
- Retrieval-Augmented Generation (RAG): Implements RAG for enhanced data retrieval and user interaction.
- Fine Tuned Model with Cypher QA Chain trained.

## About RAG 

- Utilising vector search using OpenAI embeddings - This enables users to directly tap into key aspects of the data.
- Enabling Cypher QA Chain - With the help of Langchain we can convert a Natural Language Query to Cypher Query. 

## About Fine tuning 

- Utilising open source LLMs to handle natural laangyage queries. This is a test to see how good they perform with respect to my RAG 
application. Using custom training data, I haave trained the models on a set of questions and responses.

- To facilitate my Fine tuned models I have analysed 3 models which have been used in this analysis (linked to the respective HuggingFace Repo) 

	- [Phi3](https://huggingface.co/abhi7991/promptFineTuning) - SLM from Microsoft 
	- [Llama3 - 8b](https://huggingface.co/abhi7991/promptfinetuning-llama3) - Meta's Open Source Model 
	- [Llama3 - 8b (Developed by Neo4j)](https://huggingface.co/collections/tomasonjo/llama3-text2cypher-demo-6647a9eae51e5310c9cfddcf) -  Meta's Open Source Model fine tuned by Neo4j Developers

- For my [Phi3](https://huggingface.co/abhi7991/promptFineTuning) and Llama3 - 8b](https://huggingface.co/abhi7991/promptfinetuning-llama3) models I fine tuned them Using Unsloth 
- The models were processed on special platforms like [lightening.ai](lightening.ai) and Google Colab to make use of the GPU


**Refer to the notebooks below to get a deeper understanding of the entire fine tuning process as well as implentation**

- [Generating Training Data](fine_tuning/notebook/Generate_Training_Data2.ipynb)

- [Fine Tuning Phi3](fine_tuning/notebook/FineTuning_Phi3.ipynb)

- [Fine Tuning Llama3](fine_tuning/notebook/FineTuning_llama3.ipynb)

- [Comparing models Locally](fine_tuning/notebook/Comparing_FineTunedLLMs-Local.ipynb)
