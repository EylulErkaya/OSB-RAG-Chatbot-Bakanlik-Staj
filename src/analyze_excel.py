import pandas as pd

EXCEL_PATH = "data/parsel_tablosu.xlsx"

print("=" * 60)
print("EXCEL ANALİZİ")
print("=" * 60)

excel = pd.ExcelFile(EXCEL_PATH)

print("\nSAYFALAR:")
for sheet in excel.sheet_names:
    print(f"- {sheet}")

df = pd.read_excel(
    EXCEL_PATH,
    sheet_name="Veri Tabanı"
)

print("\n" + "=" * 60)
print("GENEL BİLGİ")
print("=" * 60)

print(f"Satır sayısı : {df.shape[0]}")
print(f"Sütun sayısı : {df.shape[1]}")

# --------------------------------------------------
# SÜTUNLAR
# --------------------------------------------------

print("\n" + "=" * 60)
print("TÜM SÜTUNLAR")
print("=" * 60)

for i, column in enumerate(df.columns, start=1):
    print(f"{i:3}. {column}")

# --------------------------------------------------
# BOŞ DEĞER ANALİZİ
# --------------------------------------------------

print("\n" + "=" * 60)
print("BOŞ DEĞER ANALİZİ")
print("=" * 60)

missing = df.isna().sum()

missing_df = pd.DataFrame({
    "Sütun": missing.index,
    "Boş Değer": missing.values,
    "Boş Oranı (%)": (missing.values / len(df) * 100).round(2)
})

missing_df = missing_df[
    missing_df["Boş Değer"] > 0
].sort_values(
    "Boş Değer",
    ascending=False
)

print(missing_df.to_string(index=False))

# --------------------------------------------------
# TEKRARLI KAYITLAR
# --------------------------------------------------

print("\n" + "=" * 60)
print("TEKRARLI KAYIT ANALİZİ")
print("=" * 60)

duplicate_count = df.duplicated().sum()

print(f"Tekrarlı satır sayısı: {duplicate_count}")

# --------------------------------------------------
# BENZERSİZ DEĞER SAYILARI
# --------------------------------------------------

print("\n" + "=" * 60)
print("BENZERSİZ DEĞER SAYILARI")
print("=" * 60)

unique_df = pd.DataFrame({
    "Sütun": df.columns,
    "Benzersiz Değer": [
        df[column].nunique(dropna=True)
        for column in df.columns
    ]
})

print(unique_df.to_string(index=False))

# --------------------------------------------------
# ÖRNEK DEĞER ANALİZİ
# --------------------------------------------------

print("\n" + "=" * 60)
print("ÖRNEK DEĞERLER")
print("=" * 60)

for column in df.columns:
    values = df[column].dropna().unique()[:5]

    print(f"\n[{column}]")

    if len(values) == 0:
        print("  Veri yok")
    else:
        for value in values:
            print(f"  - {value}")