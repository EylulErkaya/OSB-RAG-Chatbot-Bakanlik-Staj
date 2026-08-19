import re


# ============================================================
# INTENT TANIMLARI
# ============================================================

INTENT_RULES = {

    "parcel": [
        "parsel",
        "boş parsel",
        "tahsis",
        "arsa",
        "alan",
    ],

    "employment": [
        "istihdam",
        "çalışan",
        "çalışıyor",
        "kaç kişi",
        "fabrika",
        "üretim",
    ],

    "sector": [
        "sektör",
        "gıda",
        "tekstil",
        "otomotiv",
        "kimya",
        "makine",
        "elektrik",
        "metal",
        "plastik",
    ],

    "general": [
        "bölge",
        "il",
        "ilçe",
        "tür",
        "aşama",
        "sicil",
        "nerede",
        "hangi bölgede",
    ],
}


# ============================================================
# NORMALİZASYON
# ============================================================

def normalize_text(text: str) -> str:

    return (
        text
        .strip()
        .lower()
    )


# ============================================================
# INTENT CLASSIFIER
# ============================================================

def detect_intent(query: str):

    query = normalize_text(query)

    scores = {
        intent: 0
        for intent in INTENT_RULES
    }

    # --------------------------------------------------------
    # KELİME EŞLEŞMESİ
    # --------------------------------------------------------

    for intent, keywords in INTENT_RULES.items():

        for keyword in keywords:

            if keyword in query:

                scores[intent] += 1
                
    # --------------------------------------------------------
    
    
    # ÖNCELİK KURALLARI
    # --------------------------------------------------------

    # Sektör adı geçiyorsa sektör sorusu önceliklidir.
    sector_specific_keywords = [
        "sektör",
        "gıda",
        "tekstil",
        "otomotiv",
        "kimya",
        "makine",
        "elektrik",
        "metal",
        "plastik",
    ]

    if any(
        keyword in query
        for keyword in sector_specific_keywords
    ):
        scores["sector"] += 2


    # --------------------------------------------------------
    # EN YÜKSEK SKOR
    # --------------------------------------------------------

    best_intent = max(
        scores,
        key=scores.get
    )

    best_score = scores[best_intent]

    # --------------------------------------------------------
    # HİÇBİR ŞEY BULUNAMADI
    # --------------------------------------------------------

    if best_score == 0:

        return {
            "intent": "general",
            "confidence": 0.0,
            "scores": scores,
        }


    # --------------------------------------------------------
    # BASİT CONFIDENCE
    # --------------------------------------------------------

    total_matches = sum(
        scores.values()
    )

    confidence = (
        best_score / total_matches
        if total_matches > 0
        else 0.0
    )

    return {
        "intent": best_intent,
        "confidence": confidence,
        "scores": scores,
    }


# ============================================================
# CHUNK TYPE HARİTASI
# ============================================================

INTENT_TO_CHUNK_TYPE = {

    "parcel":
        "osb_parcel",

    "employment":
        "osb_employment",

    "sector":
        "sector",

    "general":
        "osb_basic",
}


def get_chunk_type(intent: str):

    return INTENT_TO_CHUNK_TYPE.get(
        intent,
        "osb_general"
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    queries = [

        "Malatya-Güney OSB'de kaç boş parsel var?",

        "Malatya-Güney OSB'de kaç fabrika üretim yapıyor?",

        "Malatya-Güney OSB'de kaç kişi istihdam ediliyor?",

        "Malatya-Güney OSB hangi bölgede bulunuyor?",

        "Malatya-Güney OSB'de gıda sektöründe kaç kişi çalışıyor?",

        "Malatya-Güney OSB'nin sicil numarası nedir?",
    ]


    print("=" * 70)
    print("QUERY INTENT TESTİ")
    print("=" * 70)


    for query in queries:

        result = detect_intent(
            query
        )

        intent = result["intent"]

        chunk_type = get_chunk_type(
            intent
        )

        print("\n" + "-" * 70)

        print(
            f"SORU: {query}"
        )

        print(
            f"Intent: {intent}"
        )

        print(
            f"Chunk type: {chunk_type}"
        )

        print(
            f"Confidence: "
            f"{result['confidence']:.2f}"
        )

        print(
            f"Scores: "
            f"{result['scores']}"
        )