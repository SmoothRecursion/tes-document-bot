from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.text_splitter import RecursiveCharacterTextSplitter

def classify_and_process_documents(documents, question, openai_api_key):
    # Initialize the language model
    llm = ChatOpenAI(api_key=openai_api_key)

    # Create a text splitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    # Function to classify a document snippet
    def classify_snippet(snippet):
        classification_prompt = ChatPromptTemplate.from_template(
            "Classify the following text snippet into one of these categories: "
            "Grease, Oil Filters, Competitor Oil Filters, or Oils. "
            "Only respond with the category name.\n\nText: {snippet}"
        )
        classification_chain = classification_prompt | llm | StrOutputParser()
        return classification_chain.invoke({"snippet": snippet})

    # Process each document
    processed_docs = []
    for doc in documents:
        snippets = text_splitter.split_text(doc)
        classified_snippets = [
            {"snippet": snippet, "classification": classify_snippet(snippet)}
            for snippet in snippets
        ]
        processed_docs.extend(classified_snippets)

    # Create a prompt template for answering the question
    answer_prompt = ChatPromptTemplate.from_template(
        "You are an expert in automotive products. "
        "Answer the following question based on the provided classified document snippets:\n"
        "Question: {question}\n\n"
        "Classified Snippets:\n{classified_snippets}\n\n"
        "Provide a comprehensive answer, mentioning the relevant classifications when appropriate."
    )

    # Create the full chain
    chain = (
        {"question": RunnablePassthrough(), "classified_snippets": lambda _: processed_docs}
        | answer_prompt
        | llm
        | StrOutputParser()
    )

    # Run the chain
    return chain.invoke(question)
