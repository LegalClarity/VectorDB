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

### Coding Standards

#### Python Style Guidelines
- **PEP 8 Compliance**: Strict adherence to Python style guidelines
- **Type Hints**: Comprehensive type annotations for all functions and methods

#### Security Patterns

##### Environment Configuration Pattern
Legal Clarity implements a **secure environment-driven configuration** pattern:

```python
# Pattern: Secure Environment Loading
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Settings:
    def __init__(self):
        # Required environment variables (no defaults for secrets)
        self.api_key = os.getenv('API_KEY')  # No fallback secrets
        self.database_url = os.getenv('DATABASE_URL')
        
        # Optional with safe defaults
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        
        # Validate required variables
        self._validate_config()
    
    def _validate_config(self):
        """Validate all required environment variables are present"""
        required = ['API_KEY', 'DATABASE_URL']
        missing = [var for var in required if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {missing}")
```

##### Service Account Authentication Pattern
Google Cloud services use configurable service account authentication:

```python
# Pattern: Configurable Service Account Authentication
class CloudSettings:
    def __init__(self):
        self.service_account_path = os.getenv('GCS_SERVICE_ACCOUNT_PATH')
        self.project_id = os.getenv('GOOGLE_PROJECT_ID')
    
    def get_storage_client(self):
        """Initialize GCS client with service account"""
        if self.service_account_path:
            return storage.Client.from_service_account_json(self.service_account_path)
        else:
            return storage.Client(project=self.project_id)
```

##### API Key Management Pattern
All API keys are managed through environment variables with validation:

```python
# Pattern: Secure API Key Management
class APISettings:
    def __init__(self):
        # Load from environment only
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.qdrant_api_key = os.getenv('QDRANT_API_KEY')
        
        # Validate on startup
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
```

**Security Benefits**:
- ✅ **Zero Hardcoded Secrets**: No API keys in source code
- ✅ **Environment Isolation**: Different configs for dev/staging/production
- ✅ **Startup Validation**: Fail fast if required secrets missing
- ✅ **Repository Safety**: Code safe for public GitHub repositories
- ✅ **Configuration Flexibility**: Easy environment switching without code changes
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

### Proxy Communication Patterns

#### API-to-API Proxy Routing Pattern
Legal Clarity implements a **dual-API architecture** with proxy routing between services:

```python
# ✅ Proxy Communication Pattern
class ProxyRouter:
    def __init__(self, target_url: str, client: httpx.AsyncClient):
        self.target_url = target_url
        self.client = client

    async def proxy_request(
        self,
        method: str,
        path: str,
        data: Optional[dict] = None,
        params: Optional[dict] = None
    ) -> dict:
        """Proxy HTTP requests to target API with error handling"""
        try:
            url = f"{self.target_url}{path}"
            response = await self.client.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Proxy request failed: {e.response.status_code}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Analyzer API error: {e.response.text}"
            )
        except httpx.RequestError as e:
            logger.error(f"Proxy connection failed: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail="Analyzer service temporarily unavailable"
            )

# Usage in FastAPI endpoint
@app.post("/analyzer/analyze", response_model=AnalysisResponse)
async def analyze_document_proxy(
    request: AnalyzeDocumentRequest,
    proxy_router: ProxyRouter = Depends(get_proxy_router)
):
    """Proxy document analysis requests to analyzer API"""
    return await proxy_router.proxy_request(
        method="POST",
        path="/api/analyzer/analyze",
        data=request.dict()
    )
```

#### Benefits of Proxy Pattern
- **Service Separation**: Clean separation between upload and analysis concerns
- **Independent Scaling**: APIs can be scaled independently based on load
- **Error Isolation**: Failures in one API don't affect the other
- **Deployment Flexibility**: APIs can be deployed to different environments
- **Version Compatibility**: Different API versions can coexist

### AI Integration Patterns

#### LangExtract Integration Pattern
```python
# ✅ Real LangExtract Integration Pattern (No Mocks)
class LegalDocumentExtractor:
    def extract_clauses_and_relationships(self, document_text: str, document_type: str):
        """Extract clauses using real LangExtract with Gemini API"""

        # Initialize extraction configuration
        config = self.extraction_configs[document_type]

        # Real API call with comprehensive parameters
        result = lx.extract(
            text_or_documents=document_text,
            prompt_description=config["prompts"],
            examples=config["examples"],
            model_id=config["model_id"],  # gemini-2.5-flash for optimal performance
            api_key=self.gemini_api_key,  # Real API key
            max_char_buffer=config["max_char_buffer"],
            extraction_passes=config["extraction_passes"],
            max_workers=config["max_workers"]
        )

        # Process real results into structured data
        clauses, relationships = self._process_extraction_results(result, document_type)

        return ExtractionResult(
            document_id=f"doc_{int(time.time())}",
            document_type=DocumentType.RENTAL_AGREEMENT,
            extracted_clauses=clauses,
            clause_relationships=relationships,
            confidence_score=self._calculate_confidence_score(clauses),
            processing_time_seconds=time.time() - start_time
        )
```

#### Import Path Resolution Patterns

#### Relative Import Standardization
Legal Clarity establishes **relative import patterns** to eliminate sys.path manipulation:

```python
# ✅ Relative Import Pattern (Recommended)
from .services.legal_extractor import LegalExtractorService
from .routers.extractor import router as extractor_router
from .models.schemas import ExtractionRequest, ExtractionResponse

# ❌ Anti-pattern: sys.path manipulation
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from legal_extractor import LegalExtractorService  # Unreliable

# ✅ Path-based Import for Cross-Module Access
import sys
import os
helper_apis_path = os.path.join(os.path.dirname(__file__), "Helper-APIs", "document-upload-api", "app")
sys.path.insert(0, helper_apis_path)

try:
    from config import settings
    from database import db_manager
    # Use imported modules
except ImportError as e:
    # Fallback handling
    logger.warning(f"Helper API modules not available: {e}")
    # Provide mock or alternative implementations
```

#### Uvicorn Module Path Configuration
```python
# ✅ Correct Uvicorn Configuration
# For app/main.py structure:
uvicorn app.main:app --host 0.0.0.0 --port 8000

# For root level main.py:
uvicorn main:app --host 0.0.0.0 --port 8001

# ❌ Incorrect Configuration (causes ModuleNotFoundError)
uvicorn main:app  # When file is in app/main.py
```

#### Import Error Handling Strategy
```python
# ✅ Graceful Import Fallback Pattern
def safe_import_module(module_path: str, fallback=None):
    """Safely import a module with fallback handling"""
    try:
        module = importlib.import_module(module_path)
        return module
    except ImportError as e:
        logger.warning(f"Failed to import {module_path}: {e}")
        return fallback

# Usage
config_module = safe_import_module("config", MockConfig())
if config_module:
    settings = config_module.settings
else:
    # Use default settings
    settings = get_default_settings()
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

*Document Version: 1.3 | Last Updated: September 21, 2025 | Development Standards Committee*
