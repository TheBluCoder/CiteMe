"""
Search API Module

This module provides functionality for interacting with search APIs to retrieve
and process search results. It includes:

- Search result retrieval
- Data cleaning and normalization
- Metadata extraction
- Error handling and logging

The SearchApi class handles all search-related operations, including:
- Initializing HTTP sessions
- Executing search queries
- Cleaning and formatting results
- Managing API rate limits and errors

Classes:
    SearchApi: Main class for handling search API operations
"""

import os
from urllib.parse import quote_plus
from src.config.async_http_session import AsyncHTTPClient
from src.config.config import search_config
from datetime import datetime, timezone as tz
from src.config.log_config import setup_logging
from typing import Optional


filename = os.path.basename(__file__)
logger = setup_logging(filename=filename)


class SearchApi:
    session = None  # Shared session

    @classmethod
    async def init_session(cls):
        """Initialize the shared aiohttp session"""
        if cls.session is None:
            cls.session = await AsyncHTTPClient.getSession()

    @classmethod
    async def search(cls, query: str, top_n: Optional[int] = None) -> dict:
        """Fetch search results asynchronously using a shared session."""
        if not cls.session:
            await cls.init_session()

        url = search_config.SEARCH_URL.format(
            API_KEY=os.getenv("GPSE_API_KEY"),
            CX=os.getenv("CX"),
            query=quote_plus(query),
            TOP_N=top_n or search_config.TOP_N,
            DATE_RESTRICT=search_config.DATE_RESTRICT
        )

        try:
            async with cls.session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
        except Exception as e:
            logger.critical(f"Error occurred while fetching search results: {str(e)}")
            raise e

        # with open("sample_output\\search_results.json", "w") as f:
        #     json.dump(data, f, indent=4)

        return data

    @classmethod
    async def clean_data(cls, data: dict) -> dict:
        """Extracts relevant metadata from search results."""
        cleaned_data = {}
        links = []

        for item in data.get("items", []):
            pagemap = item.get("pagemap", {})
            metatags = pagemap.get("metatags", [{}])[0]
            link = metatags.get("citation_pdf_url") or metatags.get(
                "htmlFormattedUrl",) or metatags.get("og:url", "")

            if link:
                cleaned_data[link] = cls.clean(metatags)
                links.append(link)

        result = {"meta": cleaned_data, "links": links}

        return result

    @classmethod
    async def clean_search(
            cls,
            query: str,
            top_n: Optional[int] = None) -> dict:
        """Performs search and cleans the data asynchronously."""
        data = await cls.search(query, top_n=top_n)
        return await cls.clean_data(data)

    @classmethod
    def clean(cls, metatags: dict) -> dict:
        """Cleans metadata from search results."""
        field_mappings = {
            'title': [
                'citation_title',
                'dc.title',
                'og:title'],
            'link': [
                'citation_pdf_url',
                'htmlFormattedUrl',
                'og:url'],
            'type': [
                'type',
                'og:type'],
            'publisher': [
                'dc.publisher',
                'citation_publisher'],
            'journal_title': [
                'citation_journal_title',
                'citation_conference_title',
                'citation_book_title'],
            'publication_date': [
                'prism.publicationdate',
                'Updated Date',
                'citation_publication_date'],
            'citation_doi': ['citation_doi'],
            'author_name': [
                'dc.creator',
                'citation_author'],
            'volume': ['citation_volume'],
            'issn': [
                'citation_issn',
                'prism.issn'],
            'abstract': [
                'citation_abstract',
                'dc.description'],
        }
        # Create result dictionary using dictionary comprehension
        result = {
            field: next((metatags.get(key) for key in keys if metatags.get(key)), '')
            for field, keys in field_mappings.items()
        }

        # Add access date separately since it doesn't depend on metatags
        result['access_date'] = datetime.now(
            tz.utc).strftime("%Y-%m-%d %H:%M:%S")

        # Set default type if none found
        if not result['type']:
            result['type'] = 'website'

        return result
