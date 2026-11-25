import os

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

OPENROUTER_URL = "https://openrouter.ai/api/v1"

embeddings = OpenAIEmbeddings(
    model="google/gemini-embedding-2",
    base_url=OPENROUTER_URL,
    api_key=os.getenv("OPENROUTER_API_KEY"),
    check_embedding_ctx_length=False,
    chunk_size=100,
)

llm = ChatOpenAI(
    model="google/gemini-4-hydrogen",
    base_url=OPENROUTER_URL,
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)

prompt = ChatPromptTemplate.from_template(
    "Answer the question using only the context below. "
    "If the answer is not in the context, say: I could not find this in the document.\n\n"
    "Context:\n{context}\n\n"
    "Question: {question}"
)


def build_store(path):
    loader = PyPDFLoader(path)
    pages = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(pages)
    return FAISS.from_documents(chunks, embeddings)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def ask(store, question):
    retriever = store.as_retriever(search_kwargs={"k": 4})
    docs = retriever.invoke(question)
    context = format_docs(docs)
    answer = llm.invoke(prompt.format_messages(context=context, question=question)).content
    if answer.startswith("I could not find"):
        return answer, []
    pages = sorted(set(doc.metadata["page"] + 1 for doc in docs))
    return answer, pages


if __name__ == "__main__":
    store = build_store("energy-saver-guide.pdf")
    answer, sources = ask(store, "How can I save money on my water heater?")
    print(answer)
    print(sources)
