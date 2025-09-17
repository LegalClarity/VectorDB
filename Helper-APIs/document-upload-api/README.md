# Legal Document Upload API

A comprehensive FastAPI-based system for uploading and managing legal documents with Google Cloud Storage and MongoDB integration.

## 🚀 Features

- **File Upload & Validation**: Secure upload with comprehensive file validation
- **Cloud Storage**: Google Cloud Storage integration for scalable file storage
- **Database Integration**: MongoDB with Motor async driver for metadata management
- **RESTful API**: Complete REST API with FastAPI
- **Authentication Ready**: User-based authorization system
- **Comprehensive Testing**: Full test coverage with pytest
- **Production Ready**: CORS, logging, error handling, and health checks

## 📁 Project Structure

```
legal-document-api/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration settings
│   ├── models.py                  # MongoDB document models
│   ├── schemas.py                 # Pydantic schemas for API
│   ├── database.py                # MongoDB connection and operations
│   ├── gcs_service.py             # Google Cloud Storage operations
│   ├── validation.py              # File validation logic
│   └── routers/
│       ├── __init__.py
│       └── documents.py           # Document upload endpoints
├── tests/
│   ├── __init__.py
│   └── test_upload.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- MongoDB (local or cloud instance)
- Google Cloud Platform account with Storage enabled
- Service Account Key (optional, uses ADC if not provided)

### Setup

1. **Clone and navigate to the project:**
   ```bash
   cd legal-document-api
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your configuration:
   ```env
   # Google Cloud Configuration
   GEMINI_API_KEY=your_gemini_api_key
   GOOGLE_PROJECT_ID=your_project_id
   GOOGLE_REGION=asia-south1
   USER_DOC_BUCKET=your_bucket_name

   # MongoDB Configuration
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
   MONGO_DB=LegalClarity

   # Optional: Service Account Key path
   GCS_SERVICE_ACCOUNT_PATH=/path/to/service-account.json
   ```

## 🔧 Configuration

### Google Cloud Storage Setup

1. **Create a Google Cloud Project**
2. **Enable Cloud Storage API**
3. **Create a Storage Bucket**
4. **Create Service Account (optional)**
   - Download the JSON key file
   - Set `GCS_SERVICE_ACCOUNT_PATH` in `.env`

### MongoDB Setup

1. **MongoDB Atlas** (recommended):
   - Create cluster
   - Get connection string
   - Set `MONGO_URI` in `.env`

2. **Local MongoDB**:
   ```bash
   MONGO_URI=mongodb://localhost:27017
   ```

## 🚀 Running the Application

### Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at: http://localhost:8000

## 📚 API Documentation

Once running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔗 API Endpoints

### Document Management

#### Upload Single Document
```http
POST /documents/upload
Content-Type: multipart/form-data

Form Data:
- file: (binary) - The document file
- user_id: (string) - User identifier
```

**Response:**
```json
{
  "document_id": "uuid-string",
  "gcs_url": "gs://bucket/users/user_id/document_id",
  "message": "Document uploaded successfully"
}
```

#### Upload Multiple Documents
```http
POST /documents/upload-multiple
Content-Type: multipart/form-data

Form Data:
- files: (binary[]) - Multiple document files
- user_id: (string) - User identifier
```

#### Get Document
```http
GET /documents/{document_id}?user_id={user_id}
```

#### List User Documents
```http
GET /documents?user_id={user_id}&page=1&page_size=10
```

**Query Parameters:**
- `document_type`: Filter by document type
- `category`: Filter by category
- `confidentiality`: Filter by confidentiality level
- `tags`: Filter by tags (comma-separated)
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 10, max: 100)

#### Delete Document
```http
DELETE /documents/{document_id}?user_id={user_id}
```

#### Get Signed URL
```http
GET /documents/{document_id}/signed-url?user_id={user_id}&expiration_minutes=60
```

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test
```bash
pytest tests/test_upload.py::TestDocumentEndpoints::test_upload_document_success -v
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=html
```

## 📋 File Validation

The API validates files based on:

- **Allowed Extensions**: `.pdf`, `.docx`, `.doc`, `.txt`
- **Allowed MIME Types**: `application/pdf`, `application/msword`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, `text/plain`
- **Maximum File Size**: 50MB (configurable via `MAX_UPLOAD_SIZE`)
- **Content Validation**: Basic content structure checks

## 🗄️ Database Schema

### Documents Collection

```javascript
{
  "_id": ObjectId,
  "user_id": "string",              // User identifier
  "document_id": "string",          // Unique document identifier
  "original_filename": "string",    // Original uploaded filename
  "stored_filename": "string",      // GCS stored filename
  "gcs_bucket_name": "string",      // Google Cloud Storage bucket
  "gcs_object_path": "string",      // Full GCS object path
  "file_metadata": {
    "content_type": "string",       // MIME type
    "file_size": "int64",           // File size in bytes
    "file_hash": "string",          // SHA-256 checksum
    "upload_method": "string"       // Upload method used
  },
  "document_metadata": {
    "document_type": "string",      // Contract, Agreement, etc.
    "category": "string",           // Legal category
    "tags": ["string"],             // Searchable tags
    "description": "string",        // User-provided description
    "confidentiality": "string"     // Public, Private, Confidential
  },
  "timestamps": {
    "created_at": "datetime",       // Upload timestamp
    "updated_at": "datetime",       // Last modification
    "expires_at": "datetime"        // Optional expiration
  },
  "status": {
    "upload_status": "string",      // pending, completed, failed
    "processing_status": "string",  // processing, processed, error
    "validation_errors": ["string"] // Any validation issues
  }
}
```

## ☁️ Google Cloud Storage Structure

```
{your-bucket-name}/
└── users/
    ├── {user_id}/
    │   ├── {document_id_1}
    │   ├── {document_id_2}
    │   └── {document_id_n}
    └── {user_id_2}/
        ├── {document_id_1}
        └── {document_id_2}
```

## 🔒 Security Features

- **User-based Authorization**: All operations require valid `user_id`
- **File Validation**: Comprehensive file type and content validation
- **Secure URLs**: Signed URLs for secure file access
- **Input Sanitization**: User input validation and sanitization
- **Error Handling**: Comprehensive error handling without information leakage

## 📊 Health Monitoring

The API includes health check endpoints:

```http
GET /health
```

Returns service status and connectivity checks for MongoDB and GCS.

## 🚀 Deployment

### Docker Deployment

1. **Create Dockerfile:**
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt

   COPY . .
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Build and run:**
   ```bash
   docker build -t legal-document-api .
   docker run -p 8000:8000 legal-document-api
   ```

### Production Considerations

- **Environment Variables**: Use secure secret management
- **HTTPS**: Enable SSL/TLS in production
- **Rate Limiting**: Implement rate limiting for upload endpoints
- **Monitoring**: Set up logging and monitoring
- **Backup**: Regular database and storage backups
- **Scaling**: Consider load balancer for multiple instances

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the API documentation at `/docs`
- Review the test cases for usage examples
- Create an issue for bugs or feature requests

## 🔄 Future Enhancements

- [ ] Document versioning
- [ ] Advanced search and filtering
- [ ] Document processing and OCR
- [ ] Audit logging
- [ ] Bulk operations
- [ ] Integration with legal document processing services
- [ ] Advanced permission management
