import pandas as pd

OSB_PATH = "data/normalized/osb_data.csv"
SECTOR_PATH = "data/normalized/sektor_data.csv"

osb_df = pd.read_csv(OSB_PATH)
sector_df = pd.read_csv(SECTOR_PATH)

print("=" * 70)
print("NORMALİZE VERİ DOĞRULAMA")
print("=" * 70)

# --------------------------------------------------
# 1. KAYIT SAYISI
# --------------------------------------------------

print("\nKAYIT SAYILARI")
print("-" * 70)

print("OSB kayıtları:", len(osb_df))
print("Sektör kayıtları:", len(sector_df))

expected_sector_count = len(osb_df) * 24

print("Beklenen sektör kaydı:", expected_sector_count)

print(
    "Sektör kayıt sayısı doğru:",
    len(sector_df) == expected_sector_count
)

# --------------------------------------------------
# 2. OSB ID KONTROLÜ
# --------------------------------------------------

print("\nOSB ID KONTROLÜ")
print("-" * 70)

print(
    "Benzersiz OSB ID:",
    osb_df["ID"].nunique()
)

print(
    "Sektörlerdeki benzersiz OSB ID:",
    sector_df["osb_id"].nunique()
)

missing_osb_ids = set(osb_df["ID"]) - set(sector_df["osb_id"])

print(
    "Sektör tablosunda bulunmayan OSB ID sayısı:",
    len(missing_osb_ids)
)

# --------------------------------------------------
# 3. SEKTÖR SIRA KONTROLÜ
# --------------------------------------------------

print("\nSEKTÖR SIRA KONTROLÜ")
print("-" * 70)

sector_counts = (
    sector_df
    .groupby("osb_id")["sektor_sira"]
    .nunique()
)

print(
    "Her OSB'de 24 sektör bulunan kayıt sayısı:",
    (sector_counts == 24).sum()
)

print(
    "Toplam OSB:",
    len(osb_df)
)

# --------------------------------------------------
# 4. SEKTÖR TOPLAMLARI
# --------------------------------------------------

ps_total = (
    sector_df
    .groupby("osb_id")["ps"]
    .sum(min_count=1)
)

fs_total = (
    sector_df
    .groupby("osb_id")["fs"]
    .sum(min_count=1)
)

employment_total = (
    sector_df
    .groupby("osb_id")["istihdam"]
    .sum(min_count=1)
)

comparison = pd.DataFrame({
    "sector_ps": ps_total,
    "sector_fs": fs_total,
    "sector_employment": employment_total,
})

# --------------------------------------------------
# 5. OSB TABLOSUNDAKİ TOPLAMLAR
# --------------------------------------------------

comparison["osb_ps"] = (
    osb_df
    .set_index("ID")["Üretimdeki Toplam Parsel Sayısı"]
)

comparison["osb_fs"] = (
    osb_df
    .set_index("ID")["Üretimdeki Toplam Fabrika Sayısı"]
)

comparison["osb_employment"] = (
    osb_df
    .set_index("ID")["Toplam İstihdam"]
)

# --------------------------------------------------
# 6. FARKLAR
# --------------------------------------------------

comparison["ps_diff"] = (
    comparison["sector_ps"]
    - comparison["osb_ps"]
)

comparison["fs_diff"] = (
    comparison["sector_fs"]
    - comparison["osb_fs"]
)

comparison["employment_diff"] = (
    comparison["sector_employment"]
    - comparison["osb_employment"]
)

print("\nTOPLAM KONTROLÜ")
print("-" * 70)

print(
    "PS eşleşme:",
    (comparison["ps_diff"] == 0).sum(),
    "/",
    len(osb_df)
)

print(
    "FS eşleşme:",
    (comparison["fs_diff"] == 0).sum(),
    "/",
    len(osb_df)
)

print(
    "İstihdam eşleşme:",
    (comparison["employment_diff"] == 0).sum(),
    "/",
    len(osb_df)
)

# --------------------------------------------------
# 7. HATALI KAYITLAR
# --------------------------------------------------

errors = comparison[
    (comparison["ps_diff"] != 0)
    | (comparison["fs_diff"] != 0)
    | (comparison["employment_diff"] != 0)
]

print("\nHATALI KAYIT SAYISI:", len(errors))

if len(errors) > 0:
    print("\nHatalı kayıtlar:")
    print(errors)
else:
    print("Tüm toplamlar başarıyla eşleşti.")

print("\n" + "=" * 70)
print("DOĞRULAMA TAMAMLANDI")
print("=" * 70)