import pandas as pd
from pathlib import Path

OSB_PATH = "data//normalized//osb_data.csv"
SECTOR_PATH = "data//normalized//sektor_data.csv"

OUTPUT_PATH = Path("data/normalized/data_dictionary.csv")


# --------------------------------------------------
# VERİLERİ OKU
# --------------------------------------------------

osb_df = pd.read_csv(OSB_PATH)
sector_df = pd.read_csv(SECTOR_PATH)


# --------------------------------------------------
# VERİ SÖZLÜĞÜ OLUŞTUR
# --------------------------------------------------

records = []


def analyze_dataframe(df, table_name):

    for column in df.columns:

        records.append({
            "tablo": table_name,
            "alan": column,
            "veri_tipi": str(df[column].dtype),
            "kayit_sayisi": len(df),
            "dolu_deger": int(df[column].notna().sum()),
            "bos_deger": int(df[column].isna().sum()),
            "benzersiz_deger": int(df[column].nunique(dropna=True)),
        })


analyze_dataframe(osb_df, "osb")
analyze_dataframe(sector_df, "sektor")


dictionary_df = pd.DataFrame(records)


# --------------------------------------------------
# KAYDET
# --------------------------------------------------

dictionary_df.to_csv(
    OUTPUT_PATH,
    index=False,
    encoding="utf-8-sig"
)


# --------------------------------------------------
# EKRANA YAZDIR
# --------------------------------------------------

print("=" * 70)
print("VERİ SÖZLÜĞÜ")
print("=" * 70)

print(
    dictionary_df.to_string(index=False)
)

print("\n" + "=" * 70)
print("SONUÇ")
print("=" * 70)

print(f"Toplam alan sayısı: {len(dictionary_df)}")
print(f"OSB alanları      : {(dictionary_df['tablo'] == 'osb').sum()}")
print(f"Sektör alanları   : {(dictionary_df['tablo'] == 'sektor').sum()}")

print(f"\nDosya oluşturuldu:")
print(OUTPUT_PATH)