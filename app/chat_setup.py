from langchain_community.embeddings import OllamaEmbeddings
from langchain_google_genai import GoogleGenerativeAI
import os
from dotenv import load_dotenv
load_dotenv(override=True)

# embedding
embeddings = OllamaEmbeddings(model='nomic-embed-text', base_url=os.environ.get('LOCAL_EMBEDDING_URL')) 
# qdrant
qdrant_url = os.environ.get('QDRANT_URL')
# llm
llm = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=os.environ["GOOGLE_API_KEY_GEN"])
