from app.tasks.celery_app import celery_app
from app.utils.embeddings import generate_embedding
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
from app.models import Document

settings = get_settings()
engine = create_engine(settings.SYNC_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


@celery_app.task(name="generate_document_embedding")
def generate_document_embedding(document_id: int, content: str):
    embedding = generate_embedding(content)

    db = SessionLocal()
    try:
        stmt = update(Document).where(Document.id == document_id).values(embedding=embedding)
        db.execute(stmt)
        db.commit()
        return {"status": "success", "document_id": document_id}
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
