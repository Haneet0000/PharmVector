# PharmVector - Document Search API with Semantic Search

Production-ready FastAPI service with PostgreSQL + pgvector for semantic document search, JWT authentication, and background task processing.

## Features

- **JWT Authentication**: Secure user registration and login
- **Semantic Search**: Document search using pgvector with cosine similarity
- **Background Processing**: Celery workers for async embedding generation
- **GDPR Compliance**: Hashed user IDs and timestamped logging
- **Production Ready**: Dockerized with health checks and proper error handling
- **RESTful API**: Clean endpoint design with proper status codes

## Architecture

### Technology Stack

- **FastAPI**: High-performance async web framework
- **PostgreSQL + pgvector**: Vector similarity search
- **Redis**: Message broker for Celery
- **Celery**: Distributed task queue for background jobs
- **Sentence Transformers**: Text embedding generation (all-MiniLM-L6-v2)
- **SQLAlchemy 2.0**: Async ORM with type safety
- **JWT**: Stateless authentication

### Design Decisions

1. **Async Everything**: Full async/await pattern for optimal performance
2. **Vector Embeddings**: 384-dimensional embeddings from MiniLM model
3. **Background Tasks**: Offload expensive embedding computation to Celery workers
4. **Stateless Auth**: JWT tokens for horizontal scalability
5. **GDPR Logging**: SHA-256 hashed user IDs prevent PII exposure
6. **Docker**: Containerized deployment with health checks
7. **Database Migrations**: SQLAlchemy models with init script

### Project Structure

```
PharmVector/
├── app/
│   ├── routers/
│   │   ├── auth.py          # Authentication endpoints
│   │   └── documents.py     # Document CRUD + search
│   ├── tasks/
│   │   ├── celery_app.py    # Celery configuration
│   │   └── embeddings.py    # Background embedding tasks
│   ├── utils/
│   │   ├── logger.py        # GDPR-compliant logging
│   │   └── embeddings.py    # Embedding generation
│   ├── auth.py              # JWT authentication logic
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   └── main.py              # FastAPI application
├── docker-compose.yml       # Multi-container setup
├── Dockerfile               # Container definition
├── requirements.txt         # Python dependencies
└── init_db.py              # Database initialization
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd PharmVector
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Update `.env` with secure values:
```env
SECRET_KEY=<generate-secure-random-key>
```

4. Start services:
```bash
docker-compose up -d
```

5. Check service health:
```bash
curl http://localhost:8000/health
```

## API Documentation

### Authentication

#### Register User
```bash
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}
```

#### Login
```bash
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}

Response:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### Documents (Requires Authentication)

Add `Authorization: Bearer <token>` header to all requests.

#### Create Document
```bash
POST /documents/
Content-Type: application/json

{
  "title": "Clinical Trial Protocol",
  "content": "Study design for phase III trial..."
}
```

#### Search Documents
```bash
POST /documents/search
Content-Type: application/json

{
  "query": "clinical trial design"
}

Response:
[
  {
    "id": 1,
    "title": "Clinical Trial Protocol",
    "content": "Study design...",
    "similarity": 0.89,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

#### List All Documents
```bash
GET /documents/
```

#### Get Document
```bash
GET /documents/{document_id}
```

#### Delete Document
```bash
DELETE /documents/{document_id}
```

## GDPR Compliance

All user actions are logged with:
- **Hashed User ID**: SHA-256 hash prevents PII exposure
- **Timestamp**: ISO 8601 UTC timestamp
- **Action**: Descriptive action type
- **Details**: Non-sensitive metadata

Example log:
```
2024-01-15 10:30:45 - pharmvector - INFO - UserAction | HashedID: 5e884898da... | Timestamp: 2024-01-15T10:30:45 | Action: DOCUMENT_SEARCH | Details: {'query': 'clinical trial'}
```

## Testing

### Manual Testing

1. Register a user:
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

2. Login:
```bash
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}' \
  | jq -r '.access_token')
```

3. Create document:
```bash
curl -X POST http://localhost:8000/documents/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Doc","content":"This is a test document about clinical trials"}'
```

4. Search:
```bash
curl -X POST http://localhost:8000/documents/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"clinical trials"}'
```

## Monitoring

- **API Logs**: `docker-compose logs -f api`
- **Celery Logs**: `docker-compose logs -f celery`
- **Database**: `docker-compose exec db psql -U postgres -d pharmvector`
- **Redis**: `docker-compose exec redis redis-cli`

## Extension to eCTD Generation

### Current Architecture Support

The system is designed to extend to Electronic Common Technical Document (eCTD) generation:

### Phase 1: Document Classification
- Add document type classification (clinical, non-clinical, quality)
- Implement eCTD module structure in database schema
- Tag documents with ICH M4 section numbers

### Phase 2: Template Management
- Store eCTD templates as versioned documents
- Use vector search to find similar submissions
- Auto-suggest content based on regulatory requirements

### Phase 3: Content Assembly
- Celery tasks for document compilation
- Generate XML backbone per eCTD spec v4.0
- Validate against regulatory schemas (FDA, EMA)

### Phase 4: Intelligent Assistance
- RAG (Retrieval Augmented Generation) for content suggestions
- Vector search across historical submissions
- Compliance checking against regulatory guidelines

### Implementation Roadmap

```python
# Example schema extension
class ECTDDocument(Base):
    __tablename__ = "ectd_documents"

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    module = Column(String)  # "1", "2.3", "3.2.S.1.1", etc.
    section_type = Column(String)  # "clinical", "quality", etc.
    version = Column(String)
    status = Column(String)  # "draft", "approved", "submitted"

# Example Celery task
@celery_app.task
def generate_ectd_package(submission_id: int):
    # 1. Gather all documents for submission
    # 2. Generate XML backbone
    # 3. Create PDF renditions
    # 4. Package as eCTD zip
    # 5. Validate against schema
    pass
```

### Vector Search Applications

1. **Precedent Search**: Find similar approved submissions
2. **Content Reuse**: Identify reusable sections across modules
3. **Gap Analysis**: Compare current draft vs. requirements
4. **Smart Templates**: Suggest content based on indication/product

### Compliance Features

- Audit trail for all document changes
- Version control with SHA-256 checksums
- GDPR-compliant reviewer activity logs
- Regulatory submission history tracking

## Production Deployment

### Environment Variables

```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
SYNC_DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0
SECRET_KEY=<generate-with-openssl-rand-hex-32>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
```

### Security Checklist

- [ ] Generate strong SECRET_KEY
- [ ] Use PostgreSQL with SSL
- [ ] Enable Redis password authentication
- [ ] Configure CORS for specific origins
- [ ] Set up rate limiting (nginx/traefik)
- [ ] Enable HTTPS with valid certificates
- [ ] Configure firewall rules
- [ ] Set up database backups
- [ ] Enable container security scanning
- [ ] Configure log retention policies

### Scaling

- **Horizontal API Scaling**: Multiple FastAPI instances behind load balancer
- **Celery Workers**: Scale workers based on queue depth
- **Database**: PostgreSQL read replicas for search queries
- **Redis**: Redis Cluster for high availability
- **Caching**: Add Redis caching layer for frequent queries

## Troubleshooting

### Database Connection Issues
```bash
docker-compose exec db pg_isready -U postgres
docker-compose logs db
```

### Celery Not Processing Tasks
```bash
docker-compose logs celery
docker-compose exec redis redis-cli ping
```

### Vector Search Not Working
```bash
docker-compose exec db psql -U postgres -d pharmvector -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

## License

MIT License

## Support

For issues and questions, please open a GitHub issue.
