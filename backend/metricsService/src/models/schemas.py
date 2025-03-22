"""
Data Models and Schemas Module

This module contains all Pydantic models used for request validation and response
formatting in the Citation Credibility Service API. These models ensure type safety
and provide automatic documentation for the API endpoints.

Key Models:
- CredibilityRequest: Input model for single credibility analysis
- ComponentScore: Model for individual credibility components
- CredibilityResponse: Standard response format for credibility results
- SimplifiedCredibilityResponse: Compact response format
- BatchCredibilityRequest: Input model for batch credibility analysis

Features:
- Automatic field validation and type checking
- Detailed field descriptions for API documentation
- Support for optional fields with default values
- Nested model structures for complex data
- Consistent response formats

Usage:
These models are used throughout the API endpoints to validate incoming requests
and format responses. They also generate the API documentation automatically.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any

class CredibilityRequest(BaseModel):
    domain: Optional[str] = Field(None, description="Website domain of the publication")
    citation_doi: Optional[str] = Field(None, description="DOI of the publication")
    journal: Optional[str] = Field(None, description="Journal name")
    publication_date: Optional[str] = Field(
        None, 
        alias="publicationDate", 
        description="Publication date or year"
    )
    author_id: Optional[str| List[str]] = Field(None, description="ORCID ID of the author")
    author_name: Optional[str| List[str]] = Field(
        None, 
        alias="authors", 
        description="Author name"
    )
    title: Optional[str] = Field(None, description="Title of the publication")
    type: Optional[str] = Field(None, description="Type of publication (article, book, etc.)")
    issn: Optional[str] = Field(None, description="ISSN of the journal")
    link: Optional[str] = Field(
        None, 
        alias="url", 
        description="Link to the publication"
    )

    model_config = ConfigDict(populate_by_name=True)

class ComponentScore(BaseModel):
    score: float = Field(..., description="Raw score out of 100")
    weighted_score: float = Field(..., description="Score after applying weight")
    weight: float = Field(..., description="Weight factor applied")
    available: bool = Field(False, description="Whether this data was available")

class CredibilityResponse(BaseModel):
    status: str = Field("success", description="Status of the request")
    data: Dict[str, Any] = Field(..., description="Credibility score data")

class SimplifiedCredibilityResponse(BaseModel):
    status: str = Field("success", description="Status of the request")
    data: Dict[str, Any] = Field(..., description="Simplified credibility data")

class BatchCredibilityRequest(BaseModel):
    sources: List[CredibilityRequest] = Field(..., description="List of sources to evaluate")
