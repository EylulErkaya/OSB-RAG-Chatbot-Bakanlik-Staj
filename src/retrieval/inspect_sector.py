import json


CHUNKS_PATH = "data/documents/chunks.jsonl"


print("=" * 70)
print("SEKTÖR CHUNK ANALİZİ")
print("=" * 70)


with open(
    CHUNKS_PATH,
    "r",
    encoding="utf-8"
) as file:

    for line in file:

        if not line.strip():
            continue

        chunk = json.loads(line)

        metadata = chunk.get(
            "metadata",
            {}
        )

        if (
            metadata.get("osb_id") == 305
            and metadata.get("chunk_type") == "sector"
        ):

            print("\n" + "-" * 70)

            print(
                f"Chunk ID: "
                f"{chunk.get('chunk_id')}"
            )

            print(
                f"OSB ID: "
                f"{metadata.get('osb_id')}"
            )

            print(
                f"OSB: "
                f"{metadata.get('osb_adi')}"
            )

            print(
                "\nMETADATA:"
            )

            print(
                metadata
            )

            print(
                "\nTEXT:"
            )

            print(
                chunk.get("text")
            )