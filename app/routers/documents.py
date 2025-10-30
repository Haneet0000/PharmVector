from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, text
from typing import List
from app.database import get_db
from app.models import User, Document
from app.schemas import DocumentCreate, DocumentResponse, DocumentSearchRequest, DocumentSearchResult
from app.auth import get_current_user
from app.tasks.embeddings import generate_document_embedding
from app.utils.embeddings import generate_embedding
from app.utils.logger import log_user_action

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document_data: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    new_document = Document(
        title=document_data.title,
        content=document_data.content,
        user_id=current_user.id
    )

    db.add(new_document)
    await db.commit()
    await db.refresh(new_document)

    generate_document_embedding.delay(new_document.id, document_data.content)

    log_user_action(current_user.id, "DOCUMENT_CREATED", {"document_id": new_document.id})
    return new_document


@router.post("/search", response_model=List[DocumentSearchResult])
async def search_documents(
    search_request: DocumentSearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query_embedding = generate_embedding(search_request.query)
    embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'

    sql = text("""
        SELECT
            id,
            title,
            content,
            created_at,
            1 - (embedding <=> CAST(:query_embedding AS vector)) as similarity
        FROM documents
        WHERE user_id = :user_id AND embedding IS NOT NULL
        ORDER BY embedding <=> CAST(:query_embedding AS vector)
        LIMIT 3
    """)

    result = await db.execute(
        sql.bindparams(query_embedding=embedding_str, user_id=current_user.id)
    )

    documents = result.fetchall()

    log_user_action(current_user.id, "DOCUMENT_SEARCH", {"query": search_request.query})

    return [
        DocumentSearchResult(
            id=doc.id,
            title=doc.title,
            content=doc.content,
            similarity=float(doc.similarity),
            created_at=doc.created_at
        )
        for doc in documents
    ]


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Document).filter(Document.user_id == current_user.id).order_by(Document.created_at.desc())
    )
    documents = result.scalars().all()

    log_user_action(current_user.id, "DOCUMENTS_LISTED")
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Document).filter(Document.id == document_id, Document.user_id == current_user.id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    log_user_action(current_user.id, "DOCUMENT_VIEWED", {"document_id": document_id})
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Document).filter(Document.id == document_id, Document.user_id == current_user.id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    await db.execute(delete(Document).where(Document.id == document_id))
    await db.commit()

    log_user_action(current_user.id, "DOCUMENT_DELETED", {"document_id": document_id})
    return None
