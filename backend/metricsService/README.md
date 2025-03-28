# Citation Credibility Service

A FastAPI-based service for calculating credibility scores of academic sources.

## Features

- Calculate credibility scores for individual sources
- Batch processing of multiple sources
- Detailed and simplified response formats
- Built-in caching using fastapi-cache2 for improved performance
- Rate limiting and retry mechanisms
- Comprehensive error handling

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with required environment variables
4. Run the application:
   ```bash
   uvicorn src.main:app --reload
   ```

## API Endpoints

## API Versioning

The API follows semantic versioning (v1.x.x) with the version number included in the URL path.

### Version 1 Endpoints

#### Single Source Evaluation
`POST /api/v1/credibility/compute_credibility`

**Request Body:**
```json
{
  "domain": "example.com",
  "citation_doi": "10.1234/example",
  "journal": "Example Journal",
  "publication_date": "2023-01-01",
  "author_id": "0000-0000-0000-0000",
  "author_name": "John Doe",
  "title": "Example Title",
  "type": "article"
}
```

#### Batch Evaluation
`POST /api/v1/credibility/compute_credibility_batch`

#### Health Check
`GET /api/v1/credibility/health`

### Versioning Strategy
- Major version changes (v1 → v2) indicate breaking changes
- Minor version changes (v1.0 → v1.1) indicate new features
- Patch version changes (v1.0.0 → v1.0.1) indicate bug fixes

**Request Body:**
```json
{
  "sources": [
    {
      "domain": "example.com",
      "citation_doi": "10.1234/example",
      "journal": "Example Journal",
      "publication_date": "2023-01-01",
      "author_id": "0000-0000-0000-0000",
      "author_name": "John Doe",
      "title": "Example Title",
      "type": "article"
    }
  ]
}
```

**Query Parameter:**
- `detail`: boolean (default: false) - Return detailed results

## Configuration

Create a `.env` file with the following variables:

```
CORE_API_KEY=your_core_api_key
```

### Caching Configuration

The API uses fastapi-cache2 with in-memory caching by default. Cache settings can be configured through environment variables:

- `CACHE_TTL`: Cache time-to-live in seconds (default: 3600)
- `CACHE_MAX_SIZE`: Maximum number of cached items (default: 1000)

## Running Tests

To run tests:

```bash
pytest
```

## Deployment

For production deployment:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## License

MIT License
