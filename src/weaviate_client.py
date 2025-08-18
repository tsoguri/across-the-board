from typing import Optional

import weaviate
from sentence_transformers import SentenceTransformer

from src.settings import settings


class WeaviateClient:
    def __init__(
        self,
        host: str = settings.weaviate_host,
        port: int = settings.weaviate_port,
        collection_name=settings.collection_name,
    ):
        self.client = weaviate.connect_to_local(
            host=host, port=port
        )  # TODO: This shouldn't be local for production
        self.collection = self.client.collections.get(collection_name)
        self.embedding_model = SentenceTransformer(
            settings.embedding_model, device="cpu"
        )

    def query_collection(self, query: str, limit: Optional[int] = 7):
        """
        Query the Weaviate collection with a given query string.

        Args:
            query (str): The query string to search for.
            limit (Optional[int]): The maximum number of results to return. Defaults to 7.

        Returns:
            list: A list of results matching the query.
        """
        query_embedding = self.embedding_model.encode(query)
        res = self.collection.query.near_vector(
            near_vector=query_embedding, limit=limit
        )
        return res.objects
