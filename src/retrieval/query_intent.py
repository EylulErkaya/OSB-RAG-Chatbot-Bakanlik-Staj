import re


# ============================================================
# INTENT TANIMLARI
# ============================================================

INTENT_RULES = {

    "ranking": [],

    "aggregation": [
        "toplam",
        "toplamda",
        "hepsi",
        "kaç osb var",
        "osb'lerin toplam",
        "osblerin toplam",
    ],

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
        "deprem",
        "deprem bölgesi",
        "yatırım",
        "yatırım programı",
    ],
    
    "listing": [
        "listele",
        "listesi",
        "liste",
        "göster",
        "gösterir misin",
        "hangileri",
        "hangi osb'ler",
        "hangi osbler",
        "osb'ler",
        "osbler",
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


def is_single_osb_query(query: str) -> bool:
    """Return True when an explicitly named, singular OSB is in scope."""

    normalized = normalize_text(query)
    return bool(re.search(
        r"\b[\wçğıöşü-]+\s+osb['’](?:deki|daki|teki|taki|de|da|nin|nın|nun|nün)\b",
        normalized,
    ))


def detect_scope(query: str) -> str:
    """Classify the query scope without changing its intent scores."""

    normalized = normalize_text(query)

    if is_single_osb_query(normalized):
        return "single_osb"

    has_plural_osb_scope = bool(re.search(
        r"\bosb(?:'|’)?ler(?:in|i|de|da|den|dan)?\b",
        normalized,
    ))
    has_osb_count_scope = bool(re.search(
        r"kaç\s+(?:tane\s+)?osb(?:'|’)?(?:ler)?\s+(?:var|bulunuyor|bulunmakta)",
        normalized,
    ))

    return "group" if has_plural_osb_scope or has_osb_count_scope else "other"


def is_aggregation_query(query: str) -> bool:
    """Identify multi-OSB calculations without capturing single-OSB questions."""

    normalized = normalize_text(query)

    if is_single_osb_query(normalized):
        return False

    count_patterns = [
        r"kaç\s+(?:tane\s+)?osb(?:'|’)?(?:ler)?\s+(?:var|bulunuyor|bulunmakta)",
        r"osb\s+sayısı",
    ]
    if any(re.search(pattern, normalized) for pattern in count_patterns):
        return True

    has_aggregation_word = any(
        word in normalized
        for word in ("toplam", "toplamda", "hepsi")
    )
    has_multi_osb_scope = bool(
        re.search(r"\bosb(?:'|’)?ler(?:in|i|de|da|den|dan)?\b", normalized)
    )

    return has_aggregation_word and has_multi_osb_scope


def is_ranking_query(query: str) -> bool:
    """Identify ranking / comparison questions over structured fields."""

    normalized = normalize_text(query)

    if is_single_osb_query(normalized):
        return False

    if "en büyük" in normalized or "en buyuk" in normalized:
        return False

    ranking_phrases = [
        "en fazla",
        "en çok",
        "en cok",
        "en yüksek",
        "en yuksek",
        "en eski",
    ]

    return any(phrase in normalized for phrase in ranking_phrases)


# ============================================================
# INTENT CLASSIFIER
# ============================================================

def detect_intent(query: str):

    query = normalize_text(query)
    scope = detect_scope(query)

    scores = {
        intent: 0
        for intent in INTENT_RULES
    }

    # Aggregation scope takes precedence over field keywords such as
    # "fabrika" and "istihdam".  Single named OSBs are excluded by
    # is_aggregation_query and continue through the normal scorer.
    if is_aggregation_query(query):
        scores["aggregation"] = 1
        return {
            "intent": "aggregation",
            "confidence": 1.0,
            "scores": scores,
        }

    if is_ranking_query(query):
        scores["ranking"] = 1
        return {
            "intent": "ranking",
            "confidence": 1.0,
            "scores": scores,
        }

    # employment chunk'ındaki bilgiyi hedefler.

    production_context_keywords = [
        "üretimde",
        "üretimdeki",
        "inşaatta",
        "inşaattaki",
        "projede",
        "projedeki",
    ]

    if "parsel" in query and any(
        keyword in query
        for keyword in production_context_keywords
    ):
        scores["employment"] += 2

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

    final_scores = scores.copy()

    # Preserve the raw aggregation score for observability, but never let a
    # single named OSB be classified as an aggregation on a score tie.
    if scope == "single_osb":
        final_scores["aggregation"] = -1

    best_intent = max(
        final_scores,
        key=final_scores.get
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
        
        "Malatya'daki OSB'leri listele",

        "Malatya'daki OSB'leri göster",

        "Türkiye'deki OSB'leri listele",

        "Hangi OSB'ler var?",

        "Malatya OSB listesi",
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
        
def detect_requested_field(query: str):
    """
    Kullanıcının hangi OSB alanını sorduğunu belirler.
    """

    query = query.lower().strip()

    field_rules = [
        (
            [
                "kuruluş yılı",
                "kurulus yili",
                "kaç yılında kuruldu",
                "ne zaman kuruldu",
            ],
            "OSB Kuruluş Yılı",
        ),
        (
            [
                "kuruluş tarihi",
                "kurulus tarihi",
                "kuruluş tarihi nedir",
            ],
            "OSB Kuruluş Tarihi",
        ),
        (
            [
                "hangi bölgede",
                "hangi bölge",
            ],
            "Bölge",
        ),
        (
            [
                "hangi ilde",
                "hangi il",
            ],
            "İl Adı",
        ),
        (
            [
                "hangi ilçede",
                "hangi ilçe",
                "ilçesi nedir",
            ],
            "İlçe",
        ),
        (
            [
                "teşvik bölgesi",
                "kaçıncı teşvik",
            ],
            "Teşvik Bölgelerine Göre İller",
        ),
        (
            [
                "osb türü",
                "türü nedir",
                "hangi tür",
            ],
            "OSB Türü",
        ),
    ]

    for keywords, field in field_rules:

        for keyword in keywords:

            if keyword in query:
                return field

    return None
