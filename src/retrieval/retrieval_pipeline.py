"""
GERÇEK RAG RETRIEVAL PIPELINE

Akış:

    Kullanıcı Sorusu
          ↓
    Intent Detection
          ↓
    OSB Entity Extraction
          ↓
    OSB Entity Resolution
          ↓
    Metadata Filter
          ↓
    ChromaDB Top-K
          ↓
    Cross-Encoder Reranker
          ↓
    Top-N Context
"""

import os
import sys
import re

import chromadb
import ollama

from sector_resolver import (
    extract_sector_keyword,
    matches_sector,
)

# ============================================================
# PYTHON PATH
# ============================================================

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

SRC_DIR = os.path.dirname(
    CURRENT_DIR
)

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


# ============================================================
# PROJECT IMPORTS
# ============================================================

from retrieval.osb_resolver import resolve_osb
from retrieval.query_intent import (
    detect_intent,
    get_chunk_type,
)
from retrieval.reranker import Reranker


# ============================================================
# CONFIGURATION
# ============================================================

CHROMA_PATH = "data/vectorstore/chroma"

COLLECTION_NAME = "osb_knowledge_base"

EMBEDDING_MODEL = "nomic-embed-text:v1.5"

# Chroma'dan alınacak aday sayısı
CHROMA_TOP_K = 10

# Reranker'dan sonra tutulacak sonuç sayısı
RERANK_TOP_K = 3


# ============================================================
# CHROMADB
# ============================================================

print(
    f"ChromaDB başlatılıyor: {CHROMA_PATH}"
)

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_collection(
    name=COLLECTION_NAME
)

print(
    f"Collection: {COLLECTION_NAME}"
)

print(
    f"Kayıt sayısı: {collection.count()}"
)


# ============================================================
# RERANKER
# ============================================================

reranker = Reranker()


# ============================================================
# OSB ENTITY EXTRACTION
# ============================================================

def extract_osb_name(query: str):
    if not query:
        return None

    text = query.strip()

    match = re.search(r"\bOSB\b", text, flags=re.IGNORECASE)
    if not match:
        return None

    osb_name = text[:match.start()].strip()
    osb_name = osb_name.strip(" .,;:!?-'\"")

    if not osb_name:
        return None

    # Çoklu kelimeli isim (örn. "Yeni Sanayi") -> sonuna OSB ekle
    if " " in osb_name:
        parts = osb_name.split()
        if len(parts) == 1:
            return osb_name
        return osb_name + " OSB"

    # Tireli bileşik isim (Malatya-Güney, Malatya-Yeni) -> olduğu gibi bırak
    if "-" in osb_name:
        return osb_name

    # Düz şehir adı (Malatya) -> "<Şehir> OSB" formatına tamamla
    return osb_name + " OSB"

# ============================================================
# CITY EXTRACTION
# ============================================================

def extract_city(query: str, osb_name: str | None = None):
    """
    Şimdilik şehir bilgisini OSB adından çıkarmaya çalışır.

    Örneğin:

        Malatya-Güney
        Malatya-Yeni
        Malatya OSB

    gibi adlarda ilk kelime şehir olarak alınır.

    Ancak resolver zaten OSB adını benzersiz şekilde
    çözebiliyorsa city None olarak da çalışabilir.
    """

    if not osb_name:
        return None

    parts = osb_name.split()

    if not parts:
        return None

    # --------------------------------------------------------
    # Şehir tahmini
    # --------------------------------------------------------

    first_part = parts[0].strip()

    # Tireli OSB isimleri için:
    # Malatya-Güney → Malatya
    # Malatya-Yeni → Malatya
    if "-" in first_part:

        city = first_part.split(
            "-",
            1
        )[0].strip()

        if city:
            return city

    # "Malatya OSB" gibi isimler için
    return first_part


# ============================================================
# QUERY EMBEDDING
# ============================================================

def create_query_embedding(query: str):
    """
    Kullanıcı sorusunun embedding'ini oluşturur.

    Chroma'ya veri yüklenirken kullanılan
    embedding modeli ile aynı model kullanılır.
    """

    response = ollama.embeddings(
        model=EMBEDDING_MODEL,
        prompt=query,
    )

    return response["embedding"]


# ============================================================
# RETRIEVAL
# ============================================================

def retrieve(
    query: str,
    top_k: int = CHROMA_TOP_K,
):
    """
    Gerçek retrieval pipeline.

    Akış:

        1. Intent detection
        2. OSB entity extraction
        3. OSB resolution
        4. Query embedding
        5. Metadata filtering
        6. ChromaDB retrieval
        7. Cross-encoder reranking
        8. Final results
    """

    # ========================================================
    # 1. QUERY INTENT
    # ========================================================

    intent_result = detect_intent(
        query
    )

    intent = intent_result[
        "intent"
    ]

    chunk_type = get_chunk_type(
        intent
    )

    sector_keyword = None
    effective_top_k = top_k

    if chunk_type == "sector":
        sector_keyword = extract_sector_keyword(
            query
        )

        if sector_keyword:
            effective_top_k = max(
                top_k,
                32
            )

    intent_confidence = (
        intent_result["confidence"]
    )


    # ========================================================
    # 2. OSB ENTITY EXTRACTION
    # ========================================================

    osb_name = extract_osb_name(
        query
    )


    # --------------------------------------------------------
    # OSB ENTITY BULUNAMADI
    # --------------------------------------------------------

    if not osb_name:

        return {
            "status": "not_found",
            "query": query,
            "intent": intent,
            "intent_confidence": intent_confidence,
            "chunk_type": chunk_type,
            "osb_id": None,
            "osb_name": None,
            "results": [],
        }


    # ========================================================
    # 3. CITY EXTRACTION
    # ========================================================

    city = extract_city(
        query,
        osb_name
    )


    # ========================================================
    # 4. OSB ENTITY RESOLUTION
    # ========================================================

    osb_result = resolve_osb(
        osb_name,
        city
    )

    status = osb_result[
        "status"
    ]


    # ========================================================
    # OSB BULUNAMADI
    # ========================================================

    if status == "not_found":

        # ----------------------------------------------------
        # Şehir filtresi fazla kısıtlayıcı olabilir.
        # Bu yüzden city olmadan ikinci kez deniyoruz.
        # ----------------------------------------------------

        osb_result = resolve_osb(
            osb_name
        )

        status = osb_result[
            "status"
        ]


    # ========================================================
    # HALA BULUNAMADI
    # ========================================================

    if status == "not_found":

        return {
            "status": "not_found",
            "query": query,
            "intent": intent,
            "intent_confidence": intent_confidence,
            "chunk_type": chunk_type,
            "osb_id": None,
            "osb_name": osb_name,
            "results": [],
        }


    # ========================================================
    # OSB BELİRSİZ
    # ========================================================

    if status == "ambiguous":

        return {
            "status": "ambiguous",
            "query": query,
            "intent": intent,
            "intent_confidence": intent_confidence,
            "chunk_type": chunk_type,
            "osb_id": None,
            "osb_name": osb_name,
            "candidates": osb_result.get(
                "candidates",
                [],
            ),
            "results": [],
        }


    # ========================================================
    # UNIQUE OSB
    # ========================================================

    osb_id = osb_result[
        "osb_id"
    ]

    resolved_osb_name = osb_result[
        "osb_name"
    ]


    # ========================================================
    # 5. QUERY EMBEDDING
    # ========================================================

    query_embedding = (
        create_query_embedding(
            query
        )
    )


    # ========================================================
    # 6. METADATA FILTER
    # ========================================================

    where = {
        "$and": [
            {
                "osb_id": osb_id
            },
            {
                "chunk_type": chunk_type
            },
        ]
    }


    # ========================================================
    # 7. CHROMADB RETRIEVAL
    # ========================================================

    results = collection.query(
        query_embeddings=[
            query_embedding
        ],
        n_results=effective_top_k,
        where=where,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )


    # ========================================================
    # CHROMA SONUÇLARINI AL
    # ========================================================

    documents = results.get(
        "documents",
        [[]],
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]],
    )[0]

    distances = results.get(
        "distances",
        [[]],
    )[0]


    # ========================================================
    # SONUÇ YOK
    # ========================================================

    if not documents:

        return {
            "status": "success",
            "query": query,
            "intent": intent,
            "intent_confidence": intent_confidence,
            "chunk_type": chunk_type,
            "osb_id": osb_id,
            "osb_name": resolved_osb_name,
            "results": [],
        }


    # ========================================================
    # 8. CANDIDATES
    # ========================================================

    candidates = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):

        candidates.append(
            {
                "document": document,
                "metadata": metadata,
                "distance": float(
                    distance
                ),
            }
        )


    # ========================================================
    # SEKTÖR FİLTRELEME
    # ========================================================

    if chunk_type == "sector" and sector_keyword:

        exact_matches = [
            candidate
            for candidate in candidates
            if matches_sector(
                candidate["document"],
                sector_keyword,
            )
        ]

        if exact_matches:
            candidates = exact_matches


    # ========================================================
    # 9. RERANKING
    # ========================================================

    reranked = reranker.rerank(
        query=query,
        candidates=candidates,
        top_k=RERANK_TOP_K,
    )


    # ========================================================
    # 10. FINAL RESULT
    # ========================================================

    return {
        "status": "success",
        "query": query,
        "intent": intent,
        "intent_confidence": intent_confidence,
        "chunk_type": chunk_type,
        "osb_id": osb_id,
        "osb_name": resolved_osb_name,
        "results": reranked,
    }


# ============================================================
# RESULT PRINTING
# ============================================================

def print_results(result):
    """
    Retrieval sonucunu terminalde okunabilir
    şekilde gösterir.
    """

    print("\n" + "=" * 70)

    print(
        "RETRIEVAL SONUCU"
    )

    print("=" * 70)


    # --------------------------------------------------------
    # QUERY
    # --------------------------------------------------------

    print(
        f"\nSoru: {result.get('query')}"
    )

    print(
        f"Status: {result.get('status')}"
    )

    print(
        f"Intent: {result.get('intent')}"
    )

    print(
        f"Chunk type: "
        f"{result.get('chunk_type')}"
    )

    print(
        f"OSB ID: "
        f"{result.get('osb_id')}"
    )

    print(
        f"OSB: "
        f"{result.get('osb_name')}"
    )


    confidence = result.get(
        "intent_confidence"
    )

    if confidence is not None:

        print(
            f"Intent confidence: "
            f"{confidence:.2f}"
        )


    # --------------------------------------------------------
    # AMBIGUOUS
    # --------------------------------------------------------

    if result.get(
        "status"
    ) == "ambiguous":

        print(
            "\n⚠️ OSB BELİRSİZ"
        )

        candidates = result.get(
            "candidates",
            [],
        )

        print(
            "\nAdaylar:"
        )

        for candidate in candidates:

            print(
                f"  ID {candidate.get('id')} "
                f"| {candidate.get('name')} "
                f"| {candidate.get('city')} "
                f"| {candidate.get('district')} "
                f"| {candidate.get('region')}"
            )

        return


    # --------------------------------------------------------
    # NOT FOUND
    # --------------------------------------------------------

    if result.get(
        "status"
    ) == "not_found":

        print(
            "\n⚠️ OSB BULUNAMADI"
        )

        return


    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    reranked = result.get(
        "results",
        [],
    )

    print(
        f"\nSonuç sayısı: "
        f"{len(reranked)}"
    )


    if not reranked:

        print(
            "\n⚠️ Uygun retrieval sonucu bulunamadı."
        )

        return


    # --------------------------------------------------------
    # RESULT LOOP
    # --------------------------------------------------------

    for rank, item in enumerate(
        reranked,
        start=1,
    ):

        print(
            "\n" + "-" * 70
        )

        print(
            f"#{rank}"
        )


        # ----------------------------------------------------
        # RERANKER SCORE
        # ----------------------------------------------------

        reranker_score = item.get(
            "reranker_score"
        )

        if reranker_score is not None:

            print(
                f"Reranker score: "
                f"{reranker_score:.4f}"
            )


        # ----------------------------------------------------
        # CHROMA DISTANCE
        # ----------------------------------------------------

        distance = item.get(
            "distance"
        )

        if distance is not None:

            print(
                f"Chroma distance: "
                f"{distance:.4f}"
            )


        # ----------------------------------------------------
        # METADATA
        # ----------------------------------------------------

        metadata = item.get(
            "metadata",
            {},
        )

        print(
            f"Chunk type: "
            f"{metadata.get('chunk_type')}"
        )

        print(
            f"OSB ID: "
            f"{metadata.get('osb_id')}"
        )

        print(
            f"OSB: "
            f"{metadata.get('osb_adi')}"
        )


        # ----------------------------------------------------
        # DOCUMENT
        # ----------------------------------------------------

        print(
            "\nTEXT:"
        )

        print(
            item.get(
                "document",
                "",
            )
        )


# ============================================================
# TEST QUERIES
# ============================================================

TEST_QUERIES = [

    "Malatya-Güney OSB'de kaç boş parsel var?",

    "Malatya-Güney OSB'de kaç fabrika üretim yapıyor?",

    "Malatya-Güney OSB'de kaç kişi istihdam ediliyor?",

    "Malatya-Güney OSB hangi bölgede bulunuyor?",

    "Malatya-Güney OSB'de gıda sektöründe kaç kişi çalışıyor?",

    "Malatya OSB'de kaç fabrika üretim yapıyor?",
]


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    print(
        "\n" + "=" * 70
    )

    print(
        "GERÇEK RETRIEVAL PIPELINE TESTİ"
    )

    print(
        "=" * 70
    )


    for query in TEST_QUERIES:

        result = retrieve(
            query=query,
            top_k=CHROMA_TOP_K,
        )

        print_results(
            result
        )