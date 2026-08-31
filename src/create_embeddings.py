import json
import pickle
from pathlib import Path

import ollama


# ============================================================
# AYARLAR
# ============================================================

MODEL = "nomic-embed-text:v1.5"

CHUNKS_PATH = Path("data/documents/chunks.jsonl")
OUTPUT_PATH = Path("data/embeddings/embeddings.pkl")

BATCH_SIZE = 32

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# CHUNK'LARI OKU
# ============================================================

print("=" * 70)
print("RAG EMBEDDING OLUŞTURMA")
print("=" * 70)

chunks = []

with open(
    CHUNKS_PATH,
    "r",
    encoding="utf-8"
) as file:

    for line in file:

        if line.strip():
            chunks.append(
                json.loads(line)
            )


print(f"Toplam chunk: {len(chunks)}")
print(f"Model: {MODEL}")
print(f"Batch boyutu: {BATCH_SIZE}")


# ============================================================
# DAHA ÖNCE KAYDEDİLMİŞ EMBEDDING VAR MI?
# ============================================================

embeddings = []
start_index = 0

if OUTPUT_PATH.exists():

    print("\nMevcut embedding dosyası bulundu.")
    print("Devam edilen işlem kontrol ediliyor...")

    with open(
        OUTPUT_PATH,
        "rb"
    ) as file:

        saved_data = pickle.load(file)

    embeddings = saved_data["embeddings"]

    start_index = len(embeddings)

    print(
        f"Daha önce tamamlanan: "
        f"{start_index}"
    )

    print(
        f"Kalan: "
        f"{len(chunks) - start_index}"
    )


# ============================================================
# EMBEDDING
# ============================================================

print("\n" + "=" * 70)
print("EMBEDDING İŞLEMİ")
print("=" * 70)


for start in range(
    start_index,
    len(chunks),
    BATCH_SIZE
):

    end = min(
        start + BATCH_SIZE,
        len(chunks)
    )

    batch = chunks[start:end]

    texts = [
        chunk["text"]
        for chunk in batch
    ]


    # --------------------------------------------------------
    # OLLAMA EMBEDDING
    # --------------------------------------------------------

    try:

        response = ollama.embed(
            model=MODEL,
            input=texts
        )

        batch_embeddings = response["embeddings"]

    except Exception as error:

        print("\n❌ Embedding hatası:")
        print(error)

        print(
            f"\nİşlem {start}. chunk civarında durduruldu."
        )

        print(
            "Kaydedilmiş embeddingler korunmuştur."
        )

        break


    embeddings.extend(
        batch_embeddings
    )


    # --------------------------------------------------------
    # İLERLEME
    # --------------------------------------------------------

    completed = len(embeddings)

    percentage = (
        completed / len(chunks)
    ) * 100

    print(
        f"{completed:>5}/{len(chunks)} "
        f"(%{percentage:6.2f})"
    )


    # --------------------------------------------------------
    # ARA KAYIT
    # --------------------------------------------------------

    if (
        completed % 320 == 0
        or completed == len(chunks)
    ):

        save_data = {
            "model": MODEL,
            "chunk_count": completed,
            "embeddings": embeddings
        }

        with open(
            OUTPUT_PATH,
            "wb"
        ) as file:

            pickle.dump(
                save_data,
                file
            )

        print(
            f"   ↳ Kaydedildi: {completed}"
        )


# ============================================================
# SON KAYIT
# ============================================================

if len(embeddings) == len(chunks):

    save_data = {
        "model": MODEL,
        "chunk_count": len(embeddings),
        "embeddings": embeddings
    }

    with open(
        OUTPUT_PATH,
        "wb"
    ) as file:

        pickle.dump(
            save_data,
            file
        )


# ============================================================
# SONUÇ
# ============================================================

print("\n" + "=" * 70)
print("EMBEDDING SONUCU")
print("=" * 70)

print(
    f"Chunk sayısı       : {len(chunks)}"
)

print(
    f"Embedding sayısı   : {len(embeddings)}"
)

print(
    f"Embedding boyutu   : "
    f"{len(embeddings[0]) if embeddings else 0}"
)

print(
    f"Model              : {MODEL}"
)

print(
    f"Dosya              : {OUTPUT_PATH}"
)


if len(embeddings) == len(chunks):

    print("\nTUM EMBEDDING'LER BASARIYLA OLUSTURULDU.")

else:

    print(
        "\nEmbedding islemi henuz tamamlanmadi."
    )