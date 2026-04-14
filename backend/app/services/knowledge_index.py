from pathlib import Path
from typing import Any, Sequence

_COLLECTION_NAME = "knowledge_chunks"


def _get_chromadb():
    try:
        import chromadb
    except ModuleNotFoundError as exc:
        raise RuntimeError("未安装 chromadb，请先执行 pip install -r backend/requirements.txt") from exc
    return chromadb


def _client(index_dir: str | Path):
    path = Path(index_dir)
    path.mkdir(parents=True, exist_ok=True)
    chromadb = _get_chromadb()
    return chromadb.PersistentClient(path=str(path))


def _parse_tags(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [part.strip() for part in str(value).split(",") if part.strip()]


def _get_collection(index_dir: str | Path):
    client = _client(index_dir)
    return client.get_or_create_collection(name=_COLLECTION_NAME, metadata={"hnsw:space": "cosine"})


def reset_knowledge_index(index_dir: str | Path):
    client = _client(index_dir)
    try:
        client.delete_collection(name=_COLLECTION_NAME)
    except Exception:
        pass
    return client.get_or_create_collection(name=_COLLECTION_NAME, metadata={"hnsw:space": "cosine"})


def add_knowledge_chunks(
    index_dir: str | Path,
    ids: Sequence[str],
    documents: Sequence[str],
    embeddings: Sequence[Sequence[float]],
    metadatas: Sequence[dict[str, Any]],
) -> None:
    if not ids:
        return
    collection = _get_collection(index_dir)
    collection.add(
        ids=list(ids),
        documents=list(documents),
        embeddings=[list(item) for item in embeddings],
        metadatas=list(metadatas),
    )


def query_knowledge(index_dir: str | Path, embedding: Sequence[float], top_k: int = 3) -> list[dict[str, Any]]:
    collection = _get_collection(index_dir)
    if collection.count() == 0:
        return []
    result = collection.query(
        query_embeddings=[list(embedding)],
        n_results=max(1, top_k),
        include=["documents", "metadatas", "distances"],
    )
    documents = result.get("documents") or [[]]
    metadatas = result.get("metadatas") or [[]]
    distances = result.get("distances") or [[]]
    rows: list[dict[str, Any]] = []
    for document, metadata, distance in zip(documents[0], metadatas[0], distances[0]):
        score = 1 - float(distance or 0)
        rows.append(
            {
                "title": (metadata or {}).get("title") or "",
                "source": (metadata or {}).get("source_file") or "",
                "source_title": (metadata or {}).get("source_title") or "",
                "tags": _parse_tags((metadata or {}).get("tags")),
                "content": document or "",
                "score": round(score, 4),
            }
        )
    return rows
