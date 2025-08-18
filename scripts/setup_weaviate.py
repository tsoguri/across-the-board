import json
import os
import sys
from typing import Any, Dict, Iterable, List

import weaviate
import weaviate.classes as wvc
from weaviate.classes.config import Configure, DataType, Property

WEAVIATE_HOST = os.getenv("WEAVIATE_HOST", "localhost")
WEAVIATE_PORT = int(os.getenv("WEAVIATE_PORT", "8080"))
JSON_PATH = os.getenv("JSON_PATH", "scripts/data/clues.json")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "CrosswordClues")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "200"))

KEY_CLUE = os.getenv("KEY_CLUE", "clue")
KEY_ANSWER = os.getenv("KEY_ANSWER", "answer")
KEY_YEAR = os.getenv("KEY_YEAR", "year")
KEY_PUBID = os.getenv("KEY_PUBID", "pubid")
KEY_VECTOR = os.getenv("KEY_VECTOR", "embedding_vector")  # <— BYO vector column


def read_json(path: str) -> Iterable[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("Expected JSON file to contain a list of objects")
        for obj in data:
            yield obj


def validate_vector(vec: Any) -> List[float]:
    if not isinstance(vec, (list, tuple)):
        raise ValueError("Vector must be a list/tuple of numbers")
    out = []
    for x in vec:
        try:
            out.append(float(x))
        except Exception as e:
            raise ValueError(f"Vector contains a non-numeric value: {x!r}") from e
    if len(out) == 0:
        raise ValueError("Vector is empty")
    return out


def make_collection(client: weaviate.WeaviateClient):
    existing = [c for c in client.collections.list_all()]
    print(f"Existing collections: {existing}")
    if COLLECTION_NAME in existing:
        client.collections.delete(COLLECTION_NAME)

    props = [
        Property(name="clue", data_type=DataType.TEXT),
        Property(name="answer", data_type=DataType.TEXT),
        Property(name="year", data_type=DataType.INT),
        Property(name="pubid", data_type=DataType.TEXT),
    ]

    # BYO vectors: disable vectorizer, declare self_provided
    vector_cfg = Configure.Vectors.self_provided()

    client.collections.create(
        name=COLLECTION_NAME,
        properties=props,
        vector_config=vector_cfg,
    )


def import_data(
    client: weaviate.WeaviateClient,
    rows: Iterable[Dict[str, Any]],
) -> int:
    coll = client.collections.get(COLLECTION_NAME)
    batch: List[wvc.data.DataObject] = []
    count = 0

    def flush():
        nonlocal batch, count
        if not batch:
            return
        # insert_many accepts a list of DataObject
        coll.data.insert_many(batch)
        count += len(batch)
        batch = []

    for row in rows:
        clue = row.get(KEY_CLUE)
        answer = row.get(KEY_ANSWER)
        year = row.get(KEY_YEAR)
        pubid = row.get(KEY_PUBID)
        vec_raw = row.get(KEY_VECTOR)

        # required fields
        if not clue or not answer or vec_raw is None:
            continue

        try:
            vector = validate_vector(vec_raw)
        except ValueError as e:
            # Skip bad rows but continue the import
            print(f"Skipping row due to invalid vector: {e}", file=sys.stderr)
            continue

        obj = wvc.data.DataObject(
            properties={
                "clue": clue,
                "answer": answer,
                "year": year,
                "pubid": pubid,
            },
            vector=vector,
        )

        batch.append(obj)
        if len(batch) >= BATCH_SIZE:
            flush()

    flush()
    return count


def demo_query(client: weaviate.WeaviateClient, sample_vector: List[float]):
    coll = client.collections.get(COLLECTION_NAME)
    print("\n=== Demo vector search ===")
    res = coll.query.near_vector(near_vector=sample_vector, limit=3)
    print("near_vector results (top 3):")
    for obj in res.objects:
        print("-", obj.properties)


def main() -> int:
    client = weaviate.connect_to_local(host=WEAVIATE_HOST, port=WEAVIATE_PORT)

    try:
        if not os.path.exists(JSON_PATH):
            print(f"ERROR: JSON file not found at {JSON_PATH}", file=sys.stderr)
            return 2

        N_PEEK = 20
        buf: List[Dict[str, Any]] = []
        it = read_json(JSON_PATH)
        for _ in range(N_PEEK):
            try:
                buf.append(next(it))
            except StopIteration:
                break

        if not buf:
            print("No data found in JSON; nothing to import.")
            return 0

        sample_vector = None
        for r in buf:
            if KEY_VECTOR in r:
                try:
                    sample_vector = validate_vector(r[KEY_VECTOR])
                    break
                except ValueError:
                    continue
        if sample_vector is None:
            print(
                f"No valid '{KEY_VECTOR}' found in the first {N_PEEK} rows; cannot run demo query.",
                file=sys.stderr,
            )

        make_collection(client)

        # Chain the peeked rows back with the iterator
        def all_rows():
            for r in buf:
                yield r
            for r in it:
                yield r

        total = import_data(client, all_rows())
        print(f"Imported {total} objects into collection '{COLLECTION_NAME}'.")

        import time

        time.sleep(2)

        if sample_vector is not None:
            demo_query(client, sample_vector)
        print("\nSetup complete.")
        return 0

    finally:
        client.close()


if __name__ == "__main__":
    sys.exit(main())
