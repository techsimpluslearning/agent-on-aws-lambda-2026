from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents import create_agent
import requests
import os

API_BASE_URL = os.getenv("API_BASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4.1", api_key=OPENAI_API_KEY)

def get_products(url):
    response = requests.get(url)
    if response.status_code == 200:
        products = response.json()
        all_products: list[dict] = []
        for product in products.get("products", []):
            product.pop("reviews")
            all_products.append(product)

        return all_products
    
    return "Unable to fetch the products"


@tool
def get_all_categories():
    """Get all products categories list"""

    url = f"{API_BASE_URL}/products/categories"
    response = requests.get(url)
    if response.status_code == 200:
        categories = response.json()
        return [ {"slug": category.get("slug"), "name": category.get("name")} for category in categories ]
    return "Unable to fetch the category list"


@tool
def get_all_products():
    "Get all products and its details"
    url = f"{API_BASE_URL}/products"
    return get_products(url)


@tool
def search_products(search_query:str):
    """
        Search Product by user search query.
        Args:
            search_query - user search query string
    """

    url = f"{API_BASE_URL}/products/search?q={search_query}"
    return get_products(url)

@tool
def search_products_by_category(category_name:str):
    """
        Search Product by product category.
        Args:
            category_name - product category name
    """
    url = f"{API_BASE_URL}/products/category/{category_name}"
    return get_products(url)

@tool
def get_single_product(product_id:int):
    """
        Get Single Product Details with product reviews
        Args:
            product_id - product id to get single product
    """
    url = f"{API_BASE_URL}/products/{product_id}"
    response = requests.get(url)
    if response.status_code == 200:
        product = response.json()
        return product
    return "Unable to fetch the category list"


def getAgent():
    agent = create_agent(
        model=llm,
        tools=[get_all_categories, get_all_products, get_single_product, search_products, search_products_by_category],
        system_prompt="""
            You are product search agent, based on the user request you can call the different tools to fetch the product details.
            Available Tools:
                - get_all_categories : Fetch all the product category
                - get_all_products : Fetch all the products
                - get_single_product: Get Single Product by a Product ID
                - search_products : Search Product for user query
                - search_products_by_category: Search Product for specific category
        """
    )

    return agent


while True:
    query = input("User: ")
    if query == "quit":
        break

    res = getAgent().invoke({"messages": [ {"role":"user", "content": query} ]})
    result = res["messages"][-1].content
    print("AI: ", result)


