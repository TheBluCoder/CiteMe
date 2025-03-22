"""
API Configuration Module

This module contains all API endpoint configurations and constants used
throughout the application. It serves as a centralized location for managing
external service connections.

Key Constants:
- CROSSREF_API: Crossref API endpoint for citation data
- TRANCO_API: Tranco List API for domain rankings
- DOAJ_API: Directory of Open Access Journals API
- ORCID_API: ORCID API for author information
- SEMANTIC_SCHOLAR_AUTHOR_SEARCH_API: Semantic Scholar author search
- OPEN_ALEX_AUTHOR_API: OpenAlex author data
- OBSERVATORY_API: Mozilla Observatory security scans
- OPEN_CITATIONS_API: OpenCitations metadata

Features:
- Centralized API configuration
- Easy maintenance of endpoint URLs
- Consistent naming conventions
"""

# API endpoints and constants
CROSSREF_API = "https://api.crossref.org/works"
TRANCO_API = "https://tranco-list.eu/api/lists/date/latest"
TRANCO_DOMAIN_API = "https://tranco-list.eu/api/ranks/domain/"
DOAJ_API_WITH_ISSN = "https://doaj.org/api/v2/search/journals/issn:{issn}"
DOAJ_API = "https://doaj.org/api/v2/search/journals/{journal}"
ORCID_API = "https://pub.orcid.org/v3.0/"
SEMANTIC_SCHOLAR_AUTHOR_SEARCH_API = "https://api.semanticscholar.org/graph/v1/author/search"
OPEN_ALEX_AUTHOR_API = "https://api.openalex.org/authors"
OBSERVATORY_API = "https://http-observatory.security.mozilla.org/api/v1/analyze"
OPEN_CITATIONS_API = "https://opencitations.net/index/api/v1/"
MAX_CONCURRENT_WORKERS = 20
DEFAULT_CONCURRENT_WORKERS = 10
