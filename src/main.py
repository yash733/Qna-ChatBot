import streamlit as st
import os, sys
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

from config.config import Config


"""
[User Input + Session ID]
        ↓
[get_session_history(session_id)]
        ↓
[RunnableWithMessageHistory]
        ↓
[rag_chain]
    ↓
    [create_history_aware_retriever]
        ↓
        [contextualize_q_prompt + chat_history]
        ↓
        [Standalone Question]
        ↓
        [retriever → Documents]
    ↓
    [create_stuff_documents_chain]
        ↓
        [qa_prompt + chat_history + documents]
        ↓
        [LLM → Final Answer]
        ↓
[Output + Message History Updated]
"""

os.environ['HUGGINFFACE_API'] = os.getenv('HUGGINFFACE_API')
os.environ['LANGSMITH_TRACING'] = os.getenv('LANGSMITH_TRACING')
os.environ['LANGCHIAN_PROJECT'] = os.getenv('LANGCHIAN_PROJECT')
os.environ['LANGSMITH_API_KEY'] = os.getenv('LANGSMITH_API_KEY')


class model_utility:
    def __init__(self):
        self.store = {}

    def prompt(self):
        message = ChatPromptTemplate.from_messages([
            MessagesPlaceholder(variable_name='chat_history'),
            {'role':'system', 'content':'You are an helpful assistant answer user query, if you have no context related to the query say "sorry I cant answer that for you", use this context: {context}'},
            {'role':'user', 'content': '{input}'}]
        )
        return message
    
    def data_extractor_web(self):
        #----- load 
        loader = WebBaseLoader(st.session_state.data) #-----------------------------------------------
        docs = loader.lazy_load()

        #----- transform
        text_spliter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 200)
        splited_data = text_spliter.split_documents(docs)

        embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        vectorstore = FAISS.from_documents(documents=splited_data, embedding= embedding)
        retriever = vectorstore.as_retriever()
        return retriever
    
    # ----- call
    def stuff_doc_chain(self):
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            {'role':'system', 'content':'''Given a chat history and the latest user question which might reference context in the chat history, 
            formulate a standalone question which can be understood without the chat history. Do NOT answer the question, 
            just reformulate it if needed and otherwise return it as is.'''},
            MessagesPlaceholder(variable_name='chat_history'),
            {'role':'user', 'content':'{input}'}
            ])
        
        history_aware = create_history_aware_retriever(
            llm = st.session_state.model, 
            prompt = contextualize_q_prompt, 
            retriever = self.data_extractor_web()
            )
        qna_chain = create_stuff_documents_chain(
            llm= st.session_state.model, 
            prompt= self.prompt()
            )
        rag_chain = create_retrieval_chain(history_aware, qna_chain)
        return rag_chain
    
    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]
    
    # def get_chat_history(self, session_id: str) -> list:
    #     """Get all messages from the chat history for a session"""
    #     history = self.get_session_history(session_id)
    #     return [(msg.type, msg.content) for msg in history.messages]

    def chat_history(self):
        conversational_rag_chain = RunnableWithMessageHistory(
            self.stuff_doc_chain(),
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
            )
        return conversational_rag_chain