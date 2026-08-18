import pandas as pd
import json
from pathlib import Path

OSB_PATH = "data/normalized/osb_data.csv"
SECTOR_PATH = "data/normalized/sektor_data.csv"

OUTPUT_DIR = Path("data/documents")
OUTPUT_PATH = OUTPUT_DIR / "osb_documents.jsonl"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# VERİLERİ OKU
# --------------------------------------------------

osb_df = pd.read_csv(OSB_PATH)
sector_df = pd.read_csv(SECTOR_PATH)

print("=" * 70)
print("RAG DOKÜMANLARI OLUŞTURMA")
print("=" * 70)

print(f"OSB kayıtları    : {len(osb_df)}")
print(f"Sektör kayıtları : {len(sector_df)}")


# --------------------------------------------------
# YARDIMCI FONKSİYON
# --------------------------------------------------

def format_value(value):
    """
    NaN değerlerini metne çevirmeden atlar.
    0 değerini ise korur.
    """

    if pd.isna(value):
        return None

    return value


# --------------------------------------------------
# DOKÜMANLARI OLUŞTUR
# --------------------------------------------------

documents = []

for _, osb in osb_df.iterrows():

    osb_id = int(osb["ID"])

    # Bu OSB'nin sektörleri
    sectors = sector_df[
        sector_df["osb_id"] == osb_id
    ]

    lines = []

    # --------------------------------------------------
    # TEMEL BİLGİLER
    # --------------------------------------------------

    lines.append(f"OSB: {osb['OSB Adı']}")

    if format_value(osb["İl Adı"]) is not None:
        lines.append(f"İl: {osb['İl Adı']}")

    if format_value(osb["İlçe"]) is not None:
        lines.append(f"İlçe: {osb['İlçe']}")

    if format_value(osb["Bölge"]) is not None:
        lines.append(f"Bölge: {osb['Bölge']}")

    if format_value(osb["OSB Türü"]) is not None:
        lines.append(f"OSB Türü: {osb['OSB Türü']}")

    if format_value(osb["Aşama"]) is not None:
        lines.append(f"Aşama: {osb['Aşama']}")

    if format_value(osb["Aşama Detayı"]) is not None:
        lines.append(f"Aşama Detayı: {osb['Aşama Detayı']}")

    # --------------------------------------------------
    # PARSEL BİLGİLERİ
    # --------------------------------------------------

    lines.append("")
    lines.append("Parsel Bilgileri:")

    parcel_fields = [
        ("Bölge Büyüklüğü (Ha)", "Bölge büyüklüğü"),
        ("Sanayi Parsel Alanı (Ha) (x+y)", "Sanayi parsel alanı"),
        ("Parsel Sayısı (İmar)", "İmar parsel sayısı"),
        ("Parsel Sayısı  (Bölge)", "Bölge parsel sayısı"),
        ("Toplam Parsel Sayısı (Bölge ve Öngörü)", "Toplam parsel sayısı"),
        ("Tahsisi Yapılan Parsellerin Sayısı (m)", "Tahsisi yapılan parsel sayısı"),
        ("Boş Parsel Sayısı (n)", "Boş parsel sayısı"),
        ("Boş Parsel Alan (Ha) (y)", "Boş parsel alanı"),
        ("Üretim (a)", "Üretimdeki parsel sayısı"),
        ("İnşaat (b)", "İnşaattaki parsel sayısı"),
        ("Proje (c)", "Projedeki parsel sayısı"),
    ]

    for column, label in parcel_fields:

        value = format_value(osb[column])

        if value is not None:
            lines.append(f"- {label}: {value}")


    # --------------------------------------------------
    # İSTİHDAM
    # --------------------------------------------------

    lines.append("")
    lines.append("İstihdam Bilgileri:")

    employment_fields = [
        ("İstihdam", "İstihdam"),
        ("Öngörü İstihdam", "Öngörü istihdam"),
        ("Toplam İstihdam", "Üretimdeki toplam istihdam"),
        ("Üretimdeki Toplam Fabrika Sayısı", "Üretimdeki toplam fabrika sayısı"),
    ]

    for column, label in employment_fields:

        value = format_value(osb[column])

        if value is not None:
            lines.append(f"- {label}: {value}")


    # --------------------------------------------------
    # SEKTÖRLER
    # --------------------------------------------------

    lines.append("")
    lines.append("Sektör Bilgileri:")

    for _, sector in sectors.iterrows():

        sector_name = format_value(sector["sektor_adi"])

        if sector_name is None:
            continue

        lines.append(f"- Sektör: {sector_name}")

        nc = format_value(sector["nc"])
        ps = format_value(sector["ps"])
        fs = format_value(sector["fs"])
        employment = format_value(sector["istihdam"])

        if nc is not None:
            lines.append(f"  NC: {nc}")

        if ps is not None:
            lines.append(f"  PS: {ps}")

        if fs is not None:
            lines.append(f"  FS: {fs}")

        if employment is not None:
            lines.append(f"  İstihdam: {employment}")


    # --------------------------------------------------
    # EK NOT
    # --------------------------------------------------

    note = format_value(osb["Ek Not"])

    if note is not None:

        lines.append("")
        lines.append("Ek Not:")
        lines.append(str(note))


    # --------------------------------------------------
    # DOKÜMAN
    # --------------------------------------------------

    text = "\n".join(lines)

    documents.append({
        "id": f"osb_{osb_id}",
        "text": text,
        "metadata": {
            "osb_id": osb_id,
            "osb_adi": str(osb["OSB Adı"]),
            "il": str(osb["İl Adı"]),
            "ilce": str(osb["İlçe"]),
            "bolge": str(osb["Bölge"]),
        }
    })


# --------------------------------------------------
# JSONL OLARAK KAYDET
# --------------------------------------------------

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
            )
            + "\n"
        )


# --------------------------------------------------
# KONTROL
# --------------------------------------------------

print("\n" + "=" * 70)
print("SONUÇ")
print("=" * 70)

print(f"Oluşturulan doküman sayısı: {len(documents)}")
print(f"Beklenen doküman sayısı   : {len(osb_df)}")

print(f"\nDosya:")
print(OUTPUT_PATH)

print("\nİlk doküman:")
print("-" * 70)
print(documents[0]["text"][:3000])