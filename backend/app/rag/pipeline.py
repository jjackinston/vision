"""
SellerVision AI — RAG (Retrieval-Augmented Generation) Pipeline
Uses pgvector + LangChain for context-aware AI responses grounded in real data.
"""
from typing import List, Optional, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

RAG_PROMPT = ChatPromptTemplate.from_template("""You are SellerVision AI's intelligent assistant.
Use the following retrieved context to answer the question accurately.
If the context doesn't contain enough information, say so — don't hallucinate.

Context:
{context}

Question: {question}

Answer:""")

PRODUCT_ANALYSIS_PROMPT = ChatPromptTemplate.from_template("""You are SellerVision AI analyzing e-commerce data.
Use this market intelligence to provide actionable insights:

Market Data:
{context}

Analysis Request: {question}

Provide specific, data-driven recommendations:""")


def _get_embeddings():
    from langchain_openai import OpenAIEmbeddings
    return OpenAIEmbeddings(
        model="text-embedding-3-large",
        api_key=settings.OPENAI_API_KEY or "placeholder",
    )


def _get_vector_store():
    try:
        from langchain_postgres import PGVector
        conn = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
        return PGVector(
            embeddings=_get_embeddings(),
            collection_name="sellervision_embeddings",
            connection=conn,
            use_jsonb=True,
        )
    except ImportError:
        logger.warning("langchain_postgres not installed — vector store unavailable")
        return None


def _get_llm():
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=settings.OPENAI_MODEL,
        temperature=0,
        api_key=settings.OPENAI_API_KEY or "placeholder",
    )


def _get_text_splitter():
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    return RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""],
    )


def format_docs(docs: List[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def build_retrieval_chain(k: int = 5, filter_metadata: Optional[dict] = None):
    """Build a RAG chain with optional metadata filtering."""
    vs = _get_vector_store()
    if vs is None:
        raise RuntimeError("Vector store not available")
    retriever = vs.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k, "filter": filter_metadata} if filter_metadata else {"k": k},
    )
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | RAG_PROMPT
        | _get_llm()
        | StrOutputParser()
    )
    return chain


async def ingest_product_data(products: List[dict]) -> int:
    """Embed product data for RAG retrieval."""
    splitter = _get_text_splitter()
    vs = _get_vector_store()
    if vs is None:
        return 0
    docs = []
    for p in products:
        text = f"""Product: {p.get('title', '')}
ASIN: {p.get('asin', '')}
Category: {p.get('category', '')}
Marketplace: {p.get('marketplace', '')}
Price: ${p.get('current_price', 0)}
Opportunity Score: {p.get('opportunity_score', 0)}/100
AI Analysis: {str(p.get('ai_analysis', {}))}"""
        docs.append(Document(
            page_content=text,
            metadata={
                "source_type": "product",
                "source_id": str(p.get("id", "")),
                "marketplace": p.get("marketplace", ""),
                "category": p.get("category", ""),
            }
        ))
    chunks = splitter.split_documents(docs)
    await vs.aadd_documents(chunks)
    logger.info(f"Ingested {len(chunks)} product chunks into vector store")
    return len(chunks)


async def ingest_competitor_reviews(reviews: List[dict], product_id: str) -> int:
    """Embed competitor reviews for weakness analysis."""
    splitter = _get_text_splitter()
    vs = _get_vector_store()
    if vs is None:
        return 0
    docs = []
    for r in reviews:
        text = f"""Review Rating: {r.get('rating', 0)} stars
Title: {r.get('title', '')}
Body: {r.get('body', '')}
Date: {r.get('date', '')}
Verified: {r.get('verified', False)}"""
        docs.append(Document(
            page_content=text,
            metadata={
                "source_type": "review",
                "source_id": product_id,
                "rating": r.get("rating", 0),
            }
        ))
    chunks = splitter.split_documents(docs)
    await vs.aadd_documents(chunks)
    return len(chunks)


async def ingest_market_report(report_text: str, report_type: str, extra_meta: dict = None) -> int:
    """Embed market reports, trend data, and research."""
    splitter = _get_text_splitter()
    vs = _get_vector_store()
    if vs is None:
        return 0
    docs = [Document(page_content=report_text, metadata={"source_type": report_type, **(extra_meta or {})})]
    chunks = splitter.split_documents(docs)
    await vs.aadd_documents(chunks)
    return len(chunks)


async def query_product_intelligence(question: str, category: str = None) -> str:
    """Ask questions grounded in product data."""
    filter_meta = {"source_type": "product"}
    if category:
        filter_meta["category"] = category
    chain = build_retrieval_chain(k=8, filter_metadata=filter_meta)
    return await chain.ainvoke(question)


async def query_competitor_weaknesses(question: str, product_id: str) -> str:
    """Ask about competitor weaknesses from review data."""
    chain = build_retrieval_chain(
        k=15,
        filter_metadata={"source_type": "review", "source_id": product_id}
    )
    return await chain.ainvoke(question)


async def semantic_product_search(query: str, k: int = 10) -> List[Document]:
    """Find semantically similar products."""
    vs = _get_vector_store()
    if vs is None:
        return []
    return await vs.asimilarity_search(query, k=k, filter={"source_type": "product"})


async def find_similar_opportunities(product_desc: str, k: int = 5) -> List[Document]:
    """Find similar high-opportunity products."""
    vs = _get_vector_store()
    if vs is None:
        return []
    return await vs.asimilarity_search(
        product_desc, k=k,
        filter={"source_type": "product"},
    )
