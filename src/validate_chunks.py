import json
from collections import Counter
from pathlib import Path


INPUT_PATH = Path("data/documents/chunks.jsonl")


# --------------------------------------------------
# DOSYAYI OKU
# --------------------------------------------------

chunks = []

with open(
    INPUT_PATH,
    "r",
    encoding="utf-8"
) as file:

    for line in file:

        if line.strip():
            chunks.append(json.loads(line))


print("=" * 70)
print("CHUNK DOĞRULAMA")
print("=" * 70)

print(f"Toplam chunk: {len(chunks)}")


# --------------------------------------------------
# 1. BOŞ CHUNK KONTROLÜ
# --------------------------------------------------

empty_chunks = [
    chunk
    for chunk in chunks
    if not chunk.get("text", "").strip()
]

print("\n1. BOŞ CHUNK")
print("-" * 70)

print(f"Boş chunk sayısı: {len(empty_chunks)}")


# --------------------------------------------------
# 2. CHUNK ID KONTROLÜ
# --------------------------------------------------

chunk_ids = [
    chunk.get("chunk_id")
    for chunk in chunks
]

id_counts = Counter(chunk_ids)

duplicate_ids = {
    chunk_id: count
    for chunk_id, count in id_counts.items()
    if count > 1
}

print("\n2. CHUNK ID")
print("-" * 70)

print(f"Benzersiz chunk ID: {len(set(chunk_ids))}")
print(f"Duplicate ID sayısı: {len(duplicate_ids)}")

if duplicate_ids:
    print("\nDuplicate ID'ler:")
    for chunk_id, count in duplicate_ids.items():
        print(f"- {chunk_id}: {count}")


# --------------------------------------------------
# 3. METADATA KONTROLÜ
# --------------------------------------------------

required_metadata = [
    "osb_id",
    "osb_adi",
    "il",
    "bolge",
    "document_type",
    "chunk_type",
]

missing_metadata = []

for chunk in chunks:

    metadata = chunk.get("metadata", {})

    missing = [
        field
        for field in required_metadata
        if field not in metadata
        or metadata[field] is None
    ]

    if missing:

        missing_metadata.append({
            "chunk_id": chunk.get("chunk_id"),
            "missing": missing
        })


print("\n3. METADATA")
print("-" * 70)

print(
    f"Eksik metadata bulunan chunk: "
    f"{len(missing_metadata)}"
)

if missing_metadata:

    for item in missing_metadata[:10]:
        print(item)


# --------------------------------------------------
# 4. CHUNK TİPLERİ
# --------------------------------------------------

chunk_types = Counter(
    chunk["metadata"]["chunk_type"]
    for chunk in chunks
)

print("\n4. CHUNK TİPLERİ")
print("-" * 70)

for chunk_type, count in sorted(
    chunk_types.items()
):
    print(
        f"{chunk_type:<20}: {count}"
    )


# --------------------------------------------------
# 5. OSB ID KONTROLÜ
# --------------------------------------------------

osb_ids = {
    chunk["metadata"]["osb_id"]
    for chunk in chunks
}

print("\n5. OSB ID")
print("-" * 70)

print(
    f"Benzersiz OSB sayısı: {len(osb_ids)}"
)

print(
    f"İlk OSB ID: {min(osb_ids)}"
)

print(
    f"Son OSB ID: {max(osb_ids)}"
)


# --------------------------------------------------
# 6. OSB BAŞINA CHUNK SAYISI
# --------------------------------------------------

chunks_per_osb = Counter(
    chunk["metadata"]["osb_id"]
    for chunk in chunks
)

counts = list(
    chunks_per_osb.values()
)

print("\n6. OSB BAŞINA CHUNK")
print("-" * 70)

print(
    f"Minimum: {min(counts)}"
)

print(
    f"Maksimum: {max(counts)}"
)

print(
    f"Ortalama: {sum(counts) / len(counts):.2f}"
)


# --------------------------------------------------
# 7. METİN UZUNLUKLARI
# --------------------------------------------------

lengths = [
    len(chunk["text"])
    for chunk in chunks
]

print("\n7. METİN UZUNLUKLARI")
print("-" * 70)

print(
    f"Minimum karakter: {min(lengths)}"
)

print(
    f"Maksimum karakter: {max(lengths)}"
)

print(
    f"Ortalama karakter: "
    f"{sum(lengths) / len(lengths):.2f}"
)


# --------------------------------------------------
# 8. ÇOK KISA CHUNK
# --------------------------------------------------

very_short = [
    chunk
    for chunk in chunks
    if len(chunk["text"].strip()) < 30
]

print("\n8. ÇOK KISA CHUNK")
print("-" * 70)

print(
    f"30 karakterden kısa chunk: "
    f"{len(very_short)}"
)

if very_short:

    print("\nÖrnekler:")

    for chunk in very_short[:10]:

        print(
            f"- {chunk['chunk_id']}: "
            f"{chunk['text']!r}"
        )


# --------------------------------------------------
# 9. SEKTÖR KONTROLÜ
# --------------------------------------------------

sector_chunks = [
    chunk
    for chunk in chunks
    if chunk["metadata"]["chunk_type"] == "sector"
]

sector_osb_ids = {
    chunk["metadata"]["osb_id"]
    for chunk in sector_chunks
}

print("\n9. SEKTÖR KONTROLÜ")
print("-" * 70)

print(
    f"Sektör chunk sayısı: "
    f"{len(sector_chunks)}"
)

print(
    f"Sektörlerde benzersiz OSB: "
    f"{len(sector_osb_ids)}"
)


# --------------------------------------------------
# 10. OSB GENEL KONTROLÜ
# --------------------------------------------------

general_types = [
    "osb_basic",
    "osb_parcel",
    "osb_employment",
]

print("\n10. OSB GENEL KONTROLÜ")
print("-" * 70)

for chunk_type in general_types:

    ids = {
        chunk["metadata"]["osb_id"]
        for chunk in chunks
        if chunk["metadata"]["chunk_type"] == chunk_type
    }

    print(
        f"{chunk_type:<20}: "
        f"{len(ids)} OSB"
    )


# --------------------------------------------------
# SONUÇ
# --------------------------------------------------

print("\n" + "=" * 70)
print("DOĞRULAMA SONUCU")
print("=" * 70)

has_error = False


if empty_chunks:
    print("❌ Boş chunk bulundu.")
    has_error = True
else:
    print("✅ Boş chunk yok.")


if duplicate_ids:
    print("❌ Duplicate chunk ID bulundu.")
    has_error = True
else:
    print("✅ Duplicate chunk ID yok.")


if missing_metadata:
    print("❌ Eksik metadata bulundu.")
    has_error = True
else:
    print("✅ Metadata eksiksiz.")


if len(sector_chunks) != 12000:
    print("❌ Sektör chunk sayısı 12000 değil.")
    has_error = True
else:
    print("✅ 12000 sektör chunk mevcut.")


if len(osb_ids) != 500:
    print("❌ OSB sayısı 500 değil.")
    has_error = True
else:
    print("✅ 500 OSB mevcut.")


if has_error:
    print("\n⚠️ VERİDE KONTROL GEREKTİREN DURUM VAR.")
else:
    print("\n🎉 TÜM CHUNK KONTROLLERİ BAŞARILI.")


print("=" * 70)