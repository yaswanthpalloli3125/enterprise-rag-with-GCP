from qdrant_client import QdrantClient
from app.config import settings

client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
)

print("Connected")

print(client.get_collections())