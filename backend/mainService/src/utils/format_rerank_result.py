from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
import json
from mixedbread_ai.client import RerankingResponse
app = FastAPI()


class DocumentMetadata(BaseModel):
    access_date: str
    author: str
    doi: str
    file_path: str
    journal_title: str
    link: str
    page_content: str
    publication_date: str
    publisher: str
    title: str
    type: str
    volume: str


class Document(BaseModel):
    id: str
    metadata: DocumentMetadata
    page_content: str


class RerankedResult(BaseModel):
    index: int
    score: float
    document: Document


class RerankResponse(BaseModel):
    model: str
    data: List[RerankedResult]


def convert_rerank_result(rerank_result: RerankResponse) -> Dict[str, Any]:
    """
    Convert a rerank response object to a dictionary format.

    Args:
        rerank_result (RerankResponse): The rerank response object to convert

    Returns:
        Dict[str, Any]: A dictionary containing the model and data from the rerank result
    """

    return {
        "model": rerank_result.model,
        "data": [
            {
                "index": item.index,
                "score": item.score,
                "document": {
                    "id": item.document["id"],
                    "metadata": item.document["metadata"],
                    "page_content": item.document["page_content"]
                }
            }
            for item in rerank_result.data
        ]
    }


def filter_results(
        rerank_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter pinecone rerank results based on score threshold and remove duplicates.

    Args:
        rerank_results (List[Dict[str, Any]]): List of rerank results to filter

    Returns:
        List[Dict[str, Any]]: Filtered list of unique document metadata meeting the score threshold
    """

    unique_results = []
    seen_ids = set()
    for result in rerank_results:
        doc = result.data[0]
        benchmark = 0.6
        if doc.document.id not in seen_ids and doc.score >= benchmark:
            unique_results.append(doc.document.metadata)
            with open("sample_output\\rerank_result.json", "w") as f:
                json.dump(unique_results, f, indent=4)
            seen_ids.add(doc.document.id)
    return unique_results


def filter_mixbread_results(
        rerank_results: RerankingResponse) -> List[Dict[str, Any]]:
    """
    Filter Mixbread reranking results based on score threshold and remove duplicates.

    Args:
        rerank_results (RerankingResponse): Reranking response from Mixbread

    Returns:
        List[Dict[str, Any]]: Filtered list of unique document metadata meeting the score threshold
    """

    unique_results = []
    seen_ids = set()
    for result in rerank_results:
        benchmark = 0.6
        result = result.data[0]
        doc: dict = result.input.get("metadata")
        if doc.get("id") not in seen_ids and result.score >= benchmark:
            seen_ids.add(doc.pop("id"))
            doc["score"] = result.score
            unique_results.append(doc)
    # with open("sample_output\\rerank_result_mixbread.json", "a") as f:
    #     json.dump(unique_results, f, indent=4)
    return unique_results
