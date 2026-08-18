import pandas as pd

EXCEL_PATH = "data/parsel_tablosu.xlsx"
OUTPUT_PATH = "data/parsel_tablosu_temiz.xlsx"

# Excel'i oku
df = pd.read_excel(
    EXCEL_PATH,
    sheet_name="Veri Tabanı"
)

print("=" * 60)
print("VERİ TEMİZLEME")
print("=" * 60)

print(f"Temizleme öncesi sütun sayısı: {df.shape[1]}")

# Tamamen boş sütunları bul
completely_empty_columns = df.columns[df.isna().all()].tolist()

print("\nTamamen boş sütunlar:")

if completely_empty_columns:
    for column in completely_empty_columns:
        print(f"- {column}")
else:
    print("- Yok")

# Tamamen boş sütunları sil
df_clean = df.dropna(
    axis=1,
    how="all"
)

print("\n" + "=" * 60)
print("TEMİZLEME SONUCU")
print("=" * 60)

print(f"Önceki sütun sayısı : {df.shape[1]}")
print(f"Yeni sütun sayısı   : {df_clean.shape[1]}")
print(f"Silinen sütun sayısı: {df.shape[1] - df_clean.shape[1]}")

# Yeni Excel dosyasını kaydet
df_clean.to_excel(
    OUTPUT_PATH,
    index=False
)

print(f"\nTemiz dosya oluşturuldu:")
print(OUTPUT_PATH)