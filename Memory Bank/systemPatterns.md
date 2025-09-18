# Legal Clarity - System Patterns

## Development Standards and Patterns

### Code Organization Principles

#### Modular Architecture
Legal Clarity follows a **modular monorepo structure** with clear separation of concerns:

```
LegalClarity/
├── apps/                          # Individual application modules
│   ├── rag_chatbot/              # RAG chatbot application
│   ├── document_upload/          # Document upload API
│   └── shared/                   # Shared utilities and components
├── core/                         # Core system components
│   ├── config/                   # Configuration management
│   ├── logging/                  # Logging infrastructure
│   ├── middleware/               # FastAPI middleware
│   ├── exceptions/               # Custom exception handling
│   └── database/                 # Database connection management
├── tests/                        # Comprehensive test suite
└── docs/                         # Documentation and Memory Bank
```

#### Application Structure Pattern
Each application module follows a consistent structure:

```
app_module/
├── __init__.py                   # Module initialization
├── routers/                      # FastAPI route definitions
│   ├── __init__.py
│   └── endpoints.py
├── services/                     # Business logic layer
│   ├── __init__.py
│   └── service.py
├── models/                       # Data models and schemas
│   ├── __init__.py
│   └── schemas.py
├── dependencies/                 # Dependency injection
│   ├── __init__.py
│   └── deps.py
└── tests/                        # Module-specific tests
```

### Coding Standards

#### Python Style Guidelines
- **PEP 8 Compliance**: Strict adherence to Python style guidelines
- **Type Hints**: Comprehensive type annotations for all functions and methods
- **Docstrings**: Google-style docstrings for all public functions and classes
- **Naming Conventions**:
  - `snake_case` for variables, functions, and methods
  - `PascalCase` for classes and exceptions
  - `UPPER_CASE` for constants
  - `kebab-case` for file and directory names

#### Code Quality Standards
```python
# ✅ Pydantic V2 Migration - Good Example
class Document(BaseModel):
    """Main document model for MongoDB"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    document_id: str
    original_filename: str
    stored_filename: str
    gcs_bucket_name: str
    gcs_object_path: str
    file_metadata: FileMetadata
    document_metadata: DocumentMetadata
    timestamps: Timestamps
    status: Status

    # Pydantic V2 Configuration (No more deprecation warnings)
    model_config = {
        "populate_by_name": True,  # Replaces allow_population_by_field_name
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }

def process_legal_document(
    document_id: str,
    user_id: str,
    processing_options: Optional[ProcessingOptions] = None
) -> DocumentProcessingResult:
    """
    Process a legal document with the specified options.

    Args:
        document_id: Unique identifier for the document
        user_id: Identifier for the user requesting processing
        processing_options: Optional processing configuration

    Returns:
        DocumentProcessingResult containing processing outcomes

    Raises:
        DocumentProcessingError: If processing fails
    """
    pass

# ❌ Bad Example - Old Pydantic V1 style
class OldDocument(BaseModel):
    user_id: str
    document_id: str

    class Config:  # Deprecated in Pydantic V2
        allow_population_by_field_name = True  # Causes warnings
```

### Asynchronous Programming Patterns

#### Async/Await Best Practices
- **Async by Default**: All I/O operations use async/await
- **Context Managers**: Use `asynccontextmanager` for resource management
- **Task Groups**: Use `asyncio.gather()` for concurrent operations
- **Timeout Handling**: Implement timeouts for all external API calls

```python
# ✅ Async Context Manager Pattern
@asynccontextmanager
async def get_database_connection():
    connection = await db_manager.connect()
    try:
        yield connection
    finally:
        await db_manager.disconnect()

# ✅ Concurrent API Calls Pattern
async def process_multiple_documents(document_ids: List[str]):
    tasks = [
        process_single_document(doc_id)
        for doc_id in document_ids
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### Error Handling Patterns

#### Custom Exception Hierarchy
```python
class LegalClarityError(Exception):
    """Base exception for Legal Clarity application"""
    pass

class DocumentProcessingError(LegalClarityError):
    """Raised when document processing fails"""
    pass

class ValidationError(LegalClarityError):
    """Raised when input validation fails"""
    pass

class ExternalServiceError(LegalClarityError):
    """Raised when external service calls fail"""
    pass
```

#### Error Handling Strategy
- **Specific Exceptions**: Use specific exception types for different error conditions
- **Context Preservation**: Include relevant context in exception messages
- **Logging**: Log errors with appropriate severity levels
- **Graceful Degradation**: Handle errors gracefully without crashing the application

```python
# ✅ Comprehensive Error Handling
async def safe_document_processing(document_id: str) -> ProcessingResult:
    try:
        # Validate input
        if not document_id:
            raise ValidationError("Document ID cannot be empty")

        # Process document
        result = await process_document(document_id)

        # Log success
        logger.info(f"Successfully processed document {document_id}")

        return result

    except ValidationError as e:
        logger.warning(f"Validation failed for document {document_id}: {e}")
        raise

    except ExternalServiceError as e:
        logger.error(f"External service error for document {document_id}: {e}")
        # Return cached result or default response
        return ProcessingResult(status="degraded", error=str(e))

    except Exception as e:
        logger.error(f"Unexpected error processing document {document_id}: {e}")
        raise DocumentProcessingError(f"Failed to process document: {e}")
```

### Database Patterns

#### Repository Pattern
```python
class DocumentRepository:
    def __init__(self, db_manager):
        self.db = db_manager

    async def create_document(self, document_data: dict) -> str:
        """Create a new document record"""
        document_id = str(uuid.uuid4())
        document_data["_id"] = document_id
        document_data["created_at"] = datetime.utcnow()

        await self.db.documents.insert_one(document_data)
        return document_id

    async def get_document(self, document_id: str, user_id: str) -> Optional[dict]:
        """Retrieve a document by ID and user"""
        return await self.db.documents.find_one({
            "_id": document_id,
            "user_id": user_id
        })

    async def list_user_documents(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 10
    ) -> List[dict]:
        """List documents for a user with pagination"""
        cursor = self.db.documents.find(
            {"user_id": user_id}
        ).skip(skip).limit(limit)

        return await cursor.to_list(length=None)
```

#### Connection Management
- **Connection Pooling**: Reuse database connections efficiently
- **Transaction Management**: Use transactions for multi-step operations
- **Connection Health Checks**: Monitor and handle connection failures
- **Graceful Shutdown**: Properly close connections on application shutdown

### API Design Patterns

#### RESTful API Standards
```python
# ✅ RESTful Resource Design
@app.post("/documents/", response_model=DocumentResponse)
async def create_document(
    document: DocumentCreate,
    user_id: str = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Create a new document"""
    pass

@app.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    user_id: str = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """Retrieve a specific document"""
    pass

@app.get("/documents/", response_model=DocumentListResponse)
async def list_documents(
    user_id: str = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Database = Depends(get_database)
):
    """List documents with pagination"""
    pass
```

#### Response Standardization
```python
# ✅ Consistent Response Format
{
    "success": true,
    "data": {
        "document_id": "uuid-string",
        "status": "processed",
        "metadata": {...}
    },
    "meta": {
        "timestamp": "2025-09-17T10:30:00Z",
        "request_id": "req-uuid"
    }
}

# Error Response Format
{
    "success": false,
    "error": {
        "code": "DOCUMENT_NOT_FOUND",
        "message": "Document with specified ID not found",
        "details": {...}
    },
    "meta": {
        "timestamp": "2025-09-17T10:30:00Z",
        "request_id": "req-uuid"
    }
}
```

### API Organization Patterns

#### Tag-Based Endpoint Organization
Legal Clarity implements tag-based API organization for better documentation and maintainability:

```python
# ✅ Tag-Based Router Organization
from fastapi import APIRouter

# Health endpoints
health_router = APIRouter(tags=["health"])
@health_router.get("/health")
async def health_check(): pass

# Document management endpoints
documents_router = APIRouter(tags=["documents"])
@documents_router.post("/upload")
async def upload_document(): pass

# Document analysis endpoints
analyzer_router = APIRouter(tags=["analyzer"])
@analyzer_router.post("/analyze")
async def analyze_document(): pass

# Vector database endpoints
vectordb_router = APIRouter(tags=["vectordb"])
@vectordb_router.get("/status")
async def vectordb_status(): pass

# Main application with tag metadata
tags_metadata = [
    {"name": "health", "description": "Health check and system status endpoints"},
    {"name": "documents", "description": "Document upload, management and retrieval operations"},
    {"name": "analyzer", "description": "Document analysis and processing operations"},
    {"name": "vectordb", "description": "Vector database operations and RAG functionality"}
]

app = FastAPI(openapi_tags=tags_metadata)
```

#### Benefits of Tag Organization
- **Clear Separation**: Related endpoints grouped logically
- **Better Documentation**: Swagger UI groups endpoints by functionality
- **Future Scalability**: Easy to add new API categories
- **Maintenance**: Easier to locate and modify related endpoints
- **Testing**: Tag-based testing organization

### Testing Patterns

#### Test Structure
```python
# ✅ Comprehensive Test Example
class TestDocumentService:
    @pytest.fixture
    async def setup_service(self):
        """Setup test service with mock dependencies"""
        pass

    @pytest.mark.asyncio
    async def test_create_document_success(self, setup_service):
        """Test successful document creation"""
        pass

    @pytest.mark.asyncio
    async def test_create_document_validation_error(self, setup_service):
        """Test document creation with invalid data"""
        pass

    @pytest.mark.asyncio
    async def test_get_document_not_found(self, setup_service):
        """Test retrieving non-existent document"""
        pass
```

#### Test Coverage Requirements
- **Unit Tests**: 90%+ coverage for all business logic
- **Integration Tests**: Test external service integrations
- **End-to-End Tests**: Full user journey testing
- **Performance Tests**: Load testing for critical endpoints

### Security Patterns

#### Input Validation
```python
# ✅ Comprehensive Input Validation
from pydantic import BaseModel, validator
from typing import Optional

class DocumentUploadRequest(BaseModel):
    filename: str
    user_id: str
    document_type: Optional[str] = None

    @validator('filename')
    def validate_filename(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Filename cannot be empty')
        if len(v) > 255:
            raise ValueError('Filename too long')
        return v.strip()

    @validator('user_id')
    def validate_user_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('User ID cannot be empty')
        return v.strip()
```

#### Authentication and Authorization
- **JWT Tokens**: Stateless authentication with expiration
- **Role-Based Access**: Granular permissions for different user types
- **API Keys**: Service-to-service authentication
- **Rate Limiting**: Prevent abuse with request throttling

### Performance Patterns

#### Caching Strategy
```python
# ✅ Multi-Level Caching
from functools import lru_cache
import asyncio
from typing import Optional

class CacheManager:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.local_cache = {}

    @lru_cache(maxsize=1000)
    def get_local_cache(self, key: str) -> Optional[str]:
        """Local in-memory cache for frequently accessed data"""
        return self.local_cache.get(key)

    async def get_redis_cache(self, key: str) -> Optional[str]:
        """Redis cache for shared data across instances"""
        return await self.redis.get(key)

    async def get_with_fallback(self, key: str) -> Optional[str]:
        """Get from cache with fallback strategy"""
        # Try local cache first
        result = self.get_local_cache(key)
        if result:
            return result

        # Try Redis cache
        result = await self.get_redis_cache(key)
        if result:
            # Update local cache
            self.local_cache[key] = result
            return result

        return None
```

#### Database Optimization
- **Indexing Strategy**: Strategic indexes for query performance
- **Query Optimization**: Efficient query patterns and aggregation
- **Connection Pooling**: Reuse database connections
- **Read/Write Splitting**: Separate read and write operations

### Logging Patterns

#### Structured Logging
```python
# ✅ Structured Logging Implementation
import logging
import json
from typing import Any, Dict

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log_request(self, method: str, url: str, user_id: str, duration: float):
        """Log API request with structured data"""
        self.logger.info(
            "API Request",
            extra={
                "event_type": "api_request",
                "method": method,
                "url": url,
                "user_id": user_id,
                "duration_ms": duration * 1000,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    def log_error(self, error: Exception, context: Dict[str, Any]):
        """Log error with context"""
        self.logger.error(
            f"Error occurred: {str(error)}",
            extra={
                "event_type": "error",
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": json.dumps(context),
                "timestamp": datetime.utcnow().isoformat()
            },
            exc_info=True
        )
```

### Deployment Patterns

#### Containerization
```dockerfile
# ✅ Production-Ready Dockerfile
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Set work directory
WORKDIR /home/app

# Copy requirements and install Python dependencies
COPY --chown=app:app requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=app:app . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### CI/CD Pipeline
- **Automated Testing**: Run tests on every push
- **Code Quality**: Lint and format code automatically
- **Security Scanning**: Vulnerability scanning for dependencies
- **Deployment Automation**: Automated deployment to staging and production

---

*Document Version: 1.1 | Last Updated: September 18, 2025 | Development Standards Committee*
