import pandas as pd
from pathlib import Path

# --------------------------------------------------
# AYARLAR
# --------------------------------------------------

INPUT_PATH = "data/parsel_tablosu_temiz.xlsx"
OUTPUT_DIR = Path("data/normalized")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# EXCEL'İ OKU
# --------------------------------------------------

df = pd.read_excel(INPUT_PATH)

print("=" * 70)
print("VERİ NORMALİZASYONU")
print("=" * 70)

print(f"Kaynak satır sayısı : {len(df)}")
print(f"Kaynak sütun sayısı : {len(df.columns)}")

# --------------------------------------------------
# SEKTÖR KOLONLARI
# --------------------------------------------------

sector_numbers = range(1, 25)

sector_columns = []

for i in sector_numbers:
    sector_columns.extend([
        f"NC-{i}",
        f"SA-{i}",
        f"PS-{i}",
        f"FS-{i}",
        f"İ-{i}",
    ])

# --------------------------------------------------
# OSB TABLOSUNU OLUŞTUR
# --------------------------------------------------

osb_columns = [
    column
    for column in df.columns
    if column not in sector_columns
]

osb_df = df[osb_columns].copy()

# --------------------------------------------------
# TEKNİK KOLON ADINI DÜZELT
# --------------------------------------------------

if "Unnamed: 170" in osb_df.columns:
    osb_df = osb_df.rename(
        columns={
            "Unnamed: 170": "Ek Not"
        }
    )

# --------------------------------------------------
# SEKTÖR TABLOSUNU OLUŞTUR
# --------------------------------------------------

sector_records = []

for _, row in df.iterrows():

    osb_id = row["ID"]

    for i in sector_numbers:

        nc = row[f"NC-{i}"]
        sa = row[f"SA-{i}"]
        ps = row[f"PS-{i}"]
        fs = row[f"FS-{i}"]
        istihdam = row[f"İ-{i}"]

        # Sektör tanımı yoksa kayıt oluşturma
        if pd.isna(sa):
            continue

        sector_records.append({
            "osb_id": osb_id,
            "sektor_sira": i,
            "nc": nc,
            "sektor_adi": sa,
            "ps": ps,
            "fs": fs,
            "istihdam": istihdam,
        })

sector_df = pd.DataFrame(sector_records)

# --------------------------------------------------
# VERİLERİ KAYDET
# --------------------------------------------------

osb_path = OUTPUT_DIR / "osb_data.csv"
sector_path = OUTPUT_DIR / "sektor_data.csv"

osb_df.to_csv(
    osb_path,
    index=False,
    encoding="utf-8-sig"
)

sector_df.to_csv(
    sector_path,
    index=False,
    encoding="utf-8-sig"
)

# --------------------------------------------------
# RAPOR
# --------------------------------------------------

print("\n" + "=" * 70)
print("NORMALİZASYON SONUCU")
print("=" * 70)

print(f"OSB kayıtları    : {len(osb_df)}")
print(f"OSB sütunları    : {len(osb_df.columns)}")

print(f"\nSektör kayıtları : {len(sector_df)}")
print(f"Sektör sütunları : {len(sector_df.columns)}")

print("\nOluşturulan dosyalar:")

print(f"- {osb_path}")
print(f"- {sector_path}")

# --------------------------------------------------
# SEKTÖR KONTROLÜ
# --------------------------------------------------

print("\n" + "=" * 70)
print("SEKTÖR KAYIT KONTROLÜ")
print("=" * 70)

print(
    sector_df[
        [
            "osb_id",
            "sektor_sira",
            "nc",
            "sektor_adi",
            "ps",
            "fs",
            "istihdam",
        ]
    ].head(10).to_string(index=False)
)

# --------------------------------------------------
# OSB KONTROLÜ
# --------------------------------------------------

print("\n" + "=" * 70)
print("OSB KAYIT KONTROLÜ")
print("=" * 70)

print(
    osb_df[
        [
            "ID",
            "OSB Adı",
            "İl Adı",
            "İlçe",
            "Bölge",
        ]
    ].head(10).to_string(index=False)
)

print("\nİşlem tamamlandı.")