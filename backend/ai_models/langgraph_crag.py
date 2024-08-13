import os
from typing import List
from typing_extensions import TypedDict
from langchain.schema import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import END, StateGraph, START
from backend.database.mongodb_client import AtlasClient
from langchain.vectorstores import MongoDBAtlasVectorSearch
from langchain.embeddings import OpenAIEmbeddings

# Data model for grading documents
class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""
    binary_score: str = Field(description="Documents are relevant to the question, 'yes' or 'no'")

# Graph state
class GraphState(TypedDict):
    """Represents the state of our graph."""
    question: str
    generation: str
    web_search: str
    documents: List[str]

# Initialize LLM and tools
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
structured_llm_grader = llm.with_structured_output(GradeDocuments)
web_search_tool = TavilySearchResults(k=3)

# Initialize MongoDB Atlas client and vector store
atlas_client = AtlasClient(embedding_model="openai")  # You can change this to "huggingface" if needed
atlas_client.initialize_vector_store()

# Prompts
system_grade = """You are a grader assessing relevance of a retrieved document to a user question. 
    If the document contains keyword(s) or semantic meaning related to the question, grade it as relevant. 
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""
grade_prompt = ChatPromptTemplate.from_messages([
    ("system", system_grade),
    ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
])

system_rewrite = """You a question re-writer that converts an input question to a better version that is optimized 
     for web search. Look at the input and try to reason about the underlying semantic intent / meaning."""
re_write_prompt = ChatPromptTemplate.from_messages([
    ("system", system_rewrite),
    ("human", "Here is the initial question: \n\n {question} \n Formulate an improved question."),
])

# Chains
retrieval_grader = grade_prompt | structured_llm_grader
question_rewriter = re_write_prompt | llm | StrOutputParser()
rag_prompt = hub.pull("rlm/rag-prompt")
rag_chain = rag_prompt | llm | StrOutputParser()

# Graph functions
def retrieve(state):
    """Retrieve documents"""
    print("---RETRIEVE---")
    question = state["question"]
    # Use vector store to retrieve relevant documents
    docs = atlas_client.similarity_search(question, k=5)
    documents = [Document(page_content=doc.page_content, metadata=doc.metadata) for doc in docs]
    return {"documents": documents, "question": question}

def generate(state):
    """Generate answer"""
    print("---GENERATE---")
    question = state["question"]
    documents = state["documents"]
    context = "\n\n".join([doc.page_content for doc in documents])
    generation = rag_chain.invoke({"context": context, "question": question})
    return {"documents": documents, "question": question, "generation": generation}

def grade_documents(state):
    """Determines whether the retrieved documents are relevant to the question."""
    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    question = state["question"]
    documents = state["documents"]
    filtered_docs = []
    web_search = "No"
    for d in documents:
        score = retrieval_grader.invoke({"question": question, "document": d.page_content})
        if score.binary_score == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(d)
        else:
            print("---GRADE: DOCUMENT NOT RELEVANT---")
            web_search = "Yes"
    return {"documents": filtered_docs, "question": question, "web_search": web_search}

def transform_query(state):
    """Transform the query to produce a better question."""
    print("---TRANSFORM QUERY---")
    question = state["question"]
    better_question = question_rewriter.invoke({"question": question})
    return {"documents": state["documents"], "question": better_question}

def web_search(state):
    """Web search based on the re-phrased question."""
    print("---WEB SEARCH---")
    question = state["question"]
    docs = web_search_tool.invoke({"query": question})
    web_results = "\n".join([d["content"] for d in docs])
    web_results = Document(page_content=web_results)
    state["documents"].append(web_results)
    return {"documents": state["documents"], "question": question}

def decide_to_generate(state):
    """Determines whether to generate an answer, or re-generate a question."""
    print("---ASSESS GRADED DOCUMENTS---")
    web_search = state["web_search"]
    if web_search == "Yes":
        print("---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---")
        return "transform_query"
    else:
        print("---DECISION: GENERATE---")
        return "generate"

# Build Graph
workflow = StateGraph(GraphState)

workflow.add_node("retrieve", retrieve)
workflow.add_node("grade_documents", grade_documents)
workflow.add_node("generate", generate)
workflow.add_node("transform_query", transform_query)
workflow.add_node("web_search_node", web_search)

workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "grade_documents")
workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "transform_query": "transform_query",
        "generate": "generate",
    },
)
workflow.add_edge("transform_query", "web_search_node")
workflow.add_edge("web_search_node", "generate")
workflow.add_edge("generate", END)

# Compile
app = workflow.compile()

def run_crag(question: str):
    """Run the CRAG workflow with a given question."""
    inputs = {"question": question}
    result = app.invoke(inputs)
    return result["generation"]
