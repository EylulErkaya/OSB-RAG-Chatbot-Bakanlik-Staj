# ============================================================
# SECTOR RESOLVER
# ============================================================

SECTOR_KEYWORDS = [
    "gıda",
    "tekstil",
    "otomotiv",
    "kimya",
    "makine",
    "elektrik",
    "metal",
    "plastik",
]


def turkish_lower(text: str) -> str:
    """
    Türkçe karakterleri normalize ederek küçük harfe çevirir.
    """

    if text is None:
        return ""

    text = text.replace("İ", "i")
    text = text.replace("I", "ı")

    return text.lower()


def extract_sector_keyword(query: str):
    """
    Kullanıcı sorgusundan sektör anahtar kelimesini çıkarır.

    Örnek:

        Malatya-Güney OSB'de gıda sektöründe kaç kişi çalışıyor?
            -> gıda
    """

    normalized = turkish_lower(query)

    for keyword in SECTOR_KEYWORDS:
        if keyword in normalized:
            return keyword

    return None


def matches_sector(document: str, keyword: str) -> bool:
    """
    Dokümanda sektör anahtar kelimesi geçiyor mu?
    """

    if not keyword:
        return False

    return keyword in turkish_lower(document)


if __name__ == "__main__":

    print("=" * 70)
    print("SECTOR RESOLVER TESTİ")
    print("=" * 70)

    tests = [
        "Malatya-Güney OSB'de gıda sektöründe kaç kişi çalışıyor?",
        "Tekstil sektöründe kaç firma var?",
        "Otomotiv sektöründe kaç fabrika var?",
        "Malatya OSB'de kaç kişi çalışıyor?",
    ]

    for query in tests:

        keyword = extract_sector_keyword(query)

        print("-" * 70)
        print(f"Soru   : {query}")
        print(f"Sektör : {keyword}")