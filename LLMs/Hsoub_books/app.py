import os
import sys
from openai import OpenAI
import openai
from langchain_community.document_loaders import TextLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_openai import OpenAI as LangChainOpenAI
import warnings

warnings.filterwarnings("ignore")

openai.api_key = os.getenv("OPENAI_API_KEY")

prompt = sys.argv[1]

loader = TextLoader("data.txt")
loader.load()

embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", api_key=openai.api_key)

index = VectorstoreIndexCreator(embedding=embeddings).from_loaders([loader])

llm = LangChainOpenAI(api_key=openai.api_key, temperature=0)

result = index.query(prompt, llm=llm, retriever_kwargs={"search_kwargs": {"k": 1}})
print(result)
