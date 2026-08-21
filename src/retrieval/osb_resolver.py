import pandas as pd


# ============================================================
# AYARLAR
# ============================================================

OSB_PATH = "data/normalized/osb_data.csv"


# ============================================================
# VERİYİ YÜKLE
# ============================================================

osb_df = pd.read_csv(OSB_PATH)


# ============================================================
# OSB RESOLVER
# ============================================================

def normalize_text(text: str) -> str:
    """
    Basit metin normalizasyonu.
    """

    if text is None:
        return ""

    return (
        str(text)
        .strip()
        .lower()
    )


def find_osb_candidates(
    osb_name: str,
    city: str | None = None
):
    """
    OSB adına göre aday kayıtları bulur.

    Eğer city verilirse il ile birlikte filtreler.
    """

    name = normalize_text(osb_name)

    mask = (
        osb_df["OSB Adı"]
        .astype(str)
        .str.strip()
        .str.lower()
        == name
    )

    candidates = osb_df[mask].copy()

    # --------------------------------------------------------
    # İL FİLTRESİ
    # --------------------------------------------------------

    if city:

        city_normalized = normalize_text(city)

        city_mask = (
            candidates["İl Adı"]
            .astype(str)
            .str.strip()
            .str.lower()
            == city_normalized
        )

        candidates = candidates[city_mask]

    return candidates


def resolve_osb(
    osb_name: str,
    city: str | None = None
):
    """
    OSB adını güvenli şekilde çözer.

    Sonuç:
        - unique
        - ambiguous
        - not_found
    """

    candidates = find_osb_candidates(
        osb_name,
        city
    )

    # --------------------------------------------------------
    # BULUNAMADI
    # --------------------------------------------------------

    if candidates.empty:

        return {
            "status": "not_found",
            "candidates": []
        }

    # --------------------------------------------------------
    # TEK KAYIT
    # --------------------------------------------------------

    if len(candidates) == 1:

        row = candidates.iloc[0]

        return {
            "status": "unique",
            "osb_id": int(row["ID"]),
            "osb_name": str(row["OSB Adı"]),
            "city": str(row["İl Adı"]),
            "district": str(row["İlçe"]),
            "region": str(row["Bölge"]),
            "candidates": [
                {
                    "id": int(row["ID"]),
                    "name": str(row["OSB Adı"]),
                    "city": str(row["İl Adı"]),
                    "district": str(row["İlçe"]),
                    "region": str(row["Bölge"]),
                }
            ]
        }

    # --------------------------------------------------------
    # BİRDEN FAZLA
    # --------------------------------------------------------

    candidate_list = []

    for _, row in candidates.iterrows():

        candidate_list.append({
            "id": int(row["ID"]),
            "name": str(row["OSB Adı"]),
            "city": str(row["İl Adı"]),
            "district": str(row["İlçe"]),
            "region": str(row["Bölge"]),
            "data": row.to_dict(),
        })

    return {
        "status": "ambiguous",
        "candidates": candidate_list
    }


def compare_candidate_field(
    candidates,
    field
):
    """
    Birden fazla OSB adayının belirli bir alandaki
    değerlerini karşılaştırır.

    Sonuç:
        same     -> bütün adaylarda değer aynı
        different -> değerler farklı
        missing  -> alan bulunamadı
    """

    values = []

    for candidate in candidates:

        data = candidate.get("data", {})

        value = data.get(field)

        if pd.isna(value):
            value = None

        if value is not None:
            value = str(value).strip()

        values.append(value)

    # Hiçbir adayda veri yok
    if all(value is None for value in values):
        return {
            "status": "missing",
            "values": values
        }

    # Değerleri karşılaştır
    unique_values = set(
        value
        for value in values
        if value is not None
    )

    if len(unique_values) == 1:
        return {
            "status": "same",
            "value": next(iter(unique_values)),
            "values": values
        }

    return {
        "status": "different",
        "values": values
    }




# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    tests = [
        ("Malatya OSB", "Malatya"),
        ("Malatya-Güney", "Malatya"),
        ("Malatya-Yeni", "Malatya"),
        ("Afyon OSB", "Afyon"),
        ("Olmayan OSB", None),
    ]

    print("=" * 70)
    print("OSB ENTITY RESOLVER TESTİ")
    print("=" * 70)

    for osb_name, city in tests:

        print("\n" + "-" * 70)

        print(
            f"OSB : {osb_name}"
        )

        print(
            f"İl  : {city}"
        )

        result = resolve_osb(
            osb_name,
            city
        )

        print(
            f"Durum: {result['status']}"
        )

        if result["status"] == "unique":

            print(
                f"ID: {result['osb_id']}"
            )

        elif result["status"] == "ambiguous":

            print("Adaylar:")

            for candidate in result["candidates"]:

                print(
                    f"  ID {candidate['id']} | "
                    f"{candidate['name']} | "
                    f"{candidate['district']}"
                )