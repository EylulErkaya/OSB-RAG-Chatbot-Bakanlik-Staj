# import pandas as pd

# EXCEL_PATH = "data/parsel_tablosu.xlsx"

# df = pd.read_excel(
#     EXCEL_PATH,
#     sheet_name="Veri Tabanı"
# )

# columns_to_inspect = [
#     "Yeni Dizayn",

#     "NC-1",
#     "SA-1",
#     "PS-1",
#     "FS-1",
#     "İ-1",

#     "NC-2",
#     "SA-2",
#     "PS-2",
#     "FS-2",
#     "İ-2",

#     "A Tipi (3.000-5.000 m2)",
#     "B Tipi (5.001-.7000 m2)",
#     "C Tipi (7.001-10.000 m2)",
#     "D Tipi (10.001-20.000 m2)",
#     "E Tipi (20.001-30.000 m2)",
#     "F Tipi (30.001-40.000 m2)",
#     "G Tipi (40.001-50.000 m2)",
#     "H Tipi (50.001-100.000 m2)",
#     "I Tipi (100.001-   ..m2)",
# ]

# for column in columns_to_inspect:

#     print("\n" + "=" * 60)
#     print(column)
#     print("=" * 60)

#     if column not in df.columns:
#         print("SÜTUN BULUNAMADI")
#         continue

#     print("Veri tipi:", df[column].dtype)
#     print("Boş değer:", df[column].isna().sum())
#     print("Benzersiz:", df[column].nunique(dropna=True))

#     print("\nİlk 20 değer:")

#     values = df[column].dropna().unique()[:20]

#     for value in values:
#         print("-", value)

# import pandas as pd

# EXCEL_PATH = "data/parsel_tablosu.xlsx"

# df = pd.read_excel(
#     EXCEL_PATH,
#     sheet_name="Veri Tabanı"
# )

# columns = [
#     "ID",
#     "İl Adı",
#     "İlçe",
#     "OSB Adı",
#     "NC-1",
#     "SA-1",
#     "PS-1",
#     "FS-1",
#     "İ-1",
#     "NC-2",
#     "SA-2",
#     "PS-2",
#     "FS-2",
#     "İ-2",
# ]

# print("=" * 80)
# print("SEKTÖR VERİSİ ÖRNEKLERİ")
# print("=" * 80)

# print(df[columns].head(20).to_string(index=False))

import pandas as pd

EXCEL_PATH = "data/parsel_tablosu_temiz.xlsx"

df = pd.read_excel(EXCEL_PATH)

print("=" * 60)
print("UNNAMED: 170 ANALİZİ")
print("=" * 60)

column = "Unnamed: 170"

print("Veri tipi:", df[column].dtype)
print("Boş değer:", df[column].isna().sum())
print("Benzersiz değer:", df[column].nunique(dropna=True))

print("\nMevcut değerler:")

print(
    df[column]
    .dropna()
    .value_counts()
    .to_string()
)