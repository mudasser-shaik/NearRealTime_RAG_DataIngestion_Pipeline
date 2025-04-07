import os

from pymongo.mongo_client import MongoClient
import openai
from tabulate import tabulate

def product_vector_search():
    # Connect to your Atlas deployment
    uri ="mongodb+srv://dbuser_genai:R6WHZ7MB2KNLCIPC@cluster-genai.wcknb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster-GenAI"
    client = MongoClient(uri)

    # Access your database and collection
    database = client["retail"]
    collection = database["product"]

    # Set up OpenAI API Key
    # Or set directly: openai.api_key = "your_api_key"
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # query_text = "Find me formal winter wear for a male child price less than 20"
    # query_text = "I have a office party pick me clothes, Im 30 year old Male"
    query_text = "I have a office party pick me clothes, Im 30 year old Male"

    # Generate a 1536-dimensional vector using OpenAI
    response = openai.embeddings.create(input=query_text, model="text-embedding-ada-002")
    query_vector = response.data[0].embedding  # Extract the 1536-d vector

    # MongoDB Vector Search Query
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "vector",
                "queryVector": query_vector,
                "numCandidates": 100,
                "limit": 5,
                "metric": "dotProduct"
            }
        },
        {
            "$project": {  # Only include important fields
                "_id": 0,
                "product_id": 1,
                "brandName": 1,
                "articleType": 1,
                "ageGroup": 1,
                "price": 1,
                "store_id": 1,
                "season": 1
            }
        }
    ]

    # Execute search query
    results = list(collection.aggregate(pipeline))

    # Convert results into table format
    if results:
        table_data = [[res["product_id"], res["brandName"], res["articleType"], res["price"], res["store_id"], res["season"], res["ageGroup"]] for res in results]
        headers = ["Product ID", "Brand", "Type", "Price", "Store ID", "Season", "Age"]
        print(tabulate(table_data, headers, tablefmt="grid"))
    else:
        print("No matching products found.")


if __name__ == "__main__":
    product_vector_search()