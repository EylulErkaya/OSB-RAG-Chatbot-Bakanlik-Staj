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
            "osb_type": str(row["OSB Türü"]),
            "sicil_no": str(row["Sicil No"]),
            "kurulus_yili": str(row["OSB Kuruluş Yılı"]),
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


def filter_osbs(
    city: str | None = None,
    district: str | None = None,
    region: str | None = None,
    osb_type: str | None = None,
    stage: str | None = None,
    investment_program: str | None = None,
    earthquake_region: str | None = None,
    incentive_region: str | None = None,
):
    """Return OSB rows matching the filters used by ``list_osbs``.

    This keeps structured queries and the existing listing path on the same
    filter semantics without changing listing's pagination or response shape.
    """

    filtered = osb_df.copy()

    if city:
        value = normalize_text(city)
        filtered = filtered[
            filtered["İl Adı"].astype(str).str.strip().str.lower() == value
        ]

    if district:
        value = normalize_text(district)
        filtered = filtered[
            filtered["İlçe"].astype(str).str.strip().str.lower() == value
        ]

    if region:
        value = normalize_text(region)
        filtered = filtered[
            filtered["Bölge"].astype(str).str.strip().str.lower() == value
        ]

    if osb_type:
        value = normalize_text(osb_type)
        filtered = filtered[
            filtered["OSB Türü"].astype(str).str.strip().str.lower() == value
        ]

    if stage:
        value = normalize_text(stage)
        filtered = filtered[
            filtered["Aşama"].astype(str).str.strip().str.lower().str.contains(
                value,
                na=False,
            )
        ]

    if investment_program:
        filtered = filtered[
            filtered["Yatırım Programı"].apply(_normalize_investment)
            == investment_program
        ]

    if earthquake_region:
        filtered = filtered[
            filtered["DEPREM\nBÖLGESİ"].apply(_normalize_earthquake)
            == earthquake_region
        ]

    if incentive_region:
        value = normalize_text(incentive_region)
        filtered = filtered[
            filtered["Teşvik Bölgelerine Göre İller"]
            .astype(str)
            .str.strip()
            .str.lower()
            .str.contains(value, na=False)
        ]

    return filtered


def _normalize_investment(value):
    if pd.isna(value):
        return "Hayır"
    return "Evet" if str(value).strip() == "+" else "Hayır"


def _normalize_earthquake(value):
    if pd.isna(value):
        return "Hayır"
    return "Evet" if str(value).strip() == "+" else "Hayır"
    
    
def list_osbs(
    city: str | None = None,
    district: str | None = None,
    region: str | None = None,
    osb_type: str | None = None,
    stage: str | None = None,
    investment_program: str | None = None,
    earthquake_region: str | None = None,
    incentive_region: str | None = None,
    limit: int = 10,
    offset: int = 0,
):
    """
    OSB kayıtlarını filtreleyerek listeler.

    Desteklenen filtreler:

        city
        district
        region
        osb_type
        stage
        investment_program
        earthquake_region
        incentive_region

    Ayrıca pagination destekler.
    """

    filtered = filter_osbs(
        city=city,
        district=district,
        region=region,
        osb_type=osb_type,
        stage=stage,
        investment_program=investment_program,
        earthquake_region=earthquake_region,
        incentive_region=incentive_region,
    )

    # ========================================================
    # TÜM SONUÇLAR
    # ========================================================

    results = []

    for _, row in filtered.iterrows():

        results.append({
            "id": int(row["ID"]),
            "name": str(row["OSB Adı"]),
            "city": str(row["İl Adı"]),
            "district": str(row["İlçe"]),
            "region": str(row["Bölge"]),
            "type": str(row["OSB Türü"]),
            "stage": str(row["Aşama"]),
        })

    # ========================================================
    # TOTAL
    # ========================================================

    total_count = len(results)

    # ========================================================
    # PAGINATION
    # ========================================================

    paginated_results = results[
        offset:offset + limit
    ]

    return {
        "status": "success",
        "total_count": total_count,
        "limit": limit,
        "offset": offset,
        "returned_count": len(
            paginated_results
        ),
        "results": paginated_results,
    }



# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    
    print("\n" + "=" * 70)
    print("OSB LİSTELEME TESTİ")
    print("=" * 70)

    tests = [
        {
            "name": "Malatya OSB'leri",
            "city": "Malatya",
        },
        {
            "name": "Doğu Anadolu OSB'leri",
            "region": "Doğu Anadolu",
        },
        {
            "name": "Tüm OSB'ler",
        },
    ]

    for test in tests:

        print("\n" + "-" * 70)
        print(
            f"TEST: {test['name']}"
        )

        result = list_osbs(
            city=test.get("city"),
            region=test.get("region"),
            osb_type=test.get("osb_type"),
            limit=10,
            offset=0,
        )

        print(
            f"Toplam kayıt: "
            f"{result['total_count']}"
        )

        for item in result["results"]:

            print(
                f"{item['id']} | "
                f"{item['name']} | "
                f"{item['city']} | "
                f"{item['district']} | "
                f"{item['region']} | "
                f"{item['type']}"
            )

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
                
    print("\n" + "=" * 70)
    print("PAGINATION TESTİ")
    print("=" * 70)

    result = list_osbs(
        limit=10,
        offset=0,
    )

    print(
        f"Toplam kayıt    : {result['total_count']}"
    )

    print(
        f"Offset          : {result['offset']}"
    )

    print(
        f"Limit           : {result['limit']}"
    )

    print(
        f"Dönen kayıt     : {result['returned_count']}"
    )

    print("\nİlk 10 kayıt:")

    for item in result["results"]:

        print(
            f"{item['id']} | "
            f"{item['name']} | "
            f"{item['city']}"
        )


    print("\n" + "-" * 70)

    result = list_osbs(
        limit=10,
        offset=10,
    )

    print(
        f"Toplam kayıt    : {result['total_count']}"
    )

    print(
        f"Offset          : {result['offset']}"
    )

    print(
        f"Limit           : {result['limit']}"
    )

    print(
        f"Dönen kayıt     : {result['returned_count']}"
    )

    print("\n11-20 arasındaki kayıtlar:")

    for item in result["results"]:

        print(
            f"{item['id']} | "
            f"{item['name']} | "
            f"{item['city']}"
        )
