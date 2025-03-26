from pinecone import ServerlessSpec, Index
from pinecone import PineconeAsyncio as Pinecone
from pinecone.data.index_asyncio import _IndexAsyncio
import os
from typing import List, Dict, Optional
from langchain.schema import Document
from pydantic import BaseModel, Field
import hashlib
from datetime import datetime

"""
Pinecone Operations Module

This module provides configuration and operation classes for interacting with the pinecone vector database
"""


class PineConeConfig(BaseModel):
    """
    Configuration class for Vector Database settings.

    This class defines the configuration parameters needed for initializing and
    operating with Pinecone and related language model services.

    Attributes:
        pinecone_api_key (Optional[str]): API key for Pinecone service
        max_pool_threads (int): Maximum number of threads for connection pool
        cloud (str): Cloud provider (default: 'aws')
        region (str): Cloud region (default: 'us-east-1')
        default_dense_model (str): Default model for dense embeddings
        default_sparse_model (str): Default model for sparse embeddings
        default_dimension (int): Default embedding dimension size
    """

    pinecone_api_key: Optional[str] = Field(None, env="PINECONE_API_KEY")
    max_pool_threads: int = Field(default=30, ge=1)
    cloud: str = Field(default="aws")
    region: str = Field(default="us-east-1")
    default_dense_model: str = Field(default="multilingual-e5-large")
    default_sparse_model: str = Field(default="pinecone-sparse-english-v0")
    default_dimension: int = Field(
        default=1024, ge=1)  # Ensuring it's positive


class PineconeOperations:
    """
    Handles operations with Pinecone vector database including indexing and querying.

    This class provides comprehensive functionality for managing Pinecone indexes,
    performing vector operations, and handling hybrid search queries.

    Attributes:
        _pc (Pinecone): Pinecone client instance
        _spec (ServerlessSpec): Serverless specification for Pinecone
        _current_index_host (str): Current active index host
        _current_index (_IndexAsyncio): Current active index instance
        _current_index_name (str): Name of the current active index
        _default_dense_model (str): Default model for dense embeddings
        _default_sparse_model (str): Default model for sparse embeddings
        _default_dimension (int): Default embedding dimension

    Methods:
        create: Factory method to create PineconeOperations instance
        create_index: Create a new Pinecone index
        upsert_documents: Insert or update documents in the index
        hybrid_query: Perform hybrid search queries
        rerank: Rerank search results
    """

    __from_create = False

    __slots__ = (
        '_pc',
        '_spec',
        '_current_index_host',
        '_current_index',
        '_current_index_name',
        '_default_dense_model',
        '_default_sparse_model',
        '_default_dimension')

    def __init__(self, config: PineConeConfig, **kwargs):
        """
        Private constructor. Users should not call this directly.
        """

        if not self.__from_create:
            raise RuntimeError(
                "Use PineconeOperations.create() to instantiate this class.")

        self._pc: Pinecone = None
        self._spec = ServerlessSpec(cloud=config.cloud, region=config.region)

        # Configuration attributes
        self._default_dense_model = config.default_dense_model
        self._default_sparse_model = config.default_sparse_model
        self._default_dimension = config.default_dimension

        # Mutable runtime attributes
        self._current_index_host = None
        self._current_index: _IndexAsyncio = None
        self._current_index_name = None

    @classmethod
    async def create(cls, config: Optional[PineConeConfig] = None, **kwargs):
        """
        Asynchronously create a PineconeOperations instance.

        :param config: Configuration for the PineconeOperations instance.
        :param kwargs: Additional keyword arguments for configuration.
        :return: An instance of PineconeOperations.
        """
        # Use provided config or create a default one
        config = config or PineConeConfig(**kwargs)
        api_key = config.pinecone_api_key or os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError(
                "PINECONE_API_KEY is required to initialize Pinecone.")

        cls.__from_create = True
        instance = cls(config, **kwargs)
        instance._pc = Pinecone(
            api_key=api_key,
            pool_threads=config.max_pool_threads)
        return instance

    @property
    def default_dense_model(self) -> str:
        """
        Getter for default dense embedding model.

        A property decorator transforms a method into an attribute-like accessor.
        It allows read-only access to the underlying attribute.
        """
        return self._default_dense_model

    @property
    def default_sparse_model(self) -> str:
        """Getter for default sparse embedding model."""
        return self._default_sparse_model

    @property
    def default_dimension(self) -> int:
        """Getter for default embedding dimension."""
        return self._default_dimension

    def get_current_index(self) -> Optional[_IndexAsyncio]:
        """Getter for the current active Pinecone index."""
        return self._current_index

    async def create_index(
        self,
        index_name: str,
        dimension: Optional[int] = None,
        metric: str = "dotproduct",
        deletion_protection: str = "disabled"
    ) -> Optional[Index]:
        """
        Create a Pinecone index with specified parameters.

        :param index_name: Name of the index
        :param dimension: Embedding dimension (uses default if not specified)
        :param metric: Distance metric for index
        :param deletion_protection: Deletion protection setting
        :return: Created index or None if index already exists
        """
        if not await self._pc.has_index(index_name):
            index_model = await self._pc.create_index(
                name=index_name,
                metric=metric,
                dimension=dimension or self._default_dimension,
                deletion_protection=deletion_protection,
                spec=self._spec
            )
            await self.set_current_index(index_host=index_model.host, index_name=index_name)
        if index_name != self._current_index_name:
            await self.set_current_index(index_name)
        return self._current_index

    async def set_current_index(
            self,
            index_name: str,
            index_host: str = None) -> bool:
        """
        Set the current active Pinecone index.

        :param index_name: Name of the index to set as current
        """
        if not await self._pc.has_index(index_name):
                return False
        if not self._current_index_name == index_name and self._current_index:
            await self._current_index.close()
        elif self._current_index_name == index_name:
            return True

        if not index_host:
            index_model = await self._pc.describe_index(index_name)
            self._current_index_host = index_model.host
        else:
            self._current_index_host = index_host
        self._current_index_name = index_name
        self._current_index = self._pc.IndexAsyncio(
            host=self._current_index_host)
        return True

    async def get_dense_embeddings(
        self,
        input_data: List[str],
        model: Optional[str] = None,
        input_type: str = "passage"
    ) -> Dict:
        """
        Generate dense embeddings for given inputs.

        :param input_data: List of text inputs
        :param model: Embedding model (uses default if not specified)
        :param input_type: Type of input for embedding
        :return: Dense embeddings
        """
        result = await self._pc.inference.embed(
            model=model or self._default_dense_model,
            inputs=input_data,
            parameters={
                "input_type": input_type,
                "truncate": "END"
            }
        )
        return result.data

    async def get_sparse_embeddings(
        self,
        input_data: List[str],
        model: Optional[str] = None,
        input_type: str = "passage"
    ) -> Dict:
        """
        Generate sparse embeddings for given inputs.

        :param input_data: List of text inputs
        :param model: Sparse embedding model (uses default if not specified)
        :param input_type: Type of input for embedding
        :return: Sparse embeddings
        """
        result = await self._pc.inference.embed(
            model=model or self._default_sparse_model,
            inputs=input_data,
            parameters={
                "input_type": input_type,
                "truncate": "END"
            }
        )

        return result.data

    def make_id(
            self,
            metadata: Dict,
            chunk_num: int,
            batch_num: Optional[int]) -> str:
        basename = str(
            os.path.basename(
                metadata.get(
                    "file_path",
                    ""))).replace(
            " ",
            "-").removesuffix(".pdf")
        page_num = metadata.get("page", "")
        hash_ = f"{hashlib.sha256(str(datetime.now().timestamp()).encode()).hexdigest()[-12:]}"
        if batch_num:
            return f"{basename}-{page_num}-{chunk_num}-{hash_}-{batch_num}"
        return f"{basename}-{page_num}-{chunk_num}-{hash_}"

    # TODO: Pinecone allows upserting 1000 document in one batch request.
    # currently , we are sending 90 documents in one batch request for
    # embedding.

    async def upsert_documents(
        self,
        batches: List[List[Document]],
        dense_model: Optional[str] = None,
        sparse_model: Optional[str] = None,
    ) -> None:
        """
        Embed and upsert documents to the current index.

        :param documents: List of Langchain Documents
        :param dense_model: Optional custom dense embedding model
        :param sparse_model: Optional custom sparse embedding model
        """
        chunk_num = 1
        if not self._current_index:
            raise ValueError("No active index. Create or set an index first.")
        upsert_vectors = []
        for batch_num, documents in enumerate(batches):

            texts = [doc.page_content for doc in documents]
            dense_embeddings = await self.get_dense_embeddings(texts, model=dense_model)
            sparse_embeddings = await self.get_sparse_embeddings(texts, model=sparse_model)

            for doc, dense, sparse in zip(
                    documents, dense_embeddings, sparse_embeddings):
                doc.metadata["page_content"] = doc.page_content
                id = self.make_id(doc.metadata, chunk_num, batch_num)
                doc.metadata["id"] = id
                upsert_vector = {
                    'id': id,
                    'values': dense.get('values'),
                    'sparse_values': {
                        'values': sparse.get('sparse_values'),
                        'indices': sparse.get('sparse_indices')
                    },
                    'metadata': doc.metadata
                }
                upsert_vectors.append(upsert_vector)
                chunk_num += 1

                if batch_num == 9 or batch_num == len(batches) - 1:
                    await self._current_index.upsert(vectors=upsert_vectors, async_req=True)
                    upsert_vectors = []
                    chunk_num = 1

    def hybrid_score_norm(self, dense, sparse, alpha: float):
        """Hybrid score using a convex combination

        alpha * dense + (1 - alpha) * sparse

        Args:
            dense: Array of floats representing
            sparse: a dict of `indices` and `values`
            alpha: scale between 0 and 1
        """
        if alpha < 0 or alpha > 1:
            raise ValueError("Alpha must be between 0 and 1")
        if sparse:
            hs = {
                'indices': sparse['indices'],
                'values': [v * (1 - alpha) for v in sparse['values']]
            }
        else:
            raise ValueError("Sparse vector cannot be None or empty")
        return [v * alpha for v in dense], hs

    async def sparse_query(
        self,
        query: str | Dict,
        top_k: int = 10,
        include_metadata: bool = True
    ) -> Dict:
        """Perform a sparse vector query."""
        if isinstance(query, str):
            sparse = await self.get_sparse_embeddings([query], input_type="query")[0]
            sparse_vector = {
                "values": sparse.get("sparse_values"),
                "indices": sparse.get("sparse_indices")
            }
            query = {
                "sparse_vector": sparse_vector,
                "top_k": top_k,
                "include_metadata": include_metadata
            }

        return await self._current_index.query(**query)

    async def dense_query(
        self,
        query: str | Dict,
        top_k: int = 10,
        include_metadata: bool = True
    ) -> Dict:
        """Perform a dense vector query."""
        if isinstance(query, str):
            dense_vector = self.get_dense_embeddings(
                [query], input_type="query")[0].get("values")
            query = {
                "vector": dense_vector,
                "top_k": top_k,
                "include_metadata": include_metadata
            }

        return await self._current_index.query(**query)

    async def hybrid_query(
        self,
        query: str | Dict,
        top_k: int = 10,
        include_metadata: bool = True,
    ) -> Dict:
        """
        Query the current index with flexible input options.

        :param query: Query string or pre-prepared query dictionary
        :param top_k: Number of results to return
        :param include_metadata: Whether to include document metadata
        :return: Query results
        """
        if not self._current_index:
            raise ValueError("No active index. Create or set an index first.")

        if isinstance(query, str):
            dense_vector = await self.get_dense_embeddings([query], input_type='query')
            dense_vector = dense_vector[0].get("values")
            sparse = await self.get_sparse_embeddings([query], input_type='query')
            sparse = sparse[0]
            sparse_vector = {
                "values": sparse.get("sparse_values"),
                "indices": sparse.get("sparse_indices")
            }

            normalized_dense_vector, normalized_sparse_vector = self.hybrid_score_norm(
                dense_vector, sparse_vector, alpha=0.5)
            query = {
                "vector": normalized_dense_vector,
                "sparse_vector": normalized_sparse_vector,
                "top_k": top_k,
                "include_metadata": include_metadata
            }
        elif isinstance(query, dict):
            query["top_k"] = query.get("top_k", top_k)
            query["include_metadata"] = query.get(
                "include_metadata", include_metadata)
        else:
            raise ValueError("""Query must be a string or a dictionary in
                              {
                "vector": hdense,
                "sparse_vector": hsparse,
                "top_k": top_k,
                "include_metadata": include_metadata
            } format""")

        return await self._current_index.query(**query)

    async def delete_index(self, index_name: str) -> None:
        """
        Delete a Pinecone index.

        :param index_name: Name of the index to delete
        """
        await self._pc.delete_index(index_name, timeout=-1)

    async def rerank(
            self,
            query: str,
            matches: List[Dict],
            model: str = "bge-reranker-v2-m3",
            top_n: int = 3) -> List[Dict]:
        """
        Rerank the top-k matches using the retrieved text.

        :param query: User's search query
        :param matches: List of retrieved documents (from Pinecone search)
        :param top_k: Number of results to return after reranking
        :return: Reranked list of documents
        """
        rerank_doc = []
        for match in matches:
            rerank_doc.append({
                'id': match.get('id'),
                "page_content": match.get('metadata').get('page_content'),
                "metadata": match.get('metadata')
            })
        result = await self._pc.inference.rerank(
            model=model,
            query=query,
            documents=rerank_doc,
            top_n=top_n,
            rank_fields=["page_content"],
            return_documents=True,
            parameters={"truncate": "END"})

        return result

    async def get_idx_stat(self) -> Dict:
        """Get index statistics."""
        stat = await self._current_index.describe_index_stats()
        return stat.total_vector_count

    async def cleanup(self) -> None:
        """Cleanup resources."""
        if self._current_index:
            await self._current_index.close()
        if self._pc:
            await self._pc.close()

    def has_index(self, index_name) -> bool:
        """Check if an index is currently active."""
        return self._pc.has_index(index_name)
