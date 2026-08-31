import pandas as pd
import json
from pathlib import Path


# --------------------------------------------------
# AYARLAR
# --------------------------------------------------

OSB_PATH = "data/normalized/osb_data.csv"
SECTOR_PATH = "data/normalized/sektor_data.csv"

OUTPUT_DIR = Path("data/documents")
OUTPUT_PATH = OUTPUT_DIR / "rag_documents.jsonl"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# VERİLERİ OKU
# --------------------------------------------------

osb_df = pd.read_csv(OSB_PATH)
DEPREM_COLUMN = "DEPREM\nBÖLGESİ"
YATIRIM_COLUMN = "Yatırım Programı"
sector_df = pd.read_csv(SECTOR_PATH)


print("=" * 70)
print("GRANÜLER RAG DOKÜMANLARI")
print("=" * 70)

print(f"OSB kayıtları    : {len(osb_df)}")
print(f"Sektör kayıtları : {len(sector_df)}")


# --------------------------------------------------
# YARDIMCI FONKSİYONLAR
# --------------------------------------------------

def is_available(value):
    return pd.notna(value)


def clean_number(value):
    """
    6.0 -> 6
    314.0 -> 314
    gibi gereksiz .0 gösterimini kaldırır.
    """

    if pd.isna(value):
        return None

    if isinstance(value, float) and value.is_integer():
        return int(value)

    return value


def add_field(lines, label, value):
    """
    Değer varsa dokümana ekler.
    NaN değerleri eklemez.
    """

    value = clean_number(value)

    if value is not None:
        lines.append(f"- {label}: {value}")
        
def normalize_flag(value):
    """
    Excel'deki + ve boş değerlerini anlamlı hale getirir.

    +    -> Evet
    boş  -> Hayır
    """

    if pd.isna(value):
        return "Hayır"

    value = str(value).strip()

    if value == "+":
        return "Evet"

    return "Hayır"


# --------------------------------------------------
# DOKÜMAN LİSTESİ
# --------------------------------------------------

documents = []


# ==================================================
# 1. OSB GENEL DOKÜMANLARI
# ==================================================

for _, osb in osb_df.iterrows():

    osb_id = int(osb["ID"])

    lines = []

    lines.append(f"OSB: {osb['OSB Adı']}")

    add_field(lines, "İl", osb["İl Adı"])
    add_field(lines, "İlçe", osb["İlçe"])
    add_field(lines, "Bölge", osb["Bölge"])
    add_field(
        lines,
        "Teşvik bölgelerine göre il",
        osb["Teşvik Bölgelerine Göre İller"]
    )
    add_field(lines, "OSB türü", osb["OSB Türü"])
    add_field(lines, "Aşama", osb["Aşama"])
    add_field(lines, "Aşama detayı", osb["Aşama Detayı"])
    add_field(lines, "Sicil no", osb["Sicil No"])
    
    lines.append(
    f"- Deprem Bölgesi: "
    f"{normalize_flag(osb[DEPREM_COLUMN])}" 
    )

    lines.append(
        f"- Yatırım Programı: "
        f"{normalize_flag(osb[YATIRIM_COLUMN])}"
    )
    
     # --------------------------------------------------
    # KURULUŞ VE DURUM BİLGİLERİ
    # --------------------------------------------------

    lines.append("")
    lines.append("Kuruluş ve Durum Bilgileri:")

    establishment_fields = [
        ("OSB kuruluş yılı", "OSB Kuruluş Yılı"),
        ("OSB kuruluş tarihi", "OSB Kuruluş Tarihi"),
        ("Gerçek kuruluş yılı", "GERÇEK\nKURULUŞ\nYILI"),
        ("Evrak kayıt tarihi", "Evrak\nKayıt\nTarihi"),
        ("Geliş tarihleri", "Geliş Tarihleri"),
        ("Yeni dizayn", "Yeni Dizayn"),
    ]

    for label, column in establishment_fields:
        add_field(lines, label, osb[column])

    lines.append("")
    lines.append("Parsel Bilgileri:")

    parcel_fields = [
        ("Bölge büyüklüğü (Ha)", "Bölge Büyüklüğü (Ha)"),
        (
            "Sanayi parsel alanı (Ha)",
            "Sanayi Parsel Alanı (Ha) (x+y)"
        ),
        (
            "İmar parsel sayısı",
            "Parsel Sayısı (İmar)"
        ),
        (
            "Parsel sayısı (Bölge)",
            "Parsel Sayısı  (Bölge)"
        ),
        (
            "Toplam parsel sayısı (Bölge ve Öngörü)",
            "Toplam Parsel Sayısı (Bölge ve Öngörü)"
        ),
        (
            "Öngörü parsel sayısı",
            "Öngörü Parsel"
        ),
        (
            "Tahsisi yapılan parsel sayısı",
            "Tahsisi Yapılan Parsellerin Sayısı (m)"
        ),
        (
            "Tahsisi yapılan parsel alanı (Ha)",
            "Tahsisi Yapılan Parsellerin Alanı (Ha) (x)"
        ),
        (
            "Boş parsel sayısı",
            "Boş Parsel Sayısı (n)"
        ),
        (
            "Boş parsel alanı (Ha)",
            "Boş Parsel Alan (Ha) (y)"
        ),
        (
            "Üretim parsel sayısı",
            "Üretim (a)"
        ),
        (
            "İnşaat parsel sayısı",
            "İnşaat (b)"
        ),
        (
            "Proje parsel sayısı",
            "Proje (c)"
        ),
        (
            "Parsel birim fiyatı (m²)",
            "Parsel Birim Fiyat\n(m­²)"
        ),
        (
            "Tahsisli parsel sayısı (a+b+c)",
            "Tahsisli Parsel Sayısı (a+b+c)"
        ),
        (
            "Boş ve öngörü parsel",
            "Boş ve Öngörü Parsel"
        ),
    ]

    for label, column in parcel_fields:
        add_field(lines, label, osb[column])
        
        lines.append("")
    lines.append("Parsel Tipi Bilgileri:")

    parcel_type_fields = [
        ("A Tipi (3.000-5.000 m2)", "A Tipi (3.000-5.000 m2)"),
        ("B Tipi (5.001-7.000 m2)", "B Tipi (5.001-.7000 m2)"),
        ("C Tipi (7.001-10.000 m2)", "C Tipi (7.001-10.000 m2)"),
        ("D Tipi (10.001-20.000 m2)", "D Tipi (10.001-20.000 m2)"),
        ("E Tipi (20.001-30.000 m2)", "E Tipi (20.001-30.000 m2)"),
        ("F Tipi (30.001-40.000 m2)", "F Tipi (30.001-40.000 m2)"),
        ("G Tipi (40.001-50.000 m2)", "G Tipi (40.001-50.000 m2)"),
        ("H Tipi (50.001-100.000 m2)", "H Tipi (50.001-100.000 m2)"),
        ("I Tipi (100.001 m2 ve üzeri)", "I Tipi (100.001-   ..m2)"),
    ]

    for label, column in parcel_type_fields:
        add_field(lines, label, osb[column])

    lines.append("")
    lines.append("İstihdam ve Fabrika Bilgileri:")

    employment_fields = [
        ("İstihdam", "İstihdam"),
        ("Öngörü istihdam", "Öngörü İstihdam"),
        (
            "Üretimdeki toplam istihdam",
            "Toplam İstihdam"
        ),
        (
            "Üretimdeki toplam parsel",
            "Üretimdeki Toplam Parsel Sayısı"
        ),
        (
            "Üretimdeki toplam fabrika",
            "Üretimdeki Toplam Fabrika Sayısı"
        ),
    ]

    for label, column in employment_fields:
        add_field(lines, label, osb[column])

    # Ek not varsa ekle
    if is_available(osb["Ek Not"]):
        lines.append("")
        lines.append("Ek Not:")
        lines.append(str(osb["Ek Not"]))

    documents.append({
        "id": f"osb_{osb_id}_general",
        "document_type": "osb_general",
        "text": "\n".join(lines),
        "metadata": {
            "osb_id": osb_id,
            "osb_adi": str(osb["OSB Adı"]),
            "il": str(osb["İl Adı"]),
            "ilce": str(osb["İlçe"]),
            "bolge": str(osb["Bölge"]),
            "document_type": "osb_general",
        }
    })


# ==================================================
# 2. SEKTÖR DOKÜMANLARI
# ==================================================

for _, sector in sector_df.iterrows():

    osb_id = int(sector["osb_id"])

    # İlgili OSB bilgisini bul
    osb_match = osb_df[
        osb_df["ID"] == osb_id
    ]

    if osb_match.empty:
        continue

    osb = osb_match.iloc[0]

    sector_name = sector["sektor_adi"]

    lines = []

    lines.append(f"OSB: {osb['OSB Adı']}")
    lines.append(f"İl: {osb['İl Adı']}")
    lines.append(f"Bölge: {osb['Bölge']}")
    lines.append("")
    lines.append("Sektör Bilgileri:")
    lines.append(f"- Sektör: {sector_name}")

    add_field(lines, "NC", sector["nc"])
    add_field(lines, "PS", sector["ps"])
    add_field(lines, "FS", sector["fs"])
    add_field(lines, "İstihdam", sector["istihdam"])

    documents.append({
        "id": (
            f"osb_{osb_id}_"
            f"sector_{int(sector['nc'])}"
        ),
        "document_type": "sector",
        "text": "\n".join(lines),
        "metadata": {
            "osb_id": osb_id,
            "osb_adi": str(osb["OSB Adı"]),
            "il": str(osb["İl Adı"]),
            "bolge": str(osb["Bölge"]),
            "nc": int(sector["nc"]),
            "sektor_adi": str(sector_name),
            "document_type": "sector",
        }
    })


# ==================================================
# 3. JSONL KAYDET
# ==================================================

with open(
    OUTPUT_PATH,
    "w",
    encoding="utf-8"
) as file:

    for document in documents:

        file.write(
            json.dumps(
                document,
                ensure_ascii=False
            ) + "\n"
        )


# ==================================================
# 4. KONTROLLER
# ==================================================

general_count = sum(
    1
    for doc in documents
    if doc["document_type"] == "osb_general"
)

sector_count = sum(
    1
    for doc in documents
    if doc["document_type"] == "sector"
)

print("\n" + "=" * 70)
print("SONUÇ")
print("=" * 70)

print(f"OSB genel dokümanı   : {general_count}")
print(f"Sektör dokümanı      : {sector_count}")
print(f"Toplam doküman       : {len(documents)}")

print("\nBeklenen:")
print(f"OSB genel            : {len(osb_df)}")
print(f"Sektör              : {len(sector_df)}")
print(f"Toplam              : {len(osb_df) + len(sector_df)}")

print("\nDosya:")
print(OUTPUT_PATH)

print("\n" + "=" * 70)
print("İLK OSB GENEL DOKÜMANI")
print("=" * 70)

print(documents[0]["text"])

print("\n" + "=" * 70)
print("İLK SEKTÖR DOKÜMANI")
print("=" * 70)

first_sector = next(
    doc for doc in documents
    if doc["document_type"] == "sector"
)

print(first_sector["text"])