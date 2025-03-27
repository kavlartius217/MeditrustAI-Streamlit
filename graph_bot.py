#imports
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.neo4j_vector import Neo4jVector
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
import streamlit as st
from langchain_groq import ChatGroq
import os

rcts = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

# API KEYS
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
OPENAI_API_KEY=st.secrets['OPENAI_API_KEY']
os.environ['NEO4J_URI'] = "neo4j+s://15a09af2.databases.neo4j.io"
os.environ['NEO4J_USERNAME'] = "neo4j"
os.environ['NEO4J_PASSWORD'] = "7bfyGxtvdWQdLr8D9siRrP2Y0xVb0DxtFXHAL63kLR4"

# Loading the documents
doc_1 = TextLoader("/content/abnormalities (1).md")
doc_1 = doc_1.load()
doc_1 = rcts.split_documents(doc_1)

doc_2 = TextLoader("/content/doctors.md")
doc_2 = doc_2.load()
doc_2 = rcts.split_documents(doc_2)

doc_3 = TextLoader("/content/explained_report.md")
doc_3 = doc_3.load()
doc_3 = rcts.split_documents(doc_3)

doc = doc_1 + doc_2 + doc_3

# Creating the graph db
embeddings = OpenAIEmbeddings()
db = Neo4jVector.from_documents(
    embedding=embeddings,
    documents=doc
)

# Creating the bot

# Tools
retriever = db.as_retriever()
tool = create_retriever_tool(
    retriever,
    "Patient_Records_and_Recommendations_Tool",
    "This tool stores patient information, including medical records, suggested treatments, and recommended doctors for each patient."
)

# LLM
llm = ChatGroq(model="qwen-qwq-32b")

# Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a healthcare assistant. Use the patient's health reports and the provided tool and the chat history {chat_history} to accurately answer their questions."),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

agent = create_openai_tools_agent(llm=llm, tools=[tool], prompt=prompt)
agent_exec = AgentExecutor(agent=agent, tools=[tool], verbose=False)

# History mechanism
class ChatHistory():
    def __init__(self):
        self.history_dict = {}
        self.history_list = []

    def add(self, user_input, bot_response):
        self.history_dict = {'user': user_input, 'bot': bot_response}
        self.history_list.append(self.history_dict)
        return self.history_list

    def show(self):
        print(self.history_list)

# Bot
history = ChatHistory()

def MediGuide(user_input):
    response = agent_exec.invoke({"input": user_input, "chat_history": history.show()})
    history.add(user_input, response)
    return response
