"""
RAG Pipeline using LangChain + ChromaDB + Gemini.
Retrieves grounded information from education database before LLM generation.
"""
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import JSONLoader, DirectoryLoader
from langchain.schema import Document
from pathlib import Path
from typing import Optional
import logging

from app.core.config import settings
from app.llm.prompts import CAREER_ADVISOR_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent.parent / "data"


class RAGPipeline:
    def __init__(self):
        self.vectorstore: Optional[Chroma] = None
        self.retrieval_chain: Optional[RetrievalQA] = None
        self.llm: Optional[ChatGoogleGenerativeAI] = None

    async def initialize(self):
        """Load documents into vectorstore and build retrieval chain."""
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=settings.LLM_TEMPERATURE,  # Low for factual accuracy
                convert_system_message_to_human=True,
            )

            embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=settings.GOOGLE_API_KEY,
            )

            persist_dir = settings.CHROMA_PERSIST_DIRECTORY
            if Path(persist_dir).exists():
                self.vectorstore = Chroma(
                    persist_directory=persist_dir,
                    embedding_function=embeddings,
                )
            else:
                docs = self._load_documents()
                self.vectorstore = Chroma.from_documents(
                    documents=docs,
                    embedding=embeddings,
                    persist_directory=persist_dir,
                )

            retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5},
            )

            self.retrieval_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True,
            )
            logger.info("RAG Pipeline initialized successfully")
        except Exception as e:
            logger.warning(f"RAG Pipeline initialization failed: {e}. Falling back to LLM-only mode.")

    def _load_documents(self) -> list[Document]:
        """Load career and university data from JSON files."""
        docs = []
        for json_file in DATA_DIR.rglob("*.json"):
            try:
                loader = JSONLoader(
                    file_path=str(json_file),
                    jq_schema=".[]",
                    text_content=False,
                )
                docs.extend(loader.load())
            except Exception as e:
                logger.warning(f"Failed to load {json_file}: {e}")

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        return splitter.split_documents(docs)

    async def query(self, question: str, context: dict = None) -> dict:
        """Query the RAG pipeline with a career guidance question."""
        if self.retrieval_chain is None:
            from app.llm.fallback import rule_based_response
            return rule_based_response(question, context)

        try:
            result = self.retrieval_chain.invoke({"query": question})
            return {
                "answer": result["result"],
                "sources": [doc.metadata for doc in result.get("source_documents", [])],
                "mode": "rag",
            }
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            from app.llm.fallback import rule_based_response
            return rule_based_response(question, context)


rag_pipeline = RAGPipeline()
