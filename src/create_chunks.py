import json
from pathlib import Path


# --------------------------------------------------
# AYARLAR
# --------------------------------------------------

INPUT_PATH = Path("data/documents/rag_documents.jsonl")
OUTPUT_PATH = Path("data/documents/chunks.jsonl")

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


# --------------------------------------------------
# JSONL OKU
# --------------------------------------------------

documents = []

with open(
    INPUT_PATH,
    "r",
    encoding="utf-8"
) as file:

    for line in file:

        if line.strip():

            documents.append(
                json.loads(line)
            )


print("=" * 70)
print("CHUNKING")
print("=" * 70)

print(f"Kaynak doküman sayısı: {len(documents)}")


# --------------------------------------------------
# CHUNK OLUŞTUR
# --------------------------------------------------

chunks = []


for document in documents:

    document_type = document["document_type"]
    metadata = document["metadata"]
    text = document["text"]

    # ==================================================
    # SEKTÖR DOKÜMANLARI
    # ==================================================

    if document_type == "sector":

        chunks.append({
            "chunk_id": document["id"],
            "text": text,
            "metadata": {
                **metadata,
                "chunk_type": "sector"
            }
        })

        continue


    # ==================================================
    # OSB GENEL DOKÜMANLARI
    # ==================================================

    if document_type == "osb_general":

        lines = text.splitlines()

        basic_lines = []
        parcel_lines = []
        employment_lines = []
        note_lines = []

        current_section = "basic"

        for line in lines:

            stripped = line.strip()

            # Bölüm değişiklikleri
            if stripped == "Parsel Bilgileri:":
                current_section = "parcel"
                continue

            if stripped == "İstihdam ve Fabrika Bilgileri:":
                current_section = "employment"
                continue

            if stripped == "Ek Not:":
                current_section = "note"
                continue

            # Boş satırları atla
            if not stripped:
                continue

            if current_section == "basic":
                basic_lines.append(stripped)

            elif current_section == "parcel":
                parcel_lines.append(stripped)

            elif current_section == "employment":
                employment_lines.append(stripped)

            elif current_section == "note":
                note_lines.append(stripped)


        osb_id = metadata["osb_id"]


        # --------------------------------------------------
        # TEMEL BİLGİ CHUNK'I
        # --------------------------------------------------

        if basic_lines:

            chunks.append({
                "chunk_id": f"osb_{osb_id}_basic",
                "text": "\n".join(basic_lines),
                "metadata": {
                    **metadata,
                    "chunk_type": "osb_basic"
                }
            })


        # --------------------------------------------------
        # PARSEL CHUNK'I
        # --------------------------------------------------

        if parcel_lines:

            chunks.append({
                "chunk_id": f"osb_{osb_id}_parcel",
                "text": (
                    f"OSB: {metadata['osb_adi']}\n"
                    "Parsel Bilgileri:\n"
                    + "\n".join(
                        parcel_lines
                    )
                ),
                "metadata": {
                    **metadata,
                    "chunk_type": "osb_parcel"
                }
            })


        # --------------------------------------------------
        # İSTİHDAM CHUNK'I
        # --------------------------------------------------

        if employment_lines:

            chunks.append({
                "chunk_id": f"osb_{osb_id}_employment",
                "text": (
                    f"OSB: {metadata['osb_adi']}\n"
                    "İstihdam ve Fabrika Bilgileri:\n"
                    + "\n".join(
                        employment_lines
                    )
                ),
                "metadata": {
                    **metadata,
                    "chunk_type": "osb_employment"
                }
            })


        # --------------------------------------------------
        # EK NOT CHUNK'I
        # --------------------------------------------------

        if note_lines:

            chunks.append({
                "chunk_id": f"osb_{osb_id}_note",
                "text": (
                    f"OSB: {metadata['osb_adi']}\n"
                    "Ek Not:\n"
                    + "\n".join(
                        note_lines
                    )
                ),
                "metadata": {
                    **metadata,
                    "chunk_type": "osb_note"
                }
            })


# --------------------------------------------------
# JSONL KAYDET
# --------------------------------------------------

with open(
    OUTPUT_PATH,
    "w",
    encoding="utf-8"
) as file:

    for chunk in chunks:

        file.write(
            json.dumps(
                chunk,
                ensure_ascii=False
            ) + "\n"
        )


# --------------------------------------------------
# İSTATİSTİKLER
# --------------------------------------------------

basic_count = sum(
    1
    for chunk in chunks
    if chunk["metadata"]["chunk_type"] == "osb_basic"
)

parcel_count = sum(
    1
    for chunk in chunks
    if chunk["metadata"]["chunk_type"] == "osb_parcel"
)

employment_count = sum(
    1
    for chunk in chunks
    if chunk["metadata"]["chunk_type"] == "osb_employment"
)

note_count = sum(
    1
    for chunk in chunks
    if chunk["metadata"]["chunk_type"] == "osb_note"
)

sector_count = sum(
    1
    for chunk in chunks
    if chunk["metadata"]["chunk_type"] == "sector"
)


# --------------------------------------------------
# SONUÇ
# --------------------------------------------------

print("\n" + "=" * 70)
print("CHUNK SONUCU")
print("=" * 70)

print(f"OSB temel chunk       : {basic_count}")
print(f"OSB parsel chunk      : {parcel_count}")
print(f"OSB istihdam chunk    : {employment_count}")
print(f"OSB ek not chunk      : {note_count}")
print(f"Sektör chunk          : {sector_count}")

print("-" * 70)

print(f"Toplam chunk          : {len(chunks)}")

print("\nDosya:")
print(OUTPUT_PATH)


# --------------------------------------------------
# ÖRNEKLER
# --------------------------------------------------

print("\n" + "=" * 70)
print("ÖRNEK CHUNK'LAR")
print("=" * 70)

for chunk in chunks[:4]:

    print("\n" + "-" * 70)

    print(
        f"ID: {chunk['chunk_id']}"
    )

    print(
        f"Tip: {chunk['metadata']['chunk_type']}"
    )

    print(chunk["text"])