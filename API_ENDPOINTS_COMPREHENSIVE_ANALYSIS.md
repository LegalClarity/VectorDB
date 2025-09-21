# API Endpoints Comprehensive Analysis
## Legal Document Processing System

### System Overview
The current system has three main API applications:

1. **Main API** (port 8001) - Consolidated/Main entry point
2. **Document Analyzer API** (port 8000) - Analysis and extraction services
3. **Document Upload API** - Upload services (currently integrated into Main API)

---

## 1. MAIN API (Port 8001) - `main.py`
**Base URL**: `http://localhost:8001`

### Health & System Endpoints
| Method | Path | Purpose | Status |
|--------|------|---------|--------|
| GET | `/` | Root endpoint with API information | ✅ Working |
| GET | `/health` | System health check | ✅ Working |
| GET | `/vectordb/status` | VectorDB status (placeholder) | ✅ Working |

### Document Management Endpoints (Proxied to Upload API)
| Method | Path | Purpose | Status |
|--------|------|---------|--------|
| POST | `/documents/upload` | Single document upload | ✅ Working |
| POST | `/documents/upload-multiple` | Batch document upload | ✅ Working |
| GET | `/documents/{document_id}` | Get document by ID | ✅ Working |
| GET | `/documents/` | List user documents | ✅ Working |
| DELETE | `/documents/{document_id}` | Delete document | ✅ Working |
| GET | `/documents/{document_id}/signed-url` | Get signed URL for document | ✅ Working |

### Document Analysis Endpoints (Proxied to Analyzer API)
| Method | Path | Purpose | Status |
|--------|------|---------|--------|
| POST | `/analyzer/analyze` | Analyze document (proxy) | ✅ Working |
| GET | `/analyzer/results/{doc_id}` | Get analysis results | ✅ Working |
| GET | `/analyzer/documents` | List analyzed documents | ✅ Working |
| GET | `/analyzer/stats/{user_id}` | Get user statistics | ✅ Working |
| DELETE | `/analyzer/results/{doc_id}` | Delete analysis results | ✅ Working |
| GET | `/analyzer/health` | Analyzer health check | ✅ Working |

---

## 2. DOCUMENT ANALYZER API (Port 8000) - `Helper-APIs/document-analyzer-api/app/main.py`
**Base URL**: `http://localhost:8000`

### Root Endpoints
| Method | Path | Purpose | Status |
|--------|------|---------|--------|
| GET | `/` | Root with endpoint information | ✅ Working |
| GET | `/health` | Service health check | ✅ Working |
| GET | `/info` | Service information | ✅ Working |

### Document Analysis Endpoints - `/api/analyzer`
| Method | Path | Purpose | Status |
|--------|------|---------|--------|
| POST | `/api/analyzer/analyze` | Analyze legal document | ✅ Working |
| GET | `/api/analyzer/results/{document_id}` | Get analysis results | ✅ Working |
| GET | `/api/analyzer/documents` | List analyzed documents | ✅ Working |
| GET | `/api/analyzer/stats/{user_id}` | User statistics | ✅ Working |
| DELETE | `/api/analyzer/results/{document_id}` | Delete analysis results | ✅ Working |
| GET | `/api/analyzer/health` | Analyzer health check | ✅ Working |

### Legal Document Extraction Endpoints - `/api/extractor`
| Method | Path | Purpose | Status |
|--------|------|---------|--------|
| POST | `/api/extractor/extract` | Extract clauses from document | ✅ Working |
| POST | `/api/extractor/structured` | Create structured document | ✅ Working |
| GET | `/api/extractor/results/{document_id}` | Get extraction results | ✅ Working |
| GET | `/api/extractor/documents` | List processed documents | ✅ Working |
| GET | `/api/extractor/stats/{user_id}` | User extraction statistics | ✅ Working |
| GET | `/api/extractor/health` | Extractor health check | ✅ Working |

---

## 3. DOCUMENT UPLOAD API - `Helper-APIs/document-upload-api/app/main.py`
**Base URL**: Not directly accessible (integrated into Main API)

### Root Endpoints
| Method | Path | Purpose | Status |
|--------|------|---------|--------|
| GET | `/` | Root endpoint | 🔄 Integrated |
| GET | `/health` | Health check | 🔄 Integrated |

### Document Management Endpoints - `/documents`
| Method | Path | Purpose | Status |
|--------|------|---------|--------|
| POST | `/documents/upload` | Single document upload | 🔄 Integrated |
| POST | `/documents/upload-multiple` | Batch upload | 🔄 Integrated |
| GET | `/documents/{document_id}` | Get document by ID | 🔄 Integrated |
| GET | `/documents/` | List user documents | 🔄 Integrated |
| DELETE | `/documents/{document_id}` | Delete document | 🔄 Integrated |
| GET | `/documents/{document_id}/signed-url` | Get signed URL | 🔄 Integrated |

---

## DUPLICATE ANALYSIS

### 🔴 **TRUE DUPLICATES** (Same functionality, different paths)

#### 1. Health Check Endpoints
- **Main API**: `GET /health`
- **Analyzer API**: `GET /health`
- **Analyzer API**: `GET /api/analyzer/health`
- **Upload API**: `GET /health` (integrated)
- **Recommendation**: Keep one health endpoint per service, consolidate multiple health endpoints

#### 2. Root Information Endpoints
- **Main API**: `GET /`
- **Analyzer API**: `GET /`
- **Upload API**: `GET /` (integrated)
- **Recommendation**: Standardize root endpoint responses

#### 3. Analysis Results Endpoints (CRITICAL DUPLICATE)
- **Main API**: `GET /analyzer/results/{doc_id}` (proxy)
- **Analyzer API**: `GET /api/analyzer/results/{document_id}`
- **Extractor API**: `GET /api/extractor/results/{document_id}` (DUPLICATE DEFINITION IN CODE!)
- **Recommendation**: Remove duplicate, use only analyzer results

#### 4. Document Listing (Similar purpose, different data)
- **Main API**: `GET /analyzer/documents` (proxy)
- **Analyzer API**: `GET /api/analyzer/documents`
- **Extractor API**: `GET /api/extractor/documents`
- **Main API**: `GET /documents/` (upload history)
- **Recommendation**: Clarify purposes - upload history vs analysis history

#### 5. User Statistics
- **Main API**: `GET /analyzer/stats/{user_id}` (proxy)
- **Analyzer API**: `GET /api/analyzer/stats/{user_id}`
- **Extractor API**: `GET /api/extractor/stats/{user_id}`
- **Recommendation**: Merge statistics or make them complementary

### 🟡 **FUNCTIONAL OVERLAPS** (Similar but serve different purposes)

#### 1. Document Processing Chain
- **Upload**: `POST /documents/upload` → **Storage**
- **Analyze**: `POST /analyzer/analyze` → **Analysis**
- **Extract**: `POST /api/extractor/extract` → **Clause Extraction**
- **Status**: These are different stages of processing, keep separate

#### 2. Results Retrieval
- **Analyzer Results**: Complete analysis with risk assessment
- **Extractor Results**: Raw clause extraction data
- **Status**: Different data types, keep separate but clarify documentation

### ✅ **NO ISSUES** (Unique functionality)

1. **Document Upload Endpoints** - Unique file management functionality
2. **Document Analysis Endpoints** - Unique AI analysis functionality  
3. **Legal Extraction Endpoints** - Unique clause extraction functionality
4. **VectorDB Endpoints** - Placeholder for future functionality

---

## CRITICAL ISSUES IDENTIFIED

### 1. **Missing Upload Endpoints in Current Main API**
The user reported that upload endpoints are missing from the APN (API). Analysis shows:
- Upload functionality IS present in main.py
- Upload router is properly included: `app.include_router(documents_router, prefix="/documents", tags=["documents"])`
- **Issue might be**: Service not starting correctly or import errors

### 2. **Code-level Duplicates in Extractor Router**
Found ACTUAL duplicate function definitions in `extractor.py`:
```python
@router.get("/results/{document_id}")  # Line ~95
# ... first definition

@router.get("/results/{document_id}")  # Line ~155 
# ... DUPLICATE definition (will override the first)
```

### 3. **Service Architecture Issues**
- **Analyzer Router** uses `DatabaseService`
- **Extractor Router** uses `MongoDBService`
- **Main API** proxies between different services
- **Result**: Inconsistent data storage and retrieval

---

## RECOMMENDATIONS

### Immediate Actions (High Priority)

1. **Fix Duplicate Function Definition**
   - Remove duplicate `/results/{document_id}` in extractor.py
   - Choose the more comprehensive implementation

2. **Standardize Database Services**
   - Use consistent database service across all routers
   - Recommend MongoDBService for all operations

3. **Fix Missing Upload Endpoints**
   - Verify import paths in main.py
   - Check if database connections are working
   - Test upload functionality

4. **Consolidate Health Checks**
   - Keep one health endpoint per service
   - Remove redundant analyzer health endpoints

### Medium-term Improvements

1. **API Documentation Standardization**
   - Standardize response formats across all APIs
   - Use consistent error handling
   - Implement proper OpenAPI tags

2. **Endpoint Purpose Clarification**
   - `/analyzer/documents` → "Documents with completed analysis"
   - `/extractor/documents` → "Documents with extracted clauses"
   - `/documents/` → "Uploaded document metadata"

3. **Service Separation**
   - Main API → Entry point and coordination
   - Analyzer API → Document analysis only
   - Upload API → File management only (or integrate fully)

### Long-term Architecture

1. **API Gateway Pattern**
   - Main API acts as gateway
   - Route requests to appropriate microservices
   - Centralized authentication and logging

2. **Database Consistency**
   - Single source of truth for document metadata
   - Shared data models across services
   - Consistent data validation

---

## ENDPOINT USAGE GUIDE

### For Document Upload
```
POST /documents/upload → Upload file
GET /documents/{id} → Get file metadata
GET /documents/{id}/signed-url → Get download link
```

### For Document Analysis  
```
POST /analyzer/analyze → Analyze uploaded document
GET /analyzer/results/{id} → Get analysis results
GET /analyzer/documents → List analyzed documents
```

### For Legal Clause Extraction
```
POST /api/extractor/extract → Extract clauses
GET /api/extractor/results/{id} → Get extraction results
POST /api/extractor/structured → Create structured document
```

### Service Health Monitoring
```
GET /health → Main API health
GET /api/analyzer/health → Analyzer service health
```

This analysis reveals the system architecture is functional but has several duplicates and inconsistencies that should be addressed for better maintainability and user experience.