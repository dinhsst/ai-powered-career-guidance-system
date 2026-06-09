"""
RAG Pipeline using LangChain + ChromaDB + Gemini.
Retrieves grounded information from education database before LLM generation.
"""
import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import JSONLoader, DirectoryLoader
from langchain.schema import Document, HumanMessage, SystemMessage
from pathlib import Path
from typing import Optional
import asyncio
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
        self.rag_disabled_reason: Optional[str] = None

    async def initialize(self):
        """Load documents into vectorstore and build retrieval chain."""
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=settings.LLM_TEMPERATURE,  # Low for factual accuracy
            )

            embeddings = GoogleGenerativeAIEmbeddings(
                model=settings.GEMINI_EMBEDDING_MODEL,
                google_api_key=settings.GOOGLE_API_KEY,
            )

            persist_dir = settings.CHROMA_PERSIST_DIRECTORY
            if Path(persist_dir).exists():
                self.vectorstore = Chroma(
                    persist_directory=persist_dir,
                    embedding_function=embeddings,
                )
            else:
                logger.info("No existing vectorstore found. Loading documents and creating new vectorstore.")
                docs = self._load_documents()
                self.vectorstore = Chroma.from_documents(
                    documents=docs,
                    embedding=embeddings,
                    persist_directory=persist_dir,
                    collection_name="system_career_guidance",
                )
                logger.info("Vectorstore created and persisted with %d documents.", len(docs))

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

            # Validate retriever once at startup to catch unsupported embedding models early.
            try:
                _ = self.vectorstore.similarity_search("kiểm tra hệ thống", k=1)
            except Exception as e:
                self.rag_disabled_reason = str(e)
                self.retrieval_chain = None
                logger.warning("RAG disabled due to embedding error: %s", e)
                return

            logger.info("RAG Pipeline initialized successfully")
        except Exception as e:
            self.rag_disabled_reason = str(e)
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
            logger.info("RAG disabled. Using LLM-only fallback.")
            return await self._llm_only_fallback(question, context)

        try:
            
            result = await self._invoke_with_retry(question)
            answer = result.get("result", "").strip()
            
            # If RAG returns empty answer, switch to LLM-only fallback
            if not answer:
                logger.warning("RAG returned empty answer. Switching to LLM-only fallback.")
                return await self._llm_only_fallback(question, context)
            
            # Extract and format sources from retrieved documents
            source_documents = result.get("source_documents", [])
            sources = self._format_sources(source_documents)
            
            # Enhance answer with source citations
            answer_with_citations = self._add_source_citations(answer, source_documents)
            
            return {
                "answer": answer_with_citations,
                "sources": sources,
                "mode": "rag",
            }
        except Exception as e:
            if self._is_rate_limited_error(e):
                logger.warning("RAG rate-limited (429). Using LLM-only fallback for this request.")
                return await self._llm_only_fallback(question, context, reason="rate_limited")

            logger.error(f"RAG query failed: {e}. Switching to LLM-only fallback.")
            self.rag_disabled_reason = str(e)
            self.retrieval_chain = None
            return await self._llm_only_fallback(question, context)

    async def _invoke_with_retry(self, question: str) -> dict:
        """Invoke retrieval chain with short retries for transient API failures."""
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                return self.retrieval_chain.invoke({"query": question})
            except Exception as exc:
                if not self._is_transient_llm_error(exc) or attempt == max_attempts:
                    raise

                backoff_seconds = 0.6 * attempt
                logger.warning(
                    "Transient LLM/RAG error (attempt %s/%s): %s. Retrying in %.1fs",
                    attempt,
                    max_attempts,
                    exc,
                    backoff_seconds,
                )
                await asyncio.sleep(backoff_seconds)

    async def _llm_only_fallback(self, question: str, context: dict = None, reason: Optional[str] = None) -> dict:
        """
        Use LLM directly with career advisor prompt when RAG fails or returns empty.
        More intelligent than rule-based fallback but doesn't use knowledge base.
        """
        if not self.llm:
            from app.llm.fallback import rule_based_response
            return rule_based_response(question, context, reason=reason)

        try:
            # Build context-aware prompt
            context_info = ""
            if context:
                context_parts = []
                if context.get("holland_code"):
                    context_parts.append(f"Mã Holland: {context['holland_code']}")
                if context.get("financial_level"):
                    levels = {1: "Khó khăn", 2: "Trung bình", 3: "Khá giả"}
                    context_parts.append(f"Điều kiện kinh tế: {levels.get(context['financial_level'], 'Không rõ')}")
                if context.get("top_subjects"):
                    context_parts.append(f"Môn mạnh: {', '.join(context['top_subjects'])}")
                if context_parts:
                    context_info = "\n\nThông tin học sinh:\n" + "\n".join(context_parts)

            user_message = f"{question}{context_info}"

            # Create messages with system prompt
            messages = [
                SystemMessage(content=CAREER_ADVISOR_SYSTEM_PROMPT),
                HumanMessage(content=user_message),
            ]

            # Invoke LLM with retry
            response = await self._invoke_llm_with_retry(messages)
            
            return {
                "answer": response,
                "sources": [],
                "mode": "llm_only",
            }
        except Exception as e:
            logger.error(f"LLM-only fallback failed: {e}. Falling back to rule-based response.")
            from app.llm.fallback import rule_based_response
            return rule_based_response(question, context, reason=reason)

    async def _invoke_llm_with_retry(self, messages: list) -> str:
        """Invoke LLM directly with retry logic for transient errors."""
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                result = await self.llm.ainvoke(messages)
                return result.content
            except Exception as exc:
                if not self._is_transient_llm_error(exc) or attempt == max_attempts:
                    raise

                backoff_seconds = 0.6 * attempt
                logger.warning(
                    "Transient LLM error in fallback (attempt %s/%s): %s. Retrying in %.1fs",
                    attempt,
                    max_attempts,
                    exc,
                    backoff_seconds,
                )
                await asyncio.sleep(backoff_seconds)

    def _format_sources(self, source_documents: list) -> list:
        """
        Format source documents into a list of source metadata.
        Extracts title, source, and content from documents.
        """
        sources = []
        for i, doc in enumerate(source_documents, 1):
            source_info = {}
            
            # Extract metadata
            metadata = doc.metadata or {}
            
            # Get title from various possible fields
            title = metadata.get("title") or metadata.get("name") or f"Tài liệu {i}"
            source_info["title"] = title
            
            # Get source name/file
            source_name = metadata.get("source") or metadata.get("_name") or ""
            if source_name:
                source_info["source"] = source_name
            
            # Get URL if available
            url = metadata.get("url") or metadata.get("link")
            if url:
                source_info["url"] = url
            
            # Add document content preview (first 200 chars)
            if doc.page_content:
                content_preview = doc.page_content[:200].strip()
                if len(doc.page_content) > 200:
                    content_preview += "..."
                source_info["content"] = content_preview
            
            # Fallback: if no title found, use content preview
            if not source_info.get("title") or source_info["title"].startswith("Tài liệu"):
                if doc.page_content:
                    preview = doc.page_content[:150].strip()
                    source_info["title"] = preview if len(preview) > 0 else "Tài liệu"
            
            sources.append(source_info)
        
        return sources

    def _add_source_citations(self, answer: str, source_documents: list) -> str:
        """
        Add source citations to the answer text.
        Format: "Answer text. [Nguồn: Source 1, Source 2]"
        """
        if not source_documents:
            return answer
        
        # Extract source titles for citation
        source_titles = []
        for doc in source_documents[:3]:  # Limit to top 3 sources
            metadata = doc.metadata or {}
            title = metadata.get("title") or metadata.get("name") or metadata.get("source")
            if title:
                source_titles.append(str(title)[:50])  # Limit title length
        
        if source_titles:
            citation = f"\n\n*Nguồn tham khảo: {', '.join(source_titles)}*"
            return answer + citation
        
        return answer

    @staticmethod
    def _is_rate_limited_error(error: Exception) -> bool:
        message = str(error).lower()
        return (
            "429" in message
            or "resource exhausted" in message
            or "quota" in message
            or "rate limit" in message
        )

    @staticmethod
    def _is_transient_llm_error(error: Exception) -> bool:
        message = str(error).lower()
        return (
            "429" in message
            or "resource exhausted" in message
            or "rate limit" in message
            or "quota" in message
            or "503" in message
            or "unavailable" in message
            or "deadline exceeded" in message
            or "timeout" in message
        )


rag_pipeline = RAGPipeline()
