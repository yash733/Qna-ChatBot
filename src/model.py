from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

class Model:
    def __init__(self,model_name):
        self.model_name = model_name

    def Groq_llm(self,api):
        return ChatGroq(model=self.model_name, api_key= api)
    
    def Ollama_llm(self):
        return ChatOllama(model=self.model_name)