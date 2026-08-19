import pandas as pd


# ============================================================
# AYARLAR
# ============================================================

OSB_PATH = "data/normalized/osb_data.csv"


# ============================================================
# VERİYİ OKU
# ============================================================

df = pd.read_csv(OSB_PATH)

print("=" * 70)
print("OSB ADI - ID ANALİZİ")
print("=" * 70)

print(f"Toplam OSB kaydı: {len(df)}")


# ============================================================
# AYNI İSME SAHİP FARKLI ID'LER
# ============================================================

name_id_counts = (
    df.groupby("OSB Adı")["ID"]
    .nunique()
    .sort_values(ascending=False)
)


duplicates = name_id_counts[
    name_id_counts > 1
]


print("\n" + "=" * 70)
print("AYNI İSME SAHİP FARKLI ID'LER")
print("=" * 70)

print(
    f"Farklı ID'lere sahip tekrar eden OSB adı: "
    f"{len(duplicates)}"
)


for name in duplicates.index:

    records = df[
        df["OSB Adı"] == name
    ][
        [
            "ID",
            "OSB Adı",
            "İl Adı",
            "İlçe",
            "Bölge",
        ]
    ]

    print("\n" + "-" * 70)

    print(
        records.to_string(
            index=False
        )
    )


# ============================================================
# MALATYA ÖZEL KONTROL
# ============================================================

print("\n" + "=" * 70)
print("MALATYA KONTROLÜ")
print("=" * 70)

malatya = df[
    df["İl Adı"]
    .astype(str)
    .str.strip()
    .str.lower()
    == "malatya"
][
    [
        "ID",
        "OSB Adı",
        "İl Adı",
        "İlçe",
        "Bölge",
    ]
]

print(
    malatya.to_string(
        index=False
    )
)


# ============================================================
# SONUÇ
# ============================================================

print("\n" + "=" * 70)
print("ANALİZ TAMAMLANDI")
print("=" * 70)