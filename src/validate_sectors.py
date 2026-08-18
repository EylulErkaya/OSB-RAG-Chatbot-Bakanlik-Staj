import pandas as pd

EXCEL_PATH = "data/parsel_tablosu.xlsx"

df = pd.read_excel(
    EXCEL_PATH,
    sheet_name="Veri Tabanı"
)

# --------------------------------------------------
# SEKTÖR KOLONLARINI BUL
# --------------------------------------------------

ps_columns = [f"PS-{i}" for i in range(1, 25)]
fs_columns = [f"FS-{i}" for i in range(1, 25)]
employment_columns = [f"İ-{i}" for i in range(1, 25)]

# --------------------------------------------------
# TOPLAMLAR
# --------------------------------------------------

ps_total = df[ps_columns].sum(axis=1, skipna=True)
fs_total = df[fs_columns].sum(axis=1, skipna=True)
employment_total = df[employment_columns].sum(axis=1, skipna=True)

# --------------------------------------------------
# KARŞILAŞTIRMA
# --------------------------------------------------

result = pd.DataFrame({
    "OSB": df["OSB Adı"],

    "Sektör PS Toplamı": ps_total,
    "Üretimdeki Toplam Parsel": df["Üretimdeki Toplam Parsel Sayısı"],

    "Sektör FS Toplamı": fs_total,
    "Üretimdeki Toplam Fabrika": df["Üretimdeki Toplam Fabrika Sayısı"],

    "Sektör İstihdam Toplamı": employment_total,
    "Toplam İstihdam": df["Toplam İstihdam"],
})

print("=" * 100)
print("SEKTÖR TOPLAM KONTROLÜ")
print("=" * 100)

print(result.head(20).to_string(index=False))

# --------------------------------------------------
# FARKLAR
# --------------------------------------------------

result["PS Fark"] = (
    result["Sektör PS Toplamı"]
    - result["Üretimdeki Toplam Parsel"]
)

result["FS Fark"] = (
    result["Sektör FS Toplamı"]
    - result["Üretimdeki Toplam Fabrika"]
)

result["İstihdam Fark"] = (
    result["Sektör İstihdam Toplamı"]
    - result["Toplam İstihdam"]
)

print("\n" + "=" * 100)
print("FARK ANALİZİ")
print("=" * 100)

print(
    result[
        [
            "OSB",
            "PS Fark",
            "FS Fark",
            "İstihdam Fark"
        ]
    ].head(20).to_string(index=False)
)

# --------------------------------------------------
# TAM EŞLEŞME
# --------------------------------------------------

print("\n" + "=" * 100)
print("EŞLEŞME SONUÇLARI")
print("=" * 100)

print(
    "PS tam eşleşme:",
    (result["PS Fark"] == 0).sum(),
    "/",
    len(result)
)

print(
    "FS tam eşleşme:",
    (result["FS Fark"] == 0).sum(),
    "/",
    len(result)
)

print(
    "İstihdam tam eşleşme:",
    (result["İstihdam Fark"] == 0).sum(),
    "/",
    len(result)
)