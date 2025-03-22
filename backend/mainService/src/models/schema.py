from typing import List, Optional, Union,Literal
from pydantic import BaseModel, Field
from datetime import datetime, timezone as tz
class Source(BaseModel):
    url: Optional[str] = None
    content: Optional[str] = None
    title: str
    authors: str
    type: str='website'
    publishedDate: Optional[str] = None
    doi: Optional[str] = None
    volume: Optional[str] = None
    accessDate: Optional[str] = Field(default=datetime.now(tz.utc).strftime("%Y-%m-%d"), alias="access_date")

class AutoCitationInput(BaseModel):
    title: str
    content: str=Field(default="")
    formType: Literal["auto"]
    citationStyle: Optional[str] = "APA"

class WebCitationInput(BaseModel):
    title: str
    content: str=Field(default="")
    formType:Literal["web"]
    citationStyle: Optional[str] = "APA"
    supplementUrls: bool= False
    sources: List[Source]

class DirectSourceCitationInput(BaseModel):
    title: str
    content: str
    formType: Literal["source"]
    citationStyle: Optional[str] = "APA"
    sources: List[Source]

CitationInput = Union[AutoCitationInput, WebCitationInput, DirectSourceCitationInput]
